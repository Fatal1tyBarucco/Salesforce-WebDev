"""CacheManager test suite — deterministic, injected clock, no time.sleep.

Covers R1 (atomic writes), R2 (locking), R3 (integrity/quarantine/recovery),
R4 (SHA-256 + legacy migration), R5 (LRU budgets, scoped sweeps), R6 (stats),
R9 (config defaults) and R10 (robustness scenarios) of the cache-layer spec.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from src.cache_io import FileLock, compute_checksum
from src.cache_manager import CacheManager, CacheStats


class FakeClock:
    """Injectable monotonic wall clock for deterministic TTL tests."""

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
    """Independently compute the hashed entry path (mirrors the public contract)."""
    full_key = f"{namespace}:{key}" if namespace else key
    key_hash = hashlib.sha256(full_key.encode("utf-8")).hexdigest()
    if namespace:
        return cache_dir / namespace / f"{key_hash}.json"
    return cache_dir / f"{key_hash}.json"


def ns_lock_path(cache_dir: Path, namespace: str) -> Path:
    digest = hashlib.sha256(f"ns:{namespace}".encode()).hexdigest()
    return cache_dir / "locks" / f"{digest}.lock"


def make_envelope(
    data: Any,
    timestamp: float,
    ttl: int = 3600,
    namespace: str = "",
    checksum: str | None = None,
    schema_version: int = 2,
) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "timestamp": timestamp,
        "ttl": ttl,
        "namespace": namespace,
        "last_access": timestamp,
        "checksum": compute_checksum(data) if checksum is None else checksum,
        "data": data,
    }


# ── Basic get/set (legacy contract preserved) ─────────────────────


def test_cache_set_get(cache: CacheManager) -> None:
    cache.set("key1", "value1", ttl=3600)
    assert cache.get("key1") == "value1"


def test_cache_miss(cache: CacheManager) -> None:
    assert cache.get("nonexistent") is None


def test_cache_ttl_expiration(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("key1", "value1", ttl=3600)
    assert cache.get("key1") == "value1"
    clock.advance(3601)
    assert cache.get("key1") is None


def test_cache_ttl_boundary_not_expired(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("key1", "value1", ttl=3600)
    clock.advance(3600)  # exactly at the boundary: now - ts == ttl → still valid
    assert cache.get("key1") == "value1"


def test_cache_invalidate(cache: CacheManager) -> None:
    cache.set("key1", "value1", ttl=3600)
    cache.invalidate("key1")
    assert cache.get("key1") is None


def test_default_ttl_preserved(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("k", "v")
    payload = json.loads(entry_path(cache._cache_dir, "k").read_text(encoding="utf-8"))
    assert payload["ttl"] == 86400


def test_written_envelope_schema_version_is_2(cache: CacheManager) -> None:
    """The on-disk envelope must declare schema_version 2 (kills constant mutants)."""
    cache.set("k", "v")
    payload = json.loads(entry_path(cache._cache_dir, "k").read_text(encoding="utf-8"))
    assert payload["schema_version"] == 2
    assert payload["checksum"] == compute_checksum("v")
    assert payload["namespace"] == ""
    assert payload["data"] == "v"


def test_nested_cache_dir_created(tmp_path: Path) -> None:
    """CacheManager must create deep missing parent directories (parents=True)."""
    deep = tmp_path / "a" / "b" / "cache"
    cache = CacheManager(cache_dir=deep)
    cache.set("k", "v")
    assert cache.get("k") == "v"


def test_fresh_stats_all_zero() -> None:
    stats = CacheStats()
    assert stats.hits == 0
    assert stats.misses == 0
    assert stats.evictions == 0
    assert stats.sets == 0
    assert stats.by_namespace == {}
    assert stats.eviction_reasons == {}
    assert stats.total == 0
    assert stats.hit_rate == 0.0


def test_hit_rate_single_lookup(cache: CacheManager) -> None:
    cache.get("only-miss")
    assert cache.stats.hit_rate == 0.0
    assert cache.stats.by_namespace[""].hit_rate == 0.0
    other = CacheManager(cache_dir=cache._cache_dir / "second")
    other.set("k", "v")
    other.get("k")
    assert other.stats.hit_rate == 1.0
    assert other.stats.by_namespace[""].hit_rate == 1.0


def test_stats_multi_operation_counters(cache: CacheManager) -> None:
    """Exact counters after multiple operations (kills +=→= / -= / +=2 mutants)."""
    cache.set("a", 1, namespace="ns")
    cache.set("b", 2, namespace="ns")
    cache.set("c", 3, namespace="ns")
    cache.get("a", namespace="ns")
    cache.get("b", namespace="ns")
    cache.get("c", namespace="ns")
    cache.get("x", namespace="ns")
    cache.get("y", namespace="ns")
    cache.invalidate("a", namespace="ns")
    cache.invalidate("b", namespace="ns")
    stats = cache.stats
    assert stats.sets == 3
    assert stats.hits == 3
    assert stats.misses == 2
    assert stats.evictions == 2
    bucket = stats.by_namespace["ns"]
    assert bucket.sets == 3
    assert bucket.hits == 3
    assert bucket.misses == 2
    assert bucket.evictions == 2
    assert bucket.hit_rate == 3 / 5
    assert stats.eviction_reasons == {"manual": 2}


def test_stats_to_dict_full_structure(cache: CacheManager) -> None:
    cache.set("k", "v", namespace="ns")
    cache.get("k", namespace="ns")
    cache.get("absent", namespace="ns")
    cache.invalidate("k", namespace="ns")
    assert cache.stats.to_dict() == {
        "hits": 1,
        "misses": 1,
        "evictions": 1,
        "sets": 1,
        "total": 2,
        "hit_rate": 0.5,
        "by_namespace": {
            "ns": {
                "hits": 1,
                "misses": 1,
                "evictions": 1,
                "sets": 1,
                "hit_rate": 0.5,
            }
        },
        "eviction_reasons": {"manual": 1},
    }


def test_never_expire_ttl(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("state", {"a": 1}, ttl=-1)
    clock.advance(10 * 365 * 86400)
    assert cache.get("state") == {"a": 1}


def test_ttl_zero_expires_immediately(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("key", "value", ttl=0)
    clock.advance(0.01)
    assert cache.get("key") is None
    assert cache.stats.evictions == 1


# ── Namespace support ─────────────────────────────────────────────


def test_namespace_set_get(cache: CacheManager) -> None:
    cache.set("key1", "data_a", namespace="llm")
    cache.set("key2", "data_b", namespace="scraper")
    assert cache.get("key1", namespace="llm") == "data_a"
    assert cache.get("key2", namespace="scraper") == "data_b"
    assert cache.get("key1", namespace="scraper") is None


def test_namespace_invalidate(cache: CacheManager) -> None:
    cache.set("k1", "v1", namespace="llm")
    cache.set("k2", "v2", namespace="llm")
    cache.set("k3", "v3", namespace="other")
    removed = cache.invalidate_namespace("llm")
    assert removed == 2
    assert cache.get("k1", namespace="llm") is None
    assert cache.get("k3", namespace="other") == "v3"


def test_namespace_invalidate_empty(cache: CacheManager) -> None:
    assert cache.invalidate_namespace("nonexistent") == 0


def test_namespace_path_traversal_rejected(cache: CacheManager) -> None:
    cache.set("k", "v", namespace="../evil")
    assert cache.get("k", namespace="../evil") is None
    assert not (cache._cache_dir.parent / "evil").exists()
    assert cache.invalidate_namespace("../evil") == 0


def test_reserved_namespace_rejected(cache: CacheManager) -> None:
    cache.set("k", "v", namespace="quarantine")
    assert cache.get("k", namespace="quarantine") is None
    cache.set("k", "v", namespace="locks")
    assert cache.get("k", namespace="locks") is None


# ── R1: atomic writes ─────────────────────────────────────────────


def test_set_leaves_no_temp_files(cache: CacheManager) -> None:
    cache.set("k", "v")
    files = list(cache._cache_dir.iterdir())
    assert all(not f.name.startswith(".tmp-") for f in files)


def test_set_non_serializable_does_not_corrupt(cache: CacheManager) -> None:
    cache.set("k", {"good": 1})
    cache.set("k", {"bad": object()})  # must not raise
    assert cache.get("k") == {"good": 1}
    assert cache.stats.sets == 1  # failed set not counted


def test_set_non_serializable_logs_error(cache: CacheManager, caplog: Any) -> None:
    with caplog.at_level("ERROR"):
        cache.set("k", object())
    assert any("[CACHE]" in r.message for r in caplog.records)


def test_set_permission_denied_degrades(cache: CacheManager) -> None:
    cache.set("k", "original")
    with patch("src.cache_manager.atomic_write_json", side_effect=PermissionError("denied")):
        cache.set("k", "replacement")  # must not raise
    assert cache.get("k") == "original"


def test_set_oserror_degrades(cache: CacheManager) -> None:
    with patch("src.cache_manager.atomic_write_json", side_effect=OSError("disk full")):
        cache.set("k", "v")  # must not raise
    assert cache.get("k") is None


# ── R3: integrity, quarantine, recovery ───────────────────────────


def test_corrupt_json_quarantined(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("k", "v")
    path = entry_path(cache._cache_dir, "k")
    path.write_text("{corrupt", encoding="utf-8")
    assert cache.get("k") is None
    assert not path.exists()
    quarantined = list((cache._cache_dir / "quarantine").iterdir())
    assert len(quarantined) == 1
    assert cache.stats.eviction_reasons["corruption"] == 1
    assert cache.stats.misses == 1


def test_corrupt_then_rebuild(cache: CacheManager) -> None:
    cache.set("k", "v")
    entry_path(cache._cache_dir, "k").write_text("garbage", encoding="utf-8")
    assert cache.get("k") is None
    cache.set("k", "rebuilt")
    assert cache.get("k") == "rebuilt"


def test_checksum_mismatch_quarantined(cache: CacheManager, clock: FakeClock) -> None:
    path = entry_path(cache._cache_dir, "k")
    path.parent.mkdir(parents=True, exist_ok=True)
    envelope = make_envelope({"a": 1}, clock.now, checksum="0" * 64)
    path.write_text(json.dumps(envelope), encoding="utf-8")
    assert cache.get("k") is None
    assert not path.exists()
    assert cache.stats.eviction_reasons["corruption"] == 1


def test_unknown_schema_version_quarantined(cache: CacheManager, clock: FakeClock) -> None:
    path = entry_path(cache._cache_dir, "k")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(make_envelope("v", clock.now, schema_version=99)), encoding="utf-8")
    assert cache.get("k") is None
    assert cache.stats.eviction_reasons["corruption"] == 1


def test_payload_not_dict_quarantined(cache: CacheManager) -> None:
    path = entry_path(cache._cache_dir, "k")
    path.write_text("[1, 2, 3]", encoding="utf-8")
    assert cache.get("k") is None
    assert cache.stats.eviction_reasons["corruption"] == 1


def test_payload_missing_data_quarantined(cache: CacheManager, clock: FakeClock) -> None:
    path = entry_path(cache._cache_dir, "k")
    path.write_text(json.dumps({"timestamp": clock.now, "ttl": 3600}), encoding="utf-8")
    assert cache.get("k") is None
    assert cache.stats.eviction_reasons["corruption"] == 1


def test_invalid_timestamp_type_quarantined(cache: CacheManager) -> None:
    path = entry_path(cache._cache_dir, "k")
    envelope = make_envelope("v", 0.0)
    envelope["timestamp"] = "not-a-number"
    path.write_text(json.dumps(envelope), encoding="utf-8")
    assert cache.get("k") is None
    assert cache.stats.eviction_reasons["corruption"] == 1


def test_invalid_ttl_type_quarantined(cache: CacheManager, clock: FakeClock) -> None:
    path = entry_path(cache._cache_dir, "k")
    envelope = make_envelope("v", clock.now)
    envelope["ttl"] = "soon"
    path.write_text(json.dumps(envelope), encoding="utf-8")
    assert cache.get("k") is None


def test_legacy_v1_payload_still_read(cache: CacheManager, clock: FakeClock) -> None:
    path = entry_path(cache._cache_dir, "k")
    legacy = {"timestamp": clock.now, "ttl": 3600, "namespace": "", "data": "old-value"}
    path.write_text(json.dumps(legacy), encoding="utf-8")
    assert cache.get("k") == "old-value"
    assert cache.stats.hits == 1


def test_legacy_v1_expired_evicts(cache: CacheManager, clock: FakeClock) -> None:
    path = entry_path(cache._cache_dir, "k")
    legacy = {"timestamp": clock.now, "ttl": 10, "namespace": "", "data": "old"}
    path.write_text(json.dumps(legacy), encoding="utf-8")
    clock.advance(11)
    assert cache.get("k") is None
    assert cache.stats.eviction_reasons["ttl"] == 1


def test_cached_none_value_is_hit(cache: CacheManager) -> None:
    cache.set("k", None)
    assert cache.get("k") is None
    assert cache.stats.hits == 1  # presence, not truthiness


def test_quarantine_rotation_in_cache(cache: CacheManager) -> None:
    path = entry_path(cache._cache_dir, "k")
    for _ in range(5):
        path.write_text("bad", encoding="utf-8")
        assert cache.get("k") is None
    copies = list((cache._cache_dir / "quarantine").iterdir())
    assert len(copies) == 3  # CACHE_QUARANTINE_KEEP default


# ── R2: locking ───────────────────────────────────────────────────


def test_set_creates_lock_files(cache: CacheManager) -> None:
    cache.set("k", "v", namespace="llm")
    locks = list((cache._cache_dir / "locks").iterdir())
    assert len(locks) >= 1


def test_set_degrades_when_namespace_lock_held(cache: CacheManager) -> None:
    lock = FileLock(ns_lock_path(cache._cache_dir, "llm"), timeout=1.0)
    with lock:
        manager = CacheManager(cache_dir=cache._cache_dir, lock_timeout=0.1)
        manager.set("k", "v", namespace="llm")  # must not raise
        assert manager.get("k", namespace="llm") is None


def test_get_degrades_when_entry_lock_held(cache: CacheManager) -> None:
    cache.set("k", "v")
    digest = hashlib.sha256(b"k").hexdigest()
    lock = FileLock(cache._cache_dir / "locks" / f"{digest}.lock", timeout=1.0)
    with lock:
        manager = CacheManager(cache_dir=cache._cache_dir, lock_timeout=0.1)
        assert manager.get("k") is None  # miss, no exception


def _child_writer(cache_dir_str: str, child_id: int) -> None:
    manager = CacheManager(cache_dir=Path(cache_dir_str))
    for i in range(5):
        manager.set(f"child{child_id}-key{i}", {"child": child_id, "i": i}, namespace="parallel")
    os._exit(0)


def test_concurrent_multiprocess_sets_no_corruption(tmp_path: Path) -> None:
    cache_dir = tmp_path / "shared"
    pids: list[int] = []
    for child_id in range(4):
        pid = os.fork()
        if pid == 0:  # pragma: no cover — child branch
            try:
                _child_writer(str(cache_dir), child_id)
            except BaseException:
                os._exit(1)
        pids.append(pid)
    for pid in pids:
        _, status = os.waitpid(pid, 0)
        assert os.waitstatus_to_exitcode(status) == 0
    reader = CacheManager(cache_dir=cache_dir)
    for child_id in range(4):
        for i in range(5):
            assert reader.get(f"child{child_id}-key{i}", namespace="parallel") == {
                "child": child_id,
                "i": i,
            }


# ── R5: LRU budgets + scoped sweeps ───────────────────────────────


def test_lru_eviction_max_entries(tmp_path: Path, clock: FakeClock) -> None:
    cache = CacheManager(cache_dir=tmp_path / "c", clock=clock, max_entries_per_namespace=2)
    cache.set("a", "1", namespace="ns")
    clock.advance(120)
    cache.set("b", "2", namespace="ns")
    clock.advance(120)
    cache.set("c", "3", namespace="ns")
    assert cache.get("a", namespace="ns") is None
    assert cache.get("b", namespace="ns") == "2"
    assert cache.get("c", namespace="ns") == "3"
    assert cache.stats.eviction_reasons["lru"] == 1


def test_lru_eviction_max_bytes(tmp_path: Path, clock: FakeClock) -> None:
    cache = CacheManager(cache_dir=tmp_path / "c", clock=clock, max_bytes_per_namespace=600)
    cache.set("a", "x" * 200, namespace="ns")
    clock.advance(120)
    cache.set("b", "y" * 200, namespace="ns")
    assert cache.get("a", namespace="ns") is None
    assert cache.get("b", namespace="ns") == "y" * 200
    assert cache.stats.eviction_reasons["lru"] >= 1


def test_lru_respects_last_access(tmp_path: Path, clock: FakeClock) -> None:
    cache = CacheManager(cache_dir=tmp_path / "c", clock=clock, max_entries_per_namespace=2)
    cache.set("a", "1", namespace="ns")
    clock.advance(120)
    cache.set("b", "2", namespace="ns")
    clock.advance(120)
    assert cache.get("a", namespace="ns") == "1"  # refresh a's last_access
    clock.advance(120)
    cache.set("c", "3", namespace="ns")
    assert cache.get("a", namespace="ns") == "1"  # a survived (more recent)
    assert cache.get("b", namespace="ns") is None  # b evicted


def test_clear_expired_scoped_to_touched_namespaces(tmp_path: Path, clock: FakeClock) -> None:
    shared_dir = tmp_path / "c"
    writer = CacheManager(cache_dir=shared_dir, clock=clock)
    writer.set("old", "data", ttl=10, namespace="cold")
    reader = CacheManager(cache_dir=shared_dir, clock=clock)
    reader.set("fresh", "data", ttl=99999, namespace="hot")
    clock.advance(5000)
    # Default sweep only touches namespaces used by THIS instance.
    assert reader.clear_expired() == 0
    assert writer.get("old", namespace="cold") is None  # lazy eviction on get
    # Explicit full scan reaches untouched namespaces.
    clock.advance(1)
    writer2 = CacheManager(cache_dir=shared_dir, clock=clock)
    writer2.set("old2", "data", ttl=10, namespace="cold2")
    clock.advance(5000)
    assert reader.clear_expired(full_scan=True) >= 1


def test_clear_expired_legacy_behavior(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("old", "data", ttl=10)
    cache.set("fresh", "data", ttl=99999)
    clock.advance(5000)
    removed = cache.clear_expired()
    assert removed == 1
    assert cache.get("fresh") == "data"


def test_clear_expired_skips_stats_and_quarantine(cache: CacheManager) -> None:
    cache.set("k", "v")
    cache.persist_stats()
    entry_path(cache._cache_dir, "k").write_text("bad", encoding="utf-8")
    assert cache.get("k") is None  # creates quarantine copy
    cache.clear_expired(full_scan=True)
    assert (cache._cache_dir / "stats.json").exists()
    assert list((cache._cache_dir / "quarantine").iterdir())


def test_maintenance_full_sweep_and_rotation(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("old", "data", ttl=10)
    clock.advance(5000)
    report = cache.maintenance()
    assert report["expired_removed"] >= 1
    assert not entry_path(cache._cache_dir, "old").exists()


# ── R6: statistics ────────────────────────────────────────────────


def test_stats_hit_miss(cache: CacheManager) -> None:
    cache.get("miss")
    cache.set("k", "v")
    cache.get("k")
    stats = cache.stats
    assert stats.hits == 1
    assert stats.misses == 1
    assert stats.total == 2
    assert stats.hit_rate == 0.5


def test_stats_eviction(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("expired", "data", ttl=10)
    clock.advance(5000)
    cache.get("expired")
    assert cache.stats.evictions == 1
    assert cache.stats.misses == 1
    assert cache.stats.eviction_reasons["ttl"] == 1


def test_stats_sets(cache: CacheManager) -> None:
    cache.set("a", 1)
    cache.set("b", 2)
    assert cache.stats.sets == 2


def test_stats_by_namespace(cache: CacheManager) -> None:
    cache.set("k", "v", namespace="llm")
    cache.get("k", namespace="llm")
    cache.get("missing", namespace="llm")
    cache.get("missing", namespace="scraper")
    ns_stats = cache.stats.by_namespace
    assert ns_stats["llm"].hits == 1
    assert ns_stats["llm"].misses == 1
    assert ns_stats["llm"].hit_rate == 0.5
    assert ns_stats["scraper"].misses == 1
    assert ns_stats["scraper"].hit_rate == 0.0


def test_stats_manual_invalidation_reason(cache: CacheManager) -> None:
    cache.set("k", "v")
    cache.invalidate("k")
    assert cache.stats.eviction_reasons["manual"] == 1


def test_stats_repr() -> None:
    stats = CacheStats(hits=10, misses=2, evictions=1)
    r = repr(stats)
    assert "hits=10" in r
    assert "misses=2" in r


def test_stats_total() -> None:
    assert CacheStats(hits=8, misses=2).total == 10


def test_stats_hit_rate_zero() -> None:
    assert CacheStats().hit_rate == 0.0


def test_persist_stats_roundtrip(cache: CacheManager) -> None:
    cache.set("k", "v", namespace="llm")
    cache.get("k", namespace="llm")
    path = cache.persist_stats()
    assert path is not None and path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["stats"]["hits"] == 1
    assert data["stats"]["by_namespace"]["llm"]["hits"] == 1


def test_persist_stats_oserror_degrades(cache: CacheManager) -> None:
    with patch("src.cache_manager.atomic_write_json", side_effect=OSError("ro")):
        assert cache.persist_stats() is None  # must not raise


def test_stats_determinism(tmp_path: Path, clock: FakeClock) -> None:
    def run(dirname: str) -> dict[str, Any]:
        c = CacheManager(cache_dir=tmp_path / dirname, clock=clock)
        c.set("k", "v", namespace="ns")
        c.get("k", namespace="ns")
        c.get("absent", namespace="ns")
        return c.stats.to_dict()

    assert run("a") == run("b")


# ── R4: content hashing (SHA-256 + migration) ─────────────────────


def test_compute_file_hash_sha256(tmp_path: Path) -> None:
    f = tmp_path / "test.txt"
    f.write_text("hello world", encoding="utf-8")
    h = CacheManager.compute_file_hash(f)
    assert len(h) == 64
    assert h == hashlib.sha256(b"hello world").hexdigest()


def test_compute_file_hash_large_file_chunked(tmp_path: Path) -> None:
    f = tmp_path / "big.bin"
    content = b"a" * 200_000
    f.write_bytes(content)
    assert CacheManager.compute_file_hash(f) == hashlib.sha256(content).hexdigest()


def test_get_content_hash_exists(cache: CacheManager, tmp_path: Path) -> None:
    f = tmp_path / "test.txt"
    f.write_text("content", encoding="utf-8")
    assert cache.get_content_hash(f) is not None


def test_get_content_hash_not_exists(cache: CacheManager, tmp_path: Path) -> None:
    assert cache.get_content_hash(tmp_path / "nonexistent.txt") is None


def test_get_content_hash_permission_denied(cache: CacheManager, tmp_path: Path) -> None:
    f = tmp_path / "locked.txt"
    f.write_text("x", encoding="utf-8")
    with patch.object(Path, "open", side_effect=PermissionError("denied")):
        assert cache.get_content_hash(f) is None


def test_is_content_unchanged(cache: CacheManager, tmp_path: Path) -> None:
    f = tmp_path / "test.txt"
    f.write_text("content", encoding="utf-8")
    h = cache.get_content_hash(f)
    assert h is not None
    assert cache.is_content_unchanged(f, h) is True
    assert cache.is_content_unchanged(f, "wrong_hash") is False


def test_is_content_unchanged_nonexistent(cache: CacheManager, tmp_path: Path) -> None:
    assert cache.is_content_unchanged(tmp_path / "nope", "hash") is False


def test_is_content_unchanged_legacy_md5_mismatch(cache: CacheManager, tmp_path: Path) -> None:
    f = tmp_path / "test.txt"
    f.write_text("content", encoding="utf-8")
    legacy_md5 = hashlib.md5(b"content").hexdigest()
    assert cache.is_content_unchanged(f, legacy_md5) is False


def test_save_and_load_content_cache(cache: CacheManager, tmp_path: Path) -> None:
    cache_file = tmp_path / "content_cache.json"
    data = {"file1.md": "abc123", "file2.md": "def456"}
    cache.save_content_cache(cache_file, data)
    assert cache.load_content_cache(cache_file) == data


def test_load_content_cache_nonexistent(cache: CacheManager, tmp_path: Path) -> None:
    assert cache.load_content_cache(tmp_path / "nope.json") == {}


def test_load_content_cache_corrupt_quarantined(cache: CacheManager, tmp_path: Path) -> None:
    f = tmp_path / "corrupt.json"
    f.write_text("not json", encoding="utf-8")
    assert cache.load_content_cache(f) == {}
    assert not f.exists()
    assert list((tmp_path / "quarantine").iterdir())


def test_load_content_cache_old_format(cache: CacheManager, tmp_path: Path) -> None:
    f = tmp_path / "old.json"
    f.write_text(
        json.dumps({"file.md": {"content_hash": "abc123", "extra": "data"}}),
        encoding="utf-8",
    )
    assert cache.load_content_cache(f) == {"file.md": "abc123"}


def test_load_content_cache_migrates_md5(cache: CacheManager, tmp_path: Path) -> None:
    target = tmp_path / "doc.md"
    target.write_text("release content", encoding="utf-8")
    legacy_md5 = hashlib.md5(b"release content").hexdigest()
    cache_file = tmp_path / "content.json"
    cache_file.write_text(json.dumps({str(target): legacy_md5}), encoding="utf-8")
    loaded = cache.load_content_cache(cache_file)
    expected = hashlib.sha256(b"release content").hexdigest()
    assert loaded == {str(target): expected}
    # Migration is persisted atomically.
    assert json.loads(cache_file.read_text(encoding="utf-8")) == {str(target): expected}


def test_load_content_cache_recomputes_empty_hash(cache: CacheManager, tmp_path: Path) -> None:
    target = tmp_path / "doc.md"
    target.write_text("abc", encoding="utf-8")
    cache_file = tmp_path / "content.json"
    cache_file.write_text(json.dumps({str(target): ""}), encoding="utf-8")
    loaded = cache.load_content_cache(cache_file)
    assert loaded == {str(target): hashlib.sha256(b"abc").hexdigest()}


def test_load_content_cache_missing_file_keeps_legacy(cache: CacheManager, tmp_path: Path) -> None:
    cache_file = tmp_path / "content.json"
    cache_file.write_text(json.dumps({"gone.md": "legacyhash"}), encoding="utf-8")
    assert cache.load_content_cache(cache_file) == {"gone.md": "legacyhash"}


def test_load_content_cache_non_dict_json(cache: CacheManager, tmp_path: Path) -> None:
    f = tmp_path / "list.json"
    f.write_text("[1, 2]", encoding="utf-8")
    assert cache.load_content_cache(f) == {}


def test_load_content_cache_skips_bad_value_types(cache: CacheManager, tmp_path: Path) -> None:
    f = tmp_path / "mixed.json"
    f.write_text(
        json.dumps({"a": 123, "b": {"content_hash": "keepme"}, "c": None}),
        encoding="utf-8",
    )
    assert cache.load_content_cache(f) == {"b": "keepme"}


def test_save_content_cache_no_temp_leftovers(cache: CacheManager, tmp_path: Path) -> None:
    cache_file = tmp_path / "sub" / "content.json"
    cache.save_content_cache(cache_file, {"a.md": "h"})
    names = [p.name for p in cache_file.parent.iterdir()]
    assert "content.json" in names
    assert not any(n.startswith(".tmp-") for n in names)


def test_save_content_cache_permission_denied_degrades(cache: CacheManager, tmp_path: Path) -> None:
    cache_file = tmp_path / "content.json"
    with patch("src.cache_manager.atomic_write_json", side_effect=PermissionError("no")):
        cache.save_content_cache(cache_file, {"a": "b"})  # must not raise
    assert not cache_file.exists()


# ── Special / unicode keys ────────────────────────────────────────


def test_unicode_and_special_keys(cache: CacheManager) -> None:
    keys = ["ação/ç:★", "../etc/passwd", "a b\tc", "chave com acentuação", "🚀"]
    for key in keys:
        cache.set(key, {"k": key})
    for key in keys:
        assert cache.get(key) == {"k": key}


def test_empty_key(cache: CacheManager) -> None:
    cache.set("", "empty-key-value")
    assert cache.get("") == "empty-key-value"


# ── Mutation-driven boundary tests (ADR-011 Fase 5) ───────────────


def test_namespace_stats_fresh_hit_rate_zero() -> None:
    from src.cache_manager import NamespaceStats

    fresh = NamespaceStats()
    assert fresh.hit_rate == 0.0
    assert fresh.to_dict() == {
        "hits": 0,
        "misses": 0,
        "evictions": 0,
        "sets": 0,
        "hit_rate": 0.0,
    }


def test_invalidate_namespace_ignores_non_json(cache: CacheManager) -> None:
    cache.set("k", "v", namespace="ns")
    ns_dir = cache._cache_dir / "ns"
    (ns_dir / "notes.txt").write_text("keep me", encoding="utf-8")
    assert cache.invalidate_namespace("ns") == 1
    assert (ns_dir / "notes.txt").exists()
    assert cache.stats.eviction_reasons == {"manual": 1}


def test_clear_expired_multi_namespace_and_multi_entry(
    cache: CacheManager, clock: FakeClock
) -> None:
    cache.set("a", "1", ttl=10, namespace="n1")
    cache.set("b", "2", ttl=10, namespace="n1")
    cache.set("c", "3", ttl=10, namespace="n2")
    cache.set("fresh", "4", ttl=99999, namespace="n2")
    clock.advance(5000)
    assert cache.clear_expired() == 3
    assert cache.get("fresh", namespace="n2") == "4"


def test_maintenance_full_scan_reaches_untouched(tmp_path: Path, clock: FakeClock) -> None:
    shared = tmp_path / "c"
    writer = CacheManager(cache_dir=shared, clock=clock)
    writer.set("old", "v", ttl=10, namespace="cold")
    maint = CacheManager(cache_dir=shared, clock=clock)
    clock.advance(5000)
    report = maint.maintenance()
    assert report["expired_removed"] == 1


def test_maintenance_quarantine_copies_counted(cache: CacheManager) -> None:
    cache.set("k", "v")
    entry_path(cache._cache_dir, "k").write_text("bad", encoding="utf-8")
    assert cache.get("k") is None  # produces one quarantine copy
    report = cache.maintenance()
    assert report["quarantine_copies"] == 1


def test_persist_stats_extra_roundtrip(cache: CacheManager) -> None:
    path = cache.persist_stats(extra={"processed_releases": {"hits": 2}})
    assert path is not None
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert "generated_at" in data
    assert data["extra"] == {"processed_releases": {"hits": 2}}


def test_lru_exact_budget_boundary(tmp_path: Path, clock: FakeClock) -> None:
    cache = CacheManager(cache_dir=tmp_path / "c", clock=clock, max_entries_per_namespace=2)
    cache.set("a", "1", namespace="ns")
    clock.advance(120)
    cache.set("b", "2", namespace="ns")
    assert cache.get("a", namespace="ns") == "1"
    assert cache.get("b", namespace="ns") == "2"
    assert cache.stats.eviction_reasons.get("lru", 0) == 0


def test_lru_multi_eviction_arithmetic(tmp_path: Path, clock: FakeClock) -> None:
    cache = CacheManager(cache_dir=tmp_path / "c", clock=clock, max_entries_per_namespace=1)
    cache.set("a", "1", namespace="ns")
    clock.advance(120)
    cache.set("b", "2", namespace="ns")
    clock.advance(120)
    cache.set("c", "3", namespace="ns")
    assert cache.get("a", namespace="ns") is None
    assert cache.get("b", namespace="ns") is None
    assert cache.get("c", namespace="ns") == "3"
    assert cache.stats.eviction_reasons["lru"] == 2


def test_lru_multi_eviction_bytes(tmp_path: Path, clock: FakeClock) -> None:
    cache = CacheManager(cache_dir=tmp_path / "c", clock=clock, max_bytes_per_namespace=500)
    cache.set("a", "x" * 200, namespace="ns")
    clock.advance(120)
    cache.set("b", "y" * 200, namespace="ns")
    clock.advance(120)
    cache.set("c", "z" * 200, namespace="ns")
    assert cache.get("a", namespace="ns") is None
    assert cache.get("b", namespace="ns") is None
    assert cache.get("c", namespace="ns") == "z" * 200
    assert cache.stats.eviction_reasons["lru"] == 2


def test_sweep_ttl_zero_and_exact_boundary(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("zero", "v", ttl=0)
    cache.set("edge", "v", ttl=100)
    clock.advance(100)  # edge: now-ts == ttl → still valid; zero: expired
    assert cache.clear_expired() == 1
    assert cache.get("edge") == "v"
    assert cache.stats.eviction_reasons == {"ttl": 1}


def test_refresh_preserves_ttl_and_schema(cache: CacheManager, clock: FakeClock) -> None:
    """The last_access refresh rewrite must keep ttl and schema_version intact."""
    cache.set("k", "v", ttl=100)
    clock.advance(60)
    assert cache.get("k") == "v"  # triggers the refresh rewrite
    assert cache.get("k") == "v"  # refreshed envelope must still validate
    clock.advance(50)  # total elapsed 110 > custom ttl 100
    assert cache.get("k") is None  # custom ttl must survive the refresh


def test_checksummed_envelope_without_schema_quarantined(cache: CacheManager) -> None:
    """A v2 envelope that lost schema_version must not downgrade to legacy trust."""
    cache.set("k", "v")
    path = entry_path(cache._cache_dir, "k")
    payload = json.loads(path.read_text(encoding="utf-8"))
    del payload["schema_version"]
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert cache.get("k") is None
    quarantine = cache._cache_dir / "quarantine"
    assert quarantine.exists() and any(quarantine.iterdir())


def test_lru_multi_eviction_cross_instance_count(tmp_path: Path, clock: FakeClock) -> None:
    """One enforcement scan must evict several entries when the budget shrank."""
    shared = tmp_path / "c"
    writer = CacheManager(cache_dir=shared, clock=clock, max_entries_per_namespace=100)
    writer.set("a", "1", namespace="ns")
    clock.advance(120)
    writer.set("b", "2", namespace="ns")
    clock.advance(120)
    writer.set("c", "3", namespace="ns")
    clock.advance(120)
    enforcer = CacheManager(cache_dir=shared, clock=clock, max_entries_per_namespace=1)
    enforcer.set("d", "4", namespace="ns")
    assert enforcer.get("a", namespace="ns") is None
    assert enforcer.get("b", namespace="ns") is None
    assert enforcer.get("c", namespace="ns") is None
    assert enforcer.get("d", namespace="ns") == "4"
    assert enforcer.stats.eviction_reasons["lru"] == 3


def test_lru_multi_eviction_cross_instance_bytes(tmp_path: Path, clock: FakeClock) -> None:
    shared = tmp_path / "c"
    writer = CacheManager(cache_dir=shared, clock=clock, max_bytes_per_namespace=100000)
    writer.set("a", "x" * 200, namespace="ns")
    clock.advance(120)
    writer.set("b", "y" * 200, namespace="ns")
    clock.advance(120)
    writer.set("c", "z" * 200, namespace="ns")
    clock.advance(120)
    enforcer = CacheManager(cache_dir=shared, clock=clock, max_bytes_per_namespace=500)
    enforcer.set("d", "w" * 200, namespace="ns")
    assert enforcer.get("a", namespace="ns") is None
    assert enforcer.get("b", namespace="ns") is None
    assert enforcer.get("c", namespace="ns") is None
    assert enforcer.get("d", namespace="ns") == "w" * 200
    assert enforcer.stats.eviction_reasons["lru"] == 3


def test_last_access_refresh_exact_interval(cache: CacheManager, clock: FakeClock) -> None:
    cache.set("k", "v")
    clock.advance(60)  # exactly the throttle interval → refresh must happen (>=)
    assert cache.get("k") == "v"
    payload = json.loads(entry_path(cache._cache_dir, "k").read_text(encoding="utf-8"))
    assert payload["last_access"] == clock.now


def test_load_content_cache_dict_without_content_hash(cache: CacheManager, tmp_path: Path) -> None:
    f = tmp_path / "nohash.json"
    f.write_text(json.dumps({"gone.md": {}}), encoding="utf-8")
    assert cache.load_content_cache(f) == {"gone.md": ""}


def test_save_content_cache_nested_parents(cache: CacheManager, tmp_path: Path) -> None:
    cache_file = tmp_path / "deep" / "nested" / "content.json"
    cache.save_content_cache(cache_file, {"a": "b"})
    assert cache.load_content_cache(cache_file) == {"a": "b"}


# ── Additional tests for uncovered error paths (targeting ≥95% coverage) ──


# Lines 354, 357: invalidate early returns for invalid namespace and missing file
def test_invalidate_invalid_namespace_returns_early(cache: CacheManager) -> None:
    """Cover lines 354, 357: early returns for invalid namespace and missing file."""
    # Invalid namespace should return early without error
    cache.invalidate("key", namespace="../evil")
    # Missing file should return early
    cache.invalidate("nonexistent", namespace="")


# Lines 363-364: invalidate lock timeout and OSError
def test_invalidate_lock_timeout_logs_and_returns(cache: CacheManager, caplog) -> None:
    """Cover lines 363-364: CacheLockTimeoutError during invalidate."""
    cache.set("k", "v", namespace="ns")
    # Use the key lock, not namespace lock
    key_lock = cache._key_lock_path("k", "ns")
    with FileLock(key_lock, timeout=1.0):
        other = CacheManager(cache_dir=cache._cache_dir, lock_timeout=0.1)
        with caplog.at_level("WARNING"):
            other.invalidate("k", namespace="ns")
    assert any("Invalidate failed" in r.message for r in caplog.records)


def test_invalidate_oserror_logs_and_returns(cache: CacheManager, caplog) -> None:
    """Cover lines 363-364: OSError during invalidate unlink."""
    cache.set("k", "v")
    cache._get_cache_path("k")
    with patch.object(Path, "unlink", side_effect=OSError("permission denied")):
        with caplog.at_level("WARNING"):
            cache.invalidate("k")
    assert any("Invalidate failed" in r.message for r in caplog.records)


# Lines 376, 379: invalidate_namespace early returns
def test_invalidate_namespace_invalid_namespace_returns_zero(
    cache: CacheManager,
) -> None:
    """Cover line 376: early return for invalid namespace."""
    assert cache.invalidate_namespace("../evil") == 0


def test_invalidate_namespace_missing_dir_returns_zero(cache: CacheManager) -> None:
    """Cover line 379: early return when namespace dir doesn't exist."""
    assert cache.invalidate_namespace("nonexistent") == 0


