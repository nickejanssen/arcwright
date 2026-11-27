"""Put a written case into a session at session start (spec 0093, Parts A, B).

Each cast character becomes a ``characters`` row, the same object a player's
character is, and its ``knows`` list is saved into the knowledge graph so any
generated line stays limited by what that character knows (principle 5).
Every non-host participant is given the opening concepts.

Nothing here needs a new table: which cast ID is which character is recorded
in one saved event, and holdings are knowledge-graph facts.
"""

from __future__ import annotations

import asyncio
from collections import OrderedDict
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from threading import Lock
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.case.authored import (
    AuthoredCase,
    AuthoredCaseRefused,
    check_case,
    parse_authored_case,
)
from engine.db.orm import Character, Event, SessionParticipant
from engine.knowledge.holdings import grant_concept

CAST_SEATED_EVENT = "case_cast_seated"
_REPO_ROOT = Path(__file__).resolve().parents[2]


class CaseRefusedAtStartError(Exception):
    """The arc's case file was refused by the fairness check."""


@dataclass(frozen=True)
class _CaseInputs:
    source: bytes = field(repr=False)
    beats: tuple[str, ...]
    budget: int
    choice_beats: frozenset[str] | None


def _validate(inputs: _CaseInputs) -> AuthoredCase:
    try:
        case = parse_authored_case(inputs.source.decode("utf-8"))
        check = check_case(case, beat_order=inputs.beats, budget=inputs.budget)
        if not check.passed:
            raise AuthoredCaseRefused(check)
    except AuthoredCaseRefused as refused:
        raise CaseRefusedAtStartError(f"case refused: {refused.name}") from refused
    if inputs.choice_beats is not None:
        offered = {beat for opp in case.opportunities for beat in opp.beats}
        missing = sorted(offered.intersection(inputs.beats) - inputs.choice_beats)
        if missing:
            msg = "case offers choices in beats with no choices phase: " + ", ".join(
                missing
            )
            raise CaseRefusedAtStartError(msg)
    return case


_worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="case-validation")
_checked: OrderedDict[_CaseInputs, AuthoredCase] = OrderedDict()
_pending: dict[_CaseInputs, Future[AuthoredCase]] = {}
_cache_lock = Lock()


def _check_and_remember(inputs: _CaseInputs) -> AuthoredCase:
    try:
        case = _validate(inputs)
        with _cache_lock:
            _checked[inputs] = case
            if len(_checked) > 16:
                _checked.popitem(last=False)
        return case
    finally:
        with _cache_lock:
            del _pending[inputs]


async def cached_arc_case(arc: ArcDefinition) -> AuthoredCase | None:
    """Share a check of the exact bytes and rules across starts and room reads."""
    if not arc.case_file:
        return None
    source = await asyncio.to_thread((_REPO_ROOT / arc.case_file).read_bytes)
    inputs = _CaseInputs(
        source,
        tuple(beat.beat_id for beat in arc.beats),
        arc.choice_config.budget,
        frozenset(
            beat.beat_id
            for beat in arc.beats
            if any(phase.kind.value == "choices" for phase in beat.phases or [])
        )
        if arc.is_phased
        else None,
    )
    with _cache_lock:
        if inputs in _checked:
            _checked.move_to_end(inputs)
            return _checked[inputs]
        future = _pending.get(inputs)
        if future is None:
            future = _worker.submit(_check_and_remember, inputs)
            _pending[inputs] = future
    result = asyncio.wrap_future(future)
    return await asyncio.shield(result)


@lru_cache(maxsize=16)
def _restore_case(snapshot: str) -> AuthoredCase:
    return AuthoredCase.model_validate_json(snapshot)


async def session_case(
    db: AsyncSession, session_id: UUID, arc: ArcDefinition
) -> AuthoredCase | None:
    """Read the private snapshot saved by Start, including after API restart."""
    seated = select(Event).where(
        Event.session_id == session_id, Event.event_type == CAST_SEATED_EVENT
    )
    payload = await db.scalar(seated.with_only_columns(Event.payload))
    if payload is None:
        # A pre-start read has no pin yet.
        return await cached_arc_case(arc)
    if "case_snapshot" in payload:
        return _restore_case(payload["case_snapshot"])
    # Older sessions have no historical bytes. Pin the available validated
    # version on first read, serializing the backfill on the seating row.
    row = (
        await db.execute(
            seated.with_for_update().execution_options(populate_existing=True)
        )
    ).scalar_one()
    if "case_snapshot" in row.payload:
        return _restore_case(row.payload["case_snapshot"])
    case = await cached_arc_case(arc)
    if case is not None:
        row.payload = {**row.payload, "case_snapshot": case.model_dump_json()}
        await db.flush()
    return case


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
                    "case_snapshot": case.model_dump_json(),
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
