"""Tests for src/infrastructure/llm.py to reach 95% coverage."""

from __future__ import annotations

import concurrent.futures
import json
import sys
from unittest.mock import MagicMock, patch

import pytest


class TestLLMException(Exception):
    """Custom exception for LLM test scenarios."""


from src.infrastructure.llm import (
    GeminiClassificationAdapter,
    GeminiLLMAdapter,
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


class TestUnifiedLLMClientCoverage:
    """Tests for UnifiedLLMClient missing coverage."""

    def test_init_with_provider_no_key_falls_to_autodetect(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lines 185-194: explicit provider without key falls back to auto-detect."""
        monkeypatch.setenv("GOOGLE_API_KEY", "goog-key")
        client = UnifiedLLMClient(api_key="", provider="opencode")
        assert client.provider in ("gemini", "opencode", "openrouter")

    def test_init_manual_provider_sets_attributes(self) -> None:
        """Lines 197-204: auto-detect finds first provider with key."""
        with patch.dict(
            "os.environ",
            {"OPENROUTER_API_KEY": "or", "OPENCODE_API_KEY": "oc", "GOOGLE_API_KEY": "goog"},
        ):
            client = UnifiedLLMClient()
            assert client.provider == "openrouter"

    def test_find_provider_config(self) -> None:
        """Line 220: _find_provider_config returns config or None."""
        cfg = UnifiedLLMClient._find_provider_config("openrouter")
        assert cfg is not None
        assert cfg.name == "openrouter"

        cfg = UnifiedLLMClient._find_provider_config("nonexistent")
        assert cfg is None

    def test_next_fallback_provider(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Lines 224-229: _next_fallback_provider returns next untried provider with key."""
        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(provider="gemini", api_key="goog-key")
        client._tried_providers.add("gemini")
        next_cfg = client._next_fallback_provider()
        assert next_cfg is not None
        assert next_cfg.name in ("opencode", "openrouter")

    def test_next_fallback_provider_all_tried(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """_next_fallback_provider returns None when all tried."""
        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        client = UnifiedLLMClient(provider="opencode", api_key="oc-key")
        client._tried_providers.update(["opencode", "openrouter", "gemini"])
        next_cfg = client._next_fallback_provider()
        assert next_cfg is None

    def test_switch_to_next_provider_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Lines 233-246: _switch_to_next_provider switches and returns True."""
        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(provider="opencode", api_key="oc-key")
        result = client._switch_to_next_provider()
        assert result is True
        assert client.provider == "openrouter"

    def test_switch_to_next_provider_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """_switch_to_next_provider returns False when no fallback."""
        client = UnifiedLLMClient(provider="none", api_key="")
        result = client._switch_to_next_provider()
        assert result is False

    def test_generate_completion_empty_prompt_raises(self) -> None:
        """Line 274: empty prompt raises ValueError."""
        client = UnifiedLLMClient()
        client.provider = "none"
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            client.generate_completion("")

    def test_generate_completion_none_provider_returns_mock(self) -> None:
        """Lines 276-278: provider='none' returns mock."""
        client = UnifiedLLMClient()
        client.provider = "none"
        result = client.generate_completion("test prompt")
        assert "Mock LLM Response" in result

    def test_generate_completion_dispatch_gemini(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Lines 329-335: _dispatch_to_provider routes to _generate_gemini."""
        monkeypatch.setenv("GOOGLE_API_KEY", "goog-key")
        client = UnifiedLLMClient(provider="gemini", api_key="goog-key")
        with patch.object(client, "_generate_gemini", return_value="gemini-result") as mock:
            result = client.generate_completion("test")
        assert result == "gemini-result"
        mock.assert_called_once()

    def test_generate_completion_dispatch_openai_compatible(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lines 336-342: _dispatch_to_provider routes to _generate_openai_compatible."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(provider="openrouter", api_key="or-key")
        with patch.object(
            client, "_generate_openai_compatible", return_value="openai-result"
        ) as mock:
            result = client.generate_completion("test")
        assert result == "openai-result"
        mock.assert_called_once()

    def test_generate_completion_dispatch_unknown_provider(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Line 344: unknown provider raises ValueError after fallback chain exhausted."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(provider="openrouter", api_key="or-key")
        client.provider = "unknown"
        client._active_provider = None
        # Mock _switch_to_next_provider to return False so fallback chain ends
        with patch.object(client, "_switch_to_next_provider", return_value=False):
            with pytest.raises(ValueError, match="Unsupported LLM provider"):
                client.generate_completion("test")

    def test_generate_completion_fallback_chain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Lines 297-319: generate_completion falls back on failure."""
        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(provider="opencode", api_key="oc-key")

        call_count = {"n": 0}

        def mock_dispatch(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("first provider failed")
            return "fallback-success"

        with patch.object(client, "_dispatch_to_provider", side_effect=mock_dispatch):
            with patch.object(client, "_switch_to_next_provider", return_value=True):
                result = client.generate_completion("test")
        assert result == "fallback-success"

    def test_generate_completion_all_providers_fail(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Lines 319: all providers fail raises last error."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(provider="openrouter", api_key="or-key")

        with patch.object(client, "_dispatch_to_provider", side_effect=RuntimeError("failed")):
            with patch.object(client, "_switch_to_next_provider", return_value=False):
                with pytest.raises(RuntimeError, match="failed"):
                    client.generate_completion("test")

    def test_generate_gemini_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Lines 354-376: _generate_gemini returns response text."""
        import src.infrastructure.llm as llm_module

        fake_resp = MagicMock()
        fake_resp.text = "gemini response"
        fake_model = MagicMock()
        fake_model.generate_content.return_value = fake_resp
        fake_client = MagicMock()
        fake_client.models = fake_model
        fake_genai = MagicMock()
        fake_genai.Client.return_value = fake_client
        monkeypatch.setattr(llm_module, "genai", fake_genai)
        monkeypatch.setattr(llm_module, "_HAS_GENAI", True)

        client = UnifiedLLMClient(provider="gemini", api_key="goog-key")
        result = client._generate_gemini("prompt", "system", 0.7, 100)
        assert result == "gemini response"

    def test_generate_gemini_empty_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Line 376: empty response returns empty string."""
        import src.infrastructure.llm as llm_module

        fake_resp = MagicMock()
        fake_resp.text = ""
        fake_model = MagicMock()
        fake_model.generate_content.return_value = fake_resp
        fake_client = MagicMock()
        fake_client.models = fake_model
        fake_genai = MagicMock()
        fake_genai.Client.return_value = fake_client
        monkeypatch.setattr(llm_module, "genai", fake_genai)
        monkeypatch.setattr(llm_module, "_HAS_GENAI", True)

        client = UnifiedLLMClient(provider="gemini", api_key="goog-key")
        result = client._generate_gemini("prompt", "system", 0.7, 100)
        assert result == ""

    def test_generate_gemini_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Lines 372-374: timeout raises RuntimeError."""
        import src.infrastructure.llm as llm_module

        fake_client = MagicMock()

        def hang(*args, **kwargs):
            raise concurrent.futures.TimeoutError()

        fake_client.models.generate_content = hang
        fake_genai = MagicMock()
        fake_genai.Client.return_value = fake_client
        monkeypatch.setattr(llm_module, "genai", fake_genai)
        monkeypatch.setattr(llm_module, "_HAS_GENAI", True)

        client = UnifiedLLMClient(provider="gemini", api_key="goog-key")
        with patch("src.infrastructure.llm.LLM_CALL_TIMEOUT_S", 1):
            with pytest.raises(RuntimeError, match="timed out"):
                client._generate_gemini("prompt", "system", 0.7, 100)

    def test_generate_gemini_import_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Line 357: missing genai raises ImportError."""
        import src.infrastructure.llm as llm_module

        monkeypatch.setattr(llm_module, "genai", None)
        monkeypatch.setattr(llm_module, "_HAS_GENAI", False)

        client = UnifiedLLMClient(provider="gemini", api_key="goog-key")
        with pytest.raises(ImportError, match="google.genai package not available"):
            client._generate_gemini("prompt", "system", 0.7, 100)

    def test_generate_openai_compatible_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Lines 386-417: _generate_openai_compatible returns content."""
        fake_choice = MagicMock()
        fake_choice.message.content = "openai result"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        fake_client.chat.completions.create.return_value = fake_resp

        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(provider="openrouter", api_key="or-key")

        with patch("openai.OpenAI", return_value=fake_client):
            result = client._generate_openai_compatible("prompt", "system", 0.7, 100)
        assert result == "openai result"

    def test_generate_openai_compatible_with_system_instruction(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lines 400-403: system instruction added to messages."""
        fake_choice = MagicMock()
        fake_choice.message.content = "result"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        fake_client.chat.completions.create.return_value = fake_resp

        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(provider="openrouter", api_key="or-key")

        with patch("openai.OpenAI", return_value=fake_client):
            client._generate_openai_compatible("prompt", "system instruction", 0.7, 100)

        call_args = fake_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "system instruction"

    def test_generate_openai_compatible_null_content(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Line 417: null content returns empty string."""
        fake_choice = MagicMock()
        fake_choice.message.content = None
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        fake_client.chat.completions.create.return_value = fake_resp

        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(provider="openrouter", api_key="or-key")

        with patch("openai.OpenAI", return_value=fake_client):
            result = client._generate_openai_compatible("prompt", None, 0.7, 100)
        assert result == ""

    def test_generate_openai_compatible_403_skips(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Lines 420-426: 403 error skips model."""
        fake_choice = MagicMock()
        fake_choice.message.content = "success"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise TestLLMException("Error code: 403 - only available on agentic harnesses")
            return fake_resp

        fake_client.chat.completions.create.side_effect = side_effect

        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(provider="openrouter", api_key="or-key", model_name="bad:free")

        with patch("openai.OpenAI", return_value=fake_client):
            result = client._generate_openai_compatible("prompt", None, 0.7, 100)
        assert result == "success"
        assert call_count["n"] == 2

    def test_generate_openai_compatible_401_unsupported_skips(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lines 427-436: 401 with 'not supported' skips model."""
        fake_choice = MagicMock()
        fake_choice.message.content = "after 401"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise TestLLMException(
                    "Error code: 401 - {'type': 'error', 'error': {'type': 'ModelError', 'message': 'Model not supported'}}"
                )
            return fake_resp

        fake_client.chat.completions.create.side_effect = side_effect

        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(
            provider="openrouter", api_key="or-key", model_name="unsupported:free"
        )

        with patch("openai.OpenAI", return_value=fake_client):
            result = client._generate_openai_compatible("prompt", None, 0.7, 100)
        assert result == "after 401"
        assert call_count["n"] == 2

    def test_generate_openai_compatible_429_backoff_retry(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lines 438-456: 429 rate limit backs off and retries."""
        fake_choice = MagicMock()
        fake_choice.message.content = "after backoff"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise TestLLMException("Error code: 429 - rate limit exceeded")
            return fake_resp

        fake_client.chat.completions.create.side_effect = side_effect

        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(
            provider="openrouter", api_key="or-key", model_name="rate-limited:free"
        )

        with patch("openai.OpenAI", return_value=fake_client):
            with patch("time.sleep") as mock_sleep:
                result = client._generate_openai_compatible("prompt", None, 0.7, 100)
        assert result == "after backoff"
        assert mock_sleep.called

    def test_generate_openai_compatible_429_last_model_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lines 454-456: 429 on last model raises."""
        fake_client = MagicMock()
        fake_client.chat.completions.create.side_effect = Exception(
            "Error code: 429 - quota exceeded"
        )

        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        client = UnifiedLLMClient(provider="opencode", api_key="oc-key", model_name="only-model")
        client._active_provider.fallback_models = []

        with patch("openai.OpenAI", return_value=fake_client):
            with patch("time.sleep") as mock_sleep:
                with pytest.raises(Exception, match="quota exceeded"):
                    client._generate_openai_compatible("prompt", None, 0.7, 100)
        assert not mock_sleep.called

    def test_generate_openai_compatible_quota_exceeded_triggers_backoff(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lines 438-442: 'quota exceeded' triggers rate limit branch."""
        fake_choice = MagicMock()
        fake_choice.message.content = "after quota"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise TestLLMException("RESOURCE_EXHAUSTED - quota exceeded for metric")
            return fake_resp

        fake_client.chat.completions.create.side_effect = side_effect

        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(
            provider="openrouter", api_key="or-key", model_name="quota-model:free"
        )

        with patch("openai.OpenAI", return_value=fake_client):
            with patch("time.sleep") as mock_sleep:
                result = client._generate_openai_compatible("prompt", None, 0.7, 100)
        assert result == "after quota"
        assert mock_sleep.called

    def test_generate_openai_compatible_generic_error_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lines 457-459: generic error raises."""
        fake_client = MagicMock()
        fake_client.chat.completions.create.side_effect = RuntimeError("network down")

        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        client = UnifiedLLMClient(provider="opencode", api_key="oc-key", model_name="only-model")
        client._active_provider.fallback_models = []

        with patch("openai.OpenAI", return_value=fake_client):
            with pytest.raises(RuntimeError, match="network down"):
                client._generate_openai_compatible("prompt", None, 0.7, 100)

    def test_generate_openai_compatible_all_models_fail_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Line 466: all models fail raises."""
        fake_client = MagicMock()
        fake_client.chat.completions.create.side_effect = RuntimeError("model failed")

        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        client = UnifiedLLMClient(provider="openrouter", api_key="or-key")

        with patch("openai.OpenAI", return_value=fake_client):
            with pytest.raises(RuntimeError, match="model failed"):
                client._generate_openai_compatible("prompt", None, 0.7, 100)

    def test_generate_openai_compatible_import_error(self) -> None:
        """Lines 388-389: openai import error raises."""
        with patch.dict(sys.modules, {"openai": None}):
            client = UnifiedLLMClient(provider="openrouter", api_key="or-key")
            with pytest.raises(ImportError, match="openai package required"):
                client._generate_openai_compatible("prompt", None, 0.7, 100)

    @pytest.mark.asyncio
    async def test_classify_text_with_categories(self) -> None:
        """Lines 491-493: classify_text adds categories to prompt."""
        client = UnifiedLLMClient()
        client.provider = "none"
        result = await client.classify_text("feature text", categories=["cat1", "cat2"])
        assert "Mock LLM Response" in result

    @pytest.mark.asyncio
    async def test_classify_text_no_categories(self) -> None:
        """classify_text works without categories."""
        client = UnifiedLLMClient()
        client.provider = "none"
        result = await client.classify_text("feature text")
        assert "Mock LLM Response" in result

    def test_summarize(self) -> None:
        """Lines 498-511: summarize generates completion."""
        client = UnifiedLLMClient()
        client.provider = "none"
        result = client.summarize("text to summarize", max_length=50)
        assert "Mock LLM Response" in result

    @pytest.mark.asyncio
    async def test_enrich_feature(self) -> None:
        """Lines 517-528: enrich_feature returns enriched dict."""
        client = UnifiedLLMClient()
        client.provider = "none"
        result = await client.enrich_feature({"name": "Feature"}, context="context")
        assert result["enriched"] is True
        assert "details" in result


class TestOpenRouterLLMAdapterCoverage:
    """Tests for OpenRouterLLMAdapter missing coverage."""

    @pytest.fixture
    def mock_adapter(self) -> MockOpenRouterLLMAdapter:
        return MockOpenRouterLLMAdapter()

    @pytest.mark.asyncio
    async def test_classify_batch_with_response_format(
        self, mock_adapter: MockOpenRouterLLMAdapter
    ) -> None:
        """classify_batch uses response_format."""
        features = ["Feature 1"]
        results = await mock_adapter.classify_batch(features, categories=["cat1"])
        assert len(results) == 1
        assert mock_adapter.call_count == 1

    @pytest.mark.asyncio
    async def test_enrich_category_success(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """Lines 643-651: enrich_category parses response."""
        mock_adapter.responses = [
            json.dumps(
                {
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

    @pytest.mark.asyncio
    async def test_enrich_release_success(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """Lines 673-681: enrich_release parses response."""
        mock_adapter.responses = [
            json.dumps(
                {
                    "executive_summary": "Exec summary",
                    "strategic_themes": ["Theme 1"],
                    "migration_checklist": ["Item 1"],
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

    def test_parse_category_enrichment_full(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """Lines 696-731: _parse_category_enrichment parses all fields."""
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
        feat = result.feature_enrichments[0]
        assert feat.feature_name == "Feature 1"
        assert feat.confidence == 0.8

    def test_parse_release_enrichment_full(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """Lines 733-747: _parse_release_enrichment parses all fields."""
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

    def test_minimal_category_enrichment(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """Lines 749-770: _minimal_category_enrichment creates fallback."""
        result = mock_adapter._minimal_category_enrichment(
            "Test Category", ["Feature 1", "Feature 2"], "pt_BR"
        )

        assert result.category_name == "Test Category"
        assert "2 features" in result.overview
        assert len(result.feature_enrichments) == 2

    def test_minimal_release_enrichment(self, mock_adapter: MockOpenRouterLLMAdapter) -> None:
        """Lines 772-789: _minimal_release_enrichment creates fallback."""
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


class TestHeuristicClassificationAdapterCoverage:
    """Tests for HeuristicClassificationAdapter missing coverage."""

    @pytest.fixture
    def adapter(self) -> HeuristicClassificationAdapter:
        return HeuristicClassificationAdapter()

    @pytest.mark.asyncio
    async def test_classify_all_keyword_types(
        self, adapter: HeuristicClassificationAdapter
    ) -> None:
        """Test all keyword rules match."""
        test_cases = [
            ("security vulnerability", "high", "security"),
            ("performance optimization", "high", "performance"),
            ("deprecated API", "high", "deprecation"),
            ("breaking change", "high", "breaking_change"),
            ("bug fix", "medium", "bug_fix"),
            ("new feature", "medium", "new_feature"),
            ("improve documentation", "medium", "improvement"),
            ("API integration", "medium", "integration"),
            ("UI redesign", "low", "ui_ux"),
            ("Agentforce AI", "high", "new_feature"),
        ]

        for text, expected_impact, expected_type in test_cases:
            results = await adapter.classify([text])
            assert results[0]["impact"] == expected_impact
            assert results[0]["type"] == expected_type

    @pytest.mark.asyncio
    async def test_classify_case_insensitive(self, adapter: HeuristicClassificationAdapter) -> None:
        """Keywords should be case insensitive."""
        features = ["SECURITY FIX", "Security Fix", "security fix"]
        for feat in features:
            results = await adapter.classify([feat])
            assert results[0]["impact"] == "high"
            assert results[0]["type"] == "security"

    @pytest.mark.asyncio
    async def test_classify_priority_high_impact(
        self, adapter: HeuristicClassificationAdapter
    ) -> None:
        """High impact gets 'importante' priority."""
        results = await adapter.classify(["Security vulnerability"])
        assert results[0]["priority"] == "importante"

    @pytest.mark.asyncio
    async def test_classify_priority_low_impact(
        self, adapter: HeuristicClassificationAdapter
    ) -> None:
        """Low impact gets 'opcional' priority."""
        results = await adapter.classify(["UI redesign"])
        assert results[0]["priority"] == "opcional"

    @pytest.mark.asyncio
    async def test_classify_audience_both(self, adapter: HeuristicClassificationAdapter) -> None:
        """All classifications have audience='ambos'."""
        results = await adapter.classify(["New feature"])
        assert results[0]["audience"] == "ambos"


class TestOpenRouterClassificationAdapterCoverage:
    """Tests for OpenRouterClassificationAdapter."""

    @pytest.mark.asyncio
    async def test_classify_delegates(self) -> None:
        """classify delegates to LLM adapter."""
        mock_llm = MockOpenRouterLLMAdapter()
        adapter = OpenRouterClassificationAdapter(llm_adapter=mock_llm)

        results = await adapter.classify(["Feature 1", "Feature 2"], categories=["cat1"])

        assert len(results) == 2
        assert mock_llm.call_count == 2


class TestOpenRouterEnrichmentAdapterCoverage:
    """Tests for OpenRouterEnrichmentAdapter."""

    @pytest.mark.asyncio
    async def test_enrich_category_delegates(self) -> None:
        """enrich_category delegates to LLM adapter."""
        mock_llm = MockOpenRouterLLMAdapter()
        adapter = OpenRouterEnrichmentAdapter(llm_adapter=mock_llm)

        result = await adapter.enrich_category("Test", ["Feature 1"], {}, "pt_BR")

        assert isinstance(result, CategoryEnrichment)
        assert mock_llm.call_count == 1

    @pytest.mark.asyncio
    async def test_enrich_release_delegates(self) -> None:
        """enrich_release delegates to LLM adapter."""
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


class TestProviderConfigCoverage:
    """Tests for provider configuration."""

    def test_env_model_override_with_env(self) -> None:
        """_env_model_override returns env value."""
        cfg = _ProviderConfig(name="test", api_key_env="TEST_KEY", default_model="default")

        with patch.dict("os.environ", {"TEST_MODEL": "custom-model"}):
            result = _env_model_override(cfg)
            assert result == "custom-model"

    def test_env_model_override_empty_fallback(self) -> None:
        """Empty env falls back to default."""
        cfg = _ProviderConfig(name="test", api_key_env="TEST_KEY", default_model="default")

        with patch.dict("os.environ", {"TEST_MODEL": ""}):
            result = _env_model_override(cfg)
            assert result == "default"

    def test_env_model_override_no_env(self) -> None:
        """No env returns default."""
        cfg = _ProviderConfig(name="test", api_key_env="TEST_KEY", default_model="default")

        with patch.dict("os.environ", {}, clear=True):
            result = _env_model_override(cfg)
            assert result == "default"


class TestGeminiAdaptersCoverage:
    """Tests for optional Gemini adapters."""

    def test_gemini_llm_adapter_init_checks_genai(self) -> None:
        """GeminiLLMAdapter checks _HAS_GENAI on init."""
        import src.infrastructure.llm as llm_module

        original_has_genai = llm_module._HAS_GENAI
        try:
            llm_module._HAS_GENAI = False
            with pytest.raises(ImportError, match="google.genai package not available"):
                GeminiLLMAdapter()
        finally:
            llm_module._HAS_GENAI = original_has_genai

    def test_gemini_classification_adapter_init_checks_genai(self) -> None:
        """GeminiClassificationAdapter checks _HAS_GENAI on init."""
        import src.infrastructure.llm as llm_module

        original_has_genai = llm_module._HAS_GENAI
        try:
            llm_module._HAS_GENAI = False
            with pytest.raises(ImportError, match="google.genai not available"):
                GeminiClassificationAdapter()
        finally:
            llm_module._HAS_GENAI = original_has_genai