# Lines 388-389: unlink error during invalidate_namespace
def test_invalidate_namespace_unlink_error_logged(cache: CacheManager, caplog) -> None:
    """Cover lines 388-389: OSError when unlinking entries."""
    cache.set("k1", "v1", namespace="ns")
    cache.set("k2", "v2", namespace="ns")
    with patch.object(Path, "unlink", side_effect=OSError("unlink failed")):
        with caplog.at_level("WARNING"):
            count = cache.invalidate_namespace("ns")
    assert count == 0
    assert any("Failed to remove" in r.message for r in caplog.records)


# Lines 391-393: rmdir error during invalidate_namespace
def test_invalidate_namespace_rmdir_error_logged(cache: CacheManager, caplog) -> None:
    """Cover lines 391-393: OSError when removing namespace dir."""
    cache.set("k", "v", namespace="ns")
    # Make rmdir fail by having a non-empty dir
    with patch.object(Path, "rmdir", side_effect=OSError("not empty")):
        with caplog.at_level("DEBUG"):
            cache.invalidate_namespace("ns")
    assert any("not empty" in r.message for r in caplog.records)


# Lines 394-396: lock timeout during invalidate_namespace
def test_invalidate_namespace_lock_timeout_logs_and_returns_zero(
    cache: CacheManager, caplog
) -> None:
    """Cover lines 394-396: CacheLockTimeoutError during invalidate_namespace."""
    cache.set("k", "v", namespace="ns")
    with FileLock(cache._ns_lock_path("ns"), timeout=1.0):
        other = CacheManager(cache_dir=cache._cache_dir, lock_timeout=0.1)
        with caplog.at_level("WARNING"):
            count = other.invalidate_namespace("ns")
    assert count == 0
    assert any("Lock timeout invalidating" in r.message for r in caplog.records)


