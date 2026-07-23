"""Tests for the async event bus (src.events)."""

from __future__ import annotations

import pytest

from src.events import Event, EventBus, get_event_bus


@pytest.fixture
def bus() -> EventBus:
    return EventBus()


# ---------------------------------------------------------------------------
# Event dataclass
# ---------------------------------------------------------------------------


def test_event_immutable() -> None:
    event = Event(name="test", data={"key": "value"}, source="src")
    assert event.name == "test"
    assert event.data == {"key": "value"}
    assert event.source == "src"


def test_event_repr() -> None:
    event = Event(name="test.event")
    assert "test.event" in repr(event)


# ---------------------------------------------------------------------------
# EventBus subscribe / unsubscribe
# ---------------------------------------------------------------------------


def test_subscribe_decorator(bus: EventBus) -> None:
    @bus.on("test.event")
    async def handler(event: Event) -> None:
        pass

    assert bus.handler_count("test.event") == 1


def test_subscribe_programmatic(bus: EventBus) -> None:
    async def handler(event: Event) -> None:
        pass

    bus.subscribe("test.event", handler)
    assert bus.handler_count("test.event") == 1


def test_unsubscribe(bus: EventBus) -> None:
    async def handler(event: Event) -> None:
        pass

    bus.subscribe("test.event", handler)
    assert bus.handler_count("test.event") == 1

    bus.unsubscribe("test.event", handler)
    assert bus.handler_count("test.event") == 0


def test_unsubscribe_nonexistent(bus: EventBus) -> None:
    async def handler(event: Event) -> None:
        pass

    # Should not raise
    bus.unsubscribe("no.such.event", handler)


def test_handler_count_all(bus: EventBus) -> None:
    @bus.on("event.a")
    async def handler_a(event: Event) -> None:
        pass

    @bus.on("event.b")
    async def handler_b(event: Event) -> None:
        pass

    assert bus.handler_count() == 2
    assert bus.handler_count("event.a") == 1


# ---------------------------------------------------------------------------
# EventBus emit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_emit_calls_handler(bus: EventBus) -> None:
    received: list[Event] = []

    @bus.on("test.event")
    async def handler(event: Event) -> None:
        received.append(event)

    count = await bus.emit("test.event", {"key": "value"}, source="test")

    assert count == 1
    assert len(received) == 1
    assert received[0].name == "test.event"
    assert received[0].data == {"key": "value"}
    assert received[0].source == "test"


@pytest.mark.asyncio
async def test_emit_no_handlers(bus: EventBus) -> None:
    count = await bus.emit("no.handlers")
    assert count == 0


@pytest.mark.asyncio
async def test_emit_multiple_handlers(bus: EventBus) -> None:
    calls: list[str] = []

    @bus.on("multi")
    async def handler_a(event: Event) -> None:
        calls.append("a")

    @bus.on("multi")
    async def handler_b(event: Event) -> None:
        calls.append("b")

    count = await bus.emit("multi")

    assert count == 2
    assert calls == ["a", "b"]


@pytest.mark.asyncio
async def test_emit_handler_error_isolated(bus: EventBus) -> None:
    calls: list[str] = []

    @bus.on("err.event")
    async def bad_handler(event: Event) -> None:
        raise ValueError("boom")

    @bus.on("err.event")
    async def good_handler(event: Event) -> None:
        calls.append("ok")

    count = await bus.emit("err.event")

    # good_handler still runs despite bad_handler raising
    assert count == 1
    assert calls == ["ok"]
    assert len(bus.last_errors) == 1


@pytest.mark.asyncio
async def test_clear_errors(bus: EventBus) -> None:
    @bus.on("err")
    async def handler(event: Event) -> None:
        raise RuntimeError("fail")

    await bus.emit("err")
    assert len(bus.last_errors) == 1

    bus.clear_errors()
    assert len(bus.last_errors) == 0


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------


def test_get_event_bus_singleton() -> None:
    bus1 = get_event_bus()
    bus2 = get_event_bus()
    assert bus1 is bus2


def test_bus_repr(bus: EventBus) -> None:
    assert "EventBus" in repr(bus)
