"""LLM cache adapters (exact + semantic).

ADR-011: TTL centralizado em config, index semântico com escrita atômica,
leitura tolerante e embedding placeholder SHA-256 (MD5 removido).
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from src.cache_io import atomic_write_json, atomic_write_text, read_json_safe
from src.cache_manager import CacheManager
from src.config import CACHE_LLM_TTL_SECONDS
from src.domain.llm import LLMPrompt, LLMResponse

logger = logging.getLogger(__name__)


class LLMCacheAdapter:
    """Exact-match cache for LLM responses using CacheManager."""

    def __init__(
        self,
        cache_manager: CacheManager | None = None,
        cache_dir: Path = Path("cache/llm"),
    ):
        self._cache = cache_manager or CacheManager(cache_dir=cache_dir)
        self._ttl_default = CACHE_LLM_TTL_SECONDS  # 7 days (ADR-010/ADR-011)

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

    def _load_index(self) -> dict[str, dict[str, Any]]:
        data = read_json_safe(self._index_file)
        if isinstance(data, dict):
            return {str(k): v for k, v in data.items() if isinstance(v, dict)}
        return {}

    def _save_index(self) -> None:
        try:
            atomic_write_json(self._index_file, self._index)
        except OSError as e:
            logger.debug("Failed to save semantic index: %s", e)

    def _get_embedding(self, text: str) -> list[float]:
        """Get embedding for text (placeholder - implement with actual embedding model).

        Components are centered around zero so that cosine similarity is
        discriminative: raw bytes in ``[0, 1]`` make unrelated texts score ~0.8.
        SHA-256 replaces MD5 (ADR-011); old index entries simply miss and are
        recomputed — safe degradation for a derivable cache.
        """
        import hashlib

        hash_bytes = hashlib.sha256(text.encode()).digest()
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
        import hashlib

        prompt_text = f"{prompt.system}\n{prompt.user}"
        embedding = self._get_embedding(prompt_text)

        key = prompt.cache_key()
        response_file = self.cache_dir / f"{key}.json"

        try:
            atomic_write_text(response_file, response.model_dump_json())
            self._index[key] = {
                "embedding": embedding,
                "prompt_hash": hashlib.sha256(prompt_text.encode()).hexdigest()[:16],
                "timestamp": time.time(),
            }
            self._save_index()
        except OSError as e:
            logger.debug("Failed to set semantic cache: %s", e)