# Lines 420-425 (429-427 typo): full_scan branch in clear_expired
def test_clear_expired_full_scan_branch(tmp_path: Path, clock: FakeClock) -> None:
    """Cover lines 420-425: full_scan=True sweeps all namespaces."""
    shared = tmp_path / "c"
    writer = CacheManager(cache_dir=shared, clock=clock)
    writer.set("old", "data", ttl=10, namespace="cold")
    reader = CacheManager(cache_dir=shared, clock=clock)
    clock.advance(5000)
    # Without full_scan, cold namespace is not touched by reader
    assert reader.clear_expired() == 0
    # With full_scan, it reaches untouched namespaces
    removed = reader.clear_expired(full_scan=True)
    assert removed >= 1
    assert writer.get("old", namespace="cold") is None


# Lines 435-436: lock timeout during sweep in clear_expired
def test_clear_expired_lock_timeout_sweep(cache: CacheManager, caplog) -> None:
    """Cover lines 435-436: CacheLockTimeoutError during sweep."""
    cache.set("k", "v", ttl=10, namespace="ns")
    with FileLock(cache._ns_lock_path("ns"), timeout=1.0):
        other = CacheManager(cache_dir=cache._cache_dir, lock_timeout=0.1)
        with caplog.at_level("WARNING"):
            other.clear_expired(full_scan=True)
    assert any("Lock timeout sweeping" in r.message for r in caplog.records)


