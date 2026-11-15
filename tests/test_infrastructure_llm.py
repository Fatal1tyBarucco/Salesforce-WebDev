"""Tests for src/infrastructure/llm.py — 100% coverage target."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from src.infrastructure.llm import (
    _PROVIDER_CHAIN,
    HeuristicClassificationAdapter,
    OpenRouterClassificationAdapter,
    OpenRouterEnrichmentAdapter,
    OpenRouterLLMAdapter,
    UnifiedLLMClient,
    _env_model_override,
    _ProviderConfig,
)
from src.models.enrichment import CategoryEnrichment, ReleaseEnrichment


class MockOpenRouterLLMAdapter(OpenRouterLLMAdapter):
    """Mock OpenRouter LLM adapter for testing."""

    def __init__(self) -> None:
        # Don't call parent __init__ to avoid API key requirements
        self.api_key = "test_key"
        self.model = "test-model"
        self.base_url = "https://openrouter.ai/api/v1"
        self.timeout = 60.0
        self._client = None
        self.call_count = 0
        self.responses: list[str] = []
        self._should_fail = False

    async def _complete(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 3000,
        response_format: dict[str, str] | None = None,
    ) -> str:
        self.call_count += 1
        if self._should_fail:
            raise RuntimeError("LLM unavailable")
        if self.responses:
            return self.responses.pop(0)
        return json.dumps(
            {
                "impact": "high",
                "type": "new_feature",
                "confidence": 0.9,
                "audience": "developers",
                "priority": "high",
                "justification": "Mock classification",
            }
        )


class TestUnifiedLLMClient:
    """Tests for UnifiedLLMClient."""

    def test_init_with_explicit_provider(self) -> None:
        """Should initialize with explicit provider."""
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"}):
            client = UnifiedLLMClient(provider="openrouter", model_name="custom-model")
            assert client.provider == "openrouter"
            assert client.model_name == "custom-model"
            assert client.api_key == "test_key"

    def test_init_auto_detects_provider(self) -> None:
        """Should auto-detect first available provider."""
        with patch.dict(
            "os.environ",
            {
                "OPENROUTER_API_KEY": "or_key",
                "OPENCODE_API_KEY": "oc_key",
                "GOOGLE_API_KEY": "gemini_key",
            },
        ):
            client = UnifiedLLMClient()
            assert client.provider == "openrouter"  # First in chain
            assert client.api_key == "or_key"

    def test_init_no_provider_returns_mock(self) -> None:
        """Should return mock responses when no provider configured."""
        with patch.dict("os.environ", {}, clear=True):
            client = UnifiedLLMClient()
            assert client.provider == "none"
            assert client.api_key == ""
            assert client.model_name == "mock"

    def test_generate_completion_returns_mock_when_no_provider(self) -> None:
        """Should return mock response when no provider available."""
        client = UnifiedLLMClient()
        client.provider = "none"

        result = client.generate_completion("Test prompt")

        assert "Mock LLM Response" in result
        assert "Test prompt" in result

    def test_generate_completion_with_system_instruction(self) -> None:
        """Should include system instruction in prompt."""
        client = UnifiedLLMClient()
        client.provider = "none"

        result = client.generate_completion("Test prompt", system_instruction="System prompt")

        assert "Mock LLM Response" in result

    def test_generate_completion_empty_prompt_raises(self) -> None:
        """Should raise ValueError for empty prompt."""
        client = UnifiedLLMClient()
        client.provider = "none"

        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            client.generate_completion("")

    def test_generate_completion_whitespace_prompt_raises(self) -> None:
        """Should raise ValueError for whitespace-only prompt."""
        client = UnifiedLLMClient()
        client.provider = "none"

        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            client.generate_completion("   ")

    @pytest.mark.asyncio
    async def test_generate_text_alias(self) -> None:
        """generate_text should alias generate_completion."""
        client = UnifiedLLMClient()
        client.provider = "none"

        result = await client.generate_text("Test prompt")

        assert "Mock LLM Response" in result

    @pytest.mark.asyncio
    async def test_classify_text_alias(self) -> None:
        """classify_text should alias generate_completion with categories."""
        client = UnifiedLLMClient()
        client.provider = "none"

        result = await client.classify_text("Feature text", categories=["cat1", "cat2"])

        assert "Mock LLM Response" in result

    def test_summarize(self) -> None:
        """summarize should generate completion with summary prompt."""
        client = UnifiedLLMClient()
        client.provider = "none"

        result = client.summarize("Long text to summarize", max_length=100)

        assert "Mock LLM Response" in result

    @pytest.mark.asyncio
    async def test_summarize_release_notes(self) -> None:
        """summarize_release_notes should call summarize."""
        client = UnifiedLLMClient()
        client.provider = "none"

        result = await client.summarize_release_notes("Release notes", max_length=100)

        assert "Mock LLM Response" in result

    @pytest.mark.asyncio
    async def test_enrich_feature(self) -> None:
        """enrich_feature should return enriched feature dict."""
        client = UnifiedLLMClient()
        client.provider = "none"

        feature = {"name": "Test Feature", "description": "Test"}
        result = await client.enrich_feature(feature, context="Context")

        assert result["name"] == "Test Feature"
        assert result["enriched"] is True
        assert "details" in result


class TestOpenRouterLLMAdapter:
    """Tests for OpenRouterLLMAdapter."""

    @pytest.fixture
    def mock_adapter(self) -> MockOpenRouterLLMAdapter:
        """Create mock adapter."""
        return MockOpenRouterLLMAdapter()

    @pytest.mark.asyncio
    async def test_classify_batch(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """classify_batch should classify multiple features."""
        features = ["Feature 1", "Feature 2", "Feature 3"]

        results = await mock_adapter.classify_batch(features, categories=["cat1", "cat2"])

        assert len(results) == 3
        assert mock_adapter.call_count == 3
        for result in results:
            assert result["impact"] == "high"
            assert result["type"] == "new_feature"
            assert result["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_classify_batch_handles_errors(
        self, mock_adapter: MockOpenRouterLLMAdapter
    ) -> None:
        """classify_batch should handle errors gracefully."""
        mock_adapter._should_fail = True
        features = ["Feature 1", "Feature 2"]

        results = await mock_adapter.classify_batch(features)

        assert len(results) == 2
        for result in results:
            assert result["impact"] == "medium"
            assert result["type"] == "other"
            assert "padrão" in result["justification"]

    @pytest.mark.asyncio
    async def test_enrich_category(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """enrich_category should return CategoryEnrichment."""

        mock_adapter.responses = [
            json.dumps(
                {
                    "overview": "Category overview",
                    "key_themes": ["Theme 1"],
                    "business_impact": "High impact",
                    "adoption_guidance": "Adopt now",
                    "risk_assessment": "Low risk",
                    "feature_enrichments": [
                        {
                            "feature_name": "Feature 1",
                            "summary": "Summary",
                            "details": "Details",
                            "business_context": "Biz context",
                            "technical_context": "Tech context",
                            "migration_notes": "Migration",
                            "related_features": [],
                            "tags": [],
                            "confidence": 0.9,
                        }
                    ],
                }
            )
        ]

        classifications = {
            "Feature 1": {
                "impact": "high",
                "type": "new_feature",
                "confidence": 0.9,
                "audience": "ambos",
                "priority": "importante",
                "justification": "Test",
            }
        }

        result = await mock_adapter.enrich_category(
            "Test Category", ["Feature 1"], classifications, "pt_BR"
        )

        assert isinstance(result, CategoryEnrichment)
        assert result.category_name == "Test Category"
        assert result.overview == "Category overview"
        assert len(result.feature_enrichments) == 1

    @pytest.mark.asyncio
    async def test_enrich_category_handles_errors(
        self, mock_adapter: MockOpenRouterLLMAdapter
    ) -> None:
        """enrich_category should return minimal enrichment on error."""
        mock_adapter._should_fail = True
        classifications = {}

        result = await mock_adapter.enrich_category(
            "Test Category", ["Feature 1"], classifications, "pt_BR"
        )

        assert isinstance(result, CategoryEnrichment)
        assert result.category_name == "Test Category"
        assert "Categoria Test Category" in result.overview

    @pytest.mark.asyncio
    async def test_enrich_release(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """enrich_release should return ReleaseEnrichment."""
        mock_adapter.responses = [
            json.dumps(
                {
                    "executive_summary": "Executive summary",
                    "strategic_themes": ["Theme 1", "Theme 2"],
                    "migration_checklist": ["Item 1", "Item 2"],
                }
            )
        ]

        cat_enrichment = CategoryEnrichment(
            category_name="Test",
            overview="Overview",
            key_themes=(),
            business_impact="",
            adoption_guidance="",
            risk_assessment="",
            feature_enrichments=(),
            locale="pt_BR",
        )

        result = await mock_adapter.enrich_release("summer_26", [cat_enrichment], "pt_BR")

        assert isinstance(result, ReleaseEnrichment)
        assert result.release_slug == "summer_26"
        assert result.executive_summary == "Executive summary"
        assert list(result.strategic_themes) == ["Theme 1", "Theme 2"]

    @pytest.mark.asyncio
    async def test_enrich_release_handles_errors(
        self, mock_adapter: MockOpenRouterLLMAdapter
    ) -> None:
        """enrich_release should return minimal enrichment on error."""
        mock_adapter._should_fail = True
        cat_enrichment = CategoryEnrichment(
            category_name="Test",
            overview="Overview",
            key_themes=(),
            business_impact="",
            adoption_guidance="",
            risk_assessment="",
            feature_enrichments=(),
            locale="pt_BR",
        )

        result = await mock_adapter.enrich_release("summer_26", [cat_enrichment], "pt_BR")

        assert isinstance(result, ReleaseEnrichment)
        assert result.release_slug == "summer_26"
        assert "Release summer_26 processado" in result.executive_summary

    def test_default_classification(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """_default_classification should return expected defaults."""
        result = mock_adapter._default_classification()

        assert result["impact"] == "medium"
        assert result["type"] == "other"
        assert result["confidence"] == 0.1
        assert "indisponível" in result["justification"]

    def test_parse_category_enrichment(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """_parse_category_enrichment should parse all fields."""
        data = {
            "overview": "Overview",
            "key_themes": ["Theme 1"],
            "business_impact": "Impact",
            "adoption_guidance": "Guidance",
            "risk_assessment": "Risk",
            "feature_enrichments": [
                {
                    "feature_name": "Feature 1",
                    "summary": "Summary",
                    "details": "Details",
                    "business_context": "Biz",
                    "technical_context": "Tech",
                    "migration_notes": "Migration",
                    "related_features": ["Related"],
                    "tags": ["tag1"],
                    "confidence": 0.8,
                }
            ],
        }

        result = mock_adapter._parse_category_enrichment(
            "Test Category", ["Feature 1"], data, "pt_BR"
        )

        assert result.category_name == "Test Category"
        assert result.overview == "Overview"
        assert list(result.key_themes) == ["Theme 1"]
        assert len(result.feature_enrichments) == 1
        feat = result.feature_enrichments[0]
        assert feat.feature_name == "Feature 1"
        assert feat.confidence == 0.8

    def test_parse_release_enrichment(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """_parse_release_enrichment should parse all fields."""
        cat_enrichment = CategoryEnrichment(
            category_name="Test",
            overview="Overview",
            key_themes=(),
            business_impact="",
            adoption_guidance="",
            risk_assessment="",
            feature_enrichments=(),
            locale="pt_BR",
        )

        data = {
            "executive_summary": "Exec summary",
            "strategic_themes": ["Theme 1"],
            "migration_checklist": ["Item 1"],
        }

        result = mock_adapter._parse_release_enrichment(
            "summer_26", [cat_enrichment], data, "pt_BR"
        )

        assert result.release_slug == "summer_26"
        assert result.executive_summary == "Exec summary"
        assert list(result.strategic_themes) == ["Theme 1"]
        assert list(result.migration_checklist) == ["Item 1"]
        assert len(result.category_enrichments) == 1

    def test_minimal_category_enrichment(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """_minimal_category_enrichment should create minimal enrichment."""
        result = mock_adapter._minimal_category_enrichment(
            "Test Category", ["Feature 1", "Feature 2"], "pt_BR"
        )

        assert result.category_name == "Test Category"
        assert "2 features" in result.overview
        assert len(result.feature_enrichments) == 2

    def test_minimal_release_enrichment(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """_minimal_release_enrichment should create minimal enrichment."""
        cat1 = CategoryEnrichment(
            category_name="Cat1",
            overview="Overview",
            key_themes=(),
            business_impact="",
            adoption_guidance="",
            risk_assessment="",
            feature_enrichments=(),
            locale="pt_BR",
        )
        cat2 = CategoryEnrichment(
            category_name="Cat2",
            overview="Overview",
            key_themes=(),
            business_impact="",
            adoption_guidance="",
            risk_assessment="",
            feature_enrichments=(),
            locale="pt_BR",
        )

        result = mock_adapter._minimal_release_enrichment("summer_26", [cat1, cat2], "pt_BR")

        assert result.release_slug == "summer_26"
        assert "summer_26 processado" in result.executive_summary
        assert list(result.strategic_themes) == ["Cat1", "Cat2"]


class TestOpenRouterClassificationAdapter:
    """Tests for OpenRouterClassificationAdapter."""

    @pytest.mark.asyncio
    async def test_classify_delegates_to_llm(self) -> None:
        """classify should delegate to LLM adapter."""
        mock_llm = MockOpenRouterLLMAdapter()
        adapter = OpenRouterClassificationAdapter(llm_adapter=mock_llm)

        features = ["Feature 1", "Feature 2"]
        results = await adapter.classify(features, categories=["cat1"])

        assert len(results) == 2
        assert mock_llm.call_count == 2

    def test_name_property(self) -> None:
        """name property should return correct value."""
        adapter = OpenRouterClassificationAdapter()
        assert adapter.name == "openrouter_classification"


class TestHeuristicClassificationAdapter:
    """Tests for HeuristicClassificationAdapter."""

    @pytest.fixture
    def adapter(self) -> HeuristicClassificationAdapter:
        """Create heuristic adapter."""
        return HeuristicClassificationAdapter()

    def test_name_property(self, adapter: HeuristicClassificationAdapter) -> None:
        """name property should return correct value."""
        assert adapter.name == "heuristic_classification"

    @pytest.mark.asyncio
    async def test_classify_security_keywords(
        self, adapter: HeuristicClassificationAdapter
    ) -> None:
        """Should classify security-related features as high impact security."""
        features = [
            "Security vulnerability CVE-2024-1234 fixed",
            "MFA authentication improved",
            "XSS protection added",
        ]

        results = await adapter.classify(features)

        assert len(results) == 3
        for result in results:
            assert result["impact"] == "high"
            assert result["type"] == "security"
            assert result["confidence"] >= 0.7

    @pytest.mark.asyncio
    async def test_classify_performance_keywords(
        self, adapter: HeuristicClassificationAdapter
    ) -> None:
        """Should classify performance features."""
        features = [
            "Performance optimization for queries",
            "Latency reduced by 50%",
            "Cache throughput improved",
        ]

        results = await adapter.classify(features)

        for result in results:
            assert result["impact"] == "high"
            assert result["type"] == "performance"

    @pytest.mark.asyncio
    async def test_classify_deprecation_keywords(
        self, adapter: HeuristicClassificationAdapter
    ) -> None:
        """Should classify deprecation features."""
        features = [
            "Deprecated API removed",
            "End of life for old feature",
            "Sunset legacy component",
        ]

        results = await adapter.classify(features)

        for result in results:
            assert result["impact"] == "high"
            assert result["type"] == "deprecation"

    @pytest.mark.asyncio
    async def test_classify_breaking_change_keywords(
        self, adapter: HeuristicClassificationAdapter
    ) -> None:
        """Should classify breaking changes."""
        features = [
            "Breaking change in API",
            "Incompatible upgrade required",
            "Migration to new version",
        ]

        results = await adapter.classify(features)

        for result in results:
            assert result["impact"] == "high"
            assert result["type"] == "breaking_change"

    @pytest.mark.asyncio
    async def test_classify_bug_fix_keywords(self, adapter: HeuristicClassificationAdapter) -> None:
        """Should classify bug fixes."""
        features = [
            "Bug fix for login issue",
            "Patch for memory leak",
            "Hotfix for critical issue",
        ]

        results = await adapter.classify(features)

        for result in results:
            assert result["impact"] == "medium"
            assert result["type"] == "bug_fix"

    @pytest.mark.asyncio
    async def test_classify_new_feature_keywords(
        self, adapter: HeuristicClassificationAdapter
    ) -> None:
        """Should classify new features."""
        features = [
            "New feature added",
            "Introduce new dashboard",
            "Launch new service",
        ]

        results = await adapter.classify(features)

        for result in results:
            assert result["impact"] == "medium"
            assert result["type"] == "new_feature"

    @pytest.mark.asyncio
    async def test_classify_improvement_keywords(
        self, adapter: HeuristicClassificationAdapter
    ) -> None:
        """Should classify improvements."""
        features = [
            "Improve user experience",
            "Enhance documentation quality",
            "Update documentation",
        ]

        results = await adapter.classify(features)

        for result in results:
            assert result["impact"] == "medium"
            assert result["type"] == "improvement"

    @pytest.mark.asyncio
    async def test_classify_integration_keywords(
        self, adapter: HeuristicClassificationAdapter
    ) -> None:
        """Should classify integrations."""
        features = [
            "API integration with Mulesoft",
            "Webhook endpoint added",
            "REST endpoint updated",
        ]

        results = await adapter.classify(features)

        for result in results:
            assert result["impact"] == "medium"
            assert result["type"] == "integration"

    @pytest.mark.asyncio
    async def test_classify_ui_ux_keywords(self, adapter: HeuristicClassificationAdapter) -> None:
        """Should classify UI/UX features."""
        features = [
            "UI redesign for Lightning",
            "UX improvement for accessibility",
            "Design system updated",
        ]

        results = await adapter.classify(features)

        for result in results:
            assert result["impact"] == "low"
            assert result["type"] == "ui_ux"

    @pytest.mark.asyncio
    async def test_classify_ai_keywords(self, adapter: HeuristicClassificationAdapter) -> None:
        """Should classify AI features."""
        features = [
            "Agentforce new capability",
            "Einstein AI model updated",
            "LLM integration added",
        ]

        results = await adapter.classify(features)

        for result in results:
            assert result["impact"] == "high"
            assert result["type"] == "new_feature"

    @pytest.mark.asyncio
    async def test_classify_default_for_unknown(
        self, adapter: HeuristicClassificationAdapter
    ) -> None:
        """Should return default classification for unknown features."""
        features = ["Random text with no keywords"]

        results = await adapter.classify(features)

        assert len(results) == 1
        assert results[0]["impact"] == "medium"
        assert results[0]["type"] == "other"
        assert results[0]["confidence"] == 0.3
        assert "sem match" in results[0]["justification"]

    @pytest.mark.asyncio
    async def test_classify_sets_audience_and_priority(
        self, adapter: HeuristicClassificationAdapter
    ) -> None:
        """Should set audience and priority based on impact."""
        features = ["Security vulnerability fixed"]

        results = await adapter.classify(features)

        assert results[0]["audience"] == "ambos"
        assert results[0]["priority"] == "importante"  # high impact -> importante


class TestOpenRouterEnrichmentAdapter:
    """Tests for OpenRouterEnrichmentAdapter."""

    @pytest.mark.asyncio
    async def test_enrich_category_delegates_to_llm(self) -> None:
        """enrich_category should delegate to LLM adapter."""
        mock_llm = MockOpenRouterLLMAdapter()
        adapter = OpenRouterEnrichmentAdapter(llm_adapter=mock_llm)

        result = await adapter.enrich_category("Test", ["Feature 1"], {}, "pt_BR")

        assert isinstance(result, CategoryEnrichment)
        assert mock_llm.call_count == 1

    @pytest.mark.asyncio
    async def test_enrich_release_delegates_to_llm(self) -> None:
        """enrich_release should delegate to LLM adapter."""
        mock_llm = MockOpenRouterLLMAdapter()
        adapter = OpenRouterEnrichmentAdapter(llm_adapter=mock_llm)

        cat = CategoryEnrichment(
            category_name="Test",
            overview="Overview",
            key_themes=(),
            business_impact="",
            adoption_guidance="",
            risk_assessment="",
            feature_enrichments=(),
            locale="pt_BR",
        )

        result = await adapter.enrich_release("summer_26", [cat], "pt_BR")

        assert isinstance(result, ReleaseEnrichment)
        assert mock_llm.call_count == 1

    def test_name_property(self) -> None:
        """name property should return correct value."""
        adapter = OpenRouterEnrichmentAdapter()
        assert adapter.name == "openrouter_enrichment"


class TestProviderConfig:
    """Tests for provider configuration."""

    def test_provider_chain_order(self) -> None:
        """Provider chain should be in correct priority order."""
        names = [cfg.name for cfg in _PROVIDER_CHAIN]
        assert names == ["openrouter", "opencode", "gemini"]

    def test_openrouter_config(self) -> None:
        """OpenRouter config should have correct settings."""
        cfg = next(c for c in _PROVIDER_CHAIN if c.name == "openrouter")
        assert cfg.api_key_env == "OPENROUTER_API_KEY"
        assert cfg.base_url == "https://openrouter.ai/api/v1"
        assert cfg.default_model == "openrouter/free"
        assert len(cfg.fallback_models) > 0

    def test_opencode_config(self) -> None:
        """OpenCode config should have correct settings."""
        cfg = next(c for c in _PROVIDER_CHAIN if c.name == "opencode")
        assert cfg.api_key_env == "OPENCODE_API_KEY"
        assert cfg.base_url == "https://opencode.ai/zen/v1"

    def test_gemini_config(self) -> None:
        """Gemini config should have correct settings."""
        cfg = next(c for c in _PROVIDER_CHAIN if c.name == "gemini")
        assert cfg.api_key_env == "GOOGLE_API_KEY"
        assert cfg.default_model == "gemini-3.6-flash"

    def test_env_model_override(self) -> None:
        """_env_model_override should respect env vars."""
        cfg = _ProviderConfig(name="test", api_key_env="TEST_KEY", default_model="default-model")

        with patch.dict("os.environ", {"TEST_MODEL": "custom-model"}):
            result = _env_model_override(cfg)
            assert result == "custom-model"

        with patch.dict("os.environ", {}, clear=True):
            result = _env_model_override(cfg)
            assert result == "default-model"

    def test_env_model_override_empty_string_fallbacks(self) -> None:
        """Empty env var should fallback to default."""
        cfg = _ProviderConfig(name="test", api_key_env="TEST_KEY", default_model="default-model")

        with patch.dict("os.environ", {"TEST_MODEL": ""}):
            result = _env_model_override(cfg)
            assert result == "default-model"
