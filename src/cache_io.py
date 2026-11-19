"""Cross-cutting cache I/O primitives (stdlib only).

Provides the building blocks shared by :mod:`src.cache_manager` and
:mod:`src.processed_releases`:

- Canonical JSON serialization + SHA-256 checksums (integrity).
- Atomic file writes: serialize/validate first, then temp file in the same
  directory + ``fsync`` + ``os.replace`` (no partially written state is ever
  visible to another execution).
- Exclusive file locks (``fcntl.flock`` on POSIX, ``msvcrt.locking`` fallback
  on Windows) with a configurable timeout.
- Quarantine with rotated backups for corrupt cache payloads.

Design decisions: ADR-011 (docs/architecture/decisions/adr-011-cache-layer-hardening.md).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import Any, Self

logger = logging.getLogger(__name__)

try:
    import fcntl
except ImportError:  # pragma: no cover — Windows has no fcntl
    fcntl = None  # type: ignore[assignment]

try:
    import msvcrt
except ImportError:  # pragma: no cover — POSIX has no msvcrt
    msvcrt = None  # type: ignore[assignment]

#: Poll interval (seconds) while waiting for a contested lock.
_LOCK_POLL_INTERVAL_SECONDS = 0.05


class CacheLockTimeoutError(TimeoutError):
    """Raised when an exclusive cache lock cannot be acquired within the timeout."""


def canonical_json(data: Any) -> str:
    """Serialize data to a deterministic canonical JSON string.

    Args:
        data: Any JSON-serializable value.

    Returns:
        Compact JSON with sorted keys and unescaped unicode — identical
        inputs always produce identical bytes (checksum stability).
    """
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def compute_checksum(data: Any) -> str:
    """Compute the SHA-256 checksum of a payload body.

    Args:
        data: Any JSON-serializable value (the ``data`` field of an envelope).

    Returns:
        Hex digest (64 chars) of the canonical JSON serialization.
    """
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    """Write text atomically: temp file in the same directory + os.replace.

    The temporary file is flushed and fsynced before the rename so readers
    never observe a partially written file. On any failure the temp file is
    removed and the original target (if any) is left untouched.

    Args:
        path: Destination file path (parent directories are created).
        text: Text content to write (UTF-8).

    Raises:
        OSError: If the write or rename fails (caller decides how to degrade).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".json")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError as cleanup_err:
            logger.warning("[CACHE] Failed to remove temp file %s: %s", tmp_path, cleanup_err)
        raise


def atomic_write_json(path: Path, payload: Any) -> None:
    """Serialize and validate a payload, then write it atomically.

    Serialization happens BEFORE any disk mutation: non-serializable values
    raise without creating or modifying any file.

    Args:
        path: Destination file path.
        payload: JSON-serializable value.

    Raises:
        TypeError: If the payload is not JSON-serializable.
        ValueError: If the payload cannot be serialized (e.g. circular
            references).
        OSError: If the write or rename fails.
    """
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    atomic_write_text(path, text)


