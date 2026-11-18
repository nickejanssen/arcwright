"""A mini-game win gives the top-ranked one extra investigation (AW-328, D-126).

Spec 0093 "Q1 Answered". The reward is a setting on the beat's mini-game binding
in the arc file; it is saved as a ``budget_grant`` row, given once, and read
back from saved rows. Time is a value passed in. Every test reads saved state.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any
from unittest.mock import patch

import pytest
import pytest_asyncio
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.db.testing import make_sqlite_session_factory
from engine.events.models import AudienceTarget
from engine.mini_games.resolver import resolve_loaded_mini_game_snapshot
from engine.session.choices import remaining_budget
from engine.session.phases import finish_mini_game_phase, host_move_on, tick
from engine.tests.mini_game_reward_support import (
    AFTER_DEADLINE,
    ENTERED,
    grants,
    in_mini_game,
    place_players,
    reward_arc,
    reward_binding,
    runtime,
    the_run,
)
from engine.tests.rounds_support import at, phased_arc, where

BASE = 6  # the arc's default budget


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine, factory = await make_sqlite_session_factory()
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
    await engine.dispose()


async def budgets(db: AsyncSession, seated: Any) -> list[int]:
    return [
        await remaining_budget(db, seated.session_id, who)
        for who in seated.participants
    ]


class TestWhoIsRewarded:
    @pytest.mark.asyncio
    async def test_the_top_ranked_player_gets_one_more_and_nobody_else_changes(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(1))
        await place_players(db, seated, [1, 2, 3])
        await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        assert await budgets(db, seated) == [BASE + 1, BASE, BASE]
        assert await where(db, seated.session_id) == ("beat_one", "bridge", "running")

    @pytest.mark.asyncio
    async def test_a_tie_at_the_top_rewards_each_tied_player(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(1))
        await place_players(db, seated, [1, 1, 2])
        await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        assert await budgets(db, seated) == [BASE + 1, BASE + 1, BASE]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("places", [[1, 1, 1], [None, None, None], [5, 5, 5]])
    async def test_nobody_is_rewarded_when_every_player_ties_at_the_top(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
        places: list[int | None],
    ) -> None:
        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(1))
        await place_players(db, seated, places)
        await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        assert await budgets(db, seated) == [BASE, BASE, BASE]
        assert await grants(db, seated.session_id) == []

    @pytest.mark.asyncio
    async def test_a_player_who_sent_nothing_ranks_below_those_who_did(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(1))
        await place_players(db, seated, [None, 1, 1])
        await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        assert await budgets(db, seated) == [BASE, BASE + 1, BASE + 1]


class TestTheSetting:
    @pytest.mark.asyncio
    async def test_an_arc_with_no_reward_setting_gives_nothing(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(None))
        await place_players(db, seated, [1, 2, 3])
        await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        assert await budgets(db, seated) == [BASE, BASE, BASE]
        assert await grants(db, seated.session_id) == []
        assert rec.of_type("mini_game_reward_granted") == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize("amount", [1, 2, 3])
    async def test_the_amount_comes_from_the_arc_file(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
        amount: int,
    ) -> None:
        seated, rec = await in_mini_game(
            db, registered, monkeypatch, reward_arc(amount)
        )
        await place_players(db, seated, [1, 2, 2])
        await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        assert await budgets(db, seated) == [BASE + amount, BASE, BASE]

    def test_a_reward_must_be_at_least_one_and_of_a_known_kind(self) -> None:
        for bad in (
            {"kind": "investigation", "amount": 0, "to": "top_ranked"},
            {"kind": "prize", "amount": 1, "to": "top_ranked"},
            {"kind": "investigation", "amount": 1, "to": "everyone"},
            {"kind": "investigation", "amount": 1, "to": "top_ranked", "extra": 1},
        ):
            binding = {
                "binding_id": "b",
                "game_id": "g",
                "version": "0.1.0",
                "reward": bad,
            }
            with pytest.raises(ValidationError):
                phased_arc(mini_games={"beat_one": [binding]})

    @pytest.mark.parametrize(
        "setting",
        [
            {"reward": {"kind": "investigation", "amount": 1, "to": "top_ranked"}},
            {"release_content": False},
        ],
    )
    def test_a_setting_on_a_mini_game_that_never_runs_is_refused(
        self, setting: dict[str, Any]
    ) -> None:
        """Only the first mini-game on a beat runs (AW-303), so a setting on a
        later one would be ignored without an error."""
        later = {"binding_id": "second", "game_id": "g", "version": "0.1.0", **setting}
        with pytest.raises(ValidationError, match="only the first mini-game"):
            phased_arc(mini_games={"beat_one": [reward_binding(1), later]})
        plain = {"binding_id": "second", "game_id": "g", "version": "0.1.0"}
        phased_arc(mini_games={"beat_one": [reward_binding(1), plain]})

    def test_the_registered_arc_files_set_no_reward_and_still_load(self) -> None:
        from pathlib import Path

        root = Path(__file__).resolve().parents[2] / "nightcap"
        for name in ("arc.json", "couch-race.arc.json"):
            arc = ArcDefinition.model_validate_json((root / name).read_text("utf-8"))
            for beat in arc.beats:
                for binding in beat.mini_games or []:
                    assert binding.reward is None
                    assert binding.release_content is True


class TestGivenOnce:
    @pytest.mark.asyncio
    async def test_processing_the_end_twice_gives_it_once_and_tells_once(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        from engine.session import mini_game_reward

        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(1))
        await place_players(db, seated, [1, 2, 3])
        await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        await tick(db, seated.session_id, at(AFTER_DEADLINE + 1), rec)
        assert (
            await finish_mini_game_phase(
                db, seated.session_id, at(AFTER_DEADLINE + 2), rec
            )
            is False
        )
        run = await the_run(db, seated.session_id)
        await mini_game_reward.give(  # the same end, processed again directly
            db,
            seated.session_id,
            "beat_one",
            run.definition_snapshot["binding"]["phase_entry"],
            at(AFTER_DEADLINE + 3),
            rec,
        )
        assert len(await grants(db, seated.session_id)) == 1
        assert await budgets(db, seated) == [BASE + 1, BASE, BASE]
        assert len(rec.of_type("mini_game_reward_granted")) == 1

    @pytest.mark.asyncio
    async def test_it_is_still_there_after_the_session_is_loaded_again(
        self,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        engine, factory = await make_sqlite_session_factory()
        try:
            async with factory() as first:
                seated, rec = await in_mini_game(
                    first, registered, monkeypatch, reward_arc(2)
                )
                await place_players(first, seated, [2, 1, 3])
                await tick(first, seated.session_id, at(AFTER_DEADLINE), rec)
                await first.commit()
            async with factory() as second:
                assert await budgets(second, seated) == [BASE, BASE + 2, BASE]
        finally:
            await engine.dispose()


class TestWhoIsTold:
    @pytest.mark.asyncio
    async def test_only_each_rewarded_player_is_told_and_no_case_content_goes_with_it(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(1))
        await place_players(db, seated, [1, 1, 2])
        await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        told = rec.of_type("mini_game_reward_granted")
        assert sorted(str(e.target_player_id) for e in told) == sorted(
            str(p) for p in seated.participants[:2]
        )
        for event in told:
            assert event.target_audience is AudienceTarget.specific_player
            assert event.payload == {
                "amount": 1,
                "kind": "investigation",
                "remaining_budget": BASE + 1,
            }


class TestAFailedMessage:
    """A message that fails to send must not be lost, and must not be sent twice."""

    @pytest.mark.asyncio
    async def test_a_failure_telling_one_winner_is_retried_for_the_rest_only(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(1))
        await place_players(db, seated, [1, 1, 2])
        sent: list[str] = []
        fail = {"on": True}

        async def publish(event: Any) -> Any:
            if event.event_type == "mini_game_reward_granted":
                if fail["on"] and len(sent) == 1:
                    raise RuntimeError("the publisher failed")
                sent.append(str(event.target_player_id))
            return event

        with pytest.raises(RuntimeError):
            await tick(db, seated.session_id, at(AFTER_DEADLINE), publish)
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "mini_game")
        assert len(sent) == 1
        fail["on"] = False
        await tick(db, seated.session_id, at(AFTER_DEADLINE + 1), publish)
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "bridge")
        assert sorted(sent) == sorted(str(p) for p in seated.participants[:2])
        assert len(await grants(db, seated.session_id)) == 2
        assert await budgets(db, seated) == [BASE + 1, BASE + 1, BASE]
        await tick(db, seated.session_id, at(AFTER_DEADLINE + 2), publish)
        assert len(sent) == 2


class TestWhenNothingIsGiven:
    @pytest.mark.asyncio
    async def test_a_run_the_host_moves_past_is_cancelled_and_gives_nothing(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(1))
        await place_players(db, seated, [1, 2, 3])
        await host_move_on(db, seated.session_id, at(ENTERED + 8), rec)
        assert (await the_run(db, seated.session_id)).status == "cancelled"
        assert await budgets(db, seated) == [BASE, BASE, BASE]
        assert await grants(db, seated.session_id) == []

    @pytest.mark.asyncio
    async def test_a_run_the_host_resolves_early_is_scored_and_rewards_the_winner(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(1))
        run = await place_players(db, seated, [3, 1, 2])
        await runtime(db, ENTERED + 6).resolve_run(run.run_id)
        assert (await the_run(db, seated.session_id)).status == "completed"
        await tick(db, seated.session_id, at(ENTERED + 7), rec)
        assert await budgets(db, seated) == [BASE, BASE + 1, BASE]


class TestReleasesSwitchedOff:
    """The setting that stops a mini-game handing out case content."""

    CONTENT = {
        "clues": [
            {"clue_id": "k1", "variant": "full", "content": {"text": "made up"}},
            {"clue_id": "k2", "variant": "reduced", "content": {"text": "made up"}},
        ]
    }

    @pytest.mark.asyncio
    @pytest.mark.parametrize("finish", ["completed", "timed_out"])
    @pytest.mark.parametrize(
        ("release_content", "expect_released"),
        [(False, False), (True, True), (None, True)],
    )
    async def test_release_content_false_sends_no_case_content(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
        finish: str,
        release_content: bool | None,
        expect_released: bool,
    ) -> None:
        content = self.CONTENT

        async def with_content(*args: Any, **kwargs: Any) -> Any:
            snapshot = await resolve_loaded_mini_game_snapshot(*args, **kwargs)
            return snapshot.model_copy(update={"resolved_content": content})

        arc = reward_arc(1, release_content=release_content)
        with patch(
            "engine.session.mini_game_phase.resolve_loaded_mini_game_snapshot",
            with_content,
        ):
            seated, rec = await in_mini_game(db, registered, monkeypatch, arc)
        run = await place_players(db, seated, [1, 2, 3])
        if finish == "completed":
            await runtime(db, ENTERED + 6, rec).resolve_run(run.run_id)
            await tick(db, seated.session_id, at(ENTERED + 7), rec)
        else:
            await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        saved = await the_run(db, seated.session_id)
        assert saved.status == finish
        deliveries = [
            e
            for e in rec.events
            if e.event_type.endswith("_delivery")
            and e.event_type.startswith("mini_game_")
        ]
        unlocked = (saved.clue_unlock_record or {}).get("unlocked", [])
        if expect_released:
            assert deliveries and unlocked
        else:
            assert deliveries == []
            assert unlocked == []
        # The reward does not depend on releases: it is still given.
        assert await budgets(db, seated) == [BASE + 1, BASE, BASE]
