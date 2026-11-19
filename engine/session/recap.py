"""What each player did, and the one written line each earns (spec 0094, Part J).

``measure_players`` counts a fixed set of things the engine saw happen, from
saved rows only: nothing is held in memory, so a restart gives the same values.
``select_lines`` is a pure function: for each player, in the order given, the
first line whose condition holds and that no other player has been given, else
a fallback. No model is called and no line is written here; the lines come from
the arc file. A line can only be chosen by a measure, so none can claim what a
player thought.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import RecapCondition, RecapConfig
from engine.db.orm import Decision
from engine.session import choices, commit_phase
from engine.session.endgame import finished_standings
from engine.session.phases import READY_DECISION
from engine.session.winner import run_winners

Measures = dict[str, int]


@dataclass(frozen=True)
class ChosenLine:
    participant_id: str
    text: str
    hints: dict[str, Any]
    fallback: bool
    index: int
    """Position in the arc's list of lines, or of fallbacks when ``fallback``."""


async def _rows(db: AsyncSession, session_id: UUID, *types: str) -> list[Decision]:
    result = await db.execute(
        select(Decision).where(
            Decision.session_id == session_id, Decision.decision_type.in_(types)
        )
    )
    return list(result.scalars().all())


def _last_to_ready(ready: list[Decision], humans: set[str]) -> Counter[str]:
    """For each phase visit every player marked ready in, the player whose mark
    came last. A tie for last counts for nobody."""
    by_entry: dict[Any, dict[str, Any]] = {}
    for row in ready:
        player = str(row.context.get("participant_id"))
        entry = row.context.get("phase_entry")
        marks = by_entry.setdefault(entry, {})
        if player not in marks or row.timestamp < marks[player]:
            marks[player] = row.timestamp
    counts: Counter[str] = Counter()
    for marks in by_entry.values():
        if set(marks) < humans:
            continue
        latest = max(marks.values())
        last = [player for player, at in marks.items() if at == latest]
        if len(last) == 1:
            counts[last[0]] += 1
    return counts


async def measure_players(
    db: AsyncSession,
    session_id: UUID,
    players: Sequence[UUID],
    slots_right: Mapping[str, int],
) -> dict[str, Measures]:
    """The measures for each player, keyed by participant ID. ``slots_right``
    comes from the saved result."""
    humans = {str(p) for p in players}
    choice_rows = await _rows(db, session_id, choices.CHOICE_DECISION)
    ready = await _rows(db, session_id, READY_DECISION)
    last = _last_to_ready(ready, humans)
    standings = await finished_standings(db, session_id)
    entry = await commit_phase.latest_entry(db, session_id)
    theory_rows = await _rows(
        db, session_id, commit_phase.THEORY_DRAFT, commit_phase.THEORY_LOCK
    )
    measures: dict[str, Measures] = {}
    for player in sorted(humans):
        mine = [r for r in choice_rows if r.context.get("participant_id") == player]
        per_subject = Counter(
            str(r.context["subject_id"]) for r in mine if r.context.get("subject_id")
        )
        drafts = [
            r
            for r in theory_rows
            if r.decision_type == commit_phase.THEORY_DRAFT
            and r.context.get("participant_id") == player
            and r.context.get("phase_entry") == entry
        ]
        locks = [
            r
            for r in theory_rows
            if r.decision_type == commit_phase.THEORY_LOCK
            and r.context.get("participant_id") == player
            and r.context.get("phase_entry") == entry
        ]
        measures[player] = {
            "investigations_used": sum(int(r.outcome.get("cost", 0)) for r in mine),
            "investigations_left": await choices.remaining_budget(
                db, session_id, UUID(player)
            ),
            "subjects_looked_into": len(per_subject),
            "most_returns_to_one_subject": max(per_subject.values(), default=0),
            "reviews": sum(1 for r in mine if not r.outcome.get("first_time")),
            "times_last_to_ready": last[player],
            "mini_games_won": sum(1 for s in standings if player in run_winners(s)),
            "draft_changes": max(0, len(drafts) - 1),
            "locked_in_time": int(
                any(
                    r.outcome.get("state") == "locked"
                    and r.outcome.get("locked_by") == "player"
                    for r in locks
                )
            ),
            "slots_right": int(slots_right.get(player, 0)),
        }
    return measures


def _holds(
    condition: RecapCondition, player: str, measures: Mapping[str, Mapping[str, int]]
) -> bool:
    value = measures[player][condition.measure]
    room = [m[condition.measure] for m in measures.values()]
    if condition.compare == "highest":
        return value == max(room) and max(room) > min(room)
    if condition.compare == "lowest":
        return value == min(room) and max(room) > min(room)
    assert condition.value is not None
    if condition.compare == "equals":
        return value == condition.value
    if condition.compare == "at_least":
        return value >= condition.value
    return value <= condition.value


def select_lines(
    config: RecapConfig,
    measures: Mapping[str, Mapping[str, int]],
    order: Sequence[str],
) -> list[ChosenLine]:
    """One line per player in ``order``. A line goes to the first player it
    fits and to nobody else. A player no line fits takes an unused fallback; a
    fallback repeats only when every fallback has been given."""
    taken: set[int] = set()
    fallbacks_given = 0
    chosen: list[ChosenLine] = []
    for player in order:
        pick = next(
            (
                i
                for i, line in enumerate(config.lines)
                if i not in taken and _holds(line.when, player, measures)
            ),
            None,
        )
        if pick is not None:
            taken.add(pick)
            line = config.lines[pick]
            chosen.append(
                ChosenLine(player, line.text, line.hints.model_dump(), False, pick)
            )
            continue
        index = fallbacks_given % len(config.fallbacks)
        fallbacks_given += 1
        line = config.fallbacks[index]
        chosen.append(
            ChosenLine(player, line.text, line.hints.model_dump(), True, index)
        )
    return chosen
