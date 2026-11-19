"""Robustness branch tests for the cache layer (ADR-011 R10).

Targets defensive paths: I/O failures, lock contention, malformed payloads.
All deterministic — mocks and injected clocks, no sleeps.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from src.cache_io import FileLock, atomic_write_text, compute_checksum, quarantine_file
from src.cache_manager import CacheManager
from src.processed_releases import ProcessedReleasesStore, compute_release_fingerprint


class FakeClock:
    def __init__(self, start: float = 1_000_000.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def cache(tmp_path: Path, clock: FakeClock) -> CacheManager:
    return CacheManager(cache_dir=tmp_path / "cache", clock=clock)


def entry_path(cache_dir: Path, key: str, namespace: str = "") -> Path:
    full_key = f"{namespace}:{key}" if namespace else key
    digest = hashlib.sha256(full_key.encode("utf-8")).hexdigest()
    if namespace:
        return cache_dir / namespace / f"{digest}.json"
    return cache_dir / f"{digest}.json"


def ns_lock_path(cache_dir: Path, namespace: str) -> Path:
    digest = hashlib.sha256(f"ns:{namespace}".encode()).hexdigest()
    return cache_dir / "locks" / f"{digest}.lock"


def key_lock_path(cache_dir: Path, key: str, namespace: str = "") -> Path:
    full_key = f"{namespace}:{key}" if namespace else key
    digest = hashlib.sha256(full_key.encode("utf-8")).hexdigest()
    return cache_dir / "locks" / f"{digest}.lock"


def write_envelope(path: Path, data: Any, clock: FakeClock, **overrides: Any) -> None:
    envelope = {
        "schema_version": 2,
        "timestamp": clock.now,
        "ttl": 3600,
        "namespace": "",
        "last_access": clock.now,
        "checksum": compute_checksum(data),
        "data": data,
    }
    envelope.update(overrides)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(envelope), encoding="utf-8")


# ── cache_io defensive branches ───────────────────────────────────


def test_atomic_write_cleanup_failure_logs(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    with (
        patch("src.cache_io.os.replace", side_effect=OSError("rename failed")),
        patch.object(Path, "unlink", side_effect=OSError("cleanup failed")),
    ):
        with pytest.raises(OSError):
            atomic_write_text(target, "x")


def test_quarantine_rotation_scan_failure(tmp_path: Path) -> None:
    src = tmp_path / "entry.json"
    src.write_text("bad", encoding="utf-8")
    with patch.object(Path, "iterdir", side_effect=OSError("scan failed")):
        moved = quarantine_file(src, tmp_path / "q", keep=3)
    assert moved is not None  # quarantine itself succeeded


def test_quarantine_rotation_unlink_failure(tmp_path: Path) -> None:
    qdir = tmp_path / "q"
    src = tmp_path / "entry.json"
    for i in range(4):
        src.write_text(f"v{i}", encoding="utf-8")
        quarantine_file(src, qdir, keep=3)
    src.write_text("v4", encoding="utf-8")
    with patch.object(Path, "unlink", side_effect=OSError("rotation failed")):
        moved = quarantine_file(src, qdir, keep=3)
    assert moved is not None


def test_file_lock_exit_without_enter(tmp_path: Path) -> None:
    lock = FileLock(tmp_path / "x.lock", timeout=1.0)
    lock.__exit__(None, None, None)  # no-op, must not raise


def test_file_lock_unlock_failure_logs(tmp_path: Path) -> None:
    import fcntl

    real_flock = fcntl.flock

    def failing_unlock(fd: int, op: int) -> None:
        if op == fcntl.LOCK_UN:
            raise OSError("unlock failed")
        real_flock(fd, op)

    with patch("src.cache_io.fcntl.flock", side_effect=failing_unlock):
        with FileLock(tmp_path / "x.lock", timeout=1.0):
            pass  # release logs a warning, does not raise


# ── CacheManager.invalidate / invalidate_namespace ────────────────


def test_invalidate_invalid_namespace_noop(cache: CacheManager) -> None:
    cache.invalidate("k", namespace="../evil")  # must not raise


def test_invalidate_unlink_oserror(cache: CacheManager) -> None:
    cache.set("k", "v")
    with patch.object(Path, "unlink", side_effect=OSError("denied")):
        cache.invalidate("k")  # degrades with warning
    assert entry_path(cache._cache_dir, "k").exists()


def test_invalidate_lock_timeout(cache: CacheManager) -> None:
    cache.set("k", "v")
    with FileLock(key_lock_path(cache._cache_dir, "k"), timeout=1.0):
        manager = CacheManager(cache_dir=cache._cache_dir, lock_timeout=0.1)
        manager.invalidate("k")  # degrades
    assert entry_path(cache._cache_dir, "k").exists()


def test_invalidate_race_second_exists_false(cache: CacheManager) -> None:
    cache.set("k", "v")
    with patch.object(Path, "exists", side_effect=[True, False]):
        cache.invalidate("k")  # inner check false → skip unlink


def test_invalidate_namespace_unlink_oserror(cache: CacheManager) -> None:
    cache.set("k", "v", namespace="ns")
    with patch.object(Path, "unlink", side_effect=OSError("denied")):
        assert cache.invalidate_namespace("ns") == 0


def test_invalidate_namespace_lock_timeout(cache: CacheManager) -> None:
    cache.set("k", "v", namespace="ns")
    with FileLock(ns_lock_path(cache._cache_dir, "ns"), timeout=1.0):
        manager = CacheManager(cache_dir=cache._cache_dir, lock_timeout=0.1)
        assert manager.invalidate_namespace("ns") == 0


# ── clear_expired / maintenance ───────────────────────────────────


def test_clear_expired_lock_timeout(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("old", "v", ttl=10)
    clock.advance(5000)
    with FileLock(ns_lock_path(cache._cache_dir, ""), timeout=1.0):
        manager = CacheManager(cache_dir=cache._cache_dir, clock=clock, lock_timeout=0.1)
        manager.get("trigger")  # touch root namespace without taking the ns lock
        assert manager.clear_expired() == 0


def test_clear_expired_full_scan_skips_quarantine_json(cache: CacheManager) -> None:
    qdir = cache._cache_dir / "quarantine"
    qdir.mkdir(parents=True)
    (qdir / "old.json").write_text("{}", encoding="utf-8")
    assert cache.clear_expired(full_scan=True) == 0
    assert (qdir / "old.json").exists()


def test_maintenance_quarantine_scan_oserror(cache: CacheManager) -> None:
    (cache._cache_dir / "quarantine").mkdir()
    with patch.object(Path, "iterdir", side_effect=OSError("scan failed")):
        report = cache.maintenance()
    assert report["quarantine_copies"] == 0


def test_sweep_unlink_oserror(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("old", "v", ttl=10)
    clock.advance(5000)
    with patch.object(Path, "unlink", side_effect=OSError("denied")):
        assert cache.clear_expired() == 0


def test_sweep_glob_oserror(cache: CacheManager) -> None:
    cache.set("k", "v")
    with patch.object(Path, "glob", side_effect=OSError("scan failed")):
        assert cache.clear_expired() == 0


def test_sweep_invalid_timestamp_quarantined(cache: CacheManager, clock: FakeClock) -> None:
    path = entry_path(cache._cache_dir, "k")
    write_envelope(path, "v", clock, timestamp="bad")
    assert cache.clear_expired(full_scan=True) == 0
    assert cache.stats.eviction_reasons["corruption"] == 1


# ── get defensive branches ────────────────────────────────────────


def test_v2_envelope_missing_data_quarantined(cache: CacheManager, clock: FakeClock) -> None:
    path = entry_path(cache._cache_dir, "k")
    envelope = {
        "schema_version": 2,
        "timestamp": clock.now,
        "ttl": 3600,
        "checksum": compute_checksum("v"),
    }
    path.write_text(json.dumps(envelope), encoding="utf-8")
    assert cache.get("k") is None
    assert cache.stats.eviction_reasons["corruption"] == 1


def test_v2_envelope_missing_checksum_quarantined(cache: CacheManager, clock: FakeClock) -> None:
    path = entry_path(cache._cache_dir, "k")
    write_envelope(path, "v", clock)
    payload = json.loads(path.read_text(encoding="utf-8"))
    del payload["checksum"]
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert cache.get("k") is None


def test_expired_unlink_oserror(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("k", "v", ttl=10)
    clock.advance(5000)
    with patch.object(Path, "unlink", side_effect=OSError("denied")):
        assert cache.get("k") is None
    assert cache.stats.eviction_reasons["ttl"] == 1


def test_last_access_refresh_oserror(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("k", "v")
    clock.advance(120)
    with patch("src.cache_manager.atomic_write_json", side_effect=OSError("ro")):
        assert cache.get("k") == "v"  # hit survives refresh failure


def test_legacy_last_access_defaults_to_timestamp(cache: CacheManager, clock: FakeClock) -> None:
    path = entry_path(cache._cache_dir, "k")
    legacy = {"timestamp": clock.now, "ttl": 3600, "data": "v"}
    path.write_text(json.dumps(legacy), encoding="utf-8")
    clock.advance(120)
    assert cache.get("k") == "v"


# ── LRU budget defensive branches ─────────────────────────────────


def test_budget_within_avoids_content_reads(tmp_path: Path, clock: FakeClock) -> None:
    """Within budget, set() must not read entry payloads (stat-only pre-check)."""
    cache = CacheManager(cache_dir=tmp_path / "c", clock=clock)
    cache.set("a", "1")
    with patch("src.cache_manager.read_json_safe", side_effect=AssertionError("content read")):
        cache.set("b", "2")  # default budgets far away → no payload reads
    assert cache.get("b") == "2"


def test_budget_glob_oserror(tmp_path: Path, clock: FakeClock) -> None:
    cache = CacheManager(cache_dir=tmp_path / "c", clock=clock, max_entries_per_namespace=1)
    with patch.object(Path, "glob", side_effect=OSError("scan failed")):
        cache.set("k", "v")  # write succeeds, budget scan degrades
    assert cache.get("k") == "v"


def test_budget_stat_oserror(tmp_path: Path, clock: FakeClock) -> None:
    cache = CacheManager(cache_dir=tmp_path / "c", clock=clock, max_entries_per_namespace=1)
    cache.set("a", "1")
    with patch.object(Path, "stat", side_effect=OSError("stat failed")):
        cache.set("b", "2")  # entries skipped in budget scan
    assert cache.get("b") == "2"


def test_budget_eviction_unlink_oserror(tmp_path: Path, clock: FakeClock) -> None:
    cache = CacheManager(cache_dir=tmp_path / "c", clock=clock, max_entries_per_namespace=1)
    cache.set("a", "1")
    clock.advance(120)
    with patch.object(Path, "unlink", side_effect=OSError("denied")):
        cache.set("b", "2")  # eviction fails, logged, no raise
    assert cache.get("a") == "1"


def test_budget_invalid_last_access_falls_back(tmp_path: Path, clock: FakeClock) -> None:
    cache = CacheManager(cache_dir=tmp_path / "c", clock=clock, max_entries_per_namespace=1)
    path = entry_path(cache._cache_dir, "a")
    write_envelope(path, "1", clock, last_access="bad")
    clock.advance(120)
    cache.set("b", "2")
    assert cache.get("a") is None  # evicted with access=0 fallback


# ── content cache defensive branches ──────────────────────────────


def test_load_content_cache_lock_timeout(cache: CacheManager, tmp_path: Path) -> None:
    cache_file = tmp_path / "content.json"
    cache.save_content_cache(cache_file, {"a": "b"})
    with FileLock(cache_file.with_name(cache_file.name + ".lock"), timeout=1.0):
        manager = CacheManager(cache_dir=cache._cache_dir, lock_timeout=0.1)
        assert manager.load_content_cache(cache_file) == {}


def test_load_content_cache_non_string_content_hash(cache: CacheManager, tmp_path: Path) -> None:
    f = tmp_path / "mixed.json"
    f.write_text(json.dumps({"f": {"content_hash": 123}}), encoding="utf-8")
    assert cache.load_content_cache(f) == {"f": ""}


def test_load_content_cache_migration_write_oserror(cache: CacheManager, tmp_path: Path) -> None:
    target = tmp_path / "doc.md"
    target.write_text("abc", encoding="utf-8")
    legacy_md5 = hashlib.md5(b"abc").hexdigest()
    cache_file = tmp_path / "content.json"
    cache_file.write_text(json.dumps({str(target): legacy_md5}), encoding="utf-8")
    with patch("src.cache_manager.atomic_write_json", side_effect=OSError("ro")):
        loaded = cache.load_content_cache(cache_file)
    assert loaded == {str(target): hashlib.sha256(b"abc").hexdigest()}


def test_save_content_cache_skips_non_string(cache: CacheManager, tmp_path: Path) -> None:
    cache_file = tmp_path / "content.json"
    cache.save_content_cache(cache_file, {"ok": "hash", "bad": 123})  # type: ignore[dict-item]
    assert json.loads(cache_file.read_text(encoding="utf-8")) == {"ok": "hash"}


def test_save_content_cache_lock_timeout(cache: CacheManager, tmp_path: Path) -> None:
    cache_file = tmp_path / "content.json"
    with FileLock(cache_file.with_name(cache_file.name + ".lock"), timeout=1.0):
        manager = CacheManager(cache_dir=cache._cache_dir, lock_timeout=0.1)
        manager.save_content_cache(cache_file, {"a": "b"})  # degrades
    assert not cache_file.exists()


# ── ProcessedReleasesStore defensive branches ─────────────────────


def test_fingerprint_scan_oserror(tmp_path: Path) -> None:
    with patch.object(Path, "rglob", side_effect=OSError("scan failed")):
        value = compute_release_fingerprint(tmp_path)
    assert len(value) == 64


def test_fingerprint_unreadable_md(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("x", encoding="utf-8")
    with patch.object(CacheManager, "compute_file_hash", side_effect=OSError("denied")):
        value = compute_release_fingerprint(tmp_path)
    assert len(value) == 64


def test_fingerprint_categories_not_list(tmp_path: Path) -> None:
    (tmp_path / ".meta.json").write_text(
        json.dumps({"name": "x", "categories": "not-a-list"}), encoding="utf-8"
    )
    assert len(compute_release_fingerprint(tmp_path)) == 64


def test_store_mark_lock_timeout(tmp_path: Path) -> None:
    store = ProcessedReleasesStore(cache_dir=tmp_path / "cache", lock_timeout=0.1)
    lock_path = store._cache_dir / "processed_releases.json.lock"
    with FileLock(lock_path, timeout=1.0):
        store.mark_processed("x", "fp")  # degrades with log
    assert not (store._cache_dir / "processed_releases.json").exists()


def test_store_invalidate_lock_timeout(tmp_path: Path) -> None:
    store = ProcessedReleasesStore(cache_dir=tmp_path / "cache", lock_timeout=0.1)
    lock_path = store._cache_dir / "processed_releases.json.lock"
    with FileLock(lock_path, timeout=1.0):
        store.invalidate("x")  # degrades


def test_store_invalidate_unknown_slug(tmp_path: Path) -> None:
    store = ProcessedReleasesStore(cache_dir=tmp_path / "cache")
    store.invalidate("never-seen")  # no-op, must not raise


def test_store_load_lock_timeout(tmp_path: Path) -> None:
    store = ProcessedReleasesStore(cache_dir=tmp_path / "cache", lock_timeout=0.1)
    lock_path = store._cache_dir / "processed_releases.json.lock"
    with FileLock(lock_path, timeout=1.0):
        assert store.is_processed("x", "fp") is False


def test_store_mark_without_release_metadata(tmp_path: Path) -> None:
    store = ProcessedReleasesStore(cache_dir=tmp_path / "cache")
    store.mark_processed("x", "fp")
    data = json.loads((store._cache_dir / "processed_releases.json").read_text(encoding="utf-8"))
    assert data["releases"]["x"]["name"] == "x"
    assert data["releases"]["x"]["release_id"] == 0


def test_store_previous_entry_non_dict(tmp_path: Path) -> None:
    store = ProcessedReleasesStore(cache_dir=tmp_path / "cache")
    store.mark_processed("x", "fp")
    state_path = store._cache_dir / "processed_releases.json"
    data = json.loads(state_path.read_text(encoding="utf-8"))
    data["releases"]["x"] = "garbage"
    body = {"releases": data["releases"], "history": data["history"]}
    data["checksum"] = compute_checksum(body)
    state_path.write_text(json.dumps(data), encoding="utf-8")
    store.mark_processed("x", "fp2")
    refreshed = json.loads(state_path.read_text(encoding="utf-8"))
    assert refreshed["releases"]["x"]["run_count"] == 1


def test_store_previous_run_count_non_int(tmp_path: Path) -> None:
    store = ProcessedReleasesStore(cache_dir=tmp_path / "cache")
    store.mark_processed("x", "fp")
    state_path = store._cache_dir / "processed_releases.json"
    data = json.loads(state_path.read_text(encoding="utf-8"))
    data["releases"]["x"]["run_count"] = "many"
    body = {"releases": data["releases"], "history": data["history"]}
    data["checksum"] = compute_checksum(body)
    state_path.write_text(json.dumps(data), encoding="utf-8")
    store.mark_processed("x", "fp2")
    refreshed = json.loads(state_path.read_text(encoding="utf-8"))
    assert refreshed["releases"]["x"]["run_count"] == 1
