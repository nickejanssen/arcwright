"""Tests for the DB-backed CharacterService (AW-218 + AW-220).

AC1: Player input endpoint accepts typed character action or dialogue input.
AC3: Player clients cannot reach another character's surface.
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

from engine.characters.service import (
    CharacterAccessError,
    CharacterNotFoundError,
    CharacterService,
)
from engine.db.orm import Base
from engine.db.testing import patch_metadata_for_sqlite
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
def services() -> tuple[SessionService, CharacterService]:
    sessions = SessionService()
    return sessions, CharacterService(sessions=sessions)


class TestListCharacters:
    @pytest.mark.asyncio
    async def test_excludes_host_participant(
        self,
        services: tuple[SessionService, CharacterService],
        db: AsyncSession,
    ) -> None:
        sessions, characters = services
        session, _ = await sessions.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        await sessions.add_player(db, session.session_id)
        await sessions.add_player(db, session.session_id)

        result = await characters.list_characters(db, session.session_id)
        assert len(result) == 2
        assert all(c.surface_type == "player" for c in result)

    @pytest.mark.asyncio
    async def test_unknown_session_returns_empty_list(
        self,
        services: tuple[SessionService, CharacterService],
        db: AsyncSession,
    ) -> None:
        _, characters = services
        assert await characters.list_characters(db, uuid4()) == []


class TestGetCharacterForPlayer:
    @pytest.mark.asyncio
    async def test_owner_receives_detail(
        self,
        services: tuple[SessionService, CharacterService],
        db: AsyncSession,
    ) -> None:
        sessions, characters = services
        session, _ = await sessions.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        participant, _ = await sessions.add_player(db, session.session_id)

        detail = await characters.get_character_for_player(
            db,
            session.session_id,
            participant.character_id,
            participant.participant_id,
        )
        assert detail.character_id == participant.character_id
        assert detail.participant_id == participant.participant_id

    @pytest.mark.asyncio
    async def test_non_owner_is_rejected(
        self,
        services: tuple[SessionService, CharacterService],
        db: AsyncSession,
    ) -> None:
        sessions, characters = services
        session, _ = await sessions.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        owner, _ = await sessions.add_player(db, session.session_id)
        intruder, _ = await sessions.add_player(db, session.session_id)

        with pytest.raises(CharacterAccessError):
            await characters.get_character_for_player(
                db,
                session.session_id,
                owner.character_id,
                intruder.participant_id,
            )

    @pytest.mark.asyncio
    async def test_unknown_character_raises(
        self,
        services: tuple[SessionService, CharacterService],
        db: AsyncSession,
    ) -> None:
        sessions, characters = services
        session, _ = await sessions.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        with pytest.raises(CharacterNotFoundError):
            await characters.get_character_for_player(
                db, session.session_id, uuid4(), uuid4()
            )


class TestSubmitInput:
    @pytest.mark.asyncio
    async def test_owner_can_submit_action(
        self,
        services: tuple[SessionService, CharacterService],
        db: AsyncSession,
    ) -> None:
        sessions, characters = services
        session, _ = await sessions.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        participant, _ = await sessions.add_player(db, session.session_id)

        record = await characters.submit_input(
            db,
            session_id=session.session_id,
            character_id=participant.character_id,
            requesting_participant_id=participant.participant_id,
            kind="action",
            content="Looks under the table.",
        )
        assert record.kind == "action"
        assert record.content == "Looks under the table."
        assert characters.get_inputs(session.session_id) == [record]

    @pytest.mark.asyncio
    async def test_owner_can_submit_dialogue(
        self,
        services: tuple[SessionService, CharacterService],
        db: AsyncSession,
    ) -> None:
        sessions, characters = services
        session, _ = await sessions.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        participant, _ = await sessions.add_player(db, session.session_id)

        record = await characters.submit_input(
            db,
            session_id=session.session_id,
            character_id=participant.character_id,
            requesting_participant_id=participant.participant_id,
            kind="dialogue",
            content="Where were you at midnight?",
        )
        assert record.kind == "dialogue"

    @pytest.mark.asyncio
    async def test_non_owner_cannot_submit(
        self,
        services: tuple[SessionService, CharacterService],
        db: AsyncSession,
    ) -> None:
        sessions, characters = services
        session, _ = await sessions.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        owner, _ = await sessions.add_player(db, session.session_id)
        intruder, _ = await sessions.add_player(db, session.session_id)

        with pytest.raises(CharacterAccessError):
            await characters.submit_input(
                db,
                session_id=session.session_id,
                character_id=owner.character_id,
                requesting_participant_id=intruder.participant_id,
                kind="action",
                content="impersonation attempt",
            )

    @pytest.mark.asyncio
    async def test_unknown_character_raises(
        self,
        services: tuple[SessionService, CharacterService],
        db: AsyncSession,
    ) -> None:
        sessions, characters = services
        session, _ = await sessions.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        with pytest.raises(CharacterNotFoundError):
            await characters.submit_input(
                db,
                session_id=session.session_id,
                character_id=uuid4(),
                requesting_participant_id=uuid4(),
                kind="action",
                content="x",
            )