def read_json_safe(path: Path) -> Any | None:
    """Read and parse a JSON file, degrading to None on any I/O or parse error.

    Args:
        path: File to read.

    Returns:
        The parsed JSON value, or ``None`` when the file is missing,
        unreadable, not valid UTF-8, or not valid JSON.
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        logger.debug("[CACHE] Safe read failed for %s: %s", path, exc)
        return None


def quarantine_file(path: Path, quarantine_dir: Path, keep: int = 3) -> Path | None:
    """Move a corrupt cache file into quarantine with a UTC timestamp suffix.

    The quarantined copy IS the rotated backup: only the ``keep`` most recent
    copies per original file name are retained. Failure to quarantine never
    raises — the source file is preserved and None is returned so the caller
    can still degrade to a miss.

    Args:
        path: Corrupt file to quarantine.
        quarantine_dir: Destination directory (created on demand).
        keep: Number of timestamped copies to retain per original name.

    Returns:
        The new quarantined path, or ``None`` if the source is missing or
        the move failed.
    """
    if not path.exists():
        return None
    stamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%S%fZ")
    destination = quarantine_dir / f"{path.name}.{stamp}"
    try:
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        os.replace(path, destination)
    except OSError as exc:
        logger.warning("[CACHE] Quarantine failed for %s: %s", path, exc)
        return None
    _rotate_quarantine(quarantine_dir, path.name, keep)
    logger.warning("[CACHE] Quarantined corrupt payload %s -> %s", path, destination)
    return destination


def _rotate_quarantine(quarantine_dir: Path, original_name: str, keep: int) -> None:
    """Keep only the newest ``keep`` quarantined copies of one original file.

    Args:
        quarantine_dir: Directory holding timestamped copies.
        original_name: Original file name used as prefix.
        keep: Maximum number of copies to retain (>= 1).
    """
    keep = max(keep, 1)
    try:
        copies = sorted(
            (p for p in quarantine_dir.iterdir() if p.name.startswith(f"{original_name}.")),
            key=lambda p: p.name,
        )
    except OSError as exc:
        logger.warning("[CACHE] Quarantine rotation scan failed: %s", exc)
        return
    for old in copies[: max(0, len(copies) - keep)]:
        try:
            old.unlink()
        except OSError as exc:
            logger.warning("[CACHE] Failed to rotate quarantine copy %s: %s", old, exc)


class FileLock:
    """Exclusive advisory file lock with timeout (context manager).

    Uses ``fcntl.flock`` on POSIX and ``msvcrt.locking`` on Windows. When
    neither is available the lock degrades to a no-op with a logged warning
    (documented fallback — single-process correctness still relies on atomic
    writes). Lock files are intentionally NOT deleted on release: removing
    them races with other processes waiting on the same inode.

    Args:
        path: Lock file path (parent directories are created; the file is
            created if missing and persists after release).
        timeout: Maximum seconds to wait for acquisition. ``0`` means a
            single non-blocking attempt.

    Raises:
        CacheLockTimeoutError: If the lock is still held by another holder
            when the timeout elapses.
    """

    def __init__(self, path: Path, timeout: float = 30.0) -> None:
        self._path = path
        self._timeout = timeout
        self._fd: int | None = None

    def __enter__(self) -> Self:
        """Acquire the exclusive lock, blocking up to ``timeout`` seconds."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # Owner-only (0o600): lock files carry no payload and must not be
        # world-readable/writable (CodeQL py/overly-permissive-file-mask).
        fd = os.open(str(self._path), os.O_CREAT | os.O_RDWR, 0o600)
        deadline = time.monotonic() + self._timeout
        while True:
            if self._try_lock(fd):
                self._fd = fd
                return self
            if time.monotonic() >= deadline:
                os.close(fd)
                raise CacheLockTimeoutError(
                    f"Could not acquire cache lock {self._path} within {self._timeout}s"
                )
            time.sleep(_LOCK_POLL_INTERVAL_SECONDS)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Release the lock and close the file descriptor."""
        if self._fd is None:
            return
        try:
            self._unlock(self._fd)
        finally:
            os.close(self._fd)
            self._fd = None

    @staticmethod
    def _try_lock(fd: int) -> bool:
        """Attempt a non-blocking exclusive lock; True when acquired."""
        if fcntl is not None:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except OSError:
                return False
        if msvcrt is not None:  # pragma: no cover — Windows-only branch
            try:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                return True
            except OSError:
                return False
        logger.warning(  # pragma: no cover — no locking primitive available
            "[CACHE] No fcntl/msvcrt available — cache lock %s degraded to no-op", fd
        )
        return True  # pragma: no cover

    @staticmethod
    def _unlock(fd: int) -> None:
        """Release the exclusive lock (best-effort)."""
        if fcntl is not None:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError as exc:
                logger.warning("[CACHE] Lock release failed: %s", exc)
        elif msvcrt is not None:  # pragma: no cover — Windows-only branch
            try:
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            except OSError as exc:
                logger.warning("[CACHE] Lock release failed: %s", exc)
