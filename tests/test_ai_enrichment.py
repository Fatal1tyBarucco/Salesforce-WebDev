"""Tests for feature_enricher.py and release_summarizer.py."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from src.feature_enricher import (
    CategoryEnrichment,
    EnrichedFeature,
    FeatureEnricher,
)
from src.release_summarizer import (
    CategoryHighlight,
    ReleaseSummary,
    ReleaseSummarizer,
)

# ---------------------------------------------------------------------------
# FeatureEnricher tests
# ---------------------------------------------------------------------------


class TestEnrichedFeature:
    def test_to_markdown_row_alto(self) -> None:
        f = EnrichedFeature(
            name="Voice Feature",
            description="Permite interação por voz com Agentforce.",
            impact="alto",
            availability="usuários",
        )
        row = f.to_markdown_row()
        assert "Voice Feature" in row
        assert "🔴" in row
        assert "Permite interação" in row

    def test_to_markdown_row_medio(self) -> None:
        f = EnrichedFeature(name="Test", description="Desc", impact="médio")
        assert "🟡" in f.to_markdown_row()

    def test_to_markdown_row_baixo(self) -> None:
        f = EnrichedFeature(name="Test", description="Desc", impact="baixo")
        assert "🟢" in f.to_markdown_row()

    def test_to_markdown_row_long_description(self) -> None:
        f = EnrichedFeature(
            name="Test",
            description="A" * 200,
            impact="alto",
        )
        row = f.to_markdown_row()
        assert "…" in row


class TestCategoryEnrichment:
    def test_defaults(self) -> None:
        e = CategoryEnrichment(
            category_name="Test",
            category_slug="test",
            introduction="Intro",
        )
        assert e.total_features == 0
        assert e.high_impact_count == 0


class TestFeatureEnricher:
    @pytest.mark.asyncio
    async def test_enrich_category_empty(self) -> None:
        enricher = FeatureEnricher(llm=AsyncMock())
        result = await enricher.enrich_category("Test", "test", [])
        assert result.total_features == 0
        assert "sem recursos" in result.introduction

    @pytest.mark.asyncio
    async def test_enrich_category_with_llm_response(self) -> None:
        mock_llm = AsyncMock()
        mock_llm.generate_text.return_value = json.dumps(
            {
                "introduction": "Categoria Agentforce com foco em IA.",
                "features": [
                    {
                        "name": "Voice Feature",
                        "description": "Permite interação por voz.",
                        "impact": "alto",
                        "audience": "usuários",
                    },
                    {
                        "name": "Basic Feature",
                        "description": "Melhoria menor.",
                        "impact": "baixo",
                        "audience": "admins",
                    },
                ],
            }
        )

        enricher = FeatureEnricher(llm=mock_llm)
        result = await enricher.enrich_category(
            "Agentforce",
            "agentforce",
            [
                {"name": "Voice Feature", "availability": "usuários"},
                {"name": "Basic Feature", "availability": "admins"},
            ],
            release_name="Summer '26",
        )

        assert result.total_features == 2
        assert result.high_impact_count == 1
        assert result.low_impact_count == 1
        assert "Agentforce" in result.introduction or "IA" in result.introduction
        assert result.features[0].name == "Voice Feature"

    @pytest.mark.asyncio
    async def test_enrich_category_llm_returns_none(self) -> None:
        mock_llm = AsyncMock()
        mock_llm.generate_text.return_value = None

        enricher = FeatureEnricher(llm=mock_llm)
        result = await enricher.enrich_category("Test", "test", [{"name": "Feature A"}])

        # Should use fallback
        assert result.total_features == 1
        assert result.features[0].name == "Feature A"

    @pytest.mark.asyncio
    async def test_enrich_category_llm_returns_invalid_json(self) -> None:
        mock_llm = AsyncMock()
        mock_llm.generate_text.return_value = "not valid json"

        enricher = FeatureEnricher(llm=mock_llm)
        result = await enricher.enrich_category("Test", "test", [{"name": "Feature A"}])

        # Should use fallback
        assert result.total_features == 1

    @pytest.mark.asyncio
    async def test_enrich_category_llm_returns_markdown_fenced_json(self) -> None:
        mock_llm = AsyncMock()
        mock_llm.generate_text.return_value = '```json\n{"introduction": "Test", "features": [{"name": "F1", "description": "D1", "impact": "alto", "audience": "ambos"}]}\n```'

        enricher = FeatureEnricher(llm=mock_llm)
        result = await enricher.enrich_category("Test", "test", [{"name": "F1"}])

        assert result.total_features == 1
        assert result.features[0].impact == "alto"

    def test_extract_category_name_from_heading(self) -> None:
        content = "## Agentforce\n\nSome content"
        assert FeatureEnricher._extract_category_name(content, "fallback") == "Agentforce"

    def test_extract_category_name_fallback(self) -> None:
        assert FeatureEnricher._extract_category_name("", "my_file") == "My File"

    def test_extract_features_from_markdown(self) -> None:
        content = """## Test

