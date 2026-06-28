"""SSE event-stream endpoint.

Architecture: docs/architecture/08-event-system.md S8.6.
Route handlers are thin: validate input, call engine functions, return responses.
No arc execution logic here.

Auth: Firebase ID token (Authorization: Bearer <token>). Identity and role are
extracted from JWT claims (arcwright_player_id, arcwright_role); query-param
trust is removed as of AW-217.
"""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sse_starlette.sse import EventSourceResponse

from api.auth import JwtClaims, optional_player_or_host_jwt
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
    claims: JwtClaims | None = Depends(optional_player_or_host_jwt),
) -> EventSourceResponse:
    """Stream ContentEvents for ``session_id`` as Server-Sent Events.

    Authenticated players and hosts receive their role-filtered view. A missing
    Authorization header is treated as a display surface connection (no private
    events). Production auth enforcement is deferred to M5 (AW-269).
    """
    if claims is not None:
        if claims.session_id is not None and claims.session_id != session_id:
            raise HTTPException(
                status_code=403,
                detail="Token session_id does not match requested session",
            )
        if claims.role in ("player", "host") and claims.player_id is None:
            raise HTTPException(
                status_code=400,
                detail="Player/host tokens must include arcwright_player_id claim",
            )

    bus, registry = _get_or_create_session_state(session_id)

    async def generator() -> AsyncGenerator[dict[str, str], None]:
        if claims is None:
            conn = registry.register_display()
        elif claims.role == "player":
            assert claims.player_id is not None  # validated above
            conn = registry.register_player(claims.player_id)
        elif claims.role == "host":
            assert claims.player_id is not None  # validated above
            conn = registry.register_host(claims.player_id)
        else:
            conn = registry.register_display()

        try:
            # Capture cutoff and replay atomically (no await between these
            # calls — asyncio cannot switch to the fanout task mid-block).
            cutoff = bus.last_sequence_number
            missed = bus.replay_since(since)

            # Filter replay through registry.route() — same privacy guarantee
            # as the live fanout path.
            for event in missed:
                if conn in registry.route(event):
                    yield {"data": event.model_dump_json()}

            async for event in conn:
                if event.sequence_number > cutoff:
                    yield {"data": event.model_dump_json()}
        finally:
            registry.deregister(conn)

    return EventSourceResponse(generator(), ping=20)
