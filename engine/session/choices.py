"""The investigation menu, the saved budget and what a participant holds
(spec 0093, Part D).

Each choice is one ``decisions`` row: the choice ID the phone sent, the menu it
was made from, what it cost and what it gave. The budget is never stored; it is
worked out from those rows in one place (``remaining_budget``), so extra budget
from a later reward is a saved grant and one added term, not a new rule.

Privacy: the written content of a choice goes to that player only. The shared
screen and every other player receive nothing from it; the host hears only that
a choice was made.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition, PhaseKind
from engine.arc.registry import load_arc_definition
from engine.case.authored import AuthoredCase, AuthoredOpportunity
from engine.db.orm import Decision, SessionParticipant
from engine.db.orm import Session as OrmSession
from engine.events.models import AudienceTarget, EventCategory
from engine.knowledge.holdings import concepts_held, grant_concept
from engine.session.case_seating import cached_arc_case
from engine.session.mini_game_reward import RewardGrant, rewards_from_rows
from engine.session.models import SessionStatus
from engine.session.phases import (
    Publish,
    RoundError,
    content_event,
    current_phase,
    emit,
    human_player_ids,
    session_lock,
)

CHOICE_DECISION = "choice"
BUDGET_GRANT_DECISION = "budget_grant"
MENU_SHOWN_DECISION = "menu_shown"


@dataclass(frozen=True)
class MenuItem:
    opportunity_id: str
    subject_id: str
    subject_kind: str
    subject_label: str
    label: str
    cost: int
    taken: bool


@dataclass(frozen=True)
class Menu:
    open: bool
    remaining_budget: int
    items: tuple[MenuItem, ...]
    rewards: tuple[RewardGrant, ...] = ()


@dataclass(frozen=True)
class ChoiceResult:
    choice_id: str
    opportunity_id: str
    content: str
    gave: list[str]
    cost: int
    first_time: bool
    replayed: bool
    remaining_budget: int


@dataclass(frozen=True)
class HeldConcept:
    """What a player sees of something they hold. Deliberately has no field for
    whether it is true or misleading."""

    concept_id: str
    label: str
    text: str
    found_from: str | None = None
    """The label of the subject it came from; None for what they held at the start."""
    found_in_beat: str | None = None
    """The beat it was found in; None for what they held at the start."""
    found_in_round_title: str | None = None
    """That beat's name, the one a screen may print; None for what they held at the start."""
    found_in_round_number: int | None = None
    """That round's 1-based place among the rounds that offer choices."""


# --- the budget, worked out in one place ----------------------------------------


def budget_allowance(arc: ArcDefinition, *, granted: Iterable[int]) -> int:
    """What a participant may spend over the whole game: the arc's base budget
    plus every saved grant (a mini-game reward, AW-328, is one more grant)."""
    return arc.choice_config.budget + sum(granted)


@dataclass(frozen=True)
class _Ledger:
    choices: list[Decision]
    granted: list[int]
    rewards: tuple[RewardGrant, ...] = ()

    @property
    def spent(self) -> int:
        return sum(int(row.outcome.get("cost", 0)) for row in self.choices)

    @property
    def taken(self) -> set[str]:
        return {
            str(row.context["opportunity_id"])
            for row in self.choices
            if row.outcome.get("first_time")
        }


async def _ledger(db: AsyncSession, session_id: UUID, participant_id: UUID) -> _Ledger:
    result = await db.execute(
        select(Decision)
        .where(
            Decision.session_id == session_id,
            Decision.decision_type.in_([CHOICE_DECISION, BUDGET_GRANT_DECISION]),
        )
        .order_by(Decision.timestamp, Decision.decision_id)
    )
    mine = [
        row
        for row in result.scalars().all()
        if row.context.get("participant_id") == str(participant_id)
    ]
    return _Ledger(
        choices=[r for r in mine if r.decision_type == CHOICE_DECISION],
        granted=[
            int(r.outcome.get("amount", 0))
            for r in mine
            if r.decision_type == BUDGET_GRANT_DECISION
        ],
        rewards=rewards_from_rows(
            r for r in mine if r.decision_type == BUDGET_GRANT_DECISION
        ),
    )


