#!/usr/bin/env python3
"""Documentation Contract Validator — ADR-012 (Absolute Sync).

The manifest (``docs/.documentation-manifest.json``) is the formal contract
between code and documentation.  This validator compares four surfaces:

    repository tree  <->  manifest  <->  mkdocs.yml nav  <->  docs/ tree

and classifies every divergence with the Phase-1 audit labels:

    OK         artifact exists and is documented correctly
    ORFAO      documented, but the artifact no longer exists  (remove)
    OMITO      artifact exists, but is not documented         (create)
    OBSOLETO   documented, but stale vs the repository        (update)
    DIVERGENTE pt-BR / English surfaces disagree              (restore parity)

Any non-OK item is a BUILD DEFECT: ``validate`` exits non-zero.  Deterministic
and stdlib-only (runs in CI without the project venv, like the sync engine).

Subcommands:
    validate   Full contract check; exit 1 on any divergence (CI hard gate).
    report     Same checks, but emits the classified audit report (JSON +
               Markdown table) instead of failing; exit 0 unless I/O error.
    parity     pt-BR / English parity check only (README.md vs README.en.md).

Typing: fully annotated; check with
    uv run mypy .github/scripts/docs_contract.py --follow-imports=silent
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import docs_sync_engine as eng

STATE_OK = "OK"
STATE_ORFAO = "ORFAO"
STATE_OMITO = "OMITO"
STATE_OBSOLETO = "OBSOLETO"
STATE_DIVERGENTE = "DIVERGENTE"

DISPLAY: dict[str, str] = {
    STATE_OK: "OK",
    STATE_ORFAO: "ÓRFÃO",
    STATE_OMITO: "OMITO",
    STATE_OBSOLETO: "OBSOLETO",
    STATE_DIVERGENTE: "DIVERGENTE",
}

ACTION: dict[str, str] = {
    STATE_ORFAO: "remover da documentação (página, nav, links, manifest)",
    STATE_OMITO: "criar página e registrar no manifest",
    STATE_OBSOLETO: "atualizar para o estado atual do repositório",
    STATE_DIVERGENTE: "restaurar paridade pt-BR/English",
}

REPORT_PATH = Path(os.environ.get("CONTRACT_REPORT", "/tmp/docs_contract_report.json"))

RELEASE_ROW_RE = re.compile(r"^\|[^|]*\|\s*([\d,]+)\s*\|\s*(\d+)\s*\|", re.MULTILINE)
PYTHON_CLAIM_RE = re.compile(r"Python[- ](3\.\d+(?:\.\d+)?)")


@dataclass(frozen=True)
class Item:
    """One classified contract item (exactly one state per item)."""

    state: str
    kind: str
    path: str
    detail: str

    @property
    def action(self) -> str:
        return ACTION.get(self.state, "nenhuma")


def public_docs(inventory: set[str]) -> list[str]:
    """Doc surfaces that form the PUBLIC site (exclusions applied)."""
    return sorted(
        p
        for p in inventory
        if p.endswith(".md")
        and (p.startswith("docs/") or p in eng.DOC_ROOT_FILES)
        and not p.startswith(eng.PUBLIC_EXCLUDE_PREFIXES)
    )


# --------------------------------------------------------------------------- #
# Contract checks
# --------------------------------------------------------------------------- #
def check_manifest(inventory: dict[str, str], manifest: dict[str, Any]) -> list[Item]:
    items: list[Item] = []
    old: dict[str, str] = manifest.get("files", {})
    for path, sha in sorted(inventory.items()):
        if path == eng.MANIFEST_REL:
            continue
        if path not in old:
            items.append(
                Item(STATE_OMITO, "MANIFEST_NEW_FILE", path, "novo arquivo fora do baseline")
            )
        elif old[path] != sha:
            items.append(
                Item(STATE_OBSOLETO, "MANIFEST_STALE_SHA", path, "blob SHA diverge do baseline")
            )
    for path in sorted(old):
        if path not in inventory:
            items.append(
                Item(STATE_ORFAO, "MANIFEST_STALE_FILE", path, "no manifest, ausente do repo")
            )
    return items


def check_nav(inventory: set[str]) -> list[Item]:
    items: list[Item] = []
    _ordered, nav_set = eng.parse_nav_docs(eng.read_text("mkdocs.yml"))
    for missing in eng.nav_missing_files(nav_set, inventory):
        if missing in eng.GENERATED_PAGES:
            continue  # virtual build-time page (mkdocs-gen-files)
        if (eng.REPO_ROOT / missing).is_file():
            continue  # created in this reconcile, not yet committed
        items.append(
            Item(STATE_ORFAO, "NAV_MISSING_FILE", missing, "nav aponta para arquivo inexistente")
        )
    for doc in public_docs(inventory):
        if doc.startswith("docs/") and doc not in nav_set:
            items.append(Item(STATE_ORFAO, "ORPHAN_PAGE", doc, "página pública sem entrada no nav"))
    return items


def check_api_surface(inventory: set[str]) -> list[Item]:
    items: list[Item] = []
    for ev in eng.orphan_api_evokers():
        items.append(
            Item(STATE_ORFAO, "ORPHAN_API_DOC", ev, "evocador sem módulo/pacote de origem")
        )
    for mod in eng.missing_api_evokers():
        items.append(
            Item(STATE_OMITO, "MISSING_API_DOC", mod["file"], f"sem evocador em {mod['evoker']}")
        )
    return items


def check_coverage(inventory: dict[str, str]) -> list[Item]:
    """Every documentable artifact must have prose coverage or a dedicated page.

    The generated repository index (repo-index.md) is intentionally NOT
    counted as coverage: it is the pending-artifact ledger, not documentation.
    """
    items: list[Item] = []
    inv_set = set(inventory)
    texts = {d: eng.read_text(d) for d in public_docs(inv_set) if d != eng.REPO_INDEX_REL}
    _ordered, nav_set = eng.parse_nav_docs(eng.read_text("mkdocs.yml"))
    for art in eng.documentable_artifacts(inventory):
        if art.startswith("src/"):
            dotted = "src." + ".".join(Path(art).relative_to("src").with_suffix("").parts)
            if eng.evoker_rel_for(dotted) in inv_set:
                continue  # dedicated API page
        if art.startswith("docs/architecture/decisions/") and art in nav_set:
            continue  # ADR is its own documentation page, navigable
        if any(art in text for text in texts.values()):
            continue
        items.append(
            Item(STATE_OMITO, "UNDOCUMENTED_ARTIFACT", art, "artefato sem cobertura documental")
        )
    for directory in ("tests/", "releases/", "k8s/", "prompts/"):
        if not any(directory in text for text in texts.values()):
            items.append(
                Item(
                    STATE_OMITO,
                    "UNDOCUMENTED_DIRECTORY",
                    directory,
                    "diretório documentável sem nenhuma menção pública",
                )
            )
    return items


def check_obsolete(inventory: dict[str, str]) -> list[Item]:
    items: list[Item] = []
    for finding in eng.version_drift():
        items.append(
            Item(
                STATE_OBSOLETO,
                "VERSION_MISMATCH",
                str(finding.get("doc", "")),
                f"declara Python {finding.get('claimed')}; pyproject exige "
                f"{finding.get('authoritative')}",
            )
        )
    for finding in eng.obsolete_content(inventory):
        items.append(
            Item(
                STATE_OBSOLETO,
                "OBSOLETE_CONTENT",
                str(finding.get("path", "")),
                str(finding.get("detail", "")),
            )
        )
    for doc, title, locale in (
        ("docs/index.md", "Releases Disponíveis", "pt"),
        ("README.md", "Releases Disponíveis", "pt"),
        ("README.en.md", "Available Releases", "en"),
    ):
        for finding in eng.release_table_drift(eng.read_text(doc), title, doc, locale):
            items.append(
                Item(
                    STATE_OBSOLETO,
                    "RELEASE_TABLE_STALE",
                    doc,
                    "tabela de releases diverge de releases/*.meta.json",
                )
            )
    return items


def check_references(inventory: set[str]) -> list[Item]:
    items: list[Item] = []
    for finding in eng.dead_references(inventory):
        items.append(
            Item(
                STATE_ORFAO,
                "DEAD_CODE_REF",
                str(finding.get("doc", "")),
                f"referencia artefato inexistente: {finding.get('ref')}",
            )
        )
    for finding in eng.broken_internal_links(eng.rewritable_markdown(inventory), inventory):
        items.append(
            Item(
                STATE_ORFAO,
                "DOC_BROKEN_LINK",
                str(finding.get("doc", "")),
                f"link interno quebrado: {finding.get('target')}",
            )
        )
    return items


def _release_rows(doc: str, header_title: str) -> list[tuple[int, int]]:
    """(features, categories) pairs from the releases table under a heading."""
    text = eng.read_text(doc)
    hm = re.search(r"(?m)^##[^\n]*\b" + re.escape(header_title) + r"\b[^\n]*\n", text)
    if not hm:
        return []
    tm = re.search(
        r"(?m)\n*\| Release[^\n]*\|[^\n]*\r?\n\|\s*:?-+:?\s*\|[^\n]*\r?\n(?:\|.*\r?\n)*",
        text[hm.end() :],
    )
    if not tm:
        return []
    rows: list[tuple[int, int]] = []
    for m in RELEASE_ROW_RE.finditer(tm.group(0)):
        rows.append((int(m.group(1).replace(",", "")), int(m.group(2))))
    return rows


def check_parity() -> list[Item]:
    """Deterministic pt-BR / English parity (README.md vs README.en.md)."""
    items: list[Item] = []
    pt = eng.read_text("README.md")
    en = eng.read_text("README.en.md")
    if not pt or not en:
        items.append(
            Item(STATE_DIVERGENTE, "MISSING_LOCALE", "README.md/README.en.md", "locale ausente")
        )
        return items
    pt_ver = PYTHON_CLAIM_RE.search(pt)
    en_ver = PYTHON_CLAIM_RE.search(en)
    if pt_ver and en_ver and pt_ver.group(1) != en_ver.group(1):
        items.append(
            Item(
                STATE_DIVERGENTE,
                "PYTHON_VERSION_PARITY",
                "README.md/README.en.md",
                f"pt declara {pt_ver.group(1)}; en declara {en_ver.group(1)}",
            )
        )
    pt_rows = _release_rows("README.md", "Releases Disponíveis")
    en_rows = _release_rows("README.en.md", "Available Releases")
    if pt_rows != en_rows:
        items.append(
            Item(
                STATE_DIVERGENTE,
                "RELEASE_TABLE_PARITY",
                "README.md/README.en.md",
                f"tabelas de releases divergem: pt={pt_rows} en={en_rows}",
            )
        )
    return items


def run_checks() -> tuple[list[Item], dict[str, int]]:
    inventory = eng.tracked_inventory()
    manifest = eng.load_manifest()
    inv_set = set(inventory)
    items: list[Item] = []
    items += check_manifest(inventory, manifest)
    items += check_nav(inv_set)
    items += check_api_surface(inv_set)
    items += check_coverage(inventory)
    items += check_obsolete(inventory)
    items += check_references(inv_set)
    items += check_parity()
    ok_counts = {
        "tracked_files": len(inventory),
        "src_modules": len(eng.src_python_modules()),
        "api_evokers": len(eng.existing_api_evokers()),
        "public_pages": len([d for d in public_docs(inv_set) if d.startswith("docs/")]),
        "documentable_artifacts": len(eng.documentable_artifacts(inventory)),
        "releases": len(eng.release_inventory()),
    }
    return items, ok_counts


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _print_items(items: list[Item]) -> None:
    counts = Counter(i.state for i in items)
    for state in (STATE_ORFAO, STATE_OMITO, STATE_OBSOLETO, STATE_DIVERGENTE):
        for item in items:
            if item.state == state:
                print(f"  [{DISPLAY[state]}] {item.kind}: {item.path} — {item.detail}")
    print(
        "contrato: "
        + ", ".join(f"{DISPLAY[s]}={counts.get(s, 0)}" for s in DISPLAY)
        + f" | total divergências={len(items)}"
    )


def cmd_validate() -> int:
    items, ok_counts = run_checks()
    print(f"validando contrato de documentação (repo sha={eng.head_sha()[:7]})")
    for key, value in ok_counts.items():
        print(f"  {key}: {value}")
    _print_items(items)
    if items:
        print("❌ CONTRATO VIOLADO — divergências são defeitos de build (ADR-012).")
        return 1
    print("✅ contrato OK — manifest, nav, docs e repositório em sincronia absoluta.")
    return 0


def cmd_report() -> int:
    items, ok_counts = run_checks()
    counts = Counter(i.state for i in items)
    report = {
        "repository_sha": eng.head_sha(),
        "ok_counts": ok_counts,
        "state_counts": {DISPLAY[s]: counts.get(s, 0) for s in DISPLAY},
        "items": [asdict(i) | {"action": i.action} for i in items],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    _print_items(items)
    print(f"\nRelatório de auditoria escrito em {REPORT_PATH}")
    return 0


def cmd_parity() -> int:
    items = check_parity()
    _print_items(items)
    if items:
        print("❌ PARIDADE VIOLADA entre pt-BR e English.")
        return 1
    print("✅ paridade pt-BR/English verificada.")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(argv) if argv is not None else sys.argv[1:]
    if not argv or argv[0] not in ("validate", "report", "parity"):
        print("usage: docs_contract.py [validate|report|parity]", file=sys.stderr)
        return 2
    try:
        if argv[0] == "validate":
            return cmd_validate()
        if argv[0] == "report":
            return cmd_report()
        return cmd_parity()
    except Exception as exc:  # validator must report, never crash silently
        print(f"❌ docs_contract failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
