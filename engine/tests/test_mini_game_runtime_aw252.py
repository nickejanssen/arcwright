"""Tests for AW-252 additions to engine/mini_games/runtime.py.

Covers: cancel_run, resolve_run, get_active_run, clue delivery privacy
(specific_player per participant), and submission acknowledgement events.

All tests inject a frozen clock; no test touches wall time.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import (
    Account,
    Character,
    MiniGameRun,
    Session,
    SessionParticipant,
)
from engine.db.testing import make_sqlite_session_factory, patch_metadata_for_sqlite
from engine.events.bus import SessionEventBus
from engine.events.models import AudienceTarget, EventCategory
from engine.mini_games.models import (
    BehavioralOutputDeclaration,
    BehavioralScope,
    BehavioralValueType,
    ClueVariant,
    ContentMode,
    DelayedClueFallback,
)
from engine.mini_games.resolver import ResolvedMiniGameSnapshot
from engine.mini_games.runtime import (
    MechanicRegistry,
    MiniGameRuntime,
    MiniGameSubmission,
    RunStateError,
)

patch_metadata_for_sqlite()

T0 = datetime(2026, 6, 25, 12, 0, 0, tzinfo=timezone.utc)
MECHANIC = "test-mechanic"


# ---------------------------------------------------------------------------
# Stubs and helpers
# ---------------------------------------------------------------------------


class StubPlugin:
    mechanic_type: str = MECHANIC

    def __init__(
        self,
        *,
        threshold_met: bool = False,
        score_result: dict[str, Any] | None = None,
    ) -> None:
        self._threshold_met = threshold_met
        self._score_result = score_result or {}

    def validate_payload(self, payload: dict[str, Any]) -> None:
        pass

    def is_threshold_met(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
    ) -> bool:
        return self._threshold_met

    def score(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
    ) -> dict[str, Any]:
        return self._score_result


@pytest.fixture
async def db() -> AsyncSession:
    _, factory = await make_sqlite_session_factory()
    async with factory() as sess:
        yield sess


def make_bus() -> SessionEventBus:
    return SessionEventBus()


def frozen_clock(t: datetime = T0):
    return lambda: t


def make_registry(plugin: StubPlugin | None = None) -> MechanicRegistry:
    return MechanicRegistry([plugin or StubPlugin()])


def make_snapshot(
    *,
    clue_variant: ClueVariant = ClueVariant.full,
    resolved_content: dict[str, Any] | None = None,
) -> ResolvedMiniGameSnapshot:
    return ResolvedMiniGameSnapshot(
        game_id="test-game",
        definition_version="0.1.0",
        source_content_mode=ContentMode.authored,
        mechanic_type=MECHANIC,
        participation_mode="individual",
        min_players=1,
        max_players=8,
        duration_seconds=60,
        rules={},
        behavioral_outputs=(
            BehavioralOutputDeclaration(
                key="score",
                description="Score",
                value_type=BehavioralValueType.integer,
                scope=BehavioralScope.participant,
                derived=False,
            ),
        ),
        clue_fallback=DelayedClueFallback(
            delay_seconds=0,
            clue_variant=clue_variant,
            host_override=True,
        ),
        resolved_content=resolved_content
        or {
            "clues": [
                {"clue_id": "c1", "variant": "full", "content": {"text": "clue one"}},
            ]
        },
    )


async def _setup(
    db: AsyncSession,
    *,
    num_participants: int = 1,
) -> tuple[UUID, list[tuple[UUID, UUID]]]:
    """Insert session with N participants.

    Returns (session_id, [(char_id, participant_id), ...]).
    """
    account_id = uuid4()
    session_id = uuid4()

    db.add(Account(account_id=account_id, firebase_uid=f"uid-{account_id}"))
    await db.flush()

    db.add(
        Session(
            session_id=session_id,
            arc_id="arc-1",
            status="active",
            host_account_id=account_id,
            current_beat_id="beat-1",
            quality_tier="standard",
            player_count=num_participants,
        )
    )
    await db.flush()

    participants: list[tuple[UUID, UUID]] = []
    for _ in range(num_participants):
        char_id = uuid4()
        part_id = uuid4()
        db.add(Character(character_id=char_id, behavior_profile={}))
        await db.flush()
        db.add(
            SessionParticipant(
                participant_id=part_id,
                session_id=session_id,
                character_id=char_id,
                join_token=f"tok-{part_id}",
                surface_type="phone",
                is_ai_controlled=False,
            )
        )
        await db.flush()
        participants.append((char_id, part_id))

    return session_id, participants


async def _create_active_run(
    rt: MiniGameRuntime,
    session_id: UUID,
    snapshot: ResolvedMiniGameSnapshot | None = None,
) -> MiniGameRun:
    snap = snapshot or make_snapshot()
    run = await rt.create_run(session_id, snap)
    return await rt.start_run(run.run_id)


# ---------------------------------------------------------------------------
# cancel_run
# ---------------------------------------------------------------------------


class TestCancelRun:
    async def test_pending_run_transitions_to_cancelled(self, db: AsyncSession) -> None:
        session_id, _ = await _setup(db)
        bus = make_bus()
        rt = MiniGameRuntime(db, bus, make_registry(), clock=frozen_clock())

        run = await rt.create_run(session_id, make_snapshot())
        assert run.status == "pending"

        result = await rt.cancel_run(run.run_id)

        assert result.status == "cancelled"
        assert result.cancelled_at == T0

    async def test_active_run_transitions_to_cancelled(self, db: AsyncSession) -> None:
        session_id, _ = await _setup(db)
        bus = make_bus()
        rt = MiniGameRuntime(db, bus, make_registry(), clock=frozen_clock())

        run = await _create_active_run(rt, session_id)
        result = await rt.cancel_run(run.run_id)

        assert result.status == "cancelled"

    async def test_emits_state_transition_event_to_all(self, db: AsyncSession) -> None:
        session_id, _ = await _setup(db)
        bus = make_bus()
        rt = MiniGameRuntime(db, bus, make_registry(), clock=frozen_clock())
        run = await rt.create_run(session_id, make_snapshot())

        events_before = bus.last_sequence_number
        await rt.cancel_run(run.run_id)

        emitted = bus.replay_since(events_before)
        assert len(emitted) == 1
        evt = emitted[0]
        assert evt.category == EventCategory.state_transition
        assert evt.event_type == "mini_game_cancelled"
        assert evt.target_audience == AudienceTarget.all

    async def test_terminal_run_raises(self, db: AsyncSession) -> None:
        session_id, _ = await _setup(db, num_participants=1)
        bus = make_bus()
        plugin = StubPlugin(threshold_met=True)
        rt = MiniGameRuntime(db, bus, make_registry(plugin), clock=frozen_clock())

        run = await _create_active_run(rt, session_id)
        char_id = (
            await db.execute(
                select(SessionParticipant.character_id).where(
                    SessionParticipant.session_id == session_id
                )
            )
        ).scalar_one()
        await rt.submit_action(run.run_id, "sub-1", char_id, {})

        result = await db.get(MiniGameRun, run.run_id)
        assert result is not None
        # Threshold-met finalization may have changed the run; reload to confirm terminal
        await db.refresh(result)
        assert result.status == "completed"

        with pytest.raises(RunStateError, match="terminal"):
            await rt.cancel_run(run.run_id)


# ---------------------------------------------------------------------------
# resolve_run
# ---------------------------------------------------------------------------


class TestResolveRun:
    async def test_active_run_completes_with_scoring(self, db: AsyncSession) -> None:
        session_id, _ = await _setup(db)
        bus = make_bus()
        rt = MiniGameRuntime(db, bus, make_registry(), clock=frozen_clock())
        run = await _create_active_run(rt, session_id)

        result = await rt.resolve_run(run.run_id)

        assert result.status == "completed"
        assert result.completed_at == T0

    async def test_non_active_run_raises(self, db: AsyncSession) -> None:
        session_id, _ = await _setup(db)
        rt = MiniGameRuntime(db, make_bus(), make_registry(), clock=frozen_clock())
        run = await rt.create_run(session_id, make_snapshot())

        with pytest.raises(RunStateError, match="active"):
            await rt.resolve_run(run.run_id)


# ---------------------------------------------------------------------------
# get_active_run
# ---------------------------------------------------------------------------


class TestGetActiveRun:
    async def test_returns_active_run(self, db: AsyncSession) -> None:
        session_id, _ = await _setup(db)
        rt = MiniGameRuntime(db, make_bus(), make_registry(), clock=frozen_clock())
        run = await _create_active_run(rt, session_id)

        result = await rt.get_active_run(session_id)

        assert result is not None
        assert result.run_id == run.run_id

    async def test_returns_pending_run(self, db: AsyncSession) -> None:
        session_id, _ = await _setup(db)
        rt = MiniGameRuntime(db, make_bus(), make_registry(), clock=frozen_clock())
        run = await rt.create_run(session_id, make_snapshot())

        result = await rt.get_active_run(session_id)

        assert result is not None and result.run_id == run.run_id

    async def test_returns_none_when_no_run(self, db: AsyncSession) -> None:
        session_id, _ = await _setup(db)
        rt = MiniGameRuntime(db, make_bus(), make_registry(), clock=frozen_clock())

        assert await rt.get_active_run(session_id) is None

    async def test_returns_none_for_completed_run(self, db: AsyncSession) -> None:
        session_id, _ = await _setup(db)
        plugin = StubPlugin(threshold_met=True)
        rt = MiniGameRuntime(
            db, make_bus(), make_registry(plugin), clock=frozen_clock()
        )
        run = await _create_active_run(rt, session_id)
        char_id = (
            await db.execute(
                select(SessionParticipant.character_id).where(
                    SessionParticipant.session_id == session_id
                )
            )
        ).scalar_one()
        await rt.submit_action(run.run_id, "sub-1", char_id, {})

        assert await rt.get_active_run(session_id) is None

    async def test_eagerly_loads_submissions(self, db: AsyncSession) -> None:
        session_id, participants = await _setup(db)
        char_id, part_id = participants[0]
        rt = MiniGameRuntime(db, make_bus(), make_registry(), clock=frozen_clock())
        run = await _create_active_run(rt, session_id)
        await rt.submit_action(run.run_id, "sub-1", char_id, {}, participant_id=part_id)

        result = await rt.get_active_run(session_id)

        assert result is not None
        assert len(result.submissions) == 1
        assert result.submissions[0].submission_id == "sub-1"


# ---------------------------------------------------------------------------
# Clue delivery privacy (AC3)
# ---------------------------------------------------------------------------


class TestClueDeliveryPrivacy:
    async def test_clue_events_use_specific_player_per_participant(
        self, db: AsyncSession
    ) -> None:
        session_id, participants = await _setup(db, num_participants=2)
        part_ids = {p for _, p in participants}
        bus = make_bus()
        rt = MiniGameRuntime(db, bus, make_registry(), clock=frozen_clock())
        run = await _create_active_run(rt, session_id)

        events_before = bus.last_sequence_number
        await rt.override_clue_release(
            run.run_id,
            [{"clue_id": "c1", "variant": "full", "content": {"text": "secret"}}],
            uuid4(),
        )

        delivery_events = [
            e
            for e in bus.replay_since(events_before)
            if e.event_type == "mini_game_clue_delivery"
        ]
        assert len(delivery_events) == 2
        for evt in delivery_events:
            assert evt.category == EventCategory.private_delivery
            assert evt.target_audience == AudienceTarget.specific_player
            assert evt.target_player_id in part_ids
            assert "content" in evt.payload

    async def test_shared_display_receives_no_clue_content(
        self, db: AsyncSession
    ) -> None:
        session_id, _ = await _setup(db)
        bus = make_bus()
        rt = MiniGameRuntime(db, bus, make_registry(), clock=frozen_clock())
        run = await _create_active_run(rt, session_id)

        events_before = bus.last_sequence_number
        await rt.override_clue_release(
            run.run_id,
            [{"clue_id": "c1", "variant": "full", "content": {"text": "secret"}}],
            uuid4(),
        )

        display_acks = [
            e
            for e in bus.replay_since(events_before)
            if e.event_type == "mini_game_clue_acknowledged"
            and e.target_audience == AudienceTarget.shared_display
        ]
        assert len(display_acks) == 1
        assert "content" not in display_acks[0].payload
        assert "text" not in str(display_acks[0].payload)

    async def test_host_receives_clue_id_but_no_content(self, db: AsyncSession) -> None:
        session_id, _ = await _setup(db)
        bus = make_bus()
        rt = MiniGameRuntime(db, bus, make_registry(), clock=frozen_clock())
        run = await _create_active_run(rt, session_id)

        events_before = bus.last_sequence_number
        await rt.override_clue_release(
            run.run_id,
            [{"clue_id": "c1", "variant": "full", "content": {"text": "secret"}}],
            uuid4(),
        )

        host_acks = [
            e
            for e in bus.replay_since(events_before)
            if e.event_type == "mini_game_clue_acknowledged"
            and e.target_audience == AudienceTarget.host_only
        ]
        assert len(host_acks) == 1
        assert host_acks[0].payload["clue_id"] == "c1"
        assert "content" not in host_acks[0].payload


# ---------------------------------------------------------------------------
# Submission acknowledgement events
# ---------------------------------------------------------------------------


class TestSubmissionAckEvents:
    async def test_emits_specific_player_ack_when_participant_id_provided(
        self, db: AsyncSession
    ) -> None:
        session_id, participants = await _setup(db)
        char_id, part_id = participants[0]
        bus = make_bus()
        rt = MiniGameRuntime(db, bus, make_registry(), clock=frozen_clock())
        run = await _create_active_run(rt, session_id)

        events_before = bus.last_sequence_number
        await rt.submit_action(run.run_id, "sub-1", char_id, {}, participant_id=part_id)

        acks = [
            e
            for e in bus.replay_since(events_before)
            if e.event_type == "mini_game_submission_accepted"
        ]
        assert len(acks) == 1
        assert acks[0].category == EventCategory.acknowledgement
        assert acks[0].target_audience == AudienceTarget.specific_player
        assert acks[0].target_player_id == part_id
        assert acks[0].payload["submission_id"] == "sub-1"

    async def test_no_ack_event_without_participant_id(self, db: AsyncSession) -> None:
        session_id, participants = await _setup(db)
        char_id, _ = participants[0]
        bus = make_bus()
        rt = MiniGameRuntime(db, bus, make_registry(), clock=frozen_clock())
        run = await _create_active_run(rt, session_id)

        events_before = bus.last_sequence_number
        await rt.submit_action(run.run_id, "sub-1", char_id, {})

        acks = [
            e
            for e in bus.replay_since(events_before)
            if e.event_type == "mini_game_submission_accepted"
        ]
        assert len(acks) == 0

    async def test_emits_shared_display_progress_on_accepted_submission(
        self, db: AsyncSession
    ) -> None:
        session_id, participants = await _setup(db)
        char_id, part_id = participants[0]
        bus = make_bus()
        rt = MiniGameRuntime(db, bus, make_registry(), clock=frozen_clock())
        run = await _create_active_run(rt, session_id)

        events_before = bus.last_sequence_number
        await rt.submit_action(run.run_id, "sub-1", char_id, {}, participant_id=part_id)

        progress = [
            e
            for e in bus.replay_since(events_before)
            if e.event_type == "mini_game_submission_progress"
        ]
        assert len(progress) == 1
        assert progress[0].category == EventCategory.acknowledgement
        assert progress[0].target_audience == AudienceTarget.shared_display
        assert progress[0].payload["submission_count"] == 1

    async def test_idempotent_submission_returns_same_result(
        self, db: AsyncSession
    ) -> None:
        session_id, participants = await _setup(db)
        char_id, part_id = participants[0]
        rt = MiniGameRuntime(db, make_bus(), make_registry(), clock=frozen_clock())
        run = await _create_active_run(rt, session_id)

        sub1 = await rt.submit_action(
            run.run_id, "sub-dup", char_id, {}, participant_id=part_id
        )
        sub2 = await rt.submit_action(
            run.run_id, "sub-dup", char_id, {}, participant_id=part_id
        )

        assert sub1.submission_pk == sub2.submission_pk
        assert sub1.is_accepted == sub2.is_accepted
