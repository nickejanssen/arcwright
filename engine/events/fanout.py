"""SSE connection abstraction, per-session connection registry, and fan-out router.

Architecture: docs/architecture/08-event-system.md S8.4-S8.6.
Routing dispatches on EventCategory (closed platform enum); never on event_type.
ADR-0008: docs/decisions/0008-content-event-type-layering.md.
"""

from __future__ import annotations

import asyncio
from uuid import UUID

from engine.events.bus import SessionEventBus
from engine.events.models import AudienceTarget, ContentEvent


class _ConnectionClosed:
    """Sentinel placed in an SSEConnection queue when close() is called."""


class SSEConnection:
    """A single SSE client connection backed by a private asyncio queue.

    The fan-out router calls send() to enqueue events; the SSE endpoint reads
    them via async iteration. close() enqueues a sentinel so the iteration ends
    gracefully (used in tests and for server-initiated disconnects).
    """

    def __init__(self, player_id: UUID | None = None) -> None:
        self.player_id = player_id
        self._queue: asyncio.Queue[ContentEvent | _ConnectionClosed] = asyncio.Queue()
        self._closed = False

    def send(self, event: ContentEvent) -> None:
        if not self._closed:
            self._queue.put_nowait(event)

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            self._queue.put_nowait(_ConnectionClosed())

    def __aiter__(self) -> "SSEConnection":
        return self

    async def __anext__(self) -> ContentEvent:
        item = await self._queue.get()
        if isinstance(item, _ConnectionClosed):
            raise StopAsyncIteration
        return item


class SessionConnectionRegistry:
    """Per-session registry of live SSE connections by audience type.

    route() is the structural privacy enforcer documented in S8.4: no code path
    delivers a specific_player event to the wrong participant.
    """

    def __init__(self) -> None:
        self._player_connections: dict[UUID, list[SSEConnection]] = {}
        self._display_connections: list[SSEConnection] = []
        self._host_connections: list[SSEConnection] = []

    def register_player(self, player_id: UUID) -> SSEConnection:
        conn = SSEConnection(player_id=player_id)
        self._player_connections.setdefault(player_id, []).append(conn)
        return conn

    def register_host(self, host_id: UUID) -> SSEConnection:
        conn = SSEConnection(player_id=host_id)
        self._host_connections.append(conn)
        return conn

    def register_display(self) -> SSEConnection:
        conn = SSEConnection()
        self._display_connections.append(conn)
        return conn

    def deregister(self, conn: SSEConnection) -> None:
        if conn.player_id is not None:
            bucket = self._player_connections.get(conn.player_id, [])
            try:
                bucket.remove(conn)
            except ValueError:
                pass
            if not bucket:
                self._player_connections.pop(conn.player_id, None)
            try:
                self._host_connections.remove(conn)
            except ValueError:
                pass
        try:
            self._display_connections.remove(conn)
        except ValueError:
            pass

    def all_player_connections(self) -> list[SSEConnection]:
        return [c for conns in self._player_connections.values() for c in conns]

    def route(self, event: ContentEvent) -> list[SSEConnection]:
        """Resolve target_audience to the concrete connections that should receive event.

        Dispatches on category-derived audience target, never on event_type (ADR-0008).
        AudienceTarget.ALL excludes host connections; hosts receive events via HOST_ONLY.
        """
        match event.target_audience:
            case AudienceTarget.all:
                return self.all_player_connections() + list(self._display_connections)
            case AudienceTarget.specific_player:
                return list(self._player_connections.get(event.target_player_id, []))  # type: ignore[arg-type]
            case AudienceTarget.host_only:
                return list(self._host_connections)
            case AudienceTarget.shared_display:
                return list(self._display_connections)


async def run_fanout(bus: SessionEventBus, registry: SessionConnectionRegistry) -> None:
    """Subscribe to ``bus`` and dispatch each event to the connections resolved by
    ``registry.route``. Intended to run as a long-lived background asyncio task.
    Cancelled cleanly when the session ends."""
    async with bus.subscribe() as sub:
        async for event in sub:
            for conn in registry.route(event):
                conn.send(event)
