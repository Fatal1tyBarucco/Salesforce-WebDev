"""Adaptive rate limiter for LLM providers."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from src.domain.llm import LLMProvider, LLMRateLimiterPort

logger = logging.getLogger(__name__)


@dataclass
class ProviderRateLimitState:
    """Current rate limit state for a provider."""

    tokens: float
    current_rps: float
    max_rps: float
    min_rps: float
    burst: int
    last_refill: float = field(default_factory=time.monotonic)
    consecutive_successes: int = 0
    consecutive_failures: int = 0


class AdaptiveRateLimiter(LLMRateLimiterPort):
    """Token bucket rate limiter with adaptive capabilities per provider."""

    def __init__(
        self,
        default_rps: float = 10.0,
        default_burst: int = 5,
        min_rps: float = 0.5,
        max_rps: float = 50.0,
        adaptive: bool = True,
    ) -> None:
        self._default_rps = default_rps
        self._default_burst = default_burst
        self._min_rps = min_rps
        self._max_rps = max_rps
        self._adaptive = adaptive
        self._states: dict[str, ProviderRateLimitState] = {}
        self._lock = asyncio.Lock()
        self._refill_interval = 1.0

    def _get_state(self, provider: str, rps: float, burst: int) -> ProviderRateLimitState:
        if provider not in self._states:
            self._states[provider] = ProviderRateLimitState(
                tokens=burst,
                current_rps=rps,
                max_rps=max(rps, self._max_rps),
                min_rps=self._min_rps,
                burst=burst,
            )
        return self._states[provider]

    def _refill(self, state: ProviderRateLimitState) -> None:
        now = time.monotonic()
        elapsed = now - state.last_refill
        if elapsed >= 1.0:
            new_tokens = elapsed * state.current_rps
            state.tokens = min(state.burst, state.tokens + new_tokens)
            state.last_refill = now

    async def acquire(self, provider: LLMProvider, tokens: int = 1) -> None:
        """Acquire permission to make a request."""
        provider_key = provider.value
        state = self._get_state(provider_key, self._default_rps, self._default_burst)

        async with self._lock:
            self._refill(state)

            while state.tokens < tokens:
                wait_time = (tokens - state.tokens) / state.current_rps
                await asyncio.sleep(min(wait_time, 1.0))
                self._refill(state)

            state.tokens -= tokens

    async def record_success(self, provider: LLMProvider) -> None:
        """Record successful request."""
        if not self._adaptive:
            return

        provider_key = provider.value
        state = self._get_state(provider_key, self._default_rps, self._default_burst)

        async with self._lock:
            state.consecutive_successes += 1
            state.consecutive_failures = 0

            if state.consecutive_successes >= 10 and state.current_rps < state.max_rps:
                state.current_rps = min(state.current_rps * 1.1, state.max_rps)
                state.consecutive_successes = 0
                logger.debug(
                    "Rate limit increased to %.1f RPS for %s", state.current_rps, provider_key
                )

    async def record_failure(self, provider: LLMProvider, error: Exception) -> None:
        """Record failed request."""
        if not self._adaptive:
            return

        provider_key = provider.value
        state = self._get_state(provider_key, self._default_rps, self._default_burst)

        async with self._lock:
            state.consecutive_failures += 1
            state.consecutive_successes = 0

            if state.consecutive_failures >= 3:
                state.current_rps = max(state.current_rps * 0.5, state.min_rps)
                state.consecutive_failures = 0
                logger.warning(
                    "Rate limit decreased to %.1f RPS for %s", state.current_rps, provider_key
                )

    def get_current_limit(self, provider: LLMProvider) -> float:
        """Get current effective rate limit."""
        provider_key = provider.value
        state = self._states.get(provider_key)
        return state.current_rps if state else self._default_rps

    def get_state(self, provider: LLMProvider) -> dict[str, Any]:
        """Get full state for monitoring."""
        provider_key = provider.value
        state = self._states.get(provider_key)
        if not state:
            return {}
        return {
            "current_rps": state.current_rps,
            "tokens_available": state.tokens,
            "consecutive_successes": state.consecutive_successes,
            "consecutive_failures": state.consecutive_failures,
            "burst": state.burst,
        }
