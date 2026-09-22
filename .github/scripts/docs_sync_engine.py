#!/usr/bin/env python3
"""Documentation Sync Engine for Salesforce-WebDev.

Deterministic, LLM-free reconciliation layer.  Git-tracked files (with blob
SHAs) are the single source of truth.  The engine complements the existing
`documentation_sync.py` (drift detection) + `documentation_reconcile.py`
(LLM arm): it performs the *deterministic* structural fixes that never need a
language model and therefore run anywhere — including CI without secrets.

Subcommands:
    scan        Emit a full repository inventory + source<->doc map.
    audit       Scan repo vs docs, emit a structured drift report (read-only).
    reconcile   Apply deterministic, build-safe fixes.
    manifest    Regenerate docs/.documentation-manifest.json baseline.

Stdlib only.  Every git/filesystem operation is guarded so missing paths,
None values, or git hiccups never raise unhandled exceptions.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(os.environ.get("REPO_ROOT", Path(__file__).resolve().parents[2]))
MANIFEST_PATH = REPO_ROOT / "docs" / ".documentation-manifest.json"
MANIFEST_REL = "docs/.documentation-manifest.json"  # relative key for inventory compare (manifest is metadata, not a tracked doc)
SRC_ROOT = REPO_ROOT / "src"
DOCS_ROOT = REPO_ROOT / "docs"
MKKDOCS_PATH = REPO_ROOT / "mkdocs.yml"
REPORT_PATH = Path(os.environ.get("DRIFT_REPORT", "/tmp/drift_report.json"))

SRC_NON_MODULE_FILES = {
    "openapi_spec.json",
    "trailhead.json",
    "dashboard_template.html",
    "py.typed",
}
SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "site",
    "node_modules",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "stubs",
}
DOC_ROOT_FILES = {
    "README.md",
    "README.en.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
}

# Matches prose code-path references: src/foo.py, scripts/x.sh, .github/workflows/y.yml
PATH_REF_RE = re.compile(
    r"(?<![\w./-])((?:src|scripts|\.github/workflows|\.github/scripts)/[\w\-./]+"
    r"(?:\.py|\.yml|\.yaml|\.sh|\.json))(?![\w.-])"
)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s#]+)")
NAV_LEAF_RE = re.compile(r"^\s*-\s*(?:[^:]+:\s*)?(\S+\.md)\s*$")
FENCE_RE = re.compile(r"^```")
# Markdown links and images: [text](target) / ![alt](target).  Target has no
# spaces or closing paren (no titled links).  The optional leading "!" lets us
# treat dead image references symmetrically.
MD_LINK_RE = re.compile(r"(?<!\\)!?\[([^\]]*)\]\(([^)\s]*)\)")


# --------------------------------------------------------------------------- #
# Safe low-level helpers
# --------------------------------------------------------------------------- #
def run_git(args: list[str]) -> tuple[int, str]:
    try:
        import subprocess

        proc = subprocess.run(
            ["git", "-C", str(REPO_ROOT)] + args,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return proc.returncode, proc.stdout.strip()
    except (OSError, Exception):
        return 1, ""


def head_sha() -> str:
    code, out = run_git(["rev-parse", "HEAD"])
    return out if code == 0 else "unknown"


def tracked_inventory() -> dict[str, str]:
    code, out = run_git(["ls-files", "-s"])
    if code != 0 or not out:
        return {}
    inv: dict[str, str] = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[3] != MANIFEST_REL:
            inv[parts[3]] = parts[1]
    return inv


def read_text(rel: str) -> str:
    try:
        return (REPO_ROOT / rel).read_text(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        return ""


def load_manifest() -> dict:
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError, json.JSONDecodeError):
        return {}


def write_file(rel: str, content: str) -> bool:
    try:
        path = REPO_ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else None
        if existing == content:
            return False
        path.write_text(content, encoding="utf-8")
        return True
    except (OSError, ValueError):
        return False


# --------------------------------------------------------------------------- #
# Inventory builders
# --------------------------------------------------------------------------- #
def src_python_modules() -> list[dict]:
    modules: list[dict] = []
    if not SRC_ROOT.is_dir():
        return modules
    for py in sorted(SRC_ROOT.rglob("*.py")):
        if py.name == "__init__.py":
            continue
        rel = py.relative_to(REPO_ROOT).as_posix()
        if py.name in SRC_NON_MODULE_FILES or rel in SRC_NON_MODULE_FILES:
            continue
        dotted = ".".join(py.relative_to(SRC_ROOT).with_suffix("").parts)
        modules.append({"file": rel, "dotted": f"src.{dotted}", "stem": py.stem})
    return modules


def existing_api_evokers() -> set[str]:
    return {p.relative_to(REPO_ROOT).as_posix() for p in DOCS_ROOT.glob("api/*.md")}


def evoker_rel_for(dotted: str) -> str:
    parts = dotted.split(".")
    inner = parts[1:]
    if len(inner) == 1:
        return f"docs/api/{inner[0]}.md"
    return "docs/api/" + "-".join(inner) + ".md"


def module_title(dotted: str, rel_file: str) -> str:
    try:
        tree = ast.parse(read_text(rel_file))
        doc = ast.get_docstring(tree)
        if doc:
            first = doc.strip().splitlines()[0].strip().rstrip(".")
            if first and len(first) <= 60:
                return first
    except (SyntaxError, ValueError):
        pass
    stem = Path(rel_file).stem
    human = " ".join(w.capitalize() for w in re.split(r"[_\-.]+", stem))
    return human or stem


def missing_api_evokers() -> list[dict]:
    have = existing_api_evokers()
    out: list[dict] = []
    for mod in src_python_modules():
        ev = evoker_rel_for(mod["dotted"])
        if ev not in have:
            out.append({**mod, "evoker": ev, "title": module_title(mod["dotted"], mod["file"])})
    return out


def build_documentation_map(inventory: dict[str, str]) -> dict[str, list[str]]:
    doc_map: dict[str, set[str]] = {}

    def link(src: str, doc: str) -> None:
        if src in inventory and doc in inventory:
            doc_map.setdefault(src, set()).add(doc)

    for mod in src_python_modules():
        link(mod["file"], evoker_rel_for(mod["dotted"]))

    candidates = sorted(
        p for p in inventory if p.endswith(".md") and (p.startswith("docs/") or p in DOC_ROOT_FILES)
    )
    for doc in candidates:
        for match in PATH_REF_RE.findall(read_text(doc)[:180_000]):
            link(match, doc)
    return {k: sorted(v) for k, v in doc_map.items()}


# --------------------------------------------------------------------------- #
# mkdocs nav helpers (line-based to preserve formatting/comments)
# --------------------------------------------------------------------------- #
def parse_nav_docs(mktext: str) -> tuple[list[str], set[str]]:
    ordered: list[str] = []
    seen: set[str] = set()
    for line in mktext.splitlines():
        m = NAV_LEAF_RE.match(line)
        if not m:
            continue
        ref = m.group(1)
        if ref.startswith(("http://", "https://")):
            continue
        rel = f"docs/{ref}" if not ref.startswith("docs/") else ref
        if rel not in seen:
            seen.add(rel)
            ordered.append(rel)
    return ordered, seen


def nav_missing_files(nav_set: set[str], inventory: set[str]) -> list[str]:
    return sorted(p for p in nav_set if p not in inventory)


def docs_not_in_nav(tracked_docs: list[str], nav_set: set[str]) -> list[str]:
    return sorted(p for p in tracked_docs if p not in nav_set)


# --------------------------------------------------------------------------- #
# Drift detectors
# --------------------------------------------------------------------------- #
def stale_manifest(inventory: dict[str, str], manifest: dict) -> list[dict]:
    findings: list[dict] = []
    old_files: dict[str, str] = manifest.get("files", {})
    for path, sha in inventory.items():
        if path in old_files and old_files[path] != sha:
            findings.append(
                {
                    "type": "MANIFEST_STALE_SHA",
                    "severity": "high",
                    "path": path,
                    "detail": f"'{path}' blob SHA changed since last manifest baseline.",
                }
            )
    for path in old_files:
        if path not in inventory:
            findings.append(
                {
                    "type": "MANIFEST_STALE_FILE",
                    "severity": "medium",
                    "path": path,
                    "detail": f"'{path}' is in manifest but missing from repo.",
                }
            )
    for path in inventory:
        if path not in old_files:
            findings.append(
                {
                    "type": "MANIFEST_NEW_FILE",
                    "severity": "info",
                    "path": path,
                    "detail": f"'{path}' is new since last manifest baseline.",
                }
            )
    return findings


def _iter_doc_lines(rel: str):
    """Yield (line, in_fence) for a doc, tracking code-fence state. Skip fenced lines."""
    fenced = False
    for line in read_text(rel).splitlines():
        if FENCE_RE.search(line.strip()):
            fenced = not fenced
            continue
        if not fenced:
            yield line


def dead_references(inventory: set[str]) -> list[dict]:
    findings: list[dict] = []
    docs = sorted(
        p for p in inventory if p.endswith(".md") and (p.startswith("docs/") or p in DOC_ROOT_FILES)
    )
    for doc in docs:
        for line in _iter_doc_lines(doc):
            for m in PATH_REF_RE.findall(line):
                if m not in inventory:
                    findings.append(
                        {
                            "type": "DEAD_CODE_REF",
                            "severity": "medium",
                            "doc": doc,
                            "ref": m,
                            "detail": f"'{doc}' references '{m}' which no longer exists.",
                        }
                    )
    return findings


def broken_internal_links(docs: list[str], inventory: set[str]) -> list[dict]:
    findings: list[dict] = []
    root_resolved = REPO_ROOT.resolve()
    for doc in docs:
        base = Path(doc).parent
        text = read_text(doc)
        for target in LINK_RE.findall(text)[:200]:
            if target.startswith(("http://", "https://", "mailto:", "#", "tel:")):
                continue
            clean = target.split("#")[0].split("?")[0].strip()
            if not clean:
                continue
            resolved = (base / clean).resolve()
            try:
                rel = resolved.relative_to(root_resolved).as_posix()
            except ValueError:
                rel = str(resolved)
            exists = (
                resolved.is_file()
                or resolved.is_dir()
                or rel in inventory
                or (REPO_ROOT / rel).is_dir()
            )
            if not exists:
                findings.append(
                    {
                        "type": "DOC_BROKEN_LINK",
                        "severity": "medium",
                        "doc": doc,
                        "target": target,
                        "detail": f"'{doc}' links to inexistent '{target}'.",
                    }
                )
    return findings


def version_drift() -> list[dict]:
    findings: list[dict] = []
    m = re.search(r'requires-python\s*=\s*"([^"]+)"', read_text("pyproject.toml"))
    if not m:
        return findings
    lb = re.search(r"(\d+\.\d+)", m.group(1))
    if not lb:
        return findings
    authoritative = lb.group(1)

    def check(doc: str, pattern: str) -> None:
        for match in re.compile(pattern).finditer(read_text(doc)):
            claimed = match.group(1)
            if claimed != authoritative:
                findings.append(
                    {
                        "type": "DOC_VERSION_MISMATCH",
                        "severity": "high",
                        "doc": doc,
                        "claimed": claimed,
                        "authoritative": authoritative,
                        "detail": f"'{doc}' claims Python {claimed}; "
                        f"pyproject requires {authoritative}.",
                    }
                )

    # Patterns capture the full "3.X" literal (e.g. "3.13") so the comparison
    # against the authoritative pyproject value is exact, not minor-only.
    check("README.en.md", r"Python-(3\.\d+(?:\.\d+)?)(?:-blue)")
    check("README.en.md", r"\*\*Python (3\.\d+(?:\.\d+)?)\*\*")
    check("README.md", r"Python-(3\.\d+(?:\.\d+)?)\+")
    check("docs/index.md", r"\*\*Python (3\.\d+(?:\.\d+)?)\*\*")
    return findings


def release_inventory() -> list[dict]:
    out: list[dict] = []
    rel_dir = REPO_ROOT / "releases"
    if not rel_dir.is_dir():
        return out
    for d in sorted(rel_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        meta = d / ".meta.json"
        data: dict = {}
        if meta.is_file():
            try:
                data = json.loads(meta.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                data = {}
        cats = data.get("categories", [])
        out.append(
            {
                "dir": d.name,
                "name": data.get("name", d.name),
                "slug": data.get("slug", d.name),
                "features": data.get("total_features", 0),
                "categories": len(cats) if isinstance(cats, list) else 0,
                "release_id": int(data.get("release_id", 0) or 0),
            }
        )
    out.sort(key=lambda r: r["release_id"], reverse=True)
    return out


SEASON_ICON = {"spring": "🌸", "summer": "☀️", "winter": "❄️", "fall": "🍂", "autumn": "🍂"}


def release_table_header(locale: str = "pt") -> list[str]:
    if locale == "en":
        return ["| Release | Features | Categories | Status |", "| :--- | :---: | :---: | :---: |"]
    return ["| Release | Features | Categorias | Status |", "| :--- | :---: | :---: | :---: |"]


def release_table_rows(locale: str = "pt") -> list[str]:
    releases = release_inventory()
    cur, done = ("✅ Current", "✅ Complete") if locale == "en" else ("✅ Atual", "✅ Completo")
    rows: list[str] = []
    for i, rel in enumerate(releases):
        m = re.match(r"^(Spring|Summer|Winter|Fall|Autumn)\s+'(\d{2})$", rel["name"])
        season = rel["dir"].split("_")[0]
        icon = SEASON_ICON.get(season, "📦")
        if m:
            label = f"{icon} **{m.group(1)} '{m.group(2)}**"
        else:
            label = f"{icon} **{rel['name']}**"
        status = cur if i == 0 else done
        rows.append(f"| {label} | {rel['features']:,} | {rel['categories']} | {status} |")
    return rows


def release_table_drift(text: str, header_title: str, doc: str, locale: str = "pt") -> list[dict]:
    """Verify a locale-localised releases table matches releases/*.meta.json."""
    findings: list[dict] = []
    # Section header carries an emoji (e.g. "## 📋 Releases Disponíveis ...").
    header_re = re.compile(r"(?m)^##[^\n]*\b" + re.escape(header_title) + r"\b[^\n]*\n")
    hm = header_re.search(text)
    if not hm:
        findings.append(
            {
                "type": "RELEASE_TABLE_MISSING",
                "severity": "high",
                "doc": doc,
                "detail": f"'{doc}' has no '{header_title}' releases section.",
            }
        )
        return findings
    expected = release_table_rows(locale)
    table_re = re.compile(
        r"(?m)\n*\| Release[^\n]*\|[^\n]*\r?\n\|\s*:?-+:?\s*\|[^\n]*\r?\n(?:\|.*\r?\n)*"
    )
    tm = table_re.search(text, hm.end())
    if not tm:
        findings.append(
            {
                "type": "RELEASE_TABLE_MISSING",
                "severity": "high",
                "doc": doc,
                "detail": f"'{doc}' '{header_title}' section has no releases table.",
            }
        )
        return findings
    block = tm.group(0)
    actual = [
        s
        for s in (line.strip() for line in block.splitlines())
        if s.startswith("|") and "Release |" not in s and ":---" not in s
    ]
    if actual != expected:
        findings.append(
            {
                "type": "RELEASE_TABLE_STALE",
                "severity": "high",
                "doc": doc,
                "expected": expected,
                "detail": f"'{doc}' releases table stale vs releases/ metadata "
                f"({locale}); Winter '27 missing or feature counts drift.",
            }
        )
    return findings


def audit() -> dict:
    inventory = tracked_inventory()
    inv_set = set(inventory)
    manifest = load_manifest()
    findings: list[dict] = []

    findings += stale_manifest(inventory, manifest)
    findings += dead_references(inv_set)

    # Only real site pages are relevant for "not in nav"; generated release
    # notes, root docs, the auto-generated api/ stubs and private internal docs
    # are intentionally excluded to keep the finding actionable.
    site_docs = sorted(
        p
        for p in inv_set
        if p.endswith(".md")
        and p.startswith("docs/")
        and not p.startswith("docs/api/")
        and not p.startswith("docs/internal/")
    )
    _mk_nav, nav_set = parse_nav_docs(read_text("mkdocs.yml"))
    for missing in nav_missing_files(nav_set, inv_set):
        findings.append(
            {
                "type": "NAV_MISSING_FILE",
                "severity": "high",
                "doc": missing,
                "detail": f"mkdocs.yml nav references inexistent '{missing}'.",
            }
        )
    for orphan in docs_not_in_nav(site_docs, nav_set):
        findings.append(
            {
                "type": "DOC_NOT_IN_NAV",
                "severity": "medium",
                "doc": orphan,
                "detail": f"'{orphan}' exists but is absent from mkdocs nav.",
            }
        )

    findings += broken_internal_links(sorted(p for p in inv_set if p.endswith(".md")), inv_set)

    for mod in missing_api_evokers():
        findings.append(
            {
                "type": "MISSING_API_DOC",
                "severity": "medium",
                "source": mod["file"],
                "doc": mod["evoker"],
                "detail": f"'{mod['file']}' has no API evoker at '{mod['evoker']}'.",
            }
        )

    findings += version_drift()
    # Releases availability table is curated in BOTH locales (pt-BR docs home +
    # English README), each from the authoritative releases/*.meta.json.
    findings += release_table_drift(
        read_text("docs/index.md"), "Releases Disponíveis", "docs/index.md", "pt"
    )
    findings += release_table_drift(
        read_text("README.en.md"), "Available Releases", "README.en.md", "en"
    )

    report = {
        "mode": "audit",
        "repository_sha": head_sha(),
        "generated_at": datetime.now(UTC).isoformat(),
        "inventory_count": len(inventory),
        "src_modules": len(src_python_modules()),
        "existing_api_evokers": len(existing_api_evokers()),
        "releases": release_inventory(),
        "findings": findings,
    }
    return report


# --------------------------------------------------------------------------- #
# Reconciliation (deterministic, build-safe)
# --------------------------------------------------------------------------- #
def write_manifest() -> dict[str, str]:
    """(Re)write the documentation baseline manifest.

    Idempotent: if the tracked inventory, documentation map and HEAD SHA are
    unchanged since the last manifest, the file is left untouched so a stable
    repo produces zero reconciliation diff.  Only the stable fields are
    compared; the volatile ``generated_at`` timestamp is refreshed only when the
    baseline actually changed.
    """
    inventory = tracked_inventory()
    doc_map = build_documentation_map(inventory)
    existing = load_manifest()
    # Idempotency is content-based: the tracked inventory and documentation
    # map are the source of truth.  repository_sha is informational
    # ("generated against commit X") and is intentionally NOT part of the
    # staleness check -- otherwise every new commit would force a manifest
    # rewrite since HEAD always advances on commit.
    if existing.get("files") == inventory and existing.get("documentation_map") == doc_map:
        return {"manifest": "baseline unchanged (idempotent, no drift)", "changed": False}
    manifest = {
        "repository_sha": head_sha(),
        "generated_at": datetime.now(UTC).isoformat(),
        "files": inventory,
        "documentation_map": doc_map,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "manifest": f"regenerated baseline ({len(inventory)} files, "
        f"{len(doc_map)} map entries)",
        "changed": True,
    }


def fix_version_badges() -> list[str]:
    """Align Python version claims with pyproject requires-python."""
    m = re.search(r'requires-python\s*=\s*"([^"]+)"', read_text("pyproject.toml"))
    if not m:
        return []
    lb = re.search(r"(\d+\.\d+)", m.group(1))
    if not lb:
        return []
    ver = lb.group(1)
    actions: list[str] = []
    # ``ver`` is the full literal "3.13" (from pyproject requires-python).
    # Each pattern already consumes the "3." / space prefix, so the replacement
    # embeds the full version literal verbatim (avoids the "3.3.13" double-3 bug).
    specs = {
        "README.en.md": [
            (r"Python-3\.(\d+(?:\.\d+)?)(?:-blue)", f"Python-{ver}-blue"),
            (r"\*\*Python 3\.(\d+(?:\.\d+)?)\*\*", f"**Python {ver}**"),
        ],
        "README.md": [(r"Python-3\.(\d+(?:\.\d+)?)\+", f"Python-{ver}+")],
        # docs/index.md uses the same ``**Python 3.X**`` badge prose that
        # version_drift() audits — close the audit→reconcile gap so a stale
        # Python claim here is auto-fixed, not just flagged.
        "docs/index.md": [(r"\*\*Python 3\.(\d+(?:\.\d+)?)\*\*", f"**Python {ver}**")],
    }
    for doc, patterns in specs.items():
        txt = read_text(doc)
        new = txt
        for pat, repl in patterns:
            new = re.sub(pat, repl, new)
        if new != txt:
            write_file(doc, new)
            actions.append(f"updated {doc}: Python claim -> {ver}")
    return actions


def _upsert_release_table(doc: str, header_title: str, locale: str = "pt") -> list[str]:
    """Insert (or refresh) a locale-localised releases availability table.

    Keeps both locales current from releases/*.meta.json: the pt-BR docs home
    (``docs/index.md`` -> "Releases Disponíveis") and the English README
    (``README.en.md`` -> "Available Releases").  An existing table has only its
    rows refreshed (surrounding prose untouched); a missing table is inserted
    immediately under the section header.
    """
    txt = read_text(doc)
    if not txt:
        return []
    rows = release_table_rows(locale)
    header_lines = release_table_header(locale)
    header_re = re.compile(r"(?m)^##[^\n]*\b" + re.escape(header_title) + r"\b[^\n]*\n")
    hm = header_re.search(txt)
    if not hm:
        return []
    table_re = re.compile(
        r"(?m)\n*(\| Release[^\n]*\|[^\n]*\r?\n\|\s*:?-+:?\s*\|[^\n]*\r?\n)(?:\|.*\r?\n)*"
    )
    tm = table_re.search(txt, hm.end())
    built = "\n" + "\n".join(header_lines + rows) + "\n"
    if tm:
        block = tm.group(0)
        # Defensive guard: a legitimate table region is only "|" rows + blanks.
        # If any non-table, non-blank prose leaked into the match (regex
        # over-match, e.g. a stray (?ms)/DOTALL making ".*" cross newlines),
        # bail out -- never overwrite real content.
        if any(line.strip() and not line.lstrip().startswith("|") for line in block.splitlines()):
            return []
        new = txt[: tm.start()] + built + txt[tm.end() :]
    else:
        new = txt[: hm.end()] + built + txt[hm.end() :]
    if new != txt:
        write_file(doc, new)
        return [f"updated {doc}: {locale} releases table upserted ({len(rows)} releases)"]
    return []


def fix_release_table() -> list[str]:
    """Reconcile the releases availability table in both locales (pt-BR + en)."""
    actions: list[str] = []
    actions += _upsert_release_table("docs/index.md", "Releases Disponíveis", "pt")
    actions += _upsert_release_table("README.en.md", "Available Releases", "en")
    return actions


def add_missing_nav_entries() -> list[str]:
    """Wire orphan docs into mkdocs.yml nav under sensible, conservative sections."""
    mk = MKKDOCS_PATH
    text = read_text("mkdocs.yml")
    inv = set(tracked_inventory().keys())
    _, nav_set = parse_nav_docs(text)
    orphans = sorted(
        p for p in inv if p.endswith(".md") and p.startswith("docs/") and p not in nav_set
    )
    if not orphans:
        return []
    lines = text.splitlines(keepends=True)
    # Internal/agent docs are intentionally NOT promoted to the public site nav.
    plan = {
        "docs/SOURCE_SCHEMA.md": "  - Referências:",
        "docs/contribution/testing-strategy.md": "  - Contribuição:",
    }
    by_name = {ln.strip(): i for i, ln in enumerate(lines)}
    actions: list[str] = []

    def section_line(section: str) -> int:
        if section in by_name:
            return by_name[section]
        # append a new top-level nav section before the trailing `nav:` end
        insert_at = len(lines)
        lines.append(f"{section}\n")
        by_name[section] = insert_at
        return insert_at

    for orphan in sorted(orphans):
        section = plan.get(orphan)
        if section is None:
            continue
        target_doc = orphan.replace("docs/", "", 1)
        title = Path(target_doc).stem.replace("-", " ").replace("_", " ").title()
        leaf = f"    - {title}: {target_doc}\n"
        if orphan in nav_set:
            continue
        idx = section_line(section)
        # insert right after the section header line
        lines.insert(idx + 1, leaf)
        actions.append(f"added nav entry for {orphan}")
    if actions:
        mk.write_text("".join(lines), encoding="utf-8")
    return actions


def generate_api_stubs() -> list[str]:
    actions: list[str] = []
    for mod in missing_api_evokers():
        if (REPO_ROOT / mod["evoker"]).is_file():
            continue
        content = f"# {mod['title']}\n\n::: {mod['dotted']}\n"
        if write_file(mod["evoker"], content):
            actions.append(f"created {mod['evoker']} for {mod['file']}")
    return actions


def add_api_nav_entries() -> list[str]:
    """Add any new docs/api/*.md (excluding index) to the mkdocs API Reference nav."""
    text = read_text("mkdocs.yml")
    _, nav_set = parse_nav_docs(text)
    lines = text.splitlines(keepends=True)
    api_docs = sorted(
        p.relative_to(REPO_ROOT).as_posix()
        for p in DOCS_ROOT.glob("api/*.md")
        if p.name != "index.md" and p.relative_to(REPO_ROOT).as_posix() not in nav_set
    )
    if not api_docs:
        return []
    # find the "- API Reference:" section and insert leaves right after it
    actions: list[str] = []
    anchor = None
    for i, ln in enumerate(lines):
        if re.match(r"^\s*- API Reference:\s*$", ln):
            anchor = i
            break
    if anchor is None:
        return []
    for i, doc in enumerate(api_docs):
        rel = doc.replace("docs/api/", "api/")
        title = Path(rel).stem.replace("-", " ").replace("_", " ").title()
        leaf = f"    - {title}: {rel}\n"
        lines.insert(anchor + 1 + i, leaf)
        actions.append(f"added nav entry {rel}")
    MKKDOCS_PATH.write_text("".join(lines), encoding="utf-8")
    return actions


def generate_api_index_table() -> list[str]:
    path = "docs/api/index.md"
    txt = read_text(path)
    start = txt.find("## Módulos Documentados")
    if start < 0:
        start = len(txt)
    nxt = txt.find("\n## ", start + 1)
    if nxt < 0:
        nxt = len(txt)
    head = txt[:start]
    tail = txt[nxt:]
    # Read from the filesystem so freshly-created (uncommitted) stubs are
    # visible immediately -- the index must reflect what lives on disk, not
    # what git has recorded.
    evokers = sorted(
        p.relative_to(REPO_ROOT).as_posix()
        for p in DOCS_ROOT.glob("api/*.md")
        if p.name != "index.md"
    )
    rows = ["| Módulo | Evocador |", "|--------|----------|"]
    for ev in evokers:
        rel = ev.replace("docs/api/", "")
        stem = rel[:-3]
        rows.append(f"| `src.{stem.replace('-', '.')}` | [`{rel}`]({rel}) |")
    table = "\n".join(rows)
    new = head + "## Módulos Documentados\n\n" + table + "\n" + tail
    if new != txt:
        write_file(path, new)
        return [f"updated {path}: module table ({len(evokers)} entries)"]
    return []


def _tree_lines(root_rel: str, depth: int, prefix: str) -> list[str]:
    root_path = REPO_ROOT / root_rel
    if not root_path.is_dir():
        return []
    entries: list[str] = []
    try:
        items = sorted(root_path.iterdir(), key=lambda p: (p.is_file(), p.name))
    except OSError:
        return entries
    for i, item in enumerate(items):
        if item.name.startswith(".") or item.name == "__pycache__":
            continue
        last = i == len(items) - 1
        branch = "└── " if last else "├── "
        if item.is_dir():
            entries.append(f"{prefix}{branch}{item.name}/")
            if depth > 1:
                entries += _tree_lines(f"{root_rel}/{item.name}", depth - 1, prefix + "    ")
        elif item.suffix == ".py" and item.name != "__init__.py":
            entries.append(f"{prefix}{branch}{item.name}")
    return entries


_TOP_LEVEL_COMMENTS = {
    "releases": "Artefatos Markdown por release",
    "tests": "Suíte pytest",
    "docs": "Documentação MkDocs",
    "k8s": "Manifestos Kubernetes",
    "mkdocs.yml": "Configuração MkDocs",
    "pyproject.toml": "Configuração do projeto",
    "uv.lock": "Lockfile determinístico",
    ".github": "Workflows e scripts do GitHub",
    "scripts": "Scripts utilitários",
    "Dockerfile": "Imagem Docker de runtime",
    "CHANGELOG.md": "Changelog do projeto",
    "README.md": "Readme em português",
    "README.en.md": "Readme em inglês",
    "SECURITY.md": "Política de segurança",
    "CONTRIBUTING.md": "Guia de contribuição",
    "AGENTS.md": "Diretrizes para agentes de código",
}

# Top-level names that exist on disk but are infra/caches and should NOT
# appear in the curated project tree shown to humans.
_TREE_SKIP_DIRS = frozenset(
    {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "site",
        "node_modules",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "stubs",
        "assets",
        "data",
        ".hooks",
        "src",
    }
)
_TREE_SKIP_FILES = frozenset(
    {
        ".env",
        ".markdownlintignore",
        ".markdownlint.json",
        ".pre-commit-config.yaml",
        ".gitignore",
        ".dockerignore",
        "audit-fix.patch",
    }
)


def _top_level_tree_lines() -> list[str]:
    """Dynamically enumerate real top-level repo entries for the directory tree.

    Replaces the previously hardcoded list so the tree never goes stale as
    files/dirs are added. Curated inline comments are attached where a
    meaningful label exists; new entries are emitted without a comment rather
    than silently omitted. Never raises.
    """
    try:
        items = sorted(
            (p for p in REPO_ROOT.iterdir()),
            key=lambda p: (p.is_file(), p.name),
        )
    except OSError:
        return []
    visible: list[str] = []
    for p in items:
        if p.name in _TREE_SKIP_DIRS or p.name in _TREE_SKIP_FILES:
            continue
        visible.append(p.name)
    if not visible:
        return []
    out: list[str] = []
    for i, name in enumerate(visible):
        last = i == len(visible) - 1
        branch = "└── " if last else "├── "
        is_dir = (REPO_ROOT / name).is_dir()
        label = f"{name}{'/' if is_dir else ''}"
        comment = _TOP_LEVEL_COMMENTS.get(name)
        if comment:
            out.append(f"  {branch}{label:<26} # {comment}")
        else:
            out.append(f"  {branch}{label}")
    return out


def fix_directory_tree() -> list[str]:
    path = "docs/index.md"
    txt = read_text(path)
    if not txt:
        return []
    lines = ["Salesforce-WebDev/"]
    lines += _tree_lines("src", depth=2, prefix="  ")
    lines += _top_level_tree_lines()
    tree = "\n".join(lines)
    pattern = re.compile(r"(?ms)^```text\n(?:\s*\n)?Salesforce-WebDev/\n.*?```\n")
    replacement = f"```text\n\n{tree}\n```\n"
    new, _n = pattern.subn(replacement, txt, count=1)
    if new != txt:
        write_file(path, new)
        return [f"updated {path}: directory tree refreshed"]
    return []


def strip_dead_refs() -> list[str]:
    """Remove references to files/asset paths that no longer exist in the repo.

    Applied to *prose* lines only (code fences preserved).  Two deterministic
    transforms:

    1. Markdown links/images ``[text](./rel/path)`` (or ``![alt](...)``) whose
       relative target resolves to nothing on disk and is absent from the git
       inventory are *unwrapped* to plain ``text`` / ``alt``.  This is the
       deterministic equivalent of "remove the reference": the human-readable
       label survives, the broken hyperlink is dropped -- never guessed/redirected.
       External (http/https/mailto/tel:), anchor (``#``) and query (``?``)
       targets are skipped, so valid links are never touched.

    2. Bare code-path mentions (``src/foo.py``, ``scripts/x.sh``,
       ``.github/workflows/y.yml``) that do not exist in the inventory are
       shortened to their stem so prose stays readable without pointing at a
       dead path.

    Idempotent: a second run is a no-op.  Never raises.
    """
    inventory = set(tracked_inventory().keys())
    root_resolved = REPO_ROOT.resolve()
    docs = sorted(p for p in inventory if p.endswith(".md"))
    actions: list[str] = []
    for doc in docs:
        text = read_text(doc)
        if not text:
            continue
        base = Path(doc).parent
        lines = text.splitlines(keepends=True)
        fenced = False
        out: list[str] = []
        changed = False
        for line in lines:
            if FENCE_RE.search(line.strip()):
                fenced = not fenced
                out.append(line)
                continue
            if fenced:
                out.append(line)
                continue
            cur = line
            # (1) unwrap dead markdown links/images (track offset delta)
            delta = 0
            for m in MD_LINK_RE.finditer(line):
                target = m.group(2)
                if (
                    not target
                    or target.startswith(("http://", "https://", "mailto:", "tel:", "#"))
                    or target.endswith((":", "::"))
                ):
                    continue
                clean = target.split("#")[0].split("?")[0].strip()
                if not clean:
                    continue
                try:
                    resolved = (REPO_ROOT / base / clean).resolve()
                    rel = resolved.relative_to(root_resolved).as_posix()
                    exists = resolved.is_file() or resolved.is_dir() or rel in inventory
                except (ValueError, OSError):
                    exists = False
                if not exists:
                    replacement = m.group(1) or clean
                    cur = cur[: m.start() + delta] + replacement + cur[m.end() + delta :]
                    delta += len(replacement) - (m.end() - m.start())
                    changed = True
            # (2) shorten bare dead code-path mentions in whatever remains
            for ref in PATH_REF_RE.findall(cur):
                if ref not in inventory:
                    cur = cur.replace(ref, ref.split("/")[-1])
                    changed = True
            out.append(cur)
        if changed:
            if write_file(doc, "".join(out)):
                actions.append(f"unwrapped dead links / shortened dead paths in {doc}")
    return actions


def reconcile(generate_api: bool = True) -> int:
    actions: list[str] = []
    actions += fix_version_badges()
    actions += fix_release_table()
    actions += fix_directory_tree()
    actions += add_missing_nav_entries()
    if generate_api:
        actions += generate_api_stubs()
        actions += add_api_nav_entries()
        actions += generate_api_index_table()
    actions += strip_dead_refs()
    # Regenerate manifest LAST so it captures every reconciled file.
    # Only record the action when the baseline actually changed (idempotent).
    manifest_info = write_manifest()
    if manifest_info.get("changed"):
        actions.append(manifest_info["manifest"])

    print(f"\nDocumentation reconciliation complete: {len(actions)} action(s)")
    for a in actions:
        print(f"  - {a}")
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _write_report(report: dict) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_scan() -> int:
    inv = tracked_inventory()
    report = {
        "repository_sha": head_sha(),
        "inventory_count": len(inv),
        "src_modules": [m["file"] for m in src_python_modules()],
        "api_evokers": sorted(existing_api_evokers()),
        "releases": [r["dir"] for r in release_inventory()],
        "documentation_map": build_documentation_map(inv),
    }
    _write_report(report)
    print(
        f"scan: {len(inv)} tracked files | src_modules={len(report['src_modules'])} "
        f"| api_evokers={len(report['api_evokers'])} | releases={len(report['releases'])}"
    )
    return 0


def cmd_audit() -> int:
    report = audit()
    _write_report(report)
    counts = Counter(f["type"] for f in report["findings"])
    print(
        f"audit: {len(report['findings'])} findings | inventory={report['inventory_count']} "
        f"src_modules={report['src_modules']} api_evokers={report['existing_api_evokers']} "
        f"releases={len(report['releases'])}"
    )
    for kind, n in sorted(counts.items()):
        print(f"  {kind}: {n}")
    print(f"\nDrift report written to {REPORT_PATH}")
    return 0


def cmd_manifest() -> int:
    info = write_manifest()
    print(f"[manifest] {info['manifest']}")
    return 0


def cmd_reconcile(generate_api: bool) -> int:
    return reconcile(generate_api=generate_api)


def main(argv: list[str] | None = None) -> int:
    argv = list(argv) if argv is not None else sys.argv[1:]
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    cmd = argv[0]
    if cmd not in ("scan", "audit", "reconcile", "manifest"):
        print(
            "usage: docs_sync_engine.py [scan|audit|reconcile[--no-api-stubs]|manifest]",
            file=sys.stderr,
        )
        return 2
    generate_api = "--no-api-stubs" not in argv
    try:
        if cmd == "scan":
            return cmd_scan()
        if cmd == "audit":
            return cmd_audit()
        if cmd == "manifest":
            return cmd_manifest()
        if cmd == "reconcile":
            return cmd_reconcile(generate_api)
    except Exception as exc:  # engine must never crash CI
        print(f"❌ docs_sync_engine {cmd} failed (safe abort): {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
