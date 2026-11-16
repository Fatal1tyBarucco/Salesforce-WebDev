"""Tests for the scraper AsyncRateLimiter (token bucket with adaptive limits).

The tests below describe the *real* contract of
``src.infrastructure.scraping.rate_limiter``:

* the bucket starts with ``burst`` tokens and is refilled at ``current_rps``
  tokens per second, capped at ``burst`` tokens;
* ``get_state()`` creates the state for an unknown key and always returns the
  four monitoring keys ``current_rps``, ``tokens_available``,
  ``consecutive_successes`` and ``consecutive_failures``;
* adaptation raises the limit after 10 consecutive successes and lowers it
  after 3 consecutive failures.
"""

from __future__ import annotations

import asyncio
import time

import pytest

from src.infrastructure.scraping.rate_limiter import AsyncRateLimiter, RateLimitState


class TestRateLimitState:
    """Tests for the RateLimitState dataclass."""

    def test_default_values(self):
        """Should expose the documented fields with the given values."""
        state = RateLimitState(
            tokens=5.0,
            current_rps=10.0,
            max_rps=50.0,
            min_rps=0.5,
            burst=5,
        )

        assert state.tokens == 5.0
        assert state.current_rps == 10.0
        assert state.max_rps == 50.0
        assert state.min_rps == 0.5
        assert state.burst == 5
        assert state.consecutive_successes == 0
        assert state.consecutive_failures == 0

    def test_last_refill_defaults_to_now(self):
        """last_refill should be initialised with a monotonic timestamp."""
        before = time.monotonic()
        state = RateLimitState(tokens=1.0)
        after = time.monotonic()

        assert before <= state.last_refill <= after


class TestAsyncRateLimiterConstruction:
    """Tests for the constructor wiring of the limiter."""

    def test_defaults(self):
        """Should use the documented default parameters."""
        limiter = AsyncRateLimiter()

        state = limiter._get_state("default")
        assert state.current_rps == 10.0
        assert state.max_rps == 50.0
        assert state.min_rps == 0.5
        assert state.burst == 5
        assert state.tokens == 5

    def test_custom_parameters_are_propagated_to_new_keys(self):
        """New keys must inherit rps/burst/min_rps/max_rps from the constructor."""
        limiter = AsyncRateLimiter(rps=20.0, burst=10, min_rps=1.0, max_rps=100.0)

        state = limiter._get_state("brand-new-key")
        assert state.current_rps == 20.0
        assert state.burst == 10
        assert state.min_rps == 1.0
        assert state.max_rps == 100.0
        assert state.tokens == 10

    def test_custom_burst_controls_initial_token_count(self):
        """The bucket must start with exactly ``burst`` tokens."""
        limiter = AsyncRateLimiter(rps=1.0, burst=3)

        assert limiter.get_state("default")["tokens_available"] == 3

    def test_state_is_created_only_once_per_key(self):
        """Repeated calls must not reset an existing state."""
        limiter = AsyncRateLimiter(rps=10.0, burst=5)

        first = limiter._get_state("k")
        first.current_rps = 42.0

        assert limiter._get_state("k").current_rps == 42.0


class TestAsyncRateLimiterAcquire:
    """Tests for token acquisition."""

    @pytest.fixture
    def limiter(self):
        """Create rate limiter with test settings."""
        return AsyncRateLimiter(rps=10.0, burst=5, min_rps=0.5, max_rps=50.0, adaptive=True)

    @pytest.mark.asyncio
    async def test_acquire_allows_immediate_when_tokens_available(self, limiter):
        """Should consume one token without waiting."""
        await limiter.acquire("default", tokens=1)

        assert limiter.get_state("default")["tokens_available"] == 4.0

    @pytest.mark.asyncio
    async def test_acquire_consumes_multiple_tokens(self, limiter):
        """Should consume all requested tokens at once."""
        await limiter.acquire("default", tokens=3)

        assert limiter.get_state("default")["tokens_available"] == 2.0

    @pytest.mark.asyncio
    async def test_acquire_waits_when_tokens_exhausted(self, limiter):
        """Should block until the bucket refills."""
        for _ in range(5):
            await limiter.acquire("default", tokens=1)

        assert limiter.get_state("default")["tokens_available"] == 0.0

        await asyncio.wait_for(limiter.acquire("default", tokens=1), timeout=10)

        # The bucket refilled up to its capacity (5) and one token was consumed.
        assert limiter.get_state("default")["tokens_available"] == 4.0

    @pytest.mark.asyncio
    async def test_acquire_uses_default_key(self, limiter):
        """Calling acquire() without a key must use the 'default' bucket."""
        await limiter.acquire()

        assert limiter.get_state("default")["tokens_available"] == 4.0

    @pytest.mark.asyncio
    async def test_multiple_keys_are_independent(self, limiter):
        """Each key should have its own token bucket."""
        await limiter.acquire("key1", tokens=3)
        await limiter.acquire("key2", tokens=1)

        assert limiter.get_state("key1")["tokens_available"] == 2.0
        assert limiter.get_state("key2")["tokens_available"] == 4.0

    @pytest.mark.asyncio
    async def test_concurrent_acquires_are_serialised(self, limiter):
        """Concurrent acquires must not hand out more tokens than available."""

        async def acquire_once():
            await limiter.acquire("default", tokens=1)

        await asyncio.gather(*[acquire_once() for _ in range(5)])

        assert limiter.get_state("default")["tokens_available"] == 0.0


