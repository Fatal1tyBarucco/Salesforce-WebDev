from unittest.mock import patch
from src.cache_manager import CacheManager


def test_cache_set_get(tmp_path):
    cache_dir = tmp_path / "cache"
    cache = CacheManager(cache_dir=cache_dir)

    cache.set("key1", "value1", ttl=3600)
    assert cache.get("key1") == "value1"


def test_cache_miss(tmp_path):
    cache_dir = tmp_path / "cache"
    cache = CacheManager(cache_dir=cache_dir)

    assert cache.get("nonexistent") is None


def test_cache_ttl_expiration(tmp_path):
    cache_dir = tmp_path / "cache"
    cache = CacheManager(cache_dir=cache_dir)

    with patch("time.time") as mock_time:
        mock_time.return_value = 1000.0
        cache.set("key1", "value1", ttl=3600)  # 1 hour TTL
        assert cache.get("key1") == "value1"

        mock_time.return_value = 5000.0  # More than 1 hour later
        assert cache.get("key1") is None


def test_cache_invalidate(tmp_path):
    cache_dir = tmp_path / "cache"
    cache = CacheManager(cache_dir=cache_dir)

    cache.set("key1", "value1", ttl=3600)
    cache.invalidate("key1")
    assert cache.get("key1") is None
