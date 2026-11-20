"""Survey answers (AW-331, spec 0095 M3).

A player's answers to the game's end-of-session questions, kept as saved rows.
The engine checks only the shape (a few short keys, each a number from 1 to 5 or
a short word, and an optional comment); what the questions are belongs to the
game. A repeat is saved as a new row and the newest counts, so history is kept.
Only the player can read their own answers back; everyone else, the shared
screen included, can learn only whether a player has answered.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Event
from engine.db.orm import Session as OrmSession
from engine.session.host_seat import is_seated_player
from engine.session.models import SessionStatus
from engine.session.phases import RoundError, session_lock

SURVEY_EVENT = "survey_answers"
MAX_ANSWERS = 8
MAX_KEY_LENGTH = 40
MAX_WORD_LENGTH = 40
MAX_COMMENT_LENGTH = 1000
LOW, HIGH = 1, 5


@dataclass(frozen=True)
class SurveyAnswers:
    answers: dict[str, int | str]
    comment: str | None
    revision: int


def _invalid(message: str) -> RoundError:
    return RoundError("invalid_survey", message)


def _check(answers: dict[str, Any], comment: str | None) -> None:
    if not answers or len(answers) > MAX_ANSWERS:
        raise _invalid(f"send between 1 and {MAX_ANSWERS} answers")
    for key, value in answers.items():
        if not isinstance(key, str) or not key or len(key) > MAX_KEY_LENGTH:
            raise _invalid("each answer needs a short key")
        if isinstance(value, bool):
            raise _invalid("an answer is a number or a short word")
        if isinstance(value, int):
            if not LOW <= value <= HIGH:
                raise _invalid(f"a number answer is from {LOW} to {HIGH}")
        elif isinstance(value, str):
            if not value.strip() or len(value) > MAX_WORD_LENGTH:
                raise _invalid("a word answer is short and not empty")
        else:
            raise _invalid("an answer is a number or a short word")
    if comment is not None and len(comment) > MAX_COMMENT_LENGTH:
        raise _invalid(f"a comment is at most {MAX_COMMENT_LENGTH} characters")


async def _rows(
    db: AsyncSession, session_id: UUID, participant_id: UUID | None = None
) -> list[dict[str, Any]]:
    result = await db.execute(
        select(Event.payload).where(
            Event.session_id == session_id, Event.event_type == SURVEY_EVENT
        )
    )
    payloads: list[dict[str, Any]] = list(result.scalars().all())
    if participant_id is None:
        return payloads
    return [p for p in payloads if p["participant_id"] == str(participant_id)]


async def _require_seat(
    db: AsyncSession, session_id: UUID, participant_id: UUID
) -> OrmSession:
    orm = await db.get(OrmSession, session_id)
    if orm is None:
        raise RoundError("session_not_found")
    if not await is_seated_player(db, session_id, participant_id):
        raise RoundError("not_a_participant")
    return orm


async def save_survey(
    db: AsyncSession,
    session_id: UUID,
    participant_id: UUID,
    answers: dict[str, Any],
    comment: str | None,
    now: datetime,
) -> SurveyAnswers:
    """Save this player's answers, replacing any earlier set. Accepted once the
    game has started; the screens decide when to show the survey."""
    _check(answers, comment)
    async with session_lock(db, session_id) as locked:
        if locked is None:
            raise RoundError("session_not_found")
        orm = await _require_seat(db, session_id, participant_id)
        if orm.status == SessionStatus.created.value:
            raise RoundError("game_not_started", "the game has not started yet")
        revision = len(await _rows(db, session_id, participant_id)) + 1
        payload = {
            "participant_id": str(participant_id),
            "answers": dict(answers),
            "comment": comment,
            "revision": revision,
            "saved_at": now.isoformat(),
        }
        db.add(Event(session_id=session_id, event_type=SURVEY_EVENT, payload=payload))
        await db.flush()
    return SurveyAnswers(answers=dict(answers), comment=comment, revision=revision)


async def read_survey(
    db: AsyncSession, session_id: UUID, participant_id: UUID
) -> SurveyAnswers | None:
    """This player's newest answers, or None if they have not answered."""
    await _require_seat(db, session_id, participant_id)
    rows = await _rows(db, session_id, participant_id)
    if not rows:
        return None
    newest = max(rows, key=lambda p: int(p["revision"]))
    return SurveyAnswers(
        answers=dict(newest["answers"]),
        comment=newest["comment"],
        revision=int(newest["revision"]),
    )


async def answered_ids(db: AsyncSession, session_id: UUID) -> set[str]:
    """Who has answered, and nothing about what they said."""
    return {str(p["participant_id"]) for p in await _rows(db, session_id)}
