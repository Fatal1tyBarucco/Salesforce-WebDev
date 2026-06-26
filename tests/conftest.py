import pytest
from unittest.mock import AsyncMock


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