class TestAsyncRateLimiterRefill:
    """Tests for the token refill behaviour."""

    @pytest.fixture
    def limiter(self):
        """Create rate limiter with test settings."""
        return AsyncRateLimiter(rps=10.0, burst=5, min_rps=0.5, max_rps=50.0, adaptive=True)

    @pytest.mark.asyncio
    async def test_refill_is_capped_by_burst_not_by_max_rps(self, limiter):
        """The bucket capacity is ``burst``; ``max_rps`` is a rate, not a token count."""
        for _ in range(5):
            await limiter.acquire("default", tokens=1)

        state = limiter._get_state("default")
        state.last_refill = time.monotonic() - 5.0
        limiter._refill(state)

        assert state.tokens == 5

    @pytest.mark.asyncio
    async def test_acquire_after_idle_refills_up_to_burst(self, limiter):
        """After an idle period the bucket holds ``burst`` tokens again."""
        for _ in range(5):
            await limiter.acquire("default", tokens=1)

        limiter._get_state("default").last_refill = time.monotonic() - 5.0

        await limiter.acquire("default", tokens=1)

        assert limiter.get_state("default")["tokens_available"] == 4.0

    @pytest.mark.asyncio
    async def test_acquire_after_real_idle_refills_up_to_burst(self, limiter):
        """Same guarantee when the idle time comes from the real clock."""
        for _ in range(5):
            await limiter.acquire("default", tokens=1)

        await asyncio.sleep(1.05)

        await limiter.acquire("default", tokens=1)

        assert limiter.get_state("default")["tokens_available"] == 4.0

    def test_refill_rate_follows_current_rps(self):
        """The refill rate must be the currently effective rps."""
        limiter = AsyncRateLimiter(rps=1.0, burst=10)
        state = limiter._get_state("default")
        state.tokens = 0.0

        state.last_refill = time.monotonic() - 1.5
        limiter._refill(state)

        assert 1.4 <= state.tokens <= 1.6

    def test_refill_does_not_run_before_the_interval(self):
        """Nothing is refilled while less than one second has passed."""
        limiter = AsyncRateLimiter(rps=100.0, burst=5)
        state = limiter._get_state("default")
        state.tokens = 0.0

        limiter._refill(state)

        assert state.tokens == 0.0


