import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from openai import RateLimitError, APIConnectionError, InternalServerError
from src.llm_service import LLMService, CircuitBreakerConfig


@pytest.fixture
def config():
    return CircuitBreakerConfig(threshold=3, cooldown=0.1)


@pytest.fixture
def mock_client():
    return AsyncMock()


@pytest.fixture
def llm_service(config, mock_client):
    return LLMService(config=config, client=mock_client)


@pytest.mark.asyncio
async def test_generate_success(llm_service, mock_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello world"))]
    mock_client.chat.completions.create.return_value = mock_response

    result = await llm_service.generate_text("Prompt", "System")
    assert result == "Hello world"
    mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_retry_on_rate_limit(llm_service, mock_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Success after retry"))]

    mock_client.chat.completions.create.side_effect = [
        RateLimitError("Rate limit exceeded", response=MagicMock(), body={}),
        mock_response,
    ]

    result = await llm_service.generate_text("Prompt", "System")
    assert result == "Success after retry"
    assert mock_client.chat.completions.create.call_count == 2


@pytest.mark.asyncio
async def test_generate_retry_on_connection_error(llm_service, mock_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Success after conn error"))]

    mock_client.chat.completions.create.side_effect = [
        APIConnectionError(request=MagicMock()),
        mock_response,
    ]

    result = await llm_service.generate_text("Prompt", "System")
    assert result == "Success after conn error"
    assert mock_client.chat.completions.create.call_count == 2


@pytest.mark.asyncio
async def test_generate_retry_on_internal_server_error(llm_service, mock_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Success after server error"))]

    mock_client.chat.completions.create.side_effect = [
        InternalServerError("Server error", response=MagicMock(), body={}),
        mock_response,
    ]

    result = await llm_service.generate_text("Prompt", "System")
    assert result == "Success after server error"
    assert mock_client.chat.completions.create.call_count == 2


@pytest.mark.asyncio
async def test_circuit_breaker_trips(llm_service, mock_client):
    mock_client.chat.completions.create.side_effect = InternalServerError(
        "API Down", response=MagicMock(), body={}
    )

    for _ in range(llm_service._config.threshold):
        await llm_service.generate_text("Prompt", "System")

    mock_client.chat.completions.create.reset_mock()
    result = await llm_service.generate_text("Prompt", "System")

    assert result is None
    mock_client.chat.completions.create.assert_not_called()


@pytest.mark.asyncio
async def test_circuit_breaker_half_open_recovery(llm_service, mock_client):
    mock_client.chat.completions.create.side_effect = InternalServerError(
        "API Down", response=MagicMock(), body={}
    )
    for _ in range(llm_service._config.threshold):
        await llm_service.generate_text("Prompt", "System")

    await asyncio.sleep(0.2)

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Recovered"))]
    mock_client.chat.completions.create.side_effect = None
    mock_client.chat.completions.create.return_value = mock_response

    result = await llm_service.generate_text("Prompt", "System")
    assert result == "Recovered"

    mock_client.chat.completions.create.reset_mock()
    await llm_service.generate_text("Prompt", "System")
    mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_classify_text_default_prompt(llm_service, mock_client):
    """classify_text uses default system_prompt when none provided."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"Security": {"applies": true}}'))
    ]
    mock_client.chat.completions.create.return_value = mock_response

    result = await llm_service.classify_text("test text", ["Security"])
    assert "Security" in result


@pytest.mark.asyncio
async def test_classify_text_invalid_json(llm_service, mock_client):
    """classify_text returns error on non-JSON LLM response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="This is not JSON at all"))]
    mock_client.chat.completions.create.return_value = mock_response

    result = await llm_service.classify_text("test text", ["Security"])
    assert "error" in result


@pytest.mark.asyncio
async def test_classify_text_no_json_braces(llm_service, mock_client):
    """classify_text returns error when response has no JSON braces."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="plain text response"))]
    mock_client.chat.completions.create.return_value = mock_response

    result = await llm_service.classify_text("test text", ["Security"])
    assert "error" in result


@pytest.mark.asyncio
async def test_generate_text_rate_limit_failure_after_retries(llm_service, mock_client):
    """generate_text returns None when RateLimitError persists after all retries."""
    mock_client.chat.completions.create.side_effect = RateLimitError(
        "Rate limit exceeded", response=MagicMock(), body={}
    )

    result = await llm_service.generate_text("Prompt", "System")
    assert result is None
    assert llm_service._failures > 0


@pytest.mark.asyncio
async def test_generate_text_generic_exception(llm_service, mock_client):
    """generate_text handles generic exceptions gracefully."""
    mock_client.chat.completions.create.side_effect = ValueError("Unexpected")

    result = await llm_service.generate_text("Prompt", "System")
    assert result is None
    assert llm_service._failures > 0
