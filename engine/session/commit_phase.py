"""A phase where each player privately builds and locks a theory (spec 0094,
Parts G and H; AW-326).

``engine.session.phases`` moves a round from phase to phase. This module is
what it calls for a ``commit`` phase, and what its thin public functions use to
read the form, save a draft and lock:

  - ``begin``: give every player the opening concepts, so the offer is complete.
  - ``everyone_locked``: the rule that ends the phase early.
  - ``close``: when the phase ends for any reason, lock every complete unlocked
    draft as it stands, and record a player with no complete draft as having
    no theory.

The case supplies the slots. A cast slot offers every cast member the case
marks nameable. A concept slot offers every concept the player holds, true and
misleading alike. Neither list reads which answers are accepted, and neither
carries any mark of right or wrong. Something only heard is not held.

Nothing is stored in a new table. A draft is one ``decisions`` row per save, so
the record shows every change; the newest wins. A lock is one ``decisions`` row
per player per visit, and after it nothing more is accepted from that player.
Until the result is worked out, a draft and a lock go to their owner only; the
host and the shared screen are told only who has locked and how many.

Every function that writes is called with the session lock held by the caller,
and reads saved state first, so a repeated call finds nothing to do. The part
of the check that says whether a theory is right is never run here
(``engine.session.endgame``).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Collection, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.case.authored import AuthoredCase, AuthoredSlot, split_account
from engine.db.orm import Decision, SessionParticipant
from engine.events.models import (
    AudienceTarget,
    ContentEvent,
    EventCategory,
    PresentationHints,
)
from engine.knowledge.holdings import concepts_held, grant_concept

Publish = Callable[[ContentEvent], Awaitable[Any]] | None

THEORY_DRAFT = "theory_draft"
THEORY_LOCK = "theory_lock"
DRAFT_SAVED_EVENT = "theory_draft_saved"
LOCKED_EVENT = "theory_locked"
PROGRESS_EVENT = "theory_lock_progress"

TheoryState = Literal["none", "drafting", "locked", "no_theory"]


class CommitRefusal(Exception):
    """A request the rules refuse. ``code`` is stable; ``phases`` turns it into
    a ``RoundError`` for the routes."""

    def __init__(self, code: str, message: str | None = None) -> None:
        super().__init__(message or code)
        self.code = code


@dataclass(frozen=True)
class Theory:
    """One player's saved theory for one visit. Never carries a verdict."""

    state: TheoryState
    answers: dict[str, str]
    proof: str | None
    revision: int


@dataclass(frozen=True)
class FormOption:
    value: str
    label: str
    text: str | None = None
    """The concept's written text, for a concept option; None for a cast option."""


@dataclass(frozen=True)
class FormSlot:
    slot_id: str
    label: str
    kind: str
    options: tuple[FormOption, ...]


@dataclass(frozen=True)
class AccountPart:
    """A piece of the account text: written ``text``, or a blank for ``slot_id``."""

    text: str
    slot_id: str | None


@dataclass(frozen=True)
class TheoryForm:
    """What a player's phone needs. ``slots``, ``proof_options`` and ``account``
    are empty when no theory is being built."""

    open: bool
    phase_entry: int | None
    deadline_at: datetime | None
    seconds_left: float | None
    slots: tuple[FormSlot, ...]
    account: tuple[AccountPart, ...]
    proof_options: tuple[FormOption, ...]
    theory: Theory


_NO_THEORY = Theory(state="none", answers={}, proof=None, revision=0)


# --- reading saved rows ---------------------------------------------------------


async def _rows(db: AsyncSession, session_id: UUID) -> list[Decision]:
    result = await db.execute(
        select(Decision).where(
            Decision.session_id == session_id,
            Decision.decision_type.in_([THEORY_DRAFT, THEORY_LOCK]),
        )
    )
    return list(result.scalars().all())


def _theory_from(rows: list[Decision], participant_id: UUID, entry: int) -> Theory:
    mine = [
        r
        for r in rows
        if r.context.get("participant_id") == str(participant_id)
        and r.context.get("phase_entry") == entry
    ]
    for row in mine:
        if row.decision_type == THEORY_LOCK:
            return Theory(
                state=row.outcome["state"],
                answers=dict(row.outcome.get("answers", {})),
                proof=row.outcome.get("proof"),
                revision=int(row.context.get("revision", 0)),
            )
    drafts = [r for r in mine if r.decision_type == THEORY_DRAFT]
    if not drafts:
        return _NO_THEORY
    newest = max(drafts, key=lambda r: int(r.context["revision"]))
    return Theory(
        state="drafting",
        answers=dict(newest.outcome.get("answers", {})),
        proof=newest.outcome.get("proof"),
        revision=int(newest.context["revision"]),
    )