class TestAsyncRateLimiterAdaptation:
    """Tests for the adaptive behaviour."""

    @pytest.fixture
    def limiter(self):
        """Create rate limiter with test settings."""
        return AsyncRateLimiter(rps=10.0, burst=5, min_rps=0.5, max_rps=50.0, adaptive=True)

    @pytest.mark.asyncio
    async def test_record_success_increases_rate_after_ten_successes(self, limiter):
        """Should increase the limit by 10% after 10 consecutive successes."""
        for _ in range(9):
            await limiter.record_success("default")

        assert limiter.get_current_limit("default") == 10.0

        await limiter.record_success("default")

        assert limiter.get_current_limit("default") == 11.0
        assert limiter.get_state("default")["consecutive_successes"] == 0

    @pytest.mark.asyncio
    async def test_record_success_does_not_exceed_max(self, limiter):
        """Should never exceed max_rps."""
        for _ in range(200):
            await limiter.record_success("default")

        assert limiter.get_current_limit("default") <= 50.0

    @pytest.mark.asyncio
    async def test_record_success_resets_failure_counter(self, limiter):
        """A success must clear the consecutive failure counter."""
        await limiter.record_failure("default", "boom")
        await limiter.record_failure("default", "boom")

        assert limiter.get_state("default")["consecutive_failures"] == 2

        await limiter.record_success("default")

        assert limiter.get_state("default")["consecutive_failures"] == 0

    @pytest.mark.asyncio
    async def test_record_failure_halves_rate_after_three_failures(self, limiter):
        """Should halve the limit after 3 consecutive failures."""
        for _ in range(2):
            await limiter.record_failure("default", "boom")

        assert limiter.get_current_limit("default") == 10.0

        await limiter.record_failure("default", "boom")

        assert limiter.get_current_limit("default") == 5.0
        assert limiter.get_state("default")["consecutive_failures"] == 0

    @pytest.mark.asyncio
    async def test_record_failure_does_not_go_below_min(self, limiter):
        """Should never drop below min_rps."""
        for _ in range(100):
            await limiter.record_failure("default", "boom")

        assert limiter.get_current_limit("default") >= 0.5

    @pytest.mark.asyncio
    async def test_record_failure_resets_success_counter(self, limiter):
        """A failure must clear the consecutive success counter."""
        for _ in range(5):
            await limiter.record_success("default")

        assert limiter.get_state("default")["consecutive_successes"] == 5

        await limiter.record_failure("default", "boom")

        assert limiter.get_state("default")["consecutive_successes"] == 0

    @pytest.mark.asyncio
    async def test_record_failure_accepts_error_type(self, limiter):
        """The error_type argument is accepted and does not break the adaptation."""
        await limiter.record_failure("default", "timeout")

        assert limiter.get_state("default")["consecutive_failures"] == 1

    @pytest.mark.asyncio
    async def test_adaptive_false_disables_adaptation(self):
        """Adaptive=False must keep the limit and the counters untouched."""
        limiter = AsyncRateLimiter(rps=10.0, burst=5, adaptive=False)

        for _ in range(20):
            await limiter.record_success("default")
        for _ in range(20):
            await limiter.record_failure("default", "boom")

        state = limiter.get_state("default")
        assert state["current_rps"] == 10.0
        assert state["consecutive_successes"] == 0
        assert state["consecutive_failures"] == 0

    @pytest.mark.asyncio
    async def test_adaptation_over_time(self):
        """Successes raise the limit and failures lower it again."""
        limiter = AsyncRateLimiter(rps=10.0, burst=5, adaptive=True)

        assert limiter.get_current_limit("default") == 10.0

        for _ in range(15):
            await limiter.record_success("default")

        assert limiter.get_current_limit("default") > 10.0

        for _ in range(5):
            await limiter.record_failure("default", "boom")

        assert limiter.get_current_limit("default") >= 0.5


class TestAsyncRateLimiterMonitoring:
    """Tests for the monitoring API."""

    @pytest.fixture
    def limiter(self):
        """Create rate limiter with test settings."""
        return AsyncRateLimiter(rps=10.0, burst=5, min_rps=0.5, max_rps=50.0, adaptive=True)

    def test_get_current_limit(self, limiter):
        """Should return the effective limit of the key."""
        assert limiter.get_current_limit("default") == 10.0

    def test_get_current_limit_for_unknown_key(self, limiter):
        """An unknown key gets the default limit."""
        assert limiter.get_current_limit("never-seen") == 10.0

    def test_get_state_returns_the_monitoring_keys(self, limiter):
        """Should return the four documented monitoring keys."""
        state = limiter.get_state("default")

        assert set(state) == {
            "current_rps",
            "tokens_available",
            "consecutive_successes",
            "consecutive_failures",
        }

    def test_get_state_creates_the_state_for_an_unknown_key(self, limiter):
        """get_state() is not a read-only probe: it materialises the bucket."""
        state = limiter.get_state("unknown-key")

        assert state["current_rps"] == 10.0
        assert state["tokens_available"] == 5
        assert state["consecutive_successes"] == 0
        assert state["consecutive_failures"] == 0

    def test_get_state_reflects_consumed_tokens(self, limiter):
        """The reported token count follows the acquisitions."""
        limiter._get_state("default").tokens = 2.0

        assert limiter.get_state("default")["tokens_available"] == 2.0
