"""Integration tests for the DB-backed knowledge endpoints
(AW-218 + AW-248 + AW-220).

Session rows live in the same DB as the knowledge rows (AW-220 retired
the in-memory→DB bridge), so the previous ``_ensure_session_row_for_knowledge``
helper and its dedicated test are gone.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
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
from engine.characters import build_character_generation_context
from engine.db import get_async_session
from engine.db.orm import Base, Character, KnowledgeState
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
async def open_session(
    db_factory: async_sessionmaker[AsyncSession],
) -> UUID:
    """Create a session row via the DB-backed service and return its id."""
    svc = SessionService()
    async with db_factory() as db:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        await db.commit()
    return session.session_id


@pytest_asyncio.fixture()
async def open_player_session(
    db_factory: async_sessionmaker[AsyncSession],
) -> tuple[UUID, UUID]:
    """Create a session + player participant. Returns (session_id, participant_id)."""
    svc = SessionService()
    async with db_factory() as db:
        session, _ = await svc.create_session(
            db, arc_id="nightcap-v1", host_account_id=uuid4()
        )
        participant, _ = await svc.add_player(db, session.session_id)
        await db.commit()
    return session.session_id, participant.participant_id


@pytest.fixture()
def internal_client(
    db_factory: async_sessionmaker[AsyncSession],
) -> Iterator[TestClient]:
    """TestClient with internal (API-key) auth overridden; Bearer deps NOT
    overridden so player tokens cannot reach internal routes."""

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
        app.dependency_overrides[require_api_key] = lambda: ApiCaller(
            api_key="test-key"
        )
        app.dependency_overrides[require_api_key_or_host_jwt] = lambda: ApiCaller(
            api_key="test-key"
        )
        app.dependency_overrides[get_async_session] = _override_db
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()


@pytest.fixture()
def player_client_no_api_key(
    db_factory: async_sessionmaker[AsyncSession],
    open_player_session: tuple[UUID, UUID],
) -> Iterator[tuple[TestClient, UUID, UUID]]:
    """TestClient with a player JWT override and NO API-key override —
    proves internal endpoints reject Bearer tokens (AW-218 AC3)."""

    async def _override_db() -> AsyncIterator[AsyncSession]:
        async with db_factory() as s:
            try:
                yield s
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    session_id, participant_id = open_player_session

    with (
        patch("api.routers.sessions._ensure_firebase_app"),
        patch("firebase_admin.auth.create_custom_token", return_value=_FAKE_TOKEN),
    ):
        claims = JwtClaims(
            uid="player-uid",
            session_id=session_id,
            player_id=participant_id,
            role="player",
        )
        app.dependency_overrides[require_player_or_host_jwt] = lambda: claims
        app.dependency_overrides[require_host_jwt] = lambda: claims
        app.dependency_overrides[get_async_session] = _override_db
        with TestClient(app) as c:
            yield c, session_id, participant_id
        app.dependency_overrides.clear()


class TestAssertKnowledge:
    def test_internal_caller_can_assert(
        self, internal_client: TestClient, open_session: UUID
    ) -> None:
        char_id = uuid4()
        resp = internal_client.post(
            f"/v1/sessions/{open_session}/knowledge",
            json={
                "character_id": str(char_id),
                "fact_type": "alibi",
                "fact_content": {"location": "library"},
                "confidence": 0.9,
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["session_id"] == str(open_session)
        assert body["character_id"] == str(char_id)
        assert body["fact_type"] == "alibi"
        assert body["confidence"] == 0.9
        assert body["revoked_at"] is None

    def test_unknown_session_returns_404(self, internal_client: TestClient) -> None:
        unknown = uuid4()
        resp = internal_client.post(
            f"/v1/sessions/{unknown}/knowledge",
            json={
                "character_id": str(uuid4()),
                "fact_type": "x",
                "fact_content": {},
            },
        )
        assert resp.status_code == 404

    def test_two_asserts_same_content_dedupe_to_one_fact(
        self, internal_client: TestClient, open_session: UUID
    ) -> None:
        """AW-248 AC: identical content -> one facts row, two ks rows."""
        char_a = uuid4()
        char_b = uuid4()

        body_template = {
            "fact_type": "alibi",
            "fact_content": {"location": "library", "time": "21:30"},
        }
        r1 = internal_client.post(
            f"/v1/sessions/{open_session}/knowledge",
            json={**body_template, "character_id": str(char_a)},
        )
        r2 = internal_client.post(
            f"/v1/sessions/{open_session}/knowledge",
            json={**body_template, "character_id": str(char_b)},
        )

        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["fact_id"] == r2.json()["fact_id"]


class TestGenerationParity:
    """AW-248 AC: GET returns the same shape build_character_generation_context reads."""

    @pytest.mark.asyncio
    async def test_assert_through_api_is_visible_to_generation_context(
        self,
        internal_client: TestClient,
        open_session: UUID,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        char_id = uuid4()

        async with db_factory() as db:
            db.add(Character(character_id=char_id, behavior_profile={}))
            await db.commit()

        resp = internal_client.post(
            f"/v1/sessions/{open_session}/knowledge",
            json={
                "character_id": str(char_id),
                "fact_type": "clue",
                "fact_content": {"detail": "library, 9pm"},
            },
        )
        assert resp.status_code == 201

        async with db_factory() as db:
            context = await build_character_generation_context(
                db, session_id=open_session, character_id=char_id
            )

        assert [f.fact_content for f in context.known_facts] == [
            {"detail": "library, 9pm"}
        ]


class TestRevokeKnowledge:
    def test_internal_caller_can_revoke(
        self, internal_client: TestClient, open_session: UUID
    ) -> None:
        char_id = uuid4()
        post = internal_client.post(
            f"/v1/sessions/{open_session}/knowledge",
            json={
                "character_id": str(char_id),
                "fact_type": "alibi",
                "fact_content": {"k": 1},
            },
        )
        fact_id = post.json()["fact_id"]

        resp = internal_client.delete(
            f"/v1/sessions/{open_session}/knowledge/{fact_id}"
        )
        assert resp.status_code == 200
        assert resp.json()["revoked_at"] is not None

    def test_revoke_is_append_only(
        self,
        internal_client: TestClient,
        open_session: UUID,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """AW-248 AC: revoke writes a new row; original never deleted."""
        char_id = uuid4()
        post = internal_client.post(
            f"/v1/sessions/{open_session}/knowledge",
            json={
                "character_id": str(char_id),
                "fact_type": "alibi",
                "fact_content": {"k": 1},
            },
        )
        fact_id = UUID(post.json()["fact_id"])

        internal_client.delete(f"/v1/sessions/{open_session}/knowledge/{fact_id}")

        async def _count_rows() -> tuple[int, int]:
            async with db_factory() as db:
                rows = (
                    (
                        await db.execute(
                            select(KnowledgeState).where(
                                KnowledgeState.session_id == open_session,
                                KnowledgeState.fact_id == fact_id,
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
                superseded = [r for r in rows if r.superseded_by is not None]
                return len(rows), len(superseded)

        import asyncio

        total, superseded = asyncio.get_event_loop().run_until_complete(_count_rows())
        assert total == 2
        assert superseded == 2

    def test_unknown_fact_returns_404(
        self, internal_client: TestClient, open_session: UUID
    ) -> None:
        resp = internal_client.delete(
            f"/v1/sessions/{open_session}/knowledge/{uuid4()}"
        )
        assert resp.status_code == 404

    def test_unknown_session_returns_404(self, internal_client: TestClient) -> None:
        resp = internal_client.delete(f"/v1/sessions/{uuid4()}/knowledge/{uuid4()}")
        assert resp.status_code == 404


class TestGetKnowledge:
    def test_internal_caller_can_query(
        self, internal_client: TestClient, open_session: UUID
    ) -> None:
        char_id = uuid4()
        internal_client.post(
            f"/v1/sessions/{open_session}/knowledge",
            json={
                "character_id": str(char_id),
                "fact_type": "alibi",
                "fact_content": {"k": 1},
            },
        )
        resp = internal_client.get(f"/v1/sessions/{open_session}/knowledge/{char_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["character_id"] == str(char_id)
        assert len(body["facts"]) == 1

    def test_revoked_facts_excluded_from_query(
        self, internal_client: TestClient, open_session: UUID
    ) -> None:
        char_id = uuid4()
        post = internal_client.post(
            f"/v1/sessions/{open_session}/knowledge",
            json={
                "character_id": str(char_id),
                "fact_type": "alibi",
                "fact_content": {"k": 1},
            },
        )
        fact_id = post.json()["fact_id"]
        internal_client.delete(f"/v1/sessions/{open_session}/knowledge/{fact_id}")

        resp = internal_client.get(f"/v1/sessions/{open_session}/knowledge/{char_id}")
        assert resp.status_code == 200
        assert resp.json()["facts"] == []

    def test_unknown_session_returns_404(self, internal_client: TestClient) -> None:
        resp = internal_client.get(f"/v1/sessions/{uuid4()}/knowledge/{uuid4()}")
        assert resp.status_code == 404


class TestPlayerCannotAccessInternalKnowledge:
    def test_player_cannot_query_any_character_knowledge(
        self, player_client_no_api_key: tuple[TestClient, UUID, UUID]
    ) -> None:
        client, session_id, _ = player_client_no_api_key
        resp = client.get(f"/v1/sessions/{session_id}/knowledge/{uuid4()}")
        assert resp.status_code in (401, 422)

    def test_player_cannot_revoke_knowledge(
        self, player_client_no_api_key: tuple[TestClient, UUID, UUID]
    ) -> None:
        client, session_id, _ = player_client_no_api_key
        resp = client.delete(f"/v1/sessions/{session_id}/knowledge/{uuid4()}")
        assert resp.status_code in (401, 422)
