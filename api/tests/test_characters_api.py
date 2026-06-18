"""Integration tests for the character endpoints (AW-218 AC1, AC3).

DB-backed (AW-220): session + participant rows live in SQLite for tests
via the ORM. Firebase is mocked.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.testclient import TestClient

from api.auth import (
    ApiCaller,
    JwtClaims,
    require_api_key,
    require_api_key_or_host_jwt,
    require_host_jwt,
    require_player_or_host_jwt,
)
from api.main import app
from engine.db import get_async_session
from engine.db.orm import Base
from engine.db.testing import patch_metadata_for_sqlite
from engine.session.service import SessionService

_FAKE_TOKEN = b"fake-firebase-custom-token"

patch_metadata_for_sqlite()


@pytest_asyncio.fixture()
async def db_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def host_session(
    db_factory: async_sessionmaker[AsyncSession],
) -> tuple[UUID, UUID, UUID, UUID]:
    """Build session + two players directly via the service.

    Returns ``(session_id, player_a_participant_id, player_a_character_id,
    player_b_character_id)``.
    """
    svc = SessionService()
    async with db_factory() as db:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        a, _ = await svc.add_player(db, session.session_id)
        b, _ = await svc.add_player(db, session.session_id)
        await db.commit()
    return (
        session.session_id,
        a.participant_id,
        a.character_id,
        b.character_id,
    )


def _client_for_role(
    role: str,
    session_id: UUID,
    player_id: UUID | None,
    db_factory: async_sessionmaker[AsyncSession],
) -> Iterator[TestClient]:
    async def _override_db() -> AsyncIterator[AsyncSession]:
        async with db_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    with (
        patch("api.routers.sessions._ensure_firebase_app"),
        patch("firebase_admin.auth.create_custom_token", return_value=_FAKE_TOKEN),
    ):
        claims = JwtClaims(
            uid=f"{role}-uid",
            session_id=session_id,
            player_id=player_id,
            role=role,
        )
        app.dependency_overrides[require_api_key] = lambda: ApiCaller(
            api_key="test-key"
        )
        app.dependency_overrides[require_host_jwt] = lambda: (
            claims
            if role == "host"
            else (_ for _ in ()).throw(  # pragma: no cover
                AssertionError("host dependency invoked under non-host override")
            )
        )
        app.dependency_overrides[require_player_or_host_jwt] = lambda: claims
        app.dependency_overrides[require_api_key_or_host_jwt] = lambda: ApiCaller(
            api_key="test-key"
        )
        app.dependency_overrides[get_async_session] = _override_db
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()


class TestListCharacters:
    def test_host_sees_all_player_characters(
        self,
        host_session: tuple[UUID, UUID, UUID, UUID],
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id, _, char_a, char_b = host_session
        for c in _client_for_role("host", session_id, uuid4(), db_factory):
            resp = c.get(f"/v1/sessions/{session_id}/characters")
        assert resp.status_code == 200
        body = resp.json()
        assert body["session_id"] == str(session_id)
        ids = {item["character_id"] for item in body["characters"]}
        assert ids == {str(char_a), str(char_b)}

    def test_unknown_session_returns_404(
        self,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        unknown = uuid4()
        for c in _client_for_role("host", unknown, uuid4(), db_factory):
            resp = c.get(f"/v1/sessions/{unknown}/characters")
        assert resp.status_code == 404


class TestGetCharacterDetail:
    def test_owner_gets_own_character(
        self,
        host_session: tuple[UUID, UUID, UUID, UUID],
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id, player_a, char_a, _ = host_session
        for c in _client_for_role("player", session_id, player_a, db_factory):
            resp = c.get(f"/v1/sessions/{session_id}/characters/{char_a}")
        assert resp.status_code == 200
        assert resp.json()["character_id"] == str(char_a)

    def test_player_cannot_read_another_characters_detail(
        self,
        host_session: tuple[UUID, UUID, UUID, UUID],
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id, player_a, _, char_b = host_session
        for c in _client_for_role("player", session_id, player_a, db_factory):
            resp = c.get(f"/v1/sessions/{session_id}/characters/{char_b}")
        assert resp.status_code == 403


class TestSubmitInput:
    def test_player_submits_dialogue_as_own_character(
        self,
        host_session: tuple[UUID, UUID, UUID, UUID],
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id, player_a, char_a, _ = host_session
        for c in _client_for_role("player", session_id, player_a, db_factory):
            resp = c.post(
                f"/v1/sessions/{session_id}/characters/{char_a}/input",
                json={"kind": "dialogue", "content": "Where were you?"},
            )
        assert resp.status_code == 201
        body = resp.json()
        assert body["kind"] == "dialogue"
        assert body["character_id"] == str(char_a)

    def test_player_cannot_submit_as_another_character(
        self,
        host_session: tuple[UUID, UUID, UUID, UUID],
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id, player_a, _, char_b = host_session
        for c in _client_for_role("player", session_id, player_a, db_factory):
            resp = c.post(
                f"/v1/sessions/{session_id}/characters/{char_b}/input",
                json={"kind": "action", "content": "impersonation"},
            )
        assert resp.status_code == 403

    def test_empty_content_is_rejected(
        self,
        host_session: tuple[UUID, UUID, UUID, UUID],
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id, player_a, char_a, _ = host_session
        for c in _client_for_role("player", session_id, player_a, db_factory):
            resp = c.post(
                f"/v1/sessions/{session_id}/characters/{char_a}/input",
                json={"kind": "dialogue", "content": ""},
            )
        assert resp.status_code == 422

    def test_unknown_kind_is_rejected(
        self,
        host_session: tuple[UUID, UUID, UUID, UUID],
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id, player_a, char_a, _ = host_session
        for c in _client_for_role("player", session_id, player_a, db_factory):
            resp = c.post(
                f"/v1/sessions/{session_id}/characters/{char_a}/input",
                json={"kind": "narration", "content": "foo"},
            )
        assert resp.status_code == 422

    def test_host_token_cannot_submit_input(
        self,
        host_session: tuple[UUID, UUID, UUID, UUID],
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id, _, char_a, _ = host_session
        for c in _client_for_role("host", session_id, uuid4(), db_factory):
            resp = c.post(
                f"/v1/sessions/{session_id}/characters/{char_a}/input",
                json={"kind": "dialogue", "content": "host attempt"},
            )
        assert resp.status_code == 403

    def test_display_token_cannot_submit_input(
        self,
        host_session: tuple[UUID, UUID, UUID, UUID],
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id, _, char_a, _ = host_session
        for c in _client_for_role("display", session_id, uuid4(), db_factory):
            resp = c.post(
                f"/v1/sessions/{session_id}/characters/{char_a}/input",
                json={"kind": "dialogue", "content": "display attempt"},
            )
        assert resp.status_code == 403
