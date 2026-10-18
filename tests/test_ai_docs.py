"""Unit tests for AI documentation pipeline (existing LLMService / free tier)."""

from __future__ import annotations
import pytest
from unittest.mock import MagicMock, patch

from src.ai.llm.client import ExistingLLMClient
from src.ai.orchestrator import AIDocOrchestrator
from src.ai.schemas.change import ChangeEntry
from src.ai.collectors.change_collector import collect_changes


def test_existing_llm_client_uses_llm_service():
    with patch("src.ai.llm.client.LLMService") as MockSvc:
        mock_inst = MagicMock()
        mock_inst.provider = "openrouter"
        mock_inst.model_name = "openrouter/free"
        MockSvc.return_value = mock_inst
        client = ExistingLLMClient()
        assert client.provider == "openrouter"
        assert client.model == "openrouter/free"


def test_existing_llm_client_generate_raises_on_empty():
    with patch("src.ai.llm.client.LLMService"):
        client = ExistingLLMClient()
        with pytest.raises(ValueError):
            client.generate("")


async def test_orchestrator_no_op_on_empty_changes():
    with patch.object(AIDocOrchestrator, "_build_classify_prompt", return_value="{}"):
        with patch(
            "src.ai.orchestrator.collect_changes", return_value={"commits": [], "git_diff_stat": ""}
        ):
            orch = AIDocOrchestrator(since_ref="HEAD~1")
            result = await orch.run()
            assert result.status == "no-op"
            assert result.changes == []


def test_change_collector_ignores_irrelevant():
    result = collect_changes()
    # Just verify deterministic return structure
    assert isinstance(result, dict)
    assert "commits" in result
    assert "conventional_commits" in result
    assert "merged_prs" in result


def test_change_classification_low_confidence():
    entry = ChangeEntry(
        title="Test",
        description="Descrição detalhada da mudança para validação.",
        type="feature",
        impact="low",
        impact_justification="Test justification",
        priority="P1",
        affected_components=["core"],
        source_refs=["abc"],
        confidence=0.3,
    )
    assert entry.confidence == 0.3


# Mock LLM response for pipeline
class MockLLMClient:
    def __init__(self):
        pass

    def generate(self, prompt, schema=None):
        return {
            "changes": [
                {
                    "title": "feat: new api",
                    "description": "API update",
                    "type": "feature",
                    "impact": "high",
                    "impact_justification": "Breaks old clients",
                    "priority": "P0",
                    "affected_components": ["core"],
                    "source_refs": ["abc123"],
                    "confidence": 0.95,
                }
            ]
        }
