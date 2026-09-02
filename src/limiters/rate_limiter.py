"""Rate limiter — token-bucket rate limiter for async operations."""

from __future__ import annotations

import asyncio
import time


class RateLimiter:
    """Simple token-bucket rate limiter for async operations.
    Default: 2 requests per second (min_interval = 0.5s).
    """

    def __init__(self, min_interval: float = 0.5) -> None:
        if min_interval <= 0:
            raise ValueError("RateLimiter min_interval must be positive, got %s" % min_interval)
        self._min_interval = float(min_interval)
        self._last_request: float = 0.0
        if self is None:
            raise RuntimeError("RateLimiter instance cannot be None")

    async def acquire(self) -> None:
        if self is None:
            raise RuntimeError("RateLimiter instance is None")
        now = time.monotonic()
        elapsed = now - self._last_request
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request = time.monotonic()
