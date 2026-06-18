"""Tests for the DB-backed SessionService (AW-217 + AW-220).

AW-217 AC5: session lifecycle state machine and join-token validation.
AW-220: snapshot-on-pause and resume-from-snapshot behaviour live in
``test_session_resume.py``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from engine.db.orm import Base
from engine.db.testing import patch_metadata_for_sqlite
from engine.session.models import QualityTier, SessionStatus
from engine.session.service import (
    SessionCapacityError,
    SessionNotFoundError,
    SessionService,
    SessionStateError,
)

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


class TestCreateSession:
    @pytest.mark.asyncio
    async def test_returns_session_and_join_token(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, token = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        assert session.arc_id == "nightcap-v1"
        assert session.status is SessionStatus.created
        assert session.current_beat_id == "arrival"
        assert session.player_count == 0
        assert isinstance(token, str) and len(token) > 0

    @pytest.mark.asyncio
    async def test_respects_quality_tier(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db,
            arc_id="nightcap-v1",
            host_account_id=uuid4(),
            quality_tier=QualityTier.premium,
        )
        assert session.quality_tier is QualityTier.premium

    @pytest.mark.asyncio
    async def test_each_call_returns_distinct_session_id(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        s1, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        s2, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        assert s1.session_id != s2.session_id


class TestGetSession:
    @pytest.mark.asyncio
    async def test_returns_none_for_unknown_session(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        assert await svc.get_session(db, uuid4()) is None

    @pytest.mark.asyncio
    async def test_returns_session_after_create(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        result = await svc.get_session(db, session.session_id)
        assert result is not None
        assert result.session_id == session.session_id


class TestStartSession:
    @pytest.mark.asyncio
    async def test_transitions_to_active(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        started = await svc.start_session(db, session.session_id)
        assert started.status is SessionStatus.active
        assert started.started_at is not None

    @pytest.mark.asyncio
    async def test_fails_if_already_active(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        await svc.start_session(db, session.session_id)
        with pytest.raises(SessionStateError):
            await svc.start_session(db, session.session_id)

    @pytest.mark.asyncio
    async def test_fails_for_unknown_session(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        with pytest.raises(SessionNotFoundError):
            await svc.start_session(db, uuid4())


class TestPauseResumeSession:
    @pytest.mark.asyncio
    async def test_pause_transitions_active_to_paused(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        await svc.start_session(db, session.session_id)
        paused = await svc.pause_session(db, session.session_id)
        assert paused.status is SessionStatus.paused

    @pytest.mark.asyncio
    async def test_resume_transitions_paused_to_active(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        await svc.start_session(db, session.session_id)
        await svc.pause_session(db, session.session_id)
        resumed, _ = await svc.resume_session(db, session.session_id)
        assert resumed.status is SessionStatus.active

    @pytest.mark.asyncio
    async def test_pause_fails_if_not_active(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        with pytest.raises(SessionStateError):
            await svc.pause_session(db, session.session_id)

    @pytest.mark.asyncio
    async def test_resume_fails_if_not_paused(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        await svc.start_session(db, session.session_id)
        with pytest.raises(SessionStateError):
            await svc.resume_session(db, session.session_id)


class TestEndSession:
    @pytest.mark.asyncio
    async def test_transitions_to_completed_from_active(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        await svc.start_session(db, session.session_id)
        ended = await svc.end_session(db, session.session_id)
        assert ended.status is SessionStatus.completed
        assert ended.completed_at is not None

    @pytest.mark.asyncio
    async def test_end_session_can_end_created_session(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        ended = await svc.end_session(db, session.session_id)
        assert ended.status is SessionStatus.completed

    @pytest.mark.asyncio
    async def test_end_fails_if_already_completed(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        await svc.end_session(db, session.session_id)
        with pytest.raises(SessionStateError):
            await svc.end_session(db, session.session_id)

    @pytest.mark.asyncio
    async def test_end_fails_for_unknown_session(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        with pytest.raises(SessionNotFoundError):
            await svc.end_session(db, uuid4())


class TestValidateJoinToken:
    @pytest.mark.asyncio
    async def test_returns_participant_for_valid_token(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, host_token = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        participant = await svc.validate_join_token(db, session.session_id, host_token)
        assert participant is not None
        assert participant.session_id == session.session_id
        assert participant.surface_type == "host"

    @pytest.mark.asyncio
    async def test_returns_none_for_unknown_token(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        assert (
            await svc.validate_join_token(db, session.session_id, "not-a-token") is None
        )

    @pytest.mark.asyncio
    async def test_returns_none_when_token_belongs_to_different_session(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        s1, t1 = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        s2, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        assert await svc.validate_join_token(db, s2.session_id, t1) is None


class TestAddPlayer:
    @pytest.mark.asyncio
    async def test_returns_participant_and_join_token(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        participant, token = await svc.add_player(db, session.session_id)
        assert participant.session_id == session.session_id
        assert participant.surface_type == "player"
        assert isinstance(token, str) and len(token) > 0

    @pytest.mark.asyncio
    async def test_increments_player_count(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        await svc.add_player(db, session.session_id)
        await svc.add_player(db, session.session_id)
        reloaded = await svc.get_session(db, session.session_id)
        assert reloaded is not None
        assert reloaded.player_count == 2

    @pytest.mark.asyncio
    async def test_join_token_is_valid_for_join_endpoint(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        participant, token = await svc.add_player(db, session.session_id)
        found = await svc.validate_join_token(db, session.session_id, token)
        assert found is not None
        assert found.participant_id == participant.participant_id

    @pytest.mark.asyncio
    async def test_fails_when_at_capacity(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        await svc.add_player(db, session.session_id, max_players=2)
        await svc.add_player(db, session.session_id, max_players=2)
        with pytest.raises(SessionCapacityError):
            await svc.add_player(db, session.session_id, max_players=2)

    @pytest.mark.asyncio
    async def test_fails_for_completed_session(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        await svc.end_session(db, session.session_id)
        with pytest.raises(SessionStateError):
            await svc.add_player(db, session.session_id)

    @pytest.mark.asyncio
    async def test_fails_for_unknown_session(
        self, svc: SessionService, db: AsyncSession
    ) -> None:
        with pytest.raises(SessionNotFoundError):
            await svc.add_player(db, uuid4())
