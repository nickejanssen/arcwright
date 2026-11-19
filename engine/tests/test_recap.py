"""The recap: what each player did, and the one line each earns (AW-327,
spec 0094 Part J).

Line choice is a pure function and is tested on plain numbers. The measures
are tested against a played game and rebuilt from a second connection to the
same database, to show they come from saved rows only. All lines are made up.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest
import pytest_asyncio
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.arc.models import RecapCondition, RecapConfig
from engine.db.testing import make_sqlite_session_factory
from engine.session import recap
from engine.session.phases import lock_theory, save_theory_draft, tick
from engine.tests.rounds_support import (
    FIXTURE_RECAP,
    Recorder,
    at,
    closing_arc,
    seat_session,
)
from engine.tests.test_endgame_headless import RIGHT, WRONG, play_to_last_call

PLAYERS = ("a", "b", "c")


def config(lines: list[dict[str, Any]], fallbacks: int = 1) -> RecapConfig:
    return RecapConfig.model_validate(
        {
            "lines": lines,
            "fallbacks": [{"text": f"fallback {i}"} for i in range(fallbacks)],
        }
    )


def line(text: str, measure: str, compare: str, value: int | None = None) -> dict:
    when: dict[str, Any] = {"measure": measure, "compare": compare}
    if value is not None:
        when["value"] = value
    return {"text": text, "when": when}


def room(**per_player: dict[str, int]) -> dict[str, dict[str, int]]:
    base = {
        "investigations_used": 6,
        "investigations_left": 0,
        "subjects_looked_into": 4,
        "most_returns_to_one_subject": 1,
        "reviews": 0,
        "times_last_to_ready": 0,
        "mini_games_won": 0,
        "draft_changes": 0,
        "locked_in_time": 1,
        "slots_right": 0,
    }
    return {player: {**base, **values} for player, values in per_player.items()}


def texts(chosen: list[recap.ChosenLine]) -> list[str]:
    return [c.text for c in chosen]


class TestConditions:
    @pytest.mark.parametrize(
        ("compare", "value", "expected"),
        [
            ("equals", 3, ["hit", "fallback 0", "fallback 0"]),
            ("at_least", 3, ["hit", "fallback 0", "fallback 0"]),
            ("at_most", 1, ["fallback 0", "hit", "fallback 0"]),
        ],
    )
    def test_each_comparison_holds_for_the_right_players(
        self, compare: str, value: int, expected: list[str]
    ) -> None:
        measures = room(a={"reviews": 3}, b={"reviews": 1}, c={"reviews": 2})
        cfg = config([line("hit", "reviews", compare, value)])
        assert texts(recap.select_lines(cfg, measures, list(PLAYERS))) == expected

    def test_highest_and_lowest_name_the_extremes_of_the_room(self) -> None:
        measures = room(
            a={"mini_games_won": 2}, b={"mini_games_won": 0}, c={"mini_games_won": 1}
        )
        cfg = config(
            [
                line("top", "mini_games_won", "highest"),
                line("bottom", "mini_games_won", "lowest"),
            ]
        )
        chosen = recap.select_lines(cfg, measures, list(PLAYERS))
        assert texts(chosen) == ["top", "bottom", "fallback 0"]

    def test_nobody_is_highest_or_lowest_in_a_level_room(self) -> None:
        measures = room(a={}, b={}, c={})
        cfg = config(
            [
                line("top", "mini_games_won", "highest"),
                line("bottom", "mini_games_won", "lowest"),
            ]
        )
        chosen = recap.select_lines(cfg, measures, list(PLAYERS))
        assert all(c.fallback for c in chosen)

    def test_a_comparison_that_needs_a_value_refuses_without_one(self) -> None:
        with pytest.raises(ValidationError):
            RecapCondition(measure="reviews", compare="equals")
        with pytest.raises(ValidationError):
            RecapCondition(measure="reviews", compare="highest", value=2)

    def test_a_condition_can_only_name_something_the_engine_counts(self) -> None:
        with pytest.raises(ValidationError):
            RecapCondition.model_validate(
                {"measure": "felt_guilty", "compare": "highest"}
            )


class TestChoosing:
    def test_no_two_players_get_the_same_line(self) -> None:
        measures = room(a={"reviews": 2}, b={"reviews": 2}, c={"reviews": 2})
        cfg = config(
            [
                line("first", "reviews", "at_least", 1),
                line("second", "reviews", "at_least", 2),
            ]
        )
        chosen = recap.select_lines(cfg, measures, list(PLAYERS))
        assert texts(chosen) == ["first", "second", "fallback 0"]

    def test_the_first_line_that_holds_wins_in_the_authored_order(self) -> None:
        measures = room(a={"reviews": 5})
        cfg = config(
            [
                line("never reviewed", "reviews", "equals", 0),
                line("reviewed a lot", "reviews", "at_least", 3),
                line("reviewed", "reviews", "at_least", 1),
            ]
        )
        assert texts(recap.select_lines(cfg, measures, ["a"])) == ["reviewed a lot"]

    def test_a_player_no_line_fits_gets_a_fallback_and_marks_it(self) -> None:
        measures = room(a={})
        chosen = recap.select_lines(
            config([line("never", "reviews", "at_least", 9)]), measures, ["a"]
        )
        assert [(c.text, c.fallback) for c in chosen] == [("fallback 0", True)]

    def test_unused_fallbacks_go_first_and_repeat_only_when_they_run_out(self) -> None:
        measures = room(a={}, b={}, c={})
        chosen = recap.select_lines(config([], fallbacks=2), measures, list(PLAYERS))
        assert texts(chosen) == ["fallback 0", "fallback 1", "fallback 0"]

    def test_the_same_inputs_give_the_same_lines(self) -> None:
        measures = room(a={"reviews": 2}, b={"reviews": 1}, c={})
        cfg = RecapConfig.model_validate(FIXTURE_RECAP)
        first = recap.select_lines(cfg, measures, list(PLAYERS))
        assert recap.select_lines(cfg, measures, list(PLAYERS)) == first

    def test_a_recap_with_no_fallback_is_refused(self) -> None:
        with pytest.raises(ValidationError):
            RecapConfig.model_validate({"lines": [], "fallbacks": []})


class TestLastToReady:
    def rows(self, marks: list[tuple[int, str, int]]) -> list[Any]:
        start = datetime(2026, 12, 12, tzinfo=timezone.utc)
        return [
            SimpleNamespace(
                context={"participant_id": player, "phase_entry": entry},
                timestamp=start + timedelta(seconds=second),
            )
            for entry, player, second in marks
        ]

    def test_the_latest_mark_in_a_visit_everyone_marked_counts(self) -> None:
        rows = self.rows([(1, "a", 1), (1, "b", 5), (2, "a", 9), (2, "b", 3)])
        counts = recap._last_to_ready(rows, {"a", "b"})
        assert dict(counts) == {"b": 1, "a": 1}

    def test_a_visit_not_everyone_marked_counts_for_nobody(self) -> None:
        rows = self.rows([(1, "a", 1), (1, "b", 5)])
        assert not recap._last_to_ready(rows, {"a", "b", "c"})

    def test_a_tie_for_last_counts_for_nobody(self) -> None:
        rows = self.rows([(1, "a", 4), (1, "b", 4)])
        assert not recap._last_to_ready(rows, {"a", "b"})


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


class TestMeasuresFromSavedRows:
    @pytest.mark.asyncio
    async def test_each_measure_matches_what_was_played_and_survives_a_restart(
        self,
        db: AsyncSession,
        factory: async_sessionmaker[AsyncSession],
        registered: Callable[[Any], None],
        no_model_calls: None,
    ) -> None:
        arc = closing_arc()
        registered(arc)
        seated = await seat_session(db, arc, players=2)
        rec = Recorder()
        now = await play_to_last_call(db, seated, rec) + 5
        first, second = seated.participants
        await save_theory_draft(db, seated.session_id, first, WRONG, None, at(now), rec)
        await save_theory_draft(
            db, seated.session_id, first, RIGHT, "c_how_true", at(now + 1), rec
        )
        await lock_theory(db, seated.session_id, first, at(now + 2), rec)
        await save_theory_draft(
            db, seated.session_id, second, RIGHT, None, at(now + 3), rec
        )
        # The second player never locks: the phase ends on its clock and locks
        # the complete draft for them.
        await tick(db, seated.session_id, at(now + 500), rec)
        await db.commit()

        slots = {str(first): 2, str(second): 2}
        measured = await recap.measure_players(
            db, seated.session_id, [first, second], slots
        )
        mine, theirs = measured[str(first)], measured[str(second)]
        for values in (mine, theirs):
            assert values["investigations_used"] == 6
            assert values["investigations_left"] == 0
            assert values["subjects_looked_into"] == 6
            assert values["most_returns_to_one_subject"] == 1
            assert values["reviews"] == 0
            assert values["slots_right"] == 2
        assert mine["draft_changes"] == 1 and theirs["draft_changes"] == 0
        assert mine["locked_in_time"] == 1 and theirs["locked_in_time"] == 0

        async with factory() as fresh:
            again = await recap.measure_players(
                fresh, seated.session_id, [first, second], slots
            )
        assert again == measured