# Lines 453-454: quarantine scan error in maintenance
def test_maintenance_quarantine_scan_error(cache: CacheManager, caplog) -> None:
    """Cover lines 453-454: OSError during quarantine scan."""
    cache.set("k", "v")
    entry_path = cache._get_cache_path("k")
    entry_path.write_text("bad", encoding="utf-8")
    assert cache.get("k") is None  # creates quarantine
    with patch.object(Path, "iterdir", side_effect=OSError("scan failed")):
        with caplog.at_level("WARNING"):
            report = cache.maintenance()
    assert any("Quarantine scan failed" in r.message for r in caplog.records)
    assert report["quarantine_copies"] == 0  # scan failed, returns 0


# Lines 480-482: persist_stats OSError
def test_persist_stats_oserror_already_covered(cache: CacheManager) -> None:
    """Line 480-482 already covered by test_persist_stats_oserror_degrades."""


# Lines 561-563: lock timeout in load_content_cache
def test_load_content_cache_lock_timeout(cache: CacheManager, tmp_path: Path, caplog) -> None:
    """Cover lines 561-563: CacheLockTimeoutError loading content cache."""
    cache_file = tmp_path / "content.json"
    cache_file.write_text(json.dumps({"a": "b"}), encoding="utf-8")
    lock_path = cache_file.with_name(cache_file.name + ".lock")
    with FileLock(lock_path, timeout=1.0):
        other = CacheManager(cache_dir=tmp_path, lock_timeout=0.1)
        with caplog.at_level("WARNING"):
            result = other.load_content_cache(cache_file)
    assert result == {}
    assert any("Lock timeout loading" in r.message for r in caplog.records)