async def remaining_budget(
    db: AsyncSession, session_id: UUID, participant_id: UUID
) -> int:
    orm = await db.get(OrmSession, session_id)
    if orm is None:
        raise RoundError("session_not_found")
    arc = load_arc_definition(orm.arc_id)
    if arc is None:
        raise RoundError("not_phased")
    ledger = await _ledger(db, session_id, participant_id)
    return budget_allowance(arc, granted=ledger.granted) - ledger.spent


# --- shared checks --------------------------------------------------------------


@dataclass(frozen=True)
class _Context:
    orm: OrmSession
    arc: ArcDefinition
    case: AuthoredCase
    character_id: UUID


async def _context(
    db: AsyncSession, orm: OrmSession | None, participant_id: UUID
) -> _Context:
    if orm is None:
        raise RoundError("session_not_found")
    result = await db.execute(
        select(SessionParticipant.character_id).where(
            SessionParticipant.session_id == orm.session_id,
            SessionParticipant.participant_id == participant_id,
        )
    )
    character_id = result.scalar_one_or_none()
    if character_id is None or participant_id not in await human_player_ids(
        db, orm.session_id
    ):
        raise RoundError("not_a_participant")
    arc = load_arc_definition(orm.arc_id)
    if arc is None or not arc.is_phased:
        raise RoundError("not_phased", "this game does not run by phases")
    case = await cached_arc_case(arc)
    if case is None:
        raise RoundError("no_written_case", "this game has no written case")
    return _Context(orm, arc, case, character_id)


async def _held_with_opening(
    db: AsyncSession, ctx: _Context, *, locked: bool
) -> frozenset[str]:
    """What the participant holds, giving them the opening first if they have
    not been given it (a player who joined after the start)."""
    session_id = ctx.orm.session_id
    held = await concepts_held(db, session_id=session_id, character_id=ctx.character_id)
    if set(ctx.case.opening) <= held:
        return held
    if locked:
        await _grant_opening(db, ctx)
    else:
        async with session_lock(db, session_id):
            await _grant_opening(db, ctx)
    return await concepts_held(db, session_id=session_id, character_id=ctx.character_id)


async def _grant_opening(db: AsyncSession, ctx: _Context) -> None:
    texts = {c.concept_id: c.text for c in ctx.case.concepts}
    for concept_id in ctx.case.opening:
        await grant_concept(
            db,
            session_id=ctx.orm.session_id,
            character_id=ctx.character_id,
            concept_id=concept_id,
            text=texts[concept_id],
        )


def _menu_items(
    case: AuthoredCase, beat_id: str, held: frozenset[str], taken: set[str]
) -> list[MenuItem]:
    subjects = {s.subject_id: s for s in case.subjects}
    return [
        MenuItem(
            opportunity_id=o.opportunity_id,
            subject_id=o.subject_id,
            subject_kind=subjects[o.subject_id].kind,
            subject_label=subjects[o.subject_id].label,
            label=o.label,
            cost=o.cost,
            taken=o.opportunity_id in taken,
        )
        for o in case.opportunities
        if beat_id in o.beats and set(o.requires) <= held
    ]


async def _choices_open(db: AsyncSession, orm: OrmSession) -> bool:
    if orm.status != SessionStatus.active.value:
        return False
    state = await current_phase(db, orm.session_id)
    return (
        state is not None
        and state.status == "running"
        and state.phase == PhaseKind.choices.value
        and state.beat_id == orm.current_beat_id
    )


# --- public engine functions ----------------------------------------------------


async def read_menu(
    db: AsyncSession,
    session_id: UUID,
    participant_id: UUID,
    now: datetime | None = None,
) -> Menu:
    """This participant's menu: every choice available in this beat whose
    prerequisites they hold, marked new or already taken, with their budget.
    Closed (no items) outside a choices phase.

    The first read in each visit to the choices phase saves what was offered
    (a ``menu_shown`` row), so the record shows the menu of a player who then
    chose nothing."""
    orm = await db.get(OrmSession, session_id)
    ctx = await _context(db, orm, participant_id)
    ledger = await _ledger(db, session_id, participant_id)
    left = budget_allowance(ctx.arc, granted=ledger.granted) - ledger.spent
    rewards = ledger.rewards
    if not await _choices_open(db, ctx.orm):
        return Menu(open=False, remaining_budget=left, items=(), rewards=rewards)
    held = await _held_with_opening(db, ctx, locked=False)
    items = _menu_items(ctx.case, ctx.orm.current_beat_id, held, ledger.taken)
    await _save_menu_shown(db, ctx, participant_id, items, now)
    return Menu(open=True, remaining_budget=left, items=tuple(items), rewards=rewards)