async def theory_of(
    db: AsyncSession, session_id: UUID, participant_id: UUID, entry: int
) -> Theory:
    """This player's saved theory for one visit to the commit phase."""
    return _theory_from(await _rows(db, session_id), participant_id, entry)


async def latest_entry_of(
    db: AsyncSession, session_id: UUID, participant_id: UUID
) -> int | None:
    """The newest visit in which this player has saved anything."""
    entries = [
        int(r.context["phase_entry"])
        for r in await _rows(db, session_id)
        if r.context.get("participant_id") == str(participant_id)
    ]
    return max(entries) if entries else None


async def latest_entry(db: AsyncSession, session_id: UUID) -> int | None:
    """The newest visit to a commit phase in which anything was saved."""
    entries = [int(r.context["phase_entry"]) for r in await _rows(db, session_id)]
    return max(entries) if entries else None


async def locked_ids(db: AsyncSession, session_id: UUID, entry: int) -> set[str]:
    """Players who have locked a theory in this visit (not those recorded as
    having none)."""
    return {
        str(r.context["participant_id"])
        for r in await _rows(db, session_id)
        if r.decision_type == THEORY_LOCK
        and r.context.get("phase_entry") == entry
        and r.outcome.get("state") == "locked"
    }


async def everyone_locked(
    db: AsyncSession, session_id: UUID, entry: int, humans: Collection[UUID]
) -> bool:
    """True when there is at least one player and every one has locked."""
    if not humans:
        return False
    return {str(p) for p in humans} <= await locked_ids(db, session_id, entry)


# --- the offer ------------------------------------------------------------------


def _cast_options(case: AuthoredCase) -> tuple[FormOption, ...]:
    chosen = sorted(
        (c for c in case.cast if c.nameable),
        key=lambda c: (c.display_name.casefold(), c.cast_id),
    )
    return tuple(FormOption(value=c.cast_id, label=c.display_name) for c in chosen)


def _concept_options(
    case: AuthoredCase, held: frozenset[str]
) -> tuple[FormOption, ...]:
    chosen = sorted(
        (c for c in case.concepts if c.concept_id in held),
        key=lambda c: (c.label.casefold(), c.concept_id),
    )
    return tuple(
        FormOption(value=c.concept_id, label=c.label, text=c.text) for c in chosen
    )


def _offer(
    case: AuthoredCase, held: frozenset[str]
) -> tuple[tuple[FormSlot, ...], tuple[FormOption, ...]]:
    cast = _cast_options(case)
    concepts = _concept_options(case, held)
    slots = tuple(
        FormSlot(
            slot_id=slot.slot_id,
            label=slot.label,
            kind=slot.kind,
            options=cast if slot.kind == "cast" else concepts,
        )
        for slot in case.solution
    )
    return slots, concepts


def _account(case: AuthoredCase) -> tuple[AccountPart, ...]:
    if case.account is None:
        return ()
    return tuple(AccountPart(text, slot) for text, slot in split_account(case.account))


async def _character_id(
    db: AsyncSession, session_id: UUID, participant_id: UUID
) -> UUID:
    result = await db.execute(
        select(SessionParticipant.character_id).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.participant_id == participant_id,
        )
    )
    character_id = result.scalar_one_or_none()
    if character_id is None:
        raise CommitRefusal("not_a_participant")
    return character_id


async def _held(
    db: AsyncSession, session_id: UUID, character_id: UUID, case: AuthoredCase
) -> frozenset[str]:
    """What the player holds, giving them the opening first if they have not been
    given it (a player added after the session started)."""
    held = await concepts_held(db, session_id=session_id, character_id=character_id)
    if set(case.opening) <= held:
        return held
    texts = {c.concept_id: c.text for c in case.concepts}
    for concept_id in case.opening:
        await grant_concept(
            db,
            session_id=session_id,
            character_id=character_id,
            concept_id=concept_id,
            text=texts[concept_id],
        )
    return await concepts_held(db, session_id=session_id, character_id=character_id)


# --- events ---------------------------------------------------------------------


async def _emit(
    publish: Publish,
    session_id: UUID,
    now: datetime,
    *,
    event_type: str,
    audience: AudienceTarget,
    payload: dict[str, Any],
    category: EventCategory,
    target_player_id: UUID | None = None,
) -> None:
    if publish is None:
        return
    await publish(
        ContentEvent(
            session_id=session_id,
            timestamp=now,
            category=category,
            event_type=event_type,
            target_audience=audience,
            target_player_id=target_player_id,
            payload=payload,
            presentation_hints=PresentationHints(),
        )
    )


