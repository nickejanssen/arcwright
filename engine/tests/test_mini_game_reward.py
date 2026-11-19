"""A mini-game win gives the top-ranked one extra investigation (AW-328, D-126).

Spec 0093 "Q1 Answered". The reward is a setting on the beat's mini-game binding
in the arc file; it is saved as a ``budget_grant`` row, given once, and read
back from saved rows. Time is a value passed in. Every test reads saved state.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from dataclasses import asdict
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
from engine.session.choices import read_menu, remaining_budget
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
                "grant_id": event.payload["grant_id"],
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


class TestReadBack:
    """A phone that missed the live message, or reloaded, reads its rewards from
    the menu route instead (AW-343). The read comes from the saved grant rows."""

    @pytest.mark.asyncio
    async def test_the_winner_reads_the_reward_and_the_others_read_none(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(2))
        await place_players(db, seated, [1, 2, 3])
        await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        winner, second, third = seated.participants
        read = (await read_menu(db, seated.session_id, winner)).rewards
        assert [(r.amount, r.kind, r.beat_id) for r in read] == [
            (2, "investigation", "beat_one")
        ]
        assert read[0].run_id == str((await the_run(db, seated.session_id)).run_id)
        assert (await read_menu(db, seated.session_id, second)).rewards == ()
        assert (await read_menu(db, seated.session_id, third)).rewards == ()

    @pytest.mark.asyncio
    async def test_it_reads_while_the_menu_is_closed(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(1))
        await place_players(db, seated, [1, 2, 3])
        await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        menu = await read_menu(db, seated.session_id, seated.participants[0])
        assert menu.open is False
        assert len(menu.rewards) == 1

    @pytest.mark.asyncio
    async def test_the_same_list_comes_back_twice_and_after_a_reload(
        self,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        engine, factory = await make_sqlite_session_factory()
        try:
            async with factory() as first:
                seated, rec = await in_mini_game(
                    first, registered, monkeypatch, reward_arc(1)
                )
                await place_players(first, seated, [1, 2, 3])
                await tick(first, seated.session_id, at(AFTER_DEADLINE), rec)
                one = (
                    await read_menu(first, seated.session_id, seated.participants[0])
                ).rewards
                two = (
                    await read_menu(first, seated.session_id, seated.participants[0])
                ).rewards
                await first.commit()
            async with factory() as second:
                three = (
                    await read_menu(second, seated.session_id, seated.participants[0])
                ).rewards
            assert len(one) == 1
            assert one == two == three
        finally:
            await engine.dispose()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("delivery", ["no_publisher", "queued_never_delivered"])
    async def test_a_committed_reward_whose_message_never_arrived_is_read_fresh(
        self,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
        delivery: str,
    ) -> None:
        """The grant is committed; delivery (the outbox's job, after the commit)
        never reaches the phone. A fresh session still reads the reward."""
        engine, factory = await make_sqlite_session_factory()
        queued: list[Any] = []

        async def queue_only(event: Any) -> Any:
            queued.append(event)
            return event

        try:
            async with factory() as first:
                seated, _ = await in_mini_game(
                    first, registered, monkeypatch, reward_arc(1)
                )
                await place_players(first, seated, [1, 2, 3])
                publish = None if delivery == "no_publisher" else queue_only
                await tick(first, seated.session_id, at(AFTER_DEADLINE), publish)
                await first.commit()
            async with factory() as fresh:
                winner = seated.participants[0]
                menu = await read_menu(fresh, seated.session_id, winner)
                assert [(r.amount, r.kind) for r in menu.rewards] == [
                    (1, "investigation")
                ]
                assert menu.remaining_budget == BASE + 1
        finally:
            await engine.dispose()

    @pytest.mark.asyncio
    async def test_the_list_and_the_balance_come_from_the_same_rows(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        """A grant committed right after the budget rows were read (the READ
        COMMITTED race) must not show in the list while missing from the balance."""
        from engine.db.orm import Decision
        from engine.session import choices

        seated, _ = await in_mini_game(db, registered, monkeypatch, reward_arc(1))
        winner = seated.participants[0]
        real_ledger = choices._ledger

        async def ledger_then_a_grant_lands(*args: Any) -> Any:
            ledger = await real_ledger(*args)
            db.add(
                Decision(
                    session_id=seated.session_id,
                    timestamp=at(AFTER_DEADLINE),
                    decision_type="budget_grant",
                    context={
                        "participant_id": str(winner),
                        "run_id": "r",
                        "beat_id": "beat_one",
                        "source": "mini_game_reward",
                    },
                    outcome={"amount": 1, "kind": "investigation", "told": False},
                )
            )
            await db.flush()
            return ledger

        monkeypatch.setattr(choices, "_ledger", ledger_then_a_grant_lands)
        menu = await read_menu(db, seated.session_id, winner)
        assert menu.remaining_budget == BASE + sum(r.amount for r in menu.rewards)

    @pytest.mark.asyncio
    async def test_the_live_message_carries_the_id_the_read_returns(
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
        assert len(told) == 2
        for event in told:
            read = (
                await read_menu(db, seated.session_id, event.target_player_id)
            ).rewards
            assert [r.grant_id for r in read] == [event.payload["grant_id"]]
        assert told[0].payload["grant_id"] != told[1].payload["grant_id"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("setting", [None, 1])
    async def test_a_loser_and_an_arc_with_no_setting_read_an_empty_list(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
        setting: int | None,
    ) -> None:
        seated, rec = await in_mini_game(
            db, registered, monkeypatch, reward_arc(setting)
        )
        await place_players(db, seated, [1, 2, 3])
        await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        for who in seated.participants[1:]:
            assert (await read_menu(db, seated.session_id, who)).rewards == ()
        if setting is None:
            winner = seated.participants[0]
            assert (await read_menu(db, seated.session_id, winner)).rewards == ()

    @pytest.mark.asyncio
    async def test_a_read_holds_only_the_five_fields_and_nobody_elses_id(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, monkeypatch, reward_arc(1))
        await place_players(db, seated, [1, 1, 2])
        await tick(db, seated.session_id, at(AFTER_DEADLINE), rec)
        mine, other = seated.participants[0], seated.participants[1]
        read = (await read_menu(db, seated.session_id, mine)).rewards
        assert len(read) == 1
        assert set(asdict(read[0])) == {
            "grant_id",
            "run_id",
            "beat_id",
            "amount",
            "kind",
        }
        assert str(other) not in repr(read)
