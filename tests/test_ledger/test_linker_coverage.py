"""Testes de cobertura para branches do linker não atingidas pelos testes existentes."""

from __future__ import annotations

from src.automation.ledger.linker import FeatureLinker
from src.automation.ledger.models import (
    FeatureSnapshot,
    LinkageMethod,
    LifecycleStatus,
)


def _snap(name: str, category: str, release_slug: str = "test") -> FeatureSnapshot:
    return FeatureSnapshot(
        name=name,
        release_slug=release_slug,
        category=category,
        snippet="",
        feature_type="other",
        impact="low",
        first_seen="2026-01-01T00:00:00+00:00",
        last_seen="2026-01-01T00:00:00+00:00",
    )


# ── Linker: passo 1 (EXACT) com categoria igual ─────────────────────────

def test_exact_match_covered_by_linker_single_pair() -> None:
    """Cobre a branch de EXACT link com categoria igual."""
    linker = FeatureLinker()
    cur = [_snap("Flow Builder", "Plataforma", "summer_26")]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    assert len(links) == 1
    assert links[0].linkage_method == LinkageMethod.EXACT
    assert links[0].status == LifecycleStatus.ALIVE
    # A linha 96 do linker (continue de used_current) é atingida aqui


# ── Linker: passo 1 já marca used_current → segunda iteração pula ───────

def test_exact_match_second_iteration_skipped_via_used_current() -> None:
    """Cobre a linha 96 (continue por used_current) do passo EXACT."""
    linker = FeatureLinker()
    # Duas features idênticas no current, uma no previous
    cur = [
        _snap("Flow Builder", "Plataforma", "summer_26"),
        _snap("Flow Builder", "Plataforma", "summer_26"),
    ]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    # Só o primeiro é linkado; o segundo é pulado via continue de used_current
    assert len(links) == 1
    assert links[0].linkage_method == LinkageMethod.EXACT


# ── Linker: passo 2 (CATEGORY_CHANGED) ────────────────────────────────────

def test_category_changed_link_created() -> None:
    """Cobre a branch CATEGORY_CHANGED do passo 2."""
    linker = FeatureLinker()
    cur = [_snap("Flow Builder", "Segurança", "summer_26")]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    assert len(links) == 1
    assert links[0].status == LifecycleStatus.CATEGORY_CHANGED
    # O passo 2 cria link com linkage_method EXACT mas status CATEGORY_CHANGED


# ── Linker: continuar no passo 3 (FUZZY) quando used_previous ─────────────

def test_fuzzy_step_continue_via_used_previous() -> None:
    """Cobre o continue de used_previous no passo FUZZY.

    A primeira feature do previous é consumida pelo EXACT do Flow Builder.
    A segunda feature (Apex Debug) tenta fuzzy contra a segunda do current
    mas não há match → continue.
    """
    linker = FeatureLinker()
    # summer_26: Flow Builder EXACT cuida do primeiro pair.
    # Apex Debug Plus tenta fuzzy contra Apex Debug (spring_26).
    cur = [
        _snap("Flow Builder", "Plataforma", "summer_26"),
        _snap("Apex Debug Plus", "Desenvolvimento", "summer_26"),
    ]
    prev = [
        _snap("Flow Builder", "Plataforma", "spring_26"),
        _snap("Apex Debug", "Desenvolvimento", "spring_26"),
    ]

    links = linker.link(cur, prev, {}, {})

    # Flow Builder → EXACT ALIVE; Apex Debug Plus → FUZZY RENAMED
    assert len(links) == 2
    methods = {link.linkage_method for link in links}
    assert LinkageMethod.EXACT in methods
    assert LinkageMethod.FUZZY in methods


# ── Linker: links.append no passo FUZZY (linha 148->144) ─────────────────

def test_fuzzy_link_appended() -> None:
    """Cobre a branch de append no passo FUZZY (linha 148->144 do linker)."""
    linker = FeatureLinker()
    cur = [_snap("Flow Builder New", "Plataforma", "summer_26")]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    # Jaccard({"flow", "builder", "new"}, {"flow", "builder"}) = 2/3 ≈ 0.667 >= 0.5
    # → FUZZY match → append
    assert len(links) == 1
    assert links[0].linkage_method == LinkageMethod.FUZZY
    assert links[0].status == LifecycleStatus.RENAMED


# ── Linker: passo 4 (HEURISTIC) — append (linha 148 do passo 4) ──────────

def test_heuristic_step_appended() -> None:
    """Cobre a branch de append no passo HEURISTIC."""
    linker = FeatureLinker()
    cur = [_snap("Advanced Flow Builder Pro", "Plataforma", "summer_26")]
    prev = [_snap("Basic Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    # Jaccard 2/5 = 0.4 >= 0.2 (LLM_THRESHOLD_LOW) e mesma categoria
    # → append no passo HEURISTIC
    assert len(links) == 1
    assert links[0].linkage_method == LinkageMethod.HEURISTIC
    assert links[0].status == LifecycleStatus.RENAMED


# ── Linker: condição de Jaccard >= threshold não atendida no passo FUZZY ──

def test_fuzzy_step_no_match_below_threshold() -> None:
    """Cobre o caso onde FUZZY não encontra match (nenhum link append)."""
    linker = FeatureLinker()
    cur = [_snap("Xyz ABC", "Plataforma", "summer_26")]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    # Jaccard = 0 < 0.5 → nenhum link
    assert len(links) == 0


# ── Linker: condição best_pi is not None no passo HEURISTIC ───────────────

def test_heuristic_step_no_match_below_llm_threshold() -> None:
    """Cobre o caso onde HEURISTIC não encontra par (best_pi is None)."""
    linker = FeatureLinker()
    # Jaccard({"xyz"}, {"abc"}) = 0 < 0.2 → best_pi permanece None
    cur = [_snap("Xyz", "Plataforma", "summer_26")]
    prev = [_snap("ABC", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    assert len(links) == 0
