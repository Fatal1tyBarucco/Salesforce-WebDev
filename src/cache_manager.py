"""Unified file-based caching with TTL, content-hash, and namespace support.

Provides a single source of truth for all caching in the pipeline:
- TTL-based expiration for API responses and metadata
- Content-hash based invalidation for file change detection (SHA-256)
- Namespace-based grouping for bulk invalidation
- Cache statistics (hits, misses, evictions by reason, per-namespace)
- Atomic writes (temp file + os.replace), exclusive file locks and
  integrity verification (schema_version + checksum) with quarantine
  and rotated backups for corrupt payloads (ADR-011)

Usage::

    from src.cache_manager import CacheManager

    # TTL cache (API responses)
    cache = CacheManager(cache_dir=Path("cache"), ttl_seconds=3600)
    cache.set("key", {"data": "value"})
    result = cache.get("key")

    # Namespaced cache (group-related entries)
    cache.set("prompt1", "response", namespace="llm")
    cache.invalidate_namespace("llm")  # clear all LLM cache

    # Cache statistics (persisted per run via persist_stats())
    stats = cache.stats
    logger.info("Hit rate: %.0f%%", stats.hit_rate * 100)

    # Content-hash cache (file change detection)
    file_hash = cache.get_content_hash(Path("file.md"))
    is_cached = cache.is_content_unchanged(Path("file.md"), file_hash or "")
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypeGuard

from .cache_io import (
    CacheLockTimeoutError,
    FileLock,
    atomic_write_json,
    compute_checksum,
    quarantine_file,
    read_json_safe,
)
from .config import (
    CACHE_ACCESS_PERSIST_INTERVAL_SECONDS,
    CACHE_DEFAULT_TTL_SECONDS,
    CACHE_LOCK_TIMEOUT_SECONDS,
    CACHE_LOCKS_DIRNAME,
    CACHE_MAX_BYTES_PER_NAMESPACE,
    CACHE_MAX_ENTRIES_PER_NAMESPACE,
    CACHE_QUARANTINE_DIRNAME,
    CACHE_QUARANTINE_KEEP,
    CACHE_STATS_FILENAME,
)

logger = logging.getLogger(__name__)

#: Envelope schema written by this module (legacy v1 payloads are still read).
_SCHEMA_VERSION = 2
#: Namespaces must be simple directory-safe identifiers.
_NAMESPACE_RE = re.compile(r"^[A-Za-z0-9_-]+$")
#: Reserved namespaces (internal machinery, never user entries).
_RESERVED_NAMESPACES = frozenset({CACHE_QUARANTINE_DIRNAME, CACHE_LOCKS_DIRNAME})
#: Root-level metadata files that are not cache entries.
_RESERVED_ROOT_FILES = frozenset({CACHE_STATS_FILENAME})
#: Legacy MD5 hex digests are 32 lowercase/uppercase hex chars.
_MD5_RE = re.compile(r"^[0-9a-fA-F]{32}$")


def _is_number(value: Any) -> TypeGuard[int | float]:
    """Return True for real int/float values (bools are not numbers here)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


