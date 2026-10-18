"""Extended unit tests for AI documentation pipeline (free tier / LLMService)."""
from __future__ import annotations
import json
import pytest
from unittest.mock import MagicMock, patch

# Client / LLM
from src.ai.llm.client import ExistingLLMClient

# Collector
from src.ai.collectors.change_collector import collect_changes, IGNORE_GLOBS, run_cmd

# Orchestrator
from src.ai.orchestrator import AIDocOrchestrator

# Schemas
from src.ai.schemas.change import ChangeEntry, ChangeClassification
from src.ai.schemas.change_classifier import validate_and_annotate
from src.ai.schemas.change_reviewer import SelfReviewResponse, _json_extract
from src.ai.schemas.llm_input import RawContext


# ---------------------------------------------------------
# Client (LLMService / ExistingLLMClient)
# ---------------------------------------------------------

def test_existing_llm_client_init_with_provider():
    with patch("src.ai.llm.client.LLMService") as MockSvc:
        mock_inst = MagicMock()
        mock_inst.provider = "opencode"
        mock_inst.model_name = "gemini-3.6-flash"
        MockSvc.return_value = mock_inst
        client = ExistingLLMClient(provider="opencode")
        assert client.provider == "opencode"
        assert client.model == "gemini-3.6-flash"


def test_existing_llm_client_generate_success():
    with patch("src.ai.llm.client.LLMService") as MockSvc:
        mock_inst = MagicMock()
        mock_inst.generate_completion.side_effect = lambda **kwargs: '{"changes":[{"title":"t","description":"d","type":"feature","impact":"high","impact_justification":"j","priority":"P1","affected_components":["c"],"source_refs":["r"],"confidence":0.9}]}'
        MockSvc.return_value = mock_inst
        client = ExistingLLMClient()
        result = client.generate("test prompt")
        assert isinstance(result, dict) or isinstance(result, str)


def test_existing_llm_client_generate_empty_raises():
    with patch("src.ai.llm.client.LLMService"):
        client = ExistingLLMClient()
        with pytest.raises(ValueError):
            client.generate("")
        with pytest.raises(ValueError):
            client.generate("   ")


def test_existing_llm_client_generate_invalid_json_fallback():
    with patch("src.ai.llm.client.LLMService") as MockSvc:
        mock_inst = MagicMock()
        mock_inst.generate_completion.side_effect = lambda **kwargs: "not json"
        MockSvc.return_value = mock_inst
        client = ExistingLLMClient()
        result = client.generate("test", schema=dict)
        assert result == "not json"


# ---------------------------------------------------------
# Collector
# ---------------------------------------------------------

def test_run_cmd_success():
    out = run_cmd(["echo", "hello"])
    assert "hello" in out


def test_run_cmd_failure_graceful():
    out = run_cmd(["false"])
    assert out == ""


def test_ignore_globs_not_empty():
    assert len(IGNORE_GLOBS) > 0
    assert any(".md" in g for g in IGNORE_GLOBS)

def test_collect_changes_returns_dict():
    result = collect_changes()
    assert isinstance(result, dict)
    for key in ["commits", "git_diff_stat", "diff_snippets", "conventional_commits", "merged_prs", "since_ref", "to_ref"]:
        assert key in result


def test_collect_changes_conventional_filter():
    # Just verify conventional parsing doesn't crash
    result = collect_changes()
    assert isinstance(result.get("conventional_commits", []), list)


# ---------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------

@patch("src.ai.orchestrator.collect_changes")
def test_orchestrator_run_no_op(mock_collect):
    mock_collect.return_value = {"commits": [], "git_diff_stat": "", "merged_prs": []}
    orch = AIDocOrchestrator(since_ref="HEAD~1", publish_mode="commit")
    # We test the init/config only; async run would need event loop.
    assert orch.since_ref == "HEAD~1"
    assert orch.publish_mode == "commit"

@patch("src.ai.orchestrator.collect_changes")
def test_orchestrator_build_classify_prompt(mock_collect):
    mock_collect.return_value = {"commits":["feat(x): new"], "git_diff_stat":"", "merged_prs":[]}
    orch = AIDocOrchestrator(since_ref="HEAD")
    prompt = orch._build_classify_prompt(mock_collect.return_value)
    assert "arquiteto" in prompt
    assert "JSON" in prompt


# ---------------------------------------------------------
# Schemas
# ---------------------------------------------------------

def test_change_entry_valid():
    entry = ChangeEntry(
        title="New feature",
        description="Adds a new endpoint for user data.",
        type="feature",
        impact="high",
        impact_justification="Breaks backward compatibility.",
        priority="P0",
        affected_components=["api", "core"],
        source_refs=["commit-123", "pr-456"],
        confidence=0.95,
    )
    assert entry.title == "New feature"
    assert entry.confidence == 0.95

def test_change_classification_low_confidence_review():
    low = ChangeEntry(
        title="Minor",
        description="Small fix.",
        type="bugfix",
        impact="low",
        impact_justification="No major impact.",
        priority="P2",
        affected_components=["core"],
        source_refs=["abc"],
        confidence=0.3,
    )
    cls = ChangeClassification(changes=[low])
    cls.populate_review_needed()
    assert len(cls.review_needed) == 1
    assert len(cls.changes) == 0

def test_change_classifier_validate_and_annotate():
    entry = ChangeEntry(
        title="Fix",
        description="Fixes a bug.",
        type="bugfix",
        impact="medium",
        impact_justification="Fixes crash.",
        priority="P1",
        affected_components=["ui"],
        source_refs=["r"],
        confidence=0.4,
    )
    result = validate_and_annotate(entry)
    assert result.needs_review is True
    assert "revisado" in result.review_note

# ---------------------------------------------------------
# Change Reviewer (self-review feature flag)
# ---------------------------------------------------------

def test_self_review_response_validation():
    sr = SelfReviewResponse(valid=True, inconsistencies=["missing component"], corrected_fields={"type":"feature"}, note="ok")
    assert sr.valid is True

def test_json_extract_valid():
    text = '{"valid": true, "note":"ok"}'
    result = _json_extract(text)
    assert result is not None
    assert result.get("valid") is True

def test_json_extract_with_fences():
    text = '```json\n{"valid": false}\n```'
    result = _json_extract(text)
    assert result is not None
    assert result.get("valid") is False

# ---------------------------------------------------------
# LLM Input Schema
# ---------------------------------------------------------

def test_raw_context_default():
    ctx = RawContext()
    assert ctx.git_commits == []
    assert ctx.diff_snippets == []

# ---------------------------------------------------------
# Prompts (basic presence)
# ---------------------------------------------------------

def test_prompts_files_exist():
    import pathlib
    base = pathlib.Path(__file__).resolve().parents[2] / "src" / "ai" / "prompts"
    for name in ["release_notes.prompt", "changelog.prompt", "leadership.prompt", "roadmap.prompt"]:
        p = base / name
        assert p.exists(), f"Prompt file missing: {p}"
        content = p.read_text(encoding="utf-8")
        assert len(content) > 50
        assert "LLM" not in content or "LLMService" in content or "free" in content.lower()
