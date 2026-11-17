"""Tests for the scraper cache adapter.

The tests describe the *real* contract of
``src.infrastructure.scraping.cache_adapter``:

* every method delegates to ``CacheManager``;
* ``get`` returns ``None`` when the key is missing and swallows backend
  errors;
* ``set`` forwards the TTL (``None`` means "use the manager default");
* ``invalidate`` stores an empty payload with ``ttl=0``, which makes the
  entry expire on the next read.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.cache_manager import CacheManager
from src.infrastructure.scraping.cache_adapter import ScraperCacheAdapter


class TestScraperCacheAdapter:
    """Tests for ScraperCacheAdapter against a mocked CacheManager."""

    @pytest.fixture
    def mock_cache_manager(self):
        """Create mock cache manager."""
        mock = MagicMock()
        mock.get.return_value = None
        mock.set.return_value = None
        mock.delete.return_value = None
        return mock

    @pytest.fixture
    def adapter(self, mock_cache_manager):
        """Create adapter with mock cache."""
        return ScraperCacheAdapter(cache_manager=mock_cache_manager)

    def test_keeps_the_cache_manager(self, adapter, mock_cache_manager):
        """The adapter must keep a reference to the injected manager."""
        assert adapter._cache is mock_cache_manager

    @pytest.mark.asyncio
    async def test_get_returns_none_when_missing(self, adapter, mock_cache_manager):
        """Should return None when key not in cache."""
        mock_cache_manager.get.return_value = None
        result = await adapter.get("missing-key")
        assert result is None
        mock_cache_manager.get.assert_called_once_with("missing-key")

    @pytest.mark.asyncio
    async def test_get_returns_cached_content(self, adapter, mock_cache_manager):
        """Should return cached content."""
        mock_cache_manager.get.return_value = "<html>Cached content</html>"
        result = await adapter.get("test-key")

        assert result == "<html>Cached content</html>"
        mock_cache_manager.get.assert_called_once_with("test-key")

    @pytest.mark.asyncio
    async def test_set_stores_content(self, adapter, mock_cache_manager):
        """Should store content in cache."""
        await adapter.set("test-key", "<html>Content</html>", ttl_seconds=3600)

        mock_cache_manager.set.assert_called_once_with("test-key", "<html>Content</html>", ttl=3600)

    @pytest.mark.asyncio
    async def test_set_uses_none_ttl_when_not_specified(self, adapter, mock_cache_manager):
        """Should use None TTL when not specified."""
        await adapter.set("test-key", "<html>Content</html>")

        mock_cache_manager.set.assert_called_once_with("test-key", "<html>Content</html>", ttl=None)

    @pytest.mark.asyncio
    async def test_invalidate_expires_the_key(self, adapter, mock_cache_manager):
        """Should store an empty payload with a zero TTL."""
        await adapter.invalidate("test-key")

        mock_cache_manager.set.assert_called_once_with("test-key", "", ttl=0)

    @pytest.mark.asyncio
    async def test_get_handles_exceptions(self, adapter, mock_cache_manager):
        """Should handle exceptions gracefully."""
        mock_cache_manager.get.side_effect = Exception("Cache error")
        result = await adapter.get("test-key")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_handles_exceptions(self, adapter, mock_cache_manager):
        """Should handle exceptions gracefully."""
        mock_cache_manager.set.side_effect = Exception("Cache error")
        # Should not raise
        await adapter.set("test-key", "content")

    @pytest.mark.asyncio
    async def test_invalidate_handles_exceptions(self, adapter, mock_cache_manager):
        """Should handle exceptions gracefully."""
        mock_cache_manager.set.side_effect = Exception("Cache error")
        # Should not raise
        await adapter.invalidate("test-key")


class TestScraperCacheAdapterWithRealCacheManager:
    """Integration tests with real CacheManager."""

    @pytest.fixture
    def temp_cache_dir(self, tmp_path):
        """Create temporary cache directory."""
        return tmp_path / "cache"

    @pytest.fixture
    def cache_manager(self, temp_cache_dir):
        """Create real CacheManager."""
        return CacheManager(cache_dir=temp_cache_dir)

    @pytest.fixture
    def adapter(self, cache_manager):
        """Create adapter with real cache manager."""
        return ScraperCacheAdapter(cache_manager=cache_manager)

    @pytest.mark.asyncio
    async def test_real_cache_roundtrip(self, adapter):
        """Should store and retrieve content with real cache."""
        content = "<html><body>Real content</body></html>"

        await adapter.set("test-key", content, ttl_seconds=3600)
        result = await adapter.get("test-key")

        assert result == content

    @pytest.mark.asyncio
    async def test_real_cache_expiration(self, adapter):
        """Should expire content after TTL."""
        import asyncio

        content = "<html>Expiring content</html>"

        await adapter.set("test-key", content, ttl_seconds=0)  # Immediate expiration
        await asyncio.sleep(0.1)
        result = await adapter.get("test-key")

        assert result is None

    @pytest.mark.asyncio
    async def test_real_cache_invalidation(self, adapter):
        """Should invalidate content."""
        content = "<html>To be invalidated</html>"

        await adapter.set("test-key", content)
        await adapter.invalidate("test-key")
        result = await adapter.get("test-key")

        assert result is None

    @pytest.mark.asyncio
    async def test_real_cache_invalidation_removes_the_entry(self, adapter, cache_manager):
        """The invalidated entry must not stay on disk."""
        await adapter.set("test-key", "<html>content</html>")
        await adapter.invalidate("test-key")

        await adapter.get("test-key")

        assert list(cache_manager._cache_dir.glob("*.json")) == []

    @pytest.mark.asyncio
    async def test_real_cache_different_keys(self, adapter):
        """Should handle different keys independently."""
        await adapter.set("key1", "content1")
        await adapter.set("key2", "content2")

        assert await adapter.get("key1") == "content1"
        assert await adapter.get("key2") == "content2"
        assert await adapter.get("key3") is None

    @pytest.mark.asyncio
    async def test_real_cache_default_ttl_is_used_when_none(self, adapter):
        """A None TTL must fall back to the manager default."""
        await adapter.set("key-without-ttl", "content")

        assert await adapter.get("key-without-ttl") == "content"

    @pytest.mark.asyncio
    async def test_real_cache_set_swallows_non_serialisable_payload(self, adapter):
        """A payload that cannot be serialised must not break the adapter."""
        await adapter.set("bad-key", {"not": {1, 2, 3}})

        assert await adapter.get("bad-key") is None
