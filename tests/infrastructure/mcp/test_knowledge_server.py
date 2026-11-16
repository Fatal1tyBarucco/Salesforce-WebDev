"""Tests for Knowledge Server MCP - 100% coverage target."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from mcp.server import Server, ServerRequestContext
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    ListToolsResult,
    PaginatedRequestParams,
    TextContent,
)

from src.infrastructure.mcp.knowledge_server import (
    ReleaseNotesMCPServer,
    ReleaseNotesQuery,
    create_server,
)

TOOL_NAMES = {
    "search_release_notes",
    "get_release_summary",
    "list_releases",
    "compare_releases",
}


def _decode(contents: list[TextContent]) -> Any:
    """Decodifica a saída ``TextContent`` de uma tool em objeto Python."""
    return json.loads(contents[0].text)


def _request_ctx(method: str) -> ServerRequestContext[Any]:
    """Contexto de requisição mínimo (os handlers não usam sessão/lifespan)."""
    return ServerRequestContext(
        session=MagicMock(),
        lifespan_context={},
        protocol_version="2025-06-18",
        method=method,
    )


@pytest.fixture
def temp_releases_dir(tmp_path):
    """Create temporary releases directory structure."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    # Create winter_27 release
    winter_dir = releases_dir / "winter_27"
    winter_dir.mkdir()
    (winter_dir / ".meta.json").write_text(
        '{"name": "Winter 27", "version": "27.0", "total_features": 2}'
    )

    pt_dir = winter_dir / "pt-BR"
    pt_dir.mkdir()
    (pt_dir / "feature1.md").write_text(
        "# Feature 1\n## Categoria: Lightning Experience\nContent 1"
    )
    (pt_dir / "feature2.md").write_text("# Feature 2\n## Categoria: Sales Cloud\nContent 2")

    en_dir = winter_dir / "en-US"
    en_dir.mkdir()
    (en_dir / "feature1.md").write_text(
        "# Feature 1\n## Category: Lightning Experience\nContent 1 EN"
    )

    # Create spring_27 release
    spring_dir = releases_dir / "spring_27"
    spring_dir.mkdir()
    (spring_dir / ".meta.json").write_text(
        '{"name": "Spring 27", "version": "27.2", "total_features": 1}'
    )

    pt_dir = spring_dir / "pt-BR"
    pt_dir.mkdir()
    (pt_dir / "feature3.md").write_text("# Feature 3\n## Categoria: Platform\nContent 3")

    return releases_dir


@pytest.fixture
def server(temp_releases_dir):
    """Create MCP server with temp directory."""
    return ReleaseNotesMCPServer(releases_dir=temp_releases_dir)


class TestReleaseNotesQuery:
    """Tests for ReleaseNotesQuery model."""

    def test_default_values(self):
        """Should have correct default values."""
        query = ReleaseNotesQuery()

        assert query.release_slug is None
        assert query.category is None
        assert query.feature_name is None
        assert query.locale == "pt-BR"
        assert query.limit == 10

    def test_custom_values(self):
        """Should accept custom values."""
        query = ReleaseNotesQuery(
            release_slug="winter_27",
            category="Lightning Experience",
            feature_name="New Feature",
            locale="en-US",
            limit=5,
        )

        assert query.release_slug == "winter_27"
        assert query.category == "Lightning Experience"
        assert query.feature_name == "New Feature"
        assert query.locale == "en-US"
        assert query.limit == 5


