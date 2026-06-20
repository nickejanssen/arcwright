"""Tests for the five MVP telemetry signals (AW-222).

Uses real SQLite in-memory DB via engine.db.testing.make_sqlite_session_factory.
Asserts actual Event rows are committed to the DB. The Event write itself is
never mocked.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from engine.arc.pacing import (
    PacingIntervention,
    PacingInterventionType,
    PacingRecommendedAction,
    PacingSignalSnapshot,
)
from engine.db.orm import Event
from engine.db.testing import make_sqlite_session_factory
from engine.knowledge.graph import assert_knowledge, get_character_knowledge
from engine.session.service import SessionService
from engine.telemetry.pacing import (
    record_pacing_intervention,
    record_pacing_intervention_outcome,
    record_tension_update,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture()
async def db_engine_factory() -> AsyncIterator[
    tuple[AsyncEngine, async_sessionmaker[AsyncSession]]
]:
    engine, factory = await make_sqlite_session_factory()
    try:
        yield engine, factory
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def db(
    db_engine_factory: tuple[AsyncEngine, async_sessionmaker[AsyncSession]],
) -> AsyncIterator[AsyncSession]:
    _, factory = db_engine_factory
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture()
def svc() -> SessionService:
    return SessionService()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _stall_intervention(beat_id: str = "investigation") -> PacingIntervention:
    snapshot = PacingSignalSnapshot(
        beat_id=beat_id,
        time_pressure=0.1,
        action_rate=0.1,
        suspicion=0.1,
        clue_coverage=0.1,
    )
    return PacingIntervention(
        intervention_type=PacingInterventionType.stall,
        recommended_action=PacingRecommendedAction.inject_clue_or_narrator_prompt,
        beat_id=beat_id,
        tension_score_at_trigger=0.2,
        threshold=0.3,
        signal_snapshot=snapshot,
    )


def _quality_upgrade_intervention(beat_id: str = "investigation") -> PacingIntervention:
    snapshot = PacingSignalSnapshot(
        beat_id=beat_id,
        time_pressure=0.9,
        action_rate=0.9,
        suspicion=0.9,
        clue_coverage=0.9,
    )
    return PacingIntervention(
        intervention_type=PacingInterventionType.quality_upgrade,
        recommended_action=PacingRecommendedAction.upgrade_quality_tier,
        beat_id=beat_id,
        tension_score_at_trigger=0.9,
        threshold=0.85,
        signal_snapshot=snapshot,
    )


async def _get_event(db: AsyncSession, session_id, event_type: str) -> Event | None:
    result = await db.execute(
        select(Event).where(
            Event.session_id == session_id,
            Event.event_type == event_type,
        )
    )
    return result.scalars().first()


async def _count_events(db: AsyncSession, session_id, event_type: str) -> int:
    result = await db.execute(
        select(Event).where(
            Event.session_id == session_id,
            Event.event_type == event_type,
        )
    )
    return len(result.scalars().all())


# ---------------------------------------------------------------------------
# Signal 1: beat_transition
# ---------------------------------------------------------------------------


class TestSignal1BeatTransition:
    @pytest.mark.asyncio
    async def test_event_row_has_all_payload_keys(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="test-arc", host_account_id=uuid4()
        )
        await svc.record_beat_transition(
            db,
            session.session_id,
            from_beat="arrival",
            to_beat="investigation",
            duration_seconds=120,
            player_action_count=4,
        )
        await db.flush()

        event = await _get_event(db, session.session_id, "beat_transition")
        assert event is not None
        assert event.payload["from_beat"] == "arrival"
        assert event.payload["to_beat"] == "investigation"
        assert event.payload["duration_seconds"] == 120
        assert event.payload["player_action_count"] == 4
        assert event.actor_char_id is None
        assert event.content_text is None


# ---------------------------------------------------------------------------
# Signal 2: tension_update / pacing_intervention / pacing_intervention_outcome
# ---------------------------------------------------------------------------


class TestSignal2PacingEvents:
    @pytest.mark.asyncio
    async def test_tension_update_writes_score_and_beat_id(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="test-arc", host_account_id=uuid4()
        )
        await record_tension_update(
            db, session.session_id, score=0.42, beat_id="investigation"
        )
        await db.flush()

        event = await _get_event(db, session.session_id, "tension_update")
        assert event is not None
        assert event.payload["score"] == pytest.approx(0.42)
        assert event.payload["beat_id"] == "investigation"
        assert event.actor_char_id is None
        assert event.content_text is None

    @pytest.mark.asyncio
    async def test_pacing_intervention_stall_writes_event(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="test-arc", host_account_id=uuid4()
        )
        await record_pacing_intervention(db, session.session_id, _stall_intervention())
        await db.flush()

        event = await _get_event(db, session.session_id, "pacing_intervention")
        assert event is not None
        assert event.payload["trigger_type"] == "stall"
        assert "tension_score_at_trigger" in event.payload
        assert "beat_id" in event.payload

    @pytest.mark.asyncio
    async def test_pacing_intervention_outcome_writes_resumed_flag(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="test-arc", host_account_id=uuid4()
        )
        await record_pacing_intervention_outcome(
            db,
            session.session_id,
            _stall_intervention(),
            outcome_resumed_within_60s=True,
        )
        await db.flush()

        event = await _get_event(db, session.session_id, "pacing_intervention_outcome")
        assert event is not None
        assert event.payload["trigger_type"] == "stall"
        assert "tension_score_at_trigger" in event.payload
        assert "beat_id" in event.payload
        assert event.payload["outcome_resumed_within_60s"] is True

    @pytest.mark.asyncio
    async def test_quality_upgrade_produces_no_pacing_intervention_row(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="test-arc", host_account_id=uuid4()
        )
        await record_pacing_intervention(
            db, session.session_id, _quality_upgrade_intervention()
        )
        await db.flush()

        count = await _count_events(db, session.session_id, "pacing_intervention")
        assert count == 0


# ---------------------------------------------------------------------------
# Signal 3: knowledge_constraint_activated
# ---------------------------------------------------------------------------


class TestSignal3KnowledgeConstraint:
    @pytest.mark.asyncio
    async def test_permitted_path_writes_event_with_fact_type(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="test-arc", host_account_id=uuid4()
        )
        character_id = uuid4()
        await assert_knowledge(
            db,
            session_id=session.session_id,
            character_id=character_id,
            fact_type="murder_weapon",
            fact_content={"weapon": "candlestick"},
        )
        await db.flush()

        await get_character_knowledge(
            db, session_id=session.session_id, character_id=character_id
        )
        await db.flush()

        event = await _get_event(
            db, session.session_id, "knowledge_constraint_activated"
        )
        assert event is not None
        assert event.payload["constraint_direction"] == "permitted"
        assert event.payload["fact_type"] == "murder_weapon"
        assert event.payload["provenance_chain_length"] >= 0
        assert str(event.actor_char_id) == str(character_id)
        assert event.content_text is None

    @pytest.mark.asyncio
    async def test_blocked_path_writes_event_with_empty_fact_type(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="test-arc", host_account_id=uuid4()
        )
        character_id = uuid4()

        await get_character_knowledge(
            db, session_id=session.session_id, character_id=character_id
        )
        await db.flush()

        event = await _get_event(
            db, session.session_id, "knowledge_constraint_activated"
        )
        assert event is not None
        assert event.payload["constraint_direction"] == "blocked"
        assert event.payload["fact_type"] == ""
        assert event.payload["provenance_chain_length"] == 0
        assert str(event.actor_char_id) == str(character_id)


# ---------------------------------------------------------------------------
# Signal 4: session_completed
# ---------------------------------------------------------------------------


class TestSignal4SessionCompleted:
    @pytest.mark.asyncio
    async def test_end_session_writes_completed_event_with_all_fields(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="test-arc", host_account_id=uuid4()
        )
        await svc.start_session(db, session.session_id)
        await svc.end_session(
            db,
            session.session_id,
            completion_type="full_arc",
            killer_identified=True,
        )
        await db.flush()

        event = await _get_event(db, session.session_id, "session_completed")
        assert event is not None
        assert event.payload["completion_type"] == "full_arc"
        assert event.payload["final_beat_reached"] == "arrival"
        assert event.payload["killer_identified"] is True
        assert "total_duration_seconds" in event.payload
        assert "player_count" in event.payload
        assert event.actor_char_id is None
        assert event.content_text is None

    @pytest.mark.asyncio
    async def test_session_completed_written_without_content_logging_flag(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        """AC3: session_completed is never gated behind CONTENT_LOGGING_ENABLED."""
        os.environ.pop("CONTENT_LOGGING_ENABLED", None)

        session, _ = await svc.create_session(
            db, arc_id="test-arc", host_account_id=uuid4()
        )
        await svc.end_session(db, session.session_id)
        await db.flush()

        event = await _get_event(db, session.session_id, "session_completed")
        assert event is not None
        assert event.content_text is None


# ---------------------------------------------------------------------------
# Signal 5: replay_intent
# ---------------------------------------------------------------------------


class TestSignal5ReplayIntent:
    @pytest.mark.asyncio
    async def test_write_replay_intent_writes_event_row(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="test-arc", host_account_id=uuid4()
        )
        await svc.write_replay_intent(
            db,
            session.session_id,
            intent="yes",
            collection_method="host_report",
        )
        await db.flush()

        event = await _get_event(db, session.session_id, "replay_intent")
        assert event is not None
        assert event.payload["intent"] == "yes"
        assert event.payload["collection_method"] == "host_report"
        assert event.actor_char_id is None
        assert event.content_text is None
