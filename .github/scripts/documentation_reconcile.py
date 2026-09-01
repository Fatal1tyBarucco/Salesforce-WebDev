"""Documentation Intelligence — LLM reconciliation agent.

Consumes the drift report produced by documentation_sync.py, gathers git
evidence for each finding and asks the repository's existing LLMService
(Gemini -> OpenCode -> OpenRouter chain) to reconcile affected documentation.

Hard safety rules enforced here regardless of model output:
  - Only paths under docs/, README.md, README.en.md and mkdocs.yml are writable.
  - Source code, tests, workflows and secrets are NEVER modified.
  - Mock/no-provider responses abort without writing anything.

Stdout emits a Markdown summary suitable for GITHUB_STEP_SUMMARY.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(os.environ.get("REPO_ROOT", Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(REPO_ROOT / "src"))

MAX_FINDINGS_PER_RUN = int(os.environ.get("DOC_SYNC_MAX_FINDINGS", "8"))
EVIDENCE_MAX_CHARS = 6_000

WRITABLE_PREFIXES = ("docs/",)
WRITABLE_EXACT = {"README.md", "README.en.md", "mkdocs.yml"}

SYSTEM_PROMPT = """You are the Documentation Intelligence Agent for the Fatal1tyBarucco/Salesforce-WebDev repository.
The Git repository is the single source of truth; documentation is only its representation.
Precedence: source code > configuration > workflows > dependencies > tests > structure > git history > existing docs.
If documentation contradicts the repository, update the DOCUMENTATION — never invent functionality,
metrics or behavior. Remove statements that are no longer true; add missing current facts;
keep the existing document structure and language (pt-BR docs stay pt-BR).
When a documented component was deleted, delete exclusively-obsolete docs and strip their nav entries;
rewrite partially-obsolete docs to describe what remains.
Respond with STRICT JSON only, no markdown fences:
{"actions": [{"op": "update|create|delete", "path": "docs/...", "reason": "...", "content": "<full final file content, required for update/create>"}], "summary": "one paragraph"}
Only paths under docs/ plus exactly README.md, README.en.md, mkdocs.yml are allowed."""


def _run(cmd: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=120)
        return proc.returncode, proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)


def read_report(path: str) -> dict:
    return json.loads(Path(path).read_text())


def cap(text: str, limit: int = EVIDENCE_MAX_CHARS) -> str:
    return text if len(text) <= limit else text[:limit] + "\n...(truncated)"


def evidence_for(finding: dict) -> str:
    parts: list[str] = [f"### Finding: {finding.get('type')}\n{finding.get('detail', '')}"]
    src = finding.get("source")
    if src:
        code, current = _run(["git", "show", f"HEAD:{src}"])
        if code == 0:
            parts.append(f"#### Current content of {src}\n```text\n{cap(current)}\n```")
        else:
            parts.append(f"#### {src} no longer exists in HEAD.")
        prev_sha = _report_prev_sha()
        if prev_sha and prev_sha != "unknown":
            _, diff = _run(["git", "diff", "-U2", prev_sha, "HEAD", "--", src])
            if diff:
                parts.append(f"#### Diff since last reconciliation\n```diff\n{cap(diff)}\n```")
    doc = finding.get("doc") or next(iter(finding.get("affected_docs", [])), None)
    if doc:
        path = REPO_ROOT / doc
        if path.is_file():
            body = "\n".join(path.read_text(errors="replace").splitlines()[:120])
            parts.append(
                f"#### Current content of {doc} (first 120 lines)\n```markdown\n{cap(body)}\n```"
            )
        else:
            parts.append(f"#### {doc} does not exist yet.")
    return "\n\n".join(parts)


_report_data: dict = {}


def _report_prev_sha() -> str:
    return str(_report_data.get("previous_manifest_sha") or "unknown")


def build_user_prompt(findings: list[dict], mode: str) -> str:
    head = (
        f"Mode: {mode}. Reconcile documentation for the findings below.\n"
        "Return actions ONLY where documentation actually needs changes; "
        "return an empty actions list when everything is already accurate."
    )
    blocks = [head]
    for i, finding in enumerate(findings, 1):
        blocks.append(f"\n## Finding {i}\n{evidence_for(finding)}")
    mk = REPO_ROOT / "mkdocs.yml"
    if mk.is_file():
        blocks.append(
            f"\n## Current mkdocs.yml nav\n```yaml\n{cap(mk.read_text(errors='replace'), 3000)}\n```"
        )
    return "\n".join(blocks)


def parse_actions(raw: str) -> tuple[list[dict], str]:
    text = raw.strip()
    fence = re.search(r"\{.*\}", text, re.DOTALL)
    payload = fence.group(0) if fence else text
    data = json.loads(payload)
    return list(data.get("actions", [])), str(data.get("summary", ""))


def is_safe_path(op_path: str, op: str) -> bool:
    p = op_path.replace("\\", "/").lstrip("./")
    if p in WRITABLE_EXACT:
        return True
    return p.startswith(WRITABLE_PREFIXES) if op in ("update", "create") else p.startswith("docs/")


def strip_nav_entries(doc_rel: str) -> int:
    """Deterministically remove mkdocs.yml nav lines pointing at a deleted doc."""
    mk = REPO_ROOT / "mkdocs.yml"
    if not mk.is_file():
        return 0
    lines = mk.read_text().splitlines(keepends=True)
    needle = doc_rel.lstrip("/")
    kept = [
        ln
        for ln in lines
        if not (re.match(r"\s*-\s*[^:]+:\s*\S*" + re.escape(needle) + r"\s*$", ln))
    ]
    removed = len(lines) - len(kept)
    if removed:
        mk.write_text("".join(kept))
    return removed


def apply_actions(actions: list[dict]) -> tuple[list[str], list[str]]:
    applied: list[str] = []
    rejected: list[str] = []
    for act in actions:
        op, path = act.get("op"), str(act.get("path", ""))
        if op == "read":
            continue
        if op not in ("update", "create", "delete"):
            rejected.append(f"{path}: operação inválida '{op}'")
            continue
        if not is_safe_path(path, op):
            rejected.append(f"{path}: fora da allowlist de documentação")
            continue
        target = REPO_ROOT / path
        if op == "delete":
            if target.is_file():
                target.unlink()
                strip_nav_entries(path)
                applied.append(f"deleted {path}")
            continue
        content = act.get("content")
        if not isinstance(content, str) or len(content.strip()) < 40:
            rejected.append(f"{path}: conteúdo ausente/curto demais para {op}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        applied.append(f"{op}d {path} ({len(content)} chars)")
    return applied, rejected


def llm_generate(prompt: str) -> str:
    from llm_service import LLMService

    service = LLMService()
    if service.provider == "none":
        raise RuntimeError("no-llm-provider")
    out = service.generate_completion(
        prompt=prompt,
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1,
        max_tokens=8000,
    )
    if out.startswith("[Mock LLM Response]"):
        raise RuntimeError("mock-response")
    return out


def main() -> int:
    global _report_data

    report_path = os.environ.get("DRIFT_REPORT", "/tmp/drift_report.json")
    mode = os.environ.get("SYNC_MODE", "incremental")

    try:
        report = read_report(report_path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"❌ Relatório de drift ilegível: {exc}")
        return 1
    _report_data = report

    actionable = [
        f
        for f in report.get("findings", [])
        if f.get("type")
        in (
            "SOURCE_CHANGED",
            "DOC_ORPHANED_CANDIDATE",
            "MISSING_API_DOC",
            "NAV_MISSING_FILE",
            "DOC_BROKEN_LINK",
        )
    ]
    print(f"## 📚 Documentation Sync ({mode})\n")
    print(f"Findings acionáveis: {len(actionable)} (cap {MAX_FINDINGS_PER_RUN})\n")

    if not actionable:
        print("✅ Nenhum drift acionável — documentação consistente com o repositório.")
        return 0

    if mode == "audit":
        for f in actionable:
            print(f"- 🔍 [{f.get('type')}] {f.get('detail')}")
        print("\nModo audit: somente análise, nenhuma alteração aplicada.")
        return 0

    batch = actionable[:MAX_FINDINGS_PER_RUN]
    prompt = build_user_prompt(batch, mode)

    try:
        raw = llm_generate(prompt)
    except RuntimeError as exc:
        print(
            f"⚠️ Reconciliação LLM indisponível ({exc}); nada foi modificado. "
            "Findings ficam registrados neste sumário para revisão manual:\n"
        )
        for f in batch:
            print(f"- 🔍 [{f.get('type')}] {f.get('detail')}")
        return 0
    except Exception as exc:  # noqa: BLE001 — any provider failure must not break CI
        print(f"⚠️ Falha do LLM ({exc}); nenhuma alteração aplicada.")
        return 0

    try:
        actions, summary = parse_actions(raw)
    except json.JSONDecodeError:
        print("⚠️ LLM retornou JSON inválido; nenhuma alteração aplicada.")
        return 0

    applied, rejected = apply_actions(actions)

    print(f"**Resumo do agente:** {summary or '(sem resumo)'}\n")
    if applied:
        print("### Alterações aplicadas\n")
        for item in applied:
            print(f"- ✅ {item}")
    if rejected:
        print("\n### Ações bloqueadas pelas regras de segurança\n")
        for item in rejected:
            print(f"- ⛔ {item}")
    skipped = actionable[MAX_FINDINGS_PER_RUN:]
    if skipped:
        print(f"\n⏭️ {len(skipped)} findings deixados para o próximo ciclo:")
        for f in skipped[:5]:
            print(f"- [{f.get('type')}] {f.get('detail')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
