from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import uuid4

import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from engine.db.orm import Base, Event
from engine.db.testing import patch_metadata_for_sqlite
from engine.scoring.models import AccusationAttempt, AccusationOutcome
from engine.telemetry.scoring import (
    build_accusation_submitted_payload,
    build_last_call_triggered_payload,
    record_accusation_submitted,
)

patch_metadata_for_sqlite()


@pytest_asyncio.fixture()
async def db_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


def _attempt(*, triggered_last_call: bool = False) -> AccusationAttempt:
    return AccusationAttempt(
        session_id=str(uuid4()),
        accuser_participant_id=str(uuid4()),
        beat_id="grill",
        accused_cast_member_id="cast-1",
        outcome=AccusationOutcome.wrong,
        catches_banked_at_submission=2,
        points_awarded=-20,
        motive_correct=False,
        method_correct=False,
        triggered_last_call=triggered_last_call,
    )


def test_accusation_telemetry_can_include_outcome_and_points():
    payload = build_accusation_submitted_payload(_attempt())

    assert payload["outcome"] == "wrong"
    assert payload["points_awarded"] == -20
    assert "suspect_lock" not in payload
    assert "suspect_cast_member_id" not in payload


def test_last_call_payload_contains_only_trigger_metadata():
    payload = build_last_call_triggered_payload(_attempt(triggered_last_call=True))

    assert set(payload) == {"accusation_id", "participant_id", "beat_id"}


async def test_record_accusation_submitted_writes_event(db_session: AsyncSession):
    session_id = uuid4()
    attempt = _attempt()

    await record_accusation_submitted(db_session, session_id, attempt)

    event = await db_session.scalar(
        select(Event).where(Event.event_type == "accusation_submitted")
    )
    assert event is not None
    assert event.session_id == session_id
    assert event.payload["accusation_id"] is None
