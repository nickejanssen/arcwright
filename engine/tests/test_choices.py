"""The investigation menu, the saved budget and holdings (AW-325, spec 0093 Part D).

Uses only the made-up case in ``fixtures/authored_case/valid_case.json``.
Beat one offers ``o_ledger``, ``o_shed`` and ``o_porter`` (cost 1 each).
Beat two adds ``o_gate`` (needs the ledger), ``o_bench`` and ``o_note`` (a free
follow-up needing the ledger). Beat three adds ``o_attic`` and ``o_cellar``
(needs the tool marks from the bench).
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.arc.models import ArcDefinition
from engine.db.orm import Decision, SessionParticipant
from engine.db.testing import make_sqlite_session_factory
from engine.events.models import AudienceTarget, EventCategory
from engine.knowledge.holdings import concepts_held
from engine.session.choices import (
    ChoiceResult,
    budget_allowance,
    choose,
    read_holdings,
    read_menu,
    remaining_budget,
)
from engine.session.phases import RoundError, current_phase, host_move_on, tick
from engine.session.service import SessionService, SessionStateError
from engine.tests.rounds_support import (
    Recorder,
    Seated,
    at,
    phased_arc,
    private_to,
    reach_phase,
    seat_session,
    where,
)

LEDGER_CONTENT = "You read the ledger closely."


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


async def open_choices(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    *,
    beat: str = "beat_one",
    players: int = 2,
    budget: int | None = None,
) -> tuple[Seated, Recorder, ArcDefinition]:
    arc = phased_arc(budget=budget)
    registered(arc)
    seated = await seat_session(db, arc, players=players)
    rec = Recorder()
    await tick(db, seated.session_id, at(0), rec)
    await reach_phase(db, seated, beat, "choices", at(100), rec)
    return seated, rec, arc


async def pick(
    db: AsyncSession,
    seated: Seated,
    who: int,
    opportunity: str,
    rec: Recorder | None = None,
    choice_id: str | None = None,
    now: float = 101,
) -> ChoiceResult:
    return await choose(
        db,
        seated.session_id,
        seated.participants[who],
        choice_id or f"c-{who}-{opportunity}-{uuid4()}",
        opportunity,
        at(now),
        rec,
    )


async def decision_count(db: AsyncSession, session_id: UUID) -> int:
    count = await db.scalar(
        select(func.count())
        .select_from(Decision)
        .where(Decision.session_id == session_id, Decision.decision_type == "choice")
    )
    return int(count or 0)


class TestMenu:
    @pytest.mark.asyncio
    async def test_the_menu_lists_this_beats_choices_with_the_full_budget(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _, _ = await open_choices(db, registered)
        menu = await read_menu(db, seated.session_id, seated.participants[0])
        assert menu.open
        assert menu.remaining_budget == 6
        assert {item.opportunity_id for item in menu.items} == {
            "o_ledger",
            "o_shed",
            "o_porter",
        }
        assert not any(item.taken for item in menu.items)
        assert all(item.cost == 1 for item in menu.items)

    @pytest.mark.asyncio
    async def test_the_menu_does_not_carry_the_written_content(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _, _ = await open_choices(db, registered)
        menu = await read_menu(db, seated.session_id, seated.participants[0])
        assert LEDGER_CONTENT not in repr(menu)

    @pytest.mark.asyncio
    async def test_a_choice_needing_a_concept_you_lack_is_not_on_the_menu(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered, beat="beat_two")
        before = await read_menu(db, seated.session_id, seated.participants[0])
        assert "o_gate" not in {i.opportunity_id for i in before.items}
        assert "o_note" not in {i.opportunity_id for i in before.items}
        await pick(db, seated, 0, "o_ledger", rec)
        after = await read_menu(db, seated.session_id, seated.participants[0])
        assert {"o_gate", "o_note"} <= {i.opportunity_id for i in after.items}
        other = await read_menu(db, seated.session_id, seated.participants[1])
        assert "o_gate" not in {i.opportunity_id for i in other.items}

    @pytest.mark.asyncio
    async def test_the_menu_is_closed_outside_a_choices_phase(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await host_move_on(db, seated.session_id, at(110), rec)
        menu = await read_menu(db, seated.session_id, seated.participants[0])
        assert not menu.open and menu.items == ()

    @pytest.mark.asyncio
    async def test_taken_choices_are_marked_taken(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await pick(db, seated, 0, "o_shed", rec)
        menu = await read_menu(db, seated.session_id, seated.participants[0])
        assert {i.opportunity_id: i.taken for i in menu.items}["o_shed"]
        assert menu.remaining_budget == 5


class TestChoosing:
    @pytest.mark.asyncio
    async def test_a_choice_gives_its_concepts_to_that_participant_only(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        result = await pick(db, seated, 0, "o_shed", rec)
        assert result.first_time and result.cost == 1
        assert set(result.gave) == {"c_shed_key", "c_how_false1"}
        mine = await concepts_held(
            db, session_id=seated.session_id, character_id=seated.characters[0]
        )
        theirs = await concepts_held(
            db, session_id=seated.session_id, character_id=seated.characters[1]
        )
        assert {"c_shed_key", "c_how_false1"} <= mine
        assert not {"c_shed_key", "c_how_false1"} & theirs

    @pytest.mark.asyncio
    async def test_the_content_goes_to_that_player_only(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await pick(db, seated, 0, "o_ledger", rec)
        private = private_to(rec.events, seated.participants[0])
        assert [e.event_type for e in private] == ["choice_result"]
        assert private[0].category is EventCategory.private_delivery
        assert private[0].payload["content"] == LEDGER_CONTENT
        assert private_to(rec.events, seated.participants[1]) == []
        for event in rec.events:
            if event.event_type != "choice_result":
                assert LEDGER_CONTENT not in event.model_dump_json()

    @pytest.mark.asyncio
    async def test_the_host_hears_only_that_a_choice_was_made(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await pick(db, seated, 0, "o_ledger", rec)
        made = rec.of_type("choice_made")
        assert len(made) == 1
        assert made[0].target_audience is AudienceTarget.host_only
        assert set(made[0].payload) == {"participant_id", "beat_id"}

    @pytest.mark.asyncio
    async def test_the_decision_is_saved_with_the_menu_it_was_made_from(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await pick(db, seated, 0, "o_porter", rec, choice_id="phone-1")
        row = (
            await db.execute(select(Decision).where(Decision.decision_type == "choice"))
        ).scalar_one()
        assert row.context["choice_id"] == "phone-1"
        assert row.context["participant_id"] == str(seated.participants[0])
        assert row.context["beat_id"] == "beat_one"
        assert set(row.context["offered"]) == {"o_ledger", "o_shed", "o_porter"}
        assert row.context["opportunity_id"] == "o_porter"
        assert row.outcome["cost"] == 1 and row.outcome["gave"] == ["c_witness"]

    @pytest.mark.asyncio
    async def test_a_follow_up_costs_nothing(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered, beat="beat_two")
        await pick(db, seated, 0, "o_ledger", rec)
        spent = await remaining_budget(db, seated.session_id, seated.participants[0])
        result = await pick(db, seated, 0, "o_note", rec)
        assert result.first_time and result.cost == 0
        assert (
            await remaining_budget(db, seated.session_id, seated.participants[0])
            == spent
        )


class TestBudget:
    @pytest.mark.asyncio
    async def test_six_paid_choices_pass_and_the_seventh_is_refused_with_nothing_saved(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        for opportunity in ("o_ledger", "o_shed", "o_porter"):
            await pick(db, seated, 0, opportunity, rec)
        await reach_phase(db, seated, "beat_two", "choices", at(200), rec)
        for opportunity in ("o_gate", "o_bench"):
            await pick(db, seated, 0, opportunity, rec, now=201)
        await reach_phase(db, seated, "beat_three", "choices", at(300), rec)
        await pick(db, seated, 0, "o_attic", rec, now=301)
        participant = seated.participants[0]
        assert await remaining_budget(db, seated.session_id, participant) == 0

        saved = await decision_count(db, seated.session_id)
        held = await concepts_held(
            db, session_id=seated.session_id, character_id=seated.characters[0]
        )
        events = len(rec.events)
        with pytest.raises(RoundError) as refused:
            await pick(db, seated, 0, "o_cellar", rec, now=302)
        assert refused.value.code == "budget_exhausted"
        assert await decision_count(db, seated.session_id) == saved
        assert (
            await concepts_held(
                db, session_id=seated.session_id, character_id=seated.characters[0]
            )
            == held
        )
        assert len(rec.events) == events

    @pytest.mark.asyncio
    async def test_the_budget_belongs_to_each_participant(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await pick(db, seated, 0, "o_ledger", rec)
        assert (
            await remaining_budget(db, seated.session_id, seated.participants[0]) == 5
        )
        assert (
            await remaining_budget(db, seated.session_id, seated.participants[1]) == 6
        )

    @pytest.mark.asyncio
    async def test_the_size_of_the_budget_comes_from_the_arc_file(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered, budget=4)
        for opportunity in ("o_ledger", "o_shed", "o_porter"):
            await pick(db, seated, 0, opportunity, rec)
        await reach_phase(db, seated, "beat_two", "choices", at(200), rec)
        await pick(db, seated, 0, "o_bench", rec, now=201)
        with pytest.raises(RoundError) as refused:
            await pick(db, seated, 0, "o_gate", rec, now=202)
        assert refused.value.code == "budget_exhausted"

    @pytest.mark.asyncio
    async def test_a_budget_the_case_cannot_be_solved_within_is_refused_at_start(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        arc = phased_arc(budget=1)
        registered(arc)
        svc = SessionService()
        created, _ = await svc.create_session(
            db, arc_id=arc.arc_id, host_account_id=uuid4()
        )
        with pytest.raises(SessionStateError, match="case refused"):
            await svc.start_session(db, created.session_id)

    def test_an_added_amount_is_one_small_change(self) -> None:
        arc = phased_arc(budget=6)
        assert budget_allowance(arc, granted=[]) == 6
        assert budget_allowance(arc, granted=[1]) == 7
        assert budget_allowance(arc, granted=[1, 2]) == 9

    @pytest.mark.asyncio
    async def test_a_saved_grant_raises_what_a_participant_may_spend(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered, budget=4)
        db.add(
            Decision(
                session_id=seated.session_id,
                decision_type="budget_grant",
                context={"participant_id": str(seated.participants[0])},
                outcome={"amount": 1},
            )
        )
        await db.flush()
        assert (
            await remaining_budget(db, seated.session_id, seated.participants[0]) == 5
        )
        assert (
            await remaining_budget(db, seated.session_id, seated.participants[1]) == 4
        )

    @pytest.mark.asyncio
    async def test_two_choices_at_the_same_moment_cannot_both_pass_the_budget(
        self,
        factory: async_sessionmaker[AsyncSession],
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
    ) -> None:
        seated, rec, _ = await open_choices(db, registered, budget=4)
        for opportunity in ("o_ledger", "o_shed", "o_porter"):
            await pick(db, seated, 0, opportunity, rec)
        await reach_phase(db, seated, "beat_two", "choices", at(200), rec)
        assert (
            await remaining_budget(db, seated.session_id, seated.participants[0]) == 1
        )
        await db.commit()

        async def attempt(opportunity: str) -> str:
            async with factory() as other:
                try:
                    await choose(
                        other,
                        seated.session_id,
                        seated.participants[0],
                        f"race-{opportunity}",
                        opportunity,
                        at(201),
                        rec,
                    )
                    await other.commit()
                    return "ok"
                except RoundError as refused:
                    await other.rollback()
                    return refused.code

        outcomes = await asyncio.gather(attempt("o_gate"), attempt("o_bench"))
        assert sorted(outcomes) == ["budget_exhausted", "ok"]
        assert (
            await remaining_budget(db, seated.session_id, seated.participants[0]) == 0
        )


class TestRepeatsAndReview:
    @pytest.mark.asyncio
    async def test_choosing_something_already_taken_costs_nothing_and_shows_it_again(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        first = await pick(db, seated, 0, "o_ledger", rec)
        again = await pick(db, seated, 0, "o_ledger", rec)
        assert first.first_time and not again.first_time
        assert again.cost == 0 and again.content == first.content == LEDGER_CONTENT
        assert (
            await remaining_budget(db, seated.session_id, seated.participants[0]) == 5
        )

    @pytest.mark.asyncio
    async def test_the_same_choice_id_twice_has_one_effect_and_the_same_answer(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        first = await pick(db, seated, 0, "o_ledger", rec, choice_id="tap-1")
        saved = await decision_count(db, seated.session_id)
        events = len(rec.events)
        second = await pick(db, seated, 0, "o_ledger", rec, choice_id="tap-1")
        assert second.replayed and not first.replayed
        assert (second.content, second.gave, second.cost, second.first_time) == (
            first.content,
            first.gave,
            first.cost,
            first.first_time,
        )
        assert await decision_count(db, seated.session_id) == saved
        assert len(rec.events) == events
        assert (
            await remaining_budget(db, seated.session_id, seated.participants[0]) == 5
        )

    @pytest.mark.asyncio
    async def test_the_same_choice_id_from_two_players_is_two_choices(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await pick(db, seated, 0, "o_ledger", rec, choice_id="shared")
        other = await pick(db, seated, 1, "o_ledger", rec, choice_id="shared")
        assert other.first_time and not other.replayed


class TestRefusals:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("phase", ["scene", "mini_game", "bridge"])
    async def test_a_choice_outside_a_choices_phase_is_refused(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        phase: str,
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await reach_phase(db, seated, "beat_two", phase, at(200), rec)
        saved = await decision_count(db, seated.session_id)
        with pytest.raises(RoundError) as refused:
            await pick(db, seated, 0, "o_ledger", rec, now=201)
        assert refused.value.code == "not_in_choices_phase"
        assert await decision_count(db, seated.session_id) == saved

    @pytest.mark.asyncio
    async def test_a_choice_not_on_this_players_menu_is_refused(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        for opportunity in ("o_attic", "o_gate", "o_nonsense"):
            with pytest.raises(RoundError) as refused:
                await pick(db, seated, 0, opportunity, rec)
            assert refused.value.code == "not_on_menu"
        assert await decision_count(db, seated.session_id) == 0

    @pytest.mark.asyncio
    async def test_a_participant_not_in_the_session_is_refused(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        host_id = await db.scalar(
            select(SessionParticipant.participant_id).where(
                SessionParticipant.session_id == seated.session_id,
                SessionParticipant.surface_type == "host",
            )
        )
        for outsider in (uuid4(), host_id):
            with pytest.raises(RoundError) as refused:
                await choose(
                    db, seated.session_id, outsider, "x", "o_ledger", at(101), rec
                )
            assert refused.value.code == "not_a_participant"
            with pytest.raises(RoundError):
                await read_menu(db, seated.session_id, outsider)
            with pytest.raises(RoundError):
                await read_holdings(db, seated.session_id, outsider)

    @pytest.mark.asyncio
    async def test_a_game_with_no_written_case_has_no_menu(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        arc = phased_arc(case_path=None)
        registered(arc)
        seated = await seat_session(db, arc)
        rec = Recorder()
        await tick(db, seated.session_id, at(0), rec)
        await reach_phase(db, seated, "beat_one", "choices", at(100), rec)
        with pytest.raises(RoundError) as refused:
            await read_menu(db, seated.session_id, seated.participants[0])
        assert refused.value.code == "no_written_case"

    @pytest.mark.asyncio
    async def test_a_paused_session_refuses_choices(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await SessionService().pause_session(db, seated.session_id, now=at(105))
        with pytest.raises(RoundError) as refused:
            await pick(db, seated, 0, "o_ledger", rec, now=106)
        assert refused.value.code == "session_not_active"


class TestArcAndCaseAgree:
    @pytest.mark.asyncio
    async def test_a_case_offering_choices_in_a_beat_with_no_choices_phase_is_refused(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        arc = phased_arc(
            phases={"beat_two": [{"kind": "scene", "seconds": 5}]},
            mini_games={"beat_two": []},  # no mini_game phase, so no binding
        )
        registered(arc)
        svc = SessionService()
        created, _ = await svc.create_session(
            db, arc_id=arc.arc_id, host_account_id=uuid4()
        )
        with pytest.raises(SessionStateError, match="beat_two"):
            await svc.start_session(db, created.session_id)


class TestHoldings:
    @pytest.mark.asyncio
    async def test_holdings_list_the_opening_and_what_was_found_with_their_text(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await pick(db, seated, 0, "o_ledger", rec)
        mine = await read_holdings(db, seated.session_id, seated.participants[0])
        assert {h.concept_id for h in mine} == {"c_open_a", "c_open_b", "c_ledger"}
        assert all(h.text and h.label for h in mine)
        theirs = await read_holdings(db, seated.session_id, seated.participants[1])
        assert {h.concept_id for h in theirs} == {"c_open_a", "c_open_b"}

    @pytest.mark.asyncio
    async def test_holdings_say_where_and_when_each_was_found(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await pick(db, seated, 0, "o_ledger", rec)
        mine = {
            h.concept_id: h
            for h in await read_holdings(db, seated.session_id, seated.participants[0])
        }
        assert mine["c_open_a"].found_from is None
        assert mine["c_open_a"].found_in_beat is None
        assert mine["c_ledger"].found_in_beat == "beat_one"
        assert mine["c_ledger"].found_from

    @pytest.mark.asyncio
    async def test_holdings_do_not_say_which_concepts_are_misleading(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await pick(db, seated, 0, "o_shed", rec)
        mine = await read_holdings(db, seated.session_id, seated.participants[0])
        for held in mine:
            assert not hasattr(held, "standing")
            assert "misleading" not in repr(held)

    @pytest.mark.asyncio
    async def test_a_player_who_joins_after_the_start_gets_the_opening_on_first_read(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        late, _ = await SessionService().add_player(db, seated.session_id)
        held = await read_holdings(db, seated.session_id, late.participant_id)
        assert {h.concept_id for h in held} == {"c_open_a", "c_open_b"}
        again = await read_holdings(db, seated.session_id, late.participant_id)
        assert [h.concept_id for h in again] == [h.concept_id for h in held]


class TestRestart:
    @pytest.mark.asyncio
    async def test_menu_budget_and_holdings_read_the_same_after_a_rebuild(
        self,
        factory: async_sessionmaker[AsyncSession],
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await pick(db, seated, 0, "o_ledger", rec)
        await pick(db, seated, 0, "o_shed", rec)
        participant = seated.participants[0]

        def snapshot(menu: Any, held: Any, left: int) -> Any:
            return (
                menu.open,
                menu.remaining_budget,
                [(i.opportunity_id, i.taken, i.cost) for i in menu.items],
                sorted(h.concept_id for h in held),
                left,
            )

        before = snapshot(
            await read_menu(db, seated.session_id, participant),
            await read_holdings(db, seated.session_id, participant),
            await remaining_budget(db, seated.session_id, participant),
        )
        await db.commit()
        async with factory() as fresh:
            after = snapshot(
                await read_menu(fresh, seated.session_id, participant),
                await read_holdings(fresh, seated.session_id, participant),
                await remaining_budget(fresh, seated.session_id, participant),
            )
            assert await where(fresh, seated.session_id) == (
                "beat_one",
                "choices",
                "running",
            )
        assert after == before
        assert before[1] == 4


class TestDeadlineAndReplay:
    """AW-338: a choice is refused at the phase deadline, and a replay is exact."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("late", [0.0, 1.0])
    async def test_a_choice_at_or_after_the_deadline_is_refused_before_the_tick(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        late: float,
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        state = await current_phase(db, seated.session_id)
        assert state is not None and state.deadline_at is not None
        saved, events = await decision_count(db, seated.session_id), len(rec.events)
        with pytest.raises(RoundError) as refused:
            await choose(
                db,
                seated.session_id,
                seated.participants[0],
                "late-1",
                "o_ledger",
                state.deadline_at + timedelta(seconds=late),
                rec,
            )
        assert refused.value.code == "phase_time_up"
        assert await decision_count(db, seated.session_id) == saved
        assert len(rec.events) == events

    @pytest.mark.asyncio
    async def test_a_choice_just_before_the_deadline_is_accepted(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        state = await current_phase(db, seated.session_id)
        assert state is not None and state.deadline_at is not None
        result = await choose(
            db,
            seated.session_id,
            seated.participants[0],
            "on-time",
            "o_ledger",
            state.deadline_at - timedelta(seconds=1),
            rec,
        )
        assert result.first_time

    @pytest.mark.asyncio
    async def test_a_replay_after_the_deadline_still_returns_the_saved_answer(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        first = await pick(db, seated, 0, "o_ledger", rec, choice_id="tap-1")
        state = await current_phase(db, seated.session_id)
        assert state is not None and state.deadline_at is not None
        again = await choose(
            db,
            seated.session_id,
            seated.participants[0],
            "tap-1",
            "o_ledger",
            state.deadline_at + timedelta(seconds=5),
            rec,
        )
        assert again.replayed and again.content == first.content

    @pytest.mark.asyncio
    async def test_a_choice_id_reused_for_another_opportunity_is_refused(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        await pick(db, seated, 0, "o_ledger", rec, choice_id="tap-1")
        saved, events = await decision_count(db, seated.session_id), len(rec.events)
        with pytest.raises(RoundError) as refused:
            await pick(db, seated, 0, "o_shed", rec, choice_id="tap-1")
        assert refused.value.code == "choice_id_reused"
        assert await decision_count(db, seated.session_id) == saved
        assert len(rec.events) == events

    @pytest.mark.asyncio
    async def test_a_replay_reports_the_budget_as_it_was_at_the_first_answer(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec, _ = await open_choices(db, registered)
        first = await pick(db, seated, 0, "o_ledger", rec, choice_id="tap-1")
        await pick(db, seated, 0, "o_shed", rec)
        assert (
            await remaining_budget(db, seated.session_id, seated.participants[0])
            < first.remaining_budget
        )
        again = await pick(db, seated, 0, "o_ledger", rec, choice_id="tap-1")
        assert again.replayed
        assert again.remaining_budget == first.remaining_budget
