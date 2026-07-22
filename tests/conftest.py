import sys
import types
import pytest
from unittest.mock import AsyncMock, MagicMock

# Ensure google.genai is available as a mock before any test imports
if "google" not in sys.modules:
    _google = types.ModuleType("google")
    _google.genai = types.ModuleType("google.genai")
    _google.genai.Client = AsyncMock
    _google.genai.types = types.ModuleType("google.genai.types")
    _google.genai.types.GenerateContentConfig = MagicMock
    sys.modules["google"] = _google
    sys.modules["google.genai"] = _google.genai
    sys.modules["google.genai.types"] = _google.genai.types


# Prevent LLMService from raising ValueError when no API keys are set
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key-placeholder")


@pytest.fixture(autouse=True)
def mock_openai_client():
    """Auto-use fixture that provides a mock OpenAI client for all tests.

    Returns None by default so fallback logic in services executes.
    Individual tests can override via patch.object if they need specific LLM responses.
    """
    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = None

    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "openai.AsyncOpenAI", return_value=mock_client
    ):
        yield mock_client


@pytest.fixture
def mock_llm_service():
    """Provide a fully mocked LLMService for tests that don't need real LLM calls."""
    mock = AsyncMock()
    mock.generate_text = AsyncMock(return_value="mocked LLM response")
    mock.classify_text = AsyncMock(return_value={"Security": {"applies": True, "confidence": 0.9}})
    return mock
