"""Orchestrator × processed-releases integration tests (ADR-011 R2/R7)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.cache_manager import CacheManager
from src.config import ReleaseInfo
from src.orchestrator import PipelineOrchestrator
from src.processed_releases import ProcessedReleasesStore, compute_release_fingerprint

RELEASE = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")


@pytest.fixture
def isolated_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "releases").mkdir()
    return tmp_path


def _make_config(isolated_cwd: Path, dry_run: bool = False) -> MagicMock:
    config = MagicMock()
    config.dry_run = dry_run
    config.event_bus = MagicMock()
    config.event_bus.emit = AsyncMock()
    config.processed_store = ProcessedReleasesStore(
        cache_dir=isolated_cwd / "cache", lock_timeout=2.0
    )
    config.cache = CacheManager(cache_dir=isolated_cwd / "cache")
    return config


def _write_release_artifacts(isolated_cwd: Path) -> None:
    release_dir = isolated_cwd / "releases" / "summer_26"
    release_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "name": RELEASE.name,
        "slug": RELEASE.slug,
        "release_id": RELEASE.release_id,
        "total_features": 5,
        "categories": [{"name": "Automação", "count": 5}],
    }
    (release_dir / ".meta.json").write_text(json.dumps(meta), encoding="utf-8")
    sub = release_dir / "pt_BR"
    sub.mkdir(exist_ok=True)
    (sub / "automacao.md").write_text("# Automação\n- feature", encoding="utf-8")


async def test_second_run_skips_generation(isolated_cwd: Path) -> None:
    config = _make_config(isolated_cwd)
    orch = PipelineOrchestrator(config)

    async def fake_process(*args: object, **kwargs: object) -> bool:
        _write_release_artifacts(isolated_cwd)
        return True

    with (
        patch("src.main.process_single_release", new=AsyncMock(side_effect=fake_process)) as proc,
        patch("src.main.enrich_meta_with_classification", new_callable=AsyncMock),
    ):
        await orch._process_release(
            RELEASE, MagicMock(), MagicMock(), MagicMock(), MagicMock(), None
        )
        await orch._process_release(
            RELEASE, MagicMock(), MagicMock(), MagicMock(), MagicMock(), None
        )
    assert proc.await_count == 1  # exactly one processing
    store = config.processed_store
    release_dir = isolated_cwd / "releases" / "summer_26"
    fingerprint = compute_release_fingerprint(
        release_dir, name=RELEASE.name, release_id=RELEASE.release_id, slug=RELEASE.slug
    )
    assert store.is_processed(RELEASE.slug, fingerprint) is True
    assert store.stats.hits >= 1


async def test_content_change_invalidates_fingerprint(isolated_cwd: Path) -> None:
    config = _make_config(isolated_cwd)
    orch = PipelineOrchestrator(config)

    async def fake_process(*args: object, **kwargs: object) -> bool:
        _write_release_artifacts(isolated_cwd)
        return True

    with (
        patch("src.main.process_single_release", new=AsyncMock(side_effect=fake_process)) as proc,
        patch("src.main.enrich_meta_with_classification", new_callable=AsyncMock),
    ):
        await orch._process_release(
            RELEASE, MagicMock(), MagicMock(), MagicMock(), MagicMock(), None
        )
        # Upstream content changed after processing.
        md = isolated_cwd / "releases" / "summer_26" / "pt_BR" / "automacao.md"
        md.write_text("# Automação\n- feature alterada", encoding="utf-8")
        await orch._process_release(
            RELEASE, MagicMock(), MagicMock(), MagicMock(), MagicMock(), None
        )
    assert proc.await_count == 2


async def test_dry_run_does_not_write_state(isolated_cwd: Path) -> None:
    config = _make_config(isolated_cwd, dry_run=True)
    orch = PipelineOrchestrator(config)
    with (
        patch("src.main.process_single_release", new_callable=AsyncMock) as proc,
        patch("src.main.enrich_meta_with_classification", new_callable=AsyncMock),
    ):
        await orch._process_release(
            RELEASE, MagicMock(), MagicMock(), MagicMock(), MagicMock(), None
        )
    assert proc.await_count == 1
    assert not (isolated_cwd / "cache" / "processed_releases.json").exists()


async def test_failed_processing_not_marked(isolated_cwd: Path) -> None:
    config = _make_config(isolated_cwd)
    orch = PipelineOrchestrator(config)
    with (
        patch("src.main.process_single_release", new=AsyncMock(return_value=False)) as proc,
        patch("src.main.enrich_meta_with_classification", new_callable=AsyncMock),
    ):
        await orch._process_release(
            RELEASE, MagicMock(), MagicMock(), MagicMock(), MagicMock(), None
        )
        await orch._process_release(
            RELEASE, MagicMock(), MagicMock(), MagicMock(), MagicMock(), None
        )
    assert proc.await_count == 2
    assert not (isolated_cwd / "cache" / "processed_releases.json").exists()


async def test_stats_persisted_with_store_section(isolated_cwd: Path) -> None:
    config = _make_config(isolated_cwd)
    orch = PipelineOrchestrator(config)
    config.processed_store.is_processed("x", "y")  # generate one miss
    orch._persist_cache_stats()
    stats_path = isolated_cwd / "cache" / "stats.json"
    assert stats_path.exists()
    data = json.loads(stats_path.read_text(encoding="utf-8"))
    assert "processed_releases" in data["extra"]
    assert data["extra"]["processed_releases"]["misses"] == 1


async def test_corrupt_state_pipeline_continues(isolated_cwd: Path) -> None:
    config = _make_config(isolated_cwd)
    orch = PipelineOrchestrator(config)
    cache_dir = isolated_cwd / "cache"
    cache_dir.mkdir(exist_ok=True)
    (cache_dir / "processed_releases.json").write_text("{corrupt", encoding="utf-8")

    async def fake_process(*args: object, **kwargs: object) -> bool:
        _write_release_artifacts(isolated_cwd)
        return True

    with (
        patch("src.main.process_single_release", new=AsyncMock(side_effect=fake_process)),
        patch("src.main.enrich_meta_with_classification", new_callable=AsyncMock),
    ):
        await orch._process_release(
            RELEASE, MagicMock(), MagicMock(), MagicMock(), MagicMock(), None
        )
    assert list((cache_dir / "quarantine").iterdir())
    assert (cache_dir / "processed_releases.json").exists()
