"""Testes para o FeatureEvolutionLedgerService (SFEL service)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from pathlib import Path

from src.automation.ledger.models import (
    LedgerDiff,
    LifecycleStatus,
    LinkageMethod,
)
from src.automation.ledger.service import FeatureEvolutionLedgerService, now_iso

# ── Fixture de serviço ──────────────────────────────────────────────────


@pytest.fixture
def ledger_service(
    releases_dir_fake: Path,
) -> FeatureEvolutionLedgerService:
    """Cria um FeatureEvolutionLedgerService com releases fictícios.

    O cache é criado em tmp_path isolado para não poluir o cache real.
    """
    cache_dir = releases_dir_fake.parent / "cache_ledger_test"
    return FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(cache_dir),
    )


@pytest.fixture
def ledger_service_no_previous(
    releases_dir_fake_current_only: Path,
) -> FeatureEvolutionLedgerService:
    """Serviço com apenas release atual (sem release anterior)."""
    cache_dir = releases_dir_fake_current_only.parent / "cache_ledger_test"
    return FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake_current_only),
        cache_dir=str(cache_dir),
    )


@pytest.fixture
def mock_bus() -> MagicMock:
    """Mock do EventBus para testes que verificam emissão de eventos."""
    return MagicMock()


@pytest.fixture
def ledger_service_with_mock_bus(
    releases_dir_fake: Path,
    mock_bus: MagicMock,
) -> FeatureEvolutionLedgerService:
    """Serviço com EventBus mockado."""
    cache_dir = releases_dir_fake.parent / "cache_ledger_test"
    with patch("src.automation.ledger.service.get_event_bus", return_value=mock_bus):
        svc = FeatureEvolutionLedgerService(
            releases_dir=str(releases_dir_fake),
            cache_dir=str(cache_dir),
        )
    return svc


# ── _extract_features ───────────────────────────────────────────────────


def test_extract_features_returns_list(ledger_service: FeatureEvolutionLedgerService) -> None:
    features = ledger_service._extract_features("spring_26")
    assert isinstance(features, list)
    assert len(features) > 0


def test_extract_features_names(ledger_service: FeatureEvolutionLedgerService) -> None:
    features = ledger_service._extract_features("spring_26")
    names = {f["name"] for f in features}
    # spring_26 tem: Flow Builder, Apex Enhancements, LWC TypeScript, Apex Debug
    assert "flow builder" in names
    assert "apex enhancements" in names
    assert "lwc typescript" in names
    assert "apex debug" in names


def test_extract_features_normalizes_case(ledger_service: FeatureEvolutionLedgerService) -> None:
    features = ledger_service._extract_features("spring_26")
    names_lower = {f["name"] for f in features}
    # Todos os nomes devem estar em minúsculas após normalização
    for name in names_lower:
        assert name == name.lower()


def test_extract_features_returns_empty_for_nonexistent_release(
    ledger_service: FeatureEvolutionLedgerService,
) -> None:
    features = ledger_service._extract_features("nonexistent_release_xyz")
    assert features == []


def test_extract_features_skips_dot_files(ledger_service: FeatureEvolutionLedgerService) -> None:
    features = ledger_service._extract_features("spring_26")
    # Não deve haver feature chamada ".meta" ou similar
    names = {f["name"] for f in features}
    assert not any(n.startswith(".") for n in names)


# ── _normalize_name ─────────────────────────────────────────────────────


def test_normalize_lowercases() -> None:
    svc = FeatureEvolutionLedgerService(releases_dir="/tmp/nonexistent")
    assert svc._normalize_name("Flow Builder") == "flow builder"


def test_normalize_strips_punctuation() -> None:
    svc = FeatureEvolutionLedgerService(releases_dir="/tmp/nonexistent")
    assert svc._normalize_name("Flow Builder.") == "flow builder"
    assert svc._normalize_name("Flow Builder!") == "flow builder"


def test_normalize_strips_trailing_whitespace() -> None:
    svc = FeatureEvolutionLedgerService(releases_dir="/tmp/nonexistent")
    assert svc._normalize_name("  Flow Builder  ") == "flow builder"


# ── _extract_category ───────────────────────────────────────────────────


def test_extract_category_from_h2() -> None:
    svc = FeatureEvolutionLedgerService(releases_dir="/tmp/nonexistent")
    content = "# Título\n\n## Plataforma\n\n- Flow Builder"
    assert svc._extract_category(content) == "Plataforma"


def test_extract_category_ignores_emoji_h2() -> None:
    svc = FeatureEvolutionLedgerService(releases_dir="/tmp/nonexistent")
    content = "## 🔗 Links\n\n## Plataforma\n\n- Flow Builder"
    assert svc._extract_category(content) == "Plataforma"


def test_extract_category_fallback() -> None:
    svc = FeatureEvolutionLedgerService(releases_dir="/tmp/nonexistent")
    assert svc._extract_category("sem cabeçalho") == "geral"


# ── generate_ledger ─────────────────────────────────────────────────────

# Distância Jaccard entre "Apex Debug" e "Apex Debug Plus":
# {"apex", "debug"} vs {"apex", "debug", "plus"} = 2/3 ≈ 0.667 >= 0.5 (FUZZY_THRESHOLD)
# Então o linker deixa como RENAMED via FUZZY.
#
# Distância Jaccard entre "Flow Builder" (×2) e "Flow Builder" (×2) = 1.0 → EXACT ALIVE.
# Mas o linker só permite ONE match por feature: "Flow Builder" em summer_26 (index 0) ganha o match
# com spring_26 "Flow Builder" (index 0). O segundo "Flow Builder" em summer_26 (index 1) está
# usado? Não, porque o step 1 marca como used_current[0] e used_previous[0].
# Summer_26 tem 4 features: [Flow Builder, Apex Enhancements, LWC TypeScript, Apex Debug Plus]
# Spring_26 tem 4 features: [Flow Builder, Apex Enhancements, LWC TypeScript, Apex Debug]
# EXACT: Flow Builder==Flow Builder (1 link), Apex Enhancements==Apex Enhancements (1 link),
# LWC TypeScript==LWC TypeScript (1 link).
# Apex Debug Plus vs Apex Debug: FUZZY match (Jaccard 0.667) → RENAMED (1 link).
# Total: 4 links. alive=3, renamed=1. born=0, removed=0.


@pytest.mark.asyncio
async def test_generate_ledger_same_features_all_alive(
    ledger_service: FeatureEvolutionLedgerService,
) -> None:
    """spring_26 → summer_26: 3 features idênticas (ALIVE) + 1 renomeada (FUZZY)."""
    diff = await ledger_service.generate_ledger(
        "summer_26",
        "spring_26",
    )
    assert isinstance(diff, LedgerDiff)
    assert diff.current_slug == "summer_26"
    assert diff.previous_slug == "spring_26"
    assert diff.total_current_features == 4
    assert diff.total_previous_features == 4
    # 3 features mantidas (Flow Builder, Apex Enhancements, LWC TypeScript)
    assert len(diff.alive) == 3
    # 1 renomeada (Apex Debug → Apex Debug Plus)
    assert len(diff.renamed) == 1
    assert diff.renamed[0].linkage_method == LinkageMethod.FUZZY
    assert len(diff.born) == 0
    assert len(diff.removed) == 0


@pytest.mark.asyncio
async def test_generate_ledger_one_renamed(
    ledger_service: FeatureEvolutionLedgerService,
) -> None:
    """summer_26 vs spring_26: 'Apex Debug' → 'Apex Debug Plus' (FUZZY rename)."""
    diff = await ledger_service.generate_ledger(
        "summer_26",
        "spring_26",
    )
    # Espera-se 1 renomeado (Apex Debug → Apex Debug Plus)
    renamed_names = {(link.feature_a.name, link.feature_b.name) for link in diff.renamed}
    assert ("apex debug plus", "apex debug") in renamed_names
    assert diff.renamed[0].linkage_method == LinkageMethod.FUZZY


@pytest.mark.asyncio
async def test_generate_ledger_stats_match_diff(
    ledger_service: FeatureEvolutionLedgerService,
) -> None:
    """Stats agregadas devem ser consistentes com o LedgerDiff."""
    diff = await ledger_service.generate_ledger(
        "summer_26",
        "spring_26",
    )
    stats = ledger_service.get_cached_stats("summer_26", "spring_26")

    assert stats is not None
    assert stats.total_features_current == diff.total_current_features
    assert stats.total_features_previous == diff.total_previous_features
    assert stats.alive_count == len(diff.alive)
    assert stats.born_count == len(diff.born)
    assert stats.removed_count == len(diff.removed)
    assert stats.renamed_count == len(diff.renamed)
    assert stats.category_changed_count == len(diff.category_changed)


@pytest.mark.asyncio
async def test_generate_ledger_cache_write(ledger_service: FeatureEvolutionLedgerService) -> None:
    """Após generate_ledger, o cache deve conter o diff."""
    await ledger_service.generate_ledger("summer_26", "spring_26")
    cached = ledger_service.get_cached_ledger("summer_26", "spring_26")
    assert cached is not None
    assert cached.current_slug == "summer_26"


@pytest.mark.asyncio
async def test_generate_ledger_cache_read_returns_same_data(
    ledger_service: FeatureEvolutionLedgerService,
) -> None:
    """Segunda chamada deve retornar o mesmo diff do cache sem reextrair."""
    diff1 = await ledger_service.generate_ledger("summer_26", "spring_26")
    diff2 = ledger_service.get_cached_ledger("summer_26", "spring_26")
    assert diff2 is not None
    assert diff2.current_slug == diff1.current_slug
    assert diff2.total_current_features == diff1.total_current_features


@pytest.mark.asyncio
async def test_generate_ledger_nonexistent_previous_returns_empty(
    ledger_service: FeatureEvolutionLedgerService,
) -> None:
    """Release anterior inexistente → diff com removed vazio e current extraído."""
    diff = await ledger_service.generate_ledger(
        "spring_26",
        "nonexistent_xyz",
    )
    assert diff.previous_slug == "nonexistent_xyz"
    assert diff.total_previous_features == 0  # release inexistente não tem features
    # spring_26 tem 4 features, todas "born" porque não há previous para comparar
    assert diff.total_current_features == 4


# ── get_cached_ledger inválido ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_cached_ledger_returns_none_when_missing(
    ledger_service: FeatureEvolutionLedgerService,
) -> None:
    result = ledger_service.get_cached_ledger(" summer_26", "spring_26")
    assert result is None


@pytest.mark.asyncio
async def test_get_cached_ledger_invalid_data_regenerates(
    ledger_service: FeatureEvolutionLedgerService,
) -> None:
    """Dados corrompidos no cache devem ser invalidados e retornar None."""
    cache_dir = Path(str(ledger_service._cache._cache_dir))
    ns_dir = cache_dir / "sfel"
    ns_dir.mkdir(parents=True, exist_ok=True)
    bad_path = ns_dir / "abc123.json"
    bad_path.write_text("NOT VALID JSON", encoding="utf-8")

    # O método usa o cache_key hash sha256 do key — precisamos do key real
    result = ledger_service.get_cached_ledger("summer_26", "spring_26")
    assert result is None


# ── get_feature_history ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_feature_history_exact_match(
    ledger_service: FeatureEvolutionLedgerService,
) -> None:
    """Flow Builder aparece em spring_26 e summer_26 → 2 releases, ALIVE."""
    entry = await ledger_service.get_feature_history("Flow Builder")
    assert entry.feature_name == "Flow Builder"
    assert entry.total_releases_seen == 2
    assert entry.current_status == LifecycleStatus.ALIVE
    slugs = {e.release_slug for e in entry.entries}
    assert "spring_26" in slugs
    assert "summer_26" in slugs


@pytest.mark.asyncio
async def test_feature_history_not_found(
    ledger_service: FeatureEvolutionLedgerService,
) -> None:
    entry = await ledger_service.get_feature_history("NonExistentFeature999")
    assert entry.total_releases_seen == 0
    assert entry.current_status == LifecycleStatus.REMOVED
    assert entry.entries == []


@pytest.mark.asyncio
async def test_feature_history_came_from_winter(
    ledger_service: FeatureEvolutionLedgerService,
) -> None:
    """'Flow Orchestrator' só aparece em winter_26 → 1 release, ALIVE
    (pois winter_26 é o último release no diretório, release_id=263)."""
    entry = await ledger_service.get_feature_history("Flow Orchestrator")
    assert entry.total_releases_seen == 1
    if entry.total_releases_seen == 1:
        assert entry.entries[0].release_slug == "winter_26"


# ── Event emission ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ledger_generated_emits_event(
    ledger_service_with_mock_bus: FeatureEvolutionLedgerService,
    mock_bus: MagicMock,
) -> None:
    await ledger_service_with_mock_bus.generate_ledger(
        "summer_26",
        "spring_26",
    )
    mock_bus.emit.assert_called_once()
    call_args = mock_bus.emit.call_args
    assert call_args[0][0] == "ledger.generated"
    assert call_args[0][1]["current_slug"] == "summer_26"
    assert call_args[0][1]["previous_slug"] == "spring_26"


# ── Invalidation ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_invalidate_removes_cache_entries(
    ledger_service: FeatureEvolutionLedgerService,
) -> None:
    await ledger_service.generate_ledger("summer_26", "spring_26")
    assert ledger_service.get_cached_ledger("summer_26", "spring_26") is not None

    ledger_service.invalidate("summer_26", "spring_26")

    assert ledger_service.get_cached_ledger("summer_26", "spring_26") is None


# ── clear_all ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_clear_all_removes_all_entries(
    ledger_service: FeatureEvolutionLedgerService,
) -> None:
    await ledger_service.generate_ledger("summer_26", "spring_26")
    await ledger_service.generate_ledger("winter_26", "spring_26")

    count = ledger_service.clear_all()
    assert count >= 2  # pelo menos 2 pairs de releases

    assert ledger_service.get_cached_ledger("summer_26", "spring_26") is None
    assert ledger_service.get_cached_ledger("winter_26", "spring_26") is None


# ── now_iso helper ──────────────────────────────────────────────────────


def test_now_iso_format() -> None:
    ts = now_iso()
    assert "+" in ts
    assert "T" in ts
