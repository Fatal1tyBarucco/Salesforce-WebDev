from __future__ import annotations

import pytest
from src.limiters.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_config_snapshot() -> None:
    limiter = RateLimiter()
    assert limiter is not None
    assert limiter._min_interval == 0.5


@pytest.mark.asyncio
async def test_rate_limiter_defensive_none_guard() -> None:
    limiter = RateLimiter(min_interval=1.0)
    assert limiter is not None
    await limiter.acquire()
