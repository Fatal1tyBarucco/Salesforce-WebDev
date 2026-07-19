import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.llm_service import LLMService, CircuitBreakerConfig, LLMProvider


@pytest.fixture
def config():
    return CircuitBreakerConfig(threshold=3, cooldown=0.1)


@pytest.fixture
def mock_providers():
    return [
        LLMProvider(name="test1", api_key="key1", provider_type="openai"),
        LLMProvider(name="test2", api_key="key2", provider_type="openai"),
    ]


@pytest.fixture
def llm_service(config, mock_providers):
    return LLMService(config=config, providers=mock_providers)


def test_generate_success(llm_service):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello world"))]

    with patch.object(llm_service, "_call_provider", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = "Hello world"
        result = asyncio.run(llm_service.generate_text("Prompt", "System"))
        assert result == "Hello world"


def test_fallback_to_next_provider(llm_service):
    with patch.object(llm_service, "_call_provider", new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = [
            Exception("Provider 1 failed"),
            "Success from provider 2",
        ]
        result = asyncio.run(llm_service.generate_text("Prompt", "System"))
        assert result == "Success from provider 2"
        assert mock_call.call_count == 2


def test_all_providers_fail(llm_service):
    with patch.object(llm_service, "_call_provider", new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = Exception("All failed")
        result = asyncio.run(llm_service.generate_text("Prompt", "System"))
        assert result is None


def test_circuit_breaker_trips(llm_service):
    with patch.object(llm_service, "_call_provider", new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = Exception("API Down")

        for _ in range(llm_service._config.threshold):
            asyncio.run(llm_service.generate_text("Prompt", "System"))

        mock_call.reset_mock()
        result = asyncio.run(llm_service.generate_text("Prompt", "System"))
        assert result is None
        assert mock_call.call_count == 0


def test_circuit_breaker_half_open_recovery(llm_service):
    with patch.object(llm_service, "_call_provider", new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = Exception("API Down")
        for _ in range(llm_service._config.threshold):
            asyncio.run(llm_service.generate_text("Prompt", "System"))

        import time

        time.sleep(0.2)

        mock_call.side_effect = None
        mock_call.return_value = "Recovered"
        result = asyncio.run(llm_service.generate_text("Prompt", "System"))
        assert result == "Recovered"

        mock_call.reset_mock()
        asyncio.run(llm_service.generate_text("Prompt", "System"))
        assert mock_call.call_count == 1


def test_rate_limit_failure_after_retries(llm_service):
    with patch.object(llm_service, "_call_provider", new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = Exception("Rate limit exceeded")
        result = asyncio.run(llm_service.generate_text("Prompt", "System"))
        assert result is None
        assert llm_service._get_provider_state(llm_service._providers[0]).failures > 0


def test_generic_exception(llm_service):
    with patch.object(llm_service, "_call_provider", new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = ValueError("Unexpected")
        result = asyncio.run(llm_service.generate_text("Prompt", "System"))
        assert result is None
        assert llm_service._get_provider_state(llm_service._providers[0]).failures > 0


def test_classify_text_success(llm_service):
    with patch.object(llm_service, "generate_text", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = '{"Security": {"applies": true, "confidence": 0.9}}'
        result = asyncio.run(llm_service.classify_text("text", ["Security"]))
        assert "Security" in result
        assert result["Security"]["applies"] is True


def test_classify_text_no_result(llm_service):
    with patch.object(llm_service, "generate_text", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = None
        result = asyncio.run(llm_service.classify_text("text", ["Security"]))
        assert "error" in result


def test_classify_text_invalid_json(llm_service):
    with patch.object(llm_service, "generate_text", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "not json at all"
        result = asyncio.run(llm_service.classify_text("text", ["Security"]))
        assert "error" in result


def test_providers_loaded_from_env():
    with patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "test-key",
            "GOOGLE_API_KEY": "google-key",
            "OPENCODE_API_KEY": "opencode-key",
        },
    ):
        service = LLMService()
        names = [p.name for p in service._providers]
        assert "openai" in names
        assert "google" in names
        assert "opencode" in names


def test_providers_loaded_mimocode():
    with patch.dict("os.environ", {"MIMOCODE_API_KEY": "mimo-key"}):
        service = LLMService()
        names = [p.name for p in service._providers]
        assert "mimocode" in names


def test_call_openai_provider():
    provider = LLMProvider(name="test", api_key="key", provider_type="openai")
    service = LLMService(providers=[provider])

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]

    with patch("openai.AsyncOpenAI") as MockOpenAI:
        MockOpenAI.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
        result = asyncio.run(service._call_openai_provider(provider, "System", "User"))
        assert result == "Response"


def test_call_openai_provider_string_response():
    provider = LLMProvider(name="test", api_key="key", provider_type="openai")
    service = LLMService(providers=[provider])

    with patch("openai.AsyncOpenAI") as MockOpenAI:
        MockOpenAI.return_value.chat.completions.create = AsyncMock(return_value="String response")
        result = asyncio.run(service._call_openai_provider(provider, "System", "User"))
        assert result == "String response"


def test_call_google_provider():
    provider = LLMProvider(name="test", api_key="key", provider_type="google")
    service = LLMService(providers=[provider])

    mock_response = MagicMock()
    mock_response.text = "Google response"

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    mock_genai = MagicMock()
    mock_genai.Client.return_value = mock_client
    mock_genai.types.GenerateContentConfig = MagicMock()

    with patch("src.llm_service.genai", mock_genai):
        result = asyncio.run(service._call_google_provider(provider, "System", "User"))
        assert result == "Google response"


def test_call_provider_routing():
    service = LLMService()

    google_provider = LLMProvider(name="google", api_key="key", provider_type="google")
    openai_provider = LLMProvider(name="openai", api_key="key", provider_type="openai")

    with patch.object(service, "_call_google_provider", new_callable=AsyncMock) as mock_google:
        mock_google.return_value = "Google"
        result = asyncio.run(service._call_provider(google_provider, "System", "User"))
        assert result == "Google"

    with patch.object(service, "_call_openai_provider", new_callable=AsyncMock) as mock_openai:
        mock_openai.return_value = "OpenAI"
        result = asyncio.run(service._call_provider(openai_provider, "System", "User"))
        assert result == "OpenAI"


def test_auth_error_logging():
    config = CircuitBreakerConfig(threshold=10, cooldown=0.1)
    provider = LLMProvider(name="test", api_key="key", provider_type="openai")
    service = LLMService(config=config, providers=[provider])

    with patch.object(service, "_call_provider", new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = Exception("401 Unauthorized")
        asyncio.run(service.generate_text("Prompt", "System"))


def test_legacy_client_fallback():
    service = LLMService(providers=[])
    service._client = MagicMock()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Legacy response"))]
    service._client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = asyncio.run(service.generate_text("Prompt", "System"))
    assert result == "Legacy response"


def test_legacy_client_error():
    service = LLMService(providers=[])
    service._client = MagicMock()
    service._client.chat.completions.create = AsyncMock(side_effect=Exception("Legacy error"))

    result = asyncio.run(service.generate_text("Prompt", "System"))
    assert result is None


def test_call_openai_provider_non_standard_response():
    """_call_openai_provider falls back to str(response) for non-standard types."""
    provider = LLMProvider(name="test", api_key="key", provider_type="openai")
    service = LLMService(providers=[provider])

    # Return an object without 'choices' attribute and not a string
    class WeirdResponse:
        pass

    with patch("openai.AsyncOpenAI") as MockOpenAI:
        MockOpenAI.return_value.chat.completions.create = AsyncMock(return_value=WeirdResponse())
        result = asyncio.run(service._call_openai_provider(provider, "System", "User"))
        assert isinstance(result, str)
