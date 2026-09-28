"""Testes de validação Pydantic para os modelos do SFEL."""

from __future__ import annotations

import pytest

from pydantic import ValidationError  # type: ignore[import-not-found]

from src.automation.ledger.models import (
    FeatureHistoryEntry,
    FeatureLink,
    FeatureSnapshot,
    LedgerDiff,
    LedgerStats,
    LifecycleStatus,
    LinkageMethod,
)

# ── FeatureSnapshot ─────────────────────────────────────────────────────


def test_feature_snapshot_valid() -> None:
    fs = FeatureSnapshot(
        name="Flow Builder",
        release_slug="summer_26",
        category="Plataforma",
        snippet="Algum trecho",
        feature_type="new_feature",
        impact="high",
        first_seen="2026-01-01T00:00:00+00:00",
        last_seen="2026-01-01T00:00:00+00:00",
    )
    assert fs.name == "Flow Builder"
    assert fs.impact == "high"


def test_feature_snapshot_name_required() -> None:
    with pytest.raises(ValidationError):
        FeatureSnapshot(
            name="",
            release_slug="summer_26",
            category="Plataforma",
            snippet="",
            feature_type="other",
            impact="low",
            first_seen="2026-01-01T00:00:00+00:00",
            last_seen="2026-01-01T00:00:00+00:00",
        )


def test_feature_snapshot_slug_required() -> None:
    with pytest.raises(ValidationError):
        FeatureSnapshot(
            name="X",
            release_slug="",
            category="Plataforma",
            snippet="",
            feature_type="other",
            impact="low",
            first_seen="2026-01-01T00:00:00+00:00",
            last_seen="2026-01-01T00:00:00+00:00",
        )


def test_feature_snapshot_snippet_default_empty() -> None:
    fs = FeatureSnapshot(
        name="X",
        release_slug="summer_26",
        category="Plataforma",
        snippet="",
        feature_type="other",
        impact="low",
        first_seen="2026-01-01T00:00:00+00:00",
        last_seen="2026-01-01T00:00:00+00:00",
    )
    assert fs.snippet == ""


# ── LifecycleStatus ─────────────────────────────────────────────────────


def test_lifecycle_status_enum_values() -> None:
    assert LifecycleStatus.BORN == "born"
    assert LifecycleStatus.ALIVE == "alive"
    assert LifecycleStatus.RENAMED == "renamed"
    assert LifecycleStatus.CATEGORY_CHANGED == "category_changed"
    assert LifecycleStatus.DEPRECATED == "deprecated"
    assert LifecycleStatus.REMOVED == "removed"


def test_lifecycle_status_from_string() -> None:
    assert LifecycleStatus("born") == LifecycleStatus.BORN
    assert LifecycleStatus("alive") == LifecycleStatus.ALIVE


# ── LinkageMethod ───────────────────────────────────────────────────────


def test_linkage_method_enum_values() -> None:
    assert LinkageMethod.EXACT == "exact"
    assert LinkageMethod.FUZZY == "fuzzy"
    assert LinkageMethod.LLM == "llm"
    assert LinkageMethod.HEURISTIC == "heuristic"


# ── FeatureLink ─────────────────────────────────────────────────────────


def test_feature_link_valid() -> None:
    a = FeatureSnapshot(
        name="Flow Builder",
        release_slug="summer_26",
        category="Plataforma",
        snippet="",
        feature_type="other",
        impact="low",
        first_seen="2026-01-01T00:00:00+00:00",
        last_seen="2026-01-01T00:00:00+00:00",
    )
    b = FeatureSnapshot(
        name="Flow Builder",
        release_slug="spring_26",
        category="Plataforma",
        snippet="",
        feature_type="other",
        impact="low",
        first_seen="2026-01-01T00:00:00+00:00",
        last_seen="2026-01-01T00:00:00+00:00",
    )
    fl = FeatureLink(
        feature_a=a,
        feature_b=b,
        status=LifecycleStatus.ALIVE,
        linkage_method=LinkageMethod.EXACT,
        similarity_score=1.0,
        notes="match exato",
    )
    assert fl.status == LifecycleStatus.ALIVE
    assert fl.similarity_score == 1.0


def test_feature_link_similarity_bound_low() -> None:
    a = FeatureSnapshot(
        name="X",
        release_slug="summer_26",
        category="Y",
        snippet="",
        feature_type="other",
        impact="low",
        first_seen="2026-01-01T00:00:00+00:00",
        last_seen="2026-01-01T00:00:00+00:00",
    )
    b = FeatureSnapshot(
        name="X",
        release_slug="spring_26",
        category="Y",
        snippet="",
        feature_type="other",
        impact="low",
        first_seen="2026-01-01T00:00:00+00:00",
        last_seen="2026-01-01T00:00:00+00:00",
    )
    # similarity_score = 0.0 é válido (bound: ge=0.0)
    fl = FeatureLink(
        feature_a=a,
        feature_b=b,
        status=LifecycleStatus.ALIVE,
        linkage_method=LinkageMethod.FUZZY,
        similarity_score=0.0,
        notes="",
    )
    assert fl.similarity_score == 0.0


