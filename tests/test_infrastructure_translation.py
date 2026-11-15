"""Tests for src/infrastructure/translation.py — 100% coverage target."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from src.infrastructure.translation import (
    LLMTranslationAdapter,
    MockTranslationAdapter,
    TranslationAdapter,
)
from src.models.enrichment import (
    CategoryEnrichment,
    FeatureEnrichment,
    ReleaseEnrichment,
)


class MockLLMAdapter:
    """Mock LLM adapter for testing translation."""

    def __init__(self) -> None:
        self.call_count = 0
        self.responses: list[str] = []

    async def _complete(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        self.call_count += 1
        if self.responses:
            return self.responses.pop(0)
        return f"[TRANSLATED] {prompt}"


def _make_enrichment() -> ReleaseEnrichment:
    """Create a sample ReleaseEnrichment for testing."""
    return ReleaseEnrichment(
        release_slug="summer_26",
        locale="pt_BR",
        executive_summary="Resumo executivo de teste.",
        strategic_themes=("Tema 1", "Tema 2"),
        category_enrichments=(
            CategoryEnrichment(
                category_name="Lightning",
                overview="Visão geral do Lightning.",
                key_themes=("Tema Lightning 1",),
                business_impact="Alto impacto no negócio.",
                adoption_guidance="Adotar imediatamente.",
                risk_assessment="Baixo risco.",
                feature_enrichments=(
                    FeatureEnrichment(
                        feature_name="Lightning Feature 1",
                        summary="Resumo da feature.",
                        details="Detalhes completos.",
                        business_context="Contexto de negócio.",
                        technical_context="Contexto técnico.",
                        migration_notes="Notas de migração.",
                        related_features=("Outra feature",),
                        tags=("tag1", "tag2"),
                        confidence=0.9,
                        locale="pt_BR",
                        generated_at="2026-05-01T10:00:00",
                    ),
                ),
                locale="pt_BR",
                generated_at="2026-05-01T10:00:00",
            ),
        ),
        migration_checklist=("Verificar deploy", "Testar funcionalidade"),
        generated_at="2026-05-01T10:00:00",
    )


class TestTranslationAdapter:
    """Tests for the abstract TranslationAdapter base class."""

    @pytest.mark.asyncio
    async def test_abstract_execute_raises_not_implemented(self) -> None:
        """Abstract execute should raise NotImplementedError."""
        adapter = TranslationAdapter()
        with pytest.raises(NotImplementedError):
            await adapter.execute(MagicMock())

    def test_name_property(self) -> None:
        """Base adapter name property."""
        adapter = TranslationAdapter()
        assert adapter.name == "translation_adapter"


class TestLLMTranslationAdapter:
    """Tests for LLMTranslationAdapter."""

    @pytest.fixture
    def mock_llm(self) -> MockLLMAdapter:
        """Create mock LLM adapter."""
        return MockLLMAdapter()

    @pytest.fixture
    def adapter(self, mock_llm: MockLLMAdapter) -> LLMTranslationAdapter:
        """Create adapter with mock LLM."""
        return LLMTranslationAdapter(mock_llm, target_locale="en_US", source_locale="pt_BR")

    @pytest.fixture
    def enrichment(self) -> ReleaseEnrichment:
        """Create sample enrichment."""
        return _make_enrichment()

    @pytest.mark.asyncio
    async def test_name_property(self, adapter: LLMTranslationAdapter) -> None:
        """Adapter name should include locales."""
        assert adapter.name == "llm_translation_pt_BR_to_en_US"

    @pytest.mark.asyncio
    async def test_execute_returns_original_when_locale_matches_target(
        self, adapter: LLMTranslationAdapter, enrichment: ReleaseEnrichment
    ) -> None:
        """Execute should return original enrichment if locale already matches target."""
        # Change enrichment locale to target
        enrichment_en = ReleaseEnrichment(
            release_slug=enrichment.release_slug,
            locale="en_US",
            executive_summary=enrichment.executive_summary,
            strategic_themes=enrichment.strategic_themes,
            category_enrichments=enrichment.category_enrichments,
            migration_checklist=enrichment.migration_checklist,
            generated_at=enrichment.generated_at,
        )

        result = await adapter.execute(enrichment_en)

        assert result is enrichment_en
        assert adapter._llm.call_count == 0

    @pytest.mark.asyncio
    async def test_execute_translates_all_fields(
        self,
        adapter: LLMTranslationAdapter,
        enrichment: ReleaseEnrichment,
        mock_llm: MockLLMAdapter,
    ) -> None:
        """Execute should translate all enrichment fields."""
        # Order of calls in _translate_category:
        # 1. overview
        # 2. key_themes (list)
        # 3. business_impact
        # 4. adoption_guidance
        # 5. risk_assessment
        # 6. For each feature:
        #    - feature_name
        #    - summary
        #    - details
        #    - business_context
        #    - technical_context
        #    - migration_notes
        #    - related_features (list)
        #    - tags (list)
        # 7. category_name (LAST)
        mock_llm.responses = [
            "Executive summary of test.",  # executive_summary
            "Theme 1\n---\nTheme 2",  # strategic_themes
            "Check deploy\n---\nTest functionality",  # migration_checklist
            # Category translation:
            "Lightning overview.",  # overview
            "Lightning Theme 1",  # key_themes
            "High business impact.",  # business_impact
            "Adopt immediately.",  # adoption_guidance
            "Low risk.",  # risk_assessment
            # Feature translation:
            "Lightning Feature 1",  # feature_name
            "Feature summary.",  # summary
            "Feature details.",  # details
            "Business context.",  # business_context
            "Technical context.",  # technical_context
            "Migration notes.",  # migration_notes
            "Other feature",  # related_features (list)
            "tag1\n---\ntag2",  # tags (list)
            "Lightning",  # category_name (LAST)
        ]

        result = await adapter.execute(enrichment)

        assert result.locale == "en_US"
        assert result.release_slug == "summer_26"
        assert result.executive_summary == "Executive summary of test."
        assert list(result.strategic_themes) == ["Theme 1", "Theme 2"]
        assert list(result.migration_checklist) == ["Check deploy", "Test functionality"]
        assert len(result.category_enrichments) == 1

        cat = result.category_enrichments[0]
        assert cat.category_name == "Lightning"
        assert cat.overview == "Lightning overview."
        assert list(cat.key_themes) == ["Lightning Theme 1"]
        assert cat.business_impact == "High business impact."
        assert cat.adoption_guidance == "Adopt immediately."
        assert cat.risk_assessment == "Low risk."
        assert cat.locale == "en_US"
        assert len(cat.feature_enrichments) == 1

        feat = cat.feature_enrichments[0]
        assert feat.feature_name == "Lightning Feature 1"
        assert feat.summary == "Feature summary."
        assert feat.details == "Feature details."
        assert feat.business_context == "Business context."
        assert feat.technical_context == "Technical context."
        assert feat.migration_notes == "Migration notes."
        assert list(feat.related_features) == ["Other feature"]
        assert list(feat.tags) == ["tag1", "tag2"]
        assert feat.confidence == 0.9
        assert feat.locale == "en_US"

    @pytest.mark.asyncio
    async def test_execute_handles_empty_optional_fields(
        self, adapter: LLMTranslationAdapter, mock_llm: MockLLMAdapter
    ) -> None:
        """Execute should handle enrichment with empty optional fields."""
        from src.models.enrichment import CategoryEnrichment, FeatureEnrichment

        empty_enrichment = ReleaseEnrichment(
            release_slug="summer_26",
            locale="pt_BR",
            executive_summary=None,
            strategic_themes=(),
            category_enrichments=(
                CategoryEnrichment(
                    category_name="Test",
                    overview=None,
                    key_themes=(),
                    business_impact=None,
                    adoption_guidance=None,
                    risk_assessment=None,
                    feature_enrichments=(
                        FeatureEnrichment(
                            feature_name="Test Feature",
                            summary=None,
                            details=None,
                            business_context=None,
                            technical_context=None,
                            migration_notes=None,
                            related_features=(),
                            tags=(),
                            confidence=0.5,
                            locale="pt_BR",
                            generated_at="2026-05-01T10:00:00",
                        ),
                    ),
                    locale="pt_BR",
                    generated_at="2026-05-01T10:00:00",
                ),
            ),
            migration_checklist=(),
            generated_at="2026-05-01T10:00:00",
        )

        # Only non-empty/None fields call LLM:
        # 1. feature_name = "Test Feature"
        # 2. category_name = "Test"
        mock_llm.responses = [
            "Test Feature",  # feature_name
            "Test",  # category_name
        ]

        result = await adapter.execute(empty_enrichment)

        assert result.locale == "en_US"
        assert result.executive_summary == ""
        assert result.strategic_themes == ()
        assert result.migration_checklist == ()
        assert len(result.category_enrichments) == 1
        assert result.category_enrichments[0].category_name == "Test"
        assert result.category_enrichments[0].overview == ""
        assert result.category_enrichments[0].key_themes == ()
        assert len(result.category_enrichments[0].feature_enrichments) == 1

    @pytest.mark.asyncio
    async def test_translate_returns_original_on_error(
        self, adapter: LLMTranslationAdapter, mock_llm: MockLLMAdapter
    ) -> None:
        """_translate should return original text on LLM error."""
        mock_llm.responses = []

        # Make _complete raise an exception
        async def failing_complete(*args: Any, **kwargs: Any) -> str:
            raise RuntimeError("LLM error")

        mock_llm._complete = failing_complete

        result = await adapter._translate("Original text")

        assert result == "Original text"

    @pytest.mark.asyncio
    async def test_translate_returns_empty_for_empty_input(
        self, adapter: LLMTranslationAdapter
    ) -> None:
        """_translate should return empty string for empty input."""
        result = await adapter._translate("")
        assert result == ""

        result = await adapter._translate(None)  # type: ignore[arg-type]
        assert result == ""

    @pytest.mark.asyncio
    async def test_translate_list_returns_original_on_length_mismatch(
        self, adapter: LLMTranslationAdapter, mock_llm: MockLLMAdapter
    ) -> None:
        """_translate_list should return original list when split length mismatches."""
        mock_llm.responses = ["Single item"]  # Only 1 item returned for 2

        items = ("Item 1", "Item 2")
        result = await adapter._translate_list(items)

        assert result == items

    @pytest.mark.asyncio
    async def test_translate_list_handles_empty_input(self, adapter: LLMTranslationAdapter) -> None:
        """_translate_list should return empty tuple for empty input."""
        result = await adapter._translate_list(())
        assert result == ()

    @pytest.mark.asyncio
    async def test_translate_category_translates_all_fields(
        self, adapter: LLMTranslationAdapter, mock_llm: MockLLMAdapter
    ) -> None:
        """_translate_category should translate all category fields."""
        from src.models.enrichment import CategoryEnrichment, FeatureEnrichment

        cat = CategoryEnrichment(
            category_name="Test Category",
            overview="Overview text",
            key_themes=("Theme 1",),
            business_impact="Impact",
            adoption_guidance="Guidance",
            risk_assessment="Risk",
            feature_enrichments=(
                FeatureEnrichment(
                    feature_name="Test Feature",
                    summary="Summary",
                    details="Details",
                    business_context="Biz context",
                    technical_context="Tech context",
                    migration_notes="Migration",
                    related_features=("Related",),
                    tags=("tag1",),
                    confidence=0.8,
                    locale="pt_BR",
                    generated_at="2026-05-01T10:00:00",
                ),
            ),
            locale="pt_BR",
            generated_at="2026-05-01T10:00:00",
        )

        # Order: overview, key_themes, business_impact, adoption_guidance, risk_assessment,
        # feature: feature_name, summary, details, business_context, technical_context,
        # migration_notes, related_features, tags,
        # category_name (LAST)
        mock_llm.responses = [
            "Translated overview",
            "Translated Theme 1",
            "Translated impact",
            "Translated guidance",
            "Translated risk",
            "Test Feature",
            "Translated summary",
            "Translated details",
            "Translated biz context",
            "Translated tech context",
            "Translated migration",
            "Translated related",
            "Translated tag1",
            "Test Category",
        ]

        result = await adapter._translate_category(cat)

        assert result.category_name == "Test Category"
        assert result.overview == "Translated overview"
        assert list(result.key_themes) == ["Translated Theme 1"]
        assert result.business_impact == "Translated impact"
        assert result.adoption_guidance == "Translated guidance"
        assert result.risk_assessment == "Translated risk"
        assert result.locale == "en_US"
        assert len(result.feature_enrichments) == 1

        feat = result.feature_enrichments[0]
        assert feat.feature_name == "Test Feature"
        assert feat.summary == "Translated summary"
        assert feat.details == "Translated details"
        assert feat.business_context == "Translated biz context"
        assert feat.technical_context == "Translated tech context"
        assert feat.migration_notes == "Translated migration"
        assert list(feat.related_features) == ["Translated related"]
        assert list(feat.tags) == ["Translated tag1"]
        assert feat.confidence == 0.8
        assert feat.locale == "en_US"


class TestMockTranslationAdapter:
    """Tests for MockTranslationAdapter."""

    @pytest.fixture
    def adapter(self) -> MockTranslationAdapter:
        """Create mock translation adapter."""
        return MockTranslationAdapter(target_locale="en_US")

    @pytest.fixture
    def enrichment(self) -> ReleaseEnrichment:
        """Create sample enrichment."""
        return _make_enrichment()

    @pytest.mark.asyncio
    async def test_name_property(self, adapter: MockTranslationAdapter) -> None:
        """Adapter name should include target locale."""
        assert adapter.name == "mock_translation_to_en_US"

    @pytest.mark.asyncio
    async def test_execute_returns_original_when_locale_matches(
        self, adapter: MockTranslationAdapter, enrichment: ReleaseEnrichment
    ) -> None:
        """Execute should return original enrichment if locale already matches."""
        enrichment_en = ReleaseEnrichment(
            release_slug=enrichment.release_slug,
            locale="en_US",
            executive_summary=enrichment.executive_summary,
            strategic_themes=enrichment.strategic_themes,
            category_enrichments=enrichment.category_enrichments,
            migration_checklist=enrichment.migration_checklist,
            generated_at=enrichment.generated_at,
        )

        result = await adapter.execute(enrichment_en)

        assert result is enrichment_en

    @pytest.mark.asyncio
    async def test_execute_changes_locale_only(
        self, adapter: MockTranslationAdapter, enrichment: ReleaseEnrichment
    ) -> None:
        """Execute should change locale but keep content unchanged."""
        result = await adapter.execute(enrichment)

        assert result.locale == "en_US"
        assert result.release_slug == enrichment.release_slug
        assert result.executive_summary == enrichment.executive_summary
        assert result.strategic_themes == enrichment.strategic_themes
        assert result.category_enrichments == enrichment.category_enrichments
        assert result.migration_checklist == enrichment.migration_checklist
        assert result.generated_at == enrichment.generated_at

    @pytest.mark.asyncio
    async def test_execute_preserves_category_structure(
        self, adapter: MockTranslationAdapter, enrichment: ReleaseEnrichment
    ) -> None:
        """Execute should preserve all category and feature enrichment structure."""
        result = await adapter.execute(enrichment)

        assert len(result.category_enrichments) == 1
        orig_cat = enrichment.category_enrichments[0]
        new_cat = result.category_enrichments[0]

        assert new_cat.category_name == orig_cat.category_name
        assert new_cat.overview == orig_cat.overview
        assert new_cat.key_themes == orig_cat.key_themes
        assert new_cat.business_impact == orig_cat.business_impact
        assert new_cat.adoption_guidance == orig_cat.adoption_guidance
        assert new_cat.risk_assessment == orig_cat.risk_assessment
        # Mock adapter preserves original category locale (doesn't translate nested objects)
        assert new_cat.locale == "pt_BR"
        assert new_cat.generated_at == orig_cat.generated_at

        orig_feat = orig_cat.feature_enrichments[0]
        new_feat = new_cat.feature_enrichments[0]

        assert new_feat.feature_name == orig_feat.feature_name
        assert new_feat.summary == orig_feat.summary
        assert new_feat.details == orig_feat.details
        assert new_feat.business_context == orig_feat.business_context
        assert new_feat.technical_context == orig_feat.technical_context
        assert new_feat.migration_notes == orig_feat.migration_notes
        assert new_feat.related_features == orig_feat.related_features
        assert new_feat.tags == orig_feat.tags
        assert new_feat.confidence == orig_feat.confidence
        # Mock adapter preserves original feature locale
        assert new_feat.locale == "pt_BR"
        assert new_feat.generated_at == orig_feat.generated_at
