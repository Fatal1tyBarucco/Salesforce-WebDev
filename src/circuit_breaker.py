"""Unified Circuit Breaker pattern for external service calls.

Provides a reusable circuit breaker that tracks failures and enters an
open state (cooldown) after a configurable threshold is exceeded.

Usage::

    from src.circuit_breaker import CircuitBreaker

    breaker = CircuitBreaker(threshold=3, cooldown=60.0)

    if breaker.is_open:
        raise ServiceUnavailable("Circuit breaker open")

    try:
        result = await call_external_service()
        breaker.record_success()
        return result
    except Exception:
        breaker.record_failure()
        raise
"""

from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)

# Defaults
DEFAULT_THRESHOLD: int = 3
DEFAULT_COOLDOWN: float = 60.0


class CircuitBreaker:
    """Circuit breaker with configurable failure threshold and cooldown period.

    States:
        CLOSED  — normal operation, requests pass through.
        OPEN    — too many failures, requests are rejected for *cooldown* seconds.
        HALF-OPEN — cooldown expired, next request is a probe (automatic).

    Args:
        threshold: Number of consecutive failures before opening the circuit.
        cooldown: Seconds to keep the circuit open before allowing a probe.
    """

    def __init__(
        self,
        threshold: int = DEFAULT_THRESHOLD,
        cooldown: float = DEFAULT_COOLDOWN,
    ) -> None:
        self._threshold = threshold
        self._cooldown = cooldown
        self._failures: int = 0
        self._opened_at: float = 0.0

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (requests should be rejected).

        Returns:
            ``True`` when the circuit is open and cooldown has not expired.
            ``False`` when the circuit is closed (normal operation) or when
            the cooldown has expired (half-open, allowing a probe).
        """
        if self._failures < self._threshold:
            return False
        elapsed = time.monotonic() - self._opened_at
        if elapsed > self._cooldown:
            self._failures = 0
            return False
        return True

    @property
    def failure_count(self) -> int:
        """Return the current consecutive failure count."""
        return self._failures

    def record_success(self) -> None:
        """Record a successful call, resetting the failure counter."""
        self._failures = 0
        self._opened_at = 0.0

    def record_failure(self) -> None:
        """Record a failed call, potentially tripping the circuit."""
        self._failures += 1
        if self._failures >= self._threshold:
            now = time.monotonic()
            if self._opened_at == 0.0 or (now - self._opened_at) > self._cooldown:
                self._opened_at = now
                logger.warning(
                    "Circuit breaker tripped after %d failures, cooling down for %.0fs",
                    self._failures,
                    self._cooldown,
                )

    def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        self._failures = 0
        self._opened_at = 0.0

    def __repr__(self) -> str:
        state = "OPEN" if self.is_open else "CLOSED"
        return (
            f"CircuitBreaker(state={state}, failures={self._failures}, threshold={self._threshold})"
        )