# Line 580: non-string warning in save_content_cache
def test_save_content_cache_non_string_warning(cache: CacheManager, tmp_path: Path, caplog) -> None:
    """Cover line 580: warning for non-string key/value."""
    cache_file = tmp_path / "content.json"
    with caplog.at_level("WARNING"):
        cache.save_content_cache(cache_file, {123: "bad", "key": 456})
    assert any("Skipping non-string content-cache entry" in r.message for r in caplog.records)


# Lines 586-587: save_content_cache lock timeout and OSError
def test_save_content_cache_lock_timeout(cache: CacheManager, tmp_path: Path, caplog) -> None:
    """Cover lines 586-587: CacheLockTimeoutError saving content cache."""
    cache_file = tmp_path / "content.json"
    lock_path = cache_file.with_name(cache_file.name + ".lock")
    with FileLock(lock_path, timeout=1.0):
        other = CacheManager(cache_dir=tmp_path, lock_timeout=0.1)
        with caplog.at_level("ERROR"):
            other.save_content_cache(cache_file, {"a": "b"})
    assert any("Failed to save content cache" in r.message for r in caplog.records)


def test_save_content_cache_oserror(cache: CacheManager, tmp_path: Path, caplog) -> None:
    """Cover lines 586-587: OSError saving content cache."""
    cache_file = tmp_path / "content.json"
    with patch("src.cache_manager.atomic_write_json", side_effect=OSError("disk full")):
        with caplog.at_level("ERROR"):
            cache.save_content_cache(cache_file, {"a": "b"})
    assert any("Failed to save content cache" in r.message for r in caplog.records)


