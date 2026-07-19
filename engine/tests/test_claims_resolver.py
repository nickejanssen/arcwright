from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from engine.case.models import AuthorizedFalsehood, EvidenceEntry
from engine.claims.errors import AlreadyResolvedError, ClaimNotFoundError
from engine.claims.models import ClaimRecord, ContradictionOutcome
from engine.claims.resolver import ClaimResolver
from engine.db.orm import (
    Base,
    Character,
    Claim,
    ContradictionFlag,
    Session,
    SessionParticipant,
)
from engine.db.testing import patch_metadata_for_sqlite

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


async def _make_fixture(
    session: AsyncSession,
) -> tuple[UUID, UUID, UUID, UUID]:
    session_id = uuid4()
    speaker_id = uuid4()
    flagger_character_id = uuid4()
    flagger_participant_id = uuid4()
    session.add(
        Session(
            session_id=session_id,
            arc_id="arc-1",
            status="active",
            host_account_id=uuid4(),
            current_beat_id="beat-1",
            quality_tier="standard",
            player_count=2,
        )
    )
    session.add_all(
        [
            Character(character_id=speaker_id, behavior_profile={}),
            Character(character_id=flagger_character_id, behavior_profile={}),
            SessionParticipant(
                participant_id=flagger_participant_id,
                session_id=session_id,
                character_id=flagger_character_id,
                account_id=None,
                join_token="join-token",
                surface_type="phone",
                is_ai_controlled=False,
            ),
        ]
    )
    await session.flush()
    return session_id, speaker_id, flagger_character_id, flagger_participant_id


def _claim(
    *,
    speaker_id: UUID,
    asker_id: UUID | None = None,
    is_authorized_lie: bool = False,
    falsehood_id: str | None = None,
) -> ClaimRecord:
    return ClaimRecord(
        speaker_id=str(speaker_id),
        asker_id=str(asker_id) if asker_id else None,
        round_index=1,
        beat_id="beat-1",
        interaction_window_id="window-1",
        claim_text="I was in the garden.",
        is_authorized_lie=is_authorized_lie,
        falsehood_id=falsehood_id,
    )


def _falsehood(*, speaker_id: UUID) -> AuthorizedFalsehood:
    return AuthorizedFalsehood(
        falsehood_id="lie-1",
        speaker_id="s1",
        topic="location",
        claim_text="I was in the garden.",
        contradicted_by=["evidence-1", "evidence-2"],
    )


def _evidence(evidence_id: str) -> EvidenceEntry:
    return EvidenceEntry(
        evidence_id=evidence_id,
        evidence_type="trace",
        text="A trace links the object to the location.",
        points_toward=["member-1"],
        points_away_from=[],
        delivery="private",
    )


async def test_record_claim_persists_claim_and_populates_db_fields(
    db_session: AsyncSession,
) -> None:
    session_id, speaker_id, _, asker_id = await _make_fixture(db_session)
    resolver = ClaimResolver(session_id=session_id)

    result = await resolver.record_claim(
        db_session,
        claim=_claim(speaker_id=speaker_id, asker_id=asker_id),
    )

    assert result.claim_id is not None
    assert result.created_at is not None
    stored = await db_session.get(Claim, UUID(result.claim_id))
    assert stored is not None
    assert stored.session_id == session_id
    assert stored.speaker_character_id == speaker_id
    assert stored.asker_participant_id == asker_id


async def test_resolve_flag_rejects_non_lie_claim(
    db_session: AsyncSession,
) -> None:
    session_id, speaker_id, _, flagger_id = await _make_fixture(db_session)
    resolver = ClaimResolver(session_id=session_id)
    claim = await resolver.record_claim(db_session, claim=_claim(speaker_id=speaker_id))

    result = await resolver.resolve_flag(
        db_session,
        claim_id=claim.claim_id or "",
        flagging_participant_id=str(flagger_id),
    )

    assert result.outcome is ContradictionOutcome.rejected
    assert result.evidence_id_used is None


async def test_resolve_flag_rejects_lie_without_possession(
    db_session: AsyncSession,
) -> None:
    session_id, speaker_id, _, flagger_id = await _make_fixture(db_session)
    resolver = ClaimResolver(
        session_id=session_id,
        authorized_falsehoods=[_falsehood(speaker_id=speaker_id)],
    )
    claim = await resolver.record_claim(
        db_session,
        claim=_claim(
            speaker_id=speaker_id,
            is_authorized_lie=True,
            falsehood_id="lie-1",
        ),
    )

    result = await resolver.resolve_flag(
        db_session,
        claim_id=claim.claim_id or "",
        flagging_participant_id=str(flagger_id),
    )

    assert result.outcome is ContradictionOutcome.rejected
    assert result.evidence_id_used is None


async def test_resolve_flag_confirms_lie_with_delivered_evidence(
    db_session: AsyncSession,
) -> None:
    session_id, speaker_id, _, flagger_id = await _make_fixture(db_session)
    from engine.claims.evidence import record_evidence_delivery

    await record_evidence_delivery(
        db_session,
        session_id=session_id,
        evidence=_evidence("evidence-2"),
        participant_id=flagger_id,
    )
    resolver = ClaimResolver(
        session_id=session_id,
        authorized_falsehoods=[_falsehood(speaker_id=speaker_id)],
    )
    claim = await resolver.record_claim(
        db_session,
        claim=_claim(
            speaker_id=speaker_id,
            is_authorized_lie=True,
            falsehood_id="lie-1",
        ),
    )

    result = await resolver.resolve_flag(
        db_session,
        claim_id=claim.claim_id or "",
        flagging_participant_id=str(flagger_id),
    )

    assert result.outcome is ContradictionOutcome.confirmed
    assert result.evidence_id_used == "evidence-2"


async def test_second_confirmed_flag_raises_and_does_not_replace_first(
    db_session: AsyncSession,
) -> None:
    session_id, speaker_id, _, flagger_id = await _make_fixture(db_session)
    from engine.claims.evidence import record_evidence_delivery

    await record_evidence_delivery(
        db_session,
        session_id=session_id,
        evidence=_evidence("evidence-1"),
        participant_id=flagger_id,
    )
    resolver = ClaimResolver(
        session_id=session_id,
        authorized_falsehoods=[_falsehood(speaker_id=speaker_id)],
    )
    claim = await resolver.record_claim(
        db_session,
        claim=_claim(
            speaker_id=speaker_id,
            is_authorized_lie=True,
            falsehood_id="lie-1",
        ),
    )

    await resolver.resolve_flag(
        db_session,
        claim_id=claim.claim_id or "",
        flagging_participant_id=str(flagger_id),
    )
    with pytest.raises(AlreadyResolvedError):
        await resolver.resolve_flag(
            db_session,
            claim_id=claim.claim_id or "",
            flagging_participant_id=str(flagger_id),
        )

    count = await db_session.scalar(select(func.count()).select_from(ContradictionFlag))
    assert count == 1


async def test_resolve_flag_raises_for_missing_claim(db_session: AsyncSession) -> None:
    session_id, _, _, flagger_id = await _make_fixture(db_session)
    resolver = ClaimResolver(session_id=session_id)

    with pytest.raises(ClaimNotFoundError):
        await resolver.resolve_flag(
            db_session,
            claim_id=str(uuid4()),
            flagging_participant_id=str(flagger_id),
        )
