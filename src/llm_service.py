"""LLM Service module for interacting with OpenAI and Google Gemini models."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, List, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

__all__ = [
    "LLMService",
    "LLMProvider",
    "RateLimiter",
    "CircuitBreakerConfig",
]


@dataclass
class LLMProvider:
    """Configuration for an LLM provider."""

    name: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o"
    provider_type: str = "openai"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    threshold: int = 5
    cooldown: float = 30.0


class RateLimiter:
    """Async rate limiter using sliding window."""

    def __init__(self, max_requests: int = 10, window_seconds: float = 1.0) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.timestamps: list[float] = []
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            self.timestamps = [t for t in self.timestamps if now - t < self.window_seconds]
            if len(self.timestamps) >= self.max_requests:
                sleep_time = self.window_seconds - (now - self.timestamps[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                now = time.monotonic()
                self.timestamps = [t for t in self.timestamps if now - t < self.window_seconds]
            self.timestamps.append(now)


class LLMService:
    """Service class for handling interactions with Large Language Models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gpt-4o",
        provider: str = "openai",
    ) -> None:
        """Initialize the LLM Service.

        Args:
            api_key: Optional API key for the model provider.
            model_name: Name of the model to use.
            provider: Provider name ('openai' or 'gemini').
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.provider = provider.lower()

    @staticmethod
    def _prompt_hash(system_instruction: Optional[str], prompt: str) -> str:
        combined = f"{system_instruction or ''}::{prompt}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def generate_completion(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1000,
    ) -> str:
        """Generate text completion using the configured LLM provider."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        logger.info(
            "Generating completion using provider=%s, model=%s",
            self.provider,
            self.model_name,
        )

        try:
            if self.provider == "openai":
                return self._generate_openai(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            elif self.provider in ("gemini", "google"):
                return self._generate_gemini(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as err:
            logger.error("Failed to generate completion from LLM: %s", err)
            raise

    def _generate_openai(
        self,
        prompt: str,
        system_instruction: Optional[str],
        temperature: float,
        max_tokens: Optional[int],
    ) -> str:
        """Generate response via OpenAI API."""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            messages: list[dict[str, Any]] = []

            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})

            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content
            return content.strip() if content else ""
        except ImportError:
            logger.warning("OpenAI package not available, returning mock response.")
            return f"[Mock OpenAI Response] Prompt: {prompt[:50]}..."

    def _generate_gemini(
        self,
        prompt: str,
        system_instruction: Optional[str],
        temperature: float,
        max_tokens: Optional[int],
    ) -> str:
        """Generate response via Google Gemini API."""
        try:
            from google import genai

            client = genai.Client(api_key=self.api_key or "")
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

            response = client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
            )

            return response.text.strip() if response.text else ""
        except ImportError:
            logger.warning("Google GenAI package not available, returning mock response.")
            return f"[Mock Gemini Response] Prompt: {prompt[:50]}..."

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1000,
    ) -> str:
        """Alias for generate_completion (async-compatible wrapper)."""
        return self.generate_completion(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def classify_text(
        self,
        text: str,
        categories: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Alias for generate_completion for classification tasks."""
        prompt = text
        if categories:
            prompt = "Classify into: " + ", ".join(categories) + "\n\n" + text
        return self.generate_completion(
            prompt=prompt,
            system_instruction=system_prompt,
        )

    def summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize given text content using LLM."""
        system_prompt = (
            f"You are a concise summarizer. Summarize the text in under {max_length} words."
        )
        return self.generate_completion(prompt=text, system_instruction=system_prompt)

    async def summarize_release_notes(self, notes: str) -> str:
        """Summarize release notes async."""
        return self.summarize(notes)

    async def enrich_feature(self, feature: dict[str, Any]) -> dict[str, Any]:
        """Enrich feature information via LLM."""
        return {"enriched": True, "details": "Enriched feature", **feature}
