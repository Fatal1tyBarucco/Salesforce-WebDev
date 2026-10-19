"""Edge-case tests for the AI documentation integration."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from src.ai.collectors import change_collector
from src.ai.llm.client import ExistingLLMClient, OpenRouterQuotaError, _retry_delay
from src.ai.orchestrator import (
    AIDocOrchestrator,
    PipelineResult,
    _as_jsonable,
    _atomic_write_many,
    _detect_language,
    _estimate_tokens,
    _git_head,
    _prepend_changelog,
    _simple_diff,
    _truncate_context,
    main,
)
from src.ai.schemas.change import ChangeClassification
from src.ai.schemas.change_reviewer import SelfReviewResponse, _json_extract, review_classification
from src.ai.schemas.generated_docs import GeneratedDocuments


class FakeHTTPError(RuntimeError):
    status_code: int
    response: SimpleNamespace

    def __init__(self, status_code: int, headers: dict[str, str]) -> None:
        super().__init__("rate limited")
        self.status_code = status_code
        self.response = SimpleNamespace(headers=headers)


class ResultModel(BaseModel):
    value: int


def _raw(text: str, headers: dict[str, str] | None = None) -> MagicMock:
    response = MagicMock()
    response.choices = [SimpleNamespace(message=SimpleNamespace(content=text))]
    response.usage = None
    return response


def _entry(confidence: float = 0.9) -> dict[str, object]:
    return {
        "title": "Feature X",
        "description": "Descrição detalhada suficiente para validar a mudança.",
        "type": "feature",
        "impact": "high",
        "impact_justification": "Impacto relevante descrito com evidência suficiente.",
        "priority": "P1",
        "affected_components": ["core"],
        "source_refs": ["commit-abc"],
        "confidence": confidence,
    }


def _client(*responses: MagicMock) -> ExistingLLMClient:
    client = object.__new__(ExistingLLMClient)
    client.model = "vendor/model:free"
    client.usage = []
    client._sleep = lambda _: None
    client._client = MagicMock()
    client._client.chat.completions.create.side_effect = list(responses)
    return client


def test_free_model_config_defaults_to_openrouter_free(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.ai.config.models import get_openrouter_free_model

    monkeypatch.delenv("AI_DOCS_MODEL", raising=False)
    assert get_openrouter_free_model() == "openrouter/free"


def test_free_model_config_rejects_non_free(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.ai.config.models import get_openrouter_free_model

    monkeypatch.setenv("AI_DOCS_MODEL", "provider/paid")
    with pytest.raises(ValueError, match=":free"):
        get_openrouter_free_model()


def test_client_sends_json_mode_only_for_schema() -> None:
    client = _client(_raw("plain response"), _raw('{"value":2}'))
    assert client.generate("plain") == "plain response"
    assert client.generate("json", ResultModel) == {"value": 2}
    assert client.usage[-1]["cost_usd"] == 0.0
    requests = client._client.chat.completions.create.call_args_list
    assert requests[0].kwargs["response_format"] is None
    assert requests[1].kwargs["response_format"] == {"type": "json_object"}


def test_client_retries_api_error_with_rate_limit_header() -> None:
    client = _client(_raw('{"value":3}'))
    first = RuntimeError("rate limited")
    first.response = SimpleNamespace(headers={"retry-after": "6"})
    client._client.chat.completions.create.side_effect = [first, _raw('{"value":3}')]
    delays: list[float] = []
    client._sleep = delays.append
    assert client.generate("p", ResultModel) == {"value": 3}
    assert delays == [6]


def test_client_empty_response_retries_then_fails() -> None:
    client = _client(_raw(""), _raw(""), _raw(""))
    with pytest.raises(RuntimeError, match="after 3 attempts"):
        client.generate("prompt")


def test_retry_delay_handles_epoch_and_bad_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.ai.llm.client.time.time", lambda: 100)
    assert _retry_delay(None, "110", 1) == 110
    assert _retry_delay("not-a-number", None, 1) == 2
    assert _retry_delay(None, None, 8) == 30


def test_client_rejects_empty_prompt_and_non_model_schema() -> None:
    client = _client(_raw('{"value":4}'))
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        client.generate("  ")
    assert client.generate("prompt", dict) == {"value": 4}


def test_client_retries_non_object_and_fails_after_api_retries() -> None:
    client = _client(_raw("[]"), _raw('{"value":5}'))
    assert client.generate("prompt", dict) == {"value": 5}
    delays: list[float] = []
    client._sleep = delays.append
    client._client.chat.completions.create.side_effect = [
        RuntimeError("temporary"),
        RuntimeError("temporary"),
        RuntimeError("temporary"),
    ]
    with pytest.raises(RuntimeError, match="request failed after 3 attempts"):
        client.generate("prompt")
    assert delays == [2.0, 4.0]


def test_retry_delay_converts_epoch_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.ai.llm.client.time.time", lambda: 1_700_000_000)
    assert _retry_delay(None, "1700000012", 1) == 12


def test_rate_limit_exhaustion_is_not_retried_as_transient(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.ai.llm.client.time.time", lambda: 1_700_000_000)
    client = _client(_raw('{"value":3}'))
    error = FakeHTTPError(429, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1700003600"})
    client._client.chat.completions.create.side_effect = error
    with pytest.raises(OpenRouterQuotaError, match="quota/rate limit exhausted"):
        client.generate("prompt")
    assert client._client.chat.completions.create.call_count == 1


def test_rate_limit_headers_case_insensitive_and_retry_after() -> None:
    client = _client(_raw('{"value":3}'))
    error = RuntimeError("temporary limit")
    error.status_code = 429
    error.response = SimpleNamespace(headers={"Retry-After": "6", "X-RateLimit-Remaining": "2"})
    client._client.chat.completions.create.side_effect = [error, _raw('{"value":3}')]
    delays: list[float] = []
    client._sleep = delays.append
    assert client.generate("prompt", ResultModel) == {"value": 3}
    assert delays == [6]


def test_closed_issue_metadata_is_filtered_and_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    issue = {
        "number": 17,
        "title": "Closed in range",
        "body": "x" * (change_collector.MAX_PR_BODY_CHARS + 20),
        "labels": [{"name": "bug"}],
        "closedAt": "2026-10-19T12:00:00Z",
        "url": "https://github.com/example/repo/issues/17",
    }
    commands: list[list[str]] = []

    def fake_run(cmd: list[str]) -> str:
        commands.append(cmd)
        if cmd[:3] == ["git", "show", "-s"]:
            return "2026-10-18T01:00:00+02:00\n"
        if cmd[:3] == ["gh", "issue", "list"]:
            return json.dumps([issue, {**issue, "number": 18, "closedAt": "2026-10-17T00:00:00Z"}])
        return ""

    monkeypatch.setattr(change_collector, "run_cmd", fake_run)
    results = change_collector._collect_closed_issues("base-ref")
    assert [item["number"] for item in results] == [17]
    assert len(results[0]["body"]) == change_collector.MAX_PR_BODY_CHARS
    assert results[0]["labels"] == [{"name": "bug"}]
    assert "labels" in commands[-1][-1] and "closedAt" in commands[-1][-1]


def test_collector_patterns_and_invalid_pr_payload(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    Path(".github").mkdir()
    Path(".github/ai-docs-ignore").write_text("# comment\nsecret.txt\n", encoding="utf-8")
    patterns = change_collector._ignore_patterns()
    assert change_collector._is_ignored("secret.txt", patterns)
    assert change_collector._is_ignored("README.md", patterns)
    assert not change_collector._is_ignored("src/main.py", patterns)
    monkeypatch.setattr(change_collector, "run_cmd", lambda cmd: "not-json")
    assert change_collector._collect_merged_prs() == []


def test_collector_pr_metadata_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    body = "x" * (change_collector.MAX_PR_BODY_CHARS + 20)
    monkeypatch.setattr(
        change_collector,
        "run_cmd",
        lambda cmd: json.dumps([{"number": 7, "body": body}, None]),
    )
    prs = change_collector._collect_merged_prs()
    assert len(prs) == 1
    assert len(prs[0]["body"]) == change_collector.MAX_PR_BODY_CHARS


def test_collector_invalid_ref_and_empty_command(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError):
        change_collector.collect_changes("")
    monkeypatch.setattr(
        change_collector.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("unavailable")),
    )
    assert change_collector.run_cmd(["git", "status"]) == ""


def test_payload_parser_handles_none_invalid_and_json() -> None:
    assert AIDocOrchestrator._payload_from(None) is None
    assert AIDocOrchestrator._payload_from("invalid") is None
    assert AIDocOrchestrator._payload_from('["x"]') is None
    assert AIDocOrchestrator._payload_from('{"x":1}') == {"x": 1}


def test_changelog_delta_requires_heading_and_preserves_old_history(tmp_path: Path) -> None:
    path = tmp_path / "CHANGELOG.md"
    path.write_text("# Changelog\n\n## [1.0]\nold\n", encoding="utf-8")
    updated = _prepend_changelog(path, "<!-- marker -->", "## [Unreleased]\nnew")
    assert updated.startswith("# Changelog\n\n<!-- marker -->")
    assert updated.index("[Unreleased]") < updated.index("[1.0]")
    with pytest.raises(ValueError, match="Unreleased"):
        _prepend_changelog(path, "<!-- marker -->", "not a heading")


def test_low_confidence_is_retained_for_manual_review() -> None:
    classification = ChangeClassification(changes=[_entry(0.3)])
    classification.populate_review_needed()
    assert not classification.changes
    assert len(classification.review_needed) == 1
    assert classification.review_needed[0].needs_review is True


def test_render_adds_low_confidence_section_and_visuals(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    orchestrator = AIDocOrchestrator(since_ref="HEAD~1", llm=object())  # type: ignore[arg-type]
    classification = ChangeClassification(changes=[_entry()])
    classification.review_needed = [ChangeClassification(changes=[_entry(0.2)]).changes[0]]
    docs = GeneratedDocuments(
        release_notes="Release text",
        changelog_entry="## [Unreleased]\n\n### Added\n- x",
        leadership_summary="Executive text",
        roadmap_suggestions="SUGESTÃO — futuro",
    )
    rendered = orchestrator._render_documents(classification, docs)
    assert "Revisão Necessária" in rendered["release_notes"]
    assert "Distribuição de Impacto" in rendered["release_notes"]
    assert "gerado por IA em" in rendered["leadership_summary"]


class SelfReviewLLM:
    model = "vendor/model:free"

    def __init__(self) -> None:
        self.responses = [
            {"changes": [_entry()], "review_needed": []},
            {
                "valid": False,
                "inconsistencies": ["inconsistent"],
                "corrected_fields": {},
                "note": "review",
            },
            {
                "release_notes": "Release",
                "changelog_entry": "## [Unreleased]\n\n### Changed\n- x",
                "leadership_summary": "Summary",
                "roadmap_suggestions": "Sugestão",
            },
        ]

    def generate(self, prompt: str, schema: type | None = None) -> dict[str, object]:
        return self.responses.pop(0)


def test_self_review_marks_changes_without_dropping_them(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_SHA", "test-sha")
    monkeypatch.setenv("AI_DOCS_SELF_REVIEW", "true")
    monkeypatch.setattr(
        "src.ai.orchestrator.collect_changes",
        lambda since_ref: {"commits": ["feat: x"], "merged_prs": []},
    )
    result = asyncio.run(
        AIDocOrchestrator(
            since_ref="HEAD~1", llm=SelfReviewLLM(), output_dir=tmp_path / "docs" / "generated"
        ).run()  # type: ignore[arg-type]
    )
    assert result.status == "completed"
    assert result.changes[0]["needs_review"] is True
    audit = next((tmp_path / "docs" / ".ai-logs").glob("run-*.json"))
    record = json.loads(audit.read_text(encoding="utf-8"))
    assert record["raw_output"]["self_review"]["valid"] is False
    assert record["model"] == "vendor/model:free"


def test_failed_generation_does_not_write_partial_artifacts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "src.ai.orchestrator.collect_changes",
        lambda since_ref: {"commits": ["feat: x"], "merged_prs": []},
    )

    class FailLLM:
        def generate(self, prompt: str, schema: type | None = None) -> dict[str, object]:
            raise RuntimeError("request failed")

    result = asyncio.run(
        AIDocOrchestrator(since_ref="HEAD~1", llm=FailLLM()).run()  # type: ignore[arg-type]
    )
    assert result.status == "failed"
    assert not Path("CHANGELOG.md").exists()


def test_artifact_write_persists_document_diff_and_ref(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_SHA", "test-sha")
    (tmp_path / "docs/ai-generated").mkdir(parents=True)
    (tmp_path / "docs/ai-generated/release-notes.md").write_text("old", encoding="utf-8")
    class_llm = SimpleNamespace(model="vendor/model:free")
    orchestrator = AIDocOrchestrator(
        since_ref="HEAD~1", llm=class_llm, output_dir=tmp_path / "docs/ai-generated"  # type: ignore[arg-type]
    )
    classification = ChangeClassification(changes=[_entry()])
    rendered = {key: "new" for key in orchestrator.output_paths}
    generated = GeneratedDocuments(
        release_notes="Release",
        changelog_entry="## [Unreleased]",
        leadership_summary="Summary",
        roadmap_suggestions="Suggestion: evaluate",
    )
    orchestrator._write_artifacts(
        rendered, {"prompt": "test"}, {"raw": "{}"}, classification, generated
    )
    audit = next((tmp_path / "docs/.ai-logs").glob("run-*.json"))
    record = json.loads(audit.read_text(encoding="utf-8"))
    assert "documentation_diff" in record
    assert record["validated_documents"]["release_notes"] == "Release"
    assert (tmp_path / "docs/.last-processed-ref").exists()


def test_generated_docs_schema_rejects_missing_fields() -> None:
    with pytest.raises(Exception):
        GeneratedDocuments.model_validate({"release_notes": "missing others"})


def test_review_response_requires_validity() -> None:
    with pytest.raises(Exception):
        SelfReviewResponse.model_validate({"note": "missing valid"})


def test_context_truncates_diffs_before_pr_bodies() -> None:
    context = {
        "conventional_commits": ["feat(api): keep this first"],
        "git_diff_stat": "stat" * 3,
        "diff_snippets": ["diff" * 30],
        "merged_prs": [{"title": "PR", "body": "body" * 30}],
    }
    bounded = _truncate_context(context, max_chars=120)
    assert bounded["conventional_commits"] == context["conventional_commits"]
    assert len(json.dumps(bounded, ensure_ascii=False)) <= 120
    assert len(bounded.get("merged_prs", [])) <= 1
    stat_bounded = _truncate_context({"git_diff_stat": "s" * 200}, max_chars=60)
    assert len(json.dumps(stat_bounded, ensure_ascii=False)) <= 60
    pr_bounded = _truncate_context(
        {"merged_prs": [{"number": 3, "body": "pr body " * 80}]}, max_chars=100
    )
    assert len(json.dumps(pr_bounded, ensure_ascii=False)) <= 100
    assert len(pr_bounded["merged_prs"][0]["body"]) < len("pr body " * 80)


def test_context_truncates_to_configured_token_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_DOCS_MAX_CONTEXT_TOKENS", "35")
    raw = {
        "conventional_commits": ["feat(api): preserve this high-priority change"],
        "git_diff_stat": "stat data " * 100,
        "diff_snippets": ["diff data " * 200],
        "merged_prs": [{"title": "PR details", "body": "body " * 200}],
        "closed_issues": [{"title": "Issue details", "body": "issue " * 100}],
    }
    bounded = _truncate_context(raw)
    serialized = json.dumps(bounded, ensure_ascii=False)
    assert _estimate_tokens(serialized) <= 35
    assert bounded["conventional_commits"] == raw["conventional_commits"]
    assert len(serialized) < len(json.dumps(raw, ensure_ascii=False))


def test_language_detection_defaults_to_portuguese_and_detects_english() -> None:
    assert _detect_language("") == "pt-BR"
    assert _detect_language("The service and the client work with this data.") == "en"
    assert (
        _detect_language("A mudança não altera o contrato e permite que a equipe evolua.")
        == "pt-BR"
    )


def test_atomic_multi_file_write_rolls_back_on_replace_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("old first", encoding="utf-8")
    original_replace = Path.replace
    failed = False

    def fail_second_once(path: Path, target: Path) -> Path:
        nonlocal failed
        if target == second and not failed:
            failed = True
            raise OSError("simulated replace failure")
        return original_replace(path, target)

    monkeypatch.setattr(Path, "replace", fail_second_once)
    with pytest.raises(OSError, match="simulated replace failure"):
        _atomic_write_many({first: "new first", second: "new second"})
    assert first.read_text(encoding="utf-8") == "old first"
    assert not second.exists()


def test_merged_prs_filter_to_commit_range(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        change_collector,
        "run_cmd",
        lambda cmd: json.dumps(
            [
                {"number": 1, "mergeCommit": {"oid": "in-range"}, "body": "included"},
                {"number": 2, "mergeCommit": {"oid": "outside"}, "body": "excluded"},
            ]
        ),
    )
    prs = change_collector._collect_merged_prs({"in-range"})
    assert [item["number"] for item in prs] == [1]


def test_collector_subprocess_failures_return_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        change_collector.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=3, stdout="secret output"),
    )
    assert change_collector.run_cmd(["git", "status"]) == ""

    def timeout(*args, **kwargs):
        raise change_collector.subprocess.TimeoutExpired("git", 30)

    monkeypatch.setattr(change_collector.subprocess, "run", timeout)
    assert change_collector.run_cmd(["git", "status"]) == ""
    monkeypatch.setattr(
        change_collector.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="ok"),
    )
    assert change_collector.run_cmd(["git", "status"]) == "ok"


def test_collector_rejects_unresolvable_ref_and_handles_empty_diff(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(change_collector, "run_cmd", lambda cmd: "" if "--verify" in cmd else "")
    with pytest.raises(ValueError, match="does not resolve"):
        change_collector.collect_changes("missing-ref")

    def no_change(cmd: list[str]) -> str:
        if "--verify" in cmd:
            return "valid-sha"
        if cmd[0] == "gh":
            return "[]"
        if any(arg.startswith("--format=%H") for arg in cmd):
            return "legacy commit subject without a hash field"
        return ""

    monkeypatch.setattr(change_collector, "run_cmd", no_change)
    result = change_collector.collect_changes("HEAD~1")
    assert result["changed_files"] == []
    assert result["commits"] == ["legacy commit subject without a hash field"]
    assert result["git_diff_stat"] == ""
    assert result["merged_prs"] == []


def test_collector_parses_breaking_change_footer(monkeypatch: pytest.MonkeyPatch) -> None:
    body = chr(10) + "BREAKING CHANGE: removes the old field"

    def fake_run(cmd: list[str]) -> str:
        if "--verify" in cmd:
            return "commit-sha"
        if any(arg.startswith("--format=%H") for arg in cmd):
            return (
                "commit-sha" + chr(9) + "refactor(api): reshape response" + chr(9) + body + chr(30)
            )
        if cmd[0] == "gh":
            return "[]"
        return ""

    monkeypatch.setattr(change_collector, "run_cmd", fake_run)
    result = change_collector.collect_changes("HEAD~1")
    assert "BREAKING CHANGE: removes the old field" in result["conventional_commits"][0]
    assert result["commit_details"][0]["body"].startswith("BREAKING CHANGE:")


def test_merged_prs_handles_bad_and_non_list_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(change_collector, "run_cmd", lambda cmd: "not-json")
    assert change_collector._collect_merged_prs() == []
    monkeypatch.setattr(change_collector, "run_cmd", lambda cmd: json.dumps({"number": 1}))
    assert change_collector._collect_merged_prs() == []


def test_self_review_deterministic_validation_and_json_extract() -> None:
    valid = ChangeClassification(changes=[_entry()])
    assert review_classification(valid).valid is True
    invalid = ChangeClassification(changes=[_entry(0.4)])
    assert review_classification(invalid).valid is False
    assert "confiança baixa" in review_classification(invalid).inconsistencies[0]
    missing_components = _entry()
    missing_components["affected_components"] = []
    component_review = review_classification(ChangeClassification(changes=[missing_components]))
    assert any("sem componentes" in item for item in component_review.inconsistencies)
    assert not review_classification(ChangeClassification()).valid
    assert _json_extract('{"valid":true}') == {"valid": True}
    assert _json_extract("```json" + chr(10) + '{"valid":true}' + chr(10) + "```") == {
        "valid": True
    }
    assert _json_extract("not json") is None
    assert _json_extract("[]") is None


def test_changelog_without_standard_title_and_simple_diff(tmp_path: Path) -> None:
    path = tmp_path / "plain.md"
    path.write_text("existing content", encoding="utf-8")
    updated = _prepend_changelog(
        path, "<!-- marker -->", "## [Unreleased]" + chr(10) + chr(10) + "- New"
    )
    assert updated.endswith("existing content")
    assert "<!-- marker -->" in updated
    assert "-old" in _simple_diff("old" + chr(10), "new" + chr(10))
    assert "+new" in _simple_diff("old" + chr(10), "new" + chr(10))


def test_language_specific_render_and_document_prompts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    out = tmp_path / "docs/ai-generated"
    out.mkdir(parents=True)
    (out / "release-notes.md").write_text(
        "The service and the client work with this feature.", encoding="utf-8"
    )
    (out / "leadership.md").write_text("The service and the client work.", encoding="utf-8")
    (out / "roadmap.md").write_text("The team should evaluate this next.", encoding="utf-8")
    Path("CHANGELOG.md").write_text(
        "# Changelog" + chr(10) * 2 + "## [1.0.0]" + chr(10) * 2 + "- Historical fact.",
        encoding="utf-8",
    )
    orchestrator = AIDocOrchestrator(since_ref="HEAD~1", output_dir=out)
    prompt = orchestrator._documents_prompt(ChangeClassification(changes=[_entry()]))
    assert "Idioma obrigatório: en" in prompt
    assert "<existing_document>" in prompt
    assert "The service and the client work with this feature." in prompt
    assert "Historical fact." in prompt
    docs = GeneratedDocuments(
        release_notes="A change is ready.",
        changelog_entry="## [Unreleased]"
        + chr(10)
        + ""
        + chr(10)
        + "### Added"
        + chr(10)
        + "- New feature",
        leadership_summary="The release improves the service.",
        roadmap_suggestions="Consider another integration.",
    )
    rendered = orchestrator._render_documents(ChangeClassification(changes=[_entry()]), docs)
    assert "# Release Notes" in rendered["release_notes"]
    assert "The service and the client work with this feature." in rendered["release_notes"]
    assert "# Executive Summary" in rendered["leadership_summary"]
    assert "# Roadmap Suggestions" in rendered["roadmap_suggestions"]
    assert "Suggestion:" in rendered["roadmap_suggestions"]
    assert "📋 feature" in rendered["release_notes"]
    assert "P1" in rendered["release_notes"]


def test_orchestrator_invalid_mode_and_last_ref(tmp_path: Path, monkeypatch) -> None:
    with pytest.raises(ValueError, match="publish_mode"):
        AIDocOrchestrator(publish_mode="invalid")
    monkeypatch.chdir(tmp_path)
    assert AIDocOrchestrator().since_ref == "HEAD~10"
    Path("docs").mkdir()
    Path("docs/.last-processed-ref").write_text("abc123" + chr(10), encoding="utf-8")
    assert AIDocOrchestrator().since_ref == "abc123"


def test_pipeline_noop_after_empty_classification(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "src.ai.orchestrator.collect_changes",
        lambda since_ref: {"commits": ["chore: no actionable change"], "merged_prs": []},
    )

    class EmptyLLM:
        def generate(self, prompt: str, schema: type | None = None) -> dict[str, object]:
            return {"changes": [], "review_needed": []}

    result = asyncio.run(AIDocOrchestrator(since_ref="HEAD~1", llm=EmptyLLM()).run())
    assert result.status == "no-op"
    assert not Path("CHANGELOG.md").exists()


def test_pipeline_self_review_valid_keeps_changes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_SHA", "valid-sha")
    monkeypatch.setenv("AI_DOCS_SELF_REVIEW", "true")
    monkeypatch.setattr(
        "src.ai.orchestrator.collect_changes",
        lambda since_ref: {"commits": ["feat: safe"], "merged_prs": []},
    )

    class GoodReviewLLM:
        model = "vendor/model:free"

        def __init__(self) -> None:
            self.usage = [{"total_tokens": 25}]
            self.results = [
                {"changes": [_entry()], "review_needed": []},
                {"valid": True, "inconsistencies": [], "corrected_fields": {}, "note": "ok"},
                {
                    "release_notes": "Release",
                    "changelog_entry": (
                        "## [Unreleased]" + chr(10) * 2 + "### Added" + chr(10) + "- Safe"
                    ),
                    "leadership_summary": "Summary",
                    "roadmap_suggestions": "Sugestão: revisar",
                },
            ]

        def generate(self, prompt: str, schema: type | None = None) -> dict[str, object]:
            return self.results.pop(0)

    result = asyncio.run(AIDocOrchestrator(since_ref="HEAD~1", llm=GoodReviewLLM()).run())
    assert result.status == "completed"
    assert result.total_tokens == 25
    assert not result.changes[0]["needs_review"]


def test_atomic_write_staging_error_leaves_targets_untouched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.write_text("before", encoding="utf-8")
    original_write_text = Path.write_text

    def fail_second(path: Path, data: str, *args, **kwargs):
        if path.name.startswith(".second."):
            raise OSError("staging failed")
        return original_write_text(path, data, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_second)
    with pytest.raises(OSError, match="staging failed"):
        _atomic_write_many({first: "after", second: "new"})
    assert first.read_text(encoding="utf-8") == "before"
    assert not second.exists()
    assert not list(tmp_path.glob("*.tmp"))


def test_atomic_write_rolls_back_new_file_after_later_replace_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    second.write_text("old second", encoding="utf-8")
    original_replace = Path.replace

    def fail_second(source: Path, target: Path) -> Path:
        if target == second:
            raise OSError("replace failed")
        return original_replace(source, target)

    monkeypatch.setattr(Path, "replace", fail_second)
    with pytest.raises(OSError, match="replace failed"):
        _atomic_write_many({first: "new first", second: "new second"})
    assert not first.exists()
    assert second.read_text(encoding="utf-8") == "old second"


def test_git_head_and_jsonable_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.ai.orchestrator.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(stdout="abc123" + chr(10)),
    )
    assert _git_head() == "abc123"
    model = ChangeClassification(changes=[_entry()])
    assert _as_jsonable(model)["changes"][0]["title"] == "Feature X"
    assert _as_jsonable("plain") == "plain"


def test_cli_exit_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["ai-docs", "--since-ref", "HEAD~1", "--publish-mode", "pr"])

    async def failed_run(self):
        return PipelineResult([], [], ["bad"], status="failed")

    async def successful_run(self):
        return PipelineResult([], [], [])

    monkeypatch.setattr(AIDocOrchestrator, "run", failed_run)
    assert main() == 1
    monkeypatch.setattr(AIDocOrchestrator, "run", successful_run)
    assert main() == 0
