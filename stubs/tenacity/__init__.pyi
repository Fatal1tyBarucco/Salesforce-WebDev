"""Type stubs for tenacity (retry library).

Covers the subset of tenacity APIs used in this project:
  - retry (decorator)
  - stop_after_attempt
  - wait_exponential
  - retry_if_exception_type
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

_F = TypeVar("_F", bound=Callable[..., Any])

class retry_base:
    """Base class for retry predicates."""

    def __and__(self, other: retry_base) -> retry_all: ...
    def __or__(self, other: retry_base) -> retry_any: ...
    def __call__(self, retry_state: RetryState) -> bool: ...

class retry_all(retry_base):
    """Logical AND of retry predicates."""

    def __init__(self, *predicates: retry_base) -> None: ...

class retry_any(retry_base):
    """Logical OR of retry predicates."""

    def __init__(self, *predicates: retry_base) -> None: ...

class stop_base:
    """Base class for stop strategies."""

    def __call__(self, retry_state: RetryState) -> bool: ...

class wait_base:
    """Base class for wait strategies."""

    def __call__(self, retry_state: RetryState) -> float: ...

class RetryState:
    """State passed to retry callbacks."""

    attempt_number: int
    outcome: Any
    next_action: Any
    kwargs: dict[str, Any]
    args: tuple[Any, ...]

class retry_if_exception_type(retry_base):
    """Retry only if the exception is an instance of the given type(s)."""

    def __init__(
        self, exception_types: type[BaseException] | tuple[type[BaseException], ...] = ...
    ) -> None: ...

class stop_after_attempt(stop_base):
    """Stop after a fixed number of attempts."""

    def __init__(self, max_attempt_number: int) -> None: ...

class wait_exponential(wait_base):
    """Wait with exponential backoff between retries."""

    def __init__(
        self,
        multiplier: float | int = 1,
        min: float | int = 0,
        max: float | int = 120,
        exp_base: float | int = 2,
    ) -> None: ...

def retry(
    retry: retry_base = ...,
    stop: stop_base = ...,
    wait: wait_base = ...,
    reraise: bool = ...,
) -> Callable[[_F], _F]:
    """Decorator that retries a function on failure."""
    ...
