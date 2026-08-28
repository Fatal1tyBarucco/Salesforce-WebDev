"""Tests for src/automation/export.py — 100% coverage target."""

import pytest


class TestExportReleaseJSON:
    """export_release_json: serializes release metadata to formatted JSON."""

    @pytest.mark.asyncio
    async def test_handles_missing_meta(self) -> None:
        from src.automation.export import export_release_json

        def load_meta(slug: str):
            return None

        result = await export_release_json(load_meta, "test_slug")
        assert result == "{}"

    @pytest.mark.asyncio
    async def test_returns_formatted_json(self) -> None:
        from src.automation.export import export_release_json

        def load_meta(slug: str):
            return {"name": "Test", "slug": slug}

        result = await export_release_json(load_meta, "test_slug")
        assert "Test" in result


class TestExportReleaseCSV:
    """export_release_csv: serializes release features to CSV."""

    @pytest.mark.asyncio
    async def test_handles_missing_meta(self) -> None:
        from src.automation.export import export_release_csv

        def load_meta(slug: str):
            return None

        result = await export_release_csv(load_meta, "test_slug")
        assert result == ""