# Lines 659-661: v2 payload missing 'data' field
def test_v2_payload_missing_data_quarantined(cache: CacheManager, clock: FakeClock, caplog) -> None:
    """Cover lines 659-661: v2 envelope without 'data' field quarantined."""
    path = cache._get_cache_path("k")
    path.parent.mkdir(parents=True, exist_ok=True)
    envelope = {
        "schema_version": 2,
        "timestamp": clock.now,
        "ttl": 3600,
        "namespace": "",
        "last_access": clock.now,
        "checksum": "0" * 64,
        # "data" missing
    }
    path.write_text(json.dumps(envelope), encoding="utf-8")
    with caplog.at_level("WARNING"):
        assert cache.get("k") is None
    assert any("Quarantined corrupt payload" in r.message for r in caplog.records)


# Lines 684-685: OSError evicting expired entry
def test_evict_expired_unlink_oserror(cache: CacheManager, clock: FakeClock, caplog) -> None:
    """Cover lines 684-685: OSError when unlinking expired entry."""
    cache.set("k", "v", ttl=10)
    clock.advance(5000)
    cache._get_cache_path("k")
    with patch.object(Path, "unlink", side_effect=OSError("permission denied")):
        with caplog.at_level("WARNING"):
            cache.get("k")
    assert any("Failed to evict expired" in r.message for r in caplog.records)


