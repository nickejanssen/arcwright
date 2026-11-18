"""Play records: one reader per fact, four questions (AW-304, spec 0093 Part F).

Every session, for any game, saves the same six facts. Each reader here reads
saved rows only: no case file, arc file or other content file is opened, so the
answers are the same for any game. Rows saved before a field existed are read
with that field empty.

| Fact                                   | Reader               | Saved in                                  |
| -------------------------------------- | -------------------- | ----------------------------------------- |
| Story units entered and left, times    | story_unit_visits    | events ``phase_state``                    |
| Who learned what, and from whom        | learned              | knowledge_states, facts, decisions        |
| What was chosen from what was offered  | choices              | decisions, mini_game_submissions          |
| What each character said               | said                 | claims, events ``dialogue``/``player_input`` |
| Tension against the author's target    | tension              | events ``tension_update``, ``intent_fidelity_summary`` |
| Cost                                   | cost                 | generation_logs                           |

The four questions: ``stalled_phases``, ``unchosen_opportunities``,
``attention_by_subject``, ``reward_use``.

Queries are plain selects with grouping in Python, so they behave the same on
SQLite (tests) and Postgres.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import (
    Claim,
    Decision,
    Event,
    Fact,
    KnowledgeState,
    MiniGameRun,
    MiniGameSubmission,
    SessionParticipant,
)
from engine.telemetry.costs import CostSummaryData, get_cost_summary

READY_ABLE_PHASES = frozenset({"scene", "choices", "bridge"})


def _utc(value: datetime) -> datetime:
    """SQLite returns naive times; the engine saves UTC."""
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _uuid(raw: Any) -> UUID | None:
    return UUID(str(raw)) if raw else None


# --- fact 1: story units entered and left, with times ---------------------------


@dataclass(frozen=True)
class PhaseVisit:
    beat_id: str
    phase: str
    entry: int
    entered_at: datetime
    left_at: datetime | None
    left_reason: str | None
    active_seconds: float | None
    """Time spent running, not counting a pause. None while still inside."""


async def story_unit_visits(db: AsyncSession, session_id: UUID) -> list[PhaseVisit]:
    result = await db.execute(
        select(Event.timestamp, Event.payload).where(
            Event.session_id == session_id, Event.event_type == "phase_state"
        )
    )
    rows = sorted(result.all(), key=lambda row: int(row.payload["seq"]))
    visits: dict[int, dict[str, Any]] = {}
    for row in rows:
        payload, when = row.payload, _utc(row.timestamp)
        visit = visits.setdefault(
            int(payload["entry"]),
            {
                "beat_id": payload["beat_id"],
                "phase": payload["phase"],
                "entered_at": when,
                "running_since": None,
                "active": 0.0,
                "left_at": None,
                "left_reason": None,
            },
        )
        status = payload["status"]
        if status == "running":
            visit["running_since"] = when
        else:
            if visit["running_since"] is not None:
                visit["active"] += (when - visit["running_since"]).total_seconds()
                visit["running_since"] = None
            if status == "ended":
                visit["left_at"] = when
                visit["left_reason"] = payload.get("reason")
    return [
        PhaseVisit(
            beat_id=v["beat_id"],
            phase=v["phase"],
            entry=entry,
            entered_at=v["entered_at"],
            left_at=v["left_at"],
            left_reason=v["left_reason"],
            active_seconds=v["active"] if v["left_at"] is not None else None,
        )
        for entry, v in sorted(visits.items())
    ]


# --- fact 2: who learned what, and from whom ------------------------------------


@dataclass(frozen=True)
class Learned:
    participant_id: UUID | None
    character_id: UUID
    fact_type: str
    fact_ref: str
    source_character_id: UUID | None
    source_opportunity_id: str | None
    """What gave it, when the participant found it through a choice."""
    learned_at: datetime
    active: bool


def _fact_ref(fact: Fact) -> str:
    """The fact's own ID field (``concept_id`` and the like), else its row ID."""
    content = fact.fact_content or {}
    for key in sorted(content):
        if key.endswith("_id") and content[key]:
            return str(content[key])
    return str(fact.fact_id)


async def _participants_by_character(
    db: AsyncSession, session_id: UUID
) -> dict[UUID, UUID]:
    result = await db.execute(
        select(
            SessionParticipant.character_id, SessionParticipant.participant_id
        ).where(SessionParticipant.session_id == session_id)
    )
    return {row.character_id: row.participant_id for row in result.all()}


