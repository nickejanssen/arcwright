"""Telemetry payloads and event recorders for accusation scoring."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Event
from engine.scoring.models import AccusationAttempt


def build_accusation_submitted_payload(
    attempt: AccusationAttempt,
) -> dict[str, Any]:
    """Build telemetry for one attempt without copying private theory state."""
    return {
        "accusation_id": attempt.accusation_id,
        "participant_id": attempt.accuser_participant_id,
        "beat_id": attempt.beat_id,
        "accused_cast_member_id": attempt.accused_cast_member_id,
        "outcome": attempt.outcome.value,
        "catches_banked_at_submission": attempt.catches_banked_at_submission,
        "points_awarded": attempt.points_awarded,
        "motive_correct": attempt.motive_correct,
        "method_correct": attempt.method_correct,
        "repeat_offense_count": attempt.repeat_offense_count,
        "used_last_word": attempt.used_last_word,
        "triggered_last_call": attempt.triggered_last_call,
    }


def build_last_call_triggered_payload(
    attempt: AccusationAttempt,
) -> dict[str, Any]:
    return {
        "accusation_id": attempt.accusation_id,
        "participant_id": attempt.accuser_participant_id,
        "beat_id": attempt.beat_id,
    }


async def record_accusation_submitted(
    db: AsyncSession,
    session_id: UUID,
    attempt: AccusationAttempt,
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="accusation_submitted",
            payload=build_accusation_submitted_payload(attempt),
        )
    )
    await db.flush()


async def record_last_call_triggered(
    db: AsyncSession,
    session_id: UUID,
    attempt: AccusationAttempt,
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="last_call_triggered",
            payload=build_last_call_triggered_payload(attempt),
        )
    )
    await db.flush()