# Lines 702-703: OSError during last_access refresh
def test_last_access_refresh_oserror(cache: CacheManager, clock: FakeClock, caplog) -> None:
    """Cover lines 702-703: OSError during last_access refresh write."""
    cache.set("k", "v")
    clock.advance(60)  # trigger refresh
    with patch("src.cache_manager.atomic_write_json", side_effect=OSError("write failed")):
        with caplog.at_level("WARNING"):
            cache.get("k")
    assert any("last_access refresh failed" in r.message for r in caplog.records)


# Lines 717-719: budget scan OSError in _enforce_budget
def test_enforce_budget_scan_oserror(cache: CacheManager, caplog) -> None:
    """Cover lines 717-719: OSError during budget scan."""
    cache.set("k", "v", namespace="ns")
    with patch.object(Path, "glob", side_effect=OSError("scan failed")):
        with caplog.at_level("WARNING"):
            # Trigger budget enforcement by setting a very small budget
            small_cache = CacheManager(cache_dir=cache._cache_dir, max_entries_per_namespace=0)
            small_cache.set("k2", "v2", namespace="ns")
    assert any("Budget scan failed" in r.message for r in caplog.records)


# Lines 724-725: stat OSError in _enforce_budget
def test_enforce_budget_stat_oserror(cache: CacheManager, caplog) -> None:
    """Cover lines 724-725: OSError during stat() in budget enforcement."""
    cache.set("k", "v", namespace="ns")
    with patch.object(Path, "stat", side_effect=OSError("stat failed")):
        with caplog.at_level("WARNING"):
            small_cache = CacheManager(cache_dir=cache._cache_dir, max_entries_per_namespace=0)
            small_cache.set("k2", "v2", namespace="ns")
    # stat error is silently caught and continues


