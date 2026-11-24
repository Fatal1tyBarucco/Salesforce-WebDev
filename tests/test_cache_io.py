"""Tests for src/cache_io.py — atomic writes, locks, checksums, quarantine.

Deterministic: injected clocks / multiprocessing events, no time.sleep.
"""

from __future__ import annotations

import contextlib
import json
import os
import select
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.cache_io import (
    CacheLockTimeoutError,
    FileLock,
    atomic_write_json,
    atomic_write_text,
    canonical_json,
    compute_checksum,
    quarantine_file,
    read_json_safe,
)

# ── canonical_json / checksum ─────────────────────────────────────


def test_canonical_json_sorts_keys_and_is_compact() -> None:
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_canonical_json_preserves_unicode() -> None:
    assert canonical_json({"nome": "ação"}) == '{"nome":"ação"}'


def test_compute_checksum_deterministic_and_order_independent() -> None:
    assert compute_checksum({"a": 1, "b": 2}) == compute_checksum({"b": 2, "a": 1})


def test_compute_checksum_changes_with_data() -> None:
    assert compute_checksum({"a": 1}) != compute_checksum({"a": 2})


def test_compute_checksum_is_sha256_hex() -> None:
    digest = compute_checksum("x")
    assert len(digest) == 64
    int(digest, 16)  # valid hex


# ── atomic writes ─────────────────────────────────────────────────


def test_atomic_write_json_creates_file(tmp_path: Path) -> None:
    target = tmp_path / "sub" / "data.json"
    atomic_write_json(target, {"k": "v"})
    assert json.loads(target.read_text(encoding="utf-8")) == {"k": "v"}
    assert list(target.parent.iterdir()) == [target]  # no temp leftovers