class TestReleaseNotesMCPServer:
    """Tests for ReleaseNotesMCPServer."""

    @pytest.mark.asyncio
    async def test_search_release_notes_by_release(self, server):
        """Should search notes by release slug."""
        query = ReleaseNotesQuery(
            release_slug="winter_27",
            locale="pt-BR",
            limit=10,
        )
        result = await server._search_release_notes(query.model_dump())

        data = _decode(result)

        assert len(data) == 2
        assert all(r["release"] == "winter_27" for r in data)

    @pytest.mark.asyncio
    async def test_search_release_notes_by_category(self, server):
        """Should search notes by category."""
        query = ReleaseNotesQuery(
            category="Lightning Experience",
            locale="pt-BR",
            limit=10,
        )
        result = await server._search_release_notes(query.model_dump())

        data = _decode(result)

        assert len(data) == 1
        assert data[0]["category"] == "Lightning Experience"

    @pytest.mark.asyncio
    async def test_search_release_notes_by_feature(self, server):
        """Should search notes by feature name."""
        query = ReleaseNotesQuery(
            feature_name="Feature 1",
            locale="pt-BR",
            limit=10,
        )
        result = await server._search_release_notes(query.model_dump())

        data = _decode(result)

        assert len(data) == 1
        assert data[0]["feature"] == "feature1"

    @pytest.mark.asyncio
    async def test_search_release_notes_all_releases(self, server):
        """Should search across all releases when no release specified."""
        query = ReleaseNotesQuery(
            locale="pt-BR",
            limit=10,
        )
        result = await server._search_release_notes(query.model_dump())

        data = _decode(result)

        assert len(data) == 3  # 2 from winter_27 + 1 from spring_27

    @pytest.mark.asyncio
    async def test_search_release_notes_limit(self, server):
        """Should respect limit parameter."""
        query = ReleaseNotesQuery(
            locale="pt-BR",
            limit=1,
        )
        result = await server._search_release_notes(query.model_dump())

        data = _decode(result)

        assert len(data) == 1

    @pytest.mark.asyncio
    async def test_search_release_notes_invalid_query(self, server):
        """Should reject unknown fields and report validation errors as text."""
        # Pydantic will raise ValidationError for invalid fields
        with pytest.raises(Exception):
            ReleaseNotesQuery(invalid_field="value")

        result = await server._search_release_notes({"limit": "not-a-number"})
        assert len(result) == 1
        assert result[0].text.startswith("Invalid query:")

    @pytest.mark.asyncio
    async def test_get_release_summary_exists(self, server):
        """Should return summary for existing release."""
        result = await server._get_release_summary({"release_slug": "winter_27", "locale": "pt-BR"})

        data = _decode(result)

        assert data["release"] == "winter_27"
        assert data["locale"] == "pt-BR"
        assert data["total_features"] == 2
        assert len(data["features"]) == 2

    @pytest.mark.asyncio
    async def test_get_release_summary_not_found(self, server):
        """Should return error for non-existent release."""
        result = await server._get_release_summary(
            {"release_slug": "nonexistent", "locale": "pt-BR"}
        )

        data = _decode(result)

        assert "error" in data
        assert "not found" in data["error"]

    @pytest.mark.asyncio
    async def test_get_release_summary_locale_not_found(self, server):
        """Should return error for non-existent locale."""
        result = await server._get_release_summary({"release_slug": "winter_27", "locale": "fr-FR"})

        data = _decode(result)

        assert "error" in data
        assert "not found" in data["error"]

    @pytest.mark.asyncio
    async def test_list_releases(self, server):
        """Should list all releases with metadata."""
        result = await server._list_releases()

        data = _decode(result)

        assert len(data) == 2
        assert data[0]["slug"] == "winter_27"
        assert data[0]["name"] == "Winter 27"
        assert data[0]["version"] == "27.0"
        assert data[0]["total_features"] == 2

    @pytest.mark.asyncio
    async def test_list_releases_sorted_descending(self, server):
        """Should list releases in deterministic descending slug order."""
        result = await server._list_releases()

        data = _decode(result)

        # sorted(reverse=True): "winter_27" > "spring_27" lexicographically
        assert data[0]["slug"] == "winter_27"
        assert data[1]["slug"] == "spring_27"

    @pytest.mark.asyncio
    async def test_compare_releases(self, server):
        """Should compare two releases."""
        result = await server._compare_releases(
            {"from_slug": "winter_27", "to_slug": "spring_27", "locale": "pt-BR"}
        )

        data = _decode(result)

        assert data["from_release"] == "winter_27"
        assert data["to_release"] == "spring_27"
        assert "feature1" in data["removed"]
        assert "feature2" in data["removed"]
        assert "feature3" in data["added"]
        assert data["summary"]["added_count"] == 1
        assert data["summary"]["removed_count"] == 2

    @pytest.mark.asyncio
    async def test_compare_releases_from_not_found(self, server):
        """Should return error when from release not found."""
        result = await server._compare_releases(
            {"from_slug": "nonexistent", "to_slug": "spring_27", "locale": "pt-BR"}
        )

        data = _decode(result)

        assert "error" in data
        assert "not found" in data["error"]

    @pytest.mark.asyncio
    async def test_compare_releases_to_not_found(self, server):
        """Should return error when to release not found."""
        result = await server._compare_releases(
            {"from_slug": "winter_27", "to_slug": "nonexistent", "locale": "pt-BR"}
        )

        data = _decode(result)

        assert "error" in data
        assert "not found" in data["error"]

    @pytest.mark.asyncio
    async def test_compare_releases_changed_feature(self, tmp_path):
        """Should detect features present in both releases but with different content."""
        releases_dir = tmp_path / "releases"
        v1 = releases_dir / "v1" / "pt-BR"
        v2 = releases_dir / "v2" / "pt-BR"
        v1.mkdir(parents=True)
        v2.mkdir(parents=True)
        (v1 / "shared.md").write_text("# Shared\nOld content")
        (v2 / "shared.md").write_text("# Shared\nNew content")

        srv = ReleaseNotesMCPServer(releases_dir=releases_dir)
        result = await srv._compare_releases(
            {"from_slug": "v1", "to_slug": "v2", "locale": "pt-BR"}
        )

        data = _decode(result)

        assert data["changed"] == ["shared"]
        assert data["summary"]["changed_count"] == 1
        assert data["summary"]["added_count"] == 0
        assert data["summary"]["removed_count"] == 0

    @pytest.mark.asyncio
    async def test_compare_releases_unchanged_common_feature(self, tmp_path):
        """Should not report common features with identical content as changed."""
        releases_dir = tmp_path / "releases"
        v1 = releases_dir / "v1" / "pt-BR"
        v2 = releases_dir / "v2" / "pt-BR"
        v1.mkdir(parents=True)
        v2.mkdir(parents=True)
        (v1 / "same.md").write_text("# Same\nIdentical content")
        (v2 / "same.md").write_text("# Same\nIdentical content")
        (v2 / "new.md").write_text("# New\nBrand new content")

        srv = ReleaseNotesMCPServer(releases_dir=releases_dir)
        result = await srv._compare_releases(
            {"from_slug": "v1", "to_slug": "v2", "locale": "pt-BR"}
        )

        data = _decode(result)

        assert data["changed"] == []
        assert data["added"] == ["new"]

    @pytest.mark.asyncio
    async def test_search_release_notes_missing_locale(self, server):
        """Should skip releases without the requested locale."""
        query = ReleaseNotesQuery(
            release_slug="winter_27",
            locale="fr-FR",
        )
        result = await server._search_release_notes(query.model_dump())

        data = _decode(result)

        assert data == []

    @pytest.mark.asyncio
    async def test_search_release_notes_read_error_is_logged(self, server, monkeypatch):
        """Should log and skip files that fail to read."""

        def raise_read_text(self, *args, **kwargs):
            raise OSError("boom")

        monkeypatch.setattr("pathlib.Path.read_text", raise_read_text)
        query = ReleaseNotesQuery(
            release_slug="winter_27",
            locale="pt-BR",
        )
        result = await server._search_release_notes(query.model_dump())

        data = _decode(result)

        assert data == []

    @pytest.mark.asyncio
    async def test_get_release_summary_cache_hit(self, server, temp_releases_dir):
        """Should return the cached summary when present."""
        cache_file = temp_releases_dir / "winter_27" / ".summary_cache.json"
        cache_file.write_text('{"release": "winter_27", "cached": true}')

        result = await server._get_release_summary({"release_slug": "winter_27", "locale": "pt-BR"})

        data = _decode(result)

        assert data == {"release": "winter_27", "cached": True}

    @pytest.mark.asyncio
    async def test_get_release_summary_cache_unreadable(self, server, temp_releases_dir):
        """Should fall back to markdown when the cache cannot be read."""
        (temp_releases_dir / "winter_27" / ".summary_cache.json").mkdir()

        result = await server._get_release_summary({"release_slug": "winter_27", "locale": "pt-BR"})

        data = _decode(result)

        assert data["release"] == "winter_27"
        assert data["total_features"] == 2

    @pytest.mark.asyncio
    async def test_search_release_notes_nonexistent_release(self, server):
        """Should return no results when the release slug does not exist."""
        query = ReleaseNotesQuery(
            release_slug="nonexistent",
            locale="pt-BR",
        )
        result = await server._search_release_notes(query.model_dump())

        data = _decode(result)

        assert data == []

    @pytest.mark.asyncio
    async def test_list_releases_ignores_files_and_hidden_dirs(self, server, temp_releases_dir):
        """Should ignore plain files and hidden directories."""
        (temp_releases_dir / "README.txt").write_text("not a release")
        (temp_releases_dir / ".hidden").mkdir()

        result = await server._list_releases()

        data = _decode(result)

        slugs = {r["slug"] for r in data}
        assert "README.txt" not in slugs
        assert ".hidden" not in slugs

    @pytest.mark.asyncio
    async def test_list_releases_invalid_meta_json(self, server, temp_releases_dir):
        """Should skip releases with invalid .meta.json."""
        (temp_releases_dir / "winter_27" / ".meta.json").write_text("not json")

        result = await server._list_releases()

        data = _decode(result)

        assert all(r["slug"] != "winter_27" for r in data)

    @pytest.mark.asyncio
    async def test_list_releases_without_meta(self, server, temp_releases_dir):
        """Should list slug only for releases without .meta.json."""
        (temp_releases_dir / "summer_27").mkdir()

        result = await server._list_releases()

        data = _decode(result)

        assert {"slug": "summer_27"} in data

    def test_extract_category(self, server):
        """Should extract category from markdown."""
        content = "# Feature\n## Categoria: Lightning Experience\nContent"
        category = server._extract_category(content)
        assert category == "Lightning Experience"

        content = "# Feature\n## Category: Sales Cloud\nContent"
        category = server._extract_category(content)
        assert category == "Sales Cloud"

        content = "# Feature\nContent"
        category = server._extract_category(content)
        assert category == "Feature"

        content = "No header"
        category = server._extract_category(content)
        assert category == "Unknown"


