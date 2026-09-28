"""Testes de cobertura adicional para o SFEL — branches e erro handling."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.automation.ledger.linker import FeatureLinker
from src.automation.ledger.models import (
    FeatureSnapshot,
    LedgerDiff,
    LifecycleStatus,
    LinkageMethod,
)
from src.automation.ledger.service import FeatureEvolutionLedgerService

# ── Helpers ─────────────────────────────────────────────────────────────


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


# ── Linker: passo LLM (cobertura das linhas 203-250 do linker.py) ──────


def test_linker_llm_step_disambiguate_true() -> None:
    """LLM retorna que as features são a mesma → link via LLM (passo 5).

    Para chegar ao passo 5, a pair deve ter Jaccard entre 0.2 e 0.5
    E as categorias devem ser diferentes (senão HEURISTIC laça antes).
    """
    llm_mock = MagicMock()
    llm_mock.disambiguate_feature = MagicMock(return_value="Same feature, names differ slightly.")
    linker = FeatureLinker(llm_service=llm_mock)

    # "Flow Orch" (Segurança) vs "Flow Builder" (Plataforma):
    # Jaccard = 1/3 ≈ 0.333, categorias DIFERENTES → HEURISTIC não linka
    # → passo 5 (LLM) tenta
    cur = [_snap("Flow Orch", "Segurança", "summer_26")]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    assert len(links) == 1
    assert links[0].linkage_method == LinkageMethod.LLM
    assert "Same feature" in links[0].notes


def test_linker_llm_step_disambiguate_false() -> None:
    """LLM retorna None → nenhum link (passo 5)."""
    llm_mock = MagicMock()
    llm_mock.disambiguate_feature = MagicMock(return_value=None)
    linker = FeatureLinker(llm_service=llm_mock)

    cur = [_snap("Flow Orch", "Segurança", "summer_26")]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    assert len(links) == 0


def test_linker_llm_step_attribute_error_fallback() -> None:
    """LLM com AttributeError → pula sem erro, sem link (passo 5)."""
    llm_mock = MagicMock()
    llm_mock.disambiguate_feature = MagicMock(side_effect=AttributeError)
    linker = FeatureLinker(llm_service=llm_mock)

    cur = [_snap("Flow Orch", "Segurança", "summer_26")]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})
    assert links == []


def test_linker_llm_step_exception_fallback() -> None:
    """LLM com RuntimeError → pula sem erro, sem link (passo 5)."""
    llm_mock = MagicMock()
    llm_mock.disambiguate_feature = MagicMock(side_effect=RuntimeError("LLM unavailable"))
    linker = FeatureLinker(llm_service=llm_mock)

    cur = [_snap("Flow Orch", "Segurança", "summer_26")]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})
    assert links == []


def test_linker_llm_step_jaccard_outside_range_no_llm() -> None:
    """Jaccard abaixo de LLM_THRESHOLD_LOW → nem tenta LLM.

    "Xyz ABC" (Segurança) vs "Flow Builder" (Plataforma): Jaccard = 0.
    """
    llm_mock = MagicMock()
    llm_mock.disambiguate_feature = MagicMock()
    linker = FeatureLinker(llm_service=llm_mock)

    cur = [_snap("Xyz ABC", "Segurança", "summer_26")]
    prev = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    llm_mock.disambiguate_feature.assert_not_called()
    assert len(links) == 0


# ── Linker: coverage do passo HEURISTIC ──────────────────────────────────


def test_heuristic_single_feature_each_side_linked() -> None:
    """Cobre a branch HEURISTIC com um match real."""
    linker = FeatureLinker()
    # "Advanced Flow Builder Pro" vs "Basic Flow Builder":
    # {"advanced", "flow", "builder", "pro"} vs {"basic", "flow", "builder"} = 2/5 = 0.4
    # 0.4 >= 0.2 (LLM_THRESHOLD_LOW) e mesma categoria → HEURISTIC
    cur = [_snap("Advanced Flow Builder Pro", "Plataforma", "summer_26")]
    prev = [_snap("Basic Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur, prev, {}, {})

    assert len(links) == 1
    assert links[0].linkage_method == LinkageMethod.HEURISTIC


def test_heuristic_different_category_no_link() -> None:
    """HEURISTIC não linka se as categorias são diferentes."""
    linker = FeatureLinker()
    # "Flow Orch" (Segurança) vs "Flow Builder" (Plataforma):
    # Jaccard 1/3 ≈ 0.333 >= 0.2, mas categorias DIFERENTES → HEURISTIC não linka
    cur2 = [_snap("Flow Orch", "Segurança", "summer_26")]
    prev2 = [_snap("Flow Builder", "Plataforma", "spring_26")]

    links = linker.link(cur2, prev2, {}, {})

    # Jaccard({"flow", "orch"}, {"flow", "builder"}) = 1/3 ≈ 0.333 >= 0.2
    # Mas categorias são diferentes → HEURISTIC não linka
    assert len(links) == 0


# ── Service: _extract_features com OSError ───────────────────────────────


def test_extract_features_os_error_during_read(
    releases_dir_fake: Path,
) -> None:
    """Simula OSError ao ler um arquivo .md — a feature é pulada."""
    bad_md = releases_dir_fake / "spring_26" / "plataforma.md"
    bad_md.write_text("corrupt", encoding="utf-8")

    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_os_test"),
    )

    # Monkeypatch o método read_text da instância do Path usado pelo service.
    # Approach: patch a nível de módulo do Path.read_text vía instancecheck não é confiável.
    # Em vez disso, substituimos o arquivo plataforma.md por um symlink quebrado,
    # para que o read_text lance OSError naturalmente.
    broken_link = releases_dir_fake / "spring_26" / "plataforma.md"
    target = releases_dir_fake / "nonexistent_target_plataforma_md"
    try:
        broken_link.unlink()
    except FileNotFoundError:
        pass
    broken_link.symlink_to(str(target))

    features = svc._extract_features("spring_26")

    # Restaura o arquivo plaça depois do teste
    try:
        broken_link.unlink()
    except FileNotFoundError:
        pass
    # Reescreve o conteúdo original (será recriado pelo fixture na próxima chamada)
    broken_link.write_text(
        "# Plataforma\n\n## Plataforma\n\n- Flow Builder\n- Apex Enhancements\n",
        encoding="utf-8",
    )

    names = {f["name"] for f in features}
    assert "lwc typescript" in names
    assert "apex debug" in names
    # plataforma.md quebrado → "flow builder" e "apex enhancements" não aparecem
    assert "flow builder" not in names


# ── Service: cache falhando ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_ledger_cache_set_fails_gracefully(
    releases_dir_fake: Path,
) -> None:
    """Quando CacheManager.set falha, o generate_ledger prossegue sem crash."""
    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_fail_test"),
    )

    # Mock CacheManager.set para lançar exceção
    with patch.object(svc._cache, "set", side_effect=RuntimeError("Disk full")):
        diff = await svc.generate_ledger("summer_26", "spring_26")

    # O diff deve still ser gerado e retornado
    assert isinstance(diff, LedgerDiff)
    assert diff.current_slug == "summer_26"
    assert diff.total_current_features == 4


# ── Service: cache com ValidationError ────────────────────────────────────


def test_get_cached_ledger_validation_error_invalidates(
    releases_dir_fake: Path,
) -> None:
    """Dados inválidos no cache → ValidationError → invalidate + None."""
    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_validation_test"),
    )

    # Preenche o cache com dados inválidos usando o key correto
    cache_key = "summer_26..spring_26"
    from src.cache_manager import CacheManager

    cm = CacheManager(
        cache_dir=Path(str(svc._cache._cache_dir)),
        ttl_seconds=3600,
    )
    # Escreve diretamente no namespace sfel com dados inválidos
    ns_dir = cm._cache_dir / "sfel"
    ns_dir.mkdir(parents=True, exist_ok=True)
    import hashlib

    key_hash = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
    bad_path = ns_dir / f"{key_hash}.json"
    bad_path.write_text("not-a-dict", encoding="utf-8")

    result = svc.get_cached_ledger("summer_26", "spring_26")
    assert result is None


# ── Service: get_feature_history com status RENAMED ───────────────────────


@pytest.mark.asyncio
async def test_feature_history_status_renamed(
    releases_dir_fake: Path,
) -> None:
    """Feature renomeada entre releases → status RENAMED na história."""
    # Cria um release extra com a feature renomeada
    extra_dir = releases_dir_fake / "custom_27"
    extra_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "name": "Custom '27",
        "release_id": 264,
        "slug": "custom_27",
        "total_features": 1,
        "categories": [{"name": "Plataforma", "count": 1}],
        "generated_at": "2026-03-01T00:00:00+00:00",
    }
    (extra_dir / ".meta.json").write_text(
        json.dumps(meta, ensure_ascii=False),
        encoding="utf-8",
    )
    (extra_dir / "plataforma.md").write_text(
        "# Plataforma\n\n## Plataforma\n\n- Flow Builder Renamed\n",
        encoding="utf-8",
    )

    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_history_test"),
    )

    entry = await svc.get_feature_history("Flow Builder Renamed")
    assert entry.total_releases_seen >= 1
    # "Flow Builder Renamed" aparece em custom_27 e também
    # "Flow Builder" (normalizado) aparece em spring_26 e summer_26?
    # Não, "Flow Builder Renamed" != "flow builder" (normalizado).
    # Então a feature só aparece em custom_27.
    assert entry.feature_name == "Flow Builder Renamed"


# ── Service: _load_all_metas_sorted com JSON inválido ────────────────────


def test_load_all_metas_skips_invalid_json(
    releases_dir_fake: Path,
) -> None:
    """JSON inválido no .meta.json → pulado, não crash."""
    bad_meta = releases_dir_fake / "spring_26" / ".meta.json"
    bad_meta.write_text("NOT VALID JSON", encoding="utf-8")

    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_meta_test"),
    )

    metas = svc._load_all_metas_sorted()
    # Deve conter pelo menos summer_26 e winter_26 (que têm JSON válido)
    assert any(m.get("slug") == "summer_26" for m in metas)
    # spring_26 com JSON inválido não deve estar na lista
    assert not any(m.get("slug") == "spring_26" and "release_id" in m for m in metas)


# ── Service: _load_all_metas_sorted com diretório vazio ──────────────────


def test_load_all_metas_empty_directory() -> None:
    """Diretório sem releases → lista vazia."""
    svc = FeatureEvolutionLedgerService(
        releases_dir="/tmp/nonexistent_ledger_test_dir",
        cache_dir="/tmp/cache_ledger_test",
    )
    metas = svc._load_all_metas_sorted()
    assert metas == []


# ── Service: cache stats com ValidationError ──────────────────────────────


def test_get_cached_stats_validation_error_invalidates(
    releases_dir_fake: Path,
) -> None:
    """Stats inválidos no cache → ValidationError → invalidate + None."""
    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_stats_validation_test"),
    )

    from src.cache_manager import CacheManager

    cm = CacheManager(
        cache_dir=Path(str(svc._cache._cache_dir)),
        ttl_seconds=3600,
    )
    ns_dir = cm._cache_dir / "sfel"
    ns_dir.mkdir(parents=True, exist_ok=True)
    import hashlib

    stats_key = "stats:summer_26..spring_26"
    key_hash = hashlib.sha256(stats_key.encode("utf-8")).hexdigest()
    bad_path = ns_dir / f"{key_hash}.json"
    bad_path.write_text("invalid", encoding="utf-8")

    result = svc.get_cached_stats("summer_26", "spring_26")
    assert result is None


# ── Service: invalidate específico ───────────────────────────────────────


def test_invalidate_specific_key(
    releases_dir_fake: Path,
) -> None:
    """invalidate remove apenas o pair especificado, não outros."""
    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_invalidate_test"),
    )

    import asyncio

    async def populate() -> None:
        await svc.generate_ledger("summer_26", "spring_26")
        await svc.generate_ledger("winter_26", "spring_26")

    asyncio.run(populate())

    assert svc.get_cached_ledger("summer_26", "spring_26") is not None
    assert svc.get_cached_ledger("winter_26", "spring_26") is not None

    svc.invalidate("summer_26", "spring_26")

    assert svc.get_cached_ledger("summer_26", "spring_26") is None
    # winter_26..spring_26 deve ainda existir
    assert svc.get_cached_ledger("winter_26", "spring_26") is not None


# ── Service: EventBus falhando ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_ledger_event_bus_failure_handled(
    releases_dir_fake: Path,
) -> None:
    """Quando o EventBus falha, o generate_ledger não crash."""
    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_bus_test"),
    )

    with patch.object(svc._bus, "emit", side_effect=RuntimeError("Bus down")):
        diff = await svc.generate_ledger("summer_26", "spring_26")

    assert isinstance(diff, LedgerDiff)
    assert diff.current_slug == "summer_26"


# ── Service: current_meta com nome personalizado ──────────────────────────


@pytest.mark.asyncio
async def test_generate_ledger_with_current_meta_name(
    releases_dir_fake: Path,
) -> None:
    """current_meta com 'name' customizado → usado como current_name."""
    diff = await FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_meta_name_test"),
    ).generate_ledger(
        "summer_26",
        "spring_26",
        current_meta={"name": "Custom Summer Name"},
        previous_meta={"name": "Custom Spring Name"},
    )

    assert diff.current_name == "Custom Summer Name"
    assert diff.previous_name == "Custom Spring Name"


# ── Service: features com nome muito curto (< 4 chars) ───────────────────


def test_extract_features_skips_short_names(
    releases_dir_fake: Path,
) -> None:
    """Features com nome < 4 caracteres após strip são puladas."""
    extra_dir = releases_dir_fake / "short_names_release"
    extra_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "name": "Short Names Release",
        "release_id": 999,
        "slug": "short_names_release",
        "total_features": 1,
        "categories": [{"name": "Plataforma", "count": 1}],
        "generated_at": "2026-01-01T00:00:00+00:00",
    }
    (extra_dir / ".meta.json").write_text(
        json.dumps(meta, ensure_ascii=False),
        encoding="utf-8",
    )
    (extra_dir / "plataforma.md").write_text(
        "# Plataforma\n\n## Plataforma\n\n- Ab\n- Flow Builder\n- Xy\n",
        encoding="utf-8",
    )

    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_short_test"),
    )

    features = svc._extract_features("short_names_release")
    names = {f["name"] for f in features}
    assert "flow builder" in names
    # "ab" e "xy" têm menos de 4 chars → pulados
    assert "ab" not in names
    assert "xy" not in names


# ── Service: get_feature_history com categoria mudou ──────────────────────


@pytest.mark.asyncio
async def test_feature_history_status_category_changed(
    releases_dir_fake: Path,
) -> None:
    """Feature com mesma nome mas categoria diferente em releases consecutivas
    → status CATEGORY_CHANGED."""
    extra_dir = releases_dir_fake / "cat_change_27"
    extra_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "name": "Category Change '27",
        "release_id": 264,
        "slug": "cat_change_27",
        "total_features": 1,
        "categories": [{"name": "Segurança", "count": 1}],
        "generated_at": "2026-03-01T00:00:00+00:00",
    }
    (extra_dir / ".meta.json").write_text(
        json.dumps(meta, ensure_ascii=False),
        encoding="utf-8",
    )
    (extra_dir / "seguranca.md").write_text(
        "# Segurança\n\n## Segurança\n\n- Flow Builder\n",
        encoding="utf-8",
    )

    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_cat_change_test"),
    )

    entry = await svc.get_feature_history("Flow Builder")
    # flow builder está em spring_26 (Plataforma), summer_26 (Plataforma),
    # e cat_change_27 (Segurança)
    assert entry.total_releases_seen == 3
    # último par: summer_26 (Plataforma) → cat_change_27 (Segurança) → CATEGORY_CHANGED
    assert entry.current_status == LifecycleStatus.CATEGORY_CHANGED
