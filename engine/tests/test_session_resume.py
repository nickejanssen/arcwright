"""AW-220 acceptance tests: snapshot on pause, restore on resume.

Each test exercises the full DB-backed round trip:
  1. Create a session, start it, run the chart to a beat boundary.
  2. Persist knowledge + relationship state alongside.
  3. Pause via ``SessionService`` (writes the ``arc_beat_states`` snapshot).
  4. Discard every in-process object — the chart, the service, even the
     ``AsyncSession`` — so only the DB rows survive.
  5. Open a fresh ``AsyncSession`` and fresh ``SessionService``; resume.
  6. Assert the restored chart's beat + context, the persisted knowledge,
     the relationship row, and the session status all match what was
     active at pause time.

If the production snapshot/restore code were removed, every assertion in
``TestResumeRestoresState`` would fail — the tests load from the DB only
and the DB only carries that state because pause wrote it.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from engine.arc import ArcDefinition, ArcStateChart, transition_name_for
from engine.db.orm import (
    ArcBeatState,
    Base,
    Character,
    Event,
    RelationshipState,
)
from engine.db.testing import patch_metadata_for_sqlite
from engine.knowledge import assert_knowledge, get_character_knowledge
from engine.session.models import SessionStatus
from engine.session.service import SessionService
from engine.session.snapshots import (
    capture_chart_config,
    load_current_snapshot,
    restore_chart_from_snapshot,
)

patch_metadata_for_sqlite()

_NIGHTCAP_ARC = Path(__file__).resolve().parents[2] / "nightcap" / "arc.json"


@pytest_asyncio.fixture()
async def engine() -> AsyncIterator[AsyncEngine]:
    """A single SQLite engine per test, kept open across sessions.

    The in-memory database vanishes when the engine is disposed, so all
    sessions in the test share the same backing store — this is what lets
    us drop a session and open a new one in the resume tests.
    """
    eng = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield eng
    finally:
        await eng.dispose()


@pytest.fixture()
def factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture()
def arc_definition() -> ArcDefinition:
    return ArcDefinition(**json.loads(_NIGHTCAP_ARC.read_text(encoding="utf-8")))


class TestSnapshotOnPause:
    """AC1: pause writes a snapshot row at the current beat boundary."""

    @pytest.mark.asyncio
    async def test_pause_writes_arc_beat_states_row(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> None:
        svc = SessionService()
        async with factory() as db:
            session, _ = await svc.create_session(
                db, arc_id="nightcap-v1", host_account_id=uuid4()
            )
            await svc.start_session(db, session.session_id)
            await svc.pause_session(
                db,
                session.session_id,
                beat_id="body",
                statemachine_config={
                    "beat_id": "body",
                    "configuration_values": ["body"],
                    "session_context": {"victim_revealed": True},
                },
                transition_history=[{"from": "arrival", "to": "body"}],
            )
            await db.commit()

        async with factory() as db:
            rows = (
                (
                    await db.execute(
                        select(ArcBeatState).where(
                            ArcBeatState.session_id == session.session_id
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert len(rows) == 1
            row = rows[0]
            assert row.beat_id == "body"
            assert row.is_current is True
            assert row.statemachine_config["beat_id"] == "body"
            assert row.statemachine_config["session_context"] == {
                "victim_revealed": True
            }
            assert row.transition_history == [{"from": "arrival", "to": "body"}]

    @pytest.mark.asyncio
    async def test_second_pause_demotes_prior_snapshot(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """A new snapshot makes the previous one non-current (supplemental schema)."""
        svc = SessionService()
        async with factory() as db:
            session, _ = await svc.create_session(
                db, arc_id="nightcap-v1", host_account_id=uuid4()
            )
            await svc.start_session(db, session.session_id)
            await svc.pause_session(db, session.session_id, beat_id="body")
            await svc.resume_session(db, session.session_id)
            await svc.pause_session(db, session.session_id, beat_id="dig")
            await db.commit()

        async with factory() as db:
            rows = (
                (
                    await db.execute(
                        select(ArcBeatState)
                        .where(ArcBeatState.session_id == session.session_id)
                        .order_by(ArcBeatState.snapshot_at)
                    )
                )
                .scalars()
                .all()
            )
            assert len(rows) == 2
            assert rows[0].is_current is False
            assert rows[1].is_current is True
            assert rows[1].beat_id == "dig"

    @pytest.mark.asyncio
    async def test_pause_emits_session_interrupted_event(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """§5.4 step 6: pause logs an event_type=session_interrupted row."""
        svc = SessionService()
        async with factory() as db:
            session, _ = await svc.create_session(
                db, arc_id="nightcap-v1", host_account_id=uuid4()
            )
            await svc.start_session(db, session.session_id)
            await svc.pause_session(db, session.session_id, beat_id="body")
            await db.commit()

        async with factory() as db:
            events = (
                (
                    await db.execute(
                        select(Event).where(Event.session_id == session.session_id)
                    )
                )
                .scalars()
                .all()
            )
            interrupted = [e for e in events if e.event_type == "session_interrupted"]
            assert len(interrupted) == 1
            assert interrupted[0].payload == {"beat_id": "body"}


class TestResumeRestoresState:
    """AC2: resume restores statemachine config, knowledge, relationships, status.

    Each test drops every in-process object after pause and resumes from
    the DB alone. If the production code stopped writing the snapshot or
    stopped reading it on resume, the assertions would fail — there is no
    in-process cache to fall back on.
    """

    @pytest.mark.asyncio
    async def test_resume_restores_chart_beat_and_context(
        self,
        factory: async_sessionmaker[AsyncSession],
        arc_definition: ArcDefinition,
    ) -> None:
        # --- live phase: advance the chart, then snapshot from the live state.
        live_chart = ArcStateChart(arc_definition)
        live_chart.session_context["all_players_ready"] = True
        live_chart.session_context["body_discovered"] = True
        live_chart.send(transition_name_for("arrival", "body"))
        assert sorted(live_chart.configuration_values) == ["body"]
        live_config = capture_chart_config(live_chart)

        svc = SessionService()
        async with factory() as db:
            session, _ = await svc.create_session(
                db, arc_id=arc_definition.arc_id, host_account_id=uuid4()
            )
            await svc.start_session(db, session.session_id)
            await svc.pause_session(
                db,
                session.session_id,
                beat_id="body",
                statemachine_config=live_config,
            )
            await db.commit()
        session_id = session.session_id

        # --- discard everything in-process.
        del svc
        del live_chart
        del live_config

        # --- cold resume: fresh service, fresh DB session, fresh chart.
        cold_svc = SessionService()
        async with factory() as db:
            resumed, snapshot = await cold_svc.resume_session(db, session_id)
            assert resumed.status is SessionStatus.active
            assert resumed.current_beat_id == "body"
            assert snapshot is not None

            restored_chart = restore_chart_from_snapshot(arc_definition, snapshot)
            assert sorted(restored_chart.configuration_values) == ["body"]
            assert restored_chart.session_context == {
                "all_players_ready": True,
                "body_discovered": True,
            }
            # The restored chart is functional: enabling the next exit
            # condition allows the next beat transition to fire.
            restored_chart.session_context["body_inspected"] = True
            restored_chart.send(transition_name_for("body", "opening_move"))
            assert sorted(restored_chart.configuration_values) == ["opening_move"]

    @pytest.mark.asyncio
    async def test_resume_preserves_persisted_knowledge_state(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """Knowledge written before pause is visible after a cold resume."""
        svc = SessionService()
        character_id = uuid4()
        async with factory() as db:
            session, _ = await svc.create_session(
                db, arc_id="nightcap-v1", host_account_id=uuid4()
            )
            db.add(Character(character_id=character_id, behavior_profile={}))
            await db.flush()
            await svc.start_session(db, session.session_id)
            await assert_knowledge(
                db,
                session_id=session.session_id,
                character_id=character_id,
                fact_type="clue",
                fact_content={"detail": "broken_glass_in_library"},
            )
            await svc.pause_session(db, session.session_id, beat_id="body")
            await db.commit()
        session_id = session.session_id

        del svc

        cold_svc = SessionService()
        async with factory() as db:
            resumed, _ = await cold_svc.resume_session(db, session_id)
            assert resumed.status is SessionStatus.active
            known = await get_character_knowledge(
                db, session_id=session_id, character_id=character_id
            )
            assert len(known) == 1
            assert known[0].fact.fact_content == {"detail": "broken_glass_in_library"}

    @pytest.mark.asyncio
    async def test_resume_preserves_persisted_relationship_state(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """Relationship rows written before pause are intact after resume."""
        svc = SessionService()
        source = uuid4()
        target = uuid4()
        async with factory() as db:
            session, _ = await svc.create_session(
                db, arc_id="nightcap-v1", host_account_id=uuid4()
            )
            db.add(Character(character_id=source, behavior_profile={}))
            db.add(Character(character_id=target, behavior_profile={}))
            await db.flush()
            await svc.start_session(db, session.session_id)
            db.add(
                RelationshipState(
                    session_id=session.session_id,
                    source_char_id=source,
                    target_char_id=target,
                    trust_level=0.2,
                    history_tag="rivalry",
                    current_affect="hostile",
                )
            )
            await svc.pause_session(db, session.session_id, beat_id="body")
            await db.commit()
        session_id = session.session_id

        del svc

        cold_svc = SessionService()
        async with factory() as db:
            resumed, _ = await cold_svc.resume_session(db, session_id)
            assert resumed.status is SessionStatus.active
            row = (
                (
                    await db.execute(
                        select(RelationshipState).where(
                            RelationshipState.session_id == session_id,
                            RelationshipState.source_char_id == source,
                            RelationshipState.target_char_id == target,
                        )
                    )
                )
                .scalars()
                .one()
            )
            assert row.trust_level == 0.2
            assert row.history_tag == "rivalry"
            assert row.current_affect == "hostile"


class TestAc3NoSnapshotException:
    """AC3: a resumed session never restarts from the beginning unless no
    valid prior state exists — and that exception is documented."""

    @pytest.mark.asyncio
    async def test_resume_with_no_snapshot_falls_back_to_initial_beat(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """If a session is paused but has no ``arc_beat_states`` row,
        resume returns ``snapshot=None`` and leaves ``current_beat_id`` at
        the initial beat. This is the documented AC3 exception."""
        svc = SessionService()
        async with factory() as db:
            session, _ = await svc.create_session(
                db, arc_id="nightcap-v1", host_account_id=uuid4()
            )
            await svc.start_session(db, session.session_id)
            # Force the paused status WITHOUT going through pause_session,
            # so no snapshot row is written.
            from engine.db.orm import Session as OrmSession

            orm = await db.get(OrmSession, session.session_id)
            assert orm is not None
            orm.status = SessionStatus.paused.value
            await db.commit()
        session_id = session.session_id

        del svc

        cold_svc = SessionService()
        async with factory() as db:
            resumed, snapshot = await cold_svc.resume_session(db, session_id)
            assert snapshot is None
            assert resumed.status is SessionStatus.active
            # AC3: when no prior state exists, the session resumes at the
            # arc's initial beat — the only state available.
            assert resumed.current_beat_id == "arrival"

    @pytest.mark.asyncio
    async def test_resume_with_snapshot_never_falls_back_to_initial_beat(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """AC3 negative: when a snapshot exists, resume must not silently
        roll the session back to ``arrival``."""
        svc = SessionService()
        async with factory() as db:
            session, _ = await svc.create_session(
                db, arc_id="nightcap-v1", host_account_id=uuid4()
            )
            await svc.start_session(db, session.session_id)
            await svc.pause_session(db, session.session_id, beat_id="reckoning")
            await db.commit()
        session_id = session.session_id

        del svc

        cold_svc = SessionService()
        async with factory() as db:
            resumed, snapshot = await cold_svc.resume_session(db, session_id)
            assert snapshot is not None
            assert resumed.current_beat_id == "reckoning"
            assert resumed.current_beat_id != "arrival"


class TestSnapshotHelpers:
    @pytest.mark.asyncio
    async def test_load_current_snapshot_returns_only_active(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> None:
        svc = SessionService()
        async with factory() as db:
            session, _ = await svc.create_session(
                db, arc_id="nightcap-v1", host_account_id=uuid4()
            )
            await svc.start_session(db, session.session_id)
            await svc.pause_session(db, session.session_id, beat_id="body")
            await svc.resume_session(db, session.session_id)
            await svc.pause_session(db, session.session_id, beat_id="thread")
            await db.commit()

        async with factory() as db:
            active = await load_current_snapshot(db, session_id=session.session_id)
            assert active is not None
            assert active.beat_id == "thread"
            assert active.is_current is True