async def _decisions(db: AsyncSession, session_id: UUID, *types: str) -> list[Decision]:
    result = await db.execute(
        select(Decision)
        .where(Decision.session_id == session_id, Decision.decision_type.in_(types))
        .order_by(Decision.timestamp)
    )
    return list(result.scalars().all())


async def learned(db: AsyncSession, session_id: UUID) -> list[Learned]:
    by_character = await _participants_by_character(db, session_id)
    found_through: dict[tuple[str, str], str] = {}
    for row in await _decisions(db, session_id, "choice"):
        if not row.outcome.get("first_time"):
            continue
        for concept_id in row.outcome.get("gave", []):
            found_through.setdefault(
                (str(row.context.get("participant_id")), str(concept_id)),
                str(row.context.get("opportunity_id")),
            )
    result = await db.execute(
        select(KnowledgeState, Fact)
        .join(Fact, Fact.fact_id == KnowledgeState.fact_id)
        .where(KnowledgeState.session_id == session_id)
        .order_by(KnowledgeState.asserted_at)
    )
    rows: list[Learned] = []
    for state, fact in result.all():
        participant = by_character.get(state.character_id)
        ref = _fact_ref(fact)
        source = None
        if participant is not None and state.source_character_id is None:
            source = found_through.get((str(participant), ref))
        rows.append(
            Learned(
                participant_id=participant,
                character_id=state.character_id,
                fact_type=fact.fact_type,
                fact_ref=ref,
                source_character_id=state.source_character_id,
                source_opportunity_id=source,
                learned_at=_utc(state.asserted_at),
                active=state.superseded_by is None,
            )
        )
    return rows


# --- fact 3: what was chosen from what was offered ------------------------------


@dataclass(frozen=True)
class ChoiceRecord:
    kind: str
    """``choice``, ``ready``, ``menu_shown`` or ``mini_game_submission``."""
    participant_id: UUID | None
    at: datetime
    beat_id: str | None
    detail: dict[str, Any]


async def choices(db: AsyncSession, session_id: UUID) -> list[ChoiceRecord]:
    records: list[ChoiceRecord] = []
    for row in await _decisions(db, session_id, "choice", "ready", "menu_shown"):
        records.append(
            ChoiceRecord(
                kind=row.decision_type,
                participant_id=_uuid(row.context.get("participant_id")),
                at=_utc(row.timestamp),
                beat_id=row.context.get("beat_id"),
                detail={**row.context, **{"outcome": row.outcome}}
                if row.decision_type == "choice"
                else dict(row.context),
            )
        )
    by_character = await _participants_by_character(db, session_id)
    result = await db.execute(
        select(MiniGameSubmission, MiniGameRun)
        .join(MiniGameRun, MiniGameRun.run_id == MiniGameSubmission.run_id)
        .where(MiniGameRun.session_id == session_id)
    )
    for submission, run in result.all():
        records.append(
            ChoiceRecord(
                kind="mini_game_submission",
                participant_id=by_character.get(submission.character_id),
                at=_utc(submission.submitted_at),
                beat_id=(run.definition_snapshot or {}).get("beat_id"),
                detail={
                    "run_id": str(run.run_id),
                    "game_id": run.game_id,
                    "submission_id": submission.submission_id,
                    "accepted": submission.is_accepted,
                    "rejection_reason": submission.rejection_reason,
                },
            )
        )
    return sorted(records, key=lambda record: record.at)


# --- fact 4: what each character said -------------------------------------------


@dataclass(frozen=True)
class Said:
    source: str
    """``claim``, ``dialogue`` or ``player_input``."""
    character_id: UUID | None
    text: str
    beat_id: str | None
    at: datetime