class TestRequestHandlers:
    """Tests for the MCP ``tools/list`` and ``tools/call`` request handlers."""

    @pytest.mark.asyncio
    async def test_handle_list_tools_exposes_expected_tools(self, server):
        """Should return the four tool definitions with object schemas."""
        result = await server._handle_list_tools(
            _request_ctx("tools/list"), PaginatedRequestParams()
        )

        assert isinstance(result, ListToolsResult)
        assert {t.name for t in result.tools} == TOOL_NAMES
        assert all(t.input_schema.get("type") == "object" for t in result.tools)

    @pytest.mark.asyncio
    async def test_handle_call_tool_dispatches(self, server):
        """Should dispatch a valid tool call to its handler."""
        result = await server._handle_call_tool(
            _request_ctx("tools/call"),
            CallToolRequestParams(name="list_releases", arguments={}),
        )

        assert isinstance(result, CallToolResult)
        assert not result.is_error

        data = _decode(result.content)
        assert len(data) == 2
        assert {r["slug"] for r in data} == {"winter_27", "spring_27"}

    @pytest.mark.asyncio
    async def test_handle_call_tool_unknown_tool_raises(self, server):
        """Should raise ValueError for tools the server does not implement."""
        with pytest.raises(ValueError, match="Unknown tool: nope"):
            await server._handle_call_tool(
                _request_ctx("tools/call"),
                CallToolRequestParams(name="nope"),
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("name", "arguments"),
        [
            ("search_release_notes", {"release_slug": "winter_27", "locale": "pt-BR"}),
            ("get_release_summary", {"release_slug": "winter_27", "locale": "pt-BR"}),
            ("list_releases", {}),
            (
                "compare_releases",
                {"from_slug": "winter_27", "to_slug": "spring_27", "locale": "pt-BR"},
            ),
        ],
    )
    async def test_call_tool_dispatches_every_registered_tool(self, server, name, arguments):
        """Should route each tool name to its implementation."""
        contents = await server.call_tool(name, arguments)

        assert contents
        assert contents[0].text


class TestCreateServer:
    """Tests for create_server function."""

    @pytest.mark.asyncio
    async def test_creates_server_with_default_dir(self):
        """Should create a lowlevel Server with the tools/list handler wired."""
        lowlevel = create_server()

        assert isinstance(lowlevel, Server)
        entry = lowlevel.get_request_handler("tools/list")
        assert entry is not None

        result = await entry.handler(_request_ctx("tools/list"), PaginatedRequestParams())
        assert {t.name for t in result.tools} == TOOL_NAMES

    def test_creates_server_with_custom_dir(self):
        """Should wire the custom releases directory into the MCP server."""
        mcp = ReleaseNotesMCPServer(releases_dir=Path("/custom/path"))

        assert mcp.releases_dir == Path("/custom/path")
        entry = mcp.server.get_request_handler("tools/call")
        assert entry is not None
        assert entry.params_type is CallToolRequestParams
