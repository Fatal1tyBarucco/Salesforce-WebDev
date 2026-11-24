"""Tests for src/processed_releases.py — fingerprinting, state recovery, single-flight.

Deterministic: injected clock, fork + pipes for concurrency (no sleeps).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from src.cache_io import FileLock, compute_checksum
from src.config import ReleaseInfo
from src.processed_releases import (
    ProcessedReleasesStore,
    compute_release_fingerprint,
)

RELEASE = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")


@pytest.fixture
def store(tmp_path: Path) -> ProcessedReleasesStore:
    return ProcessedReleasesStore(cache_dir=tmp_path / "cache", lock_timeout=2.0)


@pytest.fixture
def release_dir(tmp_path: Path) -> Path:
    d = tmp_path / "releases" / "summer_26"
    d.mkdir(parents=True)
    return d


def write_meta(release_dir: Path, total: int = 10) -> None:
    meta = {
        "name": RELEASE.name,
        "slug": RELEASE.slug,
        "release_id": RELEASE.release_id,
        "total_features": total,
        "generated_at": "2026-06-26T22:38:22+00:00",
        "categories": [{"name": "Automação", "count": total}],
    }
    (release_dir / ".meta.json").write_text(json.dumps(meta), encoding="utf-8")


def write_md(release_dir: Path, text: str = "# Feature\n- item") -> None:
    sub = release_dir / "pt_BR"
    sub.mkdir(exist_ok=True)
    (sub / "automacao.md").write_text(text, encoding="utf-8")


def fp(release_dir: Path, parser_version: str = "1") -> str:
    return compute_release_fingerprint(
        release_dir,
        name=RELEASE.name,
        release_id=RELEASE.release_id,
        slug=RELEASE.slug,
        parser_version=parser_version,
    )


# ── Fingerprint determinism (R7) ──────────────────────────────────


def test_fingerprint_deterministic(release_dir: Path) -> None:
    write_meta(release_dir)
    write_md(release_dir)
    assert fp(release_dir) == fp(release_dir)
    assert len(fp(release_dir)) == 64


def test_fingerprint_ignores_meta_key_order(release_dir: Path) -> None:
    write_meta(release_dir)
    before = fp(release_dir)
    meta = json.loads((release_dir / ".meta.json").read_text(encoding="utf-8"))
    reordered = dict(reversed(list(meta.items())))
    (release_dir / ".meta.json").write_text(json.dumps(reordered), encoding="utf-8")
    assert fp(release_dir) == before


def test_fingerprint_changes_with_meta(release_dir: Path) -> None:
    write_meta(release_dir, total=10)
    before = fp(release_dir)
    write_meta(release_dir, total=11)
    assert fp(release_dir) != before


def test_fingerprint_changes_with_content(release_dir: Path) -> None:
    write_meta(release_dir)
    write_md(release_dir, "# v1")
    before = fp(release_dir)
    write_md(release_dir, "# v2")
    assert fp(release_dir) != before


def test_fingerprint_changes_with_parser_version(release_dir: Path) -> None:
    write_meta(release_dir)
    assert fp(release_dir, "1") != fp(release_dir, "2")


def test_fingerprint_ignores_generated_at(release_dir: Path) -> None:
    write_meta(release_dir)
    before = fp(release_dir)
    meta = json.loads((release_dir / ".meta.json").read_text(encoding="utf-8"))
    meta["generated_at"] = "2027-01-01T00:00:00+00:00"
    (release_dir / ".meta.json").write_text(json.dumps(meta), encoding="utf-8")
    assert fp(release_dir) == before


def test_fingerprint_missing_dir_degrades(tmp_path: Path) -> None:
    missing = tmp_path / "gone"
    value = fp(missing)
    assert len(value) == 64
    assert fp(missing) == value


def test_fingerprint_corrupt_meta_degrades(release_dir: Path) -> None:
    (release_dir / ".meta.json").write_text("{bad", encoding="utf-8")
    assert len(fp(release_dir)) == 64


def test_fingerprint_non_dict_meta_degrades(release_dir: Path) -> None:
    (release_dir / ".meta.json").write_text("[1,2]", encoding="utf-8")
    assert len(fp(release_dir)) == 64


def test_fingerprint_bad_category_types_degrade(release_dir: Path) -> None:
    meta: dict[str, Any] = {
        "name": RELEASE.name,
        "categories": ["not-a-dict", {"name": 123, "count": "many"}, {"name": "Ok", "count": 2}],
    }
    (release_dir / ".meta.json").write_text(json.dumps(meta), encoding="utf-8")
    assert len(fp(release_dir)) == 64


# ── State store: mark / check / recovery (R3, R7) ─────────────────


def test_mark_and_is_processed(store: ProcessedReleasesStore, release_dir: Path) -> None:
    write_meta(release_dir)
    fingerprint = fp(release_dir)
    assert store.is_processed(RELEASE.slug, fingerprint) is False
    store.mark_processed(RELEASE.slug, fingerprint, release=RELEASE)
    assert store.is_processed(RELEASE.slug, fingerprint) is True
    assert store.stats.hits == 1
    assert store.stats.misses == 1


def test_different_fingerprint_is_miss(store: ProcessedReleasesStore, release_dir: Path) -> None:
    write_meta(release_dir)
    store.mark_processed(RELEASE.slug, fp(release_dir), release=RELEASE)
    write_meta(release_dir, total=99)
    assert store.is_processed(RELEASE.slug, fp(release_dir)) is False


def test_state_file_has_schema_and_checksum(
    store: ProcessedReleasesStore, release_dir: Path
) -> None:
    write_meta(release_dir)
    store.mark_processed(RELEASE.slug, fp(release_dir), release=RELEASE)
    state_path = store._cache_dir / "processed_releases.json"
    data = json.loads(state_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    body = {"releases": data["releases"], "history": data["history"]}
    assert data["checksum"] == compute_checksum(body)


def test_corrupt_state_quarantined_and_rebuilt(
    store: ProcessedReleasesStore, release_dir: Path
) -> None:
    write_meta(release_dir)
    store.mark_processed(RELEASE.slug, fp(release_dir), release=RELEASE)
    state_path = store._cache_dir / "processed_releases.json"
    state_path.write_text("{corrupt", encoding="utf-8")
    assert store.is_processed(RELEASE.slug, fp(release_dir)) is False  # no raise
    assert list((store._cache_dir / "quarantine").iterdir())
    store.mark_processed(RELEASE.slug, fp(release_dir), release=RELEASE)
    assert store.is_processed(RELEASE.slug, fp(release_dir)) is True


def test_tampered_checksum_quarantined(store: ProcessedReleasesStore, release_dir: Path) -> None:
    write_meta(release_dir)
    store.mark_processed(RELEASE.slug, fp(release_dir), release=RELEASE)
    state_path = store._cache_dir / "processed_releases.json"
    data = json.loads(state_path.read_text(encoding="utf-8"))
    data["checksum"] = "0" * 64
    state_path.write_text(json.dumps(data), encoding="utf-8")
    assert store.is_processed(RELEASE.slug, fp(release_dir)) is False
    assert list((store._cache_dir / "quarantine").iterdir())


def test_wrong_schema_quarantined(store: ProcessedReleasesStore, release_dir: Path) -> None:
    write_meta(release_dir)
    store.mark_processed(RELEASE.slug, fp(release_dir), release=RELEASE)
    state_path = store._cache_dir / "processed_releases.json"
    data = json.loads(state_path.read_text(encoding="utf-8"))
    data["schema_version"] = 42
    state_path.write_text(json.dumps(data), encoding="utf-8")
    assert store.is_processed(RELEASE.slug, fp(release_dir)) is False


def test_releases_wrong_type_quarantined(store: ProcessedReleasesStore) -> None:
    state_path = store._cache_dir / "processed_releases.json"
    body = {"releases": [], "history": []}
    state_path.write_text(
        json.dumps({"schema_version": 1, "checksum": compute_checksum(body), **body}),
        encoding="utf-8",
    )
    assert store.is_processed("x", "y") is False
    assert list((store._cache_dir / "quarantine").iterdir())


def test_invalidate_entry(store: ProcessedReleasesStore, release_dir: Path) -> None:
    write_meta(release_dir)
    fingerprint = fp(release_dir)
    store.mark_processed(RELEASE.slug, fingerprint, release=RELEASE)
    store.invalidate(RELEASE.slug)
    assert store.is_processed(RELEASE.slug, fingerprint) is False


def test_history_capped(tmp_path: Path, release_dir: Path) -> None:
    store = ProcessedReleasesStore(cache_dir=tmp_path / "cache", history_limit=3)
    write_meta(release_dir)
    for i in range(5):
        store.mark_processed(RELEASE.slug, f"fp{i}", release=RELEASE)
    data = json.loads((store._cache_dir / "processed_releases.json").read_text(encoding="utf-8"))
    assert len(data["history"]) == 3
    assert data["history"][-1]["fingerprint"] == "fp4"


def test_mark_oserror_degrades(store: ProcessedReleasesStore, release_dir: Path) -> None:
    write_meta(release_dir)
    with patch("src.processed_releases.atomic_write_json", side_effect=OSError("ro")):
        store.mark_processed(RELEASE.slug, fp(release_dir), release=RELEASE)  # no raise
    assert store.is_processed(RELEASE.slug, fp(release_dir)) is False


def test_run_count_increments(store: ProcessedReleasesStore, release_dir: Path) -> None:
    write_meta(release_dir)
    fingerprint = fp(release_dir)
    store.mark_processed(RELEASE.slug, fingerprint, release=RELEASE)
    store.mark_processed(RELEASE.slug, fingerprint, release=RELEASE)
    data = json.loads((store._cache_dir / "processed_releases.json").read_text(encoding="utf-8"))
    assert data["releases"][RELEASE.slug]["run_count"] == 2


# ── run_once: single-flight (R2) ──────────────────────────────────


async def test_run_once_processes_then_skips(
    store: ProcessedReleasesStore, release_dir: Path
) -> None:
    calls: list[int] = []

    async def process() -> bool:
        calls.append(1)
        write_meta(release_dir)
        write_md(release_dir)
        return True

    first = await store.run_once(RELEASE, release_dir, process)
    second = await store.run_once(RELEASE, release_dir, process)
    assert first is True
    assert second is False
    assert len(calls) == 1
    assert store.stats.hits == 1
    assert store.stats.misses == 1


async def test_run_once_reprocesses_on_content_change(
    store: ProcessedReleasesStore, release_dir: Path
) -> None:
    calls: list[int] = []

    async def process() -> bool:
        calls.append(1)
        write_meta(release_dir, total=10 + len(calls))
        return True

    assert await store.run_once(RELEASE, release_dir, process) is True
    # Simulate upstream content change after processing.
    write_meta(release_dir, total=999)
    assert await store.run_once(RELEASE, release_dir, process) is True
    assert len(calls) == 2


async def test_run_once_failed_process_not_marked(
    store: ProcessedReleasesStore, release_dir: Path
) -> None:
    calls: list[int] = []

    async def process() -> bool:
        calls.append(1)
        return False

    assert await store.run_once(RELEASE, release_dir, process) is False
    assert await store.run_once(RELEASE, release_dir, process) is False
    assert len(calls) == 2


async def test_run_once_lock_timeout_skips(
    store: ProcessedReleasesStore, release_dir: Path
) -> None:
    digest = hashlib.sha256(f"release:{RELEASE.slug}".encode()).hexdigest()
    lock_path = store._cache_dir / "locks" / f"{digest}.lock"
    calls: list[int] = []

    async def process() -> bool:
        calls.append(1)  # pragma: no cover — must never run
        return True  # pragma: no cover

    with FileLock(lock_path, timeout=1.0):
        result = await store.run_once(RELEASE, release_dir, process)
    assert result is False
    assert calls == []


def _child_run_once(cache_dir_str: str, release_dir_str: str, counter_path_str: str) -> None:
    """Forked child: run_once with a process that counts real processings."""
    cache_dir = Path(cache_dir_str)
    release_dir = Path(release_dir_str)
    counter = Path(counter_path_str)
    store = ProcessedReleasesStore(cache_dir=cache_dir, lock_timeout=15.0)
    release = RELEASE

    async def process() -> bool:
        fd = os.open(str(counter), os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o600)
        os.write(fd, b"processed\n")
        os.close(fd)
        write_meta(release_dir)
        write_md(release_dir)
        return True

    asyncio.run(store.run_once(release, release_dir, process))
    os._exit(0)


def test_run_once_multiprocess_exactly_one_processing(tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    release_dir = tmp_path / "releases" / "summer_26"
    release_dir.mkdir(parents=True)
    counter = tmp_path / "counter.txt"
    pids: list[int] = []
    for _ in range(3):
        pid = os.fork()
        if pid == 0:  # pragma: no cover — child branch
            try:
                _child_run_once(str(cache_dir), str(release_dir), str(counter))
            except BaseException:
                os._exit(1)
        pids.append(pid)
    for pid in pids:
        _, status = os.waitpid(pid, 0)
        assert os.waitstatus_to_exitcode(status) == 0
    assert counter.read_text(encoding="utf-8").splitlines() == ["processed"]
    reader = ProcessedReleasesStore(cache_dir=cache_dir)
    assert reader.is_processed(RELEASE.slug, fp(release_dir)) is True


async def test_run_once_history_records_actions(
    store: ProcessedReleasesStore, release_dir: Path
) -> None:
    async def process() -> bool:
        write_meta(release_dir)
        return True

    await store.run_once(RELEASE, release_dir, process)
    await store.run_once(RELEASE, release_dir, process)
    data = json.loads((store._cache_dir / "processed_releases.json").read_text(encoding="utf-8"))
    actions = [h["action"] for h in data["history"]]
    assert actions == ["processed", "skipped_hit"]


def test_stats_determinism(tmp_path: Path, release_dir: Path) -> None:
    write_meta(release_dir)
    fingerprint = fp(release_dir)

    def run(name: str) -> dict[str, Any]:
        s = ProcessedReleasesStore(cache_dir=tmp_path / name)
        s.is_processed(RELEASE.slug, fingerprint)
        s.mark_processed(RELEASE.slug, fingerprint, release=RELEASE)
        s.is_processed(RELEASE.slug, fingerprint)
        return s.stats.to_dict()

    assert run("a") == run("b")


# ── Additional tests for uncovered error paths (targeting ≥95% coverage) ──


# Lines 106-118: categories processing in compute_release_fingerprint
def test_fingerprint_categories_processing(release_dir: Path) -> None:
    """Cover lines 106-118: categories list processing with various types."""
    # Test with valid categories
    meta = {
        "name": RELEASE.name,
        "categories": [
            {"name": "Cat A", "count": 5},
            {"name": "Cat B", "count": 3},
        ],
    }
    (release_dir / ".meta.json").write_text(json.dumps(meta), encoding="utf-8")
    assert len(fp(release_dir)) == 64

    # Test with non-dict categories (should be skipped)
    meta["categories"] = ["not-a-dict", {"name": 123, "count": "many"}, {"name": "Ok", "count": 2}]
    (release_dir / ".meta.json").write_text(json.dumps(meta), encoding="utf-8")
    assert len(fp(release_dir)) == 64

    # Test with empty categories
    meta["categories"] = []
    (release_dir / ".meta.json").write_text(json.dumps(meta), encoding="utf-8")
    assert len(fp(release_dir)) == 64


# Lines 124-126: OSError during rglob in compute_release_fingerprint
def test_fingerprint_rglob_oserror(tmp_path: Path, caplog) -> None:
    """Cover lines 124-126: OSError during rglob scan."""
    release_dir = tmp_path / "releases" / "test"
    release_dir.mkdir(parents=True)
    (release_dir / ".meta.json").write_text(json.dumps({"name": "Test"}), encoding="utf-8")

    with patch.object(Path, "rglob", side_effect=OSError("scan failed")):
        with caplog.at_level("WARNING"):
            result = compute_release_fingerprint(release_dir, name="Test")
    assert len(result) == 64
    assert any("Fingerprint scan failed" in r.message for r in caplog.records)


# Lines 131-132: OSError during compute_file_hash in compute_release_fingerprint
def test_fingerprint_compute_file_hash_oserror(release_dir: Path, caplog) -> None:
    """Cover lines 131-132: OSError during file hash computation."""
    write_meta(release_dir)
    write_md(release_dir)

    with patch(
        "src.processed_releases.CacheManager.compute_file_hash", side_effect=OSError("hash failed")
    ):
        result = compute_release_fingerprint(
            release_dir, name=RELEASE.name, release_id=RELEASE.release_id, slug=RELEASE.slug
        )
    assert result == compute_checksum(
        {
            "meta": {
                "name": RELEASE.name,
                "release_id": RELEASE.release_id,
                "slug": RELEASE.slug,
                "total_features": 10,
                "categories": [{"name": "Automação", "count": 10}],
            },
            "content": {"pt_BR/automacao.md": "unreadable"},
            "parser_version": "1",
        }
    )


# Lines 216-217: lock timeout in mark_processed
def test_mark_processed_lock_timeout(
    store: ProcessedReleasesStore, release_dir: Path, caplog
) -> None:
    """Cover lines 216-217: CacheLockTimeoutError in mark_processed."""
    write_meta(release_dir)
    fingerprint = fp(release_dir)
    state_lock = store._state_lock_path()
    with FileLock(state_lock, timeout=1.0):
        other = ProcessedReleasesStore(cache_dir=store._cache_dir, lock_timeout=0.1)
        with caplog.at_level("ERROR"):
            other.mark_processed(RELEASE.slug, fingerprint, release=RELEASE)
    assert any("Lock timeout marking" in r.message for r in caplog.records)


# Lines 228-233: lock timeout in invalidate
def test_invalidate_lock_timeout(store: ProcessedReleasesStore, release_dir: Path, caplog) -> None:
    """Cover lines 228-233: CacheLockTimeoutError in invalidate."""
    write_meta(release_dir)
    fingerprint = fp(release_dir)
    store.mark_processed(RELEASE.slug, fingerprint, release=RELEASE)
    state_lock = store._state_lock_path()
    with FileLock(state_lock, timeout=1.0):
        other = ProcessedReleasesStore(cache_dir=store._cache_dir, lock_timeout=0.1)
        with caplog.at_level("ERROR"):
            other.invalidate(RELEASE.slug)
    assert any("Lock timeout invalidating" in r.message for r in caplog.records)


# Lines 371-373: lock timeout in _load_state
def test_load_state_lock_timeout(store: ProcessedReleasesStore, caplog) -> None:
    """Cover lines 371-373: CacheLockTimeoutError in _load_state."""
    state_lock = store._state_lock_path()
    with FileLock(state_lock, timeout=1.0):
        other = ProcessedReleasesStore(cache_dir=store._cache_dir, lock_timeout=0.1)
        with caplog.at_level("WARNING"):
            result = other.is_processed("any", "fingerprint")
    assert result is False
    assert any("Lock timeout reading processed-releases" in r.message for r in caplog.records)


# Lines 404-413: release attribute handling in _mark_in_state
def test_mark_in_state_release_attribute_fallbacks(
    store: ProcessedReleasesStore, release_dir: Path
) -> None:
    """Cover lines 404-413: release attribute handling with various types."""
    write_meta(release_dir)
    fingerprint = fp(release_dir)

    # Test with None release (should use defaults)
    store.mark_processed(RELEASE.slug, fingerprint, release=None)
    data = json.loads((store._cache_dir / "processed_releases.json").read_text(encoding="utf-8"))
    assert data["releases"][RELEASE.slug]["release_id"] == 0
    assert data["releases"][RELEASE.slug]["name"] == RELEASE.slug

    # Test with release object having non-int release_id and non-str name
    class BadRelease:
        release_id = "not-an-int"
        name = 123

    store2 = ProcessedReleasesStore(cache_dir=store._cache_dir / "other")
    store2.mark_processed(RELEASE.slug, fingerprint, release=BadRelease())
    data2 = json.loads((store2._cache_dir / "processed_releases.json").read_text(encoding="utf-8"))
    assert data2["releases"][RELEASE.slug]["release_id"] == 0
    assert data2["releases"][RELEASE.slug]["name"] == RELEASE.slug

    # Test with release object having valid attributes
    class GoodRelease:
        release_id = 999
        name = "Custom Name"

    store3 = ProcessedReleasesStore(cache_dir=store._cache_dir / "other2")
    store3.mark_processed(RELEASE.slug, fingerprint, release=GoodRelease())
    data3 = json.loads((store3._cache_dir / "processed_releases.json").read_text(encoding="utf-8"))
    assert data3["releases"][RELEASE.slug]["release_id"] == 999
    assert data3["releases"][RELEASE.slug]["name"] == "Custom Name"
