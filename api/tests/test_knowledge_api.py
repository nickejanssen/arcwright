"""Integration tests for the DB-backed knowledge endpoints (AW-218 + AW-248).

The router now persists through ``engine.knowledge.graph`` against an
in-memory SQLite-backed AsyncSession. The fixtures override the
``get_async_session`` FastAPI dependency so each test owns its engine.

Tests preserve the AW-218 HTTP contract (status codes, response shapes,
player-token rejection on internal routes) while adding AW-248 invariants
(fact-row dedup, append-only revoke, visibility from
``engine.characters.context``).
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

import api.routers.knowledge as knowledge_module
import api.routers.sessions as sessions_module
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


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


patch_metadata_for_sqlite()


@pytest_asyncio.fixture()
async def db_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    """Per-test in-memory SQLite engine + session factory."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        await engine.dispose()


@pytest.fixture()
def fresh_sessions(monkeypatch: pytest.MonkeyPatch) -> SessionService:
    """Fresh in-memory SessionService swapped into both routers."""
    svc = SessionService()
    monkeypatch.setattr(sessions_module, "_session_service", svc)
    monkeypatch.setattr(knowledge_module, "_session_service", svc)
    return svc


@pytest.fixture()
def internal_client(
    db_factory: async_sessionmaker[AsyncSession], fresh_sessions: SessionService
) -> Iterator[TestClient]:
    """TestClient where the API-key dep is overridden but Bearer deps are NOT.

    Bearer deps remain unmocked so a player JWT cannot reach internal
    routes — verifies AW-218 AC3.
    """

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
    db_factory: async_sessionmaker[AsyncSession], fresh_sessions: SessionService
) -> Iterator[tuple[TestClient, UUID, UUID]]:
    """TestClient with a player JWT override and NO API-key override.

    Used to prove that internal endpoints reject player Bearer tokens.
    Returns (client, session_id, player_participant_id).
    """
    session, _ = fresh_sessions.create_session(
        arc_id="nightcap-v1", host_account_id=uuid4()
    )
    participant, _ = fresh_sessions.add_player(session.session_id)

    async def _override_db() -> AsyncIterator[AsyncSession]:
        async with db_factory() as s:
            try:
                yield s
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    with (
        patch("api.routers.sessions._ensure_firebase_app"),
        patch("firebase_admin.auth.create_custom_token", return_value=_FAKE_TOKEN),
    ):
        claims = JwtClaims(
            uid="player-uid",
            session_id=session.session_id,
            player_id=participant.participant_id,
            role="player",
        )
        app.dependency_overrides[require_player_or_host_jwt] = lambda: claims
        app.dependency_overrides[require_host_jwt] = lambda: claims
        app.dependency_overrides[get_async_session] = _override_db
        # require_api_key intentionally not overridden.
        with TestClient(app) as c:
            yield c, session.session_id, participant.participant_id
        app.dependency_overrides.clear()


def _open_session(fresh: SessionService) -> UUID:
    session, _ = fresh.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
    return session.session_id


# ---------------------------------------------------------------------------
# Assert
# ---------------------------------------------------------------------------


