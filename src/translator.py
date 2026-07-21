"""LLM-powered translation service with caching."""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from pathlib import Path
from typing import Optional

from .llm_service import LLMService


class TranslatorService:
    """Translates release notes content using LLM with caching."""

    CACHE_TTL_SECONDS: int = 7 * 24 * 60 * 60  # 7 days

    def __init__(self, cache_dir: str = "cache", llm: Optional[LLMService] = None) -> None:
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._llm = llm or LLMService()
        self._cache: dict[str, dict[str, object]] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        cache_file = self._cache_dir / ".translation_cache.json"
        if cache_file.exists():
            try:
                self._cache = json.loads(cache_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._cache = {}

    def _save_cache(self) -> None:
        cache_file = self._cache_dir / ".translation_cache.json"
        cache_file.write_text(
            json.dumps(self._cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _cache_key(self, text: str, source: str, target: str) -> str:
        raw = f"{source}:{target}:{text}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _get_cached(self, key: str) -> Optional[str]:
        if key in self._cache:
            entry = self._cache[key]
            ts = entry.get("timestamp", 0)
            if isinstance(ts, (int, float)) and time.time() - ts < self.CACHE_TTL_SECONDS:
                return str(entry["translation"])
            del self._cache[key]
        return None

    def _set_cached(self, key: str, translation: str) -> None:
        self._cache[key] = {"translation": translation, "timestamp": time.time()}
        self._save_cache()

    async def translate_feature(self, text: str, source: str, target: str) -> str:
        """Translate a single feature description."""
        if source == target:
            return text

        key = self._cache_key(text, source, target)
        cached = self._get_cached(key)
        if cached is not None:
            return cached

        system_prompt = (
            f"You are a professional translator. Translate the following Salesforce "
            f"release note feature from {'Portuguese' if source == 'pt_BR' else 'English'} "
            f"to {'English' if target == 'en_US' else 'Portuguese'}. "
            f"Keep technical terms (API, LWC, Apex, etc.) unchanged. "
            f"Return ONLY the translated text, nothing else."
        )

        result = await self._llm.generate_text(text, system_prompt)
        if result is None:
            return text

        self._set_cached(key, result)
        return result

    async def translate_batch(self, features: list[str], source: str, target: str) -> list[str]:
        """Translate multiple features in parallel."""
        tasks = [self.translate_feature(f, source, target) for f in features]
        return list(await asyncio.gather(*tasks))

    async def translate_category(self, name: str, source: str, target: str) -> str:
        """Translate a category name."""
        return await self.translate_feature(name, source, target)
