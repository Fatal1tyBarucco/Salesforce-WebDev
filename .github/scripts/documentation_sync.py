"""Documentation Intelligence — deterministic inventory, manifest and drift engine.

Repository state (tracked files + blob SHAs via `git ls-files -s`) is the single
source of truth. This tool compares it against docs/.documentation-manifest.json
to produce a structured drift report consumed by documentation_reconcile.py.

Commands:
    drift     compare current repository against the manifest, emit report JSON
    manifest  regenerate the manifest baseline after successful reconciliation

Stdlib only; safe to run anywhere `git` is available.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(os.environ.get("REPO_ROOT", Path(__file__).resolve().parents[2]))
MANIFEST_PATH = REPO_ROOT / "docs" / ".documentation-manifest.json"

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "site",
    "node_modules",
    ".mimocode",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".geminiignore",
}

DOC_AREAS = ("docs/", "README.md", "README.en.md", "mkdocs.yml")
CODE_AREAS = ("src/", ".github/workflows/", ".github/scripts/", "pyproject.toml", "Dockerfile")

MAX_REPORT_FILES_PER_LIST = 400


def _run(cmd: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=120)
        return proc.returncode, proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)


def head_sha() -> str:
    code, out = _run(["git", "rev-parse", "HEAD"])
    return out if code == 0 else "unknown"


def tracked_inventory() -> dict[str, str]:
    """Return {path: blob_sha} for every tracked file (one `ls-files -s` call)."""
    code, out = _run(["git", "ls-files", "-s"])
    if code != 0:
        raise RuntimeError(f"git ls-files failed: {out}")
    inv: dict[str, str] = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 4:
            inv[parts[3]] = parts[1]
    return inv


def load_manifest() -> dict | None:
    if not MANIFEST_PATH.is_file():
        return None
    try:
        data = json.loads(MANIFEST_PATH.read_text())
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def build_documentation_map(inventory: dict[str, str]) -> dict[str, list[str]]:
    """Deterministic source<->doc mapping: api convention + literal path mentions."""
    doc_map: dict[str, set[str]] = {}

    def link(src: str, doc: str) -> None:
        if src in inventory and doc in inventory:
            doc_map.setdefault(src, set()).add(doc)

    for src in inventory:
        if src.startswith("src/") and src.endswith(".py"):
            stem = Path(src).stem
            if stem == "__init__":
                continue
            link(src, f"docs/api/{stem}.md")

    mention_re = re.compile(r"(?<![\w./-])((?:src|\.github)/[\w\-./]+\.(?:py|yml|yaml))(?![\w.-])")
    candidates = [
        p
        for p in inventory
        if p.endswith(".md") and (p.startswith("docs/") or p in ("README.md", "README.en.md"))
    ]
    for doc in candidates:
        path = REPO_ROOT / doc
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        for match in mention_re.findall(text[:120_000]):
            link(match, doc)
    return {k: sorted(v) for k, v in doc_map.items()}


def check_nav_and_links(inventory: dict[str, str]) -> list[dict]:
    """Global deterministic checks: mkdocs nav entries + internal md links."""
    findings: list[dict] = []

    mk = REPO_ROOT / "mkdocs.yml"
    if mk.is_file():
        for idx, line in enumerate(mk.read_text(errors="replace").splitlines(), 1):
            entry = re.match(r"\s*-\s*[^:]+:\s*(\S+\.md)\s*$", line)
            resolved = f"docs/{entry.group(1)}" if entry else ""
            if entry and resolved not in inventory:
                findings.append(
                    {
                        "type": "NAV_MISSING_FILE",
                        "severity": "high",
                        "detail": f"mkdocs.yml:{idx}: nav aponta para arquivo inexistente '{entry.group(1)}'",
                        "doc": "mkdocs.yml",
                    }
                )

    link_re = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
    for doc in inventory:
        if not doc.endswith(".md") or not doc.startswith("docs/"):
            continue
        text = (REPO_ROOT / doc).read_text(errors="replace") if (REPO_ROOT / doc).is_file() else ""
        base = Path(doc).parent
        for target in link_re.findall(text)[:200]:
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#")[0].split("?")[0].strip()
            if not clean:
                continue
            resolved = (base / clean).resolve().relative_to(REPO_ROOT.resolve()).as_posix()
            if resolved not in inventory and not (REPO_ROOT / resolved).is_dir():
                findings.append(
                    {
                        "type": "DOC_BROKEN_LINK",
                        "severity": "medium",
                        "detail": f"{doc}: link interno quebrado -> '{target}'",
                        "doc": doc,
                    }
                )
    return findings


def build_drift(mode: str) -> dict:
    inventory = tracked_inventory()
    current_sha = head_sha()
    manifest = load_manifest()

    report: dict = {
        "mode": mode,
        "repository_sha": current_sha,
        "previous_manifest_sha": (manifest or {}).get("repository_sha"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "changed_files": [],
        "added_files": [],
        "deleted_files": [],
        "findings": [],
    }

    if manifest is None:
        report["findings"].append(
            {
                "type": "MANIFEST_MISSING",
                "severity": "info",
                "detail": "Primeira execução: manifesto inexistente; documentação será auditada e baseline criada.",
            }
        )
        report["findings"] += check_nav_and_links(inventory)
        return report

    old_files: dict[str, str] = manifest.get("files", {})
    old_map: dict[str, list[str]] = manifest.get("documentation_map", {})

    changed = [p for p, sha in inventory.items() if p in old_files and old_files[p] != sha]
    added = [p for p in inventory if p not in old_files]
    deleted = [p for p in old_files if p not in inventory]

    def cap(items: list[str]) -> list[str]:
        return (
            items
            if len(items) <= MAX_REPORT_FILES_PER_LIST
            else items[:MAX_REPORT_FILES_PER_LIST] + ["...(truncated)"]
        )

    report["changed_files"] = cap(sorted(changed))
    report["added_files"] = cap(sorted(added))
    report["deleted_files"] = cap(sorted(deleted))

    for src in changed:
        if src.startswith(CODE_AREAS):
            affected = old_map.get(src, [])
            report["findings"].append(
                {
                    "type": "SOURCE_CHANGED",
                    "severity": "high",
                    "source": src,
                    "affected_docs": affected,
                    "detail": f"'{src}' mudou desde a última reconciliação; documentação afetada: {affected or '(a mapear)'}",
                }
            )

    for src in deleted:
        for doc in old_map.get(src, []):
            if doc in inventory:
                report["findings"].append(
                    {
                        "type": "DOC_ORPHANED_CANDIDATE",
                        "severity": "high",
                        "source": src,
                        "doc": doc,
                        "detail": f"'{src}' foi removido mas '{doc}' ainda existe — confirmar exclusão semântica.",
                    }
                )

    for src in added:
        if src.startswith("src/") and src.endswith(".py") and "__init__" not in src:
            stem = Path(src).stem
            api_doc = f"docs/api/{stem}.md"
            if api_doc not in inventory:
                report["findings"].append(
                    {
                        "type": "MISSING_API_DOC",
                        "severity": "medium",
                        "source": src,
                        "detail": f"Novo módulo '{src}' sem documentação em '{api_doc}'.",
                    }
                )

    if mode == "full":
        report["findings"] += check_nav_and_links(inventory)

    return report


def write_manifest() -> int:
    inventory = tracked_inventory()
    manifest = {
        "repository_sha": head_sha(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": inventory,
        "documentation_map": build_documentation_map(inventory),
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(
        f"Manifest gravado em {MANIFEST_PATH.relative_to(REPO_ROOT)} "
        f"({len(inventory)} arquivos, mapa com {len(manifest['documentation_map'])} entradas)"
    )
    return 0


def main() -> int:
    args = sys.argv[1:]
    command = args[0] if args else ""

    if command == "drift":
        mode = "full"
        if "--mode" in args:
            mode = args[args.index("--mode") + 1]
        report_path = os.environ.get("DRIFT_REPORT", "/tmp/drift_report.json")
        if "--report" in args:
            report_path = args[args.index("--report") + 1]
        report = build_drift(mode)
        Path(report_path).write_text(json.dumps(report, indent=2, ensure_ascii=False))
        counts: dict[str, int] = {}
        for f in report["findings"]:
            counts[f["type"]] = counts.get(f["type"], 0) + 1
        print(
            f"Drift ({mode}): {len(report['findings'])} findings "
            f"| changed={len(report['changed_files'])} added={len(report['added_files'])} "
            f"deleted={len(report['deleted_files'])}"
        )
        for kind, n in sorted(counts.items()):
            print(f"  {kind}: {n}")
        print(f"Relatório: {report_path}")
        return 0

    if command == "manifest":
        return write_manifest()

    print(
        "uso: documentation_sync.py drift [--mode incremental|full] [--report PATH] | manifest",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