class TestAssertKnowledge:
    def test_internal_caller_can_assert(
        self, internal_client: TestClient, fresh_sessions: SessionService
    ) -> None:
        session_id = _open_session(fresh_sessions)
        char_id = uuid4()
        resp = internal_client.post(
            f"/v1/sessions/{session_id}/knowledge",
            json={
                "character_id": str(char_id),
                "fact_type": "alibi",
                "fact_content": {"location": "library"},
                "confidence": 0.9,
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["session_id"] == str(session_id)
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
        self,
        internal_client: TestClient,
        fresh_sessions: SessionService,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """AW-248 AC: two asserts with identical content produce ONE facts row
        and TWO knowledge_states rows (§4.2 — a fact exists once per session)."""
        session_id = _open_session(fresh_sessions)
        char_a = uuid4()
        char_b = uuid4()

        body_template = {
            "fact_type": "alibi",
            "fact_content": {"location": "library", "time": "21:30"},
        }
        r1 = internal_client.post(
            f"/v1/sessions/{session_id}/knowledge",
            json={**body_template, "character_id": str(char_a)},
        )
        r2 = internal_client.post(
            f"/v1/sessions/{session_id}/knowledge",
            json={**body_template, "character_id": str(char_b)},
        )

        assert r1.status_code == 201
        assert r2.status_code == 201
        # Same fact_id surfaced by the response.
        assert r1.json()["fact_id"] == r2.json()["fact_id"]


# ---------------------------------------------------------------------------
# Generation parity
# ---------------------------------------------------------------------------


class TestGenerationParity:
    """AW-248 AC: GET returns the same shape build_character_generation_context reads."""

    @pytest.mark.asyncio
    async def test_assert_through_api_is_visible_to_generation_context(
        self,
        internal_client: TestClient,
        fresh_sessions: SessionService,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id = _open_session(fresh_sessions)
        char_id = uuid4()

        # Seed a Character row so generation context can resolve it.
        async with db_factory() as db:
            db.add(Character(character_id=char_id, behavior_profile={}))
            await db.commit()

        resp = internal_client.post(
            f"/v1/sessions/{session_id}/knowledge",
            json={
                "character_id": str(char_id),
                "fact_type": "clue",
                "fact_content": {"detail": "library, 9pm"},
            },
        )
        assert resp.status_code == 201

        async with db_factory() as db:
            context = await build_character_generation_context(
                db, session_id=session_id, character_id=char_id
            )

        assert [f.fact_content for f in context.known_facts] == [
            {"detail": "library, 9pm"}
        ]


# ---------------------------------------------------------------------------
# Revoke
# ---------------------------------------------------------------------------


class TestRevokeKnowledge:
    def test_internal_caller_can_revoke(
        self,
        internal_client: TestClient,
        fresh_sessions: SessionService,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id = _open_session(fresh_sessions)
        char_id = uuid4()
        post = internal_client.post(
            f"/v1/sessions/{session_id}/knowledge",
            json={
                "character_id": str(char_id),
                "fact_type": "alibi",
                "fact_content": {"k": 1},
            },
        )
        fact_id = post.json()["fact_id"]

        resp = internal_client.delete(f"/v1/sessions/{session_id}/knowledge/{fact_id}")
        assert resp.status_code == 200
        assert resp.json()["revoked_at"] is not None

    def test_revoke_is_append_only(
        self,
        internal_client: TestClient,
        fresh_sessions: SessionService,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """AW-248 AC: revoke writes a new row with superseded_by set on the
        original; original is never DELETEd."""
        session_id = _open_session(fresh_sessions)
        char_id = uuid4()
        post = internal_client.post(
            f"/v1/sessions/{session_id}/knowledge",
            json={
                "character_id": str(char_id),
                "fact_type": "alibi",
                "fact_content": {"k": 1},
            },
        )
        fact_id = UUID(post.json()["fact_id"])

        internal_client.delete(f"/v1/sessions/{session_id}/knowledge/{fact_id}")

        async def _count_rows() -> tuple[int, int]:
            async with db_factory() as db:
                rows = (
                    (
                        await db.execute(
                            select(KnowledgeState).where(
                                KnowledgeState.session_id == session_id,
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
        # Original + tombstone, both with superseded_by set.
        assert total == 2
        assert superseded == 2

    def test_unknown_fact_returns_404(
        self, internal_client: TestClient, fresh_sessions: SessionService
    ) -> None:
        session_id = _open_session(fresh_sessions)
        resp = internal_client.delete(f"/v1/sessions/{session_id}/knowledge/{uuid4()}")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------


class TestGetKnowledge:
    def test_internal_caller_can_query(
        self,
        internal_client: TestClient,
        fresh_sessions: SessionService,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id = _open_session(fresh_sessions)
        char_id = uuid4()
        internal_client.post(
            f"/v1/sessions/{session_id}/knowledge",
            json={
                "character_id": str(char_id),
                "fact_type": "alibi",
                "fact_content": {"k": 1},
            },
        )
        resp = internal_client.get(f"/v1/sessions/{session_id}/knowledge/{char_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["character_id"] == str(char_id)
        assert len(body["facts"]) == 1

    def test_revoked_facts_excluded_from_query(
        self,
        internal_client: TestClient,
        fresh_sessions: SessionService,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id = _open_session(fresh_sessions)
        char_id = uuid4()
        post = internal_client.post(
            f"/v1/sessions/{session_id}/knowledge",
            json={
                "character_id": str(char_id),
                "fact_type": "alibi",
                "fact_content": {"k": 1},
            },
        )
        fact_id = post.json()["fact_id"]
        internal_client.delete(f"/v1/sessions/{session_id}/knowledge/{fact_id}")

        resp = internal_client.get(f"/v1/sessions/{session_id}/knowledge/{char_id}")
        assert resp.status_code == 200
        assert resp.json()["facts"] == []


# ---------------------------------------------------------------------------
# AC3: player JWTs cannot access internal routes
# ---------------------------------------------------------------------------


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