async def said(db: AsyncSession, session_id: UUID) -> list[Said]:
    result = await db.execute(
        select(Event).where(
            Event.session_id == session_id,
            Event.event_type.in_(["dialogue", "player_input"]),
        )
    )
    events = list(result.scalars().all())
    spoken_claims = {
        str(e.payload.get("claim_id"))
        for e in events
        if e.event_type == "dialogue" and e.payload.get("claim_id")
    }
    rows = [
        Said(
            source=e.event_type,
            character_id=e.actor_char_id,
            text=e.content_text or "",
            beat_id=e.payload.get("current_beat_id") or e.payload.get("beat_id"),
            at=_utc(e.timestamp),
        )
        for e in events
        if e.content_text
    ]
    claim_rows = await db.execute(select(Claim).where(Claim.session_id == session_id))
    for claim in claim_rows.scalars().all():
        if str(claim.claim_id) in spoken_claims:
            continue
        rows.append(
            Said(
                source="claim",
                character_id=claim.speaker_character_id,
                text=claim.claim_text,
                beat_id=claim.beat_id,
                at=_utc(claim.created_at),
            )
        )
    return sorted(rows, key=lambda row: row.at)


# --- fact 5: tension against the author's target --------------------------------


@dataclass(frozen=True)
class TensionRow:
    kind: str
    """``update`` (one reading) or ``summary`` (a finished beat)."""
    beat_id: str | None
    score: float | None
    target_score: float | None
    deviation: float | None
    at: datetime


async def tension(db: AsyncSession, session_id: UUID) -> list[TensionRow]:
    result = await db.execute(
        select(Event)
        .where(
            Event.session_id == session_id,
            Event.event_type.in_(["tension_update", "intent_fidelity_summary"]),
        )
        .order_by(Event.timestamp)
    )
    rows: list[TensionRow] = []
    for event in result.scalars().all():
        payload = event.payload
        summary = event.event_type == "intent_fidelity_summary"
        rows.append(
            TensionRow(
                kind="summary" if summary else "update",
                beat_id=payload.get("beat_id"),
                score=payload.get("mean_score" if summary else "score"),
                target_score=payload.get("target_score"),
                deviation=payload.get("mean_abs_deviation") if summary else None,
                at=_utc(event.timestamp),
            )
        )
    return rows


# --- fact 6: cost ---------------------------------------------------------------


async def cost(db: AsyncSession, session_id: UUID) -> CostSummaryData:
    return await get_cost_summary(db, session_id=session_id)


# --- question: where did players stall ------------------------------------------


@dataclass(frozen=True)
class PhaseStall:
    beat_id: str
    phase: str
    entry: int
    entered_at: datetime
    left_at: datetime | None
    active_seconds: float | None
    ended_by: str | None
    not_ready: tuple[UUID, ...]
    """Players who had not marked ready when it ended (or have not yet)."""


async def stalled_phases(db: AsyncSession, session_id: UUID) -> list[PhaseStall]:
    visits = await story_unit_visits(db, session_id)
    humans = await db.execute(
        select(SessionParticipant.participant_id).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.surface_type != "host",
            SessionParticipant.is_ai_controlled.is_(False),
        )
    )
    human_ids = set(humans.scalars().all())
    ready: dict[int, set[UUID]] = {}
    for row in await _decisions(db, session_id, "ready"):
        who = _uuid(row.context.get("participant_id"))
        entry = row.context.get("phase_entry")
        if who is not None and isinstance(entry, int):
            ready.setdefault(entry, set()).add(who)
    return [
        PhaseStall(
            beat_id=v.beat_id,
            phase=v.phase,
            entry=v.entry,
            entered_at=v.entered_at,
            left_at=v.left_at,
            active_seconds=v.active_seconds,
            ended_by=v.left_reason,
            not_ready=tuple(
                sorted(human_ids - ready.get(v.entry, set()), key=str)
                if v.phase in READY_ABLE_PHASES
                else ()
            ),
        )
        for v in visits
    ]


# --- question: what content did nobody see --------------------------------------


@dataclass(frozen=True)
class UnchosenOpportunity:
    opportunity_id: str
    subject_id: str | None
    times_offered: int
    """How many players' menus (one per visit) it was on."""


