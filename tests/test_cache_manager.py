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
    r = repr(stats)
    assert "hits=10" in r
    assert "misses=2" in r


def test_stats_total():
    stats = CacheStats(hits=8, misses=2)
    assert stats.total == 10


def test_stats_hit_rate_zero():
    stats = CacheStats()
    assert stats.hit_rate == 0.0


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


# ── Content hash ──────────────────────────────────────────────────


def test_compute_file_hash(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello world")
    h = CacheManager.compute_file_hash(f)
    assert len(h) == 32


def test_get_content_hash_exists(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    f = tmp_path / "test.txt"
    f.write_text("content")
    h = cache.get_content_hash(f)
    assert h is not None


def test_get_content_hash_not_exists(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    h = cache.get_content_hash(tmp_path / "nonexistent.txt")
    assert h is None


def test_is_content_unchanged(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    f = tmp_path / "test.txt"
    f.write_text("content")
    h = cache.get_content_hash(f)
    assert cache.is_content_unchanged(f, h) is True
    assert cache.is_content_unchanged(f, "wrong_hash") is False


def test_is_content_unchanged_nonexistent(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    assert cache.is_content_unchanged(tmp_path / "nope", "hash") is False


# ── Content cache (JSON file) ────────────────────────────────────


def test_save_and_load_content_cache(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    cache_file = tmp_path / "content_cache.json"
    data = {"file1.md": "abc123", "file2.md": "def456"}
    cache.save_content_cache(cache_file, data)
    loaded = cache.load_content_cache(cache_file)
    assert loaded == data


def test_load_content_cache_nonexistent(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    result = cache.load_content_cache(tmp_path / "nope.json")
    assert result == {}


def test_load_content_cache_corrupt(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    f = tmp_path / "corrupt.json"
    f.write_text("not json")
    result = cache.load_content_cache(f)
    assert result == {}


def test_load_content_cache_old_format(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    f = tmp_path / "old.json"
    import json as json_mod

    f.write_text(json_mod.dumps({"file.md": {"content_hash": "abc123", "extra": "data"}}))
    result = cache.load_content_cache(f)
    assert result == {"file.md": "abc123"}


# ── Edge cases ───────────────────────────────────────────────────


def test_invalidate_nonexistent(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    cache.invalidate("nonexistent_key")


def test_invalidate_namespace_with_entries(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    cache.set("k1", "v1", namespace="test_ns")
    cache.set("k2", "v2", namespace="test_ns")
    count = cache.invalidate_namespace("test_ns")
    assert count == 2
    assert cache.get("k1", namespace="test_ns") is None


def test_get_expired_entry(tmp_path):
    cache = CacheManager(cache_dir=tmp_path / "cache", ttl_seconds=1)
    cache.set("key", "value", ttl=0)
    import time as time_mod

    time_mod.sleep(0.01)
    result = cache.get("key")
    assert result is None
    assert cache.stats.evictions == 1
