"""The host seat (AW-331, spec 0095 Q1 and M6, D-133).

One seated human player holds the host role: the first to join. It is kept as
saved rows (``host_seat`` events, newest counter wins), never in memory, so a
cold process and a reconnecting phone see the same answer. It is checked on every
call and can be handed to another seated human. An AI seat, and the slot the
session's creator holds, are never the host seat.

Who may call a route is decided from this saved rule, not from the sign-in's
claims: no token is reissued when the role moves.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Event, SessionParticipant
from engine.events.models import AudienceTarget, EventCategory
from engine.session.phases import Publish, RoundError, content_event, emit, session_lock

HOST_SEAT_EVENT = "host_seat"
HOST_CHANGED_EVENT = "host_changed"


async def _latest(db: AsyncSession, session_id: UUID) -> dict[str, Any] | None:
    result = await db.execute(
        select(Event.payload).where(
            Event.session_id == session_id, Event.event_type == HOST_SEAT_EVENT
        )
    )
    payloads = list(result.scalars().all())
    if not payloads:
        return None
    latest: dict[str, Any] = max(payloads, key=lambda p: int(p["counter"]))
    return latest


async def current_host(db: AsyncSession, session_id: UUID) -> UUID | None:
    """The participant who holds the host seat, or None if nobody does yet."""
    latest = await _latest(db, session_id)
    return UUID(str(latest["participant_id"])) if latest is not None else None


async def is_host_seat(
    db: AsyncSession, session_id: UUID, participant_id: UUID | None
) -> bool:
    if participant_id is None:
        return False
    return await current_host(db, session_id) == participant_id


async def is_seated_player(
    db: AsyncSession, session_id: UUID, participant_id: UUID | None
) -> bool:
    """A human player seat of this session: not the creator's slot, not an AI."""
    if participant_id is None:
        return False
    result = await db.execute(
        select(SessionParticipant.participant_id).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.participant_id == participant_id,
            SessionParticipant.surface_type != "host",
            SessionParticipant.is_ai_controlled.is_(False),
        )
    )
    return result.scalar_one_or_none() is not None


async def _save(
    db: AsyncSession, session_id: UUID, participant_id: UUID, previous: int
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type=HOST_SEAT_EVENT,
            payload={"counter": previous + 1, "participant_id": str(participant_id)},
        )
    )
    await db.flush()


async def assign_first(
    db: AsyncSession, session_id: UUID, participant_id: UUID
) -> bool:
    """Make ``participant_id`` the host seat if nobody holds it. Call it under
    the session lock, as ``lobby_join`` does, so two joins at once get one host.
    Returns whether it was assigned."""
    if await _latest(db, session_id) is not None:
        return False
    if not await is_seated_player(db, session_id, participant_id):
        return False
    await _save(db, session_id, participant_id, 0)
    return True


async def hand_over(
    db: AsyncSession,
    session_id: UUID,
    to_participant_id: UUID,
    now: datetime,
    publish: Publish = None,
) -> UUID:
    """Give the host seat to another seated human player. The old host loses
    host controls at once. Tells the room who the host is now (no private
    content). Hold ``phases.delivery_lock`` and pass an ``Outbox`` when the
    caller commits afterwards."""
    async with session_lock(db, session_id) as orm:
        if orm is None:
            raise RoundError("session_not_found")
        latest = await _latest(db, session_id)
        if latest is not None and UUID(str(latest["participant_id"])) == (
            to_participant_id
        ):
            raise RoundError("already_host", "that player already hosts")
        if not await is_seated_player(db, session_id, to_participant_id):
            raise RoundError("not_a_participant", "that is not a seated player")
        await _save(
            db,
            session_id,
            to_participant_id,
            int(str(latest["counter"])) if latest is not None else 0,
        )
        name = await db.scalar(
            select(SessionParticipant.display_name).where(
                SessionParticipant.participant_id == to_participant_id
            )
        )
        await emit(
            publish,
            content_event(
                session_id,
                now,
                category=EventCategory.system,
                event_type=HOST_CHANGED_EVENT,
                audience=AudienceTarget.all,
                payload={
                    "participant_id": str(to_participant_id),
                    "display_name": name,
                },
            ),
        )
        return to_participant_id