async def unchosen_opportunities(
    db: AsyncSession, session_id: UUID
) -> list[UnchosenOpportunity]:
    """Opportunities that were on a saved menu and never chosen by anyone. One
    never offered to anyone is not in the record and so is not listed."""
    menus: dict[tuple[str, Any], set[str]] = {}
    subjects: dict[str, str] = {}
    chosen: set[str] = set()
    for row in await _decisions(db, session_id, "choice", "menu_shown"):
        key = (str(row.context.get("participant_id")), row.context.get("phase_entry"))
        menus.setdefault(key, set()).update(
            str(o) for o in row.context.get("offered", [])
        )
        for opportunity_id, pair in (row.context.get("subjects") or {}).items():
            subjects[str(opportunity_id)] = str(pair[0])
        if row.decision_type == "choice":
            chosen.add(str(row.context.get("opportunity_id")))
            if row.context.get("subject_id"):
                subjects[str(row.context["opportunity_id"])] = str(
                    row.context["subject_id"]
                )
    offered: dict[str, int] = {}
    for menu in menus.values():
        for opportunity_id in menu:
            offered[opportunity_id] = offered.get(opportunity_id, 0) + 1
    return [
        UnchosenOpportunity(opportunity_id, subjects.get(opportunity_id), count)
        for opportunity_id, count in sorted(offered.items())
        if opportunity_id not in chosen
    ]


# --- question: which characters drew attention ----------------------------------


@dataclass(frozen=True)
class SubjectAttention:
    subject_id: str | None
    subject_kind: str | None
    choices: int
    participants: int


async def attention_by_subject(
    db: AsyncSession, session_id: UUID
) -> list[SubjectAttention]:
    grouped: dict[tuple[str | None, str | None], list[str]] = {}
    for row in await _decisions(db, session_id, "choice"):
        key = (row.context.get("subject_id"), row.context.get("subject_kind"))
        grouped.setdefault(key, []).append(str(row.context.get("participant_id")))
    rows = [
        SubjectAttention(subject, kind, len(who), len(set(who)))
        for (subject, kind), who in grouped.items()
    ]
    return sorted(rows, key=lambda r: (-r.choices, r.subject_id is None, r.subject_id))


# --- question: was the mini-game reward used ------------------------------------


@dataclass(frozen=True)
class RewardUse:
    participant_id: UUID
    granted: int
    extra_spent: int
    """Investigation points spent beyond the base budget."""
    used: bool


@dataclass(frozen=True)
class RunResult:
    run_id: UUID
    game_id: str
    status: str
    beat_id: str | None
    outcome: dict[str, Any] | None


@dataclass(frozen=True)
class RewardReport:
    grants: list[RewardUse] = field(default_factory=list)
    runs: list[RunResult] = field(default_factory=list)


async def reward_use(db: AsyncSession, session_id: UUID) -> RewardReport:
    """Per participant given extra budget (``budget_grant``): how much, and how
    much they spent past their base allowance; plus each mini-game run's saved
    result, tied to its beat by the run's own beat link when it has one, else by
    the time it started inside a ``mini_game`` phase."""
    grants: dict[UUID, list[tuple[datetime, int]]] = {}
    spends: dict[UUID, list[tuple[datetime, dict[str, Any]]]] = {}
    for row in await _decisions(db, session_id, "budget_grant", "choice"):
        who = _uuid(row.context.get("participant_id"))
        if who is None:
            continue
        when = _utc(row.timestamp)
        if row.decision_type == "budget_grant":
            grants.setdefault(who, []).append((when, int(row.outcome.get("amount", 0))))
        else:
            spends.setdefault(who, []).append((when, row.outcome))
    report: list[RewardUse] = []
    for who, given in grants.items():
        extra = 0
        for when, outcome in spends.get(who, []):
            if "allowance" not in outcome or "spent_after" not in outcome:
                continue
            before = sum(amount for at, amount in given if at <= when)
            base = int(outcome["allowance"]) - before
            extra = max(extra, int(outcome["spent_after"]) - base)
        extra = max(0, extra)
        report.append(
            RewardUse(who, sum(amount for _, amount in given), extra, extra > 0)
        )
    visits = [
        v for v in await story_unit_visits(db, session_id) if v.phase == "mini_game"
    ]
    runs_result = await db.execute(
        select(MiniGameRun)
        .where(MiniGameRun.session_id == session_id)
        .order_by(MiniGameRun.started_at)
    )
    runs: list[RunResult] = []
    for run in runs_result.scalars().all():
        beat = (run.definition_snapshot or {}).get("beat_id")
        if beat is None and run.started_at is not None:
            started = _utc(run.started_at)
            for visit in visits:
                if visit.entered_at <= started and (
                    visit.left_at is None or started <= visit.left_at
                ):
                    beat = visit.beat_id
        runs.append(RunResult(run.run_id, run.game_id, run.status, beat, run.outcome))
    return RewardReport(grants=report, runs=runs)
