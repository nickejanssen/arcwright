"""Working out the result after Last Call (AW-326, spec 0094 Parts H and I).

Runs a real commit phase on the fixture arc and case, then calls
``resolve_endgame``. Mini-game standings are saved as finished runs. The
``result`` phase that will save and send this result is AW-327. No model is
called (``no_model_calls`` fails the test if one is).
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.case.authored import AuthoredCase
from engine.db.orm import MiniGameRun
from engine.db.testing import make_sqlite_session_factory
from engine.session.case_seating import cached_arc_case
from engine.session.commit_phase import CommitRefusal
from engine.session.endgame import EndgameResult, resolve_endgame
from engine.session.phases import tick
from engine.tests.rounds_support import Recorder, Seated, at, seat_session
from engine.tests.test_commit_phase import (
    DEADLINE,
    RIGHT,
    at_commit,
    commit_arc,
    draft,
    grant,
    lock,
)

WRONG = {"slot_who": "pinecone", "slot_how": "c_how_false1"}


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine, factory = await make_sqlite_session_factory()
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
    await engine.dispose()


async def the_case() -> AuthoredCase:
    case = await cached_arc_case(commit_arc())
    assert case is not None
    return case


async def player_locks(
    db: AsyncSession, seated: Seated, who: int, answers: dict[str, str]
) -> None:
    await grant(db, seated, who, answers["slot_how"])
    await draft(db, seated, who, answers)
    await lock(db, seated, who)


async def add_run(
    db: AsyncSession,
    seated: Seated,
    tiers: list[list[int]],
    status: str = "completed",
) -> None:
    db.add(
        MiniGameRun(
            session_id=seated.session_id,
            game_id="made-up",
            definition_version="1",
            definition_snapshot={},
            status=status,
            outcome={
                "standing": [[str(seated.participants[i]) for i in t] for t in tiers]
            },
        )
    )
    await db.flush()


def who_won(seated: Seated, result: EndgameResult) -> list[int]:
    return sorted(seated.participants.index(UUID(w)) for w in result.winners)


class TestResults:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("players", [2, 4])
    async def test_one_solver_wins(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
        players: int,
    ) -> None:
        seated, _ = await at_commit(db, registered, players=players)
        await player_locks(db, seated, 0, RIGHT)
        for who in range(1, players):
            await player_locks(db, seated, who, WRONG)
        result = await resolve_endgame(db, seated.session_id, await the_case())
        assert who_won(seated, result) == [0]
        assert result.decided_by == "only_solver"
        assert len(result.solvers) == 1
        mine = {p.participant_id: p for p in result.players}[
            str(seated.participants[1])
        ]
        assert not mine.check.solved
        assert dict(mine.check.slots) == {"slot_who": False, "slot_how": False}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("players", [2, 4])
    async def test_nobody_solved_it_so_nobody_wins(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
        players: int,
    ) -> None:
        seated, _ = await at_commit(db, registered, players=players)
        for who in range(players):
            await player_locks(db, seated, who, WRONG)
        result = await resolve_endgame(db, seated.session_id, await the_case())
        assert (result.winners, result.decided_by) == ((), "no_solver")

    @pytest.mark.asyncio
    async def test_several_solvers_are_split_by_mini_games_won(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, _ = await at_commit(db, registered, players=4)
        for who in (0, 1):
            await player_locks(db, seated, who, RIGHT)
        for who in (2, 3):
            await player_locks(db, seated, who, WRONG)
        await add_run(db, seated, [[1], [0, 2, 3]])
        await add_run(db, seated, [[1], [2], [0, 3]])
        await add_run(db, seated, [[0], [1, 2, 3]])
        result = await resolve_endgame(db, seated.session_id, await the_case())
        assert who_won(seated, result) == [1]
        assert result.decided_by == "mini_game_wins"

    @pytest.mark.asyncio
    async def test_level_on_wins_is_split_by_placings_then_shared(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, _ = await at_commit(db, registered, players=3)
        for who in (0, 1):
            await player_locks(db, seated, who, RIGHT)
        await player_locks(db, seated, 2, WRONG)
        await add_run(db, seated, [[0], [1], [2]])
        await add_run(db, seated, [[1], [2], [0]])
        await add_run(db, seated, [[2], [0], [1]])
        # Wins: 1 each. Placings: player 0 is 1+3+2, player 1 is 2+1+3: level.
        shared = await resolve_endgame(db, seated.session_id, await the_case())
        assert (who_won(seated, shared), shared.decided_by) == ([0, 1], "shared")
        await add_run(db, seated, [[2], [0], [1]])
        closer = await resolve_endgame(db, seated.session_id, await the_case())
        assert (who_won(seated, closer), closer.decided_by) == (
            [0],
            "mini_game_placings",
        )

    @pytest.mark.asyncio
    async def test_a_cancelled_run_counts_for_nothing(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, _ = await at_commit(db, registered, players=2)
        for who in (0, 1):
            await player_locks(db, seated, who, RIGHT)
        await add_run(db, seated, [[1], [0]], status="cancelled")
        result = await resolve_endgame(db, seated.session_id, await the_case())
        assert (who_won(seated, result), result.decided_by) == ([0, 1], "shared")

    @pytest.mark.asyncio
    async def test_a_draft_locked_by_the_clock_still_solves_it(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, _ = await at_commit(db, registered, players=2)
        await grant(db, seated, 0, "c_how_true")
        await draft(db, seated, 0, RIGHT)
        await tick(db, seated.session_id, at(DEADLINE), Recorder())
        result = await resolve_endgame(db, seated.session_id, await the_case())
        assert who_won(seated, result) == [0]
        states = {p.participant_id: p.state for p in result.players}
        assert states[str(seated.participants[0])] == "locked"
        assert states[str(seated.participants[1])] == "no_theory"

    @pytest.mark.asyncio
    async def test_nobody_doing_anything_ends_with_no_winner(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, _ = await at_commit(db, registered, players=4)
        await tick(db, seated.session_id, at(DEADLINE), Recorder())
        result = await resolve_endgame(db, seated.session_id, await the_case())
        assert (result.winners, result.decided_by) == ((), "no_solver")
        assert {p.state for p in result.players} == {"no_theory"}

    @pytest.mark.asyncio
    async def test_the_result_is_the_same_when_worked_out_again(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, _ = await at_commit(db, registered, players=3)
        await player_locks(db, seated, 0, RIGHT)
        await player_locks(db, seated, 1, RIGHT)
        await tick(db, seated.session_id, at(DEADLINE), Recorder())
        await add_run(db, seated, [[1], [0, 2]])
        first = await resolve_endgame(db, seated.session_id, await the_case())
        assert first == await resolve_endgame(db, seated.session_id, await the_case())


class TestNothingBeforeEveryoneHasLocked:
    @pytest.mark.asyncio
    async def test_it_refuses_while_theories_are_still_being_built(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered, players=2)
        await player_locks(db, seated, 0, RIGHT)
        with pytest.raises(CommitRefusal) as refused:
            await resolve_endgame(db, seated.session_id, await the_case())
        assert refused.value.code == "commit_not_finished"

    @pytest.mark.asyncio
    async def test_it_refuses_when_no_commit_phase_was_played(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        arc = commit_arc()
        registered(arc)
        seated = await seat_session(db, arc, players=2)
        await tick(db, seated.session_id, at(0), Recorder())
        with pytest.raises(CommitRefusal) as refused:
            await resolve_endgame(db, seated.session_id, await the_case())
        assert refused.value.code == "no_theories"