async def _tell_owner(
    publish: Publish,
    session_id: UUID,
    participant_id: UUID,
    now: datetime,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    await _emit(
        publish,
        session_id,
        now,
        event_type=event_type,
        audience=AudienceTarget.specific_player,
        target_player_id=participant_id,
        payload=payload,
        category=EventCategory.private_delivery,
    )


async def _tell_progress(
    db: AsyncSession,
    publish: Publish,
    session_id: UUID,
    participant_id: UUID,
    entry: int,
    humans: Collection[UUID],
    now: datetime,
) -> None:
    """Tell the shared screen and the host who has locked and how many. Never
    the answers, and never another player's phone."""
    payload = {
        "participant_id": str(participant_id),
        "locked_count": len(await locked_ids(db, session_id, entry)),
        "player_count": len(humans),
    }
    for audience in (AudienceTarget.shared_display, AudienceTarget.host_only):
        await _emit(
            publish,
            session_id,
            now,
            event_type=PROGRESS_EVENT,
            audience=audience,
            payload=payload,
            category=EventCategory.state_transition,
        )


# --- the phase ------------------------------------------------------------------


async def begin(
    db: AsyncSession,
    session_id: UUID,
    case: AuthoredCase,
    humans: Collection[UUID],
) -> None:
    """The phase has started: make sure every player holds the opening, so the
    concept offer is complete. The countdown is the phase's own deadline."""
    for participant_id in humans:
        await _held(
            db, session_id, await _character_id(db, session_id, participant_id), case
        )


async def read_form(
    db: AsyncSession,
    session_id: UUID,
    case: AuthoredCase,
    participant_id: UUID,
    *,
    entry: int | None,
    open_now: bool,
    deadline_at: datetime | None,
    seconds_left: float | None,
) -> TheoryForm:
    """This player's form. ``entry`` is the visit being built, or None when no
    commit phase is current (running or paused); then the form carries only the
    player's own saved theory. ``open_now`` is whether it can be edited at this
    moment (running and before the deadline)."""
    character_id = await _character_id(db, session_id, participant_id)
    rows = await _rows(db, session_id)
    shown = entry
    if shown is None:
        mine = [
            int(r.context["phase_entry"])
            for r in rows
            if r.context.get("participant_id") == str(participant_id)
        ]
        shown = max(mine) if mine else None
    theory = (
        _theory_from(rows, participant_id, shown) if shown is not None else _NO_THEORY
    )
    if entry is None:
        return TheoryForm(False, shown, deadline_at, seconds_left, (), (), (), theory)
    held = await _held(db, session_id, character_id, case)
    slots, proof_options = _offer(case, held)
    return TheoryForm(
        open=open_now and theory.state in ("none", "drafting"),
        phase_entry=entry,
        deadline_at=deadline_at,
        seconds_left=seconds_left,
        slots=slots,
        account=_account(case),
        proof_options=proof_options,
        theory=theory,
    )


def _validate(
    case: AuthoredCase,
    held: frozenset[str],
    answers: Mapping[str, str],
    proof: str | None,
) -> None:
    slots: dict[str, AuthoredSlot] = {s.slot_id: s for s in case.solution}
    nameable = {c.cast_id for c in case.cast if c.nameable}
    for slot_id, value in answers.items():
        slot = slots.get(slot_id)
        if slot is None:
            raise CommitRefusal("unknown_slot", "that slot is not in this theory")
        if slot.kind == "cast" and value not in nameable:
            raise CommitRefusal("answer_not_offered", "that answer is not on offer")
        if slot.kind == "concept" and value not in held:
            raise CommitRefusal("concept_not_held", "you do not hold that")
    if proof is not None and proof not in held:
        raise CommitRefusal("proof_not_held", "you do not hold that")


async def save_draft(
    db: AsyncSession,
    session_id: UUID,
    case: AuthoredCase,
    participant_id: UUID,
    *,
    entry: int,
    beat_id: str,
    answers: Mapping[str, str],
    proof: str | None,
    now: datetime,
    publish: Publish,
) -> Theory:
    """Replace this player's draft. Refused after a lock, and for an answer that
    is not on offer or a concept not held. Saving what is already saved changes
    nothing."""
    character_id = await _character_id(db, session_id, participant_id)
    current = await theory_of(db, session_id, participant_id, entry)
    if current.state in ("locked", "no_theory"):
        raise CommitRefusal("theory_locked", "your theory is already locked")
    held = await _held(db, session_id, character_id, case)
    _validate(case, held, answers, proof)
    if current.state == "drafting" and (current.answers, current.proof) == (
        dict(answers),
        proof,
    ):
        return current
    revision = current.revision + 1
    db.add(
        Decision(
            session_id=session_id,
            timestamp=now,
            decision_type=THEORY_DRAFT,
            context={
                "participant_id": str(participant_id),
                "beat_id": beat_id,
                "phase_entry": entry,
                "revision": revision,
            },
            outcome={"answers": dict(answers), "proof": proof},
        )
    )
    await db.flush()
    saved = Theory("drafting", dict(answers), proof, revision)
    await _tell_owner(
        publish,
        session_id,
        participant_id,
        now,
        DRAFT_SAVED_EVENT,
        {"answers": saved.answers, "proof": proof, "revision": revision},
    )
    return saved


def _is_complete(case: AuthoredCase, answers: Mapping[str, str]) -> bool:
    return all(answers.get(slot.slot_id) for slot in case.solution)


async def _write_lock(
    db: AsyncSession,
    session_id: UUID,
    participant_id: UUID,
    entry: int,
    beat_id: str,
    state: Literal["locked", "no_theory"],
    answers: Mapping[str, str],
    proof: str | None,
    locked_by: str,
    now: datetime,
) -> Theory:
    db.add(
        Decision(
            session_id=session_id,
            timestamp=now,
            decision_type=THEORY_LOCK,
            context={
                "participant_id": str(participant_id),
                "beat_id": beat_id,
                "phase_entry": entry,
            },
            outcome={
                "state": state,
                "answers": dict(answers),
                "proof": proof,
                "locked_by": locked_by,
            },
        )
    )
    await db.flush()
    return Theory(state, dict(answers), proof, 0)


async def lock(
    db: AsyncSession,
    session_id: UUID,
    case: AuthoredCase,
    participant_id: UUID,
    *,
    entry: int,
    beat_id: str,
    humans: Collection[UUID],
    now: datetime,
    publish: Publish,
) -> Theory:
    """Lock this player's saved draft. Refused when any slot is empty, and after
    a lock. The proof is optional."""
    await _character_id(db, session_id, participant_id)
    current = await theory_of(db, session_id, participant_id, entry)
    if current.state in ("locked", "no_theory"):
        raise CommitRefusal("theory_locked", "your theory is already locked")
    if current.state != "drafting" or not _is_complete(case, current.answers):
        raise CommitRefusal("theory_incomplete", "every slot needs an answer")
    locked = await _write_lock(
        db,
        session_id,
        participant_id,
        entry,
        beat_id,
        "locked",
        current.answers,
        current.proof,
        "player",
        now,
    )
    await _tell_owner(
        publish,
        session_id,
        participant_id,
        now,
        LOCKED_EVENT,
        {
            "state": "locked",
            "answers": locked.answers,
            "proof": locked.proof,
            "locked_by": "player",
        },
    )
    await _tell_progress(db, publish, session_id, participant_id, entry, humans, now)
    return Theory("locked", locked.answers, locked.proof, current.revision)


async def close(
    db: AsyncSession,
    session_id: UUID,
    case: AuthoredCase,
    *,
    entry: int,
    beat_id: str,
    humans: Collection[UUID],
    now: datetime,
    publish: Publish,
) -> None:
    """The phase is ending. Lock each complete unlocked draft as it stands;
    record everyone else as having no theory. A second call finds a row for
    every player and does nothing."""
    rows = await _rows(db, session_id)
    for participant_id in sorted(humans, key=str):
        current = _theory_from(rows, participant_id, entry)
        if current.state in ("locked", "no_theory"):
            continue
        if current.state == "drafting" and _is_complete(case, current.answers):
            await _write_lock(
                db,
                session_id,
                participant_id,
                entry,
                beat_id,
                "locked",
                current.answers,
                current.proof,
                "phase_end",
                now,
            )
            await _tell_owner(
                publish,
                session_id,
                participant_id,
                now,
                LOCKED_EVENT,
                {
                    "state": "locked",
                    "answers": current.answers,
                    "proof": current.proof,
                    "locked_by": "phase_end",
                },
            )
            await _tell_progress(
                db, publish, session_id, participant_id, entry, humans, now
            )
        else:
            await _write_lock(
                db,
                session_id,
                participant_id,
                entry,
                beat_id,
                "no_theory",
                {},
                None,
                "phase_end",
                now,
            )
            await _tell_owner(
                publish,
                session_id,
                participant_id,
                now,
                LOCKED_EVENT,
                {"state": "no_theory", "answers": {}, "proof": None},
            )