@dataclass
class NamespaceStats:
    """Per-namespace cache counters.

    Attributes:
        hits: Successful lookups in this namespace.
        misses: Failed/expired/corrupt lookups in this namespace.
        evictions: Entries removed from this namespace (any reason).
        sets: Successful writes in this namespace.
    """

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    sets: int = 0

    @property
    def hit_rate(self) -> float:
        """Hit rate for this namespace (0.0 to 1.0)."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable snapshot of this namespace's counters."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "sets": self.sets,
            "hit_rate": self.hit_rate,
        }


@dataclass
class CacheStats:
    """Cache performance statistics (aggregate + per-namespace + reasons).

    The four original counters and their semantics are preserved for
    backward compatibility; ``by_namespace`` and ``eviction_reasons``
    add the observability required by ADR-011 (R6).
    """

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    sets: int = 0
    by_namespace: dict[str, NamespaceStats] = field(default_factory=dict)
    eviction_reasons: dict[str, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        """Total number of cache lookups."""
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0.0 to 1.0)."""
        return self.hits / self.total if self.total > 0 else 0.0

    def __repr__(self) -> str:
        return (
            f"CacheStats(hits={self.hits}, misses={self.misses}, "
            f"evictions={self.evictions}, hit_rate={self.hit_rate:.1%})"
        )

    def _ns(self, namespace: str) -> NamespaceStats:
        """Return (creating if needed) the counter bucket for a namespace."""
        bucket = self.by_namespace.get(namespace)
        if bucket is None:
            bucket = NamespaceStats()
            self.by_namespace[namespace] = bucket
        return bucket

    def record_hit(self, namespace: str) -> None:
        """Record a successful lookup in aggregate and namespace counters."""
        self.hits += 1
        self._ns(namespace).hits += 1

    def record_miss(self, namespace: str) -> None:
        """Record a failed lookup in aggregate and namespace counters."""
        self.misses += 1
        self._ns(namespace).misses += 1

    def record_set(self, namespace: str) -> None:
        """Record a successful write in aggregate and namespace counters."""
        self.sets += 1
        self._ns(namespace).sets += 1

    def record_eviction(self, namespace: str, reason: str) -> None:
        """Record an eviction with its reason (ttl, lru, corruption, manual)."""
        self.evictions += 1
        self._ns(namespace).evictions += 1
        self.eviction_reasons[reason] = self.eviction_reasons.get(reason, 0) + 1

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-serializable snapshot of all counters."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "sets": self.sets,
            "total": self.total,
            "hit_rate": self.hit_rate,
            "by_namespace": {
                ns: bucket.to_dict() for ns, bucket in sorted(self.by_namespace.items())
            },
            "eviction_reasons": dict(sorted(self.eviction_reasons.items())),
        }


