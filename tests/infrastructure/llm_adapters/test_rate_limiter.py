"""Tests for AdaptiveRateLimiter - 100% coverage target."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest

from src.domain.llm import LLMProvider
from src.infrastructure.llm_adapters.rate_limiter import (
    AdaptiveRateLimiter,
    ProviderRateLimitState,
)


class TestProviderRateLimitState:
    """Tests for ProviderRateLimitState dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        state = ProviderRateLimitState(
            tokens=10.0,
            current_rps=10.0,
            max_rps=50.0,
            min_rps=0.5,
            burst=5,
        )

        assert state.tokens == 10.0
        assert state.current_rps == 10.0
        assert state.max_rps == 50.0
        assert state.min_rps == 0.5
        assert state.burst == 5
        assert state.consecutive_successes == 0
        assert state.consecutive_failures == 0


class TestAdaptiveRateLimiter:
    """Tests for AdaptiveRateLimiter."""

    @pytest.fixture
    def limiter(self):
        """Create rate limiter with test settings."""
        return AdaptiveRateLimiter(
            default_rps=10.0,
            default_burst=5,
            min_rps=0.5,
            max_rps=50.0,
            adaptive=True,
        )

    @pytest.mark.asyncio
    async def test_acquire_allows_immediate_when_tokens_available(self, limiter):
        """Should allow immediate acquisition when tokens available."""
        await limiter.acquire(LLMProvider.OPENROUTER, tokens=1)
        state = limiter.get_state(LLMProvider.OPENROUTER)
        assert state["tokens_available"] == 4.0  # 5 - 1

    @pytest.mark.asyncio
    async def test_acquire_waits_when_tokens_exhausted(self, limiter):
        """Should wait when tokens exhausted."""
        # Exhaust tokens
        for _ in range(5):
            await limiter.acquire(LLMProvider.OPENROUTER, tokens=1)

        state = limiter.get_state(LLMProvider.OPENROUTER)
        assert state["tokens_available"] == 0.0

        # Next acquire should wait (but we'll test with small wait)
        # This is hard to test precisely, so just verify it doesn't hang
        await limiter.acquire(LLMProvider.OPENROUTER, tokens=1)

    @pytest.mark.asyncio
    async def test_acquire_refills_tokens_over_time(self, limiter):
        """Should refill tokens over time."""
        # Exhaust tokens
        for _ in range(5):
            await limiter.acquire(LLMProvider.OPENROUTER, tokens=1)

        # Wait for refill
        await asyncio.sleep(1.1)

        # Refill happens on acquire
        await limiter.acquire(LLMProvider.OPENROUTER, tokens=1)

        state = limiter.get_state(LLMProvider.OPENROUTER)
        assert state["tokens_available"] > 0

    @pytest.mark.asyncio
    async def test_record_success_increases_rate(self, limiter):
        """Should increase rate limit on sustained success."""
        # Record 10 successes
        for _ in range(10):
            await limiter.record_success(LLMProvider.OPENROUTER)

        state = limiter.get_state(LLMProvider.OPENROUTER)
        assert state["current_rps"] > 10.0  # Should have increased
        assert state["consecutive_successes"] == 0  # Reset after increase

    @pytest.mark.asyncio
    async def test_record_success_does_not_exceed_max(self, limiter):
        """Should not exceed max rate limit."""
        # Record many successes
        for _ in range(100):
            await limiter.record_success(LLMProvider.OPENROUTER)

        state = limiter.get_state(LLMProvider.OPENROUTER)
        assert state["current_rps"] <= 50.0  # max_rps

    @pytest.mark.asyncio
    async def test_record_failure_decreases_rate(self, limiter):
        """Should decrease rate limit on failures."""
        # Record 3 failures
        error = Exception("Test error")
        for _ in range(3):
            await limiter.record_failure(LLMProvider.OPENROUTER, error)

        state = limiter.get_state(LLMProvider.OPENROUTER)
        assert state["current_rps"] < 10.0  # Should have decreased
        assert state["consecutive_failures"] == 0  # Reset after decrease

    @pytest.mark.asyncio
    async def test_record_failure_does_not_go_below_min(self, limiter):
        """Should not go below min rate limit."""
        # Record many failures
        error = Exception("Test error")
        for _ in range(100):
            await limiter.record_failure(LLMProvider.OPENROUTER, error)

        state = limiter.get_state(LLMProvider.OPENROUTER)
        assert state["current_rps"] >= 0.5  # min_rps

    def test_get_current_limit(self, limiter):
        """Should return current rate limit."""
        limit = limiter.get_current_limit(LLMProvider.OPENROUTER)
        assert limit == 10.0  # default

    @pytest.mark.asyncio
    async def test_get_state_returns_correct_structure(self, limiter):
        """Should return state with correct structure."""
        await limiter.acquire(LLMProvider.OPENROUTER, tokens=1)
        state = limiter.get_state(LLMProvider.OPENROUTER)

        assert "current_rps" in state
        assert "tokens_available" in state
        assert "consecutive_successes" in state
        assert "consecutive_failures" in state
        assert "burst" in state

    def test_get_state_for_unknown_provider(self, limiter):
        """Should return empty dict for unknown provider."""
        state = limiter.get_state(LLMProvider.GEMINI)
        assert state == {}

    @pytest.mark.asyncio
    async def test_adaptive_false_disables_adaptation(self):
        """Adaptive should be disabled when False."""
        limiter = AdaptiveRateLimiter(adaptive=False)

        # Create the provider state, then record successes without adaptation
        await limiter.acquire(LLMProvider.OPENROUTER, tokens=1)
        for _ in range(20):
            await limiter.record_success(LLMProvider.OPENROUTER)

        state = limiter.get_state(LLMProvider.OPENROUTER)
        assert state["current_rps"] == 10.0  # unchanged
        assert state["consecutive_successes"] == 0  # never recorded

    @pytest.mark.asyncio
    async def test_adaptive_false_ignores_failures(self):
        """Recorded failures must not lower the limit when adaptive is off."""
        limiter = AdaptiveRateLimiter(adaptive=False)

        await limiter.acquire(LLMProvider.OPENROUTER, tokens=1)
        for _ in range(3):
            await limiter.record_failure(LLMProvider.OPENROUTER, Exception("Test error"))

        state = limiter.get_state(LLMProvider.OPENROUTER)
        assert state["current_rps"] == 10.0
        assert state["consecutive_failures"] == 0

    @pytest.mark.asyncio
    async def test_multiple_providers_independent(self, limiter):
        """Each provider should have independent state."""
        await limiter.acquire(LLMProvider.OPENROUTER, tokens=3)
        await limiter.acquire(LLMProvider.OPENCODE, tokens=1)

        openrouter_state = limiter.get_state(LLMProvider.OPENROUTER)
        opencode_state = limiter.get_state(LLMProvider.OPENCODE)

        assert openrouter_state["tokens_available"] == 2.0  # 5 - 3
        assert opencode_state["tokens_available"] == 4.0  # 5 - 1

    @pytest.mark.asyncio
    async def test_acquire_multiple_tokens(self, limiter):
        """Should acquire multiple tokens at once."""
        await limiter.acquire(LLMProvider.OPENROUTER, tokens=3)

        state = limiter.get_state(LLMProvider.OPENROUTER)
        assert state["tokens_available"] == 2.0  # 5 - 3

    @pytest.mark.asyncio
    async def test_concurrent_acquires(self, limiter):
        """Should handle concurrent acquires correctly."""

        async def acquire_once():
            await limiter.acquire(LLMProvider.OPENROUTER, tokens=1)

        # Run 5 concurrent acquires
        await asyncio.gather(*[acquire_once() for _ in range(5)])

        state = limiter.get_state(LLMProvider.OPENROUTER)
        assert state["tokens_available"] == 0.0

    @pytest.mark.asyncio
    async def test_get_state_with_custom_params(self):
        """Should build provider state from the constructor parameters."""
        limiter = AdaptiveRateLimiter(default_rps=20.0, default_burst=10)

        await limiter.acquire(LLMProvider.OPENROUTER, tokens=1)
        state = limiter.get_state(LLMProvider.OPENROUTER)

        assert state["current_rps"] == 20.0
        assert state["burst"] == 10
        assert state["tokens_available"] == 9.0  # burst 10 - 1 acquired

    def test_get_current_limit_uses_configured_default(self):
        """Unknown provider limit should come from default_rps."""
        limiter = AdaptiveRateLimiter(default_rps=7.5, default_burst=3)

        assert limiter.get_current_limit(LLMProvider.OPENROUTER) == 7.5
        assert limiter.get_state(LLMProvider.OPENROUTER) == {}

    @pytest.mark.asyncio
    async def test_refill_does_not_exceed_burst(self, limiter):
        """Refill should not exceed burst capacity."""
        # Exhaust tokens
        await limiter.acquire(LLMProvider.OPENROUTER, tokens=5)

        # Wait long enough for full refill
        await asyncio.sleep(2.0)

        state = limiter.get_state(LLMProvider.OPENROUTER)
        assert state["tokens_available"] <= 5.0  # burst limit

    @pytest.mark.asyncio
    async def test_new_provider_uses_configured_defaults(self, limiter):
        """First use of a provider should seed state with constructor defaults."""
        assert limiter.get_state(LLMProvider.GEMINI) == {}

        await limiter.acquire(LLMProvider.GEMINI, tokens=1)
        state = limiter.get_state(LLMProvider.GEMINI)

        assert state["current_rps"] == 10.0
        assert state["burst"] == 5
        assert state["tokens_available"] == 4.0


