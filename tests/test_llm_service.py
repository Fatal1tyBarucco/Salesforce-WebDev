"""Tests for the LLM service module."""

from unittest.mock import AsyncMock, patch

import pytest

from src.llm_service import LLMService


@pytest.fixture
def llm_service():
    """Fixture for LLM service instance."""
    with patch("src.llm_service.genai"):
        service = LLMService(api_key="test-key")
        return service


@pytest.mark.asyncio
async def test_generate_text_success(llm_service):
    """Test successful text generation."""
    with patch.object(llm_service, "generate_text", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "Generated text response"
        result = await llm_service.generate_text("Test prompt")
        assert result == "Generated text response"


@pytest.mark.asyncio
async def test_summarize_release_notes(llm_service):
    """Test release notes summarization."""
    with patch.object(llm_service, "summarize_release_notes", new_callable=AsyncMock) as mock_sum:
        mock_sum.return_value = "Summary of release notes"
        result = await llm_service.summarize_release_notes("Raw notes content")
        assert result == "Summary of release notes"


@pytest.mark.asyncio
async def test_enrich_feature(llm_service):
    """Test feature enrichment via LLM."""
    with patch.object(llm_service, "enrich_feature", new_callable=AsyncMock) as mock_enrich:
        mock_enrich.return_value = {"enriched": True, "details": "Enriched feature"}
        result = await llm_service.enrich_feature({"name": "Test Feature"})
        assert result == {"enriched": True, "details": "Enriched feature"}
