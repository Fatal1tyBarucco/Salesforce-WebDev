"""Tests for src/circuit_breaker.py — 100% coverage target."""

from src.circuit_breaker import CircuitBreaker


class TestCircuitBreaker:
    """CircuitBreaker state machine: CLOSED → OPEN → HALF-OPEN."""

    def test_initial_state_closed(self) -> None:
        cb = CircuitBreaker(threshold=3, cooldown=60)
        assert cb._failures == 0
        assert cb._opened_at == 0.0

    def test_record_failure_increments(self) -> None:
        cb = CircuitBreaker(threshold=3, cooldown=60)
        cb.record_failure()
        cb.record_failure()
        assert cb._failures == 2

    def test_reset_clears_state(self) -> None:
        cb = CircuitBreaker(threshold=3, cooldown=60)
        cb.record_failure()
        cb.record_failure()
        cb.reset()
        assert cb._failures == 0
        assert cb._opened_at == 0.0

    def test_repr_closed(self) -> None:
        cb = CircuitBreaker(threshold=3, cooldown=60)
        r = repr(cb)
        assert "CLOSED" in r
        assert "failures=0" in r

    def test_repr_open(self) -> None:
        cb = CircuitBreaker(threshold=1, cooldown=60)
        cb.record_failure()
        r = repr(cb)
        assert "OPEN" in r

    def test_reset_after_failures(self) -> None:
        cb = CircuitBreaker(threshold=3, cooldown=60)
        cb.record_failure()
        cb.record_failure()
        assert cb._failures == 2
        cb.reset()
        assert cb._failures == 0
        assert cb._opened_at == 0.0

    def test_repr_when_closed_shows_zero_failures(self) -> None:
        cb = CircuitBreaker(threshold=3, cooldown=60)
        r = repr(cb)
        assert "CLOSED" in r
        assert "failures=0" in r
