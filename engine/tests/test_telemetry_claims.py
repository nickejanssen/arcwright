from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import uuid4

import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from engine.claims.models import ClaimRecord, ContradictionOutcome, FlagResult
from engine.db.orm import Base, Event
from engine.db.testing import patch_metadata_for_sqlite
from engine.telemetry.claims import (
    build_answer_latency_payload,
    build_claim_recorded_payload,
    build_contradiction_outcome_payload,
    compute_answer_latency_p95,
    record_answer_latency,
    record_claim_recorded,
    record_contradiction_outcome,
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


def _claim() -> ClaimRecord:
    return ClaimRecord(
        claim_id="claim-1",
        speaker_id=str(uuid4()),
        round_index=2,
        beat_id="beat-1",
        interaction_window_id="window-1",
        claim_text="I was in the garden.",
        is_authorized_lie=True,
        falsehood_id="lie-1",
    )


def test_claim_telemetry_payload_excludes_lie_markers() -> None:
    payload = build_claim_recorded_payload(_claim())

    assert payload["claim_id"] == "claim-1"
    assert "is_authorized_lie" not in payload
    assert "falsehood_id" not in payload


def test_contradiction_payload_is_outcome_only() -> None:
    payload = build_contradiction_outcome_payload(
        FlagResult(
            claim_id="claim-1",
            outcome=ContradictionOutcome.confirmed,
            evidence_id_used="evidence-1",
        )
    )

    assert payload == {
        "claim_id": "claim-1",
        "outcome": "confirmed",
        "evidence_id_used": "evidence-1",
    }
    assert not {"score", "points", "score_value"} & set(payload)


def test_answer_latency_payload_is_numeric_and_aggregatable() -> None:
    assert build_answer_latency_payload(latency_ms=123.5, quality_tier="fast") == {
        "latency_ms": 123.5,
        "quality_tier": "fast",
    }


def test_answer_latency_p95_is_computable_from_recorded_values() -> None:
    values = [120.0, 80.0, 310.0, 150.0, 200.0, 90.0, 175.0, 225.0, 130.0, 160.0]

    assert compute_answer_latency_p95(values) == 310.0


async def test_claim_telemetry_recorders_write_generic_events(
    db_session: AsyncSession,
) -> None:
    session_id = uuid4()
    claim = _claim()
    result = FlagResult(
        claim_id="claim-1",
        outcome=ContradictionOutcome.rejected,
        evidence_id_used=None,
    )

    await record_claim_recorded(db_session, session_id, claim)
    await record_contradiction_outcome(db_session, session_id, result)
    await record_answer_latency(
        db_session,
        session_id,
        latency_ms=123.5,
        quality_tier="fast",
    )

    events = list(
        (await db_session.execute(select(Event).order_by(Event.event_type))).scalars()
    )
    assert [event.event_type for event in events] == [
        "answer_generation_latency",
        "claim_recorded",
        "contradiction_rejected",
    ]
    assert "falsehood_id" not in events[1].payload
    assert events[0].payload["latency_ms"] == 123.5