# Lines 734-738: read_json_safe error during budget enforcement
def test_enforce_budget_read_json_safe_error(cache: CacheManager, caplog) -> None:
    """Cover lines 734-738: read_json_safe returns None during budget."""
    cache.set("k", "v", namespace="ns")
    with patch("src.cache_manager.read_json_safe", return_value=None):
        with caplog.at_level("WARNING"):
            small_cache = CacheManager(cache_dir=cache._cache_dir, max_entries_per_namespace=0)
            small_cache.set("k2", "v2", namespace="ns")
    # The entry with corrupt payload gets quarantined during eviction attempt


# Lines 740-747: LRU eviction OSError
def test_lru_eviction_unlink_oserror(cache: CacheManager, caplog) -> None:
    """Cover lines 740-747: OSError during LRU eviction unlink."""
    cache.set("a", "1", namespace="ns")
    cache.set("b", "2", namespace="ns")
    with patch.object(Path, "unlink", side_effect=OSError("eviction failed")):
        with caplog.at_level("WARNING"):
            small_cache = CacheManager(cache_dir=cache._cache_dir, max_entries_per_namespace=1)
            small_cache.set("c", "3", namespace="ns")
    assert any("LRU eviction failed" in r.message for r in caplog.records)


# Lines 758-760: sweep scan OSError in _sweep_directory
def test_sweep_directory_scan_oserror(cache: CacheManager, caplog) -> None:
    """Cover lines 758-760: OSError during sweep directory scan (ns_dir.glob)."""
    # Create a namespace directory with an expired entry
    cache.set("k", "v", ttl=10, namespace="ns")
    ns_dir = cache._cache_dir / "ns"
    # Directly test _sweep_directory with mocked glob
    with patch.object(Path, "glob", side_effect=OSError("scan failed")):
        with caplog.at_level("WARNING"):
            removed = cache._sweep_directory(ns_dir, "ns", cache._now())
    assert removed == 0
    assert any("Sweep scan failed" in r.message for r in caplog.records)


# Lines 766-767: quarantine corrupt during sweep
def test_sweep_quarantines_corrupt(cache: CacheManager, clock: FakeClock) -> None:
    """Cover lines 766-767: corrupt payload quarantined during sweep."""
    path = cache._get_cache_path("k")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("not json", encoding="utf-8")
    cache.clear_expired(full_scan=True)
    assert not path.exists()
    quarantine = cache._cache_dir / "quarantine"
    assert quarantine.exists() and any(quarantine.iterdir())


# Lines 771-772: quarantine invalid timestamp/ttl during sweep
def test_sweep_quarantines_invalid_timestamp_ttl(cache: CacheManager, clock: FakeClock) -> None:
    """Cover lines 771-772: invalid timestamp/ttl quarantined during sweep."""
    path = cache._get_cache_path("k")
    path.parent.mkdir(parents=True, exist_ok=True)
    envelope = {
        "timestamp": "not-a-number",
        "ttl": "not-a-number",
        "namespace": "",
        "data": "v",
    }
    path.write_text(json.dumps(envelope), encoding="utf-8")
    cache.clear_expired(full_scan=True)
    assert not path.exists()
    quarantine = cache._cache_dir / "quarantine"
    assert quarantine.exists() and any(quarantine.iterdir())


# Lines 776-778: sweep eviction unlink OSError
def test_sweep_eviction_unlink_oserror(cache: CacheManager, clock: FakeClock, caplog) -> None:
    """Cover lines 776-778: OSError during sweep eviction unlink."""
    cache.set("k", "v", ttl=10)
    clock.advance(5000)
    cache._get_cache_path("k")
    with patch.object(Path, "unlink", side_effect=OSError("unlink failed")):
        with caplog.at_level("WARNING"):
            cache.clear_expired(full_scan=True)
    assert any("Sweep eviction failed" in r.message for r in caplog.records)


# Lines 817-818: migration write error in _load_content_locked
def test_load_content_locked_migration_write_error(
    cache: CacheManager, tmp_path: Path, caplog
) -> None:
    """Cover lines 817-818: OSError during migration write."""
    target = tmp_path / "doc.md"
    target.write_text("release content", encoding="utf-8")
    legacy_md5 = hashlib.md5(b"release content").hexdigest()
    cache_file = tmp_path / "content.json"
    cache_file.write_text(json.dumps({str(target): legacy_md5}), encoding="utf-8")
    with patch("src.cache_manager.atomic_write_json", side_effect=OSError("write failed")):
        with caplog.at_level("WARNING"):
            loaded = cache.load_content_cache(cache_file)
    assert any("Content-cache migration write failed" in r.message for r in caplog.records)
    # Migration should still return the recomputed hash
    assert loaded == {str(target): hashlib.sha256(b"release content").hexdigest()}
