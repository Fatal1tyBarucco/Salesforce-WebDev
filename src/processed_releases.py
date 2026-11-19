"""Incremental pipeline state: processed releases with fingerprint invalidation.

Implements the ``cache/processed_releases.json`` state store described in
``docs/maintenance/cache-management.md`` (it did not exist in code before
ADR-011). Responsibilities:

- Deterministic SHA-256 fingerprint per release (normalized metadata +
  markdown content hashes + parser version).
- Skip regeneration when the fingerprint matches (hit + history record).
- Single-flight processing: two concurrent executions of the same release
  produce exactly one processing (exclusive per-release file lock held
  across check → process → mark).
- Integrity envelope (schema_version + checksum), quarantine with rotated
  backups and empty-state rebuild on corruption — never an unhandled
  exception into the pipeline.

The state file is runtime data: never versioned (ADR-011); auditable
history lives in workflow artifacts and ``releases/``.
"""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .cache_io import (
    CacheLockTimeoutError,
    FileLock,
    atomic_write_json,
    compute_checksum,
    quarantine_file,
    read_json_safe,
)
from .cache_manager import CacheManager, CacheStats
from .config import (
    CACHE_DIR,
    CACHE_LOCKS_DIRNAME,
    CACHE_QUARANTINE_DIRNAME,
    CACHE_QUARANTINE_KEEP,
    CACHE_RELEASE_LOCK_TIMEOUT_SECONDS,
    PARSER_VERSION,
    PROCESSED_RELEASES_FILENAME,
    PROCESSED_RELEASES_HISTORY_LIMIT,
    ReleaseInfo,
)

logger = logging.getLogger(__name__)

#: Envelope schema for the state file.
_STATE_SCHEMA_VERSION = 1
#: Stats namespace used by this store.
_STATS_NAMESPACE = "processed_releases"


def compute_release_fingerprint(
    release_dir: Path,
    *,
    name: str = "",
    release_id: int = 0,
    slug: str = "",
    parser_version: str = PARSER_VERSION,
) -> str:
    """Compute a deterministic SHA-256 fingerprint for a release.

    Covers everything that can change the generated artifacts: normalized
    ``.meta.json`` fields (volatile fields like ``generated_at`` are
    excluded), the SHA-256 of every markdown file (sorted by relative path,
    including locale subdirectories) and the parser version constant.
    Missing or corrupt inputs degrade to a stable fingerprint of the empty
    state — never an exception.

    Args:
        release_dir: Release artifact directory (``releases/<slug>``).
        name: Fallback release name when meta is unavailable.
        release_id: Fallback release id when meta is unavailable.
        slug: Fallback slug when meta is unavailable.
        parser_version: Parser version included in the hash (bump on
            parser changes to force reprocessing).

    Returns:
        SHA-256 hex digest (64 chars) of the canonical fingerprint body.
    """
    meta = read_json_safe(release_dir / ".meta.json")
    normalized: dict[str, Any] = {
        "name": name if isinstance(name, str) else "",
        "release_id": release_id if isinstance(release_id, int) else 0,
        "slug": slug if isinstance(slug, str) else "",
        "total_features": 0,
        "categories": [],
    }
    if isinstance(meta, dict):
        raw_name = meta.get("name", name)
        raw_id = meta.get("release_id", release_id)
        raw_slug = meta.get("slug", slug)
        raw_total = meta.get("total_features", 0)
        normalized["name"] = raw_name if isinstance(raw_name, str) else normalized["name"]
        normalized["release_id"] = raw_id if isinstance(raw_id, int) else normalized["release_id"]
        normalized["slug"] = raw_slug if isinstance(raw_slug, str) else normalized["slug"]
        normalized["total_features"] = raw_total if isinstance(raw_total, int) else 0
        categories: list[dict[str, Any]] = []
        raw_cats = meta.get("categories", [])
        if isinstance(raw_cats, list):
            for cat in raw_cats:
                if not isinstance(cat, dict):
                    continue
                cat_name = cat.get("name", "")
                cat_count = cat.get("count", 0)
                categories.append(
                    {
                        "name": cat_name if isinstance(cat_name, str) else "",
                        "count": cat_count if isinstance(cat_count, int) else 0,
                    }
                )
        categories.sort(key=lambda c: (c["name"], c["count"]))
        normalized["categories"] = categories
    content_hashes: dict[str, str] = {}
    if release_dir.is_dir():
        try:
            md_files = sorted(release_dir.rglob("*.md"))
        except OSError as exc:
            logger.warning("[CACHE] Fingerprint scan failed for %s: %s", release_dir, exc)
            md_files = []
        for md_path in md_files:
            rel = md_path.relative_to(release_dir).as_posix()
            try:
                content_hashes[rel] = CacheManager.compute_file_hash(md_path)
            except OSError:
                content_hashes[rel] = "unreadable"
    body = {
        "meta": normalized,
        "content": content_hashes,
        "parser_version": parser_version,
    }
    return compute_checksum(body)