def test_atomic_write_json_replaces_existing(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    target.write_text('{"old": true}', encoding="utf-8")
    atomic_write_json(target, {"new": True})
    assert json.loads(target.read_text(encoding="utf-8")) == {"new": True}


def test_atomic_write_json_validates_before_touching_disk(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    target.write_text('{"keep": 1}', encoding="utf-8")
    with pytest.raises(TypeError):
        atomic_write_json(target, {"bad": object()})
    # Original file untouched, no temp files left behind.
    assert json.loads(target.read_text(encoding="utf-8")) == {"keep": 1}
    assert list(tmp_path.iterdir()) == [target]


def test_atomic_write_text_replace_failure_cleans_temp(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    target.write_text("original", encoding="utf-8")
    with patch("src.cache_io.os.replace", side_effect=OSError("disk full")):
        with pytest.raises(OSError):
            atomic_write_text(target, "new content")
    assert target.read_text(encoding="utf-8") == "original"
    assert list(tmp_path.iterdir()) == [target]


def test_atomic_write_text_permission_denied_propagates(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    with patch("src.cache_io.os.replace", side_effect=PermissionError("denied")):
        with pytest.raises(PermissionError):
            atomic_write_text(target, "x")
    assert not target.exists()
    assert list(tmp_path.iterdir()) == []


# ── safe reads ────────────────────────────────────────────────────


def test_read_json_safe_valid(tmp_path: Path) -> None:
    f = tmp_path / "ok.json"
    f.write_text('{"a": 1}', encoding="utf-8")
    assert read_json_safe(f) == {"a": 1}


def test_read_json_safe_missing(tmp_path: Path) -> None:
    assert read_json_safe(tmp_path / "nope.json") is None


def test_read_json_safe_corrupt(tmp_path: Path) -> None:
    f = tmp_path / "bad.json"
    f.write_text("{not json", encoding="utf-8")
    assert read_json_safe(f) is None


def test_read_json_safe_directory(tmp_path: Path) -> None:
    assert read_json_safe(tmp_path) is None


def test_read_json_safe_invalid_utf8(tmp_path: Path) -> None:
    f = tmp_path / "bin.json"
    f.write_bytes(b"\xff\xfe\x00")
    assert read_json_safe(f) is None


# ── quarantine ────────────────────────────────────────────────────


def test_quarantine_moves_file_with_timestamp(tmp_path: Path) -> None:
    src = tmp_path / "entry.json"
    src.write_text("corrupt", encoding="utf-8")
    qdir = tmp_path / "quarantine"
    moved = quarantine_file(src, qdir, keep=3)
    assert moved is not None
    assert not src.exists()
    assert moved.parent == qdir
    assert moved.name.startswith("entry.json.")
    assert moved.read_text(encoding="utf-8") == "corrupt"


def test_quarantine_missing_source_returns_none(tmp_path: Path) -> None:
    assert quarantine_file(tmp_path / "gone.json", tmp_path / "q", keep=3) is None


def test_quarantine_rotation_keeps_newest(tmp_path: Path) -> None:
    qdir = tmp_path / "quarantine"
    src = tmp_path / "entry.json"
    moved_names: list[str] = []
    for i in range(5):
        src.write_text(f"v{i}", encoding="utf-8")
        moved = quarantine_file(src, qdir, keep=3)
        assert moved is not None
        moved_names.append(moved.name)
    remaining = sorted(p.name for p in qdir.iterdir())
    assert remaining == sorted(moved_names[-3:])


def test_quarantine_oserror_degrades_to_none(tmp_path: Path) -> None:
    src = tmp_path / "entry.json"
    src.write_text("x", encoding="utf-8")
    with patch("src.cache_io.os.replace", side_effect=OSError("denied")):
        assert quarantine_file(src, tmp_path / "q", keep=3) is None
    assert src.exists()  # source preserved when quarantine fails


# ── FileLock ──────────────────────────────────────────────────────


def test_file_lock_acquire_release(tmp_path: Path) -> None:
    lock_path = tmp_path / "locks" / "entry.lock"
    with FileLock(lock_path, timeout=1.0):
        assert lock_path.exists()
    # Re-acquirable after release.
    with FileLock(lock_path, timeout=1.0):
        pass


def test_file_lock_blocks_second_holder_until_timeout(tmp_path: Path) -> None:
    lock_path = tmp_path / "entry.lock"
    with FileLock(lock_path, timeout=1.0):
        with pytest.raises(CacheLockTimeoutError):
            with FileLock(lock_path, timeout=0.15):
                pass  # pragma: no cover — must not acquire


def test_file_lock_zero_timeout_single_attempt(tmp_path: Path) -> None:
    lock_path = tmp_path / "entry.lock"
    with FileLock(lock_path, timeout=1.0):
        with pytest.raises(CacheLockTimeoutError):
            with FileLock(lock_path, timeout=0.0):
                pass  # pragma: no cover


def _child_hold_lock(lock_path_str: str, notify_fd: int, wait_fd: int) -> None:
    """Child process: hold the lock until the parent signals release.

    Uses raw pipes (not multiprocessing primitives) because this environment's
    kernel denies POSIX named semaphores.
    """
    with FileLock(Path(lock_path_str), timeout=5.0):
        os.write(notify_fd, b"h")
        os.read(wait_fd, 1)


def test_file_lock_multiprocess_concession_and_release(tmp_path: Path) -> None:
    lock_path = tmp_path / "multi.lock"
    child_to_parent_r, child_to_parent_w = os.pipe()
    parent_to_child_r, parent_to_child_w = os.pipe()
    pid = os.fork()
    if pid == 0:  # pragma: no cover — child branch runs in forked process
        os.close(child_to_parent_r)
        os.close(parent_to_child_w)
        try:
            _child_hold_lock(str(lock_path), child_to_parent_w, parent_to_child_r)
        except BaseException:
            os._exit(1)
        os._exit(0)
    os.close(child_to_parent_w)
    os.close(parent_to_child_r)
    try:
        ready, _, _ = select.select([child_to_parent_r], [], [], 10.0)
        assert ready, "child never acquired the lock"
        os.read(child_to_parent_r, 1)
        # Parent cannot acquire while the child holds it.
        with pytest.raises(CacheLockTimeoutError):
            with FileLock(lock_path, timeout=0.15):
                pass  # pragma: no cover
        os.write(parent_to_child_w, b"r")
        _, status = os.waitpid(pid, 0)
        assert os.waitstatus_to_exitcode(status) == 0
        # After the child releases, the parent acquires immediately.
        with FileLock(lock_path, timeout=1.0):
            pass
    finally:
        with contextlib.suppress(OSError):
            os.write(parent_to_child_w, b"r")
        os.close(child_to_parent_r)
        os.close(parent_to_child_w)
        with contextlib.suppress(ChildProcessError):
            os.waitpid(pid, 0)


def test_file_lock_reentrant_same_instance_not_required(tmp_path: Path) -> None:
    """Two distinct FileLock objects on the same path conflict (flock semantics)."""
    lock_path = tmp_path / "entry.lock"
    first = FileLock(lock_path, timeout=1.0)
    second = FileLock(lock_path, timeout=0.1)
    first.__enter__()
    try:
        with pytest.raises(CacheLockTimeoutError):
            second.__enter__()
    finally:
        first.__exit__(None, None, None)
    # Now the second can acquire.
    with second:
        pass


def test_atomic_write_json_fsync_called(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    with patch("src.cache_io.os.fsync", wraps=os.fsync) as mock_fsync:
        atomic_write_json(target, {"a": 1})
    assert mock_fsync.called


# ── Error paths for atomic_write_text temp cleanup ──────────────────


def test_atomic_write_text_temp_cleanup_oserror_logged(tmp_path: Path, caplog) -> None:
    """Cover lines 101-102: OSError during temp file cleanup is logged."""
    target = tmp_path / "data.json"
    target.write_text("original", encoding="utf-8")

    # Make os.replace fail to trigger exception path, then make cleanup also fail
    with patch("src.cache_io.os.replace", side_effect=OSError("replace failed")):
        with patch("src.cache_io.Path.unlink", side_effect=OSError("cleanup failed")):
            with pytest.raises(OSError):
                atomic_write_text(target, "new content")

    # Original file should be preserved
    assert target.read_text(encoding="utf-8") == "original"
    # Warning about failed temp cleanup should be logged
    assert any("Failed to remove temp file" in r.message for r in caplog.records)


# ── Quarantine rotation error paths ─────────────────────────────────


def test_quarantine_rotation_scan_oserror_logged(tmp_path: Path, caplog) -> None:
    """Cover lines 189-191: OSError during quarantine rotation scan."""
    src = tmp_path / "entry.json"
    src.write_text("v1", encoding="utf-8")
    qdir = tmp_path / "quarantine"
    qdir.mkdir()

    with patch.object(Path, "iterdir", side_effect=OSError("scan failed")):
        quarantine_file(src, qdir, keep=3)

    assert any("Quarantine rotation scan failed" in r.message for r in caplog.records)


def test_quarantine_rotation_unlink_oserror_logged(tmp_path: Path, caplog) -> None:
    """Cover lines 195-196: OSError during old quarantine copy removal."""
    src = tmp_path / "entry.json"
    src.write_text("v1", encoding="utf-8")
    qdir = tmp_path / "quarantine"
    qdir.mkdir()

    # Create 5 quarantine copies manually
    for i in range(5):
        (qdir / f"entry.json.20240101T00000{i}Z").write_text(f"v{i}")

    # Make os.replace succeed but unlink fail during rotation
    original_replace = os.replace

    def failing_replace(src_path, dst_path):
        return original_replace(src_path, dst_path)

    with patch("src.cache_io.os.replace", side_effect=failing_replace):
        with patch("src.cache_io.Path.unlink", side_effect=OSError("unlink failed")):
            quarantine_file(src, qdir, keep=3)

    assert any("Failed to rotate quarantine copy" in r.message for r in caplog.records)


# ── FileLock edge cases ─────────────────────────────────────────────


def test_file_lock_exit_when_fd_is_none(tmp_path: Path) -> None:
    """Cover line 250: __exit__ returns early when _fd is None."""
    lock_path = tmp_path / "entry.lock"
    lock = FileLock(lock_path, timeout=1.0)
    # Manually set _fd to None (simulates __enter__ not called or failed)
    lock._fd = None
    # Should not raise
    lock.__exit__(None, None, None)


def test_file_lock_no_fcntl_msvcrt_warning(tmp_path: Path, caplog) -> None:
    """Cover lines 272-274: warning when neither fcntl nor msvcrt available."""
    lock_path = tmp_path / "entry.lock"

    with patch("src.cache_io.fcntl", None), patch("src.cache_io.msvcrt", None):
        lock = FileLock(lock_path, timeout=0.1)
        # This will log the warning and return True (degraded to no-op)
        lock.__enter__()

    assert any("No fcntl/msvcrt available" in r.message for r in caplog.records)
    lock.__exit__(None, None, None)


def test_file_lock_fcntl_unlock_oserror_logged(tmp_path: Path, caplog) -> None:
    """Cover lines 283-284: OSError during fcntl flock unlock."""
    lock_path = tmp_path / "entry.lock"
    lock = FileLock(lock_path, timeout=1.0)
    lock.__enter__()

    with patch("src.cache_io.fcntl.flock", side_effect=OSError("unlock failed")):
        lock.__exit__(None, None, None)

    assert any("Lock release failed" in r.message for r in caplog.records)


def test_file_lock_msvcrt_unlock_oserror_logged(tmp_path: Path, caplog) -> None:
    """Cover lines 289-290: OSError during msvcrt locking unlock."""
    lock_path = tmp_path / "entry.lock"
    lock = FileLock(lock_path, timeout=1.0)
    lock.__enter__()

    # Simulate Windows branch: fcntl=None, msvcrt available but unlock fails
    mock_msvcrt = MagicMock()
    mock_msvcrt.locking.side_effect = OSError("unlock failed")
    with (
        patch("src.cache_io.fcntl", None),
        patch("src.cache_io.msvcrt", mock_msvcrt),
        patch("src.cache_io.os.lseek"),
    ):
        lock.__exit__(None, None, None)

    assert any("Lock release failed" in r.message for r in caplog.records)
