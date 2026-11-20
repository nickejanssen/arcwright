"""No new seat after the start (AW-331, spec 0095 M2).

``lobby_join`` works before the start. Once the game has started (running or
paused) it is refused with the stable code ``game_started``; a finished game is
refused with ``game_over``. A refused join adds no seat. Made-up arc and case
only; no model is called.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.arc.models import ArcDefinition
from engine.db.orm import Session as OrmSession
from engine.db.testing import make_sqlite_session_factory
from engine.session.service import (
    SeatClosedError,
    SessionService,
    SessionStateError,
)
from engine.tests.rounds_support import at, closing_arc


@pytest_asyncio.fixture()
async def factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine, session_factory = await make_sqlite_session_factory()
    try:
        yield session_factory
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def db(
    factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


async def lobby(
    db: AsyncSession, registered: Callable[[ArcDefinition], None]
) -> tuple[SessionService, UUID, str]:
    arc = closing_arc()
    registered(arc)
    svc = SessionService()
    created, _ = await svc.create_session(
        db, arc_id=arc.arc_id, host_account_id=uuid4()
    )
    assert created.join_code is not None
    return svc, created.session_id, created.join_code


async def seat_count(db: AsyncSession, svc: SessionService, session_id: UUID) -> int:
    seats = await svc.list_participants(db, session_id)
    return sum(1 for p in seats if p.surface_type == "player")


class TestBeforeTheStart:
    @pytest.mark.asyncio
    async def test_a_join_before_the_start_works_as_before(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        svc, session_id, code = await lobby(db, registered)
        first = await svc.lobby_join(db, join_code=code, display_name="Ada")
        second = await svc.lobby_join(db, join_code=code, display_name="Bo")
        assert first.participant_id != second.participant_id
        assert await seat_count(db, svc, session_id) == 2


class TestAfterTheStart:
    @pytest.mark.asyncio
    async def test_a_join_while_running_is_refused_with_game_started(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        svc, session_id, code = await lobby(db, registered)
        await svc.lobby_join(db, join_code=code, display_name="Ada")
        await svc.lobby_join(db, join_code=code, display_name="Bo")
        await svc.start_session(db, session_id)
        before = await seat_count(db, svc, session_id)
        with pytest.raises(SeatClosedError) as refused:
            await svc.lobby_join(db, join_code=code, display_name="Late")
        assert refused.value.code == "game_started"
        assert await seat_count(db, svc, session_id) == before
        orm = await db.get(OrmSession, session_id)
        assert orm is not None and orm.player_count == before

    @pytest.mark.asyncio
    async def test_a_join_while_paused_is_refused_with_game_started(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        svc, session_id, code = await lobby(db, registered)
        await svc.lobby_join(db, join_code=code, display_name="Ada")
        await svc.start_session(db, session_id)
        await svc.pause_session(db, session_id, now=at(1))
        with pytest.raises(SeatClosedError) as refused:
            await svc.lobby_join(db, join_code=code, display_name="Late")
        assert refused.value.code == "game_started"

    @pytest.mark.asyncio
    async def test_a_finished_game_is_refused_with_game_over(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        svc, session_id, code = await lobby(db, registered)
        await svc.lobby_join(db, join_code=code, display_name="Ada")
        await svc.start_session(db, session_id)
        await svc.end_session(db, session_id)
        with pytest.raises(SeatClosedError) as refused:
            await svc.lobby_join(db, join_code=code, display_name="Late")
        assert refused.value.code == "game_over"

    @pytest.mark.asyncio
    async def test_the_refusal_is_still_a_session_state_error(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        svc, session_id, code = await lobby(db, registered)
        await svc.lobby_join(db, join_code=code, display_name="Ada")
        await svc.start_session(db, session_id)
        with pytest.raises(SessionStateError):
            await svc.lobby_join(db, join_code=code, display_name="Late")


class TestAJoinRacingTheStart:
    @pytest.mark.asyncio
    async def test_a_join_and_a_start_at_once_never_leave_a_seat_after_the_start(
        self,
        factory: async_sessionmaker[AsyncSession],
        registered: Callable[[ArcDefinition], None],
    ) -> None:
        arc = closing_arc()
        registered(arc)
        svc = SessionService()
        async with factory() as setup:
            created, _ = await svc.create_session(
                setup, arc_id=arc.arc_id, host_account_id=uuid4()
            )
            await svc.lobby_join(
                setup, join_code=str(created.join_code), display_name="Ada"
            )
            await setup.commit()
        session_id = created.session_id
        code = str(created.join_code)

        async def join() -> str:
            async with factory() as db:
                try:
                    await svc.lobby_join(db, join_code=code, display_name="Late")
                    await db.commit()
                    return "joined"
                except SeatClosedError as refused:
                    await db.rollback()
                    return refused.code

        async def start() -> str:
            async with factory() as db:
                await svc.start_session(db, session_id)
                await db.commit()
                return "started"

        outcomes = await asyncio.gather(join(), start())
        async with factory() as check:
            orm = await check.get(OrmSession, session_id)
            assert orm is not None
            assert orm.status == "active"
            seats = await svc.list_participants(check, session_id)
            players = [p for p in seats if p.surface_type == "player"]
        # Either the join landed before the start, or it was refused after it.
        # What may never happen is a refusal that still left a seat behind.
        if outcomes[0] == "joined":
            assert len(players) == 2
        else:
            assert outcomes[0] == "game_started"
            assert len(players) == 1
        assert orm.player_count == len(players)
