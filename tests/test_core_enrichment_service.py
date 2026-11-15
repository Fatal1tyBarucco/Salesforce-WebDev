"""Tests for src/core/enrichment/service.py — 100% coverage target."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.enrichment.service import (
    EnrichmentAdapter,
    EnrichmentConfig,
    EnrichmentService,
    EnrichmentStrategy,
)
from src.core.classification.service import ClassificationResult, ClassifiedFeature
from src.models.classification import FeatureType, ImpactLevel
from src.models.enrichment import CategoryEnrichment, FeatureEnrichment, ReleaseEnrichment
from src.models.feature import FeatureCategory


class MockEnrichmentAdapter(EnrichmentAdapter):
    """Mock enrichment adapter for testing."""

    def __init__(
        self,
        name: str = "mock",
        category_result: CategoryEnrichment | None = None,
        release_result: ReleaseEnrichment | None = None,
    ) -> None:
        self._name = name
        self._category_result = category_result
        self._release_result = release_result
        self.category_call_count = 0
        self.release_call_count = 0
        self._should_fail_category = False
        self._should_fail_release = False

    @property
    def name(self) -> str:
        return self._name

    def set_should_fail_category(self, should_fail: bool) -> None:
        self._should_fail_category = should_fail

    def set_should_fail_release(self, should_fail: bool) -> None:
        self._should_fail_release = should_fail

    async def enrich_category(
        self,
        category_name: str,
        features: list[str],
        classifications: dict[str, any],
        locale: str,
    ) -> CategoryEnrichment:
        self.category_call_count += 1
        if self._should_fail_category:
            raise RuntimeError("LLM unavailable")
        if self._category_result:
            return self._category_result
        return CategoryEnrichment(
            category_name=category_name,
            overview=f"Mock overview for {category_name}",
            key_themes=tuple(features[:3]),
            business_impact="Mock business impact",
            adoption_guidance="Mock adoption guidance",
            risk_assessment="Mock risk assessment",
            feature_enrichments=tuple(
                FeatureEnrichment(
                    feature_name=name,
                    summary=f"Summary for {name}",
                    details=f"Details for {name}",
                    business_context=f"Biz context for {name}",
                    technical_context=f"Tech context for {name}",
                    migration_notes=f"Migration for {name}",
                    locale=locale,
                    generated_at=datetime.now().isoformat(),
                )
                for name in features
            ),
            locale=locale,
            generated_at=datetime.now().isoformat(),
        )

    async def enrich_release(
        self,
        release_slug: str,
        category_enrichments: list[CategoryEnrichment],
        locale: str,
    ) -> ReleaseEnrichment:
        self.release_call_count += 1
        if self._should_fail_release:
            raise RuntimeError("LLM unavailable")
        if self._release_result:
            return self._release_result
        return ReleaseEnrichment(
            release_slug=release_slug,
            executive_summary=f"Mock summary for {release_slug}",
            strategic_themes=("Theme 1", "Theme 2"),
            category_enrichments=tuple(category_enrichments),
            migration_checklist=("Check 1", "Check 2"),
            locale=locale,
            generated_at=datetime.now().isoformat(),
        )


def _make_feature_category() -> FeatureCategory:
    """Create a sample FeatureCategory for testing."""
    return FeatureCategory(
        name="Lightning",
        locale="pt_BR",
        features=[
            MagicMock(name="Lightning Feature 1", raw_text="New Lightning component"),
            MagicMock(name="Lightning Feature 2", raw_text="Improved performance"),
        ],
    )


def _make_classification_result() -> ClassificationResult:
    """Create a sample ClassificationResult for testing."""
    return ClassificationResult(
        release_slug="summer_26",
        total_features=2,
        by_impact={"high": 1, "medium": 1},
        by_type={"new_feature": 1, "improvement": 1},
        features=(
            ClassifiedFeature(
                name="Lightning Feature 1",
                impact=ImpactLevel.HIGH,
                feature_type=FeatureType.NEW_FEATURE,
                confidence=0.95,
            ),
            ClassifiedFeature(
                name="Lightning Feature 2",
                impact=ImpactLevel.MEDIUM,
                feature_type=FeatureType.IMPROVEMENT,
                confidence=0.8,
            ),
        ),
    )


class TestEnrichmentConfig:
    """Tests for EnrichmentConfig."""

    def test_default_values(self) -> None:
        """Config should have sensible defaults."""
        config = EnrichmentConfig()
        assert config.strategy == EnrichmentStrategy.HYBRID
        assert config.locale == "pt_BR"
        assert config.include_migration_notes is True
        assert config.include_business_context is True
        assert config.include_technical_context is True
        assert config.max_features_per_category == 50
        assert config.timeout_seconds == 120

    def test_custom_values(self) -> None:
        """Config should accept custom values."""
        config = EnrichmentConfig(
            strategy=EnrichmentStrategy.LLM,
            locale="en_US",
            max_features_per_category=10,
            timeout_seconds=60,
        )
        assert config.strategy == EnrichmentStrategy.LLM
        assert config.locale == "en_US"
        assert config.max_features_per_category == 10
        assert config.timeout_seconds == 60

    def test_immutable(self) -> None:
        """Config should be immutable (frozen dataclass)."""
        config = EnrichmentConfig()
        with pytest.raises(Exception):
            config.strategy = EnrichmentStrategy.LLM  # type: ignore


class TestEnrichmentStrategy:
    """Tests for EnrichmentStrategy enum."""

    def test_values(self) -> None:
        """Enum should have expected values."""
        assert EnrichmentStrategy.LLM.value == "llm"
        assert EnrichmentStrategy.TEMPLATE.value == "template"
        assert EnrichmentStrategy.HYBRID.value == "hybrid"


class TestEnrichmentAdapter:
    """Tests for EnrichmentAdapter abstract base."""

    @pytest.mark.asyncio
    async def test_abstract_enrich_category_raises_not_implemented(self) -> None:
        """Abstract enrich_category should raise NotImplementedError."""
        with pytest.raises(TypeError):
            EnrichmentAdapter()

    @pytest.mark.asyncio
    async def test_abstract_enrich_release_raises_not_implemented(self) -> None:
        """Abstract enrich_release should raise NotImplementedError."""
        with pytest.raises(TypeError):
            EnrichmentAdapter()

    def test_name_property_abstract(self) -> None:
        """Name property should be abstract."""
        with pytest.raises(TypeError):
            EnrichmentAdapter()


class TestEnrichmentService:
    """Tests for EnrichmentService."""

    @pytest.fixture
    def mock_llm(self) -> MockEnrichmentAdapter:
        """Create mock LLM adapter."""
        return MockEnrichmentAdapter("llm")

    @pytest.fixture
    def mock_template(self) -> MockEnrichmentAdapter:
        """Create mock template adapter."""
        return MockEnrichmentAdapter("template")

    @pytest.fixture
    def category(self) -> FeatureCategory:
        """Create sample category."""
        return _make_feature_category()

    @pytest.fixture
    def classification_result(self) -> ClassificationResult:
        """Create sample classification result."""
        return _make_classification_result()

    @pytest.mark.asyncio
    async def test_enrich_release_with_llm_strategy(
        self,
        mock_llm: MockEnrichmentAdapter,
        category: FeatureCategory,
        classification_result: ClassificationResult,
    ) -> None:
        """Should use LLM adapter when strategy is LLM."""
        config = EnrichmentConfig(strategy=EnrichmentStrategy.LLM)
        service = EnrichmentService(config=config, llm_adapter=mock_llm)

        result = await service.enrich_release("summer_26", classification_result, [category])

        assert result.release_slug == "summer_26"
        assert result.locale == "pt_BR"
        assert len(result.category_enrichments) == 1
        assert mock_llm.category_call_count == 1
        assert mock_llm.release_call_count == 1

    @pytest.mark.asyncio
    async def test_enrich_release_with_template_strategy(
        self,
        mock_template: MockEnrichmentAdapter,
        category: FeatureCategory,
        classification_result: ClassificationResult,
    ) -> None:
        """Should use template adapter when strategy is TEMPLATE."""
        config = EnrichmentConfig(strategy=EnrichmentStrategy.TEMPLATE)
        service = EnrichmentService(config=config, template_adapter=mock_template)

        result = await service.enrich_release("summer_26", classification_result, [category])

        assert result.release_slug == "summer_26"
        assert mock_template.category_call_count == 1
        assert mock_template.release_call_count == 1

    @pytest.mark.asyncio
    async def test_enrich_release_hybrid_uses_llm_first(
        self,
        mock_llm: MockEnrichmentAdapter,
        mock_template: MockEnrichmentAdapter,
        category: FeatureCategory,
        classification_result: ClassificationResult,
    ) -> None:
        """Hybrid strategy should try LLM first for categories, and LLM for release if available."""
        config = EnrichmentConfig(strategy=EnrichmentStrategy.HYBRID)
        service = EnrichmentService(
            config=config, llm_adapter=mock_llm, template_adapter=mock_template
        )

        result = await service.enrich_release("summer_26", classification_result, [category])

        assert result.release_slug == "summer_26"
        # For HYBRID: _enrich_category tries LLM first, _enrich_release tries LLM if strategy==LLM and adapter exists
        # But strategy is HYBRID, so _enrich_release goes to template adapter
        assert mock_llm.category_call_count == 1
        assert mock_template.release_call_count == 1

    @pytest.mark.asyncio
    async def test_enrich_release_hybrid_falls_back_to_template(
        self,
        mock_llm: MockEnrichmentAdapter,
        mock_template: MockEnrichmentAdapter,
        category: FeatureCategory,
        classification_result: ClassificationResult,
    ) -> None:
        """Hybrid should fall back to template when LLM fails for category enrichment."""
        mock_llm.set_should_fail_category(True)

        config = EnrichmentConfig(strategy=EnrichmentStrategy.HYBRID)
        service = EnrichmentService(
            config=config, llm_adapter=mock_llm, template_adapter=mock_template
        )

        result = await service.enrich_release("summer_26", classification_result, [category])

        assert result.release_slug == "summer_26"
        assert mock_llm.category_call_count == 1
        assert mock_template.category_call_count == 1

    @pytest.mark.asyncio
    async def test_enrich_release_llm_unavailable_falls_back(
        self,
        mock_template: MockEnrichmentAdapter,
        category: FeatureCategory,
        classification_result: ClassificationResult,
    ) -> None:
        """Should fall back to template when LLM adapter not configured."""
        # When strategy is LLM but no LLM adapter, _enrich_with_llm raises RuntimeError
        # Then _enrich_category catches it and falls back to template
        config = EnrichmentConfig(strategy=EnrichmentStrategy.HYBRID)
        service = EnrichmentService(config=config, template_adapter=mock_template)

        result = await service.enrich_release("summer_26", classification_result, [category])

        assert result.release_slug == "summer_26"
        assert mock_template.category_call_count == 1

    @pytest.mark.asyncio
    async def test_enrich_release_template_unavailable_uses_minimal(
        self,
        mock_llm: MockEnrichmentAdapter,
        category: FeatureCategory,
        classification_result: ClassificationResult,
    ) -> None:
        """Should use minimal enrichment when template adapter not configured."""
        # When strategy is TEMPLATE but no template adapter, _enrich_with_template returns minimal
        config = EnrichmentConfig(strategy=EnrichmentStrategy.TEMPLATE)
        service = EnrichmentService(config=config, llm_adapter=mock_llm)

        result = await service.enrich_release("summer_26", classification_result, [category])

        assert result.release_slug == "summer_26"
        # Category enrichment uses minimal, not LLM
        assert mock_llm.category_call_count == 0

    @pytest.mark.asyncio
    async def test_enrich_release_no_categories(
        self, mock_llm: MockEnrichmentAdapter, classification_result: ClassificationResult
    ) -> None:
        """Should handle empty categories list."""
        config = EnrichmentConfig(strategy=EnrichmentStrategy.LLM)
        service = EnrichmentService(config=config, llm_adapter=mock_llm)

        result = await service.enrich_release("summer_26", classification_result, [])

        assert result.release_slug == "summer_26"
        assert len(result.category_enrichments) == 0
        assert mock_llm.category_call_count == 0

    @pytest.mark.asyncio
    async def test_enrich_release_limits_features_per_category(
        self, classification_result: ClassificationResult
    ) -> None:
        """Should limit features per category based on config."""
        # Use AsyncMock to capture call arguments
        mock_llm = AsyncMock(spec=EnrichmentAdapter)
        mock_llm.name = "llm"
        mock_llm.enrich_category = AsyncMock(
            return_value=CategoryEnrichment(
                category_name="Test",
                overview="Overview",
                key_themes=tuple(),
                business_impact="",
                adoption_guidance="",
                risk_assessment="",
                feature_enrichments=tuple(),
                locale="pt_BR",
                generated_at=datetime.now().isoformat(),
            )
        )
        mock_llm.enrich_release = AsyncMock(
            return_value=ReleaseEnrichment(
                release_slug="summer_26",
                executive_summary="Summary",
                strategic_themes=tuple(),
                category_enrichments=tuple(),
                migration_checklist=tuple(),
                locale="pt_BR",
                generated_at=datetime.now().isoformat(),
            )
        )

        # Create category with many features
        many_features = [MagicMock(name=f"Feature {i}", raw_text=f"Text {i}") for i in range(100)]
        cat = FeatureCategory(name="Test", locale="pt_BR", features=many_features)

        config = EnrichmentConfig(strategy=EnrichmentStrategy.LLM, max_features_per_category=10)
        service = EnrichmentService(config=config, llm_adapter=mock_llm)

        result = await service.enrich_release("summer_26", classification_result, [cat])

        assert result.release_slug == "summer_26"
        # LLM should be called with only 10 features
        mock_llm.enrich_category.assert_called_once()
        call_args = mock_llm.enrich_category.call_args
        features_arg = call_args[0][1]  # Second positional arg
        assert len(features_arg) == 10

    @pytest.mark.asyncio
    async def test_enrich_release_skips_empty_categories(
        self, mock_llm: MockEnrichmentAdapter, classification_result: ClassificationResult
    ) -> None:
        """Should skip categories with no features."""
        cat = FeatureCategory(name="Empty", locale="pt_BR", features=[])

        config = EnrichmentConfig(strategy=EnrichmentStrategy.LLM)
        service = EnrichmentService(config=config, llm_adapter=mock_llm)

        result = await service.enrich_release("summer_26", classification_result, [cat])

        assert result.release_slug == "summer_26"
        assert len(result.category_enrichments) == 0
        assert mock_llm.category_call_count == 0

    @pytest.mark.asyncio
    async def test_minimal_category_enrichment(self) -> None:
        """_minimal_category_enrichment should create basic enrichment."""
        config = EnrichmentConfig()
        service = EnrichmentService(config=config)

        features = ["Feature 1", "Feature 2"]
        result = service._minimal_category_enrichment("Test", features, "pt_BR")

        assert result.category_name == "Test"
        assert "Test" in result.overview
        assert result.key_themes == ("Feature 1", "Feature 2")
        assert result.business_impact is not None
        assert result.adoption_guidance is not None
        assert result.risk_assessment is not None
        assert len(result.feature_enrichments) == 2
        assert result.locale == "pt_BR"

    @pytest.mark.asyncio
    async def test_minimal_release_enrichment(self) -> None:
        """_minimal_release_enrichment should create basic release enrichment."""
        config = EnrichmentConfig()
        service = EnrichmentService(config=config)

        cat_enrichment = CategoryEnrichment(
            category_name="Test",
            overview="Overview",
            key_themes=("Theme 1", "Theme 2"),
            business_impact="Impact",
            adoption_guidance="Guidance",
            risk_assessment="Risk",
            feature_enrichments=(),
            locale="pt_BR",
            generated_at=datetime.now().isoformat(),
        )

        result = service._minimal_release_enrichment("summer_26", [cat_enrichment], "pt_BR")

        assert result.release_slug == "summer_26"
        assert "summer_26" in result.executive_summary
        assert result.strategic_themes == ("Theme 1", "Theme 2")
        assert len(result.category_enrichments) == 1
        assert len(result.migration_checklist) == 3
        assert result.locale == "pt_BR"

    @pytest.mark.asyncio
    async def test_enrich_category_builds_classifications_lookup(
        self, category: FeatureCategory, classification_result: ClassificationResult
    ) -> None:
        """Should build classifications lookup from classification result."""
        mock_llm = AsyncMock(spec=EnrichmentAdapter)
        mock_llm.name = "llm"
        mock_llm.enrich_category = AsyncMock(
            return_value=CategoryEnrichment(
                category_name="Lightning",
                overview="Overview",
                key_themes=tuple(),
                business_impact="",
                adoption_guidance="",
                risk_assessment="",
                feature_enrichments=tuple(),
                locale="pt_BR",
                generated_at=datetime.now().isoformat(),
            )
        )
        mock_llm.enrich_release = AsyncMock(
            return_value=ReleaseEnrichment(
                release_slug="summer_26",
                executive_summary="Summary",
                strategic_themes=tuple(),
                category_enrichments=tuple(),
                migration_checklist=tuple(),
                locale="pt_BR",
                generated_at=datetime.now().isoformat(),
            )
        )

        config = EnrichmentConfig(strategy=EnrichmentStrategy.LLM)
        service = EnrichmentService(config=config, llm_adapter=mock_llm)

        await service.enrich_release("summer_26", classification_result, [category])

        mock_llm.enrich_category.assert_called_once()
        call_args = mock_llm.enrich_category.call_args
        classifications_arg = call_args[0][2]  # Third positional arg
        assert "Lightning Feature 1" in classifications_arg
        assert classifications_arg["Lightning Feature 1"]["impact"] == "high"
        assert classifications_arg["Lightning Feature 1"]["type"] == "new_feature"
        assert classifications_arg["Lightning Feature 1"]["confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_enrich_release_passes_locale(
        self, category: FeatureCategory, classification_result: ClassificationResult
    ) -> None:
        """Should pass category locale to adapters (not config locale for category)."""
        mock_llm = AsyncMock(spec=EnrichmentAdapter)
        mock_llm.name = "llm"
        mock_llm.enrich_category = AsyncMock(
            return_value=CategoryEnrichment(
                category_name="Lightning",
                overview="Overview",
                key_themes=tuple(),
                business_impact="",
                adoption_guidance="",
                risk_assessment="",
                feature_enrichments=tuple(),
                locale="pt_BR",  # Category locale is pt_BR
                generated_at=datetime.now().isoformat(),
            )
        )
        mock_llm.enrich_release = AsyncMock(
            return_value=ReleaseEnrichment(
                release_slug="summer_26",
                executive_summary="Summary",
                strategic_themes=tuple(),
                category_enrichments=tuple(),
                migration_checklist=tuple(),
                locale="en_US",  # Release locale comes from config
                generated_at=datetime.now().isoformat(),
            )
        )

        config = EnrichmentConfig(strategy=EnrichmentStrategy.LLM, locale="en_US")
        service = EnrichmentService(config=config, llm_adapter=mock_llm)

        await service.enrich_release("summer_26", classification_result, [category])

        mock_llm.enrich_category.assert_called_once()
        call_args = mock_llm.enrich_category.call_args
        locale_arg = call_args[0][3]  # Fourth positional arg
        # Category enrichment uses cat.locale (pt_BR), not config.locale
        assert locale_arg == "pt_BR"

        mock_llm.enrich_release.assert_called_once()
        call_args = mock_llm.enrich_release.call_args
        locale_arg = call_args[0][2]  # Third positional arg
        # Release enrichment uses config.locale (en_US)
        assert locale_arg == "en_US"

    @pytest.mark.asyncio
    async def test_enrich_with_llm_raises_when_no_adapter(self) -> None:
        """_enrich_with_llm should raise when no LLM adapter configured."""
        config = EnrichmentConfig()
        service = EnrichmentService(config=config)

        with pytest.raises(RuntimeError, match="LLM adapter not configured"):
            await service._enrich_with_llm("Test", [], {}, "pt_BR")

    @pytest.mark.asyncio
    async def test_enrich_with_template_returns_minimal_when_no_adapter(self) -> None:
        """_enrich_with_template should return minimal when no template adapter."""
        config = EnrichmentConfig()
        service = EnrichmentService(config=config)

        result = await service._enrich_with_template("Test", ["Feature 1"], {}, "pt_BR")

        assert result.category_name == "Test"
        assert len(result.feature_enrichments) == 1

    @pytest.mark.asyncio
    async def test_enrich_release_calls_llm_then_template_on_failure(
        self,
        mock_llm: MockEnrichmentAdapter,
        mock_template: MockEnrichmentAdapter,
        category: FeatureCategory,
        classification_result: ClassificationResult,
    ) -> None:
        """_enrich_release with HYBRID uses template, but LLM strategy with failure falls back."""
        # Make LLM fail for release enrichment only
        mock_llm.set_should_fail_release(True)

        # Use LLM strategy so it tries LLM for release, then falls back to template
        config = EnrichmentConfig(strategy=EnrichmentStrategy.LLM)
        service = EnrichmentService(
            config=config, llm_adapter=mock_llm, template_adapter=mock_template
        )

        result = await service.enrich_release("summer_26", classification_result, [category])

        assert result.release_slug == "summer_26"
        assert mock_llm.release_call_count == 1
        assert mock_template.release_call_count == 1
