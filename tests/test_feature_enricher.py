"""Tests for src/feature_enricher.py — release-level enrichment coverage."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.feature_enricher import FeatureEnricher


class TestEnrichRelease:
    """enrich_release: per-release multi-file enrichment."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_pt_br_dir(self, tmp_path: Path) -> None:
        enricher = FeatureEnricher(llm=AsyncMock())
        with patch("src.feature_enricher.RELEASES_DIR", str(tmp_path)):
            result = await enricher.enrich_release("nonexistent")
        assert result == {}

    @pytest.mark.asyncio
    async def test_processes_all_md_files(self, tmp_path: Path) -> None:
        release_dir = tmp_path / "test_release" / "pt_BR"
        release_dir.mkdir(parents=True)
        (release_dir / "cat1.md").write_text(
            "## Category 1\n\n| Recurso | Usuários |\n| :--- | :---: |\n| **F1** | ✅ |\n"
        )

        mock_llm = AsyncMock()
        mock_llm.generate_text.return_value = json.dumps(
            {
                "introduction": "Test intro.",
                "features": [
                    {"name": "F1", "description": "Desc", "impact": "alto", "audience": "ambos"}
                ],
            }
        )

        enricher = FeatureEnricher(llm=mock_llm)
        with patch("src.feature_enricher.RELEASES_DIR", str(tmp_path)):
            result = await enricher.enrich_release("test_release", "Test Release")

        assert len(result) == 1
        assert "cat1" in result

    @pytest.mark.asyncio
    async def test_loads_meta_for_context(self, tmp_path: Path) -> None:
        release_dir = tmp_path / "test_release"
        release_dir.mkdir(parents=True)
        (release_dir / ".meta.json").write_text(
            json.dumps(
                {
                    "name": "Test Release",
                    "total_features": 1,
                    "categories": [{"name": "Cat", "count": 1}],
                }
            )
        )
        pt_br = release_dir / "pt_BR"
        pt_br.mkdir()
        (pt_br / "cat.md").write_text(
            "## Cat\n\n| Recurso | Usuários |\n| :--- | :---: |\n| **F1** | ✅ |\n"
        )

        mock_llm = AsyncMock()
        mock_llm.generate_text.return_value = json.dumps(
            {
                "introduction": "Intro text for category",
                "features": [
                    {
                        "name": "F1",
                        "description": "Description of feature one with details",
                        "impact": "médio",
                        "audience": "admins",
                    }
                ],
            }
        )

        enricher = FeatureEnricher(llm=mock_llm)
        with patch("src.feature_enricher.RELEASES_DIR", str(tmp_path)):
            result = await enricher.enrich_release("test_release")

        assert len(result) == 1
        assert result["cat"].medium_impact_count == 1


class TestParseLLMResponse:
    """_parse_llm_response: tolerates mismatched feature counts."""

    def test_extra_features_in_response_still_parses(self) -> None:
        enricher = FeatureEnricher(llm=AsyncMock())
        response = json.dumps(
            {
                "introduction": "Test category overview",
                "features": [
                    {
                        "name": "Extra",
                        "description": "Detailed description of feature",
                        "impact": "alto",
                        "audience": "ambos",
                    }
                ],
            }
        )
        result = enricher._parse_llm_response(response, [{"name": "Original"}])
        assert result is not None


class TestExtractCategoryName:
    """_extract_category_name: skips release headings."""

    def test_h1_heading_extracted(self) -> None:
        assert FeatureEnricher._extract_category_name("# My Category\n", "fb") == "My Category"

    def test_release_heading_skipped_uses_fallback(self) -> None:
        assert FeatureEnricher._extract_category_name("# Release Notes\n", "fb") == "Fb"


class TestExtractFeatures:
    """_extract_features_from_markdown: parses table rows."""

    def test_skips_separator_row(self) -> None:
        content = "| Recurso | Usuários |\n| :--- | :---: |\n| **F1** | ✅ |\n"
        features = FeatureEnricher._extract_features_from_markdown(content)
        assert len(features) == 1
