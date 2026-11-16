"""Scraper cache adapter using CacheManager."""

from __future__ import annotations

import logging

from src.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class ScraperCacheAdapter:
    """Adapter for scraper caching using CacheManager."""

    def __init__(self, cache_manager: CacheManager) -> None:
        self._cache = cache_manager

    async def get(self, key: str) -> str | None:
        """Get cached content by key."""
        try:
            return self._cache.get(key)
        except Exception as e:
            logger.debug("Cache get failed for %s: %s", key, e)
            return None

    async def set(self, key: str, content: str, ttl_seconds: int | None = None) -> None:
        """Cache content with TTL."""
        try:
            self._cache.set(key, content, ttl=ttl_seconds)
        except Exception as e:
            logger.debug("Cache set failed for %s: %s", key, e)

    async def invalidate(self, key: str) -> None:
        """Invalidate cache for key."""
        try:
            self._cache.set(key, "", ttl=0)
        except Exception as e:
            logger.debug("Cache invalidate failed for %s: %s", key, e)
