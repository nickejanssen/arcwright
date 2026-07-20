from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from engine.case.models import ResolvedCase
from engine.claims.models import ContradictionOutcome
from engine.db.orm import (
    Accusation,
    Base,
    Character,
    Claim,
    ContradictionFlag,
    Session,
    SessionParticipant,
    SuspectLock,
)
from engine.db.testing import patch_metadata_for_sqlite
from engine.scoring.errors import AccusationLockedOutError, AlreadyCorrectError
from engine.scoring.models import AccusationOutcome
from engine.scoring.resolver import AccusationResolver

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


def _case() -> ResolvedCase:
    return ResolvedCase(
        case_id="case-1",
        arc_id="arc-1",
        seed=1,
        skeleton_id="skeleton-1",
        cast=[],
        culprit_id="culprit-1",
        evidence=[],
        falsehoods=[],
        facts=[],
        reveal_shape={},
    )


async def _fixture(session: AsyncSession) -> tuple[UUID, UUID, UUID]:
    session_id = uuid4()
    participant_id = uuid4()
    character_id = uuid4()
    session.add(
        Session(
            session_id=session_id,
            arc_id="arc-1",
            status="active",
            host_account_id=uuid4(),
            current_beat_id="grill",
            quality_tier="standard",
            player_count=2,
        )
    )
    session.add(Character(character_id=character_id, behavior_profile={}))
    session.add(
        SessionParticipant(
            participant_id=participant_id,
            session_id=session_id,
            character_id=character_id,
            account_id=None,
            join_token="join-token",
            surface_type="phone",
            is_ai_controlled=False,
        )
    )
    await session.flush()
    return session_id, participant_id, character_id


def _clock() -> datetime:
    return datetime(2026, 7, 19, 12, 0, tzinfo=timezone.utc)


def _resolver(
    session_id: UUID,
    *,
    context: dict[str, object] | None = None,
) -> AccusationResolver:
    return AccusationResolver(
        session_id=session_id,
        resolved_case=_case(),
        session_context=context,
        clock=_clock,
        round_duration_seconds=60,
        last_call_duration_seconds=100,
    )


async def _submit(
    resolver: AccusationResolver,
    db: AsyncSession,
    session_id: UUID,
    participant_id: UUID,
    *,
    beat_id: str = "grill",
    accused: str = "wrong-1",
    progress: float = 0.0,
):
    return await resolver.submit_accusation(
        db,
        session_id=session_id,
        accuser_participant_id=participant_id,
        beat_id=beat_id,
        beat_progress_fraction=progress,
        accused_cast_member_id=accused,
        motive_correct=False,
        method_correct=False,
    )


async def test_wrong_accusation_persists_penalty_and_lockout(
    db_session: AsyncSession,
):
    session_id, participant_id, _ = await _fixture(db_session)
    result = await _submit(
        _resolver(session_id), db_session, session_id, participant_id
    )

    assert result.outcome is AccusationOutcome.wrong
    assert result.points_awarded == -20
    row = await db_session.get(Accusation, UUID(result.accusation_id or ""))
    assert row is not None
    assert row.repeat_offense_count == 0
    assert row.lockout_until.replace(tzinfo=timezone.utc) == _clock() + timedelta(
        seconds=60
    )


async def test_correct_accusation_uses_confirmed_catches_for_momentum(
    db_session: AsyncSession,
):
    session_id, participant_id, character_id = await _fixture(db_session)
    claim = Claim(
        session_id=session_id,
        speaker_character_id=character_id,
        asker_participant_id=participant_id,
        round_index=1,
        beat_id="grill",
        interaction_window_id="window-1",
        claim_text="A claim",
    )
    db_session.add(claim)
    await db_session.flush()
    db_session.add(
        ContradictionFlag(
            claim_id=claim.claim_id,
            session_id=session_id,
            flagged_by_participant_id=participant_id,
            outcome=ContradictionOutcome.confirmed.value,
            created_at=_clock() - timedelta(seconds=1),
        )
    )
    await db_session.flush()

    result = await _submit(
        _resolver(session_id),
        db_session,
        session_id,
        participant_id,
        accused="culprit-1",
        progress=0.5,
    )

    assert result.outcome is AccusationOutcome.correct
    assert result.catches_banked_at_submission == 1
    assert result.points_awarded == 143


