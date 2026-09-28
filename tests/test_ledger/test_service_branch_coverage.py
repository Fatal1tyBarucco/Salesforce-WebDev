"""Testes de cobertura adicionais para branches do service.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.automation.ledger.linker import FeatureLinker
from src.automation.ledger.models import (
    FeatureLink,
    FeatureSnapshot,
    LifecycleStatus,
    LinkageMethod,
)
from src.automation.ledger.service import FeatureEvolutionLedgerService


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


# ── Service: DEPRECATED status (linha 246-247) ───────────────────────────

@pytest.mark.asyncio
async def test_generate_ledger_deprecated_status(
    releases_dir_fake: Path,
) -> None:
    """Cobre a branch DEPRECATED do service.generate_ledger.

    A branch DEPRECATED só é atingida quando um FeatureLink tem
    status == LifecycleStatus.DEPRECATED. Como o linker atual não produz
    esse status, mockamos o linker para emitir um link DEPRECATED.
    """
    class DeprecatedLinker(FeatureLinker):
        def link(  # type: ignore[misc]
            self,
            current_snaps: list[FeatureSnapshot],
            previous_snaps: list[FeatureSnapshot],
            current_meta: dict,
            previous_meta: dict,
        ) -> list[FeatureLink]:
            if current_snaps and previous_snaps:
                return [
                    FeatureLink(
                        feature_a=current_snaps[0],
                        feature_b=previous_snaps[0],
                        status=LifecycleStatus.DEPRECATED,
                        linkage_method=LinkageMethod.EXACT,
                        similarity_score=1.0,
                        notes="Deprecated via test mock.",
                    )
                ]
            return []

    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_deprecated_test"),
        linker_instance=DeprecatedLinker(),
    )

    diff = await svc.generate_ledger("summer_26", "spring_26")
    stats = svc.get_cached_stats("summer_26", "spring_26")
    assert stats is not None
    assert stats.deprecated_count == 1
    assert len(diff.deprecated) == 1


# ── Service: REMOVED status via link (linha 248-249) ──────────────────────

@pytest.mark.asyncio
async def test_generate_ledger_removed_via_link(
    releases_dir_fake: Path,
) -> None:
    """Cobre a branch REMOVED quando um link tem status REMOVED."""
    class RemovedLinker(FeatureLinker):
        def link(  # type: ignore[misc]
            self,
            current_snaps: list[FeatureSnapshot],
            previous_snaps: list[FeatureSnapshot],
            current_meta: dict,
            previous_meta: dict,
        ) -> list[FeatureLink]:
            if current_snaps and previous_snaps:
                return [
                    FeatureLink(
                        feature_a=current_snaps[0],
                        feature_b=previous_snaps[0],
                        status=LifecycleStatus.REMOVED,
                        linkage_method=LinkageMethod.EXACT,
                        similarity_score=1.0,
                        notes="Removed via test mock.",
                    )
                ]
            return []

    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_removed_test"),
        linker_instance=RemovedLinker(),
    )

    diff = await svc.generate_ledger("summer_26", "spring_26")
    stats = svc.get_cached_stats("summer_26", "spring_26")
    assert stats is not None
    assert stats.removed_count == 1
    assert len(diff.removed) == 1


# ── Service: BORN status via link (linha 239 do service) ───────────────────

@pytest.mark.asyncio
async def test_generate_ledger_born_via_link(
    releases_dir_fake: Path,
) -> None:
    """Cobre a branch BORN quando um FeatureLink tem status BORN."""
    class BornLinker(FeatureLinker):
        def link(  # type: ignore[misc]
            self,
            current_snaps: list[FeatureSnapshot],
            previous_snaps: list[FeatureSnapshot],
            current_meta: dict,
            previous_meta: dict,
        ) -> list[FeatureLink]:
            if current_snaps:
                return [
                    FeatureLink(
                        feature_a=current_snaps[0],
                        feature_b=current_snaps[0],  # mesmo snap, status BORN
                        status=LifecycleStatus.BORN,
                        linkage_method=LinkageMethod.EXACT,
                        similarity_score=1.0,
                        notes="Born via test mock.",
                    )
                ]
            return []

    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_born_test"),
        linker_instance=BornLinker(),
    )

    diff = await svc.generate_ledger("summer_26", "spring_26")
    stats = svc.get_cached_stats("summer_26", "spring_26")
    assert stats is not None
    assert stats.born_count >= 1


# ── Service: get_cached_ledger com ValidationError (linhas 377-384) ───────

def test_get_cached_ledger_validation_error_branch(
    releases_dir_fake: Path,
) -> None:
    """Cobre a branch de ValidationError em get_cached_ledger.

    Escreve dados inválidos diretamente no cache para forçar
    a exception path.
    """
    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_val_err_test"),
    )

    from src.cache_manager import CacheManager
    import hashlib

    cm = CacheManager(
        cache_dir=Path(str(svc._cache._cache_dir)),
        ttl_seconds=3600,
    )
    cache_key = "summer_26..spring_26"
    key_hash = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
    ns_dir = cm._cache_dir / "sfel"
    ns_dir.mkdir(parents=True, exist_ok=True)
    (ns_dir / f"{key_hash}.json").write_text("not-a-dict", encoding="utf-8")

    result = svc.get_cached_ledger("summer_26", "spring_26")
    assert result is None


# ── Service: get_cached_stats com ValidationError (linhas 406-413) ────────

def test_get_cached_stats_validation_error_branch(
    releases_dir_fake: Path,
) -> None:
    """Cobre a branch de ValidationError em get_cached_stats."""
    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_stats_val_err_test"),
    )

    from src.cache_manager import CacheManager
    import hashlib

    cm = CacheManager(
        cache_dir=Path(str(svc._cache._cache_dir)),
        ttl_seconds=3600,
    )
    stats_key = "stats:summer_26..spring_26"
    key_hash = hashlib.sha256(stats_key.encode("utf-8")).hexdigest()
    ns_dir = cm._cache_dir / "sfel"
    ns_dir.mkdir(parents=True, exist_ok=True)
    (ns_dir / f"{key_hash}.json").write_text("bad", encoding="utf-8")

    result = svc.get_cached_stats("summer_26", "spring_26")
    assert result is None


# ── Service: feature com nome curto pulado (linha 93 do service) ──────────

def test_extract_features_skips_short_names_branch(
    releases_dir_fake: Path,
) -> None:
    """Cobre a linha 93 (continue de len(raw_name) < 4) do service."""
    extra_dir = releases_dir_fake / "short_names_test"
    extra_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "name": "Short Names Test",
        "release_id": 999,
        "slug": "short_names_test",
        "total_features": 1,
        "categories": [{"name": "Plataforma", "count": 1}],
        "generated_at": "2026-01-01T00:00:00+00:00",
    }
    (extra_dir / ".meta.json").write_text(
        json.dumps(meta, ensure_ascii=False), encoding="utf-8",
    )
    (extra_dir / "plataforma.md").write_text(
        "# Plataforma\n\n## Plataforma\n\n- Ab\n- Flow Builder\n",
        encoding="utf-8",
    )

    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_short_branch_test"),
    )

    features = svc._extract_features("short_names_test")
    names = {f["name"] for f in features}
    assert "flow builder" in names
    assert "ab" not in names


# ── Service: get_feature_history com status RENAMED na branch (linha 473) ─

@pytest.mark.asyncio
async def test_feature_history_covers_renamed_branch(
    releases_dir_fake: Path,
) -> None:
    """Cobre a branch de RENAMED no get_feature_history (linha 473).

    Cria um release extra onde 'Flow Builder' aparece como 'Flow Builder New Name'
    na categoria Plataforma. O histórico de 'Flow Builder' terá 2 entradas
    com nomes diferentes → RENAMED.
    """
    extra_dir = releases_dir_fake / "renamed_history_test"
    extra_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "name": "Renamed History Test",
        "release_id": 999,
        "slug": "renamed_history_test",
        "total_features": 1,
        "categories": [{"name": "Plataforma", "count": 1}],
        "generated_at": "2026-03-01T00:00:00+00:00",
    }
    (extra_dir / ".meta.json").write_text(
        json.dumps(meta, ensure_ascii=False), encoding="utf-8",
    )
    (extra_dir / "plataforma.md").write_text(
        "# Plataforma\n\n## Plataforma\n\n- Flow Builder New Name\n",
        encoding="utf-8",
    )

    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_renamed_branch_test"),
    )

    entry = await svc.get_feature_history("Flow Builder")
    # flow builder está em spring_26 (Plataforma) e summer_26 (Plataforma)
    # flow builder new name está em renamed_history_test (Plataforma)
    # Entradas: [spring_26/flow builder, summer_26/flow builder, renamed_history_test/flow builder new name]
    assert entry.total_releases_seen == 3
    # Os dois últimos entries têm nomes diferentes → current_status == RENAMED
    if entry.total_releases_seen >= 2:
        prev = entry.entries[-2]
        curr = entry.entries[-1]
        assert prev.name != curr.name
        assert entry.current_status == LifecycleStatus.RENAMED
    # Nota: se total_releases_seen != 3, fluxo de extração de features não
    # encontrou o release extra — ignoramos o assert exato de total.


# ── Service: get_feature_history com categoria diferente (linha 475) ──────

@pytest.mark.asyncio
async def test_feature_history_covers_category_changed_branch(
    releases_dir_fake: Path,
) -> None:
    """Cobre a branch de CATEGORY_CHANGED no get_feature_history (linha 475).

    Cria um release extra onde 'Flow Builder' aparece na categoria Segurança.
    O histórico de 'Flow Builder' terá entradas em Plataforma e Segurança.
    """
    extra_dir = releases_dir_fake / "cat_changed_history_test"
    extra_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "name": "Cat Changed History Test",
        "release_id": 1000,
        "slug": "cat_changed_history_test",
        "total_features": 1,
        "categories": [{"name": "Segurança", "count": 1}],
        "generated_at": "2026-04-01T00:00:00+00:00",
    }
    (extra_dir / ".meta.json").write_text(
        json.dumps(meta, ensure_ascii=False), encoding="utf-8",
    )
    (extra_dir / "seguranca.md").write_text(
        "# Segurança\n\n## Segurança\n\n- Flow Builder\n",
        encoding="utf-8",
    )

    svc = FeatureEvolutionLedgerService(
        releases_dir=str(releases_dir_fake),
        cache_dir=str(releases_dir_fake.parent / "cache_cat_changed_branch_test"),
    )

    entry = await svc.get_feature_history("Flow Builder")
    # flow builder está em spring_26 (Plataforma), summer_26 (Plataforma),
    # e cat_changed_history_test (Segurança)
    assert entry.total_releases_seen == 3
    # Os dois últimos entries têm a mesma nome mas categorias diferentes
    if entry.total_releases_seen >= 2:
        prev = entry.entries[-2]
        curr = entry.entries[-1]
        assert prev.name == curr.name
        assert prev.category != curr.category
        assert entry.current_status == LifecycleStatus.CATEGORY_CHANGED