class CacheManager:
    """File-based caching with TTL, integrity, locking and content-hash support.

    Every write is atomic (temp file + fsync + os.replace) and guarded by an
    exclusive file lock. Every payload carries ``schema_version`` and a
    SHA-256 checksum; corrupt or incompatible payloads are quarantined with
    rotated backups and degrade to a miss — never an unhandled exception.

    Args:
        cache_dir: Directory for cache files.
        ttl_seconds: Default time-to-live in seconds. Negative values mean
            "never expire"; ``0`` keeps the legacy "expire immediately"
            semantics used by adapter invalidation.
        clock: Injectable wall-clock callable (defaults to ``time.time``).
            Tests use a fake clock — no sleeps required.
        max_entries_per_namespace: LRU entry budget (default from config).
        max_bytes_per_namespace: LRU byte budget (default from config).
        lock_timeout: Seconds to wait for entry/namespace locks.
        access_persist_interval: Minimum seconds between ``last_access``
            rewrites on cache hits (write-amplification throttle).
        quarantine_keep: Rotated backup copies kept per corrupt file.
    """

    def __init__(
        self,
        cache_dir: Path,
        ttl_seconds: int = CACHE_DEFAULT_TTL_SECONDS,
        *,
        clock: Callable[[], float] | None = None,
        max_entries_per_namespace: int | None = None,
        max_bytes_per_namespace: int | None = None,
        lock_timeout: float | None = None,
        access_persist_interval: float | None = None,
        quarantine_keep: int | None = None,
    ) -> None:
        self._cache_dir = cache_dir
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._max_entries = (
            max_entries_per_namespace
            if max_entries_per_namespace is not None
            else CACHE_MAX_ENTRIES_PER_NAMESPACE
        )
        self._max_bytes = (
            max_bytes_per_namespace
            if max_bytes_per_namespace is not None
            else CACHE_MAX_BYTES_PER_NAMESPACE
        )
        self._lock_timeout = (
            lock_timeout if lock_timeout is not None else CACHE_LOCK_TIMEOUT_SECONDS
        )
        self._access_interval = (
            access_persist_interval
            if access_persist_interval is not None
            else CACHE_ACCESS_PERSIST_INTERVAL_SECONDS
        )
        self._quarantine_keep = (
            quarantine_keep if quarantine_keep is not None else CACHE_QUARANTINE_KEEP
        )
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._stats = CacheStats()
        self._touched_namespaces: set[str] = set()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def stats(self) -> CacheStats:
        """Return current cache statistics."""
        return self._stats

    def set(self, key: str, data: Any, ttl: int | None = None, namespace: str = "") -> None:
        """Store data in the cache atomically under an exclusive lock.

        Non-serializable values and I/O failures degrade with an error log;
        they never corrupt existing entries nor raise into the pipeline.

        Args:
            key: Cache key (will be hashed).
            data: Data to cache (must be JSON-serializable).
            ttl: Override default TTL in seconds. Negative = never expire.
            namespace: Optional namespace for grouping related entries.
        """
        if not self._valid_namespace(namespace):
            logger.error("[CACHE] Rejected unsafe namespace %r — set skipped", namespace)
            return
        try:
            checksum = compute_checksum(data)
        except (TypeError, ValueError, RecursionError) as exc:
            logger.error("[CACHE] Non-serializable value for key %r: %s", key, exc)
            return
        effective_ttl = ttl if ttl is not None else self._ttl_seconds
        now = self._now()
        envelope = {
            "schema_version": _SCHEMA_VERSION,
            "timestamp": now,
            "ttl": effective_ttl,
            "namespace": namespace,
            "last_access": now,
            "checksum": checksum,
            "data": data,
        }
        path = self._get_cache_path(key, namespace)
        try:
            with (
                FileLock(self._key_lock_path(key, namespace), timeout=self._lock_timeout),
                FileLock(self._ns_lock_path(namespace), timeout=self._lock_timeout),
            ):
                path.parent.mkdir(parents=True, exist_ok=True)
                atomic_write_json(path, envelope)
                self._enforce_budget(namespace)
        except CacheLockTimeoutError as exc:
            logger.error("[CACHE] Lock timeout on set for key %r: %s", key, exc)
            return
        except OSError as exc:
            logger.error("[CACHE] Write failed for key %r: %s", key, exc)
            return
        self._stats.record_set(namespace)
        self._touched_namespaces.add(namespace)

    def get(self, key: str, namespace: str = "") -> Any | None:
        """Retrieve data from the cache, validating integrity and TTL.

        Corrupt, checksum-invalid or schema-incompatible payloads are
        quarantined (rotated backup) and treated as a miss. Expired entries
        are evicted. Lock contention degrades to a miss with a warning.

        Args:
            key: Cache key.
            namespace: Optional namespace.

        Returns:
            Cached data if found, valid and not expired; ``None`` otherwise.
        """
        if not self._valid_namespace(namespace):
            logger.error("[CACHE] Rejected unsafe namespace %r — get skipped", namespace)
            return None
        self._touched_namespaces.add(namespace)
        path = self._get_cache_path(key, namespace)
        if not path.exists():
            self._stats.record_miss(namespace)
            return None
        try:
            with FileLock(self._key_lock_path(key, namespace), timeout=self._lock_timeout):
                return self._get_locked(path, namespace)
        except CacheLockTimeoutError as exc:
            logger.warning("[CACHE] Lock timeout on get for key %r: %s", key, exc)
            self._stats.record_miss(namespace)
            return None

    def invalidate(self, key: str, namespace: str = "") -> None:
        """Manually remove an item from the cache.

        Args:
            key: Cache key to remove.
            namespace: Optional namespace.
        """
        if not self._valid_namespace(namespace):
            return
        path = self._get_cache_path(key, namespace)
        if not path.exists():
            return
        try:
            with FileLock(self._key_lock_path(key, namespace), timeout=self._lock_timeout):
                if path.exists():
                    path.unlink()
                    self._stats.record_eviction(namespace, "manual")
        except (CacheLockTimeoutError, OSError) as exc:
            logger.warning("[CACHE] Invalidate failed for key %r: %s", key, exc)

    def invalidate_namespace(self, namespace: str) -> int:
        """Remove all entries in a namespace.

        Args:
            namespace: Namespace to invalidate.

        Returns:
            Number of entries removed.
        """
        if not self._valid_namespace(namespace):
            return 0
        ns_dir = self._cache_dir / namespace
        if not ns_dir.exists():
            return 0
        count = 0
        try:
            with FileLock(self._ns_lock_path(namespace), timeout=self._lock_timeout):
                for entry in ns_dir.iterdir():
                    if entry.is_file() and entry.suffix == ".json":
                        try:
                            entry.unlink()
                            count += 1
                        except OSError as exc:
                            logger.warning("[CACHE] Failed to remove %s: %s", entry, exc)
                try:
                    ns_dir.rmdir()
                except OSError:
                    logger.debug("[CACHE] Namespace dir %s not empty — kept", ns_dir)
        except CacheLockTimeoutError as exc:
            logger.warning("[CACHE] Lock timeout invalidating namespace %s: %s", namespace, exc)
            return 0
        for _ in range(count):
            self._stats.record_eviction(namespace, "manual")
        logger.info("[CACHE] Invalidated namespace '%s': %d entries removed", namespace, count)
        return count

    def clear_expired(self, full_scan: bool = False) -> int:
        """Remove expired entries; lazy by default (R5).

        Without ``full_scan`` only namespaces touched by this instance are
        swept — no full disk scan per call. Full scans are reserved for
        explicit maintenance (``full_scan=True`` or ``maintenance()``).
        Corrupt payloads found during a sweep are quarantined, not counted
        as expired removals.

        Args:
            full_scan: When True, sweep every namespace on disk.

        Returns:
            Number of expired entries removed.
        """
        now = self._now()
        removed = 0
        groups: dict[Path, str] = {}
        if full_scan:
            for path in self._cache_dir.rglob("*.json"):
                if self._is_reserved_path(path):
                    continue
                ns = "" if path.parent == self._cache_dir else path.parent.name
                groups.setdefault(path.parent, ns)
        else:
            for ns in sorted(self._touched_namespaces):
                ns_dir = self._cache_dir / ns if ns else self._cache_dir
                if ns_dir.exists():
                    groups.setdefault(ns_dir, ns)
        for ns_dir, ns in groups.items():
            try:
                with FileLock(self._ns_lock_path(ns), timeout=self._lock_timeout):
                    removed += self._sweep_directory(ns_dir, ns, now)
            except CacheLockTimeoutError as exc:
                logger.warning("[CACHE] Lock timeout sweeping %s: %s", ns_dir, exc)
        if removed > 0:
            logger.info("[CACHE] Cleared %d expired entries", removed)
        return removed

    def maintenance(self) -> dict[str, int]:
        """Explicit maintenance: full expired sweep + quarantine report.

        Returns:
            Dict with ``expired_removed`` and ``quarantine_copies`` counts.
        """
        removed = self.clear_expired(full_scan=True)
        qdir = self._cache_dir / CACHE_QUARANTINE_DIRNAME
        copies = 0
        if qdir.exists():
            try:
                copies = sum(1 for p in qdir.iterdir() if p.is_file())
            except OSError as exc:
                logger.warning("[CACHE] Quarantine scan failed: %s", exc)
        return {"expired_removed": removed, "quarantine_copies": copies}

    def persist_stats(self, extra: dict[str, Any] | None = None) -> Path | None:
        """Persist statistics for this execution to ``cache/stats.json``.

        Best-effort: I/O failures are logged and degrade to None so the
        pipeline never fails on observability writes.

        Args:
            extra: Optional additional sections (e.g. processed-releases
                store counters) merged into the stats document.

        Returns:
            The stats file path when written, ``None`` on failure.
        """
        path = self._cache_dir / CACHE_STATS_FILENAME
        payload: dict[str, Any] = {
            "schema_version": 1,
            "generated_at": datetime.now(tz=UTC).isoformat(),
            "stats": self._stats.to_dict(),
        }
        if extra is not None:
            payload["extra"] = extra
        try:
            atomic_write_json(path, payload)
        except OSError as exc:
            logger.error("[CACHE] Failed to persist stats: %s", exc)
            return None
        return path

    # ------------------------------------------------------------------
    # Content-hash based caching for file change detection (SHA-256)
    # ------------------------------------------------------------------

    @staticmethod
    def compute_file_hash(file_path: Path) -> str:
        """Compute the SHA-256 hash of a file's content (chunked).

        Args:
            file_path: Path to the file.

        Returns:
            Hex digest (64 chars) of the SHA-256 hash.

        Raises:
            OSError: If the file cannot be read.
        """
        digest = hashlib.sha256()
        with file_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def get_content_hash(self, file_path: Path) -> str | None:
        """Get the SHA-256 hash of a file's content.

        Args:
            file_path: Path to the file.

        Returns:
            SHA-256 hex digest if the file exists and is readable,
            ``None`` otherwise.
        """
        if not file_path.exists():
            return None
        try:
            return self.compute_file_hash(file_path)
        except OSError as exc:
            logger.warning("[CACHE] Cannot hash %s: %s", file_path, exc)
            return None

    def is_content_unchanged(self, file_path: Path, expected_hash: str) -> bool:
        """Check if a file's content matches an expected SHA-256 hash.

        Legacy MD5 digests (32 chars) never match a SHA-256 digest, so they
        degrade to "changed" — one reprocessing migrates the entry (R4).

        Args:
            file_path: Path to the file.
            expected_hash: Expected SHA-256 hex digest.

        Returns:
            ``True`` if the file exists and the hash matches.
        """
        current_hash = self.get_content_hash(file_path)
        return current_hash == expected_hash if current_hash else False

    def load_content_cache(self, cache_file: Path) -> dict[str, str]:
        """Load a content-hash cache, migrating legacy formats tolerantly.

        Accepts both legacy shapes (dict of hash strings and dict of objects
        with ``content_hash``). Empty or MD5-looking hashes are recomputed
        as SHA-256 when the file exists (migration persisted atomically);
        entries whose file is gone keep their stored hash instead of being
        invalidated. Corrupt files are quarantined and degrade to ``{}``.

        Args:
            cache_file: Path to the cache JSON file.

        Returns:
            Dictionary mapping file paths to their content hashes.
        """
        lock_path = cache_file.with_name(cache_file.name + ".lock")
        try:
            with FileLock(lock_path, timeout=self._lock_timeout):
                return self._load_content_locked(cache_file)
        except CacheLockTimeoutError as exc:
            logger.warning("[CACHE] Lock timeout loading %s: %s", cache_file, exc)
            return {}

    def save_content_cache(self, cache_file: Path, cache: dict[str, str]) -> None:
        """Save a content-hash cache atomically under an exclusive lock.

        Non-string keys/values are skipped with a warning; I/O failures
        degrade with an error log and never raise into the pipeline.

        Args:
            cache_file: Path to the cache JSON file.
            cache: Dictionary mapping file paths to SHA-256 hashes.
        """
        validated: dict[str, str] = {}
        for key, value in cache.items():
            if isinstance(key, str) and isinstance(value, str):
                validated[key] = value
            else:
                logger.warning("[CACHE] Skipping non-string content-cache entry %r", key)
        lock_path = cache_file.with_name(cache_file.name + ".lock")
        try:
            with FileLock(lock_path, timeout=self._lock_timeout):
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                atomic_write_json(cache_file, validated)
        except (CacheLockTimeoutError, OSError) as exc:
            logger.error("[CACHE] Failed to save content cache %s: %s", cache_file, exc)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _now(self) -> float:
        """Return the current wall-clock time (injectable for tests)."""
        return self._clock() if self._clock is not None else time.time()

    @staticmethod
    def _valid_namespace(namespace: str) -> bool:
        """Validate a namespace identifier (directory-safe, non-reserved)."""
        if namespace == "":
            return True
        return bool(_NAMESPACE_RE.match(namespace)) and namespace not in _RESERVED_NAMESPACES

    def _get_cache_path(self, key: str, namespace: str = "") -> Path:
        """Return the cache file path for a given key (SHA-256 of ns:key)."""
        full_key = f"{namespace}:{key}" if namespace else key
        key_hash = hashlib.sha256(full_key.encode("utf-8")).hexdigest()
        if namespace:
            return self._cache_dir / namespace / f"{key_hash}.json"
        return self._cache_dir / f"{key_hash}.json"

    def _key_lock_path(self, key: str, namespace: str) -> Path:
        """Return the per-entry lock file path."""
        full_key = f"{namespace}:{key}" if namespace else key
        digest = hashlib.sha256(full_key.encode("utf-8")).hexdigest()
        return self._cache_dir / CACHE_LOCKS_DIRNAME / f"{digest}.lock"

    def _ns_lock_path(self, namespace: str) -> Path:
        """Return the per-namespace lock file path."""
        digest = hashlib.sha256(f"ns:{namespace}".encode()).hexdigest()
        return self._cache_dir / CACHE_LOCKS_DIRNAME / f"{digest}.lock"

    def _is_reserved_path(self, path: Path) -> bool:
        """True for internal machinery paths (stats, quarantine, locks)."""
        if path.name in _RESERVED_ROOT_FILES:
            return True
        return any(
            part in _RESERVED_NAMESPACES for part in path.relative_to(self._cache_dir).parts[:-1]
        )

    def _quarantine(self, path: Path, namespace: str) -> None:
        """Quarantine a corrupt payload and record the eviction reason."""
        quarantine_file(
            path, self._cache_dir / CACHE_QUARANTINE_DIRNAME, keep=self._quarantine_keep
        )
        self._stats.record_eviction(namespace, "corruption")

    def _get_locked(self, path: Path, namespace: str) -> Any | None:
        """Read, validate and return an entry while holding its lock."""
        payload = read_json_safe(path)
        if not isinstance(payload, dict):
            self._quarantine(path, namespace)
            self._stats.record_miss(namespace)
            return None
        schema = payload.get("schema_version")
        if schema is None:
            # Legacy v1 payload: no checksum, trusted shape (migration path).
            if "data" not in payload:
                self._quarantine(path, namespace)
                self._stats.record_miss(namespace)
                return None
            timestamp = payload.get("timestamp")
            ttl = payload.get("ttl", self._ttl_seconds)
            last_access = payload.get("last_access", timestamp)
        elif schema == _SCHEMA_VERSION:
            if "data" not in payload:
                self._quarantine(path, namespace)
                self._stats.record_miss(namespace)
                return None
            expected = payload.get("checksum")
            if not isinstance(expected, str) or compute_checksum(payload["data"]) != expected:
                logger.warning("[CACHE] Checksum mismatch for %s — quarantining", path)
                self._quarantine(path, namespace)
                self._stats.record_miss(namespace)
                return None
            timestamp = payload.get("timestamp")
            ttl = payload.get("ttl", self._ttl_seconds)
            last_access = payload.get("last_access", timestamp)
        else:
            logger.warning("[CACHE] Unknown schema_version %r in %s — quarantining", schema, path)
            self._quarantine(path, namespace)
            self._stats.record_miss(namespace)
            return None
        if not _is_number(timestamp) or not _is_number(ttl) or not _is_number(last_access):
            self._quarantine(path, namespace)
            self._stats.record_miss(namespace)
            return None
        now = self._now()
        if ttl >= 0 and now - timestamp > ttl:
            try:
                path.unlink()
            except OSError as exc:
                logger.warning("[CACHE] Failed to evict expired %s: %s", path, exc)
            self._stats.record_eviction(namespace, "ttl")
            self._stats.record_miss(namespace)
            return None
        self._stats.record_hit(namespace)
        if now - last_access >= self._access_interval:
            refreshed = {
                "schema_version": _SCHEMA_VERSION,
                "timestamp": timestamp,
                "ttl": ttl,
                "namespace": namespace,
                "last_access": now,
                "checksum": compute_checksum(payload["data"]),
                "data": payload["data"],
            }
            try:
                atomic_write_json(path, refreshed)
            except OSError as exc:
                logger.warning("[CACHE] last_access refresh failed for %s: %s", path, exc)
        return payload["data"]

    def _enforce_budget(self, namespace: str) -> None:
        """Evict LRU entries until the namespace fits its budgets.

        Called while holding the namespace lock. Two-phase for I/O economy:
        a stat-only pre-check returns immediately when within budget (no
        payload reads); envelopes are read only when eviction is actually
        needed, to order entries by ``last_access`` (fallback ``timestamp``).
        """
        ns_dir = self._cache_dir / namespace if namespace else self._cache_dir
        try:
            candidates = [p for p in ns_dir.glob("*.json") if p.name not in _RESERVED_ROOT_FILES]
        except OSError as exc:
            logger.warning("[CACHE] Budget scan failed for %s: %s", ns_dir, exc)
            return
        sizes: dict[Path, int] = {}
        for path in candidates:
            try:
                sizes[path] = path.stat().st_size
            except OSError:
                continue
        count = len(sizes)
        total_bytes = sum(sizes.values())
        if count <= self._max_entries and total_bytes <= self._max_bytes:
            return
        entries: list[tuple[float, int, Path]] = []
        for path, size in sizes.items():
            payload = read_json_safe(path)
            access = 0.0
            if isinstance(payload, dict):
                la = payload.get("last_access", payload.get("timestamp", 0.0))
                if _is_number(la):
                    access = float(la)
            entries.append((access, size, path))
        entries.sort(key=lambda item: item[0])
        for _, size, path in entries:
            if count <= self._max_entries and total_bytes <= self._max_bytes:
                break
            try:
                path.unlink()
            except OSError as exc:
                logger.warning("[CACHE] LRU eviction failed for %s: %s", path, exc)
                continue
            count -= 1
            total_bytes -= size
            self._stats.record_eviction(namespace, "lru")
            logger.info("[CACHE] LRU evicted %s (namespace=%s)", path.name, namespace or "<root>")

    def _sweep_directory(self, ns_dir: Path, namespace: str, now: float) -> int:
        """Remove expired entries in one directory; quarantine corrupt ones."""
        removed = 0
        try:
            paths = list(ns_dir.glob("*.json"))
        except OSError as exc:
            logger.warning("[CACHE] Sweep scan failed for %s: %s", ns_dir, exc)
            return 0
        for path in paths:
            if path.name in _RESERVED_ROOT_FILES:
                continue
            payload = read_json_safe(path)
            if not isinstance(payload, dict):
                self._quarantine(path, namespace)
                continue
            timestamp = payload.get("timestamp", 0)
            ttl = payload.get("ttl", self._ttl_seconds)
            if not _is_number(timestamp) or not _is_number(ttl):
                self._quarantine(path, namespace)
                continue
            if ttl >= 0 and now - timestamp > ttl:
                try:
                    path.unlink()
                except OSError as exc:
                    logger.warning("[CACHE] Sweep eviction failed for %s: %s", path, exc)
                    continue
                removed += 1
                self._stats.record_eviction(namespace, "ttl")
        return removed

    def _load_content_locked(self, cache_file: Path) -> dict[str, str]:
        """Load and migrate a content-cache file while holding its lock."""
        if not cache_file.exists():
            return {}
        raw = read_json_safe(cache_file)
        if not isinstance(raw, dict):
            logger.warning("[CACHE] Corrupt content cache %s — quarantining", cache_file)
            quarantine_file(
                cache_file,
                cache_file.parent / CACHE_QUARANTINE_DIRNAME,
                keep=self._quarantine_keep,
            )
            return {}
        result: dict[str, str] = {}
        migrated = False
        for key, value in raw.items():
            if isinstance(value, str):
                hash_value = value
            elif isinstance(value, dict):
                candidate = value.get("content_hash", "")
                hash_value = candidate if isinstance(candidate, str) else ""
            else:
                logger.debug("[CACHE] Skipping unsupported content-cache value for %r", key)
                continue
            if not hash_value or _MD5_RE.match(hash_value):
                recomputed = self.get_content_hash(Path(key))
                if recomputed is not None:
                    hash_value = recomputed
                    migrated = True
            result[key] = hash_value
        if migrated:
            try:
                atomic_write_json(cache_file, result)
                logger.info("[CACHE] Migrated content cache %s to SHA-256", cache_file)
            except OSError as exc:
                logger.warning("[CACHE] Content-cache migration write failed: %s", exc)
        return result
