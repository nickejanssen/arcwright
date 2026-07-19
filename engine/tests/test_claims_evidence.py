"""Evidence delivery bridges case evidence to participant knowledge state."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from engine.case.models import EvidenceEntry
from engine.db.orm import Base, Character, Fact, Session, SessionParticipant
from engine.db.testing import patch_metadata_for_sqlite

patch_metadata_for_sqlite()


@pytest.fixture
async def db_session() -> AsyncSession:  # type: ignore[override]
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:  # type: ignore[attr-defined]
        yield session  # type: ignore[misc]

    await engine.dispose()


async def _make_participant(
    session: AsyncSession,
    *,
    session_id: UUID,
    participant_id: UUID,
    character_id: UUID,
) -> SessionParticipant:
    session.add(Character(character_id=character_id, behavior_profile={}))
    session.add(
        Session(
            session_id=session_id,
            arc_id="arc-1",
            status="active",
            host_account_id=uuid4(),
            current_beat_id="beat-1",
            quality_tier="standard",
            player_count=1,
        )
    )
    await session.flush()
    participant = SessionParticipant(
        participant_id=participant_id,
        session_id=session_id,
        character_id=character_id,
        account_id=None,
        join_token="join-token",
        surface_type="phone",
        is_ai_controlled=False,
    )
    session.add(participant)
    await session.flush()
    return participant


def _evidence(*, evidence_id: str = "evidence-1") -> EvidenceEntry:
    return EvidenceEntry(
        evidence_id=evidence_id,
        evidence_type="trace",
        text="A trace links the object to the location.",
        points_toward=["member-1"],
        points_away_from=[],
        delivery="private",
    )


async def test_record_evidence_delivery_asserts_evidence_fact_for_participant(
    db_session: AsyncSession,
) -> None:
    session_id = uuid4()
    participant_id = uuid4()
    character_id = uuid4()
    await _make_participant(
        db_session,
        session_id=session_id,
        participant_id=participant_id,
        character_id=character_id,
    )

    from engine.claims.evidence import record_evidence_delivery

    knowledge_state = await record_evidence_delivery(
        db_session,
        session_id=session_id,
        evidence=_evidence(),
        participant_id=participant_id,
    )

    assert knowledge_state.session_id == session_id
    assert knowledge_state.character_id == character_id
    fact = await db_session.get(Fact, knowledge_state.fact_id)
    assert fact is not None
    assert fact.fact_type == "evidence_delivered"
    assert fact.fact_content == {
        "evidence_id": "evidence-1",
        "evidence_type": "trace",
    }


async def test_participant_has_evidence_checks_active_evidence_facts(
    db_session: AsyncSession,
) -> None:
    session_id = uuid4()
    participant_id = uuid4()
    character_id = uuid4()
    await _make_participant(
        db_session,
        session_id=session_id,
        participant_id=participant_id,
        character_id=character_id,
    )

    from engine.claims.evidence import (
        participant_has_evidence,
        record_evidence_delivery,
    )

    await record_evidence_delivery(
        db_session,
        session_id=session_id,
        evidence=_evidence(),
        participant_id=participant_id,
    )

    assert await participant_has_evidence(
        db_session,
        session_id=session_id,
        participant_id=participant_id,
        evidence_ids=["evidence-1"],
    )
    assert not await participant_has_evidence(
        db_session,
        session_id=session_id,
        participant_id=participant_id,
        evidence_ids=["missing-evidence"],
    )


async def test_participant_has_evidence_returns_false_for_empty_requested_ids(
    db_session: AsyncSession,
) -> None:
    session_id = uuid4()
    participant_id = uuid4()
    character_id = uuid4()
    await _make_participant(
        db_session,
        session_id=session_id,
        participant_id=participant_id,
        character_id=character_id,
    )

    from engine.claims.evidence import participant_has_evidence

    assert not await participant_has_evidence(
        db_session,
        session_id=session_id,
        participant_id=participant_id,
        evidence_ids=[],
    )
