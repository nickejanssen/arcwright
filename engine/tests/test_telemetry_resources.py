"""Tests for resource-economy telemetry (spec 0075, AW-287, Task 9).

Mirrors engine/tests/test_obligations.py's fixture and mocking strategy
exactly: a direct in-memory SQLite engine via patch_metadata_for_sqlite,
a real session row created through SessionService, and Event rows read
back with a plain SQLAlchemy select. The Event write itself is never
mocked.

Payload-builder tests are pure (no DB) and assert each function's output
against a fixed allowlist of permitted keys, proving no private content
(free text, copied observations) can leak into resource telemetry.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from engine.db.orm import Base, Event
from engine.db.testing import patch_metadata_for_sqlite
from engine.resources.models import EffectActivation, ResourceGrant, ResourceSpend
from engine.session.service import SessionService
from engine.telemetry.resources import (
    build_resource_counterplay_payload,
    build_resource_grant_payload,
    build_resource_outcome_payload,
    build_resource_recovery_payload,
    build_resource_spend_payload,
    build_resource_target_payload,
    record_resource_counterplay,
    record_resource_grant,
    record_resource_outcome,
    record_resource_recovery,
    record_resource_spend,
    record_resource_target,
)

patch_metadata_for_sqlite()

NOW = datetime(2026, 7, 19, tzinfo=timezone.utc)
SESSION_ID = "00000000-0000-0000-0000-000000000090"
PLAYER_A = "00000000-0000-0000-0000-000000000091"
PLAYER_B = "00000000-0000-0000-0000-000000000092"


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


async def _events_of_type(db: AsyncSession, event_type: str) -> list[Event]:
    result = await db.execute(select(Event).where(Event.event_type == event_type))
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Payload builders: no-private-content allowlist assertions (pure, no DB)
# ---------------------------------------------------------------------------


class TestPayloadBuildersContainNoPrivateContent:
    def test_grant_payload_matches_allowlist(self) -> None:
        grant = ResourceGrant(
            player_id=PLAYER_A,
            session_id=SESSION_ID,
            amount=4,
            source="mini_game_reward",
            beat_id="b1",
            timestamp=NOW,
        )
        payload = build_resource_grant_payload(grant)
        assert set(payload) == {"player_id", "amount", "source", "beat_id"}
        assert payload["player_id"] == PLAYER_A
        assert payload["amount"] == 4
        assert payload["source"] == "mini_game_reward"
        assert payload["beat_id"] == "b1"

    def test_spend_payload_matches_allowlist(self) -> None:
        spend = ResourceSpend(
            player_id=PLAYER_A,
            session_id=SESSION_ID,
            amount=2,
            effect_key="advantage.deep_read",
            beat_id="b1",
            timestamp=NOW,
        )
        payload = build_resource_spend_payload(spend)
        assert set(payload) == {"player_id", "amount", "effect_key", "beat_id"}
        assert payload["effect_key"] == "advantage.deep_read"

    def test_target_payload_matches_allowlist(self) -> None:
        activation = EffectActivation(
            effect_key="sabotage.rattle_the_witness",
            activator_id=PLAYER_A,
            target_id=PLAYER_B,
            interaction_window_id="w1",
        )
        payload = build_resource_target_payload(activation, beat_id="b1")
        assert set(payload) == {
            "effect_key",
            "activator_id",
            "target_id",
            "window_id",
            "beat_id",
        }
        assert payload["activator_id"] == PLAYER_A
        assert payload["target_id"] == PLAYER_B

    def test_target_payload_requires_a_target(self) -> None:
        activation = EffectActivation(
            effect_key="advantage.deep_read",
            activator_id=PLAYER_A,
            target_id=None,
            interaction_window_id="w1",
        )
        with pytest.raises(ValueError, match="targeted activation"):
            build_resource_target_payload(activation, beat_id="b1")

    def test_outcome_payload_matches_allowlist(self) -> None:
        activation = EffectActivation(
            effect_key="sabotage.rattle_the_witness",
            activator_id=PLAYER_A,
            target_id=PLAYER_B,
            interaction_window_id="w1",
            resolved_at=NOW,
            source_reveal_at=NOW,
        )
        payload = build_resource_outcome_payload(activation, beat_id="b1")
        assert set(payload) == {
            "effect_key",
            "activator_id",
            "target_id",
            "window_id",
            "beat_id",
            "source_revealed",
        }
        assert payload["source_revealed"] is True

    def test_outcome_payload_source_revealed_false_when_not_revealed(self) -> None:
        activation = EffectActivation(
            effect_key="advantage.deep_read",
            activator_id=PLAYER_A,
            target_id=None,
            interaction_window_id="w1",
        )
        payload = build_resource_outcome_payload(activation, beat_id="b1")
        assert payload["source_revealed"] is False

    def test_counterplay_payload_matches_allowlist(self) -> None:
        payload = build_resource_counterplay_payload(
            countering_activator_id=PLAYER_B,
            countered_activator_id=PLAYER_A,
            countered_window_id="w1",
            beat_id="b1",
        )
        assert set(payload) == {
            "countering_activator_id",
            "countered_activator_id",
            "countered_window_id",
            "beat_id",
        }
        assert payload["countering_activator_id"] == PLAYER_B
        assert payload["countered_activator_id"] == PLAYER_A

    def test_recovery_payload_matches_allowlist(self) -> None:
        payload = build_resource_recovery_payload(
            recovered_player_id=PLAYER_B, beat_id="b2"
        )
        assert set(payload) == {"recovered_player_id", "beat_id"}
        assert payload["recovered_player_id"] == PLAYER_B

    @pytest.mark.parametrize(
        "payload",
        [
            build_resource_grant_payload(
                ResourceGrant(
                    player_id=PLAYER_A,
                    session_id=SESSION_ID,
                    amount=4,
                    source="mini_game_reward",
                    beat_id="b1",
                    timestamp=NOW,
                )
            ),
            build_resource_spend_payload(
                ResourceSpend(
                    player_id=PLAYER_A,
                    session_id=SESSION_ID,
                    amount=2,
                    effect_key="advantage.deep_read",
                    beat_id="b1",
                    timestamp=NOW,
                )
            ),
            build_resource_counterplay_payload(
                countering_activator_id=PLAYER_B,
                countered_activator_id=PLAYER_A,
                countered_window_id="w1",
                beat_id="b1",
            ),
            build_resource_recovery_payload(recovered_player_id=PLAYER_B, beat_id="b2"),
        ],
    )
    def test_payload_values_are_scalar_never_free_text_blobs(
        self, payload: dict
    ) -> None:
        """Every value is a short structural scalar (id/amount/tag/bool), never a
        long free-text string that could carry copied private-observation content.
        """
        for value in payload.values():
            assert isinstance(value, (str, int, bool)) or value is None
            if isinstance(value, str):
                assert len(value) <= 64


# ---------------------------------------------------------------------------
# Recorders: real Event rows written to the events table
# ---------------------------------------------------------------------------


async def _make_session(svc: SessionService, db: AsyncSession):
    session, _token = await svc.create_session(
        db, arc_id="nightcap-v1", host_account_id=uuid4()
    )
    return session


class TestRecorders:
    @pytest.mark.asyncio
    async def test_record_resource_grant_writes_event(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session = await _make_session(svc, db)
        grant = ResourceGrant(
            player_id=PLAYER_A,
            session_id=str(session.session_id),
            amount=4,
            source="mini_game_reward",
            beat_id="b1",
            timestamp=NOW,
        )
        await record_resource_grant(db, session.session_id, grant)

        events = await _events_of_type(db, "resource_grant")
        assert len(events) == 1
        assert events[0].payload == build_resource_grant_payload(grant)

    @pytest.mark.asyncio
    async def test_record_resource_spend_writes_event(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session = await _make_session(svc, db)
        spend = ResourceSpend(
            player_id=PLAYER_A,
            session_id=str(session.session_id),
            amount=2,
            effect_key="advantage.deep_read",
            beat_id="b1",
            timestamp=NOW,
        )
        await record_resource_spend(db, session.session_id, spend)

        events = await _events_of_type(db, "resource_spend")
        assert len(events) == 1
        assert events[0].payload == build_resource_spend_payload(spend)

    @pytest.mark.asyncio
    async def test_record_resource_target_writes_event(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session = await _make_session(svc, db)
        activation = EffectActivation(
            effect_key="sabotage.rattle_the_witness",
            activator_id=PLAYER_A,
            target_id=PLAYER_B,
            interaction_window_id="w1",
        )
        await record_resource_target(db, session.session_id, activation, beat_id="b1")

        events = await _events_of_type(db, "resource_target")
        assert len(events) == 1
        assert events[0].payload["target_id"] == PLAYER_B

    @pytest.mark.asyncio
    async def test_record_resource_outcome_writes_event(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session = await _make_session(svc, db)
        activation = EffectActivation(
            effect_key="sabotage.rattle_the_witness",
            activator_id=PLAYER_A,
            target_id=PLAYER_B,
            interaction_window_id="w1",
            resolved_at=NOW,
            source_reveal_at=NOW,
        )
        await record_resource_outcome(db, session.session_id, activation, beat_id="b1")

        events = await _events_of_type(db, "resource_outcome")
        assert len(events) == 1
        assert events[0].payload["source_revealed"] is True

    @pytest.mark.asyncio
    async def test_record_resource_counterplay_writes_event(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session = await _make_session(svc, db)
        await record_resource_counterplay(
            db,
            session.session_id,
            countering_activator_id=PLAYER_B,
            countered_activator_id=PLAYER_A,
            countered_window_id="w1",
            beat_id="b1",
        )

        events = await _events_of_type(db, "resource_counterplay")
        assert len(events) == 1
        assert events[0].payload["countering_activator_id"] == PLAYER_B

    @pytest.mark.asyncio
    async def test_record_resource_recovery_writes_event(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session = await _make_session(svc, db)
        await record_resource_recovery(
            db, session.session_id, recovered_player_id=PLAYER_B, beat_id="b2"
        )

        events = await _events_of_type(db, "resource_recovery")
        assert len(events) == 1
        assert events[0].payload == {
            "recovered_player_id": PLAYER_B,
            "beat_id": "b2",
        }
