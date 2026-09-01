import sys
import types
from unittest.mock import AsyncMock, MagicMock

import pytest

# Stub google.genai before any test imports (prevents import hangs)
if "google" not in sys.modules:
    _google = types.ModuleType("google")
    _google.genai = types.ModuleType("google.genai")
    _google.genai.Client = MagicMock
    _google.genai.types = types.ModuleType("google.genai.types")
    _google.genai.types.GenerateContentConfig = MagicMock
    sys.modules["google"] = _google
    sys.modules["google.genai"] = _google.genai
    sys.modules["google.genai.types"] = _google.genai.types

# Stub openai before any test imports (prevents import hangs when patch() is called)
if "openai" not in sys.modules:
    _openai = types.ModuleType("openai")
    _openai.OpenAI = MagicMock
    sys.modules["openai"] = _openai


@pytest.fixture(autouse=True)
def mock_openai_client():
    """Auto-use fixture that provides a mock OpenAI client for all tests.

    Returns None by default so fallback logic in services executes.
    Individual tests can override via patch.object if they need specific LLM responses.

    Skipped gracefully if the openai package is unavailable or hangs during import
    (e.g. in environments where the package can't be loaded).
    """
    import contextlib

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="mocked LLM response"))]
    mock_client.chat.completions.create.return_value = mock_response

    mock_async_client = AsyncMock()
    mock_async_client.chat.completions.create.return_value = mock_response

    import unittest.mock

    patchers: list[unittest.mock._patch] = []
    with contextlib.suppress(Exception):
        patchers.append(unittest.mock.patch("openai.OpenAI", return_value=mock_client))
        patchers.append(unittest.mock.patch("openai.AsyncOpenAI", return_value=mock_async_client))
        for p in patchers:
            p.start()

    try:
        yield mock_client
    finally:
        for p in patchers:
            with contextlib.suppress(Exception):
                p.stop()


@pytest.fixture
def mock_llm_service():
    """Provide a fully mocked LLMService for tests that don't need real LLM calls."""
    mock = AsyncMock()
    mock.generate_text = AsyncMock(return_value="mocked LLM response")
    mock.classify_text = AsyncMock(return_value={"Security": {"applies": True, "confidence": 0.9}})
    return mock
