import time
import json
import hashlib
from pathlib import Path
from typing import Any, Optional


class CacheManager:
    """
    Handles file-based caching with TTL (Time-To-Live) support.
    """

    def __init__(self, cache_dir: Path, ttl_seconds: int = 86400):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        key_hash = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        path = self._get_cache_path(key)
        effective_ttl = ttl if ttl is not None else self.ttl_seconds
        payload = {"timestamp": time.time(), "ttl": effective_ttl, "data": data}
        path.write_text(json.dumps(payload), encoding="utf-8")

    def get(self, key: str) -> Optional[Any]:
        path = self._get_cache_path(key)
        if not path.exists():
            return None

        payload = json.loads(path.read_text(encoding="utf-8"))
        ttl = payload.get("ttl", self.ttl_seconds)
        if time.time() - payload["timestamp"] > ttl:
            path.unlink()  # Evict
            return None

        return payload["data"]

    def invalidate(self, key: str) -> None:
        """Manually remove an item from the cache."""
        path = self._get_cache_path(key)
        if path.exists():
            path.unlink()