async def _save_menu_shown(
    db: AsyncSession,
    ctx: _Context,
    participant_id: UUID,
    items: list[MenuItem],
    now: datetime | None,
) -> None:
    state = await current_phase(db, ctx.orm.session_id)
    if state is None:
        return
    result = await db.execute(
        select(Decision.context).where(
            Decision.session_id == ctx.orm.session_id,
            Decision.decision_type == MENU_SHOWN_DECISION,
        )
    )
    contexts: list[dict[str, Any]] = list(result.scalars().all())
    if any(
        c.get("participant_id") == str(participant_id)
        and c.get("phase_entry") == state.entry
        for c in contexts
    ):
        return
    row = Decision(
        session_id=ctx.orm.session_id,
        decision_type=MENU_SHOWN_DECISION,
        context={
            "participant_id": str(participant_id),
            "beat_id": ctx.orm.current_beat_id,
            "phase_entry": state.entry,
            "offered": [item.opportunity_id for item in items],
            "subjects": {
                item.opportunity_id: [item.subject_id, item.subject_kind]
                for item in items
            },
        },
        outcome={},
    )
    if now is not None:
        row.timestamp = now
    db.add(row)
    await db.flush()


async def read_holdings(
    db: AsyncSession, session_id: UUID, participant_id: UUID
) -> list[HeldConcept]:
    """What this participant found for themselves, with its written text."""
    orm = await db.get(OrmSession, session_id)
    ctx = await _context(db, orm, participant_id)
    held = await _held_with_opening(db, ctx, locked=False)
    ledger = await _ledger(db, session_id, participant_id)
    subjects = {s.subject_id: s.label for s in ctx.case.subjects}
    found: dict[str, tuple[str, str]] = {}
    for row in ledger.choices:
        if not row.outcome.get("first_time"):
            continue
        opportunity = _opportunity(ctx.case, str(row.context["opportunity_id"]))
        for concept_id in row.outcome.get("gave", []):
            found.setdefault(
                concept_id,
                (subjects[opportunity.subject_id], str(row.context["beat_id"])),
            )
    rounds = [
        b
        for b in ctx.arc.beats
        if any(p.kind is PhaseKind.choices for p in (b.phases or []))
    ]
    titles = {b.beat_id: (b.beat_name, n) for n, b in enumerate(rounds, start=1)}
    held_concepts: list[HeldConcept] = []
    for c in ctx.case.concepts:
        if c.concept_id not in held:
            continue
        subject, beat = found.get(c.concept_id, (None, None))
        title, number = titles.get(beat, (None, None)) if beat else (None, None)
        held_concepts.append(
            HeldConcept(c.concept_id, c.label, c.text, subject, beat, title, number)
        )
    return held_concepts


def _result_from_row(
    case: AuthoredCase, row: Decision, left: int, *, replayed: bool
) -> ChoiceResult:
    opportunity = _opportunity(case, str(row.context["opportunity_id"]))
    return ChoiceResult(
        choice_id=str(row.context["choice_id"]),
        opportunity_id=opportunity.opportunity_id,
        content=opportunity.content,
        gave=list(row.outcome.get("gave", [])),
        cost=int(row.outcome.get("cost", 0)),
        first_time=bool(row.outcome.get("first_time")),
        replayed=replayed,
        remaining_budget=left,
    )


def _subject_kind(case: AuthoredCase, subject_id: str) -> str:
    for subject in case.subjects:
        if subject.subject_id == subject_id:
            return subject.kind
    return ""


def _opportunity(case: AuthoredCase, opportunity_id: str) -> AuthoredOpportunity:
    for opportunity in case.opportunities:
        if opportunity.opportunity_id == opportunity_id:
            return opportunity
    raise RoundError("not_on_menu")


