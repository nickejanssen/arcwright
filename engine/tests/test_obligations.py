"""Tests for the narrative obligations model (AW-271, spec 0065).

Covers the obligation lifecycle (register, misdirection creation,
resolution, expiration), the reveal-readiness session-context boolean,
telemetry emission to the events table, and the live-loop exit-condition
gate. Schema validation tests for the arc-level ObligationConfig live
here too.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from unittest.mock import patch
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from engine.arc.models import ArcDefinition, BeatDefinition, ObligationConfig
from engine.arc.pacing import (
    PacingIntervention,
    PacingInterventionType,
    PacingRecommendedAction,
    PacingSignalSnapshot,
)
from engine.db.orm import Base, Event, Obligation
from engine.db.testing import patch_metadata_for_sqlite
from engine.session.models import SessionStatus
from engine.session.obligations import (
    REVEAL_READINESS_CONTEXT_KEY,
    all_mandatory_obligations_resolved,
    create_misdirection_obligation,
    expire_open_obligations,
    register_authored_obligations,
    resolve_obligation,
    resolve_obligations_on_beat_entry,
)
from engine.session.service import SessionService

patch_metadata_for_sqlite()


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
    await engine.dispose()


@pytest.fixture()
def svc() -> SessionService:
    return SessionService()


def _beat(
    beat_id: str, step: int, entry: list[str], exit_: list[str]
) -> BeatDefinition:
    return BeatDefinition(
        beat_id=beat_id,
        beat_name=beat_id.title(),
        beat_type="investigation",
        story_circle_step=step,
        structural_function="surface_disruption",
        emotional_target="tense",
        information_goal="Players gather clues",
        tension_target=0.5,
        character_emphasis=[],
        generative_triggers=[],
        entry_conditions=entry,
        exit_conditions=exit_,
        pacing_config={"stall_threshold_seconds": 300},
        audience_targets=["all"],
    )


def _arc(
    *,
    obligations: list[ObligationConfig] | None = None,
    gate_reveal: bool = False,
    misdirection_obligation_mandatory: bool = False,
) -> ArcDefinition:
    """Three-beat arc: introduction -> investigation -> reveal.

    When ``gate_reveal`` is True, leaving investigation requires the
    reveal-readiness context key, exactly as an arc author would
    configure it (generic condition-name contract, architecture 03 §3.2).
    """
    investigation_exit = (
        [REVEAL_READINESS_CONTEXT_KEY] if gate_reveal else ["core_clues_revealed"]
    )
    return ArcDefinition(
        arc_id="test_arc",
        name="Test Arc",
        min_players=4,
        max_players=10,
        character_mode="generated",
        aesthetic_config={
            "selection_model": {},
            "asset_generation": {"background_art": "pre_produced_per_theme"},
        },
        arc_structure="story_circle",
        play_mode="imposter",
        narrator={
            "type": "host_persona",
            "surface": "shared_display",
            "persona_mode": "fixed",
            "behavior_triggers": ["beat_transition"],
            "omniscient": True,
            "player_addressable": True,
        },
        quality_tier_default="standard",
        characters=[],
        beats=[
            _beat("introduction", 1, [], ["all_players_ready"]),
            _beat("investigation", 4, [], investigation_exit),
            _beat("reveal", 8, [], ["session_complete"]),
        ],
        beat_graph={
            "introduction": ["investigation"],
            "investigation": ["reveal"],
            "reveal": [],
        },
        generative_elements={"killer_assignment": True},
        content_rails={
            "prohibited_categories": ["graphic_violence"],
            "thematic_warnings": [],
            "age_floor": 18,
        },
        knowledge_rules={},
        pacing_config={
            "w_time": 0.3,
            "w_action": 0.3,
            "w_suspicion": 0.2,
            "w_coverage": 0.2,
            "misdirection_obligation_mandatory": misdirection_obligation_mandatory,
        },
        obligations=obligations or [],
    )


def _misdirection_intervention(beat_id: str = "investigation") -> PacingIntervention:
    return PacingIntervention(
        intervention_type=PacingInterventionType.misdirection,
        recommended_action=PacingRecommendedAction.inject_misdirection,
        beat_id=beat_id,
        tension_score_at_trigger=0.82,
        threshold=0.80,
        signal_snapshot=PacingSignalSnapshot(
            beat_id=beat_id,
            time_pressure=0.8,
            action_rate=0.8,
            suspicion=0.9,
            clue_coverage=0.8,
        ),
    )


async def _events_of_type(db: AsyncSession, event_type: str) -> list[Event]:
    result = await db.execute(select(Event).where(Event.event_type == event_type))
    return list(result.scalars().all())


async def _make_session(svc: SessionService, db: AsyncSession, arc: ArcDefinition):
    with patch("engine.session.service.load_arc_definition", return_value=arc):
        session, _token = await svc.create_session(
            db, arc_id="test_arc-v1", host_account_id=uuid4()
        )
        session = await svc.start_session(db, session.session_id)
    return session


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


class TestObligationConfigValidation:
    def test_arc_without_obligations_remains_valid(self) -> None:
        arc = _arc()
        assert arc.obligations == []

    def test_duplicate_obligation_keys_rejected(self) -> None:
        with pytest.raises(ValueError, match="duplicate keys"):
            _arc(
                obligations=[
                    ObligationConfig(obligation_key="setup", description="a"),
                    ObligationConfig(obligation_key="setup", description="b"),
                ]
            )

    def test_unknown_resolution_beat_rejected(self) -> None:
        with pytest.raises(ValueError, match="unknown resolve_on_beat_entry"):
            _arc(
                obligations=[
                    ObligationConfig(
                        obligation_key="setup",
                        description="a",
                        resolve_on_beat_entry="no_such_beat",
                    )
                ]
            )


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


class TestObligationLifecycle:
    @pytest.mark.asyncio
    async def test_register_authored_obligations_creates_rows_and_telemetry(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        arc = _arc(
            obligations=[
                ObligationConfig(
                    obligation_key="locket_setup",
                    description="The locket shown in act one must pay off.",
                    mandatory=True,
                    resolve_on_beat_entry="reveal",
                ),
                ObligationConfig(
                    obligation_key="rumor_thread",
                    description="The rumor thread should be addressed.",
                ),
            ]
        )
        session = await _make_session(svc, db, arc)

        rows = (await db.execute(select(Obligation))).scalars().all()
        assert {row.source_ref["obligation_key"] for row in rows} == {
            "locket_setup",
            "rumor_thread",
        }
        assert all(row.status == "open" for row in rows)
        assert all(row.source_type == "authored" for row in rows)
        created_events = await _events_of_type(db, "obligation_created")
        assert len(created_events) == 2
        payload_keys = set(created_events[0].payload)
        assert payload_keys == {"obligation_id", "source_type", "mandatory", "beat_id"}

        # Idempotent: a second registration creates nothing new.
        again = await register_authored_obligations(
            db, session.session_id, arc, created_beat="introduction"
        )
        assert again == []

    @pytest.mark.asyncio
    async def test_misdirection_obligation_row_and_telemetry(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session = await _make_session(svc, db, _arc())
        obligation = await create_misdirection_obligation(
            db, session.session_id, _misdirection_intervention(), mandatory=True
        )
        assert obligation.source_type == "pacing_misdirection"
        assert obligation.mandatory is True
        assert obligation.created_beat == "investigation"
        assert obligation.source_ref["tension_score_at_trigger"] == 0.82
        assert len(await _events_of_type(db, "obligation_created")) == 1

    @pytest.mark.asyncio
    async def test_resolution_updates_row_and_emits_telemetry(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session = await _make_session(svc, db, _arc())
        obligation = await create_misdirection_obligation(
            db, session.session_id, _misdirection_intervention(), mandatory=True
        )

        resolved = await resolve_obligation(db, obligation, resolved_beat="reveal")

        assert resolved.status == "resolved"
        assert resolved.resolved_beat == "reveal"
        assert resolved.resolved_at is not None
        events = await _events_of_type(db, "obligation_resolved")
        assert len(events) == 1
        payload = events[0].payload
        assert payload["resolution_beat"] == "reveal"
        assert payload["open_duration_seconds"] >= 0.0

        # Resolving twice is a no-op with no duplicate telemetry.
        await resolve_obligation(db, obligation, resolved_beat="reveal")
        assert len(await _events_of_type(db, "obligation_resolved")) == 1

    @pytest.mark.asyncio
    async def test_beat_entry_trigger_resolves_matching_obligations_only(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        arc = _arc(
            obligations=[
                ObligationConfig(
                    obligation_key="pays_off_at_reveal",
                    description="resolves on reveal entry",
                    mandatory=True,
                    resolve_on_beat_entry="reveal",
                ),
                ObligationConfig(
                    obligation_key="never_auto_resolves",
                    description="no beat trigger",
                ),
            ]
        )
        session = await _make_session(svc, db, arc)

        resolved = await resolve_obligations_on_beat_entry(
            db, session.session_id, entered_beat_id="reveal"
        )

        assert [o.source_ref["obligation_key"] for o in resolved] == [
            "pays_off_at_reveal"
        ]
        remaining_open = (
            (await db.execute(select(Obligation).where(Obligation.status == "open")))
            .scalars()
            .all()
        )
        assert [o.source_ref["obligation_key"] for o in remaining_open] == [
            "never_auto_resolves"
        ]

    @pytest.mark.asyncio
    async def test_session_end_expires_open_obligations(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        arc = _arc(
            obligations=[
                ObligationConfig(obligation_key="dangling", description="left open"),
            ]
        )
        session = await _make_session(svc, db, arc)

        await svc.end_session(db, session.session_id)

        rows = (await db.execute(select(Obligation))).scalars().all()
        assert [row.status for row in rows] == ["expired"]

    @pytest.mark.asyncio
    async def test_expire_open_obligations_direct(self, svc, db) -> None:
        session = await _make_session(svc, db, _arc())
        await create_misdirection_obligation(
            db, session.session_id, _misdirection_intervention(), mandatory=False
        )
        expired = await expire_open_obligations(db, session.session_id)
        assert len(expired) == 1
        assert expired[0].status == "expired"


# ---------------------------------------------------------------------------
# Reveal-readiness boolean
# ---------------------------------------------------------------------------


class TestRevealReadiness:
    @pytest.mark.asyncio
    async def test_true_with_no_obligations(self, svc, db) -> None:
        session = await _make_session(svc, db, _arc())
        assert await all_mandatory_obligations_resolved(db, session.session_id)

    @pytest.mark.asyncio
    async def test_open_mandatory_blocks_and_resolution_unblocks(self, svc, db) -> None:
        session = await _make_session(svc, db, _arc())
        obligation = await create_misdirection_obligation(
            db, session.session_id, _misdirection_intervention(), mandatory=True
        )
        assert not await all_mandatory_obligations_resolved(db, session.session_id)

        await resolve_obligation(db, obligation, resolved_beat="reveal")
        assert await all_mandatory_obligations_resolved(db, session.session_id)

    @pytest.mark.asyncio
    async def test_open_non_mandatory_does_not_block(self, svc, db) -> None:
        session = await _make_session(svc, db, _arc())
        await create_misdirection_obligation(
            db, session.session_id, _misdirection_intervention(), mandatory=False
        )
        assert await all_mandatory_obligations_resolved(db, session.session_id)


# ---------------------------------------------------------------------------
# Live-loop integration: exit-condition gate and misdirection hook
# ---------------------------------------------------------------------------


class TestLiveLoopIntegration:
    @pytest.mark.asyncio
    async def test_reveal_gate_holds_then_releases(self, svc, db) -> None:
        """AC: the reveal-readiness key gates a test arc's exit condition."""
        arc = _arc(gate_reveal=True)
        session = await _make_session(svc, db, arc)

        with patch("engine.session.service.load_arc_definition", return_value=arc):
            # introduction -> investigation advances normally.
            state = await svc.advance_live_session_on_input(db, session.session_id)
            assert state.current_beat_id == "investigation"

            obligation = await create_misdirection_obligation(
                db, session.session_id, _misdirection_intervention(), mandatory=True
            )

            # Gate holds: open mandatory obligation blocks investigation -> reveal.
            state = await svc.advance_live_session_on_input(db, session.session_id)
            assert state.current_beat_id == "investigation"
            assert state.status is SessionStatus.active

            # Gate releases after deterministic resolution.
            await resolve_obligation(db, obligation, resolved_beat="investigation")
            state = await svc.advance_live_session_on_input(db, session.session_id)
            assert state.current_beat_id == "reveal"

    @pytest.mark.asyncio
    async def test_live_misdirection_intervention_creates_obligation(
        self, svc, db
    ) -> None:
        """AC: pacing misdirection injection writes an obligation record."""
        arc = _arc(misdirection_obligation_mandatory=True)
        session = await _make_session(svc, db, arc)

        with (
            patch("engine.session.service.load_arc_definition", return_value=arc),
            patch(
                "engine.arc.pacing.evaluate_pacing_interventions",
                return_value=[_misdirection_intervention()],
            ),
        ):
            await svc.advance_live_session_on_input(db, session.session_id)

        rows = (
            (
                await db.execute(
                    select(Obligation).where(
                        Obligation.source_type == "pacing_misdirection"
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(rows) == 1
        assert rows[0].mandatory is True
        assert len(await _events_of_type(db, "obligation_created")) == 1