async def test_active_lockout_is_rejected(db_session: AsyncSession):
    session_id, participant_id, _ = await _fixture(db_session)
    resolver = _resolver(session_id)
    await _submit(resolver, db_session, session_id, participant_id)

    with pytest.raises(AccusationLockedOutError):
        await _submit(resolver, db_session, session_id, participant_id)


async def test_second_correct_accusation_is_rejected(db_session: AsyncSession):
    session_id, participant_id, _ = await _fixture(db_session)
    resolver = _resolver(session_id)
    await _submit(
        resolver,
        db_session,
        session_id,
        participant_id,
        accused="culprit-1",
    )

    with pytest.raises(AlreadyCorrectError):
        await _submit(
            resolver,
            db_session,
            session_id,
            participant_id,
            accused="culprit-1",
        )


async def test_first_correct_accusation_wins_server_order(db_session: AsyncSession):
    session_id, first_id, _ = await _fixture(db_session)
    second_id = uuid4()
    db_session.add(
        SessionParticipant(
            participant_id=second_id,
            session_id=session_id,
            character_id=uuid4(),
            join_token="join-token-2",
            surface_type="phone",
            is_ai_controlled=False,
        )
    )
    await db_session.flush()
    resolver = _resolver(session_id)

    first = await _submit(
        resolver,
        db_session,
        session_id,
        first_id,
        accused="culprit-1",
    )
    second = await _submit(
        resolver,
        db_session,
        session_id,
        second_id,
        accused="culprit-1",
    )

    assert first.triggered_last_call is True
    assert second.triggered_last_call is False
    assert (
        await db_session.scalar(
            select(func.count())
            .select_from(Accusation)
            .where(Accusation.triggered_last_call.is_(True))
        )
        == 1
    )


async def test_chain_reaction_compresses_remaining_countdown(db_session: AsyncSession):
    session_id, first_id, _ = await _fixture(db_session)
    second_id = uuid4()
    db_session.add(
        SessionParticipant(
            participant_id=second_id,
            session_id=session_id,
            character_id=uuid4(),
            join_token="join-token-2",
            surface_type="phone",
            is_ai_controlled=False,
        )
    )
    await db_session.flush()
    context: dict[str, object] = {"last_call_remaining_seconds": 100.0}
    resolver = _resolver(session_id, context=context)
    await _submit(resolver, db_session, session_id, first_id, accused="culprit-1")
    await _submit(resolver, db_session, session_id, second_id, accused="culprit-1")

    assert context["last_call_remaining_seconds"] == 80.0


async def test_last_word_allows_one_follow_up_then_blocks(
    db_session: AsyncSession,
):
    session_id, participant_id, _ = await _fixture(db_session)
    resolver = _resolver(session_id, context={"last_call_remaining_seconds": 100.0})
    first = await _submit(
        resolver,
        db_session,
        session_id,
        participant_id,
        beat_id="last_call",
    )
    assert first.used_last_word is True

    second = await _submit(
        resolver,
        db_session,
        session_id,
        participant_id,
        beat_id="last_call",
    )
    assert second.repeat_offense_count == 1

    with pytest.raises(AccusationLockedOutError):
        await _submit(
            resolver,
            db_session,
            session_id,
            participant_id,
            beat_id="last_call",
        )


async def test_suspect_lock_upserts_without_accusation_row(
    db_session: AsyncSession,
):
    session_id, participant_id, _ = await _fixture(db_session)
    resolver = _resolver(session_id)
    await resolver.set_suspect_lock(
        db_session,
        session_id=session_id,
        participant_id=participant_id,
        suspect_cast_member_id="suspect-1",
    )
    await resolver.set_suspect_lock(
        db_session,
        session_id=session_id,
        participant_id=participant_id,
        suspect_cast_member_id="suspect-2",
    )

    assert await db_session.scalar(select(func.count()).select_from(Accusation)) == 0
    assert await db_session.scalar(select(func.count()).select_from(SuspectLock)) == 1
    row = await db_session.scalar(select(SuspectLock))
    assert row is not None
    assert row.suspect_cast_member_id == "suspect-2"