async def choose(
    db: AsyncSession,
    session_id: UUID,
    participant_id: UUID,
    choice_id: str,
    opportunity_id: str,
    now: datetime,
    publish: Publish = None,
) -> ChoiceResult:
    """Make a choice from the menu.

    Order of checks (spec 0093, Part D): the phase is open; the opportunity is
    on this player's menu; the budget covers it. Then it is saved, the concepts
    are given, and the content goes to this player only. Something already
    taken costs nothing and shows the same content again. The same ``choice_id``
    from the same player has one effect and returns the same answer, with the
    budget as it was then. Choices are refused once the phase deadline has
    passed, even before the tick has ended the phase.
    """
    async with session_lock(db, session_id) as orm:
        ctx = await _context(db, orm, participant_id)
        ledger = await _ledger(db, session_id, participant_id)
        left = budget_allowance(ctx.arc, granted=ledger.granted) - ledger.spent

        for row in ledger.choices:
            if row.context.get("choice_id") == choice_id:
                if row.context.get("opportunity_id") != opportunity_id:
                    raise RoundError(
                        "choice_id_reused",
                        "that choice_id was already used for a different choice",
                    )
                # A replay repeats the first answer, budget included.
                saved = row.outcome
                then = (
                    int(saved["allowance"]) - int(saved["spent_after"])
                    if "allowance" in saved and "spent_after" in saved
                    else left
                )
                return _result_from_row(ctx.case, row, then, replayed=True)

        if ctx.orm.status != SessionStatus.active.value:
            raise RoundError("session_not_active", f"session is {ctx.orm.status}")
        if not await _choices_open(db, ctx.orm):
            raise RoundError("not_in_choices_phase")
        state = await current_phase(db, session_id)
        if (
            state is not None
            and state.deadline_at is not None
            and now >= state.deadline_at
        ):
            raise RoundError("phase_time_up", "the time for this phase is up")

        held = await _held_with_opening(db, ctx, locked=True)
        beat_id = ctx.orm.current_beat_id
        taken = ledger.taken
        menu = _menu_items(ctx.case, beat_id, held, taken)
        if opportunity_id not in {item.opportunity_id for item in menu}:
            raise RoundError("not_on_menu")
        opportunity = _opportunity(ctx.case, opportunity_id)

        first_time = opportunity_id not in taken
        cost = opportunity.cost if first_time else 0
        if cost > left:
            raise RoundError("budget_exhausted")

        gave = list(opportunity.gives) if first_time else []
        db.add(
            Decision(
                session_id=session_id,
                timestamp=now,
                decision_type=CHOICE_DECISION,
                context={
                    "choice_id": choice_id,
                    "participant_id": str(participant_id),
                    "beat_id": beat_id,
                    "phase_entry": state.entry if state else None,
                    "offered": [item.opportunity_id for item in menu],
                    "opportunity_id": opportunity_id,
                    "subject_id": opportunity.subject_id,
                    "subject_kind": _subject_kind(ctx.case, opportunity.subject_id),
                },
                outcome={
                    "cost": cost,
                    "gave": gave,
                    "first_time": first_time,
                    "allowance": budget_allowance(ctx.arc, granted=ledger.granted),
                    "spent_after": ledger.spent + cost,
                },
            )
        )
        await db.flush()
        if first_time:
            texts = {c.concept_id: c.text for c in ctx.case.concepts}
            for concept_id in gave:
                await grant_concept(
                    db,
                    session_id=session_id,
                    character_id=ctx.character_id,
                    concept_id=concept_id,
                    text=texts[concept_id],
                )
        left -= cost
        result = ChoiceResult(
            choice_id=choice_id,
            opportunity_id=opportunity_id,
            content=opportunity.content,
            gave=gave,
            cost=cost,
            first_time=first_time,
            replayed=False,
            remaining_budget=left,
        )
        await _announce(publish, session_id, participant_id, beat_id, result, now)
        return result


async def _announce(
    publish: Publish,
    session_id: UUID,
    participant_id: UUID,
    beat_id: str,
    result: ChoiceResult,
    now: datetime,
) -> None:
    payload: dict[str, Any] = {
        "choice_id": result.choice_id,
        "opportunity_id": result.opportunity_id,
        "content": result.content,
        "gave": result.gave,
        "cost": result.cost,
        "first_time": result.first_time,
        "remaining_budget": result.remaining_budget,
    }
    await emit(
        publish,
        content_event(
            session_id,
            now,
            category=EventCategory.private_delivery,
            event_type="choice_result",
            audience=AudienceTarget.specific_player,
            target_player_id=participant_id,
            payload=payload,
        ),
    )
    if result.first_time:
        await emit(
            publish,
            content_event(
                session_id,
                now,
                category=EventCategory.state_transition,
                event_type="choice_made",
                audience=AudienceTarget.host_only,
                payload={"participant_id": str(participant_id), "beat_id": beat_id},
            ),
        )
