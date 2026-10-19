"""Contract tests for the OpenRouter-only AI documentation pipeline."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from src.ai.collectors.change_collector import collect_changes
from src.ai.llm.client import (
    MAX_DIAGNOSTIC_CHARS,
    ExistingLLMClient,
    OpenRouterQuotaError,
    _provider_error,
    _retry_delay,
    _retry_delay_with_source,
    describe_exception,
    sanitize_diagnostic,
)
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


def _completion_with(
    text: str | None,
    finish_reason: str | None = None,
    *,
    refusal: str | None = None,
    error: object | None = None,
    choices: list[object] | None = None,
) -> MagicMock:
    """Build an HTTP-200 completion with diagnostic fields the client must surface."""
    if choices is None:
        message = SimpleNamespace(content=text, refusal=refusal)
        choices = [SimpleNamespace(message=message, finish_reason=finish_reason)]
    response = MagicMock()
    response.choices = choices
    response.usage = None
    if error is not None:
        response.error = error
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


def test_client_uses_openrouter_free_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("AI_DOCS_MODEL", "openrouter/free")
    with patch("src.ai.llm.client.OpenAI") as openai:
        client = ExistingLLMClient()
    assert client.provider == "openrouter"
    assert client.model == "openrouter/free"
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
    with pytest.raises(ValueError) as excinfo:
        client.generate("prompt", StrictObject)
    assert "invalid after 3 attempts" in str(excinfo.value)
    assert "phase=output-validation" in str(excinfo.value)
    assert "error=ValidationError" in str(excinfo.value)


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


def test_retry_delay_reports_delay_source() -> None:
    assert _retry_delay_with_source("7", None, 1) == (7.0, "retry-after")
    assert _retry_delay_with_source(None, "9", 1) == (9.0, "x-ratelimit-reset")
    assert _retry_delay_with_source("soon", None, 2) == (4.0, "exponential-backoff")


def _diagnostic_client(*effects: object) -> ExistingLLMClient:
    client = object.__new__(ExistingLLMClient)
    client.model = "provider/model:free"
    client.usage = []
    client._sleep = lambda _: None
    client._client = MagicMock()
    client._client.chat.completions.create.side_effect = list(effects)
    return client


def test_client_final_transport_failure_reports_root_cause(
    caplog: pytest.LogCaptureFixture,
) -> None:
    transport_error = ConnectionError("connection reset by peer")
    client = _diagnostic_client(transport_error, transport_error, transport_error)
    with caplog.at_level(logging.DEBUG, logger="src.ai.llm.client"):
        with pytest.raises(RuntimeError) as excinfo:
            client.generate("prompt")
    message = str(excinfo.value)
    assert "OpenRouter request failed after 3 attempts" in message
    assert "phase=request" in message
    assert "error=ConnectionError" in message
    assert "connection reset by peer" in message
    assert excinfo.value.__cause__ is transport_error
    logged = [record.getMessage() for record in caplog.records]
    assert any(
        "attempt 1/3" in entry and "delay_source=exponential-backoff" in entry for entry in logged
    )
    assert any("attempt 3/3" in entry and "giving up" in entry for entry in logged)


def test_client_final_http_failure_reports_status_and_provider_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class HTTPStatusError(RuntimeError):
        def __init__(self, status_code: int, payload: object, headers: dict[str, str]) -> None:
            super().__init__(f"HTTP {status_code} returned by provider")
            self.status_code = status_code
            self.response = SimpleNamespace(headers=headers, json=lambda: payload)

    failure = HTTPStatusError(
        503,
        {
            "error": {
                "code": 503,
                "message": "Provider temporarily unavailable",
                "metadata": {"error_type": "provider_overloaded"},
            }
        },
        {"retry-after": "5"},
    )
    client = _diagnostic_client(failure, failure, failure)
    delays: list[float] = []
    client._sleep = delays.append
    with caplog.at_level(logging.DEBUG, logger="src.ai.llm.client"):
        with pytest.raises(RuntimeError) as excinfo:
            client.generate("prompt")
    message = str(excinfo.value)
    assert "phase=request" in message
    assert "error=HTTPStatusError" in message
    assert "status=503" in message
    assert "provider_error=503 | Provider temporarily unavailable" in message
    assert "provider_overloaded" in message
    assert delays == [5.0, 5.0]
    logged = " ".join(record.getMessage() for record in caplog.records)
    assert "delay_source=retry-after" in logged
    assert "attempt 3/3" in logged


def test_client_failure_diagnostics_redact_credentials(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-super-secret-key")
    failure = RuntimeError(
        "401 unauthorized: key sk-or-v1-super-secret-key via Bearer abc123.token"
    )
    client = _diagnostic_client(failure, failure, failure)
    with caplog.at_level(logging.DEBUG, logger="src.ai.llm.client"):
        with pytest.raises(RuntimeError) as excinfo:
            client.generate("prompt")
    message = str(excinfo.value)
    logged = " ".join(record.getMessage() for record in caplog.records)
    assert "sk-or-v1-super-secret-key" not in message
    assert "sk-or-v1-super-secret-key" not in logged
    assert "abc123.token" not in logged
    assert "Bearer [REDACTED]" in message
    assert "[REDACTED]" in logged


def test_client_empty_content_diagnostics_report_finish_reason() -> None:
    client = _diagnostic_client(
        _completion_with(None, "stop"),
        _completion_with("   ", "stop"),
        _completion_with(None, "stop"),
    )
    with pytest.raises(RuntimeError) as excinfo:
        client.generate("prompt")
    message = str(excinfo.value)
    assert "phase=empty-completion" in message
    assert "empty completion" in message
    assert "choices=1" in message
    assert "finish_reason=stop" in message
    requests = client._client.chat.completions.create.call_args_list
    assert len(requests) == 3
    assert "veio vazia" in requests[1].kwargs["messages"][1]["content"]
    assert "veio vazia" in requests[2].kwargs["messages"][1]["content"]


def test_client_missing_choices_reports_empty_completion() -> None:
    client = _diagnostic_client(
        _completion_with(None, choices=[]),
        _completion_with(None, choices=[]),
        _completion_with(None, choices=[]),
    )
    with pytest.raises(RuntimeError) as excinfo:
        client.generate("prompt")
    message = str(excinfo.value)
    assert "phase=empty-completion" in message
    assert "no choices" in message
    assert "choices=0" in message


def test_client_empty_completion_drops_json_mode_and_accepts_fenced_json() -> None:
    fenced = '```json\n{"required_value":"fenced"}\n```'
    client = _diagnostic_client(
        _completion_with(None, "stop"),
        _completion_with(fenced, "stop"),
    )
    assert client.generate("prompt", StrictObject) == {"required_value": "fenced"}
    requests = client._client.chat.completions.create.call_args_list
    assert requests[0].kwargs["response_format"] == {"type": "json_object"}
    assert requests[1].kwargs["response_format"] is None
    assert "veio vazia" in requests[1].kwargs["messages"][1]["content"]


def test_client_invalid_json_diagnoses_preview_and_finish_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-leaked-preview-key")
    text = "Desculpe, não posso gerar o JSON. sk-or-v1-leaked-preview-key"
    client = _diagnostic_client(
        _completion_with(text, "stop"),
        _completion_with(text, "stop"),
        _completion_with(text, "stop"),
    )
    with pytest.raises(ValueError) as excinfo:
        client.generate("prompt", StrictObject)
    message = str(excinfo.value)
    assert "invalid after 3 attempts" in message
    assert "phase=output-validation" in message
    assert "issue=invalid-json" in message
    assert "finish_reason=stop" in message
    assert "output=Desculpe" in message
    assert "sk-or-v1-leaked-preview-key" not in message
    assert "[REDACTED]" in message


def test_client_truncated_output_retries_with_concise_guidance(
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = _diagnostic_client(
        _completion_with('{"required_value": "trunca', "length"),
        _completion_with('{"required_value":"ok"}', "stop"),
    )
    with caplog.at_level(logging.WARNING, logger="src.ai.llm.client"):
        assert client.generate("prompt", StrictObject) == {"required_value": "ok"}
    logged = " ".join(record.getMessage() for record in caplog.records)
    assert "issue=truncated-output" in logged
    requests = client._client.chat.completions.create.call_args_list
    assert "truncada" in requests[1].kwargs["messages"][1]["content"]


def test_client_empty_length_completion_escalates_max_tokens(
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = _diagnostic_client(
        _completion_with(None, "length"),
        _completion_with('{"required_value":"ok"}', "stop"),
    )
    with caplog.at_level(logging.INFO, logger="src.ai.llm.client"):
        assert client.generate("prompt", StrictObject) == {"required_value": "ok"}
    requests = client._client.chat.completions.create.call_args_list
    assert requests[0].kwargs["max_tokens"] == 3000
    assert requests[1].kwargs["max_tokens"] == 6000
    logged = " ".join(record.getMessage() for record in caplog.records)
    assert "raising max_tokens to 6000" in logged


def test_client_truncated_output_escalates_max_tokens() -> None:
    client = _diagnostic_client(
        _completion_with('{"required_value": "trunca', "length"),
        _completion_with('{"required_value":"ok"}', "stop"),
    )
    assert client.generate("prompt", StrictObject) == {"required_value": "ok"}
    requests = client._client.chat.completions.create.call_args_list
    assert requests[0].kwargs["max_tokens"] == 3000
    assert requests[1].kwargs["max_tokens"] == 6000


def test_client_output_budget_env_override_and_cap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_DOCS_MAX_OUTPUT_TOKENS", "500")
    monkeypatch.setenv("AI_DOCS_MAX_OUTPUT_TOKENS_LIMIT", "1000")
    client = _diagnostic_client(
        _completion_with(None, "length"),
        _completion_with(None, "length"),
        _completion_with('{"required_value":"capped"}', "stop"),
    )
    assert client.generate("prompt", StrictObject) == {"required_value": "capped"}
    budgets = [
        call.kwargs["max_tokens"] for call in client._client.chat.completions.create.call_args_list
    ]
    assert budgets == [500, 1000, 1000]


def test_client_output_budget_invalid_env_falls_back_to_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_DOCS_MAX_OUTPUT_TOKENS", "not-a-number")
    monkeypatch.setenv("AI_DOCS_MAX_OUTPUT_TOKENS_LIMIT", "0")
    client = _diagnostic_client(_completion('{"required_value":"ok"}'))
    assert client.generate("prompt", StrictObject) == {"required_value": "ok"}
    assert client._client.chat.completions.create.call_args.kwargs["max_tokens"] == 3000


def test_client_provider_refusal_output_is_diagnosed() -> None:
    blocked = _completion_with("resposta bloqueada pelo provedor", "content_filter")
    client = _diagnostic_client(blocked, blocked, blocked)
    with pytest.raises(ValueError) as excinfo:
        client.generate("prompt", StrictObject)
    message = str(excinfo.value)
    assert "invalid after 3 attempts" in message
    assert "issue=provider-refusal" in message
    assert "finish_reason=content_filter" in message


def test_client_empty_completion_surfaces_refusal_text() -> None:
    refused = _completion_with(None, "stop", refusal="I cannot assist with that request.")
    client = _diagnostic_client(refused, refused, refused)
    with pytest.raises(RuntimeError) as excinfo:
        client.generate("prompt")
    message = str(excinfo.value)
    assert "phase=empty-completion" in message
    assert "refusal=I cannot assist with that request." in message


def test_client_embedded_provider_error_is_surfaced() -> None:
    error_payload = {
        "code": 402,
        "message": "Quota temporarily exhausted",
        "metadata": {"error_type": "rate_limit"},
    }
    failing = _completion_with(None, "stop", error=error_payload)
    client = _diagnostic_client(failing, failing, failing)
    with pytest.raises(RuntimeError) as excinfo:
        client.generate("prompt")
    message = str(excinfo.value)
    assert "phase=empty-completion" in message
    assert "error=402 | Quota temporarily exhausted" in message
    assert "rate_limit" in message


def test_pipeline_empty_completion_failure_writes_diagnostic_audit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "src.ai.orchestrator.collect_changes",
        lambda since_ref: {"commits": ["feat: x"], "merged_prs": []},
    )
    client = _diagnostic_client(
        _completion_with(None, "stop"),
        _completion_with(None, "stop"),
        _completion_with(None, "stop"),
    )
    result = asyncio.run(AIDocOrchestrator(since_ref="HEAD~1", llm=client).run())
    assert result.status == "failed"
    assert "empty completion" in result.errors[0]
    failure = next((tmp_path / "docs/.ai-logs").glob("*-failed.json"))
    record = json.loads(failure.read_text(encoding="utf-8"))
    chain = record["error"]["chain"]
    assert "phase=empty-completion" in chain[0]
    assert "empty completion" in chain[0]
    assert chain[1].startswith("error=ValueError")
    assert "finish_reason=stop" in chain[1]


def test_diagnostic_helpers_bound_and_describe_odd_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-abcdef123456")
    assert sanitize_diagnostic("bad key sk-or-abcdef123456") == "bad key [REDACTED]"
    long_detail = "x" * (MAX_DIAGNOSTIC_CHARS + 50)
    sanitized = sanitize_diagnostic(long_detail)
    assert len(sanitized) == MAX_DIAGNOSTIC_CHARS
    assert sanitized.endswith("…")
    assert len(sanitize_diagnostic(long_detail, limit=None)) == len(long_detail)
    assert describe_exception(ValueError()) == "error=ValueError"

    assert _provider_error(RuntimeError("plain failure")) is None

    without_body = RuntimeError("failure without body")
    without_body.response = SimpleNamespace(headers={})
    assert _provider_error(without_body) is None

    broken_body = RuntimeError("failure with unreadable body")

    def boom() -> object:
        raise ValueError("no body")

    broken_body.response = SimpleNamespace(headers={}, json=boom)
    assert _provider_error(broken_body) is None

    listed_body = RuntimeError("list body")
    listed_body.response = SimpleNamespace(headers={}, json=lambda: ["body"])
    assert _provider_error(listed_body) is None

    empty_body = RuntimeError("empty error body")
    empty_body.response = SimpleNamespace(headers={}, json=lambda: {"error": {}})
    assert _provider_error(empty_body) is None

    missing_body = RuntimeError("missing error body")
    missing_body.response = SimpleNamespace(headers={}, json=lambda: {"detail": "bad request"})
    assert _provider_error(missing_body) is None

    quoted_body = RuntimeError("string error body")
    quoted_body.response = SimpleNamespace(headers={}, json=lambda: {"error": "quota hit"})
    assert _provider_error(quoted_body) == "quota hit"


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


def test_pipeline_failure_logs_and_audits_exception_cause_chain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "src.ai.orchestrator.collect_changes",
        lambda since_ref: {"commits": ["feat: x"], "merged_prs": []},
    )
    root = OSError("upstream connection reset")
    root.status_code = 502

    class RootCauseLLM:
        model = "vendor/model:free"

        def generate(self, prompt: str, schema: type | None = None) -> dict[str, object]:
            raise RuntimeError("documentation generation failed") from root

    with caplog.at_level(logging.ERROR, logger="src.ai.orchestrator"):
        result = asyncio.run(AIDocOrchestrator(since_ref="HEAD~1", llm=RootCauseLLM()).run())
    assert result.status == "failed"
    logged = " ".join(record.getMessage() for record in caplog.records)
    assert "AI-doc pipeline failed" in logged
    assert "error=RuntimeError, detail=documentation generation failed" in logged
    assert "error=OSError, status=502, detail=upstream connection reset" in logged
    failure_audit = next((tmp_path / "docs/.ai-logs").glob("*-failed.json"))
    record = json.loads(failure_audit.read_text(encoding="utf-8"))
    assert record["error"]["type"] == "RuntimeError"
    assert record["error"]["message"] == "documentation generation failed"
    assert record["error"]["chain"][0].startswith("error=RuntimeError")
    assert record["error"]["chain"][1] == (
        "error=OSError, status=502, detail=upstream connection reset"
    )


def test_pipeline_collect_failure_still_writes_failure_audit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    def boom(since_ref: str) -> dict[str, object]:
        raise RuntimeError("collector exploded")

    monkeypatch.setattr("src.ai.orchestrator.collect_changes", boom)
    result = asyncio.run(AIDocOrchestrator(since_ref="HEAD~1").run())
    assert result.status == "failed"
    assert "collector exploded" in result.errors[0]
    failure = next((tmp_path / "docs/.ai-logs").glob("*-failed.json"))
    record = json.loads(failure.read_text(encoding="utf-8"))
    assert record["error"]["type"] == "RuntimeError"
    assert record["context_budget_tokens"] == 12000


def test_pipeline_warns_when_prompt_tokens_exceed_context_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AI_DOCS_MAX_CONTEXT_TOKENS", "12000")
    monkeypatch.setattr(
        "src.ai.orchestrator.collect_changes",
        lambda since_ref: {"commits": ["feat: x"], "merged_prs": []},
    )

    class UsageLLM(FakeLLM):
        def __init__(self) -> None:
            super().__init__()
            self.usage = [
                {
                    "prompt_tokens": 13774,
                    "completion_tokens": 10,
                    "total_tokens": 13784,
                    "cost_usd": 0.0,
                }
            ]

    with caplog.at_level(logging.WARNING, logger="src.ai.orchestrator"):
        result = asyncio.run(AIDocOrchestrator(since_ref="HEAD~1", llm=UsageLLM()).run())
    assert result.status == "completed"
    logged = " ".join(record.getMessage() for record in caplog.records)
    assert "prompt_tokens=13774 exceeded AI_DOCS_MAX_CONTEXT_TOKENS=12000" in logged
    audit = next((tmp_path / "docs/.ai-logs").glob("run-*.json"))
    record = json.loads(audit.read_text(encoding="utf-8"))
    assert record["context_budget_tokens"] == 12000


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
