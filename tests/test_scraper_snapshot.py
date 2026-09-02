"""Snapshot test for scraper rate-limiter consistency (newPrompt.md §Testes)."""

from __future__ import annotations

import pytest
from src.scraper import RateLimiter, RATE_LIMIT_RPS


@pytest.mark.asyncio
async def test_scraper_rate_limiter_config_snapshot() -> None:
    limiter = RateLimiter()
    assert limiter._min_interval == 1.0 / RATE_LIMIT_RPS
    assert limiter._min_interval == 0.5
