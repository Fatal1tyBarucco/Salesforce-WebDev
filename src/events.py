"""Lightweight async event bus for pipeline decoupling.

Provides a publish/subscribe mechanism so that pipeline stages can
communicate without direct imports or function calls.

Usage::

    from src.events import EventBus, Event

    bus = EventBus()

    # Subscribe
    @bus.on("release.processed")
    async def handle_release(event: Event) -> None:
        print(f"Release processed: {event.data['slug']}")

    # Emit
    await bus.emit("release.processed", {"slug": "summer_26"})

Built-in events:
    - ``release.detected``   — new release candidate found
    - ``release.processed``  — release files generated
    - ``release.classified`` — feature classification complete
    - ``pipeline.started``   — pipeline execution began
    - ``pipeline.completed`` — pipeline finished successfully
    - ``pipeline.error``     — pipeline encountered an error
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)

# Type alias for event handlers
EventHandler = Callable[["Event"], Coroutine[Any, Any, None]]


@dataclass(frozen=True)
class Event:
    """An immutable event dispatched through the bus.

    Attributes:
        name: Event identifier (e.g. ``"release.processed"``).
        data: Arbitrary payload associated with the event.
        source: Optional identifier of the emitter.
    """

    name: str
    data: dict[str, Any] = field(default_factory=dict)
    source: str = ""

    def __repr__(self) -> str:
        return f"Event(name={self.name!r}, source={self.source!r})"


class EventBus:
    """Async publish/subscribe event bus.

    Handlers are invoked in registration order.  A handler that raises
    an exception does *not* prevent subsequent handlers from running;
    the exception is logged and collected in ``last_errors``.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._last_errors: list[tuple[str, Exception]] = []

    def on(self, event_name: str) -> Callable[[EventHandler], EventHandler]:
        """Decorator to register a handler for an event.

        Args:
            event_name: The event to listen for.

        Returns:
            Decorator that registers the handler and returns it unchanged.
        """

        def decorator(func: EventHandler) -> EventHandler:
            self._handlers[event_name].append(func)
            return func

        return decorator

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Register a handler programmatically.

        Args:
            event_name: The event to listen for.
            handler: Async callable that accepts an Event.
        """
        self._handlers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        """Remove a previously registered handler.

        Args:
            event_name: The event the handler was registered for.
            handler: The handler to remove.
        """
        try:
            self._handlers[event_name].remove(handler)
        except ValueError:
            pass

    async def emit(self, event_name: str, data: dict[str, Any] | None = None, source: str = "") -> int:
        """Dispatch an event to all registered handlers.

        Args:
            event_name: Event identifier.
            data: Optional payload dict.
            source: Optional emitter identifier.

        Returns:
            Number of handlers that were invoked.
        """
        event = Event(name=event_name, data=data or {}, source=source)
        handlers = self._handlers.get(event_name, [])

        if not handlers:
            logger.debug("[EVENT] No handlers for '%s'", event_name)
            return 0

        invoked = 0
        for handler in handlers:
            try:
                await handler(event)
                invoked += 1
            except Exception as exc:
                logger.error(
                    "[EVENT] Handler %s for '%s' failed: %s",
                    handler.__name__,
                    event_name,
                    exc,
                )
                self._last_errors.append((event_name, exc))

        logger.debug("[EVENT] '%s' dispatched to %d handler(s)", event_name, invoked)
        return invoked

    @property
    def last_errors(self) -> list[tuple[str, Exception]]:
        """Return errors from the most recent emit cycle."""
        return list(self._last_errors)

    def clear_errors(self) -> None:
        """Clear collected errors."""
        self._last_errors.clear()

    def handler_count(self, event_name: str | None = None) -> int:
        """Return the number of registered handlers.

        Args:
            event_name: If given, count handlers for that event only.
                        Otherwise, count all handlers across all events.
        """
        if event_name is not None:
            return len(self._handlers.get(event_name, []))
        return sum(len(h) for h in self._handlers.values())

    def __repr__(self) -> str:
        total = self.handler_count()
        events = len(self._handlers)
        return f"EventBus(events={events}, handlers={total})"


# ---------------------------------------------------------------------------
# Module-level singleton for convenience
# ---------------------------------------------------------------------------
_default_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Return the module-level default event bus, creating it if needed."""
    global _default_bus
    if _default_bus is None:
        _default_bus = EventBus()
    return _default_bus
