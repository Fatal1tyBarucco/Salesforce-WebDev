"""Async rate limiter with adaptive capabilities."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RateLimitState:
    """Current state of rate limiter for a provider/client."""

    tokens: float
    last_refill: float = field(default_factory=time.monotonic)
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    current_rps: float = 10.0
    max_rps: float = 10.0
    min_rps: float = 0.5
    burst: int = 5


class AsyncRateLimiter:
    """Token bucket rate limiter with adaptive capabilities."""

    def __init__(
        self,
        rps: float = 10.0,
        burst: int = 5,
        min_rps: float = 0.5,
        max_rps: float = 50.0,
        adaptive: bool = True,
    ) -> None:
        self._default_state = RateLimitState(
            tokens=burst,
            current_rps=rps,
            max_rps=max_rps,
            min_rps=min_rps,
            burst=burst,
        )
        self._states: dict[str, RateLimitState] = {}
        self._lock = asyncio.Lock()
        self._adaptive = adaptive
        self._refill_interval = 1.0  # seconds

    def _get_state(self, key: str) -> RateLimitState:
        if key not in self._states:
            self._states[key] = RateLimitState(
                tokens=self._default_state.tokens,
                current_rps=self._default_state.current_rps,
                max_rps=self._default_state.max_rps,
                min_rps=self._default_state.min_rps,
                burst=self._default_state.burst,
            )
        return self._states[key]

    def _refill(self, state: RateLimitState) -> None:
        now = time.monotonic()
        elapsed = now - state.last_refill
        if elapsed >= self._refill_interval:
            new_tokens = elapsed * state.current_rps
            state.tokens = min(state.burst, state.tokens + new_tokens)
            state.last_refill = now

    async def acquire(self, key: str = "default", tokens: int = 1) -> None:
        """Acquire tokens, waiting if necessary."""
        async with self._lock:
            state = self._get_state(key)
            self._refill(state)

            while state.tokens < tokens:
                wait_time = (tokens - state.tokens) / state.current_rps
                await asyncio.sleep(min(wait_time, 1.0))
                self._refill(state)

            state.tokens -= tokens

    async def record_success(self, key: str = "default") -> None:
        """Record successful request - may increase rate limit."""
        if not self._adaptive:
            return

        async with self._lock:
            state = self._get_state(key)
            state.consecutive_successes += 1
            state.consecutive_failures = 0

            # Gradually increase rate limit on sustained success
            if state.consecutive_successes >= 10 and state.current_rps < state.max_rps:
                state.current_rps = min(state.current_rps * 1.1, state.max_rps)
                state.consecutive_successes = 0
                logger.debug("Rate limit increased to %.1f RPS for %s", state.current_rps, key)

    async def record_failure(self, key: str = "default", error_type: str = "unknown") -> None:
        """Record failed request - may decrease rate limit."""
        if not self._adaptive:
            return

        async with self._lock:
            state = self._get_state(key)
            state.consecutive_failures += 1
            state.consecutive_successes = 0

            # Aggressively decrease rate limit on failures
            if state.consecutive_failures >= 3:
                state.current_rps = max(state.current_rps * 0.5, state.min_rps)
                state.consecutive_failures = 0
                logger.warning("Rate limit decreased to %.1f RPS for %s", state.current_rps, key)

    def get_current_limit(self, key: str = "default") -> float:
        """Get current effective rate limit."""
        state = self._get_state(key)
        return state.current_rps

    def get_state(self, key: str = "default") -> dict[str, Any]:
        """Get full state for monitoring."""
        state = self._get_state(key)
        return {
            "current_rps": state.current_rps,
            "tokens_available": state.tokens,
            "consecutive_successes": state.consecutive_successes,
            "consecutive_failures": state.consecutive_failures,
        }
