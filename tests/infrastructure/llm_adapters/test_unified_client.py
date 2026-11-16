"""Tests for UnifiedLLMClient - 100% coverage target."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from src.cache_manager import CacheManager
from src.domain.llm import (
    LLMAuthError,
    LLMModel,
    LLMPrompt,
    LLMProvider,
    LLMRateLimitError,
    LLMResponse,
    LLMUsage,
    ProviderConfig,
)
from src.infrastructure.llm_adapters.cache import LLMCacheAdapter
from src.infrastructure.llm_adapters.unified_client import UnifiedLLMClient

# Set environment variables globally for all tests
os.environ["TEST_OPENROUTER_KEY"] = "test-key-1"
os.environ["TEST_OPENCODE_KEY"] = "test-key-2"
os.environ["TEST_GEMINI_KEY"] = "test-key-3"


@pytest.fixture(autouse=True)
def isolated_llm_cache(tmp_path, monkeypatch):
    """Point the default LLMCacheAdapter at a per-test directory.

    The adapter defaults to ``cache/llm`` relative to the working directory;
    without this shim the (now functional) cache leaks between tests and
    writes files into the repository working tree.
    """
    from src.infrastructure.llm_adapters import cache as cache_module

    real_cache_manager = cache_module.CacheManager
    cache_dir = tmp_path / "llm_cache"

    def _isolated_manager(*_args, **_kwargs):
        return real_cache_manager(cache_dir=cache_dir)

    monkeypatch.setattr(cache_module, "CacheManager", _isolated_manager)


def make_mock_response(content: str, prompt_tokens: int = 10, completion_tokens: int = 20):
    """Create a properly configured mock response with content attribute."""
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.content = content
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_response.usage = MagicMock(
        prompt_tokens=prompt_tokens, completion_tokens=completion_tokens
    )
    # Add content attribute for the _dispatch_with_fallback method
    type(mock_response).content = PropertyMock(return_value=content)
    return mock_response


def make_mock_openai(response_content: str):
    """Create a mock OpenAI client."""
    mock_openai = MagicMock()
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.content = response_content
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=20)
    type(mock_response).content = PropertyMock(return_value=response_content)
    mock_openai = MagicMock()
    mock_openai.chat.completions.create = MagicMock(return_value=mock_response)
    return mock_openai


def get_openai_client(client):
    """Get the OpenAI client from the client's internal cache."""
    from src.domain.llm import LLMProvider

    return client._clients.get(LLMProvider.OPENROUTER)


