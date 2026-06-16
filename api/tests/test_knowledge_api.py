"""Integration tests for the knowledge endpoints (AW-218 AC2, AC3).

Specifically proves that player JWTs cannot reach the GET and DELETE
knowledge endpoints — those are restricted to internal API-key callers in
§9.2. Per-session singletons are replaced per-test for isolation.
"""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
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
from engine.knowledge.service import KnowledgeService
from engine.session.service import SessionService

_FAKE_TOKEN = b"fake-firebase-custom-token"


@pytest.fixture()
def services(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[SessionService, KnowledgeService]:
    sessions = SessionService()
    knowledge = KnowledgeService()
    monkeypatch.setattr(sessions_module, "_session_service", sessions)
    monkeypatch.setattr(knowledge_module, "_session_service", sessions)
    monkeypatch.setattr(knowledge_module, "_knowledge_service", knowledge)
    return sessions, knowledge


@pytest.fixture()
def open_session(
    services: tuple[SessionService, KnowledgeService],
) -> tuple[SessionService, KnowledgeService, UUID]:
    sessions, knowledge = services
    session, _ = sessions.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
    return sessions, knowledge, session.session_id


def _internal_client() -> Iterator[TestClient]:
    """TestClient where the API-key dep is overridden but Bearer deps are NOT.

    require_player_or_host_jwt and require_host_jwt remain unmocked here
    because the DELETE and GET knowledge routes must NOT depend on them.
    If a future refactor accidentally wires Bearer auth onto those routes,
    the test will fail loudly.
    """
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
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()


def _player_client_no_api_key(
    session_id: UUID, player_id: UUID
) -> Iterator[TestClient]:
    """TestClient with a player JWT override but no API-key override.

    Used to prove that internal endpoints reject player tokens.
    """
    with (
        patch("api.routers.sessions._ensure_firebase_app"),
        patch("firebase_admin.auth.create_custom_token", return_value=_FAKE_TOKEN),
    ):
        claims = JwtClaims(
            uid="player-uid",
            session_id=session_id,
            player_id=player_id,
            role="player",
        )
        app.dependency_overrides[require_player_or_host_jwt] = lambda: claims
        app.dependency_overrides[require_host_jwt] = lambda: claims
        # require_api_key is intentionally NOT overridden.
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()


class TestAssertKnowledge:
    def test_internal_caller_can_assert(
        self, open_session: tuple[SessionService, KnowledgeService, UUID]
    ) -> None:
        _, knowledge, session_id = open_session
        char_id = uuid4()
        for c in _internal_client():
            resp = c.post(
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
        assert len(knowledge.get_character_knowledge(session_id, char_id)) == 1

    def test_unknown_session_returns_404(
        self, services: tuple[SessionService, KnowledgeService]
    ) -> None:
        unknown = uuid4()
        for c in _internal_client():
            resp = c.post(
                f"/v1/sessions/{unknown}/knowledge",
                json={
                    "character_id": str(uuid4()),
                    "fact_type": "x",
                    "fact_content": {},
                },
            )
        assert resp.status_code == 404


class TestRevokeKnowledge:
    def test_internal_caller_can_revoke(
        self, open_session: tuple[SessionService, KnowledgeService, UUID]
    ) -> None:
        _, knowledge, session_id = open_session
        char_id = uuid4()
        fact = knowledge.assert_fact(
            session_id=session_id,
            character_id=char_id,
            fact_type="x",
            fact_content={},
        )
        for c in _internal_client():
            resp = c.delete(f"/v1/sessions/{session_id}/knowledge/{fact.fact_id}")
        assert resp.status_code == 200
        assert resp.json()["revoked_at"] is not None
        assert knowledge.get_character_knowledge(session_id, char_id) == []

    def test_unknown_fact_returns_404(
        self, open_session: tuple[SessionService, KnowledgeService, UUID]
    ) -> None:
        _, _, session_id = open_session
        for c in _internal_client():
            resp = c.delete(f"/v1/sessions/{session_id}/knowledge/{uuid4()}")
        assert resp.status_code == 404


class TestGetKnowledge:
    def test_internal_caller_can_query(
        self, open_session: tuple[SessionService, KnowledgeService, UUID]
    ) -> None:
        _, knowledge, session_id = open_session
        char_id = uuid4()
        knowledge.assert_fact(
            session_id=session_id,
            character_id=char_id,
            fact_type="alibi",
            fact_content={"k": 1},
        )
        for c in _internal_client():
            resp = c.get(f"/v1/sessions/{session_id}/knowledge/{char_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["character_id"] == str(char_id)
        assert len(body["facts"]) == 1


class TestPlayerCannotAccessInternalKnowledge:
    """AC3: Player clients must not be able to query character knowledge state."""

    def test_player_cannot_query_any_character_knowledge(
        self, open_session: tuple[SessionService, KnowledgeService, UUID]
    ) -> None:
        sessions, knowledge, session_id = open_session
        # Create a player so the JWT is realistic. Player attempts to read
        # their OWN character's knowledge — the endpoint must still reject.
        participant, _ = sessions.add_player(session_id)
        knowledge.assert_fact(
            session_id=session_id,
            character_id=participant.character_id,
            fact_type="alibi",
            fact_content={"private": True},
        )
        for c in _player_client_no_api_key(session_id, participant.participant_id):
            resp = c.get(
                f"/v1/sessions/{session_id}/knowledge/{participant.character_id}"
            )
        # No X-Api-Key header was sent, so FastAPI fails the dependency.
        # 401 (missing/invalid) or 422 (header missing) both prove rejection;
        # the spec requires player Bearer tokens NOT be a valid credential here.
        assert resp.status_code in (401, 422)

    def test_player_cannot_query_another_characters_knowledge(
        self, open_session: tuple[SessionService, KnowledgeService, UUID]
    ) -> None:
        sessions, knowledge, session_id = open_session
        owner, _ = sessions.add_player(session_id)
        intruder, _ = sessions.add_player(session_id)
        knowledge.assert_fact(
            session_id=session_id,
            character_id=owner.character_id,
            fact_type="secret",
            fact_content={"who_did_it": True},
        )
        for c in _player_client_no_api_key(session_id, intruder.participant_id):
            resp = c.get(f"/v1/sessions/{session_id}/knowledge/{owner.character_id}")
        assert resp.status_code in (401, 422)

    def test_player_cannot_revoke_knowledge(
        self, open_session: tuple[SessionService, KnowledgeService, UUID]
    ) -> None:
        sessions, knowledge, session_id = open_session
        participant, _ = sessions.add_player(session_id)
        fact = knowledge.assert_fact(
            session_id=session_id,
            character_id=participant.character_id,
            fact_type="x",
            fact_content={},
        )
        for c in _player_client_no_api_key(session_id, participant.participant_id):
            resp = c.delete(f"/v1/sessions/{session_id}/knowledge/{fact.fact_id}")
        assert resp.status_code in (401, 422)
        # Fact must still be active.
        assert (
            len(knowledge.get_character_knowledge(session_id, participant.character_id))
            == 1
        )