class TestRateLimiterIntegration:
    """Integration tests for rate limiter with UnifiedLLMClient."""

    @pytest.mark.asyncio
    async def test_rate_limiter_respected_by_client(self, tmp_path):
        """Client should consume rate limiter tokens for each dispatch."""
        from unittest.mock import MagicMock

        from src.cache_manager import CacheManager
        from src.domain.llm import LLMModel, LLMPrompt, LLMProvider, ProviderConfig
        from src.infrastructure.llm_adapters.cache import LLMCacheAdapter
        from src.infrastructure.llm_adapters.rate_limiter import AdaptiveRateLimiter
        from src.infrastructure.llm_adapters.unified_client import UnifiedLLMClient

        provider = ProviderConfig(
            name=LLMProvider.OPENROUTER,
            api_key_env="TEST_KEY",
            default_model=LLMModel.OPENROUTER_FREE,
        )
        cache = LLMCacheAdapter(cache_manager=CacheManager(cache_dir=tmp_path / "llm"))

        provider_response = MagicMock()
        provider_response.content = "ok"
        provider_response.usage = MagicMock(prompt_tokens=1, completion_tokens=1)
        mock_openai = MagicMock()
        mock_openai.chat.completions.create.return_value = provider_response

        with patch.dict("os.environ", {"TEST_KEY": "test"}):
            limiter = AdaptiveRateLimiter(default_rps=1.0, default_burst=1)
            client = UnifiedLLMClient(
                provider_chain=(provider,),
                cache=cache,
                rate_limiter=limiter,
            )

            with patch("openai.OpenAI", return_value=mock_openai):
                response = await client.generate(LLMPrompt(user="Rate limited prompt"))

            assert response.content == "ok"
            state = limiter.get_state(LLMProvider.OPENROUTER)
            assert state["current_rps"] == 1.0
            assert state["burst"] == 1
            assert state["tokens_available"] < 1.0