class TestUnifiedLLMClient:
    """Tests for UnifiedLLMClient."""

    @pytest.fixture
    def mock_provider_chain(self) -> tuple[ProviderConfig, ...]:
        """Create mock provider chain with test env vars."""
        return (
            ProviderConfig(
                name=LLMProvider.OPENROUTER,
                api_key_env="TEST_OPENROUTER_KEY",
                base_url="https://test.openrouter.ai",
                default_model=LLMModel.OPENROUTER_FREE,
            ),
            ProviderConfig(
                name=LLMProvider.OPENCODE,
                api_key_env="TEST_OPENCODE_KEY",
                base_url="https://test.opencode.ai",
                default_model=LLMModel.GEMINI_36_FLASH,
            ),
            ProviderConfig(
                name=LLMProvider.GEMINI,
                api_key_env="TEST_GEMINI_KEY",
                default_model=LLMModel.GEMINI_36_FLASH_DIRECT,
            ),
        )

    @pytest.fixture
    def client(self, mock_provider_chain) -> UnifiedLLMClient:
        """Create client with mock providers."""
        return UnifiedLLMClient(provider_chain=mock_provider_chain)

    @pytest.mark.asyncio
    async def test_init_auto_detects_first_provider(self, client):
        """Should auto-detect first available provider."""
        assert client._active_provider is not None
        assert client._active_provider.name == LLMProvider.OPENROUTER

    @pytest.mark.asyncio
    async def test_init_no_keys_returns_mock(self, mock_provider_chain):
        """Should return mock responses when no API keys configured."""
        old_env = {}
        for key in ["TEST_OPENROUTER_KEY", "TEST_OPENCODE_KEY", "TEST_GEMINI_KEY"]:
            old_env[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]

        try:
            client = UnifiedLLMClient(provider_chain=mock_provider_chain)
            assert client._active_provider is None
        finally:
            for key, value in old_env.items():
                if value is not None:
                    os.environ[key] = value

    @pytest.mark.asyncio
    async def test_generate_returns_mock_when_no_provider(self, mock_provider_chain):
        """Should return mock response when no provider available."""
        old_env = {}
        for key in ["TEST_OPENROUTER_KEY", "TEST_OPENCODE_KEY", "TEST_GEMINI_KEY"]:
            old_env[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]

        try:
            client = UnifiedLLMClient(provider_chain=mock_provider_chain)
            prompt = LLMPrompt(user="Test prompt")
            response = await client.generate(prompt)

            assert isinstance(response, LLMResponse)
            assert "[Mock]" in response.content
            assert response.provider == LLMProvider.OPENROUTER
        finally:
            for key, value in old_env.items():
                if value is not None:
                    os.environ[key] = value

    @pytest.mark.asyncio
    async def test_generate_returns_same_response(self, client):
        """Should return same response for same prompt (cache or no cache)."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai = make_mock_openai("Test response")
            mock_openai_class.return_value = mock_openai

            prompt = LLMPrompt(user="Test prompt")
            response1 = await client.generate(prompt)
            response2 = await client.generate(prompt)

            assert response1.content == "Test response"
            assert response2.content == "Test response"
            # Both responses should have same content
            assert response1.content == response2.content

    @pytest.mark.asyncio
    async def test_generate_structured_validates_schema(self, client):
        """Should generate and validate structured response."""
        from pydantic import BaseModel

        class TestSchema(BaseModel):
            name: str
            value: int

        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai = make_mock_openai('{"name": "test", "value": 42}')
            mock_openai_class.return_value = mock_openai

            prompt = LLMPrompt(user="Generate test data")
            result = await client.generate_structured(prompt, TestSchema)

            assert isinstance(result, TestSchema)
            assert result.name == "test"
            assert result.value == 42

    @pytest.mark.asyncio
    async def test_generate_structured_raises_on_invalid_json(self, client):
        """Should raise LLMError on invalid JSON response."""
        from pydantic import BaseModel

        class TestSchema(BaseModel):
            name: str

        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai = make_mock_openai("not valid json")
            mock_openai_class.return_value = mock_openai

            prompt = LLMPrompt(user="Generate test data")
            with pytest.raises(Exception):
                await client.generate_structured(prompt, TestSchema)

    @pytest.mark.asyncio
    async def test_health_check_with_provider(self, client):
        """Should return True when provider is healthy."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai = make_mock_openai("OK")
            mock_openai_class.return_value = mock_openai

            result = await client.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_without_provider(self, mock_provider_chain):
        """Should return False when no provider available."""
        old_env = {}
        for key in ["TEST_OPENROUTER_KEY", "TEST_OPENCODE_KEY", "TEST_GEMINI_KEY"]:
            old_env[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]

        try:
            client = UnifiedLLMClient(provider_chain=mock_provider_chain)
            result = await client.health_check()
            assert result is False
        finally:
            for key, value in old_env.items():
                if value is not None:
                    os.environ[key] = value

    def test_get_usage_stats(self, client):
        """Should return usage statistics."""
        stats = client.get_usage_stats()

        assert "total_calls" in stats
        assert "total_tokens" in stats
        assert "total_cost_usd" in stats
        assert "active_provider" in stats
        assert "rate_limits" in stats

    @pytest.mark.asyncio
    async def test_fallback_on_rate_limit(self, mock_provider_chain):
        """Should fallback to next provider on rate limit."""
        client = UnifiedLLMClient(provider_chain=mock_provider_chain)

        with patch("openai.OpenAI") as mock_openai_class:
            mock_openrouter = make_mock_openai("")
            mock_openrouter.chat.completions.create.side_effect = LLMRateLimitError(
                "Rate limited", provider=LLMProvider.OPENROUTER
            )

            mock_opencode = make_mock_openai("Fallback response")

            mock_openai_class.side_effect = [mock_openrouter, mock_opencode]

            prompt = LLMPrompt(user="Test prompt")
            response = await client.generate(prompt)

            assert response.content == "Fallback response"
            assert client._active_provider.name == LLMProvider.OPENCODE

    @pytest.mark.asyncio
    async def test_fallback_on_auth_error(self, mock_provider_chain):
        """Should fallback to next provider on auth error."""
        client = UnifiedLLMClient(provider_chain=mock_provider_chain)

        with patch("openai.OpenAI") as mock_openai_class:
            mock_openrouter = make_mock_openai("")
            mock_openrouter.chat.completions.create.side_effect = LLMAuthError(
                "Invalid key", provider=LLMProvider.OPENROUTER
            )

            mock_opencode = make_mock_openai("Fallback response")

            mock_openai_class.side_effect = [mock_openrouter, mock_opencode]

            prompt = LLMPrompt(user="Test prompt")
            response = await client.generate(prompt)

            assert response.content == "Fallback response"

    @pytest.mark.asyncio
    async def test_all_providers_exhausted_raises(self, mock_provider_chain):
        """Should raise when all providers exhausted."""
        from src.domain.llm import LLMRateLimitError

        single_provider = (mock_provider_chain[0],)
        client = UnifiedLLMClient(provider_chain=single_provider)

        with patch("openai.OpenAI") as mock_openai_class:
            mock_openrouter = make_mock_openai("")
            mock_openrouter.chat.completions.create.side_effect = LLMRateLimitError(
                "Rate limited", provider=LLMProvider.OPENROUTER
            )
            mock_openai_class.return_value = mock_openrouter

            prompt = LLMPrompt(user="Test prompt")
            with pytest.raises(LLMRateLimitError):
                await client.generate(prompt)

    @pytest.mark.asyncio
    async def test_cache_key_is_deterministic(self, client):
        """Cache key should be deterministic for same prompt."""
        prompt1 = LLMPrompt(user="Test", system="System", temperature=0.5)
        prompt2 = LLMPrompt(user="Test", system="System", temperature=0.5)
        prompt3 = LLMPrompt(user="Test", system="System", temperature=0.7)

        assert prompt1.cache_key() == prompt2.cache_key()
        assert prompt1.cache_key() != prompt3.cache_key()

    @pytest.mark.asyncio
    async def test_usage_aggregation(self, client):
        """Should aggregate usage across calls."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai = make_mock_openai("Test")
            mock_openai_class.return_value = mock_openai

            # Distinct prompts: identical prompts are served from the cache and
            # would not be counted as a second call.
            await client.generate(LLMPrompt(user="Test one"))
            await client.generate(LLMPrompt(user="Test two"))

            stats = client.get_usage_stats()
            assert stats["total_calls"] == 2
            assert stats["total_tokens"] == 60
            assert stats["prompt_tokens"] == 20
            assert stats["completion_tokens"] == 40

    @pytest.mark.asyncio
    async def test_env_model_override(self, mock_provider_chain):
        """Should respect environment model override."""
        os.environ["OPENROUTER_MODEL"] = "custom/model"

        try:
            client = UnifiedLLMClient(provider_chain=mock_provider_chain)

            with patch("openai.OpenAI") as mock_openai_class:
                mock_openai = make_mock_openai("Test")
                mock_openai_class.return_value = mock_openai

                prompt = LLMPrompt(user="Test")
                await client.generate(prompt)

                openai_client = get_openai_client(client)
                call_args = openai_client.chat.completions.create.call_args
                assert call_args[1]["model"] == "custom/model"
        finally:
            if "OPENROUTER_MODEL" in os.environ:
                del os.environ["OPENROUTER_MODEL"]

    @pytest.mark.asyncio
    async def test_temperature_and_max_tokens(self, client):
        """Should pass temperature and max_tokens to provider."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai = make_mock_openai("Test")
            mock_openai_class.return_value = mock_openai

            prompt = LLMPrompt(user="Test", temperature=0.9, max_tokens=500)
            await client.generate(prompt)

            openai_client = get_openai_client(client)
            call_args = openai_client.chat.completions.create.call_args
            assert call_args[1]["temperature"] == 0.9
            assert call_args[1]["max_tokens"] == 500

    @pytest.mark.asyncio
    async def test_response_format(self, client):
        """Should pass response_format to provider."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai = make_mock_openai('{"key": "value"}')
            mock_openai_class.return_value = mock_openai

            prompt = LLMPrompt(user="Test", response_format={"type": "json_object"})
            await client.generate(prompt)

            openai_client = get_openai_client(client)
            call_args = openai_client.chat.completions.create.call_args
            assert call_args[1]["response_format"] == {"type": "json_object"}

    @pytest.mark.asyncio
    async def test_rate_limiter_integration(self, client):
        """Should respect rate limiter."""
        prompt = LLMPrompt(user="Test")

        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai = make_mock_openai("Test")
            mock_openai_class.return_value = mock_openai

            await client.generate(prompt)

            # Rate limiter uses masked provider value as key
            assert client._rate_limiter._states.get("XXXXopenrouterXXXX") is not None

    @pytest.mark.asyncio
    async def test_cache_hit_marks_response_cached(self, mock_provider_chain, tmp_path):
        """Cache hit must return the stored response flagged as cached."""
        cache = LLMCacheAdapter(cache_manager=CacheManager(cache_dir=tmp_path / "cache_hit"))
        client = UnifiedLLMClient(provider_chain=mock_provider_chain, cache=cache)

        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai = make_mock_openai("Cached content")
            mock_openai_class.return_value = mock_openai

            prompt = LLMPrompt(user="Cache hit marking")

            first = await client.generate(prompt)
            assert first.cached is False
            assert first.provider is LLMProvider.OPENROUTER
            assert first.usage.total_tokens == 30

            second = await client.generate(prompt)

            assert second.cached is True
            assert second.content == "Cached content"
            assert second.provider is LLMProvider.OPENROUTER
            assert second.usage.total_tokens == 30
            assert mock_openai.chat.completions.create.call_count == 1
            assert client.get_usage_stats()["total_calls"] == 1

    @pytest.mark.asyncio
    async def test_generate_structured_hits_cache(self, mock_provider_chain, tmp_path):
        """Structured generation goes through the working cache."""
        from pydantic import BaseModel

        class Schema(BaseModel):
            name: str

        cache = LLMCacheAdapter(cache_manager=CacheManager(cache_dir=tmp_path / "structured"))
        client = UnifiedLLMClient(provider_chain=mock_provider_chain, cache=cache)

        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai = make_mock_openai('{"name": "cached"}')
            mock_openai_class.return_value = mock_openai

            prompt = LLMPrompt(user="Structured cache")
            first = await client.generate_structured(prompt, Schema)
            second = await client.generate_structured(prompt, Schema)

            assert first.name == "cached"
            assert second.name == "cached"
            assert mock_openai.chat.completions.create.call_count == 1

    @pytest.mark.asyncio
    async def test_mock_response_usage(self):
        """Mock responses carry mock usage metadata."""
        client = UnifiedLLMClient()
        client._active_provider = None

        response = await client.generate(LLMPrompt(user="Mock usage"))

        assert isinstance(response.usage, LLMUsage)
        assert response.usage.provider == "mock"
        assert response.cached is False


class TestLLMServiceCompat:
    """Tests for legacy LLMService compatibility wrapper."""

    def test_generate_completion_sync(self):
        """Legacy generate_completion should work synchronously."""
        from src.infrastructure.llm_adapters.unified_client import LLMService

        os.environ["TEST_KEY"] = "test"
        try:
            service = LLMService()
            service._client._active_provider = None

            result = service.generate_completion("Test prompt")
            assert "[Mock]" in result
        finally:
            if "TEST_KEY" in os.environ:
                del os.environ["TEST_KEY"]

    def test_summarize(self):
        """Legacy summarize should work."""
        from src.infrastructure.llm_adapters.unified_client import LLMService

        os.environ["TEST_KEY"] = "test"
        try:
            service = LLMService()
            service._client._active_provider = None

            result = service.summarize("Long text to summarize", max_length=50)
            assert "[Mock]" in result
        finally:
            if "TEST_KEY" in os.environ:
                del os.environ["TEST_KEY"]
