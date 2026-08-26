"""Build a didactic failure-diagnosis issue body for the Release Notes Pipeline.

Reads captured step logs from LOG_DIR (default /tmp/pipeline_logs), classifies
known error patterns, and emits a Markdown body with per-error sections
(evidence, probable cause, local reproduction, suggested fix) plus a dynamic
action-plan checklist. Stdout only; stdlib only.
"""

import os
import re
import sys
from pathlib import Path

LOG_DIR = Path(os.environ.get("LOG_DIR", "/tmp/pipeline_logs"))

LINT_RESULT = os.environ.get("LINT_RESULT", "unknown")
EXTRACT_RESULT = os.environ.get("EXTRACT_RESULT", "unknown")

RUN_ID = os.environ.get("GITHUB_RUN_ID", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "")
SHA = os.environ.get("GITHUB_SHA", "")[:12]
BRANCH = os.environ.get("GITHUB_REF_NAME", "")
TRIGGER = os.environ.get("GITHUB_EVENT_NAME", "")
RUN_URL = f"https://github.com/{REPO}/actions/runs/{RUN_ID}" if REPO and RUN_ID else ""

STATUS_BADGE = {
    "success": "✅ success",
    "failure": "❌ failure",
    "cancelled": "⚠️ cancelled",
    "skipped": "⏭️ skipped",
}

PATTERNS: list[tuple[str, str, str, str, str]] = [
    (
        r"APIConnectionError|Connection error|ConnectionError|Failed to establish|Name or service not known|SSLError",
        "Falha de conexão com provedor de LLM",
        "Endpoint (`base_url`) incorreto/indisponível, DNS ou instabilidade de rede no runner.",
        "`OPENCODE_API_KEY=<key> uv run python -m src.main --dry-run`",
        "Conferir `base_url` de cada provider em `_PROVIDER_CHAIN` (`src/llm_service.py`) e em `_call_opencode` "
        "(`.github/scripts/llm_fallback.py`). Endpoint correto do OpenCode Zen: `https://opencode.ai/zen/v1`.",
    ),
    (
        r"429[^\n]*RESOURCE_EXHAUSTED|RESOURCE_EXHAUSTED",
        "Quota diária do Gemini esgotada (HTTP 429)",
        "O free tier do Gemini permite ~20 requisições/dia; o limite foi atingido.",
        "—",
        "O circuit breaker já desativa o provider pelo resto do run. Aguardar reset diário da cota ou reforçar o "
        "pool gratuito OpenCode/OpenRouter em `_opencode_models()` / `_openrouter_models()`.",
    ),
    (
        r"\b503\b[^\n]*(upstream|Service Unavailable)|Service Unavailable",
        "Modelo gratuito indisponível (503 upstream)",
        "Modelos free oscilam ao longo do dia (503 um dia, stalls noutro).",
        "—",
        "Confirmar nos logs que o sweep varreu os modelos alternativos do pool antes de falhar; se todos caíram, "
        "considerar adicionar um novo modelo free à lista.",
    ),
    (
        r"Traceback \(most recent call last\)",
        "Exceção não tratada no pipeline",
        "Bug de código ou entrada inesperada (HTML atípico, JSON malformado, timeout de Playwright).",
        "Rodar o mesmo comando do step com a mesma `--release <slug>` afetada.",
        "Analisar o stack trace na evidência abaixo; o módulo/arquivo da última linha indica onde intervir.",
    ),
    (
        r"cache says '0 recursos'|no \.summary_cache\.json found|0 category_summaries but meta has",
        "Cache de resumos (.summary_cache.json) inconsistente com .meta.json",
        "A geração de resumos foi interrompida antes de gravar todos os caches, ou gravou estado vazio.",
        "`uv run python -m src.main --release <slug>` e conferir `releases/<slug>/.summary_cache.json`",
        "Reexecutar a geração da(s) release(s) apontada(s) na validação de caches; investigar falha parcial do "
        "provedor de LLM durante a geração de summaries.",
    ),
    (
        r"failed to push some refs|!\s*\[remote rejected\]|fetch first",
        "Push rejeitado — concorrência com outro commit",
        "Outro commit chegou ao branch entre o checkout e o push deste run.",
        "`git pull --rebase origin main && git push`",
        "Reexecutar o job. O grupo de concurrency já limita execuções paralelas; verificar agendamentos sobrepostos.",
    ),
    (
        r"error: failed to push|fatal:[^\n]*push",
        "Falha no git commit/push",
        "Estado do repositório inconsistente (detached head, credenciais, force-with-lease stale).",
        "Inspecionar o trecho do log abaixo.",
        "Verificar o step 'Commit e push' e as permissões do GITHUB_TOKEN (contents: write).",
    ),
    (
        r"gh:[^\n]*Not Found|release create[^\n]*error|Failed: ",
        "Falha ao criar GitHub Release",
        "Tag já existente, permissões insuficientes ou resposta inesperada da API.",
        "`gh release list --limit 10` e comparar tags geradas (`v20YY-<season>`).",
        "Conferir dedup de tags em `.meta.json` vs releases existentes e o escopo do token.",
    ),
    (
        r"ERROR[^\n]*Playwright|Timeout.*exceeded|net::ERR_|browser[^a-z]*crashed",
        "Falha de scraping (Playwright/browser)",
        "Salesforce Help lento/instável, seletor alterado ou crash do browser no runner.",
        "`uv run playwright install chromium && uv run python -m src.main --release <slug>`",
        "Revisar seletores do parser para a página que falhou; considerar retry/backoff maior.",
    ),
    (
        r"(?m)^src/[^\s:]+:\d+:\s+error:",
        "Erros de tipagem estática (mypy)",
        "Assinaturas/anotações divergentes após mudanças recentes no código.",
        "`uv run mypy src/ --ignore-missing-imports`",
        "Corrigir cada linha reportada no log `lint_mypy.log` (arquivo:linha: erro).",
    ),
    (
        r"(?m)^(?:[A-Z]+:\d+:\d+:|[a-zA-Z_/]+\.py:)\s*(E\d+|F\d+|W\d+)\s",
        "Problemas de lint (ruff)",
        "Código fora das regras do projeto (imports, naming, complexidade).",
        "`uv run ruff check . --fix`",
        "Aplicar autofix quando seguro; ajustar manualmente o restante conforme códigos E/F/W no log.",
    ),
    (
        r"FAILED tests/",
        "Testes automatizados falhando (pytest)",
        "Regressão funcional ou fixture desatualizada.",
        "`uv run pytest tests/ -q --tb=short -k <teste>`",
        "Rodar os testes indicados em `FAILED` isoladamente; corrigir código ou teste conforme o caso.",
    ),
]


