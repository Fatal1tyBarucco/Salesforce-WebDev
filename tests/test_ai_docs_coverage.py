"""Extended unit tests for AI documentation pipeline (free tier / LLMService)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

# Collector
from src.ai.collectors.change_collector import IGNORE_GLOBS, collect_changes, run_cmd

# Client / LLM
from src.ai.llm.client import ExistingLLMClient

# Orchestrator
from src.ai.orchestrator import AIDocOrchestrator

# Schemas
from src.ai.schemas.change import ChangeClassification, ChangeEntry
from src.ai.schemas.change_classifier import validate_and_annotate
from src.ai.schemas.change_reviewer import SelfReviewResponse, _json_extract, review_classification
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
        mock_inst.generate_completion.side_effect = (
            lambda **kwargs: '{"changes":[{"title":"t","description":"d","type":"feature","impact":"high","impact_justification":"j","priority":"P1","affected_components":["c"],"source_refs":["r"],"confidence":0.9}]}'
        )
        MockSvc.return_value = mock_inst
        client = ExistingLLMClient()
        result = client.generate("test prompt")
        assert isinstance(result, (dict, str))


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
    for key in [
        "commits",
        "git_diff_stat",
        "diff_snippets",
        "conventional_commits",
        "merged_prs",
        "since_ref",
        "to_ref",
    ]:
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
    mock_collect.return_value = {"commits": ["feat(x): new"], "git_diff_stat": "", "merged_prs": []}
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
    sr = SelfReviewResponse(
        valid=True,
        inconsistencies=["missing component"],
        corrected_fields={"type": "feature"},
        note="ok",
    )
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
    import os
    import pathlib

    base = pathlib.Path(__file__).resolve().parents[2] / "src" / "ai" / "prompts"
    # Fallback: resolve via cwd if resolve produces wrong path
    if not base.exists():
        cwd_path = pathlib.Path(os.getcwd()) / "src" / "ai" / "prompts"
        if cwd_path.exists():
            base = cwd_path
    for name in ["release_notes.prompt", "changelog.prompt", "leadership.prompt", "roadmap.prompt"]:
        p = base / name
        assert p.exists(), f"Prompt file missing: {p}"
        content = p.read_text(encoding="utf-8")
        assert len(content) > 50
        assert (
            ("LLMService" in content)
            or ("free" in content.lower())
            or ("prompt" in content.lower())
        )


# ---------------------------------------------------------
# Extended coverage: client.generate paths
# ---------------------------------------------------------


def test_generate_with_dict_schema_parses_json():
    with patch("src.ai.llm.client.LLMService") as MockSvc:
        mock_inst = MagicMock()
        mock_inst.generate_completion.return_value = '{"changes": []}'
        MockSvc.return_value = mock_inst
        client = ExistingLLMClient()
        result = client.generate("p", schema=dict)
        assert result == {"changes": []}


def test_generate_strips_code_fences_before_parse():
    with patch("src.ai.llm.client.LLMService") as MockSvc:
        mock_inst = MagicMock()
        mock_inst.generate_completion.return_value = '```json\n{"a": 1}\n```'
        MockSvc.return_value = mock_inst
        client = ExistingLLMClient()
        assert client.generate("p", schema=dict) == {"a": 1}


def test_generate_with_model_validate_schema_returns_raw_dict():
    with patch("src.ai.llm.client.LLMService") as MockSvc:
        mock_inst = MagicMock()
        mock_inst.generate_completion.return_value = '{"valid": true, "note": "ok"}'
        MockSvc.return_value = mock_inst
        client = ExistingLLMClient()
        # model_validate returns a BaseModel (non-dict) -> falls back to raw data dict
        result = client.generate("p", schema=SelfReviewResponse)
        assert result == {"valid": True, "note": "ok"}


def test_generate_non_dict_json_returns_raw_string():
    with patch("src.ai.llm.client.LLMService") as MockSvc:
        mock_inst = MagicMock()
        mock_inst.generate_completion.return_value = "[1, 2, 3]"
        MockSvc.return_value = mock_inst
        client = ExistingLLMClient()
        assert client.generate("p", schema=dict) == "[1, 2, 3]"


def test_generate_propagates_service_error():
    with patch("src.ai.llm.client.LLMService") as MockSvc:
        mock_inst = MagicMock()
        mock_inst.generate_completion.side_effect = RuntimeError("provider down")
        MockSvc.return_value = mock_inst
        client = ExistingLLMClient()
        with pytest.raises(RuntimeError):
            client.generate("p")


# ---------------------------------------------------------
# Extended coverage: collector edge cases
# ---------------------------------------------------------


def test_run_cmd_exception_returns_empty(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("subprocess exploded")

    monkeypatch.setattr("src.ai.collectors.change_collector.subprocess.run", boom)
    assert run_cmd(["git", "status"]) == ""


def test_collect_changes_empty_pr_output(monkeypatch):
    def fake_run_cmd(cmd):
        if cmd[0] == "gh":
            return ""
        if "diff" in cmd:
            return ""
        return ""

    monkeypatch.setattr("src.ai.collectors.change_collector.run_cmd", fake_run_cmd)
    result = collect_changes(since_ref="HEAD~1")
    assert result["merged_prs"] == []
    assert result["conventional_commits"] == []


def test_collect_changes_invalid_pr_json_and_filters(monkeypatch):
    def fake_run_cmd(cmd):
        if cmd[0] == "gh":
            return "not-json"
        if "diff" in cmd:
            return "src/main.py | 10 ++\ndocs/readme.md | 2 +\nuv.lock | 5 +++"
        return "feat(x): add feature\nchore(y): other\n"

    monkeypatch.setattr("src.ai.collectors.change_collector.run_cmd", fake_run_cmd)
    result = collect_changes(since_ref="HEAD~2")
    assert result["merged_prs"] == []
    assert len(result["conventional_commits"]) == 2
    assert any("main.py" in s for s in result["diff_snippets"])
    assert all(".md" not in s and "uv.lock" not in s for s in result["diff_snippets"])


def test_collect_changes_valid_pr_json(monkeypatch):
    def fake_run_cmd(cmd):
        if cmd[0] == "gh":
            return '[{"title": "t", "body": "b", "labels": [], "number": 7}]'
        return ""

    monkeypatch.setattr("src.ai.collectors.change_collector.run_cmd", fake_run_cmd)
    result = collect_changes(since_ref="HEAD~1")
    assert result["merged_prs"][0]["number"] == 7


# ---------------------------------------------------------
# Extended coverage: orchestrator (run / payload / render)
# ---------------------------------------------------------


def test_last_ref_reads_file_and_fallback(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / ".last-processed-ref").write_text("abc123\n", encoding="utf-8")
    orch = AIDocOrchestrator()
    assert orch._last_ref() == "abc123"

    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.chdir(empty)
    orch2 = AIDocOrchestrator()
    assert orch2._last_ref() == "HEAD~10"


def test_payload_from_variants():
    assert AIDocOrchestrator._payload_from({"a": 1}) == {"a": 1}
    assert AIDocOrchestrator._payload_from('{"a": 1}') == {"a": 1}
    assert AIDocOrchestrator._payload_from("not json") is None
    assert AIDocOrchestrator._payload_from("[1, 2]") is None


def test_render_documents_error_and_empty_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    orch = AIDocOrchestrator(since_ref="HEAD~1")
    assert orch._render_documents("not json at all")[0].startswith("<!-- erro")
    assert orch._render_documents('["list", "not", "dict"]')[0].startswith("<!-- erro")
    assert orch._render_documents({"changes": []}) == []


def test_render_documents_with_changes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    orch = AIDocOrchestrator(since_ref="HEAD~1")
    docs = orch._render_documents({"changes": [{"impact": "high", "name": "X"}]})
    assert len(docs) == 2
    assert "X" in docs[0]


def test_orchestrator_run_completed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docs").mkdir()
    payload = (
        '{"changes": [{"impact": "high", "name": "API", "description": "d",'
        ' "audience": "devs"}]}'
    )
    with (
        patch("src.ai.orchestrator.collect_changes") as mock_collect,
        patch.object(ExistingLLMClient, "generate", return_value=payload),
    ):
        mock_collect.return_value = {"commits": ["feat(x): new"]}
        orch = AIDocOrchestrator(since_ref="HEAD~1")
        import asyncio

        result = asyncio.run(orch.run())
    assert result.status == "completed"
    assert len(result.changes) == 1
    assert (tmp_path / "docs" / ".last-processed-ref").exists()


def test_orchestrator_run_completed_with_dict_payload(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docs").mkdir()
    with (
        patch("src.ai.orchestrator.collect_changes") as mock_collect,
        patch.object(
            ExistingLLMClient,
            "generate",
            return_value={"changes": [{"impact": "low", "name": "Y"}]},
        ),
    ):
        mock_collect.return_value = {"commits": ["fix(z): bug"]}
        orch = AIDocOrchestrator(since_ref="HEAD~1")
        import asyncio

        result = asyncio.run(orch.run())
    assert result.status == "completed"
    assert len(result.changes) == 1


def test_orchestrator_run_failure_path(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with patch("src.ai.orchestrator.collect_changes", side_effect=RuntimeError("collector boom")):
        orch = AIDocOrchestrator(since_ref="HEAD~1")
        import asyncio

        result = asyncio.run(orch.run())
    assert result.status == "failed"
    assert "collector boom" in result.errors[0]


# ---------------------------------------------------------
# Extended coverage: change_reviewer + classifier branches
# ---------------------------------------------------------


def _make_entry(**overrides):
    base = {
        "title": "Feature X",
        "description": "Descrição longa o suficiente para o schema.",
        "type": "feature",
        "impact": "high",
        "impact_justification": "Justificativa longa o suficiente aqui.",
        "priority": "P1",
        "affected_components": ["core"],
        "source_refs": ["abc"],
        "confidence": 0.9,
    }
    base.update(overrides)
    return ChangeEntry(**base)


def test_review_classification_valid():
    cls = ChangeClassification(changes=[_make_entry()])
    result = review_classification(cls)
    assert result.valid is True
    assert result.inconsistencies == []


def test_review_classification_flags_low_confidence_and_missing_components():
    cls = ChangeClassification(changes=[_make_entry(affected_components=[], confidence=0.4)])
    result = review_classification(cls)
    assert result.valid is False
    assert any("confiança baixa" in i for i in result.inconsistencies)
    assert any("componentes" in i for i in result.inconsistencies)


def test_review_classification_empty_classification():
    result = review_classification(ChangeClassification())
    assert result.valid is False
    assert any("vazia" in i for i in result.inconsistencies)


def test_json_extract_non_dict_returns_none():
    assert _json_extract("[1, 2, 3]") is None
    assert _json_extract('"just a string"') is None


def test_validate_and_annotate_high_confidence_unchanged():
    entry = _make_entry(confidence=0.9)
    result = validate_and_annotate(entry)
    assert result.needs_review is False
    assert result.review_note == ""
