"""In-memory per-session ContentEvent bus.

Architecture: docs/architecture/08-event-system.md S8.3.
This module is transport-agnostic: it owns publish, multi-subscriber fan-out,
monotonic sequence assignment, and a bounded in-session history for reconnect
replay. SSE wire concerns live in AW-216 and beyond.
"""

from __future__ import annotations

import asyncio
from collections import deque
from types import TracebackType
from typing import AsyncIterator, Optional

from engine.events.models import ContentEvent

DEFAULT_HISTORY_CAP = 1000


class SessionEventBus:
    """A per-session async pub/sub bus.

    Each call to ``subscribe`` returns an independent async iterator that
    receives every event published after the subscription. Past events are not
    delivered through the live channel; consumers must call ``replay_since`` to
    receive missed events when reconnecting.
    """

    def __init__(self, history_cap: int = DEFAULT_HISTORY_CAP) -> None:
        if history_cap < 1:
            raise ValueError("history_cap must be at least 1")
        self._history_cap = history_cap
        self._history: deque[ContentEvent] = deque(maxlen=history_cap)
        self._subscribers: list[asyncio.Queue[ContentEvent]] = []
        self._next_sequence_number = 1
        self._lock = asyncio.Lock()

    @property
    def history_cap(self) -> int:
        return self._history_cap

    @property
    def last_sequence_number(self) -> int:
        return self._next_sequence_number - 1

    async def publish(self, event: ContentEvent) -> ContentEvent:
        """Stamp ``event`` with the next sequence number, retain it, and fan
        it out to all current subscribers. Returns the stamped event."""
        async with self._lock:
            event.sequence_number = self._next_sequence_number
            self._next_sequence_number += 1
            self._history.append(event)
            for queue in list(self._subscribers):
                queue.put_nowait(event)
        return event

    def subscribe(self) -> "Subscription":
        """Register a new live subscriber.

        The subscription starts receiving events published after this method
        returns. Consumers that need past events or a reconnect gap must use
        ``replay_since`` explicitly.
        """
        queue: asyncio.Queue[ContentEvent] = asyncio.Queue()
        self._subscribers.append(queue)
        return Subscription(self, queue)

    def unsubscribe(self, queue: asyncio.Queue[ContentEvent]) -> None:
        try:
            self._subscribers.remove(queue)
        except ValueError:
            return

    def replay_since(self, sequence_number: int) -> list[ContentEvent]:
        """Return retained events with sequence_number strictly greater than
        ``sequence_number``, in publish order. Events older than the history
        buffer's window will not be present."""
        return [
            event for event in self._history if event.sequence_number > sequence_number
        ]


class Subscription:
    """An async iterator wrapper around a per-subscriber queue.

    Use as ``async with bus.subscribe() as sub: async for event in sub: ...``
    to guarantee unsubscribe on exit. Direct ``aclose()`` is also supported.
    """

    def __init__(
        self, bus: SessionEventBus, queue: asyncio.Queue[ContentEvent]
    ) -> None:
        self._bus = bus
        self._queue: Optional[asyncio.Queue[ContentEvent]] = queue

    def __aiter__(self) -> AsyncIterator[ContentEvent]:
        return self

    async def __anext__(self) -> ContentEvent:
        if self._queue is None:
            raise StopAsyncIteration
        return await self._queue.get()

    async def __aenter__(self) -> "Subscription":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._queue is not None:
            self._bus.unsubscribe(self._queue)
            self._queue = None
