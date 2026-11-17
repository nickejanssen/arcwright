"""Rounds that move by rule: phases, the tick, readiness, pause (AW-325).

Spec 0093, Part C. Every transition test reads the saved state back, because
a refused state-machine transition is ignored silently and does not raise.
Time is a value passed in; no test waits and no test uses the API loop.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.arc.registry import load_arc_definition
from engine.characters.service import CharacterService
from engine.db.orm import Decision, Event
from engine.db.orm import Session as OrmSession
from engine.db.testing import make_sqlite_session_factory
from engine.events.models import AudienceTarget, EventCategory
from engine.session.phases import (
    PHASE_EVENT,
    RoundError,
    current_phase,
    finish_mini_game_phase,
    host_move_on,
    mark_ready,
    round_view,
    tick,
)
from engine.session.service import SessionService
from engine.tests.rounds_support import (
    BEATS,
    BRIDGE_SECONDS,
    CHOICES_SECONDS,
    MINI_GAME_SECONDS,
    SCENE_SECONDS,
    SCENE_TEXT,
    Recorder,
    Seated,
    at,
    phased_arc,
    reach_phase,
    round_phases,
    seat_session,
    where,
)

SECONDS = {
    "scene": SCENE_SECONDS,
    "choices": CHOICES_SECONDS,
    "mini_game": MINI_GAME_SECONDS,
    "bridge": BRIDGE_SECONDS,
}


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine, factory = await make_sqlite_session_factory()
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
    await engine.dispose()


async def phase_event_count(db: AsyncSession, session_id: UUID) -> int:
    count = await db.scalar(
        select(func.count())
        .select_from(Event)
        .where(Event.session_id == session_id, Event.event_type == PHASE_EVENT)
    )
    return int(count or 0)


@pytest_asyncio.fixture()
async def started(
    db: AsyncSession, registered: Callable[[ArcDefinition], None]
) -> tuple[Seated, Recorder]:
    registered(phased_arc())
    seated = await seat_session(db, phased_arc())
    rec = Recorder()
    await tick(db, seated.session_id, at(0), rec)
    return seated, rec


# --- the arc file ---------------------------------------------------------------


class TestArcFile:
    def test_both_registered_arc_files_load_unphased_with_budget_six(self) -> None:
        for arc_id in ("nightcap-v1", "nightcap-couch-race-v1"):
            arc = load_arc_definition(arc_id)
            assert arc is not None
            assert not arc.is_phased
            assert all(beat.phases is None for beat in arc.beats)
            assert arc.choice_config.budget == 6

    def test_the_fixture_arc_is_phased(self) -> None:
        arc = phased_arc()
        assert arc.is_phased
        assert [p.kind.value for p in arc.beats[1].phases or []] == [
            "scene",
            "choices",
            "mini_game",
            "bridge",
        ]

    def test_budget_is_read_from_the_arc_file(self) -> None:
        assert phased_arc(budget=2).choice_config.budget == 2

    def test_phases_on_some_beats_and_not_others_is_refused(self) -> None:
        with pytest.raises(ValidationError, match="every beat or on none"):
            phased_arc(phases={"beat_two": None})

    def test_phases_out_of_order_are_refused(self) -> None:
        reordered = list(reversed(round_phases("beat_one")))
        with pytest.raises(ValidationError, match="order"):
            phased_arc(phases={"beat_one": reordered})

    def test_a_repeated_phase_is_refused(self) -> None:
        doubled = round_phases("beat_one")
        doubled.insert(1, dict(doubled[0]))
        with pytest.raises(ValidationError, match="at most once"):
            phased_arc(phases={"beat_one": doubled})

    def test_a_phase_needs_a_time_limit(self) -> None:
        bad = round_phases("beat_one")
        bad[1]["seconds"] = 0
        with pytest.raises(ValidationError):
            phased_arc(phases={"beat_one": bad})

    def test_lines_belong_on_scene_and_bridge_only(self) -> None:
        bad = round_phases("beat_one")
        bad[1]["lines"] = [{"text": "hello"}]
        with pytest.raises(ValidationError, match="written lines"):
            phased_arc(phases={"beat_one": bad})

    def test_lines_cannot_be_addressed_to_one_player(self) -> None:
        bad = round_phases("beat_one")
        bad[0]["audience"] = "specific_player"
        with pytest.raises(ValidationError, match="one player"):
            phased_arc(phases={"beat_one": bad})


# --- entering and sending lines -------------------------------------------------


class TestEnteringAPhase:
    @pytest.mark.asyncio
    async def test_the_first_tick_enters_the_first_phase(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, _ = started
        assert await where(db, seated.session_id) == ("opening", "scene", "running")

    @pytest.mark.asyncio
    async def test_scene_lines_are_published_once_with_the_named_audience(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
    ) -> None:
        arc = phased_arc()
        registered(arc)
        seated = await seat_session(db, arc)
        rec = Recorder()
        await tick(db, seated.session_id, at(0), rec)
        await tick(db, seated.session_id, at(0), rec)
        await tick(db, seated.session_id, at(1), rec)
        lines = rec.of_type("phase_line")
        assert [e.payload["text"] for e in lines] == ["Welcome to the house."]
        assert lines[0].target_audience is AudienceTarget.shared_display
        assert lines[0].category is EventCategory.narrative
        assert lines[0].payload["beat_id"] == "opening"
        assert lines[0].payload["phase"] == "scene"

    @pytest.mark.asyncio
    async def test_lines_carry_presentation_hints_and_their_order(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        await reach_phase(db, seated, "beat_one", "scene", at(1), rec)
        lines = [
            e for e in rec.of_type("phase_line") if e.payload["beat_id"] == "beat_one"
        ]
        assert [e.payload["text"] for e in lines] == [
            SCENE_TEXT.format(beat="beat_one"),
            "Nobody speaks.",
        ]
        assert [e.payload["line_index"] for e in lines] == [0, 1]
        assert lines[0].presentation_hints.emotion == "uneasy"
        assert lines[1].presentation_hints.pause_before_ms == 500

    @pytest.mark.asyncio
    async def test_a_phase_change_event_names_the_deadline_and_no_content(
        self, started: tuple[Seated, Recorder]
    ) -> None:
        _, rec = started
        changes = rec.of_type("phase_changed")
        assert len(changes) == 1
        payload = changes[0].payload
        assert payload["phase"] == "scene"
        assert payload["seconds"] == SCENE_SECONDS
        assert changes[0].target_audience is AudienceTarget.all
        assert "text" not in payload


# --- each phase ends on each of its rules ---------------------------------------

NEXT_PHASE = {
    ("beat_one", "scene"): "choices",
    ("beat_one", "choices"): "mini_game",
    ("beat_one", "mini_game"): "bridge",
}


class TestPhaseEndRules:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("phase", ["scene", "choices", "mini_game", "bridge"])
    async def test_the_clock_ends_every_phase(
        self, started: tuple[Seated, Recorder], db: AsyncSession, phase: str
    ) -> None:
        seated, rec = started
        await reach_phase(db, seated, "beat_one", phase, at(100), rec)
        before = await where(db, seated.session_id)
        await tick(db, seated.session_id, at(100 + SECONDS[phase] - 1), rec)
        assert await where(db, seated.session_id) == before
        await tick(db, seated.session_id, at(100 + SECONDS[phase]), rec)
        after = await where(db, seated.session_id)
        assert after != before
        if phase == "bridge":
            assert after[:2] == ("beat_two", "scene")
        else:
            assert after[:2] == ("beat_one", _next(phase))

    @pytest.mark.asyncio
    @pytest.mark.parametrize("phase", ["scene", "choices", "bridge"])
    async def test_everyone_ready_ends_the_phase_without_a_tick(
        self, started: tuple[Seated, Recorder], db: AsyncSession, phase: str
    ) -> None:
        seated, rec = started
        await reach_phase(db, seated, "beat_one", phase, at(100), rec)
        first, *rest = seated.participants
        state = await mark_ready(db, seated.session_id, first, at(101), rec)
        assert state.phase == phase and state.status == "running"
        assert await where(db, seated.session_id) == ("beat_one", phase, "running")
        for participant in rest:
            await mark_ready(db, seated.session_id, participant, at(102), rec)
        after = await where(db, seated.session_id)
        expected = (
            ("beat_two", "scene") if phase == "bridge" else ("beat_one", _next(phase))
        )
        assert after[:2] == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize("phase", ["scene", "choices", "mini_game", "bridge"])
    async def test_the_host_ends_every_phase(
        self, started: tuple[Seated, Recorder], db: AsyncSession, phase: str
    ) -> None:
        seated, rec = started
        await reach_phase(db, seated, "beat_one", phase, at(100), rec)
        state = await host_move_on(db, seated.session_id, at(101), rec)
        after = await where(db, seated.session_id)
        expected = (
            ("beat_two", "scene") if phase == "bridge" else ("beat_one", _next(phase))
        )
        assert after[:2] == expected
        assert state.phase == after[1]
        ended = await _ended_reasons(db, seated.session_id)
        assert ended[-1] == "host"

    @pytest.mark.asyncio
    async def test_the_mini_game_phase_ends_when_the_stand_in_says_so(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        await reach_phase(db, seated, "beat_one", "mini_game", at(100), rec)
        assert await finish_mini_game_phase(db, seated.session_id, at(110), rec)
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "bridge")
        assert (await _ended_reasons(db, seated.session_id))[-1] == "mini_game_ended"

    @pytest.mark.asyncio
    async def test_a_stale_mini_game_end_changes_nothing(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        await reach_phase(db, seated, "beat_one", "choices", at(100), rec)
        before = await phase_event_count(db, seated.session_id)
        assert not await finish_mini_game_phase(db, seated.session_id, at(101), rec)
        assert await phase_event_count(db, seated.session_id) == before

    @pytest.mark.asyncio
    async def test_ready_does_not_end_the_mini_game_phase(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        await reach_phase(db, seated, "beat_one", "mini_game", at(100), rec)
        with pytest.raises(RoundError) as refused:
            await mark_ready(
                db, seated.session_id, seated.participants[0], at(101), rec
            )
        assert refused.value.code == "phase_not_ready_able"
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "mini_game")

    @pytest.mark.asyncio
    async def test_marking_ready_twice_saves_one_decision(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        await mark_ready(db, seated.session_id, seated.participants[0], at(1), rec)
        await mark_ready(db, seated.session_id, seated.participants[0], at(2), rec)
        count = await db.scalar(
            select(func.count())
            .select_from(Decision)
            .where(Decision.decision_type == "ready")
        )
        assert count == 1

    @pytest.mark.asyncio
    async def test_a_late_tick_ends_one_phase_and_does_not_skip_the_next(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        await tick(db, seated.session_id, at(5000), rec)
        assert (await where(db, seated.session_id))[:2] == ("opening", "bridge")
        view = await round_view(db, seated.session_id, at(5000))
        assert view.seconds_left == BRIDGE_SECONDS


def _next(phase: str) -> str:
    order = ["scene", "choices", "mini_game", "bridge"]
    return order[order.index(phase) + 1]


async def _ended_reasons(db: AsyncSession, session_id: UUID) -> list[str]:
    result = await db.execute(
        select(Event.payload).where(
            Event.session_id == session_id, Event.event_type == PHASE_EVENT
        )
    )
    rows = sorted(result.scalars().all(), key=lambda p: p["seq"])
    return [p["reason"] for p in rows if p["status"] == "ended"]


# --- the tick is safe to repeat -------------------------------------------------


class TestTickIsRepeatable:
    @pytest.mark.asyncio
    async def test_calling_the_tick_twice_at_the_same_moment_changes_once(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        first = await tick(db, seated.session_id, at(SCENE_SECONDS), rec)
        count = await phase_event_count(db, seated.session_id)
        events = len(rec.events)
        second = await tick(db, seated.session_id, at(SCENE_SECONDS), rec)
        assert first and not second
        assert await phase_event_count(db, seated.session_id) == count
        assert len(rec.events) == events

    @pytest.mark.asyncio
    async def test_a_tick_before_any_deadline_does_nothing(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        count = await phase_event_count(db, seated.session_id)
        assert not await tick(db, seated.session_id, at(SCENE_SECONDS - 1), rec)
        assert await phase_event_count(db, seated.session_id) == count

    @pytest.mark.asyncio
    async def test_a_session_not_started_is_left_alone(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        arc = phased_arc()
        registered(arc)
        seated = await seat_session(db, arc, start=False)
        assert not await tick(db, seated.session_id, at(0), Recorder())
        assert await current_phase(db, seated.session_id) is None

    @pytest.mark.asyncio
    async def test_an_unphased_arc_is_left_alone(self, db: AsyncSession) -> None:
        arc = load_arc_definition("nightcap-v1")
        assert arc is not None
        seated = await seat_session(db, arc)
        assert not await tick(db, seated.session_id, at(0), Recorder())
        assert await current_phase(db, seated.session_id) is None
        assert (await where(db, seated.session_id))[0] == arc.beats[0].beat_id


# --- moving from beat to beat ---------------------------------------------------


class TestBeatMovement:
    @pytest.mark.asyncio
    async def test_the_last_phase_of_a_beat_moves_to_the_next_beat(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        await reach_phase(db, seated, "beat_one", "bridge", at(10), rec)
        await tick(db, seated.session_id, at(10 + BRIDGE_SECONDS), rec)
        assert await where(db, seated.session_id) == ("beat_two", "scene", "running")
        transitions = await db.scalar(
            select(func.count())
            .select_from(Event)
            .where(Event.event_type == "beat_transition")
        )
        assert transitions == 2  # opening to beat_one, beat_one to beat_two

    @pytest.mark.asyncio
    async def test_the_final_beat_holds_after_its_last_phase(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        await reach_phase(db, seated, "finale", "scene", at(10), rec)
        await tick(db, seated.session_id, at(10 + SCENE_SECONDS), rec)
        assert await where(db, seated.session_id) == ("finale", "scene", "ended")
        count = await phase_event_count(db, seated.session_id)
        await tick(db, seated.session_id, at(9999), rec)
        assert await phase_event_count(db, seated.session_id) == count
        orm = await db.get(OrmSession, seated.session_id)
        assert orm is not None and orm.status == "active"

    @pytest.mark.asyncio
    async def test_a_gate_that_is_not_met_holds_the_beat_and_does_not_raise(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        from engine.session.obligations import REVEAL_READINESS_CONTEXT_KEY

        arc = phased_arc()
        data = arc.model_dump(mode="json")
        for beat in data["beats"]:
            if beat["beat_id"] == "beat_one":
                beat["exit_conditions"] = [REVEAL_READINESS_CONTEXT_KEY]
        data["obligations"] = [
            {"obligation_key": "hold", "description": "unmet", "mandatory": True}
        ]
        gated = ArcDefinition.model_validate(data)
        registered(gated)
        seated = await seat_session(db, gated)
        rec = Recorder()
        await tick(db, seated.session_id, at(0), rec)
        await reach_phase(db, seated, "beat_one", "bridge", at(10), rec)
        await tick(db, seated.session_id, at(10 + BRIDGE_SECONDS), rec)
        assert await where(db, seated.session_id) == ("beat_one", "bridge", "ended")
        count = await phase_event_count(db, seated.session_id)
        await tick(db, seated.session_id, at(10 + BRIDGE_SECONDS + 5), rec)
        assert await phase_event_count(db, seated.session_id) == count


# --- pause and resume -----------------------------------------------------------


class TestPauseAndResume:
    @pytest.mark.asyncio
    async def test_pause_then_resume_keeps_the_time_left_to_the_second(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        svc = SessionService()
        await svc.pause_session(db, seated.session_id, now=at(7))
        assert await where(db, seated.session_id) == ("opening", "scene", "paused")
        view = await round_view(db, seated.session_id, at(500))
        assert view.status == "paused"
        assert view.seconds_left == SCENE_SECONDS - 7
        await svc.resume_session(db, seated.session_id, now=at(500))
        assert await where(db, seated.session_id) == ("opening", "scene", "running")
        view = await round_view(db, seated.session_id, at(500))
        assert view.seconds_left == SCENE_SECONDS - 7

    @pytest.mark.asyncio
    async def test_the_clock_does_not_run_while_paused(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        svc = SessionService()
        await svc.pause_session(db, seated.session_id, now=at(7))
        assert not await tick(db, seated.session_id, at(9000), rec)
        await svc.resume_session(db, seated.session_id, now=at(500))
        assert not await tick(db, seated.session_id, at(500 + 12), rec)
        assert (await where(db, seated.session_id))[:2] == ("opening", "scene")
        assert await tick(db, seated.session_id, at(500 + 13), rec)
        assert (await where(db, seated.session_id))[:2] == ("opening", "bridge")

    @pytest.mark.asyncio
    async def test_a_player_ready_before_a_pause_is_still_ready_after_resume(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        first, second = seated.participants[0], seated.participants[1]
        await mark_ready(db, seated.session_id, first, at(1), rec)
        svc = SessionService()
        await svc.pause_session(db, seated.session_id, now=at(7))
        await svc.resume_session(db, seated.session_id, now=at(500))
        view = await round_view(db, seated.session_id, at(500))
        assert view.ready_count == 1
        await mark_ready(db, seated.session_id, second, at(501), rec)
        assert (await where(db, seated.session_id))[:2] == ("opening", "bridge")

    @pytest.mark.asyncio
    async def test_actions_are_refused_while_paused(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        await SessionService().pause_session(db, seated.session_id, now=at(7))
        with pytest.raises(RoundError) as ready:
            await mark_ready(db, seated.session_id, seated.participants[0], at(8), rec)
        assert ready.value.code == "session_not_active"
        with pytest.raises(RoundError) as move:
            await host_move_on(db, seated.session_id, at(8), rec)
        assert move.value.code == "session_not_active"


# --- who may mark ready ---------------------------------------------------------


class TestReadiness:
    @pytest.mark.asyncio
    async def test_a_ready_for_a_phase_that_has_moved_on_is_ignored(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        seen = await current_phase(db, seated.session_id)
        assert seen is not None
        await host_move_on(db, seated.session_id, at(5), rec)
        assert (await where(db, seated.session_id))[:2] == ("opening", "bridge")
        state = await mark_ready(
            db,
            seated.session_id,
            seated.participants[0],
            at(6),
            rec,
            phase_entry=seen.entry,
        )
        assert (state.phase, state.status) == ("bridge", "running")
        assert state.entry != seen.entry
        assert (await round_view(db, seated.session_id, at(6))).ready_count == 0
        count = await db.scalar(
            select(func.count())
            .select_from(Decision)
            .where(Decision.decision_type == "ready")
        )
        assert count == 0

    @pytest.mark.asyncio
    async def test_a_ready_for_the_current_phase_counts(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        seen = await current_phase(db, seated.session_id)
        assert seen is not None
        await mark_ready(
            db,
            seated.session_id,
            seated.participants[0],
            at(1),
            rec,
            phase_entry=seen.entry,
        )
        assert (await round_view(db, seated.session_id, at(1))).ready_count == 1

    @pytest.mark.asyncio
    async def test_a_stranger_cannot_mark_ready(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        with pytest.raises(RoundError) as refused:
            await mark_ready(db, seated.session_id, uuid4(), at(1), rec)
        assert refused.value.code == "not_a_participant"

    @pytest.mark.asyncio
    async def test_the_host_does_not_count_as_a_player(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        from engine.db.orm import SessionParticipant

        host_id = await db.scalar(
            select(SessionParticipant.participant_id).where(
                SessionParticipant.session_id == seated.session_id,
                SessionParticipant.surface_type == "host",
            )
        )
        assert host_id is not None
        with pytest.raises(RoundError) as refused:
            await mark_ready(db, seated.session_id, host_id, at(1), rec)
        assert refused.value.code == "not_a_participant"

    @pytest.mark.asyncio
    async def test_a_room_with_no_players_never_ends_a_phase_by_readiness(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        arc = phased_arc()
        registered(arc)
        seated = await seat_session(db, arc, players=0)
        await tick(db, seated.session_id, at(0), Recorder())
        await tick(db, seated.session_id, at(1), Recorder())
        assert (await where(db, seated.session_id))[:2] == ("opening", "scene")


# --- typed input no longer moves a phased arc -----------------------------------


class TestTypedInput:
    @pytest.mark.asyncio
    async def test_everyone_typing_does_not_change_beat_or_phase(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, _ = started
        service = CharacterService(sessions=SessionService())
        before = await where(db, seated.session_id)
        for participant, character in zip(seated.participants, seated.characters):
            await service.submit_input(
                db, seated.session_id, character, participant, "dialogue", "hello"
            )
        assert await where(db, seated.session_id) == before

    @pytest.mark.asyncio
    async def test_the_old_arc_still_advances_on_typed_input(
        self, db: AsyncSession
    ) -> None:
        arc = load_arc_definition("nightcap-v1")
        assert arc is not None
        seated = await seat_session(db, arc, players=1)
        service = CharacterService(sessions=SessionService())
        await service.submit_input(
            db,
            seated.session_id,
            seated.characters[0],
            seated.participants[0],
            "dialogue",
            "hello",
        )
        beat, _, _ = await where(db, seated.session_id)
        assert beat != arc.beats[0].beat_id


class TestRoundView:
    @pytest.mark.asyncio
    async def test_the_view_names_beat_phase_deadline_and_readiness(
        self, started: tuple[Seated, Recorder], db: AsyncSession
    ) -> None:
        seated, rec = started
        await mark_ready(db, seated.session_id, seated.participants[0], at(3), rec)
        view = await round_view(db, seated.session_id, at(5))
        assert (view.beat_id, view.phase, view.status) == (
            "opening",
            "scene",
            "running",
        )
        assert view.deadline_at == at(SCENE_SECONDS)
        assert view.seconds_left == SCENE_SECONDS - 5
        assert (view.ready_count, view.player_count) == (1, 2)
        assert [line["text"] for line in view.lines] == ["Welcome to the house."]
        assert view.beat_name == "opening"
        assert view.lines[0]["hints"]["pause_before_ms"] == 0

    @pytest.mark.asyncio
    async def test_the_view_of_a_session_with_no_phase_yet(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        arc = phased_arc()
        registered(arc)
        seated = await seat_session(db, arc, start=False)
        view = await round_view(db, seated.session_id, at(0))
        assert view.phase is None and view.status is None
        assert view.beat_id == "opening"


def test_a_helper_arc_has_five_beats() -> None:
    assert [b.beat_id for b in phased_arc().beats] == BEATS
