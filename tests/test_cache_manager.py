from unittest.mock import patch
from src.cache_manager import CacheManager, CacheStats


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


# ------------------------------------------------------------------
# Namespace support
# ------------------------------------------------------------------


def test_namespace_set_get(tmp_path):
    cache_dir = tmp_path / "cache"
    cache = CacheManager(cache_dir=cache_dir)

    cache.set("key1", "data_a", namespace="llm")
    cache.set("key2", "data_b", namespace="scraper")

    assert cache.get("key1", namespace="llm") == "data_a"
    assert cache.get("key2", namespace="scraper") == "data_b"
    # Cross-namespace miss
    assert cache.get("key1", namespace="scraper") is None


def test_namespace_invalidate(tmp_path):
    cache_dir = tmp_path / "cache"
    cache = CacheManager(cache_dir=cache_dir)

    cache.set("k1", "v1", namespace="llm")
    cache.set("k2", "v2", namespace="llm")
    cache.set("k3", "v3", namespace="other")

    removed = cache.invalidate_namespace("llm")
    assert removed == 2
    assert cache.get("k1", namespace="llm") is None
    assert cache.get("k3", namespace="other") == "v3"


def test_namespace_invalidate_empty(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    assert cache.invalidate_namespace("nonexistent") == 0


# ------------------------------------------------------------------
# Cache stats
# ------------------------------------------------------------------


def test_stats_hit_miss(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")

    cache.get("miss")  # miss
    cache.set("k", "v")
    cache.get("k")  # hit

    stats = cache.stats
    assert stats.hits == 1
    assert stats.misses == 1
    assert stats.total == 2
    assert stats.hit_rate == 0.5


def test_stats_eviction(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")

    with patch("time.time") as mock_time:
        mock_time.return_value = 1000.0
        cache.set("expired", "data", ttl=10)

        mock_time.return_value = 5000.0
        cache.get("expired")  # triggers eviction

    stats = cache.stats
    assert stats.evictions == 1
    assert stats.misses == 1


def test_stats_sets(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    cache.set("a", 1)
    cache.set("b", 2)
    assert cache.stats.sets == 2


def test_stats_repr():
    stats = CacheStats(hits=10, misses=2, evictions=1)
    assert "hit_rate=" in repr(stats)


def test_clear_expired(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")

    with patch("time.time") as mock_time:
        mock_time.return_value = 1000.0
        cache.set("old", "data", ttl=10)
        cache.set("fresh", "data", ttl=99999)

        mock_time.return_value = 5000.0
        removed = cache.clear_expired()

        assert removed == 1
        assert cache.get("fresh") == "data"
