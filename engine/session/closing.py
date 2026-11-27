"""The closing sequence: reveal, result and recap (spec 0094, Part J; AW-327).

``enter`` runs once when each of the three phases starts, inside the session
lock and the caller's transaction (events go through the caller's ``Outbox``,
so nothing is sent unless the save succeeds):

  - ``reveal``: tell everyone, for each player, the answer in the one slot the
    case marks shown first. Nothing else from any theory, and no right or wrong.
  - ``result``: work out who solved it and who wins (``endgame.resolve_endgame``),
    save the whole result once, tell everyone the public part and each player
    their own part.
  - ``recap``: count what each player did, choose one written line each by rule
    (``recap.select_lines``), save them, tell everyone.

``closing_view`` is the one read of all of it, for any caller that needs it
after the fact (a route, a screen rebuilding). It shows only what the session
has reached: nothing about right or wrong before the ``result`` phase.

Players are always listed in participant-ID order. It carries no meaning and
never depends on who is right; staging and order for a room belong to the game.
No model is called and no line is written here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition, PhaseKind
from engine.arc.registry import load_arc_definition
from engine.case.authored import AuthoredCase
from engine.db.orm import Decision, Event
from engine.db.orm import Session as OrmSession
from engine.events.models import AudienceTarget, EventCategory
from engine.session import commit_phase, phases, recap
from engine.session.case_seating import cached_arc_case
from engine.session.endgame import EndgameResult, resolve_endgame

REVEAL_EVENT = "theory_reveal"
RESULT_EVENT = "endgame_result"
PRIVATE_RESULT_EVENT = "endgame_result_private"
RECAP_EVENT = "recap_lines"
RESULT_DECISION = "endgame_result"
RECAP_DECISION = "recap_lines"


@dataclass(frozen=True)
class ClosingView:
    """What has been reached so far. A part is None until its phase has been
    entered. ``private`` is the asking player's own part of the result, or None
    when no player asked or the result is not out yet."""

    reveal: dict[str, Any] | None
    result: dict[str, Any] | None
    recap: dict[str, Any] | None
    private: dict[str, Any] | None


async def _case(arc: ArcDefinition) -> AuthoredCase:
    case = await cached_arc_case(arc)
    if case is None:
        raise phases.RoundError("no_written_case", "this game has no written case")
    return case


def _label(case: AuthoredCase, kind: str, value: str) -> str:
    if kind == "cast":
        return next((c.display_name for c in case.cast if c.cast_id == value), value)
    return next((c.label for c in case.concepts if c.concept_id == value), value)


# --- reveal ---------------------------------------------------------------------


async def _reveal_payload(
    db: AsyncSession, session_id: UUID, case: AuthoredCase
) -> dict[str, Any]:
    slot = next(s for s in case.solution if s.shown_first)
    entry = await commit_phase.latest_entry(db, session_id)
    players: list[dict[str, Any]] = []
    for player in sorted(await phases.human_player_ids(db, session_id), key=str):
        theory = (
            await commit_phase.theory_of(db, session_id, player, entry)
            if entry is not None
            else None
        )
        value = (
            theory.answers.get(slot.slot_id)
            if theory is not None and theory.state == "locked"
            else None
        )
        players.append(
            {
                "participant_id": str(player),
                "answer": None
                if not value
                else {"value": value, "label": _label(case, slot.kind, value)},
            }
        )
    return {
        "slot_id": slot.slot_id,
        "slot_label": slot.label,
        "players": players,
    }


# --- result ---------------------------------------------------------------------


def _public_result(case: AuthoredCase, result: EndgameResult) -> dict[str, Any]:
    proofs = {p.participant_id: p.proof for p in result.players}
    concepts = {c.concept_id: c for c in case.concepts}

    def proof_of(player: str) -> dict[str, Any] | None:
        concept = concepts.get(proofs.get(player) or "")
        if concept is None:
            return None
        return {
            "concept_id": concept.concept_id,
            "label": concept.label,
            "text": concept.text,
        }

    return {
        "decided_by": result.decided_by,
        "winners": [
            {"participant_id": w, "proof": proof_of(w)} for w in result.winners
        ],
        "players": [
            {"participant_id": p.participant_id, "solved": p.check.solved}
            for p in result.players
        ],
    }


def _private_results(
    case: AuthoredCase, result: EndgameResult
) -> dict[str, dict[str, Any]]:
    labels = {slot.slot_id: slot.label for slot in case.solution}
    return {
        p.participant_id: {
            "participant_id": p.participant_id,
            "state": p.state,
            "solved": p.check.solved,
            "slots": [
                {"slot_id": slot_id, "label": labels[slot_id], "right": right}
                for slot_id, right in p.check.slots
            ],
        }
        for p in result.players
    }


async def _saved(
    db: AsyncSession, session_id: UUID, decision_type: str, entry: int | None = None
) -> Decision | None:
    result = await db.execute(
        select(Decision).where(
            Decision.session_id == session_id, Decision.decision_type == decision_type
        )
    )
    rows = [
        r
        for r in result.scalars().all()
        if entry is None or r.context.get("phase_entry") == entry
    ]
    if not rows:
        return None
    return max(rows, key=lambda r: r.context.get("phase_entry", 0))


# --- entering a phase -----------------------------------------------------------


async def enter(
    db: AsyncSession,
    arc: ArcDefinition,
    session_id: UUID,
    kind: PhaseKind,
    state: phases.PhaseState,
    now: datetime,
    publish: phases.Publish,
    definition_index: int,
) -> None:
    """Do what ``kind`` does when it starts. Safe to call twice for one visit:
    the second call finds the saved row and does nothing."""
    case = await _case(arc)
    if kind is PhaseKind.reveal:
        await phases.emit(
            publish,
            phases.content_event(
                session_id,
                now,
                category=EventCategory.state_transition,
                event_type=REVEAL_EVENT,
                audience=AudienceTarget.all,
                payload=await _reveal_payload(db, session_id, case),
            ),
        )
    elif kind is PhaseKind.result:
        await _enter_result(db, case, session_id, state, now, publish)
    elif kind is PhaseKind.recap:
        await _enter_recap(
            db, arc, case, session_id, state, now, publish, definition_index
        )


async def _enter_result(
    db: AsyncSession,
    case: AuthoredCase,
    session_id: UUID,
    state: phases.PhaseState,
    now: datetime,
    publish: phases.Publish,
) -> None:
    if await _saved(db, session_id, RESULT_DECISION, state.entry) is not None:
        return
    result = await resolve_endgame(db, session_id, case)
    public = _public_result(case, result)
    private = _private_results(case, result)
    db.add(
        Decision(
            session_id=session_id,
            timestamp=now,
            decision_type=RESULT_DECISION,
            context={"beat_id": state.beat_id, "phase_entry": state.entry},
            outcome={"public": public, "private": private},
        )
    )
    await db.flush()
    await phases.emit(
        publish,
        phases.content_event(
            session_id,
            now,
            category=EventCategory.state_transition,
            event_type=RESULT_EVENT,
            audience=AudienceTarget.all,
            payload=public,
        ),
    )
    for player, part in private.items():
        await phases.emit(
            publish,
            phases.content_event(
                session_id,
                now,
                category=EventCategory.private_delivery,
                event_type=PRIVATE_RESULT_EVENT,
                audience=AudienceTarget.specific_player,
                target_player_id=UUID(player),
                payload=part,
            ),
        )


async def _enter_recap(
    db: AsyncSession,
    arc: ArcDefinition,
    case: AuthoredCase,
    session_id: UUID,
    state: phases.PhaseState,
    now: datetime,
    publish: phases.Publish,
    definition_index: int,
) -> None:
    if await _saved(db, session_id, RECAP_DECISION, state.entry) is not None:
        return
    saved = await _saved(db, session_id, RESULT_DECISION)
    if saved is None:
        raise phases.RoundError("no_result", "the result has not been worked out")
    config = next(beat for beat in arc.beats if beat.beat_id == state.beat_id).phases
    assert config is not None
    recap_config = config[definition_index].recap
    assert recap_config is not None
    private: dict[str, dict[str, Any]] = saved.outcome["private"]
    humans = sorted(await phases.human_player_ids(db, session_id), key=str)
    measures = await recap.measure_players(
        db,
        session_id,
        humans,
        {
            player: sum(1 for slot in part["slots"] if slot["right"])
            for player, part in private.items()
        },
    )
    chosen = recap.select_lines(recap_config, measures, [str(p) for p in humans])
    lines = [
        {"participant_id": c.participant_id, "text": c.text, "hints": c.hints}
        for c in chosen
    ]
    db.add(
        Decision(
            session_id=session_id,
            timestamp=now,
            decision_type=RECAP_DECISION,
            context={"beat_id": state.beat_id, "phase_entry": state.entry},
            outcome={
                "lines": lines,
                "measures": measures,
                "fallback": {c.participant_id: c.fallback for c in chosen},
            },
        )
    )
    await db.flush()
    await phases.emit(
        publish,
        phases.content_event(
            session_id,
            now,
            category=EventCategory.narrative,
            event_type=RECAP_EVENT,
            audience=AudienceTarget.all,
            payload={"lines": lines},
        ),
    )


# --- reading it back ------------------------------------------------------------


async def _entered(db: AsyncSession, session_id: UUID) -> set[str]:
    result = await db.execute(
        select(Event.payload).where(
            Event.session_id == session_id, Event.event_type == phases.PHASE_EVENT
        )
    )
    payloads: list[dict[str, Any]] = list(result.scalars().all())
    return {str(payload["phase"]) for payload in payloads}


async def closing_view(
    db: AsyncSession, session_id: UUID, participant_id: UUID | None = None
) -> ClosingView:
    """Everything the session has reached of the closing sequence, rebuilt from
    saved rows. Before the ``result`` phase it holds no right or wrong. The
    private part is returned only for ``participant_id`` and only that player's."""
    orm = await db.get(OrmSession, session_id)
    if orm is None:
        raise phases.RoundError("session_not_found")
    arc = load_arc_definition(orm.arc_id)
    if arc is None or not arc.is_phased:
        raise phases.RoundError("not_phased", "this game does not run by phases")
    if not arc.case_file:
        raise phases.RoundError("no_written_case", "this game has no written case")
    reached = await _entered(db, session_id)
    if participant_id is not None and participant_id not in set(
        await phases.human_player_ids(db, session_id)
    ):
        raise phases.RoundError("not_a_participant")
    reveal = (
        await _reveal_payload(db, session_id, await _case(arc))
        if PhaseKind.reveal.value in reached
        else None
    )
    result_row = (
        await _saved(db, session_id, RESULT_DECISION)
        if PhaseKind.result.value in reached
        else None
    )
    recap_row = (
        await _saved(db, session_id, RECAP_DECISION)
        if PhaseKind.recap.value in reached
        else None
    )
    private = None
    if result_row is not None and participant_id is not None:
        private = result_row.outcome["private"].get(str(participant_id))
    return ClosingView(
        reveal=reveal,
        result=result_row.outcome["public"] if result_row is not None else None,
        recap={"lines": recap_row.outcome["lines"]} if recap_row is not None else None,
        private=private,
    )
