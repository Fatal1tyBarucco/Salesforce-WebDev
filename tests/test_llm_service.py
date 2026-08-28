"""Tests for src/llm_service.py — 100% coverage target."""

import asyncio
import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest

from src.llm_service import LLMService

# ── Provider initialization ───────────────────────────────────────


class TestLLMProviderInit:
    """LLMService.__init__: auto-detect, explicit provider, no-key fallback."""

    def test_explicit_provider_openrouter(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        svc = LLMService(api_key="k", provider="openrouter")
        assert svc.provider == "openrouter"
        assert svc.api_key == "k"
        assert svc.model_name == "google/gemma-4-31b-it:free"

    def test_explicit_provider_opencode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        svc = LLMService(api_key="k", provider="opencode")
        assert svc.provider == "opencode"
        assert svc.model_name == "hy3-free"

    def test_explicit_provider_gemini(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GOOGLE_API_KEY", "goog-key")
        svc = LLMService(api_key="k", provider="gemini")
        assert svc.provider == "gemini"
        assert svc.model_name == "gemini-3.6-flash"

    def test_explicit_unknown_provider_falls_to_autodetect(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("GOOGLE_API_KEY", "goog-key")
        svc = LLMService(api_key="k", provider="banana")
        assert svc.provider in ("groq", "opencode", "openrouter", "gemini")

    def test_no_key_available_returns_mock(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("OPENCODE_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        svc = LLMService()
        assert svc.provider == "none"

    def test_unsupported_provider_with_key_uses_first(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("GROQ_API_KEY", "groq-key")
        monkeypatch.setenv("GOOGLE_API_KEY", "goog-key")
        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        svc = LLMService(api_key="k", provider="banana")
        assert svc.provider in ("groq", "gemini", "opencode", "openrouter")

    def test_explicit_provider_groq(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GROQ_API_KEY", "groq-key")
        svc = LLMService(api_key="k", provider="groq")
        assert svc.provider == "groq"
        assert svc.model_name == "llama-3.3-70b-versatile"


# ── Prompt validation ──────────────────────────────────────────────


class TestLLMPromptValidation:
    """generate_completion rejects empty/whitespace prompts."""

    def test_empty_prompt_raises_value_error(self) -> None:
        svc = LLMService(api_key="k")
        with pytest.raises(ValueError):
            svc.generate_completion("")

    def test_whitespace_only_prompt_raises(self) -> None:
        svc = LLMService(api_key="k")
        with pytest.raises(ValueError):
            svc.generate_completion("   ")


# ── Mock mode ─────────────────────────────────────────────────────


class TestLLMMockMode:
    """Provider='none' returns mock responses without hitting any API."""

    def test_mock_response_prefix(self) -> None:
        svc = LLMService(api_key=None, provider="none")
        out = svc.generate_completion("hello world")
        assert out.startswith("[Mock LLM Response]")

    def test_mock_with_gemini_no_key(self) -> None:
        svc = LLMService(api_key=None, provider="gemini")
        out = svc.generate_completion("hello")
        assert out.startswith("[Mock LLM Response]")


# ── Provider fallback chain ────────────────────────────────────────


class TestLLMFallbackChain:
    """_switch_to_next_provider / _next_fallback_provider: blacklist and rotate."""

    def test_switch_to_next_provider_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Lines 169-178: switch logs, updates provider/model/key."""
        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        monkeypatch.setenv("GOOGLE_API_KEY", "goog-key")
        svc = LLMService(api_key="oc-key", provider="opencode")
        result = svc._switch_to_next_provider()
        assert result is True
        assert svc.provider == "openrouter"
        assert svc.api_key == "or-key"
        assert svc.model_name == "google/gemma-4-31b-it:free"

    def test_switch_to_next_provider_all_exhausted_returns_false(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("GROQ_API_KEY", "groq-key")
        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        monkeypatch.setenv("GOOGLE_API_KEY", "goog-key")
        svc = LLMService(api_key="oc-key", provider="opencode")
        svc._tried_providers.update(["groq", "opencode", "openrouter", "gemini"])
        result = svc._switch_to_next_provider()
        assert result is False

    def test_next_fallback_provider_skips_tried(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GROQ_API_KEY", "groq-key")
        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        monkeypatch.setenv("GOOGLE_API_KEY", "goog-key")
        svc = LLMService(api_key="oc-key", provider="opencode")
        svc._tried_providers.update(["groq", "opencode"])
        result = svc._next_fallback_provider()
        assert result is not None
        assert result.name == "openrouter"

    def test_generate_completion_fallback_chain_succeeds(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Line 224: success clears _tried_providers (blacklist reset)."""
        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        monkeypatch.setenv("GOOGLE_API_KEY", "goog-key")
        svc = LLMService(api_key="oc-key", provider="opencode")

        fake_choice = MagicMock()
        fake_choice.message.content = "fallback-success"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):  # type: ignore[no-untyped-def]
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("opencode down")
            return fake_resp

        fake_client.chat.completions.create.side_effect = side_effect
        with patch("openai.OpenAI", return_value=fake_client):
            out = svc.generate_completion("hi")
        assert out == "fallback-success"
        assert svc._tried_providers == set()

    def test_generate_completion_all_providers_fail(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        monkeypatch.setenv("GOOGLE_API_KEY", "goog-key")
        svc = LLMService(api_key="oc-key", provider="opencode")
        with patch.object(svc, "_dispatch_to_provider", side_effect=RuntimeError("fail")):
            with pytest.raises(RuntimeError, match="fail"):
                svc.generate_completion("hi")

    def test_provider_loops_through_models_before_switching(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """All models of a provider failing must RAISE so the chain advances.

        Regression: previously a silent return caused the pipeline to think
        the provider succeeded with empty content.
        """
        monkeypatch.setenv("GROQ_API_KEY", "groq-key")
        monkeypatch.setenv("OPENCODE_API_KEY", "oc-key")
        svc = LLMService(api_key="groq-key", provider="groq")

        attempts: list[str] = []

        def fake_dispatch(*args, **kwargs):  # type: ignore[no-untyped-def]
            attempts.append(svc.provider)
            raise RuntimeError(f"{svc.provider} down")

        with patch.object(svc, "_dispatch_to_provider", side_effect=fake_dispatch):
            with pytest.raises(RuntimeError):
                svc.generate_completion("hi")

        assert attempts[0] == "groq"
        assert "opencode" in attempts


# ── OpenAI-compatible provider (OpenCode / OpenRouter) ─────────────


class TestLLMOpenAICompatible:
    """_generate_openai_compatible: models loop, 403 skip, 429 backoff."""

    def test_successful_response(self) -> None:
        fake_choice = MagicMock()
        fake_choice.message.content = "ok-result"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        fake_client.chat.completions.create.return_value = fake_resp
        with patch("openai.OpenAI", return_value=fake_client):
            svc = LLMService(api_key="k", provider="openrouter")
            out = svc._generate_openai_compatible("hi", None, 0.7, 100)
        assert out == "ok-result"

    def test_with_system_instruction(self) -> None:
        """Line 334: system_instruction is prepended to messages."""
        fake_choice = MagicMock()
        fake_choice.message.content = "result"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        fake_client.chat.completions.create.return_value = fake_resp
        with patch("openai.OpenAI", return_value=fake_client):
            svc = LLMService(api_key="k", provider="openrouter")
            out = svc._generate_openai_compatible("prompt", "sys instruction", 0.7, 100)
        assert out == "result"
        fake_client.chat.completions.create.assert_called_once()
        call_kwargs = fake_client.chat.completions.create.call_args
        messages = call_kwargs.kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "sys instruction"

    def test_null_content_returns_empty_string(self) -> None:
        fake_choice = MagicMock()
        fake_choice.message.content = None
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        fake_client.chat.completions.create.return_value = fake_resp
        with patch("openai.OpenAI", return_value=fake_client):
            svc = LLMService(api_key="k", provider="openrouter")
            out = svc._generate_openai_compatible("hi", None, 0.7, 100)
        assert out == ""

    def test_403_forbidden_skips_model(self) -> None:
        """Lines 358-360: 403 → skip without retry, next model succeeds."""

        fake_choice = MagicMock()
        fake_choice.message.content = "ok"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):  # type: ignore[no-untyped-def]
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise Exception("Error code: 403 - only available on agentic harness")
            return fake_resp

        fake_client.chat.completions.create.side_effect = side_effect
        with patch("openai.OpenAI", return_value=fake_client):
            svc = LLMService(api_key="k", provider="openrouter", model_name="bad:free")
            out = svc._generate_openai_compatible("hi", None, 0.7, 100)
        assert out == "ok"
        assert call_count["n"] == 2

    def test_401_unsupported_skips_model(self) -> None:
        """Lines 391-394: 401 with 'ModelError'/'not supported' → skip next model."""
        fake_choice = MagicMock()
        fake_choice.message.content = "ok-after-401"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):  # type: ignore[no-untyped-def]
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise Exception(
                    "Error code: 401 - {'type': 'error', 'error': {'type': 'ModelError', 'message': 'Model not supported'}}"
                )
            return fake_resp

        fake_client.chat.completions.create.side_effect = side_effect
        with patch("openai.OpenAI", return_value=fake_client):
            svc = LLMService(api_key="k", provider="openrouter", model_name="unsupported:free")
            out = svc._generate_openai_compatible("hi", None, 0.7, 100)
        assert out == "ok-after-401"
        assert call_count["n"] == 2

    def test_429_rate_limit_backoff_and_retry(self) -> None:
        """Lines 368-377: 429 on non-last model → backoff sleep → retry next."""
        fake_choice = MagicMock()
        fake_choice.message.content = "after-backoff"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):  # type: ignore[no-untyped-def]
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise Exception("Error code: 429 - rate limit exceeded")
            return fake_resp

        fake_client.chat.completions.create.side_effect = side_effect
        with (
            patch("openai.OpenAI", return_value=fake_client),
            patch("src.llm_service.time.sleep") as mock_sleep,
        ):
            svc = LLMService(api_key="k", provider="openrouter", model_name="rate-limited:free")
            out = svc._generate_openai_compatible("hi", None, 0.7, 100)
        assert out == "after-backoff"
        assert mock_sleep.called
        assert mock_sleep.call_args.args[0] == 8

    def test_429_on_last_model_raises_no_backoff(self) -> None:
        """Lines 378-384: 429 on last model → no backoff, raise."""
        fake_client = MagicMock()
        fake_client.chat.completions.create.side_effect = Exception(
            "Error code: 429 - quota exceeded"
        )
        with (
            patch("openai.OpenAI", return_value=fake_client),
            patch("src.llm_service.time.sleep") as mock_sleep,
        ):
            svc = LLMService(api_key="k", provider="opencode", model_name="only-model")
            svc._active_provider.fallback_models = []
            with pytest.raises(Exception, match="quota exceeded"):
                svc._generate_openai_compatible("hi", None, 0.7, 100)
        assert not mock_sleep.called

    def test_429_keyword_quota_exceeded_triggers_backoff(self) -> None:
        """Lines 362-366: 'quota exceeded' substring triggers rate-limit branch."""
        fake_choice = MagicMock()
        fake_choice.message.content = "after-quota"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):  # type: ignore[no-untyped-def]
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise Exception("RESOURCE_EXHAUSTED - quota exceeded for metric")
            return fake_resp

        fake_client.chat.completions.create.side_effect = side_effect
        with (
            patch("openai.OpenAI", return_value=fake_client),
            patch("src.llm_service.time.sleep") as mock_sleep,
        ):
            svc = LLMService(api_key="k", provider="openrouter", model_name="quota-model:free")
            out = svc._generate_openai_compatible("hi", None, 0.7, 100)
        assert out == "after-quota"
        assert mock_sleep.called

    def test_generic_error_on_last_model_raises(self) -> None:
        """Lines 385-389: generic error (not 403/429) → raise last_error."""
        fake_client = MagicMock()
        fake_client.chat.completions.create.side_effect = RuntimeError("network down")
        with patch("openai.OpenAI", return_value=fake_client):
            svc = LLMService(api_key="k", provider="opencode", model_name="only-model")
            svc._active_provider.fallback_models = []
            with pytest.raises(RuntimeError, match="network down"):
                svc._generate_openai_compatible("hi", None, 0.7, 100)

    def test_openai_import_error_raised(self) -> None:
        """Lines 321-322: ImportError when openai package missing."""
        with patch.dict(sys.modules, {"openai": None}):
            with pytest.raises(ImportError, match="openai package required"):
                LLMService._generate_openai_compatible(
                    self=None,  # type: ignore[arg-type]
                    prompt="hi",
                    system_instruction=None,
                    temperature=0.7,
                    max_tokens=100,
                )


# ── Gemini provider ────────────────────────────────────────────────


class TestLLMGemini:
    """_generate_gemini: timeout, successful response, empty text."""

    def test_gemini_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import src.llm_service as ls

        fake_resp = MagicMock()
        fake_resp.text = "gemini-result"
        fake_model = MagicMock()
        fake_model.generate_content.return_value = fake_resp
        fake_client = MagicMock()
        fake_client.models = fake_model
        fake_genai = MagicMock()
        fake_genai.Client.return_value = fake_client
        monkeypatch.setattr(ls, "genai", fake_genai)
        svc = LLMService(api_key="goog-key", provider="gemini")
        out = svc._generate_gemini("hi", None, 0.7, 100)
        assert out == "gemini-result"

    def test_gemini_response_empty_text_returns_empty_string(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import src.llm_service as ls

        fake_resp = MagicMock()
        fake_resp.text = ""
        fake_model = MagicMock()
        fake_model.generate_content.return_value = fake_resp
        fake_client = MagicMock()
        fake_client.models = fake_model
        fake_genai = MagicMock()
        fake_genai.Client.return_value = fake_client
        monkeypatch.setattr(ls, "genai", fake_genai)
        svc = LLMService(api_key="goog-key", provider="gemini")
        out = svc._generate_gemini("hi", None, 0.7, 100)
        assert out == ""

    def test_gemini_timeout_raises_runtime_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Lines 305-307: ThreadPoolExecutor TimeoutError → RuntimeError."""
        import concurrent.futures
        import src.llm_service as ls

        fake_client = MagicMock()

        def hang(*args, **kwargs):  # type: ignore[no-untyped-def]
            raise concurrent.futures.TimeoutError()

        fake_client.models.generate_content = hang
        fake_genai = MagicMock()
        fake_genai.Client.return_value = fake_client
        monkeypatch.setattr(ls, "genai", fake_genai)
        monkeypatch.setattr(ls, "LLM_CALL_TIMEOUT_S", 1)
        svc = LLMService(api_key="goog-key", provider="gemini", model_name="gemini-3.6-flash")
        with pytest.raises(RuntimeError, match="Gemini call timed out"):
            svc._generate_gemini("hi", None, 0.7, 100)

    def test_gemini_import_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import src.llm_service as ls

        monkeypatch.setattr(ls, "genai", None)
        svc = LLMService(api_key="goog-key", provider="gemini")
        with pytest.raises(ImportError, match="google.genai package not available"):
            svc._generate_gemini("hi", None, 0.7, 100)


# ── Public async/sync API ─────────────────────────────────────────


class TestLLMPublicAPI:
    """Async aliases and public methods: generate_text, classify_text, summarize, etc."""

    def test_generate_text_alias(self) -> None:
        svc = LLMService(api_key=None, provider="none")
        out = asyncio.run(svc.generate_text("hello"))
        assert out.startswith("[Mock")

    def test_classify_text_with_categories(self) -> None:
        svc = LLMService(api_key=None, provider="none")
        out = asyncio.run(svc.classify_text("some text", categories=["A", "B"]))
        assert out.startswith("[Mock")

    def test_classify_text_no_categories(self) -> None:
        svc = LLMService(api_key=None, provider="none")
        out = asyncio.run(svc.classify_text("some text"))
        assert out.startswith("[Mock")

    def test_summarize(self) -> None:
        svc = LLMService(api_key=None, provider="none")
        out = svc.summarize("long text here")
        assert out.startswith("[Mock")

    def test_summarize_with_max_length(self) -> None:
        svc = LLMService(api_key=None, provider="none")
        out = svc.summarize("long text here", max_length=50)
        assert out.startswith("[Mock")

    @pytest.mark.asyncio
    async def test_summarize_release_notes(self) -> None:
        svc = LLMService(api_key=None, provider="none")
        out = await svc.summarize_release_notes("raw notes")
        assert out.startswith("[Mock")

    @pytest.mark.asyncio
    async def test_enrich_feature(self) -> None:
        svc = LLMService(api_key=None, provider="none")
        out = await svc.enrich_feature({"name": "Feature X"})
        assert out["enriched"] is True
        assert "details" in out

    @pytest.mark.asyncio
    async def test_enrich_feature_with_context(self) -> None:
        svc = LLMService(api_key=None, provider="none")
        out = await svc.enrich_feature({"name": "Feature X"}, context="release context")
        assert out["enriched"] is True

    @pytest.mark.asyncio
    async def test_async_context_manager(self) -> None:
        async with LLMService(api_key="k") as svc:
            assert isinstance(svc, LLMService)


# ── Module integrity ───────────────────────────────────────────────


class TestLLMModuleIntegrity:
    """Module-level sanity: reload, constants, _find_provider_config."""

    def test_module_reload_succeeds(self) -> None:
        if "src.llm_service" in sys.modules:
            importlib.reload(sys.modules["src.llm_service"])
        assert "src.llm_service" in sys.modules

    def test_find_provider_config(self) -> None:
        assert LLMService._find_provider_config("opencode") is not None
        assert LLMService._find_provider_config("openrouter") is not None
        assert LLMService._find_provider_config("gemini") is not None
        assert LLMService._find_provider_config("banana") is None

    def test_llm_call_timeout_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import importlib
        import src.llm_service as ls

        monkeypatch.setenv("LLM_CALL_TIMEOUT_S", "30")
        importlib.reload(ls)
        assert ls.LLM_CALL_TIMEOUT_S == 30
        monkeypatch.delenv("LLM_CALL_TIMEOUT_S", raising=False)
        importlib.reload(ls)
        assert ls.LLM_CALL_TIMEOUT_S == 60

    def test_llm_call_timeout_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import importlib
        import src.llm_service as ls

        monkeypatch.delenv("LLM_CALL_TIMEOUT_S", raising=False)
        importlib.reload(ls)
        assert ls.LLM_CALL_TIMEOUT_S == 60


# ── Dispatch router ──────────────────────────────────────────────


class TestLLMDispatch:
    """_dispatch_to_provider: routes by provider name, raises on unknown."""

    def test_dispatch_to_gemini(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Line 263: provider='gemini' → _generate_gemini path."""
        monkeypatch.setenv("GOOGLE_API_KEY", "goog-key")
        svc = LLMService(api_key="goog-key", provider="gemini")
        with patch.object(svc, "_generate_gemini", return_value="gem-out") as mock_g:
            out = svc._dispatch_to_provider("hi", None, 0.7, 100)
        assert out == "gem-out"
        mock_g.assert_called_once()

    def test_dispatch_to_openai_compatible(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Line 270: provider in (opencode, openrouter) → _generate_openai_compatible."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        svc = LLMService(api_key="or-key", provider="openrouter")
        with patch.object(svc, "_generate_openai_compatible", return_value="oai-out") as mock_o:
            out = svc._dispatch_to_provider("hi", None, 0.7, 100)
        assert out == "oai-out"
        mock_o.assert_called_once()

    def test_dispatch_unsupported_raises(self) -> None:
        """Line 277: provider='none' (no active provider) → ValueError."""
        svc = LLMService(api_key=None, provider="none")
        svc._active_provider = None
        svc.provider = "none"
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            svc._dispatch_to_provider("hi", None, 0.7, 100)