class ProcessedReleasesStore:
    """Fingerprint-based incremental state for processed releases.

    Args:
        cache_dir: Runtime cache directory (default ``cache/``).
        lock_timeout: Seconds to wait for the per-release single-flight
            lock. On timeout the release is skipped (another execution
            owns it) — never processed twice.
        history_limit: Maximum execution events kept in the state file.
        quarantine_keep: Rotated backup copies kept per corrupt file.
    """

    def __init__(
        self,
        cache_dir: Path = Path(CACHE_DIR),
        *,
        lock_timeout: float | None = None,
        history_limit: int | None = None,
        quarantine_keep: int | None = None,
    ) -> None:
        self._cache_dir = cache_dir
        self._lock_timeout = (
            lock_timeout if lock_timeout is not None else CACHE_RELEASE_LOCK_TIMEOUT_SECONDS
        )
        self._history_limit = (
            history_limit if history_limit is not None else PROCESSED_RELEASES_HISTORY_LIMIT
        )
        self._quarantine_keep = (
            quarantine_keep if quarantine_keep is not None else CACHE_QUARANTINE_KEEP
        )
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._stats = CacheStats()

    @property
    def stats(self) -> CacheStats:
        """Return hit/miss statistics for this store (namespace-scoped)."""
        return self._stats

    def is_processed(self, slug: str, fingerprint: str) -> bool:
        """Check whether a release was processed with the same fingerprint.

        Args:
            slug: Release slug (directory name).
            fingerprint: Current fingerprint of the release.

        Returns:
            ``True`` when the stored fingerprint matches (safe to skip).
        """
        state = self._load_state()
        entry = state["releases"].get(slug)
        if isinstance(entry, dict) and entry.get("fingerprint") == fingerprint:
            self._stats.record_hit(_STATS_NAMESPACE)
            return True
        self._stats.record_miss(_STATS_NAMESPACE)
        return False

    def mark_processed(
        self,
        slug: str,
        fingerprint: str,
        *,
        release: ReleaseInfo | None = None,
    ) -> None:
        """Persist a processed release with its fingerprint (atomic, locked).

        Args:
            slug: Release slug.
            fingerprint: Fingerprint computed AFTER successful processing.
            release: Optional release metadata for the history record.
        """
        try:
            with FileLock(self._state_lock_path(), timeout=self._lock_timeout):
                state = self._load_state_unlocked()
                self._mark_in_state(state, slug, fingerprint, release)
                self._save_state(state)
        except CacheLockTimeoutError as exc:
            logger.error("[CACHE] Lock timeout marking %s processed: %s", slug, exc)

    def invalidate(self, slug: str) -> None:
        """Remove a release entry, forcing reprocessing on the next run.

        Args:
            slug: Release slug to invalidate.
        """
        try:
            with FileLock(self._state_lock_path(), timeout=self._lock_timeout):
                state = self._load_state_unlocked()
                if slug in state["releases"]:
                    del state["releases"][slug]
                    self._append_history(state, slug, "invalidated", "")
                    self._save_state(state)
        except CacheLockTimeoutError as exc:
            logger.error("[CACHE] Lock timeout invalidating %s: %s", slug, exc)

    async def run_once(
        self,
        release: ReleaseInfo,
        release_dir: Path,
        process: Callable[[], Awaitable[bool]],
    ) -> bool:
        """Process a release exactly once across concurrent executions.

        Holds the per-release exclusive lock across check → process → mark
        (single-flight). A concurrent execution that finds the fingerprint
        unchanged records a hit and skips. On lock timeout the release is
        skipped with a warning — the lock holder owns the processing.

        Args:
            release: Release metadata.
            release_dir: Release artifact directory.
            process: Awaitable performing the actual processing; must
                return True on success (only success is marked).

        Returns:
            ``True`` when this execution processed the release, ``False``
            when it was skipped (hit, failure or lock contention).
        """
        try:
            with FileLock(self._release_lock_path(release.slug), timeout=self._lock_timeout):
                fingerprint = compute_release_fingerprint(
                    release_dir,
                    name=release.name,
                    release_id=release.release_id,
                    slug=release.slug,
                )
                state = self._load_state_unlocked()
                entry = state["releases"].get(release.slug)
                if isinstance(entry, dict) and entry.get("fingerprint") == fingerprint:
                    self._stats.record_hit(_STATS_NAMESPACE)
                    with FileLock(self._state_lock_path(), timeout=self._lock_timeout):
                        fresh = self._load_state_unlocked()
                        self._append_history(fresh, release.slug, "skipped_hit", fingerprint)
                        self._save_state(fresh)
                    logger.info(
                        "[CACHE] Release %s unchanged (fingerprint hit) — skipping generation",
                        release.slug,
                    )
                    return False
                self._stats.record_miss(_STATS_NAMESPACE)
                succeeded = await process()
                if not succeeded:
                    logger.warning(
                        "[CACHE] Processing failed for %s — not marking as processed",
                        release.slug,
                    )
                    return False
                new_fingerprint = compute_release_fingerprint(
                    release_dir,
                    name=release.name,
                    release_id=release.release_id,
                    slug=release.slug,
                )
                with FileLock(self._state_lock_path(), timeout=self._lock_timeout):
                    fresh = self._load_state_unlocked()
                    self._mark_in_state(fresh, release.slug, new_fingerprint, release)
                    self._save_state(fresh)
                return True
        except CacheLockTimeoutError:
            logger.warning(
                "[CACHE] Release %s is being processed by another execution — skipping",
                release.slug,
            )
            return False

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _state_path(self) -> Path:
        """Return the state file path."""
        return self._cache_dir / PROCESSED_RELEASES_FILENAME

    def _state_lock_path(self) -> Path:
        """Return the state-file lock path."""
        return self._cache_dir / (PROCESSED_RELEASES_FILENAME + ".lock")

    def _release_lock_path(self, slug: str) -> Path:
        """Return the per-release single-flight lock path."""
        digest = hashlib.sha256(f"release:{slug}".encode()).hexdigest()
        return self._cache_dir / CACHE_LOCKS_DIRNAME / f"{digest}.lock"

    def _empty_state(self) -> dict[str, Any]:
        """Return a fresh empty state structure."""
        return {"releases": {}, "history": []}

    def _quarantine_state(self) -> None:
        """Quarantine the corrupt state file (rotated backup)."""
        quarantine_file(
            self._state_path(),
            self._cache_dir / CACHE_QUARANTINE_DIRNAME,
            keep=self._quarantine_keep,
        )

    def _load_state_unlocked(self) -> dict[str, Any]:
        """Load and validate the state file without taking the state lock.

        Corrupt, tampered or incompatible payloads are quarantined and the
        store rebuilds from empty state. Never raises.
        """
        path = self._state_path()
        if not path.exists():
            return self._empty_state()
        payload = read_json_safe(path)
        if not isinstance(payload, dict):
            logger.warning("[CACHE] Corrupt processed-releases state — quarantining")
            self._quarantine_state()
            return self._empty_state()
        if payload.get("schema_version") != _STATE_SCHEMA_VERSION:
            logger.warning("[CACHE] Incompatible processed-releases schema — quarantining")
            self._quarantine_state()
            return self._empty_state()
        releases = payload.get("releases")
        history = payload.get("history")
        if not isinstance(releases, dict) or not isinstance(history, list):
            logger.warning("[CACHE] Invalid processed-releases shape — quarantining")
            self._quarantine_state()
            return self._empty_state()
        expected = payload.get("checksum")
        body = {"releases": releases, "history": history}
        if not isinstance(expected, str) or compute_checksum(body) != expected:
            logger.warning("[CACHE] Processed-releases checksum mismatch — quarantining")
            self._quarantine_state()
            return self._empty_state()
        return {"releases": dict(releases), "history": list(history)}

    def _load_state(self) -> dict[str, Any]:
        """Load the state under the state-file lock (degrades to empty)."""
        try:
            with FileLock(self._state_lock_path(), timeout=self._lock_timeout):
                return self._load_state_unlocked()
        except CacheLockTimeoutError as exc:
            logger.warning("[CACHE] Lock timeout reading processed-releases: %s", exc)
            return self._empty_state()

    def _save_state(self, state: dict[str, Any]) -> None:
        """Persist state atomically with a fresh checksum (best-effort)."""
        releases = state.get("releases", {})
        history = state.get("history", [])
        body = {"releases": releases, "history": history}
        try:
            payload = {
                "schema_version": _STATE_SCHEMA_VERSION,
                "checksum": compute_checksum(body),
                "releases": releases,
                "history": history,
            }
            atomic_write_json(self._state_path(), payload)
        except (TypeError, ValueError, OSError) as exc:
            logger.error("[CACHE] Failed to persist processed-releases state: %s", exc)

    def _mark_in_state(
        self,
        state: dict[str, Any],
        slug: str,
        fingerprint: str,
        release: ReleaseInfo | None,
    ) -> None:
        """Upsert a release entry and append a 'processed' history event."""
        releases: dict[str, Any] = state["releases"]
        previous = releases.get(slug)
        run_count = 1
        if isinstance(previous, dict):
            prev_count = previous.get("run_count", 0)
            if isinstance(prev_count, int):
                run_count = prev_count + 1
        release_id = 0
        release_name = slug
        if release is not None:
            raw_id = getattr(release, "release_id", 0)
            raw_name = getattr(release, "name", slug)
            release_id = raw_id if isinstance(raw_id, int) else 0
            release_name = raw_name if isinstance(raw_name, str) else slug
        releases[slug] = {
            "fingerprint": fingerprint,
            "processed_at": datetime.now(tz=UTC).isoformat(),
            "release_id": release_id,
            "name": release_name,
            "run_count": run_count,
        }
        self._append_history(state, slug, "processed", fingerprint)

    def _append_history(
        self, state: dict[str, Any], slug: str, action: str, fingerprint: str
    ) -> None:
        """Append a capped execution event to the in-memory state."""
        history: list[Any] = state["history"]
        history.append(
            {
                "slug": slug,
                "action": action,
                "fingerprint": fingerprint,
                "at": datetime.now(tz=UTC).isoformat(),
            }
        )
        if len(history) > self._history_limit:
            del history[: len(history) - self._history_limit]