def read_logs() -> dict[str, str]:
    logs: dict[str, str] = {}
    if not LOG_DIR.is_dir():
        return logs
    for path in sorted(LOG_DIR.rglob("*")):
        if path.is_file():
            try:
                text = path.read_text(errors="replace")
            except OSError:
                continue
            if text.strip():
                rel = path.relative_to(LOG_DIR)
                logs[str(rel)] = text[-200_000:]
    return logs


def excerpt(text: str, regex: str, context: int = 4, max_lines: int = 30) -> tuple[int, str] | None:
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if re.search(regex, line):
            start = max(0, idx - context)
            end = min(len(lines), idx + context + 1)
            window = lines[start:end]
            if len(window) > max_lines:
                window = window[:max_lines]
            return idx + 1, "\n".join(window)
    return None


def classify(logs: dict[str, str]) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    seen_titles: set[str] = set()
    for filename, text in logs.items():
        for regex, title, cause, repro, fix in PATTERNS:
            hit = excerpt(text, regex)
            if not hit or title in seen_titles:
                continue
            seen_titles.add(title)
            findings.append(
                {
                    "title": title,
                    "file": filename,
                    "line": hit[0],
                    "evidence": hit[1],
                    "cause": cause,
                    "repro": repro,
                    "fix": fix,
                }
            )
    return findings


def status_table() -> list[str]:
    return [
        "| Etapa | Resultado |",
        "|---|---|",
        f"| 🔍 Lint & Type Check (ruff · mypy · pytest) | {STATUS_BADGE.get(LINT_RESULT, LINT_RESULT)} |",
        f"| 📥 Extração e Geração de Artefatos | {STATUS_BADGE.get(EXTRACT_RESULT, EXTRACT_RESULT)} |",
    ]


def error_section(num: int, finding: dict[str, object]) -> list[str]:
    out = [
        f"### {num}. {finding['title']}",
        "",
        f"**Onde:** `{finding['file']}`, por volta da linha {finding['line']}",
        "",
        "**Evidência (trecho do log):**",
        "",
        "```text",
        str(finding["evidence"]),
        "```",
        "",
        f"**Causa provável:** {finding['cause']}",
        "",
        f"**Como reproduzir localmente:** {finding['repro']}",
        "",
        f"**Reparo sugerido:** {finding['fix']}",
        "",
    ]
    return out


def build_body(findings: list[dict[str, object]]) -> str:
    parts: list[str] = [
        "## 🚀 Release Notes Automation Pipeline falhou",
        "",
        f"**Run:** [#{RUN_ID}]({RUN_URL}) · **Branch:** `{BRANCH}` · **Commit:** `{SHA}` · **Trigger:** `{TRIGGER}`",
        "",
        "### 📊 Status das etapas",
        "",
        *status_table(),
        "",
    ]

    if not findings:
        parts += [
            "### 🔍 Diagnóstico",
            "",
            "Nenhum padrão conhecido foi identificado nos logs capturados. Os arquivos completos estão nos "
            "artifacts do run (ver links abaixo) — inspecioná-los manualmente para classificar a falha.",
            "",
        ]
    else:
        parts += ["### 🔍 Erros detectados e explicação detalhada", ""]
        for i, finding in enumerate(findings, 1):
            parts += error_section(i, finding)

    parts += ["### ✅ Plano de ação sugerido", ""]
    for i, finding in enumerate(findings, 1):
        parts.append(f"- [ ] **{i}.** {finding['title']} → {finding['fix']}")
    if not findings:
        parts.append("- [ ] Baixar artifacts do run e identificar a etapa exata da falha")
    parts += [
        "- [ ] Após aplicar os reparos, validar localmente: `uv run ruff check . && uv run black --check . && uv run mypy src/ && uv run pytest`",
        "- [ ] Reexecutar o workflow (`workflow_dispatch`) confirmando recuperação",
        "",
        "### 🔗 Links",
        f"- [Logs completos desta execução]({RUN_URL})",
        f"- Artifacts `lint-logs` / `extract-logs` disponíveis nesta run (retenção de 7 dias): {RUN_URL}",
        "",
        "> 🤖 Issue gerada automaticamente pelo Release Notes Automation Pipeline.",
    ]
    return "\n".join(parts)


def main() -> int:
    logs = read_logs()
    findings = classify(logs)
    sys.stdout.write(build_body(findings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
