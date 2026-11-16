"""Put a written case into a session at session start (spec 0093, Parts A, B).

Each cast character becomes a ``characters`` row, the same object a player's
character is, and its ``knows`` list is saved into the knowledge graph so any
generated line stays limited by what that character knows (principle 5).
Every non-host participant is given the opening concepts.

Nothing here needs a new table: which cast ID is which character is recorded
in one saved event, and holdings are knowledge-graph facts.
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.case.authored import AuthoredCase, AuthoredCaseRefused, load_authored_case
from engine.db.orm import Character, Event, SessionParticipant
from engine.knowledge.holdings import grant_concept

CAST_SEATED_EVENT = "case_cast_seated"
_REPO_ROOT = Path(__file__).resolve().parents[2]


class CaseRefusedAtStartError(Exception):
    """The arc's case file was refused by the fairness check."""


def load_arc_case(arc: ArcDefinition) -> AuthoredCase | None:
    """Load and check the case the arc names, or None if it names none.

    The path is relative to the repository root, like ``config/arcs.json``.
    """
    if not arc.case_file:
        return None
    try:
        return load_authored_case(
            _REPO_ROOT / arc.case_file,
            beat_order=[beat.beat_id for beat in arc.beats],
        )
    except AuthoredCaseRefused as refused:
        msg = f"case refused: {refused.name}"
        raise CaseRefusedAtStartError(msg) from refused


async def seat_authored_case(
    db: AsyncSession, *, session_id: UUID, case: AuthoredCase
) -> dict[str, UUID]:
    """Create the cast characters, save what they know, give every participant
    the opening. Safe to call twice: the second call changes nothing.

    Returns the cast ID to character ID map.
    """
    seated = await _existing_cast(db, session_id)
    if seated is None:
        seated = {}
        for cast in case.cast:
            character = Character(
                behavior_profile={
                    "case_cast_id": cast.cast_id,
                    "display_name": cast.display_name,
                }
            )
            db.add(character)
            await db.flush()
            seated[cast.cast_id] = character.character_id
        db.add(
            Event(
                session_id=session_id,
                actor_char_id=None,
                event_type=CAST_SEATED_EVENT,
                payload={
                    "case_id": case.case_id,
                    "cast": {k: str(v) for k, v in seated.items()},
                },
            )
        )
        await db.flush()

    texts = {c.concept_id: c.text for c in case.concepts}
    for cast in case.cast:
        for concept_id in cast.knows:
            await grant_concept(
                db,
                session_id=session_id,
                character_id=seated[cast.cast_id],
                concept_id=concept_id,
                text=texts[concept_id],
            )

    result = await db.execute(
        select(SessionParticipant.character_id).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.surface_type != "host",
        )
    )
    for character_id in result.scalars().all():
        for concept_id in case.opening:
            await grant_concept(
                db,
                session_id=session_id,
                character_id=character_id,
                concept_id=concept_id,
                text=texts[concept_id],
            )
    return seated


async def _existing_cast(db: AsyncSession, session_id: UUID) -> dict[str, UUID] | None:
    result = await db.execute(
        select(Event.payload).where(
            Event.session_id == session_id,
            Event.event_type == CAST_SEATED_EVENT,
        )
    )
    payload = result.scalars().first()
    if payload is None:
        return None
    return {k: UUID(v) for k, v in payload["cast"].items()}