def test_feature_link_similarity_bound_high() -> None:
    a = FeatureSnapshot(
        name="X",
        release_slug="summer_26",
        category="Y",
        snippet="",
        feature_type="other",
        impact="low",
        first_seen="2026-01-01T00:00:00+00:00",
        last_seen="2026-01-01T00:00:00+00:00",
    )
    b = FeatureSnapshot(
        name="X",
        release_slug="spring_26",
        category="Y",
        snippet="",
        feature_type="other",
        impact="low",
        first_seen="2026-01-01T00:00:00+00:00",
        last_seen="2026-01-01T00:00:00+00:00",
    )
    fl = FeatureLink(
        feature_a=a,
        feature_b=b,
        status=LifecycleStatus.ALIVE,
        linkage_method=LinkageMethod.EXACT,
        similarity_score=1.0,
        notes="",
    )
    assert fl.similarity_score == 1.0


# ── LedgerDiff ──────────────────────────────────────────────────────────


def test_ledger_diff_minimal_valid() -> None:
    ld = LedgerDiff(
        current_slug="summer_26",
        previous_slug="spring_26",
        current_name="Summer '26",
        previous_name="Spring '26",
        born=[],
        alive=[],
        renamed=[],
        category_changed=[],
        deprecated=[],
        removed=[],
        total_current_features=0,
        total_previous_features=0,
        generated_at="2026-01-01T00:00:00+00:00",
    )
    assert ld.current_slug == "summer_26"
    assert ld.total_current_features == 0


def test_ledger_diff_slugs_required() -> None:
    with pytest.raises(ValidationError):
        LedgerDiff(
            current_slug="",
            previous_slug="spring_26",
            current_name="X",
            previous_name="Y",
            born=[],
            alive=[],
            renamed=[],
            category_changed=[],
            deprecated=[],
            removed=[],
            total_current_features=0,
            total_previous_features=0,
            generated_at="2026-01-01T00:00:00+00:00",
        )


def test_ledger_diff_feature_counts_non_negative() -> None:
    ld = LedgerDiff(
        current_slug="summer_26",
        previous_slug="spring_26",
        current_name="X",
        previous_name="Y",
        born=[],
        alive=[],
        renamed=[],
        category_changed=[],
        deprecated=[],
        removed=[],
        total_current_features=0,
        total_previous_features=0,
        generated_at="2026-01-01T00:00:00+00:00",
    )
    assert ld.total_current_features >= 0


# ── LedgerStats ─────────────────────────────────────────────────────────


def test_ledger_stats_default_zero() -> None:
    ls = LedgerStats(
        current_slug="summer_26",
        previous_slug="spring_26",
    )
    assert ls.born_count == 0
    assert ls.alive_count == 0
    assert ls.removed_count == 0
    assert ls.linkage_method_counts == {}


def test_ledger_stats_populated() -> None:
    ls = LedgerStats(
        current_slug="summer_26",
        previous_slug="spring_26",
        total_features_current=10,
        total_features_previous=8,
        born_count=3,
        alive_count=5,
        renamed_count=1,
        category_changed_count=0,
        deprecated_count=0,
        removed_count=2,
        linkage_method_counts={"exact": 5, "fuzzy": 1},
        unlinked_previous=["old feature"],
        unlinked_current=["new feature"],
    )
    assert ls.born_count == 3
    assert ls.alive_count == 5
    assert ls.linkage_method_counts["exact"] == 5


# ── FeatureHistoryEntry ─────────────────────────────────────────────────


def test_feature_history_entry_default_status() -> None:
    fhe = FeatureHistoryEntry(
        feature_name="Flow Builder",
        entries=[],
        current_status=LifecycleStatus.ALIVE,
        total_releases_seen=0,
        removed_in=None,
    )
    assert fhe.current_status == LifecycleStatus.ALIVE
    assert fhe.removed_in is None


def test_feature_history_entry_with_entries() -> None:
    entry = FeatureSnapshot(
        name="Flow Builder",
        release_slug="summer_26",
        category="Plataforma",
        snippet="",
        feature_type="other",
        impact="low",
        first_seen="2026-01-01T00:00:00+00:00",
        last_seen="2026-01-01T00:00:00+00:00",
    )
    fhe = FeatureHistoryEntry(
        feature_name="Flow Builder",
        entries=[entry],
        current_status=LifecycleStatus.ALIVE,
        total_releases_seen=1,
        removed_in=None,
    )
    assert fhe.total_releases_seen == 1
    assert len(fhe.entries) == 1
    assert fhe.entries[0].release_slug == "summer_26"


def test_feature_history_entry_removed_in_set() -> None:
    fhe = FeatureHistoryEntry(
        feature_name="Legacy Feature",
        entries=[],
        current_status=LifecycleStatus.REMOVED,
        total_releases_seen=0,
        removed_in="spring_26",
    )
    assert fhe.removed_in == "spring_26"
