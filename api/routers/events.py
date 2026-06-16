"""SSE event-stream endpoint.

Architecture: docs/architecture/08-event-system.md S8.6.
Route handlers are thin: validate input, call engine functions, return responses.
No arc execution logic here.

Auth: JWT auth on SSE connections is M3-B scope. For MVP this endpoint accepts
connection_type and player_id as query parameters.
"""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sse_starlette.sse import EventSourceResponse

from engine.events.bus import SessionEventBus
from engine.events.fanout import SessionConnectionRegistry, run_fanout

router = APIRouter(prefix="/sessions", tags=["events"])

# In-process session state — single-process MVP.
# H2 upgrade: replace with a distributed store keyed on session_id.
_buses: dict[UUID, SessionEventBus] = {}
_registries: dict[UUID, SessionConnectionRegistry] = {}
_fanout_tasks: dict[UUID, asyncio.Task] = {}  # type: ignore[type-arg]


def _get_or_create_session_state(
    session_id: UUID,
) -> tuple[SessionEventBus, SessionConnectionRegistry]:
    """Return (bus, registry) for ``session_id``, creating them on first access.

    This function is synchronous and contains no await, so it is atomic under
    asyncio's cooperative scheduling — no risk of double-initialisation from
    concurrent requests.
    """
    if session_id not in _buses:
        bus = SessionEventBus()
        registry = SessionConnectionRegistry()
        _buses[session_id] = bus
        _registries[session_id] = registry
        _fanout_tasks[session_id] = asyncio.create_task(
            run_fanout(bus, registry), name=f"fanout-{session_id}"
        )
    return _buses[session_id], _registries[session_id]


@router.get("/{session_id}/events")
async def session_events_stream(
    session_id: UUID,
    since: int = Query(
        default=0, ge=0, description="Last seen sequence number; 0 for full replay."
    ),
    player_id: UUID | None = Query(
        default=None,
        description="Participant UUID (required for player/host connections).",
    ),
    connection_type: Literal["player", "host", "display"] = Query(
        default="player",
        description="Connection audience type.",
    ),
) -> EventSourceResponse:
    """Stream ContentEvents for ``session_id`` as Server-Sent Events.

    On connect, missed events (sequence_number > ``since``) are replayed first.
    Live events follow with no duplication — the replay cutoff is captured
    atomically before any await so replay and live ranges are always disjoint.
    """
    if connection_type in ("player", "host") and player_id is None:
        raise HTTPException(
            status_code=400,
            detail="player_id is required for player and host connections",
        )

    bus, registry = _get_or_create_session_state(session_id)

    async def generator() -> AsyncGenerator[dict[str, str], None]:
        if connection_type == "player":
            assert player_id is not None  # validated above
            conn = registry.register_player(player_id)
        elif connection_type == "host":
            assert player_id is not None  # validated above
            conn = registry.register_host(player_id)
        else:
            conn = registry.register_display()

        try:
            # Capture cutoff and replay atomically (no await between these
            # calls — asyncio cannot switch to the fanout task mid-block).
            cutoff = bus.last_sequence_number
            missed = bus.replay_since(since)

            # Filter replay through registry.route() — same privacy guarantee
            # as the live fanout path. Without this, a player reconnecting
            # with an old sequence number would receive specific_player or
            # host_only events from the history buffer that route() would
            # have excluded from this connection.
            for event in missed:
                if conn in registry.route(event):
                    yield {"data": event.model_dump_json()}

            async for event in conn:
                if event.sequence_number > cutoff:
                    yield {"data": event.model_dump_json()}
        finally:
            registry.deregister(conn)

    return EventSourceResponse(generator(), ping=20)
