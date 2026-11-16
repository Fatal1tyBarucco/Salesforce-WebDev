"""MCP Server for Knowledge-as-Code - exposes Salesforce Release Notes to agents."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP
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
        self.mcp: FastMCP = FastMCP("salesforce-release-notes")
        self._register_tools()

    def _register_tools(self) -> None:
        """Register MCP tools using FastMCP decorators."""

        @self.mcp.tool()
        async def search_release_notes(
            release_slug: str | None = None,
            category: str | None = None,
            feature_name: str | None = None,
            locale: str = "pt-BR",
            limit: int = 10,
        ) -> str:
            """Search Salesforce Release Notes by release, category, or feature name."""
            return await self._search_release_notes(
                release_slug=release_slug,
                category=category,
                feature_name=feature_name,
                locale=locale,
                limit=limit,
            )

        @self.mcp.tool()
        async def get_release_summary(
            release_slug: str,
            locale: str = "pt-BR",
        ) -> str:
            """Get executive summary for a specific release."""
            return await self._get_release_summary(release_slug=release_slug, locale=locale)

        @self.mcp.tool()
        async def list_releases() -> str:
            """List all available releases."""
            return await self._list_releases()

        @self.mcp.tool()
        async def compare_releases(
            from_slug: str,
            to_slug: str,
            locale: str = "pt-BR",
        ) -> str:
            """Compare two releases - what's new, changed, removed."""
            return await self._compare_releases(from_slug=from_slug, to_slug=to_slug, locale=locale)

    async def _search_release_notes(
        self,
        query: ReleaseNotesQuery | None = None,
        release_slug: str | None = None,
        category: str | None = None,
        feature_name: str | None = None,
        locale: str = "pt-BR",
        limit: int = 10,
    ) -> str:
        """Search release notes and return JSON string.

        Accepts either a ReleaseNotesQuery object or individual keyword arguments
        for backward compatibility with existing tests.
        """
        # Handle both ReleaseNotesQuery object and individual parameters
        if query is not None and isinstance(query, ReleaseNotesQuery):
            release_slug = query.release_slug
            category = query.category
            feature_name = query.feature_name
            locale = query.locale
            limit = query.limit

        results = []

        releases_to_search = []
        if release_slug:
            release_dir = self.releases_dir / release_slug
            if release_dir.exists():
                releases_to_search = [release_dir]
        else:
            releases_to_search = [d for d in self.releases_dir.iterdir() if d.is_dir()]

        for release_dir in releases_to_search:
            locale_dir = release_dir / locale
            if not locale_dir.exists():
                continue

            for md_file in locale_dir.glob("*.md"):
                try:
                    content = md_file.read_text(encoding="utf-8")

                    # Filter by category if specified
                    if category and category.lower() not in content.lower():
                        continue

                    # Filter by feature name if specified
                    if feature_name and feature_name.lower() not in content.lower():
                        continue

                    # Extract feature name from filename
                    feature_name_extracted = md_file.stem

                    results.append(
                        {
                            "release": release_dir.name,
                            "feature": feature_name_extracted,
                            "category": self._extract_category(content),
                            "excerpt": content[:500] + "..." if len(content) > 500 else content,
                            "file": str(md_file.relative_to(self.releases_dir)),
                        }
                    )

                    if len(results) >= limit:
                        break
                except Exception as e:
                    logger.warning("Error reading %s: %s", md_file, e)

            if len(results) >= limit:
                break

        return json.dumps(results, ensure_ascii=False, indent=2)

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

    async def _get_release_summary(self, release_slug: str, locale: str = "pt-BR") -> str:
        """Get release summary and return JSON string."""
        release_dir = self.releases_dir / release_slug
        if not release_dir.exists():
            return json.dumps({"error": f"Release {release_slug} not found"})

        # Try to load summary cache
        cache_file = release_dir / ".summary_cache.json"
        if cache_file.exists():
            try:
                return cache_file.read_text(encoding="utf-8")
            except Exception:
                pass

        # Fallback: generate from markdown files
        locale_dir = release_dir / locale
        if not locale_dir.exists():
            return json.dumps({"error": f"Locale {locale} not found for {release_slug}"})

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

        return json.dumps(summary, ensure_ascii=False, indent=2)

    async def _list_releases(self) -> str:
        """List all releases and return JSON string."""
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

        return json.dumps(releases, ensure_ascii=False, indent=2)

    async def _compare_releases(self, from_slug: str, to_slug: str, locale: str = "pt-BR") -> str:
        """Compare two releases and return JSON string."""
        from_dir = self.releases_dir / from_slug / locale
        to_dir = self.releases_dir / to_slug / locale

        if not from_dir.exists():
            return json.dumps({"error": f"Release {from_slug} not found"})
        if not to_dir.exists():
            return json.dumps({"error": f"Release {to_slug} not found"})

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

        return json.dumps(diff, ensure_ascii=False, indent=2)


def create_server(releases_dir: Path = Path("releases")) -> FastMCP:
    """Create and configure the MCP server."""
    mcp_server = ReleaseNotesMCPServer(releases_dir)
    return mcp_server.mcp


if __name__ == "__main__":  # pragma: no cover
    import asyncio
    from mcp.server.stdio import stdio_server

    async def main() -> None:
        server = create_server()
        async with stdio_server() as (read_stream, write_stream):
            server.run(read_stream, write_stream)

    asyncio.run(main())
