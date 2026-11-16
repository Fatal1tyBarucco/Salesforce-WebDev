"""LLM cache adapters (exact + semantic)."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from src.cache_manager import CacheManager
from src.domain.llm import LLMPrompt, LLMResponse

logger = logging.getLogger(__name__)


class LLMCacheAdapter:
    """Exact-match cache for LLM responses using CacheManager."""

    def __init__(
        self, cache_manager: CacheManager | None = None, cache_dir: Path = Path("cache/llm")
    ):
        self._cache = cache_manager or CacheManager(cache_dir=cache_dir)
        self._ttl_default = 7 * 24 * 3600  # 7 days

    async def get(self, key: str) -> LLMResponse | None:
        """Get cached response by exact key."""
        try:
            data = self._cache.get(f"llm:{key}")
            if data:
                return LLMResponse.model_validate_json(data)
        except Exception as e:
            logger.debug("Cache get failed for %s: %s", key, e)
        return None

    async def set(self, key: str, response: LLMResponse, ttl_seconds: int | None = None) -> None:
        """Cache response with TTL."""
        try:
            ttl = ttl_seconds or self._ttl_default
            self._cache.set(f"llm:{key}", response.model_dump_json(), ttl=ttl)
        except Exception as e:
            logger.debug("Cache set failed for %s: %s", key, e)

    async def invalidate(self, key: str) -> None:
        """Invalidate cache for key."""
        try:
            self._cache.set(f"llm:{key}", "", ttl=0)
        except Exception as e:
            logger.debug("Cache invalidate failed for %s: %s", key, e)


class SemanticCacheAdapter:
    """Semantic cache using embeddings for similar prompt matching."""

    def __init__(self, cache_dir: Path = Path("cache/llm/semantic"), threshold: float = 0.95):
        self.cache_dir = cache_dir
        self.threshold = threshold
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = cache_dir / "index.json"
        self._index: dict[str, dict[str, Any]] = self._load_index()

    def _load_index(self) -> dict[str, dict[str, Any]]:  # type: ignore[no-any-return]
        if self._index_file.exists():
            try:
                return json.loads(self._index_file.read_text())  # type: ignore[no-any-return]
            except Exception:
                pass
        return {}

    def _save_index(self) -> None:
        try:
            self._index_file.write_text(json.dumps(self._index))
        except Exception as e:
            logger.debug("Failed to save semantic index: %s", e)

    def _get_embedding(self, text: str) -> list[float]:
        """Get embedding for text (placeholder - implement with actual embedding model).

        Components are centered around zero so that cosine similarity is
        discriminative: raw bytes in ``[0, 1]`` make unrelated texts score ~0.8.
        """
        import hashlib

        hash_bytes = hashlib.md5(text.encode()).digest()
        return [b / 255.0 - 0.5 for b in hash_bytes[:16]]  # 16-dim vector

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        import math

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    async def get(self, prompt: LLMPrompt) -> LLMResponse | None:
        """Get semantically similar cached response."""
        prompt_text = f"{prompt.system}\n{prompt.user}"
        prompt_embedding = self._get_embedding(prompt_text)

        best_key = None
        best_score = 0.0

        for key, entry in self._index.items():
            score = self._cosine_similarity(prompt_embedding, entry["embedding"])
            if score >= self.threshold and score > best_score:
                best_score = score
                best_key = key

        if best_key:
            response_file = self.cache_dir / f"{best_key}.json"
            if response_file.exists():
                try:
                    return LLMResponse.model_validate_json(response_file.read_text())
                except Exception as e:
                    logger.debug("Failed to load semantic cache: %s", e)

        return None

    async def set(self, prompt: LLMPrompt, response: LLMResponse) -> None:
        """Cache response with semantic embedding."""
        prompt_text = f"{prompt.system}\n{prompt.user}"
        embedding = self._get_embedding(prompt_text)

        key = prompt.cache_key()
        response_file = self.cache_dir / f"{key}.json"

        try:
            response_file.write_text(response.model_dump_json(), encoding="utf-8")
            self._index[key] = {
                "embedding": embedding,
                "prompt_hash": hash(prompt_text),
                "timestamp": time.time(),
            }
            self._save_index()
        except Exception as e:
            logger.debug("Failed to set semantic cache: %s", e)
