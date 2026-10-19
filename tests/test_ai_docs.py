"""Contract tests for the OpenRouter-only AI documentation pipeline."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from src.ai.collectors.change_collector import collect_changes
from src.ai.llm.client import ExistingLLMClient, OpenRouterQuotaError, _retry_delay
from src.ai.orchestrator import AIDocOrchestrator
from src.ai.schemas.change import ChangeClassification
from src.ai.schemas.generated_docs import GeneratedDocuments
from tests.factories import make_ai_change


class StrictObject(BaseModel):
    required_value: str


def _completion(text: str) -> MagicMock:
    response = MagicMock()
    response.choices = [SimpleNamespace(message=SimpleNamespace(content=text))]
    response.usage = SimpleNamespace(prompt_tokens=12, completion_tokens=8, total_tokens=20, cost=0)
    return response


def _entry(confidence: float = 0.9) -> dict[str, object]:
    return make_ai_change(confidence)


class FakeLLM:
    model = "google/gemma-4-31b-it:free"

    def __init__(self) -> None:
        self.calls = 0

    def generate(self, prompt: str, schema: type | None = None) -> dict[str, object]:
        self.calls += 1
        if schema is ChangeClassification:
            return {"changes": [_entry()], "review_needed": []}
        if schema is GeneratedDocuments:
            return {
                "release_notes": "Adicionado endpoint para consulta.",
                "changelog_entry": "## [Unreleased]\n\n### Added\n- Novo endpoint de consulta.",
                "leadership_summary": "A mudança amplia os recursos disponíveis.",
                "roadmap_suggestions": "SUGESTÃO — avaliar adoção por outros componentes.",
            }
        raise AssertionError(f"Unexpected schema: {schema}")


def test_client_requires_key_and_free_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        ExistingLLMClient()
    with pytest.raises(ValueError, match=":free"):
        ExistingLLMClient(api_key="test-key", model="paid/model")
    with pytest.raises(ValueError, match="OpenRouter only"):
        ExistingLLMClient(api_key="test-key", provider="gemini")


def test_client_uses_only_openrouter_free_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("AI_DOCS_MODEL", "provider/model:free")
    with patch("src.ai.llm.client.OpenAI") as openai:
        client = ExistingLLMClient()
    assert client.provider == "openrouter"
    assert client.model == "provider/model:free"
    assert openai.call_args.kwargs["base_url"] == "https://openrouter.ai/api/v1"
    assert openai.call_args.kwargs["max_retries"] == 0


def test_client_validates_schema_and_returns_dict() -> None:
    client = object.__new__(ExistingLLMClient)
    client.model = "provider/model:free"
    client.usage = []
    client._sleep = lambda _: None
    client._client = MagicMock()
    client._client.chat.completions.create.return_value = _completion('{"required_value":"ok"}')
    assert client.generate("prompt", StrictObject) == {"required_value": "ok"}


def test_client_retries_invalid_json_with_correction() -> None:
    client = object.__new__(ExistingLLMClient)
    client.model = "provider/model:free"
    client.usage = []
    client._sleep = lambda _: None
    client._client = MagicMock()
    endpoint = client._client.chat.completions.create
    endpoint.side_effect = [
        _completion('{"wrong":"field"}'),
        _completion('{"required_value":"fixed"}'),
    ]
    assert client.generate("prompt", StrictObject) == {"required_value": "fixed"}
    assert endpoint.call_count == 2
    assert "falhou na validação" in endpoint.call_args.kwargs["messages"][1]["content"]


def test_client_aborts_after_three_invalid_responses() -> None:
    client = object.__new__(ExistingLLMClient)
    client.model = "provider/model:free"
    client.usage = []
    client._sleep = lambda _: None
    client._client = MagicMock()
    client._client.chat.completions.create.side_effect = [
        _completion("{}"),
        _completion("{}"),
        _completion("{}"),
    ]
    with pytest.raises(ValueError, match="invalid after 3 attempts"):
        client.generate("prompt", StrictObject)


def test_client_retries_http_errors_and_detects_quota() -> None:
    client = object.__new__(ExistingLLMClient)
    client.model = "provider/model:free"
    client.usage = []
    delays: list[float] = []
    client._sleep = delays.append
    client._client = MagicMock()
    endpoint = client._client.chat.completions.create
    endpoint.side_effect = [RuntimeError("temporary"), _completion("ok")]
    assert client.generate("prompt") == "ok"
    assert delays == [2.0]
    endpoint.side_effect = RuntimeError("daily limit exceeded")
    with pytest.raises(OpenRouterQuotaError, match="refusing paid-provider fallback"):
        client.generate("prompt")


def test_retry_delay_prefers_server_headers() -> None:
    assert _retry_delay("7", None, 1) == 7
    assert _retry_delay(None, "invalid", 2) == 4
    assert _retry_delay("9999", None, 1) == 120


def test_collector_ignores_markdown_and_returns_real_diff(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd: list[str]) -> str:
        if "--verify" in cmd:
            return "abc123\n"
        if cmd[0] == "gh":
            return "[]"
        if any(arg.startswith("--format=%H") for arg in cmd):
            return "abc123\tfeat(api): add endpoint\n"
        if "--name-only" in cmd:
            return "src/api.py\0README.md\0uv.lock\0"
        if "--stat" in cmd:
            return "src/api.py | 4 ++++\nREADME.md | 1 +\n"
        if "src/api.py" in cmd:
            return "diff --git a/src/api.py b/src/api.py\n+def endpoint(): pass\n"
        return ""

    monkeypatch.setattr("src.ai.collectors.change_collector.run_cmd", fake_run)
    result = collect_changes("HEAD~1")
    assert result["conventional_commits"] == ["feat(api): add endpoint"]
    assert result["changed_files"] == ["src/api.py"]
    assert "def endpoint" in result["diff_snippets"][0]


def test_collector_rejects_option_like_ref() -> None:
    with pytest.raises(ValueError, match="Git ref"):
        collect_changes("--help")


def test_noop_does_not_require_api_key_or_write_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "src.ai.orchestrator.collect_changes",
        lambda since_ref: {"commits": [], "merged_prs": []},
    )
    result = asyncio.run(AIDocOrchestrator(since_ref="HEAD~1").run())
    assert result.status == "no-op"
    assert not (tmp_path / "docs").exists()


def test_pipeline_generates_artifacts_and_preserves_changelog(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_SHA", "test-sha")
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [1.0.0]\n\n- Histórico preservado.\n", encoding="utf-8"
    )
    monkeypatch.setattr(
        "src.ai.orchestrator.collect_changes",
        lambda since_ref: {
            "commits": ["feat(api): endpoint"],
            "merged_prs": [],
            "diff_snippets": ["diff input"],
        },
    )
    llm = FakeLLM()
    out_dir = tmp_path / "docs" / "ai-generated"
    result = asyncio.run(AIDocOrchestrator(since_ref="HEAD~1", llm=llm, output_dir=out_dir).run())
    assert result.status == "completed"
    assert llm.calls == 2
    release = (out_dir / "release-notes.md").read_text(encoding="utf-8")
    assert "impacto" in release.lower()
    assert "Notas de Release" in release
    changelog = (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [Unreleased]" in changelog
    assert "Histórico preservado." in changelog
    assert changelog.index("[Unreleased]") < changelog.index("[1.0.0]")
    assert (out_dir / "leadership.md").exists()
    assert (out_dir / "roadmap.md").exists()
    assert list((tmp_path / "docs" / ".ai-logs").glob("run-*.json"))
    assert (tmp_path / "docs" / ".last-processed-ref").exists()


def test_pipeline_fails_without_publishing_invalid_classification(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "src.ai.orchestrator.collect_changes",
        lambda since_ref: {"commits": ["feat(api): endpoint"], "merged_prs": []},
    )

    class BadLLM:
        def generate(self, prompt: str, schema: type | None = None) -> dict[str, object]:
            return {"changes": [{"title": "incomplete"}]}

    result = asyncio.run(AIDocOrchestrator(since_ref="HEAD~1", llm=BadLLM()).run())
    assert result.status == "failed"
    assert not (tmp_path / "CHANGELOG.md").exists()
    failure_audit = next((tmp_path / "docs/.ai-logs").glob("*-failed.json"))
    failure_record = json.loads(failure_audit.read_text(encoding="utf-8"))
    assert failure_record["error"]["type"] == "ValidationError"
    assert "classification" in failure_record["prompts"]


def test_prompts_are_versioned_and_present() -> None:
    prompt_dir = Path(__file__).parents[1] / "src" / "ai" / "prompts"
    for name in (
        "classification.prompt",
        "self_review.prompt",
        "release_notes.prompt",
        "changelog.prompt",
        "leadership.prompt",
        "roadmap.prompt",
    ):
        assert (prompt_dir / name).is_file()