| Recurso | Usuários | Admins | Config | Contato | Docs |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Feature A** | ✅ | ❌ | ❌ | ❌ | |
| **Feature B** | ✅ | ✅ | ❌ | ❌ | |
"""
        features = FeatureEnricher._extract_features_from_markdown(content)
        assert len(features) == 2
        assert features[0]["name"] == "Feature A"
        assert "usuários" in features[0]["availability"]

    def test_extract_features_empty(self) -> None:
        assert FeatureEnricher._extract_features_from_markdown("") == []


class TestFallbackEnrichment:
    def test_security_keyword_high_impact(self) -> None:
        enricher = FeatureEnricher(llm=AsyncMock())
        result = enricher._generate_fallback_enrichment(
            "Security", "security", [{"name": "MFA Enhancement"}]
        )
        assert result.high_impact_count == 1
        assert result.features[0].impact == "alto"

    def test_beta_keyword_medium_impact(self) -> None:
        enricher = FeatureEnricher(llm=AsyncMock())
        result = enricher._generate_fallback_enrichment(
            "Test", "test", [{"name": "New Beta Feature"}]
        )
        assert result.medium_impact_count == 1


# ---------------------------------------------------------------------------
# ReleaseSummarizer tests
# ---------------------------------------------------------------------------


class TestReleaseSummarizer:
    @pytest.mark.asyncio
    async def test_summarize_no_dir(self, tmp_path: Path) -> None:
        summarizer = ReleaseSummarizer(str(tmp_path))
        result = await summarizer.summarize("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_summarize_with_llm(self, tmp_path: Path) -> None:
        release_dir = tmp_path / "summer_26" / "pt_BR"
        release_dir.mkdir(parents=True)
        (release_dir / "agentforce.md").write_text(
            "## Agentforce\n\n> **2 recursos**\n\n"
            "| Recurso | Usuários | Admins | Config | Contato | Docs |\n"
            "| :--- | :---: | :---: | :---: | :---: | :---: |\n"
            "| **Voice** | ✅ | ❌ | ❌ | ❌ | |\n"
            "| **Chat** | ✅ | ❌ | ❌ | ❌ | |\n"
        )
        (tmp_path / "summer_26" / ".meta.json").write_text(
            json.dumps(
                {
                    "name": "Summer '26",
                    "total_features": 2,
                    "categories": [{"name": "Agentforce", "count": 2}],
                }
            )
        )

        mock_llm = AsyncMock()
        mock_llm.generate_text.return_value = json.dumps(
            {
                "executive_summary": "Summer '26 traz 2 recursos em Agentforce.",
                "business_impact": "Impacto positivo no atendimento.",
                "strategic_themes": ["AI-First"],
                "top_categories": [
                    {
                        "name": "Agentforce",
                        "feature_count": 2,
                        "percentage": 100.0,
                        "top_feature": "Voice",
                        "theme": "AI",
                    }
                ],
                "migration_notes": "Nenhuma nota.",
            }
        )

        summarizer = ReleaseSummarizer(str(tmp_path), llm=mock_llm)
        result = await summarizer.summarize("summer_26")

        assert result is not None
        assert result.total_features == 2
        assert "Summer" in result.executive_summary
        assert len(result.strategic_themes) == 1

    @pytest.mark.asyncio
    async def test_summarize_llm_returns_none(self, tmp_path: Path) -> None:
        release_dir = tmp_path / "summer_26" / "pt_BR"
        release_dir.mkdir(parents=True)
        (release_dir / "test.md").write_text(
            "## Test\n\n> **1 recurso**\n\n"
            "| Recurso | Usuários | Admins | Config | Contato | Docs |\n"
            "| :--- | :---: | :---: | :---: | :---: | :---: |\n"
            "| **F1** | ✅ | ❌ | ❌ | ❌ | |\n"
        )
        (tmp_path / "summer_26" / ".meta.json").write_text(
            json.dumps(
                {
                    "name": "Summer '26",
                    "total_features": 1,
                    "categories": [{"name": "Test", "count": 1}],
                }
            )
        )

        mock_llm = AsyncMock()
        mock_llm.generate_text.return_value = None

        summarizer = ReleaseSummarizer(str(tmp_path), llm=mock_llm)
        result = await summarizer.summarize("summer_26")

        assert result is not None
        assert result.confidence == 0.7  # fallback confidence

    def test_to_markdown(self) -> None:
        summary = ReleaseSummary(
            release_slug="summer_26",
            release_name="Summer '26",
            total_features=100,
            total_categories=10,
            executive_summary="Test summary.",
            business_impact="Business impact.",
            strategic_themes=["AI-First", "Security"],
            top_categories=[
                CategoryHighlight("Agentforce", 47, 47.0, "Voice", "AI"),
            ],
            migration_notes="No migration notes.",
            confidence=0.95,
        )

        md = ReleaseSummarizer().to_markdown(summary)
        assert "Summer '26" in md
        assert "100 recursos" in md
        assert "AI-First" in md
        assert "Agentforce" in md
        assert "Business impact" in md

    def test_extract_category_name(self) -> None:
        assert (
            ReleaseSummarizer._extract_category_name("## Agentforce\n", "fallback") == "Agentforce"
        )

    def test_extract_feature_names(self) -> None:
        content = """| Recurso | Usuários |
| :--- | :---: |
| **Feature A** | ✅ |
| **Feature B** | ✅ |
"""
        names = ReleaseSummarizer._extract_feature_names(content)
        assert len(names) == 2
        assert "Feature A" in names

    def test_extract_themes(self) -> None:
        content = "agentforce ai einstein security compliance"
        themes = ReleaseSummarizer._extract_themes(content)
        assert any("AI" in t for t in themes)
        assert any("Segurança" in t or "Security" in t for t in themes)


class TestCategoryHighlight:
    def test_defaults(self) -> None:
        h = CategoryHighlight(name="Test", feature_count=10, percentage=50.0)
        assert h.top_feature == ""
        assert h.theme == ""
