"""A whole game from join to the last recap line, headless (AW-327).

Spec 0094, "Whole game". Opening, three rounds with real investigations and a
real mini-game run each, Last Call, the reveal, the written truth, the result
and the recap, all by rule. No model is called anywhere (the ``no_model_calls``
fixture fails the test if one is). Time is passed in.

Everything is made up: the case is ``fixtures/authored_case/valid_case.json``
and the recap lines are ``rounds_support.FIXTURE_RECAP``.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Callable
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.arc.models import ArcDefinition
from engine.db.testing import make_sqlite_session_factory
from engine.events.models import AudienceTarget
from engine.session import closing
from engine.session.endgame import finished_standings
from engine.session.phases import (
    lock_theory,
    mark_ready,
    round_view,
    save_theory_draft,
    tick,
)
from engine.session.winner import decide_winners
from engine.tests.rounds_support import (
    BEATS,
    VALID_CASE,
    Recorder,
    Seated,
    at,
    closing_arc,
    seat_session,
    where,
)
from engine.tests.test_spine_headless import entered_once, phase_order, play_a_round

RIGHT = {"slot_who": "marlowe", "slot_how": "c_how_true"}
WRONG = {"slot_who": "pinecone", "slot_how": "c_how_false1"}
CLOSING_ORDER = [
    ("finale", "commit"),
    ("finale", "reveal"),
    ("truth", "scene"),
    ("verdict", "result"),
    ("verdict", "recap"),
]
VERDICT_KEYS = {"solved", "right", "winners", "decided_by", "slots"}
# Who gets the right theory in each branch (by seat). Everyone else gets WRONG.
BRANCHES = {
    "one_winner": {0},
    "tie_break": {0, 1},
    "nobody_solves": set(),
}


@pytest_asyncio.fixture()
async def factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine, session_factory = await make_sqlite_session_factory()
    try:
        yield session_factory
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def db(
    factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


def keys_of(value: Any) -> set[str]:
    if isinstance(value, dict):
        found = set(value)
        for item in value.values():
            found |= keys_of(item)
        return found
    if isinstance(value, list):
        return set().union(*(keys_of(item) for item in value)) if value else set()
    return set()


async def play_to_last_call(db: AsyncSession, seated: Seated, rec: Recorder) -> float:
    """Join to the start of Last Call: the opening and the three rounds, played.
    Returns the time Last Call began."""
    now = 0.0
    await tick(db, seated.session_id, at(now), rec)
    for participant in seated.participants:
        await mark_ready(db, seated.session_id, participant, at(now), rec)
    for participant in seated.participants:
        await mark_ready(db, seated.session_id, participant, at(now), rec)
    for beat in BEATS[1:4]:
        assert (await where(db, seated.session_id))[:2] == (beat, "scene")
        now = await play_a_round(db, seated, rec, beat, now + 1)
    assert await where(db, seated.session_id) == ("finale", "commit", "running")
    return now


async def everyone_ready(
    db: AsyncSession, seated: Seated, rec: Recorder, now: float
) -> None:
    for participant in seated.participants:
        await mark_ready(db, seated.session_id, participant, at(now), rec)


def sorted_ids(seated: Seated) -> list[str]:
    return sorted(str(p) for p in seated.participants)


@pytest.mark.asyncio
@pytest.mark.parametrize("branch", list(BRANCHES))
@pytest.mark.parametrize("players", [2, 4])
async def test_full_game_join_to_recap(
    db: AsyncSession,
    factory: async_sessionmaker[AsyncSession],
    registered: Callable[[ArcDefinition], None],
    no_model_calls: None,
    players: int,
    branch: str,
) -> None:
    arc = closing_arc()
    registered(arc)
    seated = await seat_session(db, arc, players=players)
    rec = Recorder()
    now = await play_to_last_call(db, seated, rec)

    # Last Call: each player saves a theory and locks it.
    solvers = {str(seated.participants[i]) for i in BRANCHES[branch]}
    now += 5
    for seat, participant in enumerate(seated.participants):
        theory = RIGHT if seat in BRANCHES[branch] else WRONG
        await save_theory_draft(
            db, seated.session_id, participant, theory, "c_how_true", at(now), rec
        )
        await lock_theory(db, seated.session_id, participant, at(now), rec)
    # The last lock ended Last Call; the room is at the reveal.
    assert await where(db, seated.session_id) == ("finale", "reveal", "running")

    # Nothing told to anyone before the result holds right or wrong.
    assert not rec.of_type("endgame_result")
    for event in rec.events:
        assert not keys_of(event.payload) & VERDICT_KEYS, event.event_type

    reveal = rec.of_type("theory_reveal")
    assert len(reveal) == 1 and reveal[0].target_audience is AudienceTarget.all
    shown = reveal[0].payload
    assert set(shown) == {"slot_id", "slot_label", "players"}
    assert [p["participant_id"] for p in shown["players"]] == sorted_ids(seated)
    for entry in shown["players"]:
        expected = "marlowe" if entry["participant_id"] in solvers else "pinecone"
        assert entry["answer"]["value"] == expected
    assert "c_how_true" not in json.dumps(shown)

    # The room moves on: reveal, the written truth, the result, the recap.
    now += 1
    await everyone_ready(db, seated, rec, now)
    assert (await where(db, seated.session_id))[:2] == ("truth", "scene")
    truth = [e for e in rec.of_type("phase_line") if e.payload["beat_id"] == "truth"]
    written = json.loads(VALID_CASE.read_text("utf-8"))["closing"]
    assert [e.payload["text"] for e in truth] == written

    now += 1
    await everyone_ready(db, seated, rec, now)
    assert (await where(db, seated.session_id))[:2] == ("verdict", "result")
    public = rec.of_type("endgame_result")
    assert len(public) == 1 and public[0].target_audience is AudienceTarget.all
    outcome = public[0].payload
    winners = [w["participant_id"] for w in outcome["winners"]]
    if branch == "one_winner":
        assert winners == sorted(solvers) and outcome["decided_by"] == "only_solver"
    elif branch == "nobody_solves":
        assert winners == [] and outcome["decided_by"] == "no_solver"
    else:
        standings = await finished_standings(db, seated.session_id)
        expected_rule = decide_winners(solvers, standings)
        assert tuple(winners) == expected_rule.winners
        assert outcome["decided_by"] == expected_rule.decided_by
        assert outcome["decided_by"] in {
            "mini_game_wins",
            "mini_game_placings",
            "shared",
        }
        assert winners and set(winners) <= solvers
    assert {p["participant_id"] for p in outcome["players"] if p["solved"]} == solvers
    assert all(w["proof"]["concept_id"] == "c_how_true" for w in outcome["winners"])
    for participant in seated.participants:
        mine = [
            e
            for e in rec.of_type("endgame_result_private")
            if e.target_player_id == participant
        ]
        assert len(mine) == 1
        assert mine[0].target_audience is AudienceTarget.specific_player
        assert mine[0].payload["solved"] == (str(participant) in solvers)
    assert len(rec.of_type("endgame_result_private")) == players

    now += 1
    await everyone_ready(db, seated, rec, now)
    assert (await where(db, seated.session_id))[:2] == ("verdict", "recap")
    recap = rec.of_type("recap_lines")
    assert len(recap) == 1 and recap[0].target_audience is AudienceTarget.all
    lines = recap[0].payload["lines"]
    assert [line["participant_id"] for line in lines] == sorted_ids(seated)
    assert lines[0]["text"] == "Spent every last investigation."
    texts = [line["text"] for line in lines]
    fallbacks = {"Played a quiet game.", "Kept to the edges."}
    assert len({t for t in texts if t not in fallbacks}) == len(
        [t for t in texts if t not in fallbacks]
    )

    # The last recap line is the end: the game holds there.
    now += 1
    await everyone_ready(db, seated, rec, now)
    assert await where(db, seated.session_id) == ("verdict", "recap", "ended")

    # Every beat and phase, in order, from join to the last recap.
    order = entered_once(await phase_order(db, seated.session_id))
    assert order[-len(CLOSING_ORDER) :] == CLOSING_ORDER
    assert [b for b, p in order if p in ("scene", "bridge")][0] == "opening"

    # A fresh connection to the same database reads back the same sequence.
    async with factory() as fresh:
        view = await closing.closing_view(fresh, seated.session_id)
    assert view.result == outcome
    assert view.recap == {"lines": lines}
    assert view.reveal == shown


@pytest.mark.asyncio
@pytest.mark.parametrize("players", [2, 4])
async def test_a_game_where_nobody_does_anything_ends_on_clocks_alone(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    no_model_calls: None,
    players: int,
) -> None:
    arc = closing_arc()
    registered(arc)
    seated = await seat_session(db, arc, players=players)
    rec = Recorder()
    now = 0.0
    await tick(db, seated.session_id, at(now), rec)
    for _ in range(40):
        if (await where(db, seated.session_id))[2] == "ended":
            break
        view = await round_view(db, seated.session_id, at(now))
        assert view.seconds_left is not None
        now += view.seconds_left
        await tick(db, seated.session_id, at(now), rec)
    assert await where(db, seated.session_id) == ("verdict", "recap", "ended")
    order = entered_once(await phase_order(db, seated.session_id))
    assert order[-len(CLOSING_ORDER) :] == CLOSING_ORDER

    outcome = rec.of_type("endgame_result")[0].payload
    assert outcome["winners"] == [] and outcome["decided_by"] == "no_solver"
    assert not any(p["solved"] for p in outcome["players"])
    reveal = rec.of_type("theory_reveal")[0].payload
    assert all(p["answer"] is None for p in reveal["players"])
    lines = rec.of_type("recap_lines")[0].payload["lines"]
    assert len(lines) == players
    private = rec.of_type("endgame_result_private")
    assert {e.payload["state"] for e in private} == {"no_theory"}
