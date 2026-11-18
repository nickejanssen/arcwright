"""Every finished mini-game run saves a standing (AW-328; spec 0094, Part I).

A standing is the players in order, best first, ties sharing a tier, each
eligible player named once. It is one key in the run's saved outcome.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.db.testing import make_sqlite_session_factory
from engine.mini_games.plugins._evidence_locker_breach import (
    EvidenceLockerBreachPlugin,
)
from engine.mini_games.plugins._evidence_search_race import EvidenceSearchRacePlugin
from engine.mini_games.plugins._match_3_clue_race import Match3ClueRacePlugin
from engine.mini_games.plugins._social_truth_bluff import SocialTruthBluffPlugin
from engine.mini_games.runtime import build_standing
from engine.session.phases import tick
from engine.tests.mini_game_reward_support import (
    AFTER_DEADLINE,
    RankedPlugin,
    in_mini_game,
    place_players,
    reward_arc,
    the_run,
)
from engine.tests.rounds_support import at


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine, factory = await make_sqlite_session_factory()
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
    await engine.dispose()


NO_SNAPSHOT: Any = None  # the games under test read none of it


def pairs(count: int) -> list[tuple[UUID, UUID]]:
    return [(uuid4(), uuid4()) for _ in range(count)]


class TestTheRuntimeBuildsIt:
    def test_a_game_with_no_ranking_ties_everyone(self) -> None:
        eligible = pairs(3)
        standing = build_standing(
            Match3ClueRacePlugin(),
            None,
            [],
            {},
            eligible,
        )
        assert len(standing) == 1
        assert sorted(standing[0]) == sorted(str(p) for _, p in eligible)

    def test_both_stub_games_take_the_same_default(self) -> None:
        eligible = pairs(2)
        for plugin in (Match3ClueRacePlugin(), EvidenceLockerBreachPlugin()):
            standing = build_standing(plugin, NO_SNAPSHOT, [], {}, eligible)
            assert [len(tier) for tier in standing] == [2]

    def test_a_ranked_game_keeps_its_order_and_ties_and_adds_the_unnamed_last(
        self,
    ) -> None:
        a, b, c, d = pairs(4)

        class Fixed:
            def standing(self, *_: object) -> list[list[str]]:
                return [[str(a[0])], [str(b[0]), str(c[0])]]

        standing = build_standing(Fixed(), NO_SNAPSHOT, [], {}, [a, b, c, d])
        assert standing == [
            [str(a[1])],
            sorted([str(b[1]), str(c[1])]),
            [str(d[1])],
        ]

    def test_a_name_that_is_not_eligible_or_is_repeated_is_ignored(self) -> None:
        a, b = pairs(2)

        class Messy:
            def standing(self, *_: object) -> list[list[str]]:
                return [[str(a[0]), str(a[0]), str(uuid4())], []]

        standing = build_standing(Messy(), NO_SNAPSHOT, [], {}, [a, b])
        assert standing == [[str(a[1])], [str(b[1])]]

    def test_no_eligible_players_gives_an_empty_standing(self) -> None:
        assert build_standing(RankedPlugin(), NO_SNAPSHOT, [], {}, []) == []


class TestTheRealGames:
    def test_the_search_race_puts_the_finder_alone_first(self) -> None:
        finder = str(uuid4())
        out = {"finder-character-id": finder, "real-object-claimed": True}
        assert EvidenceSearchRacePlugin().standing(NO_SNAPSHOT, [], out) == [[finder]]

    def test_the_search_race_names_no_one_when_the_real_object_was_not_found(
        self,
    ) -> None:
        out = {"finder-character-id": None, "real-object-claimed": False}
        assert EvidenceSearchRacePlugin().standing(NO_SNAPSHOT, [], out) == []

    def test_truth_bluff_ranks_by_score_and_keeps_ties(self) -> None:
        a, b, c = (str(uuid4()) for _ in range(3))
        out = {"scores": {a: 2, b: 5, c: 2}}
        tiers = SocialTruthBluffPlugin().standing(NO_SNAPSHOT, [], out)
        assert tiers[0] == [b]
        assert sorted(tiers[1]) == sorted([a, c])
        assert len(tiers) == 2

    def test_a_standing_names_each_eligible_player_once_for_every_real_game(
        self,
    ) -> None:
        eligible = pairs(4)
        ids = [str(c) for c, _ in eligible]
        cases: list[tuple[Any, dict[str, Any]]] = [
            (EvidenceSearchRacePlugin(), {"finder-character-id": ids[2]}),
            (EvidenceSearchRacePlugin(), {"finder-character-id": None}),
            (SocialTruthBluffPlugin(), {"scores": {ids[0]: 1, ids[1]: 1}}),
            (SocialTruthBluffPlugin(), {"scores": {}}),
        ]
        for plugin, outcome in cases:
            standing = build_standing(plugin, NO_SNAPSHOT, [], outcome, eligible)
            named = [p for tier in standing for p in tier]
            assert sorted(named) == sorted(str(p) for _, p in eligible)


class TestSavedOnTheRun:
    @pytest.mark.asyncio
    async def test_a_finished_run_saves_the_standing_in_its_outcome(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(None))
        await place_players(db, seated, [2, 1, None])
        await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        run = await the_run(db, seated.session_id)
        assert run.outcome is not None
        p0, p1, p2 = (str(p) for p in seated.participants)
        assert run.outcome["standing"] == [[p1], [p0], [p2]]
        assert run.outcome["submissions"] == 2  # the game's own outcome is kept

    @pytest.mark.asyncio
    async def test_a_cancelled_run_saves_no_standing(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        from engine.session.phases import host_move_on

        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(None))
        await host_move_on(db, seated.session_id, at(110), rec)
        run = await the_run(db, seated.session_id)
        assert run.status == "cancelled"
        assert not (run.outcome or {}).get("standing")
