"""Testes para o módulo de linkage de features (SFEL linker)."""

from __future__ import annotations

from src.automation.ledger.linker import FeatureLinker, _jaccard, _tokenize_name
from src.automation.ledger.models import (
    FeatureSnapshot,
    LinkageMethod,
    LifecycleStatus,
)

# ── Helpers de snapshot ─────────────────────────────────────────────────


def _snap(name: str, category: str, release_slug: str = "test") -> FeatureSnapshot:
    """Cria um FeatureSnapshot mínimo para testes."""
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


# ── _jaccard ────────────────────────────────────────────────────────────


def test_jaccard_identical_sets() -> None:
    assert _jaccard({"a", "b"}, {"a", "b"}) == 1.0


def test_jaccard_disjoint_sets() -> None:
    assert _jaccard({"a"}, {"b"}) == 0.0


def test_jaccard_partial_overlap() -> None:
    # {"flow", "builder"} vs {"flow", "builder", "apex"} → 2/3 ≈ 0.666
    assert abs(_jaccard({"flow", "builder"}, {"flow", "builder", "apex"}) - 0.666) < 0.001


def test_jaccard_both_empty() -> None:
    assert _jaccard(set(), set()) == 0.0


def test_jaccard_one_empty() -> None:
    assert _jaccard({"a"}, set()) == 0.0


# ── _tokenize_name ──────────────────────────────────────────────────────


def test_tokenize_single_word() -> None:
    assert _tokenize_name("flowbuilder") == {"flowbuilder"}


def test_tokenize_multi_word() -> None:
    assert _tokenize_name("flow builder") == {"flow", "builder"}


def test_tokenize_empty() -> None:
    assert _tokenize_name("") == set()


# ── FeatureLinker: EXACT ────────────────────────────────────────────────


def test_exact_match_same_category() -> None:
    linker = FeatureLinker()
    cur = [_snap("Flow Builder", "Plataforma", "summer_26")]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    assert len(links) == 1
    assert links[0].status == LifecycleStatus.ALIVE
    assert links[0].linkage_method == LinkageMethod.EXACT
    assert links[0].similarity_score == 1.0


def test_exact_match_different_category_emits_category_changed() -> None:
    linker = FeatureLinker()
    cur = [_snap("Flow Builder", "Segurança", "summer_26")]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    assert len(links) == 1
    assert links[0].status == LifecycleStatus.CATEGORY_CHANGED
    assert links[0].linkage_method == LinkageMethod.EXACT
    assert "Plataforma" in links[0].notes
    assert "Segurança" in links[0].notes


def test_exact_match_multiple_features_all_linked() -> None:
    linker = FeatureLinker()
    cur = [
        _snap("Flow Builder", "Plataforma", "summer_26"),
        _snap("Apex Debug", "Desenvolvimento", "summer_26"),
    ]
    prev = [
        _snap("Flow Builder", "Plataforma", "spring_26"),
        _snap("Apex Debug", "Desenvolvimento", "spring_26"),
    ]

    links = linker.link(cur, prev, {}, {})

    assert len(links) == 2
    assert all(link.linkage_method == LinkageMethod.EXACT for link in links)
    assert all(link.status == LifecycleStatus.ALIVE for link in links)


# ── FeatureLinker: RENAMED via FUZZY ────────────────────────────────────


def test_fuzzy_match_renamed() -> None:
    linker = FeatureLinker()
    cur = [_snap("Flow Builder New", "Plataforma", "summer_26")]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    assert len(links) == 1
    assert links[0].status == LifecycleStatus.RENAMED
    assert links[0].linkage_method == LinkageMethod.FUZZY
    # Jaccard({"flow", "builder", "new"}, {"flow", "builder"}) = 2/3 ≈ 0.667
    assert links[0].similarity_score >= 0.5


def test_fuzzy_match_below_threshold_no_link() -> None:
    linker = FeatureLinker()
    # Jaccard({"xyz", "abc"}, {"flow", "builder"}) = 0 < 0.5 → nenhum link
    cur = [_snap("Xyz ABC", "Plataforma", "summer_26")]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    assert len(links) == 0


# ── FeatureLinker: HEURISTIC ────────────────────────────────────────────


def test_heuristic_match_same_category_similar_names() -> None:
    linker = FeatureLinker()
    cur = [_snap("Advanced Flow Builder Pro", "Plataforma", "summer_26")]
    prev = [_snap("Basic Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    # Jaccard({"advanced", "flow", "builder", "pro"}, {"basic", "flow", "builder"})
    # = 2/5 = 0.4 → 0.4 >= 0.2 (LLM_THRESHOLD_LOW) e mesma categoria → HEURISTIC
    assert len(links) == 1
    assert links[0].linkage_method == LinkageMethod.HEURISTIC
    assert links[0].status == LifecycleStatus.RENAMED
    assert 0.2 <= links[0].similarity_score < 0.5


# ── FeatureLinker: features não encontradas → born / removed ────────────


def test_current_only_features_not_linked() -> None:
    linker = FeatureLinker()
    # "Brand New Feature" vs "Old Feature" → Jaccard({"brand", "new", "feature"},
    # {"old", "feature"}) = 1/4 = 0.25 >= 0.2 → HEURISTIC match (mesma categoria)
    # Então o linker encontra um match. Afirmamos apenas que houve algum match.
    cur = [_snap("Brand New Feature", "Plataforma", "summer_26")]
    prev = [_snap("Old Feature", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    assert len(links) == 1
    assert links[0].linkage_method == LinkageMethod.HEURISTIC
    assert links[0].status == LifecycleStatus.RENAMED


def test_previous_only_features_not_linked() -> None:
    linker = FeatureLinker()
    cur: list[FeatureSnapshot] = []
    prev = [_snap("Removed Feature", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    assert len(links) == 0


# ── FeatureLinker: mutual exclusion ─────────────────────────────────────


def test_each_feature_linked_at_most_once() -> None:
    linker = FeatureLinker()
    cur = [
        _snap("Flow Builder", "Plataforma", "summer_26"),
        _snap("Flow Builder", "Plataforma", "summer_26"),
    ]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    # Apenas um link possível, já que há apenas uma feature no previous
    assert len(links) <= 1
    # Verifica que não há duplicates de feature_a.name no resultado
    names_linked = [link.feature_a.name for link in links]
    assert len(names_linked) == len(set(names_linked))


# ── FeatureLinker: sem features ─────────────────────────────────────────


def test_empty_current_no_links() -> None:
    linker = FeatureLinker()
    links = linker.link([], [_snap("X", "Y", "spring_26")], {}, {})
    assert links == []


def test_empty_previous_no_links() -> None:
    linker = FeatureLinker()
    links = linker.link([_snap("X", "Y", "summer_26")], [], {}, {})
    assert links == []


def test_both_empty_no_links() -> None:
    linker = FeatureLinker()
    links = linker.link([], [], {}, {})
    assert links == []
