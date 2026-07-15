import sys
import types
import pytest
from unittest.mock import AsyncMock

# Ensure google.genai is available as a mock before any test imports
if "google" not in sys.modules:
    _google = types.ModuleType("google")
    _google.genai = types.ModuleType("google.genai")
    _google.genai.Client = AsyncMock
    sys.modules["google"] = _google
    sys.modules["google.genai"] = _google.genai


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
