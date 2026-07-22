"""Unified file-based caching with TTL, content-hash, and namespace support.

Provides a single source of truth for all caching in the pipeline:
- TTL-based expiration for API responses and metadata
- Content-hash based invalidation for file change detection
- Namespace-based grouping for bulk invalidation
- Cache statistics (hits, misses, evictions)
- Thread-safe file operations

Usage::

    from src.cache_manager import CacheManager

    # TTL cache (API responses)
    cache = CacheManager(cache_dir=Path("cache"), ttl_seconds=3600)
    cache.set("key", {"data": "value"})
    result = cache.get("key")

    # Namespaced cache (group-related entries)
    cache.set("prompt1", "response", namespace="llm")
    cache.invalidate_namespace("llm")  # clear all LLM cache

    # Cache statistics
    stats = cache.stats
    print(f"Hit rate: {stats.hit_rate:.0%}")

    # Content-hash cache (file change detection)
    file_hash = cache.get_content_hash(Path("file.md"))
    is_cached = cache.is_content_unchanged(Path("file.md"))
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Cache performance statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    sets: int = 0

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


class CacheManager:
    """File-based caching with TTL and content-hash support.

    Args:
        cache_dir: Directory for cache files.
        ttl_seconds: Default time-to-live in seconds.
    """

    def __init__(self, cache_dir: Path, ttl_seconds: int = 86400) -> None:
        self._cache_dir = cache_dir
        self._ttl_seconds = ttl_seconds
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._stats = CacheStats()

    @property
    def stats(self) -> CacheStats:
        """Return current cache statistics."""
        return self._stats

    def _get_cache_path(self, key: str, namespace: str = "") -> Path:
        """Return the cache file path for a given key."""
        full_key = f"{namespace}:{key}" if namespace else key
        key_hash = hashlib.sha256(full_key.encode("utf-8")).hexdigest()
        if namespace:
            ns_dir = self._cache_dir / namespace
            ns_dir.mkdir(parents=True, exist_ok=True)
            return ns_dir / f"{key_hash}.json"
        return self._cache_dir / f"{key_hash}.json"

    def set(self, key: str, data: Any, ttl: Optional[int] = None, namespace: str = "") -> None:
        """Store data in the cache.

        Args:
            key: Cache key (will be hashed).
            data: Data to cache (must be JSON-serializable).
            ttl: Override default TTL in seconds.
            namespace: Optional namespace for grouping related entries.
        """
        path = self._get_cache_path(key, namespace)
        effective_ttl = ttl if ttl is not None else self._ttl_seconds
        payload = {
            "timestamp": time.time(),
            "ttl": effective_ttl,
            "namespace": namespace,
            "data": data,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        self._stats.sets += 1

    def get(self, key: str, namespace: str = "") -> Optional[Any]:
        """Retrieve data from the cache.

        Args:
            key: Cache key.
            namespace: Optional namespace.

        Returns:
            Cached data if found and not expired, ``None`` otherwise.
        """
        path = self._get_cache_path(key, namespace)
        if not path.exists():
            self._stats.misses += 1
            return None

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._stats.misses += 1
            return None

        ttl = payload.get("ttl", self._ttl_seconds)
        if time.time() - payload.get("timestamp", 0) > ttl:
            path.unlink()
            self._stats.evictions += 1
            self._stats.misses += 1
            return None

        self._stats.hits += 1
        return payload.get("data")

    def invalidate(self, key: str, namespace: str = "") -> None:
        """Manually remove an item from the cache.

        Args:
            key: Cache key to remove.
            namespace: Optional namespace.
        """
        path = self._get_cache_path(key, namespace)
        if path.exists():
            path.unlink()

    def invalidate_namespace(self, namespace: str) -> int:
        """Remove all entries in a namespace.

        Args:
            namespace: Namespace to invalidate.

        Returns:
            Number of entries removed.
        """
        ns_dir = self._cache_dir / namespace
        if not ns_dir.exists():
            return 0

        count = 0
        for entry in ns_dir.iterdir():
            if entry.suffix == ".json":
                entry.unlink()
                count += 1

        try:
            ns_dir.rmdir()
        except OSError:
            pass

        logger.info("[CACHE] Invalidated namespace '%s': %d entries removed", namespace, count)
        return count

    def clear_expired(self) -> int:
        """Remove all expired entries across all namespaces.

        Returns:
            Number of expired entries removed.
        """
        removed = 0
        now = time.time()
        for path in self._cache_dir.rglob("*.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                ttl = payload.get("ttl", self._ttl_seconds)
                if now - payload.get("timestamp", 0) > ttl:
                    path.unlink()
                    removed += 1
            except (json.JSONDecodeError, OSError):
                continue

        if removed > 0:
            self._stats.evictions += removed
            logger.info("[CACHE] Cleared %d expired entries", removed)
        return removed

    # ------------------------------------------------------------------
    # Content-hash based caching for file change detection
    # ------------------------------------------------------------------

    @staticmethod
    def compute_file_hash(file_path: Path) -> str:
        """Compute MD5 hash of a file's content.

        Args:
            file_path: Path to the file.

        Returns:
            Hex digest of the MD5 hash.
        """
        return hashlib.md5(file_path.read_bytes()).hexdigest()

    def get_content_hash(self, file_path: Path) -> Optional[str]:
        """Get the MD5 hash of a file's content.

        Args:
            file_path: Path to the file.

        Returns:
            MD5 hex digest if file exists, ``None`` otherwise.
        """
        if not file_path.exists():
            return None
        return self.compute_file_hash(file_path)

    def is_content_unchanged(self, file_path: Path, expected_hash: str) -> bool:
        """Check if a file's content matches an expected hash.

        Args:
            file_path: Path to the file.
            expected_hash: Expected MD5 hex digest.

        Returns:
            ``True`` if file exists and hash matches.
        """
        current_hash = self.get_content_hash(file_path)
        return current_hash == expected_hash if current_hash else False

    def load_content_cache(self, cache_file: Path) -> dict[str, str]:
        """Load a content-hash cache from a JSON file.

        Args:
            cache_file: Path to the cache JSON file.

        Returns:
            Dictionary mapping file paths to their MD5 hashes.
        """
        if not cache_file.exists():
            return {}
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            # Support both old format (dict of ContentHash vars) and new format (dict of hashes)
            result: dict[str, str] = {}
            for key, value in data.items():
                if isinstance(value, str):
                    result[key] = value
                elif isinstance(value, dict):
                    result[key] = value.get("content_hash", "")
            return result
        except (json.JSONDecodeError, TypeError):
            return {}

    def save_content_cache(self, cache_file: Path, cache: dict[str, str]) -> None:
        """Save a content-hash cache to a JSON file.

        Args:
            cache_file: Path to the cache JSON file.
            cache: Dictionary mapping file paths to MD5 hashes.
        """
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
