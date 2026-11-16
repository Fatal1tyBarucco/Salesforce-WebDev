"""MCP Server for Knowledge-as-Code - exposes Salesforce Release Notes to agents."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import (
    CallToolRequest,
    CallToolRequestParams,
    CallToolResult,
    ContentBlock,
    ListToolsRequest,
    ListToolsResult,
    PaginatedRequestParams,
    TextContent,
    Tool,
)
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class ReleaseNotesQuery(BaseModel):
    """Query parameters for release notes."""

    model_config = ConfigDict(extra="forbid")

    release_slug: str | None = Field(
        default=None, description="Specific release slug (e.g., winter_27)"
    )
    category: str | None = Field(
        default=None, description="Filter by category (e.g., Lightning Experience)"
    )
    feature_name: str | None = Field(default=None, description="Search for specific feature")
    locale: str = Field(default="pt-BR", description="Language locale (pt-BR or en-US)")
    limit: int = Field(default=10, description="Maximum results to return")


class ReleaseNotesMCPServer:
    """MCP Server exposing Salesforce Release Notes as tools."""

    def __init__(self, releases_dir: Path = Path("releases")):
        self.releases_dir = releases_dir
        self.server: Server[Any, Any] = Server("salesforce-release-notes")
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register MCP tool handlers using decorators."""

        @self.server.list_tools()  # type: ignore[untyped-decorator]
        async def handle_list_tools(
            request: ListToolsRequest | None = None,
        ) -> ListToolsResult:
            """MCP SDK v2 handler for ``tools/list``."""
            del request  # unused, but kept for signature compatibility
            return ListToolsResult(tools=self._build_tools())

        @self.server.call_tool()  # type: ignore[untyped-decorator]
        async def handle_call_tool(
            request: CallToolRequest,
        ) -> CallToolResult:
            """MCP SDK v2 handler for ``tools/call``."""
            params: CallToolRequestParams = request.params
            blocks: list[ContentBlock] = []
            # list[TextContent] is Iterable[ContentBlock]; extend avoids list invariance.
            blocks.extend(await self.call_tool(params.name, params.arguments or {}))
            return CallToolResult(content=blocks)

    def _build_tools(self) -> list[Tool]:
        """Build the tool definitions exposed by this server."""
        return [
            Tool(
                name="search_release_notes",
                description="Search Salesforce Release Notes by release, category, or feature name",
                inputSchema=ReleaseNotesQuery.model_json_schema(),
            ),
            Tool(
                name="get_release_summary",
                description="Get executive summary for a specific release",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "release_slug": {
                            "type": "string",
                            "description": "Release slug (e.g., winter_27)",
                        },
                        "locale": {"type": "string", "default": "pt-BR"},
                    },
                    "required": ["release_slug"],
                },
            ),
            Tool(
                name="list_releases",
                description="List all available releases",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="compare_releases",
                description="Compare two releases - what's new, changed, removed",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "from_slug": {"type": "string", "description": "Base release slug"},
                        "to_slug": {"type": "string", "description": "Target release slug"},
                        "locale": {"type": "string", "default": "pt-BR"},
                    },
                    "required": ["from_slug", "to_slug"],
                },
            ),
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Dispatch a tool call by name; raises ValueError for unknown tools."""
        if name == "search_release_notes":
            return await self._search_release_notes(arguments)
        elif name == "get_release_summary":
            return await self._get_release_summary(arguments)
        elif name == "list_releases":
            return await self._list_releases()
        elif name == "compare_releases":
            return await self._compare_releases(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    async def _search_release_notes(self, args: dict[str, Any]) -> list[TextContent]:
        from pydantic import ValidationError

        try:
            query = ReleaseNotesQuery(**args)
        except ValidationError as e:
            return [TextContent(type="text", text=f"Invalid query: {e}")]

        results = []

        releases_to_search = []
        if query.release_slug:
            release_dir = self.releases_dir / query.release_slug
            if release_dir.exists():
                releases_to_search = [release_dir]
        else:
            releases_to_search = [d for d in self.releases_dir.iterdir() if d.is_dir()]

        for release_dir in releases_to_search:
            locale_dir = release_dir / query.locale
            if not locale_dir.exists():
                continue

            for md_file in locale_dir.glob("*.md"):
                try:
                    content = md_file.read_text(encoding="utf-8")

                    # Filter by category if specified
                    if query.category and query.category.lower() not in content.lower():
                        continue

                    # Filter by feature name if specified
                    if query.feature_name and query.feature_name.lower() not in content.lower():
                        continue

                    # Extract feature name from filename
                    feature_name = md_file.stem

                    results.append(
                        {
                            "release": release_dir.name,
                            "feature": feature_name,
                            "category": self._extract_category(content),
                            "excerpt": content[:500] + "..." if len(content) > 500 else content,
                            "file": str(md_file.relative_to(self.releases_dir)),
                        }
                    )

                    if len(results) >= query.limit:
                        break
                except Exception as e:
                    logger.warning("Error reading %s: %s", md_file, e)

            if len(results) >= query.limit:
                break

        return [TextContent(type="text", text=json.dumps(results, ensure_ascii=False, indent=2))]

    def _extract_category(self, content: str) -> str:
        """Extract category from markdown content."""
        lines = content.splitlines()
        # Category header takes precedence over the feature title.
        for line in lines:
            if line.startswith("## Categoria:") or line.startswith("## Category:"):
                return line.split(":", 1)[1].strip()
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
        return "Unknown"

    async def _get_release_summary(self, arguments: dict[str, Any]) -> list[TextContent]:
        release_slug = arguments["release_slug"]
        locale = arguments.get("locale", "pt-BR")

        release_dir = self.releases_dir / release_slug
        if not release_dir.exists():
            return [
                TextContent(
                    type="text", text=json.dumps({"error": f"Release {release_slug} not found"})
                )
            ]

        # Try to load summary cache
        cache_file = release_dir / ".summary_cache.json"
        if cache_file.exists():
            try:
                return [TextContent(type="text", text=cache_file.read_text(encoding="utf-8"))]
            except Exception:
                pass

        # Fallback: generate from markdown files
        locale_dir = release_dir / locale
        if not locale_dir.exists():
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": f"Locale {locale} not found for {release_slug}"}),
                )
            ]

        features = []
        for md_file in locale_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            features.append(
                {
                    "feature": md_file.stem,
                    "category": self._extract_category(content),
                    "preview": content[:300],
                }
            )

        summary = {
            "release": release_slug,
            "locale": locale,
            "total_features": len(features),
            "features": features,
        }

        return [TextContent(type="text", text=json.dumps(summary, ensure_ascii=False, indent=2))]

    async def _list_releases(self) -> list[TextContent]:
        releases = []
        for d in sorted(self.releases_dir.iterdir(), reverse=True):
            if d.is_dir() and not d.name.startswith("."):
                meta_file = d / ".meta.json"
                if meta_file.exists():
                    try:
                        meta = json.loads(meta_file.read_text(encoding="utf-8"))
                        releases.append(
                            {
                                "slug": d.name,
                                "name": meta.get("name", d.name),
                                "version": meta.get("version", "unknown"),
                                "total_features": meta.get("total_features", 0),
                                "categories": meta.get("categories", []),
                            }
                        )
                    except Exception:
                        pass
                else:
                    releases.append({"slug": d.name})

        return [TextContent(type="text", text=json.dumps(releases, ensure_ascii=False, indent=2))]

    async def _compare_releases(self, arguments: dict[str, Any]) -> list[TextContent]:
        from_slug = arguments["from_slug"]
        to_slug = arguments["to_slug"]
        locale = arguments.get("locale", "pt-BR")

        from_dir = self.releases_dir / from_slug / locale
        to_dir = self.releases_dir / to_slug / locale

        if not from_dir.exists():
            return [
                TextContent(
                    type="text", text=json.dumps({"error": f"Release {from_slug} not found"})
                )
            ]
        if not to_dir.exists():
            return [
                TextContent(
                    type="text", text=json.dumps({"error": f"Release {to_slug} not found"})
                )
            ]

        from_features = {f.stem: f.read_text(encoding="utf-8") for f in from_dir.glob("*.md")}
        to_features = {f.stem: f.read_text(encoding="utf-8") for f in to_dir.glob("*.md")}

        added = set(to_features.keys()) - set(from_features.keys())
        removed = set(from_features.keys()) - set(to_features.keys())
        common = set(from_features.keys()) & set(to_features.keys())

        changed = []
        for feature in common:
            if from_features[feature] != to_features[feature]:
                changed.append(feature)

        diff = {
            "from_release": from_slug,
            "to_release": to_slug,
            "added": list(added),
            "removed": list(removed),
            "changed": changed,
            "summary": {
                "added_count": len(added),
                "removed_count": len(removed),
                "changed_count": len(changed),
            },
        }

        return [TextContent(type="text", text=json.dumps(diff, ensure_ascii=False, indent=2))]


def create_server(releases_dir: Path = Path("releases")) -> Server:
    """Create and configure the MCP server."""
    mcp_server = ReleaseNotesMCPServer(releases_dir)
    return mcp_server.server


if __name__ == "__main__":  # pragma: no cover
    import asyncio
    from mcp.server.stdio import stdio_server

    async def main() -> None:
        server = create_server()
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(main())
