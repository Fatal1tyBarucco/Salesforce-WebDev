"""Contract validator + hardened sync engine tests (ADR-012).

Every test runs against an isolated fixture repository (tmp_path + git init)
via the REPO_ROOT environment override, so the real repository is never
touched.  The drift simulations required by the Definition of Done are
covered here: artifact removal -> ÓRFÃO -> reconcile removes page/nav with
audit history; artifact addition -> OMITO -> reconcile creates the evoker.

The helper ``_sync`` mirrors the CI order: reconcile -> git add -A ->
manifest refresh -> git add -A (the contract validates the staged index).
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / ".github" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def _stage(root: Path) -> None:
    _git(root, "add", "-A")


def _sync(root: Path, eng) -> None:
    """reconcile + stage + manifest refresh + stage (CI gate order)."""
    eng.reconcile()
    _stage(root)
    eng.write_manifest()
    _stage(root)


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Minimal synchronized fixture repository + reloaded engine/contract."""
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")

    (root / "src" / "pkg").mkdir(parents=True)
    (root / "src" / "pkg" / "__init__.py").write_text('"""Package."""\n', encoding="utf-8")
    (root / "src" / "pkg" / "mod.py").write_text('"""Modulo de exemplo."""\n', encoding="utf-8")
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")
    (root / ".github" / "scripts").mkdir(parents=True)
    (root / ".github" / "scripts" / "docs_sync_engine.py").write_text(
        '"""Engine stub."""\n', encoding="utf-8"
    )
    (root / "releases" / "winter_27").mkdir(parents=True)
    (root / "releases" / "winter_27" / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Winter '27",
                "slug": "winter-27",
                "release_id": 264,
                "total_features": 10,
                "categories": [{}, {}],
            }
        ),
        encoding="utf-8",
    )
    for locale in ("pt_BR", "en_US"):
        loc_dir = root / "releases" / "winter_27" / locale
        loc_dir.mkdir(parents=True)
        (loc_dir / "feature.md").write_text("# Feature\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        '[project]\nrequires-python = ">=3.14,<3.15"\n', encoding="utf-8"
    )

    docs = root / "docs"
    (docs / "api").mkdir(parents=True)
    (docs / "api" / "pkg-mod.md").write_text("# Mod\n\n::: src.pkg.mod\n", encoding="utf-8")
    (docs / "api" / "index.md").write_text("# API\n", encoding="utf-8")
    (docs / "index.md").write_text("# Home\n\n## Releases Disponíveis\n", encoding="utf-8")
    (docs / "en").mkdir(parents=True)
    (docs / "en" / "index.md").write_text("# English\n", encoding="utf-8")
    (docs / ".last-processed-ref").write_text("0" * 40 + "\n", encoding="utf-8")
    (docs / "catalog.md").write_text(
        "# Catalogo\n\n"
        "Cobre `.github/workflows/ci.yml`, `.github/scripts/docs_sync_engine.py`, "
        "tests/, releases/, k8s/ e prompts/.\n",
        encoding="utf-8",
    )
    (root / "mkdocs.yml").write_text(
        "site_name: Test\n"
        "nav:\n"
        "  - Home: index.md\n"
        "  - English: en/index.md\n"
        "  - Catalogo: catalog.md\n"
        "  - API Reference:\n"
        "    - Mod: api/pkg-mod.md\n"
        "    - Visão Geral: api/index.md\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "# README\n\n"
        "![Python](https://img.shields.io/badge/Python-3.14+-blue)\n\n"
        "## Releases Disponíveis\n",
        encoding="utf-8",
    )
    (root / "README.en.md").write_text(
        "# README\n\n"
        "![Python](https://img.shields.io/badge/Python-3.14+-blue)\n\n"
        "## Available Releases\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("REPO_ROOT", str(root))
    monkeypatch.setenv("DRIFT_REPORT", str(tmp_path / "drift.json"))
    monkeypatch.setenv("CONTRACT_REPORT", str(tmp_path / "contract.json"))
    eng = importlib.import_module("docs_sync_engine")
    importlib.reload(eng)
    contract = importlib.import_module("docs_contract")
    importlib.reload(contract)

    # Bring the fixture to a synchronized baseline (tables + manifest).
    _stage(root)
    _sync(root, eng)
    _git(root, "commit", "-q", "-m", "baseline")
    return root, eng, contract


def test_clean_fixture_passes_contract(repo) -> None:
    _root, _eng, contract = repo
    items, _counts = contract.run_checks()
    assert items == [], [(i.kind, i.path, i.detail) for i in items]
    assert contract.main(["validate"]) == 0


def test_addition_is_omito_then_reconciled(repo) -> None:
    """DoD drift simulation: new artifact -> OMITO -> sync documents it."""
    root, eng, contract = repo
    (root / "src" / "pkg" / "novo.py").write_text('"""Novo modulo."""\n', encoding="utf-8")
    _stage(root)
    items, _ = contract.run_checks()
    kinds = {(i.state, i.kind) for i in items}
    assert (contract.STATE_OMITO, "MISSING_API_DOC") in kinds
    assert contract.main(["validate"]) == 1

    _sync(root, eng)
    assert (root / "docs" / "api" / "pkg-novo.md").is_file()
    assert "api/pkg-novo.md" in (root / "mkdocs.yml").read_text(encoding="utf-8")
    items, _ = contract.run_checks()
    assert items == []
    assert contract.main(["validate"]) == 0


def test_removal_is_orfao_then_removed_with_history(repo) -> None:
    """DoD drift simulation: deleted artifact -> ÓRFÃO -> sync removes docs."""
    root, eng, contract = repo
    (root / "src" / "pkg" / "mod.py").unlink()
    _stage(root)
    items, _ = contract.run_checks()
    assert any(i.state == contract.STATE_ORFAO and i.kind == "ORPHAN_API_DOC" for i in items)
    assert contract.main(["validate"]) == 1

    _sync(root, eng)
    assert not (root / "docs" / "api" / "pkg-mod.md").exists()
    assert "api/pkg-mod.md" not in (root / "mkdocs.yml").read_text(encoding="utf-8")
    manifest = json.loads(
        (root / "docs" / ".documentation-manifest.json").read_text(encoding="utf-8")
    )
    removals = manifest["removals"]
    record = next(r for r in removals if r["path"] == "docs/api/pkg-mod.md")
    assert record["removed_at"] and record["commit"] and record["reason"]
    items, _ = contract.run_checks()
    assert items == []

    # History survives subsequent regenerations (append-only audit trail).
    _sync(root, eng)
    manifest2 = json.loads(
        (root / "docs" / ".documentation-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest2["removals"] == removals


def test_orphan_page_fails_strict_contract(repo) -> None:
    root, _eng, contract = repo
    (root / "docs" / "lost.md").write_text("# Perdida\n", encoding="utf-8")
    _stage(root)
    items, _ = contract.run_checks()
    assert any(i.kind == "ORPHAN_PAGE" and i.path == "docs/lost.md" for i in items)
    assert contract.main(["validate"]) == 1


def test_dead_nav_entry_removed_with_history(repo) -> None:
    root, eng, contract = repo
    mk = root / "mkdocs.yml"
    mk.write_text(mk.read_text(encoding="utf-8") + "  - Fantasma: gone.md\n", encoding="utf-8")
    _stage(root)
    items, _ = contract.run_checks()
    assert any(i.kind == "NAV_MISSING_FILE" for i in items)
    _sync(root, eng)
    assert "gone.md" not in mk.read_text(encoding="utf-8")
    manifest = json.loads(
        (root / "docs" / ".documentation-manifest.json").read_text(encoding="utf-8")
    )
    assert any(r["path"] == "docs/gone.md" for r in manifest["removals"])
    items, _ = contract.run_checks()
    assert items == []


def test_package_evoker_is_not_orphan(repo) -> None:
    root, eng, _contract = repo
    (root / "docs" / "api" / "pkg.md").write_text("# Pkg\n\n::: src.pkg\n", encoding="utf-8")
    assert eng.evoker_target_exists("docs/api/pkg.md") is True
    assert "docs/api/pkg.md" not in eng.orphan_api_evokers()


def test_excluded_surfaces_are_not_orphans(repo) -> None:
    root, _eng, contract = repo
    for surface in ("ai-generated", "internal", "plans"):
        d = root / "docs" / surface
        d.mkdir(parents=True, exist_ok=True)
        (d / "page.md").write_text("# X\n", encoding="utf-8")
    _stage(root)
    items, _ = contract.run_checks()
    assert not any(i.kind == "ORPHAN_PAGE" for i in items)


def test_generated_page_whitelisted_in_nav(repo) -> None:
    root, _eng, contract = repo
    mk = root / "mkdocs.yml"
    mk.write_text(
        mk.read_text(encoding="utf-8") + "  - Arvore: reference/code-tree.md\n",
        encoding="utf-8",
    )
    _stage(root)
    items, _ = contract.run_checks()
    assert not any(i.kind == "NAV_MISSING_FILE" for i in items)


def test_stale_manifest_sha_is_obsoleto(repo) -> None:
    root, eng, contract = repo
    (root / "docs" / "catalog.md").write_text("# Catalogo v2\n", encoding="utf-8")
    _stage(root)
    items, _ = contract.run_checks()
    assert any(i.kind == "MANIFEST_STALE_SHA" for i in items)
    _sync(root, eng)
    items, _ = contract.run_checks()
    assert not any(i.kind == "MANIFEST_STALE_SHA" for i in items)


def test_parity_divergence_detected(repo) -> None:
    root, _eng, contract = repo
    en = root / "README.en.md"
    en.write_text(
        en.read_text(encoding="utf-8").replace("Python-3.14+", "Python-3.13+"),
        encoding="utf-8",
    )
    items = contract.check_parity()
    assert any(i.kind == "PYTHON_VERSION_PARITY" for i in items)
    assert contract.main(["parity"]) == 1


def test_report_emits_classified_json(repo) -> None:
    root, _eng, contract = repo
    (root / "docs" / "lost.md").write_text("# Perdida\n", encoding="utf-8")
    _stage(root)
    assert contract.main(["report"]) == 0
    report = json.loads(contract.REPORT_PATH.read_text(encoding="utf-8"))
    assert report["state_counts"]["ÓRFÃO"] >= 1
    assert report["ok_counts"]["src_modules"] == 1
    assert all("action" in item for item in report["items"])


def test_reconcile_idempotent_on_clean_repo(repo) -> None:
    root, eng, _contract = repo
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file() and ".git" not in p.parts}
    eng.reconcile()
    after = {p: p.read_bytes() for p in root.rglob("*") if p.is_file() and ".git" not in p.parts}
    changed = [str(p.relative_to(root)) for p in after if before.get(p) != after[p]] + [
        str(p.relative_to(root)) for p in before if p not in after
    ]
    assert before == after, f"changed: {changed}"


def test_repo_index_lists_documentable_artifacts(repo) -> None:
    root, eng, _contract = repo
    index = (root / eng.REPO_INDEX_REL).read_text(encoding="utf-8")
    assert "src/pkg/mod.py" in index
    assert ".github/workflows/ci.yml" in index
    assert "Não editar manualmente" in index


def test_untracked_new_page_nav_survives_reconcile(repo) -> None:
    """Regression: nav targets created in-run (untracked) are never removed."""
    root, eng, _contract = repo
    (root / "docs" / "fresh.md").write_text("# Fresh\n", encoding="utf-8")
    mk = root / "mkdocs.yml"
    mk.write_text(mk.read_text(encoding="utf-8") + "  - Fresh: fresh.md\n", encoding="utf-8")
    eng.reconcile()  # fresh.md intentionally NOT staged
    assert "fresh.md" in mk.read_text(encoding="utf-8")
    assert (root / "docs" / "fresh.md").is_file()


def test_release_artifact_parity_divergence(repo) -> None:
    """DoD5: bilingual release artifact sets must stay at parity."""
    root, _eng, contract = repo
    (root / "releases" / "winter_27" / "en_US" / "feature.md").unlink()
    _stage(root)
    items = contract.check_parity()
    assert any(i.kind == "RELEASE_ARTIFACT_PARITY" for i in items)
    assert contract.main(["parity"]) == 1


def test_missing_en_surface_divergence(repo) -> None:
    root, _eng, contract = repo
    (root / "docs" / "en" / "index.md").unlink()
    _stage(root)
    items = contract.check_parity()
    assert any(i.kind == "MISSING_EN_SURFACE" for i in items)


def test_report_includes_automation_coverage(repo) -> None:
    """Fase 1.4: report cruza HEAD com docs(sync) e .last-processed-ref."""
    _root, _eng, contract = repo
    assert contract.main(["report"]) == 0
    report = json.loads(contract.REPORT_PATH.read_text(encoding="utf-8"))
    coverage = report["automation_coverage"]
    assert coverage["last_processed_ref"] == "0" * 40
    assert "last_docs_sync_commit" in coverage
    assert coverage["head"]


def test_usage_error_exit_code(repo) -> None:
    _root, _eng, contract = repo
    assert contract.main([]) == 2
    assert contract.main(["bogus"]) == 2
