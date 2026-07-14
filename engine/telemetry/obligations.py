"""Obligation lifecycle telemetry (spec 0065, architecture 11.8).

Two events, both written to the ``events`` table like every other
telemetry signal:

- ``obligation_created``: authored setup registration or pacing
  misdirection injection.
- ``obligation_resolved``: a deterministic resolution trigger fired.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Event, Obligation


def build_obligation_created_payload(obligation: Obligation) -> dict[str, Any]:
    return {
        "obligation_id": str(obligation.obligation_id),
        "source_type": obligation.source_type,
        "mandatory": obligation.mandatory,
        "beat_id": obligation.created_beat,
    }


def build_obligation_resolved_payload(
    obligation: Obligation, *, open_duration_seconds: float
) -> dict[str, Any]:
    return {
        "obligation_id": str(obligation.obligation_id),
        "resolution_beat": obligation.resolved_beat,
        "open_duration_seconds": open_duration_seconds,
    }


async def record_obligation_created(
    db: AsyncSession, session_id: UUID, obligation: Obligation
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="obligation_created",
            payload=build_obligation_created_payload(obligation),
        )
    )
    await db.flush()


async def record_obligation_resolved(
    db: AsyncSession,
    session_id: UUID,
    obligation: Obligation,
    *,
    open_duration_seconds: float,
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="obligation_resolved",
            payload=build_obligation_resolved_payload(
                obligation, open_duration_seconds=open_duration_seconds
            ),
        )
    )
    await db.flush()
