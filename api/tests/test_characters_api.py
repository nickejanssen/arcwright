"""Integration tests for the character endpoints (AW-218 AC1, AC3).

Firebase is mocked; the in-memory SessionService and CharacterService
singletons are replaced per-test for isolation.
"""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from starlette.testclient import TestClient

import api.routers.characters as characters_module
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
from engine.characters.service import CharacterService
from engine.session.service import SessionService

_FAKE_TOKEN = b"fake-firebase-custom-token"


@pytest.fixture()
def services(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[SessionService, CharacterService]:
    sessions = SessionService()
    characters = CharacterService(sessions=sessions)
    monkeypatch.setattr(sessions_module, "_session_service", sessions)
    monkeypatch.setattr(characters_module, "_session_service", sessions)
    monkeypatch.setattr(characters_module, "_character_service", characters)
    return sessions, characters


@pytest.fixture()
def host_session(
    services: tuple[SessionService, CharacterService],
) -> tuple[SessionService, CharacterService, UUID, UUID, UUID, UUID]:
    """A session with one host plus two players. Returns (sessions, characters,
    session_id, player_a_participant_id, player_a_character_id,
    player_b_character_id)."""
    sessions, characters = services
    session, _ = sessions.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
    a, _ = sessions.add_player(session.session_id)
    b, _ = sessions.add_player(session.session_id)
    return (
        sessions,
        characters,
        session.session_id,
        a.participant_id,
        a.character_id,
        b.character_id,
    )


def _client_for_role(
    role: str, session_id: UUID, player_id: UUID | None
) -> Iterator[TestClient]:
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
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()


class TestListCharacters:
    def test_host_sees_all_player_characters(
        self,
        host_session: tuple[SessionService, CharacterService, UUID, UUID, UUID, UUID],
    ) -> None:
        _, _, session_id, _, char_a, char_b = host_session
        for c in _client_for_role("host", session_id, uuid4()):
            resp = c.get(f"/v1/sessions/{session_id}/characters")
        assert resp.status_code == 200
        body = resp.json()
        assert body["session_id"] == str(session_id)
        ids = {item["character_id"] for item in body["characters"]}
        assert ids == {str(char_a), str(char_b)}

    def test_unknown_session_returns_404(
        self, services: tuple[SessionService, CharacterService]
    ) -> None:
        unknown = uuid4()
        for c in _client_for_role("host", unknown, uuid4()):
            resp = c.get(f"/v1/sessions/{unknown}/characters")
        assert resp.status_code == 404


class TestGetCharacterDetail:
    def test_owner_gets_own_character(
        self,
        host_session: tuple[SessionService, CharacterService, UUID, UUID, UUID, UUID],
    ) -> None:
        _, _, session_id, player_a, char_a, _ = host_session
        for c in _client_for_role("player", session_id, player_a):
            resp = c.get(f"/v1/sessions/{session_id}/characters/{char_a}")
        assert resp.status_code == 200
        assert resp.json()["character_id"] == str(char_a)

    def test_player_cannot_read_another_characters_detail(
        self,
        host_session: tuple[SessionService, CharacterService, UUID, UUID, UUID, UUID],
    ) -> None:
        _, _, session_id, player_a, _, char_b = host_session
        for c in _client_for_role("player", session_id, player_a):
            resp = c.get(f"/v1/sessions/{session_id}/characters/{char_b}")
        assert resp.status_code == 403


class TestSubmitInput:
    def test_player_submits_dialogue_as_own_character(
        self,
        host_session: tuple[SessionService, CharacterService, UUID, UUID, UUID, UUID],
    ) -> None:
        _, characters, session_id, player_a, char_a, _ = host_session
        for c in _client_for_role("player", session_id, player_a):
            resp = c.post(
                f"/v1/sessions/{session_id}/characters/{char_a}/input",
                json={"kind": "dialogue", "content": "Where were you?"},
            )
        assert resp.status_code == 201
        body = resp.json()
        assert body["kind"] == "dialogue"
        assert body["character_id"] == str(char_a)
        assert len(characters.get_inputs(session_id)) == 1

    def test_player_cannot_submit_as_another_character(
        self,
        host_session: tuple[SessionService, CharacterService, UUID, UUID, UUID, UUID],
    ) -> None:
        _, characters, session_id, player_a, _, char_b = host_session
        for c in _client_for_role("player", session_id, player_a):
            resp = c.post(
                f"/v1/sessions/{session_id}/characters/{char_b}/input",
                json={"kind": "action", "content": "impersonation"},
            )
        assert resp.status_code == 403
        assert characters.get_inputs(session_id) == []

    def test_empty_content_is_rejected(
        self,
        host_session: tuple[SessionService, CharacterService, UUID, UUID, UUID, UUID],
    ) -> None:
        _, _, session_id, player_a, char_a, _ = host_session
        for c in _client_for_role("player", session_id, player_a):
            resp = c.post(
                f"/v1/sessions/{session_id}/characters/{char_a}/input",
                json={"kind": "dialogue", "content": ""},
            )
        assert resp.status_code == 422

    def test_unknown_kind_is_rejected(
        self,
        host_session: tuple[SessionService, CharacterService, UUID, UUID, UUID, UUID],
    ) -> None:
        _, _, session_id, player_a, char_a, _ = host_session
        for c in _client_for_role("player", session_id, player_a):
            resp = c.post(
                f"/v1/sessions/{session_id}/characters/{char_a}/input",
                json={"kind": "narration", "content": "foo"},
            )
        assert resp.status_code == 422

    def test_host_token_cannot_submit_input(
        self,
        host_session: tuple[SessionService, CharacterService, UUID, UUID, UUID, UUID],
    ) -> None:
        _, characters, session_id, _, char_a, _ = host_session
        for c in _client_for_role("host", session_id, uuid4()):
            resp = c.post(
                f"/v1/sessions/{session_id}/characters/{char_a}/input",
                json={"kind": "dialogue", "content": "host attempt"},
            )
        assert resp.status_code == 403
        assert characters.get_inputs(session_id) == []

    def test_display_token_cannot_submit_input(
        self,
        host_session: tuple[SessionService, CharacterService, UUID, UUID, UUID, UUID],
    ) -> None:
        _, characters, session_id, _, char_a, _ = host_session
        for c in _client_for_role("display", session_id, uuid4()):
            resp = c.post(
                f"/v1/sessions/{session_id}/characters/{char_a}/input",
                json={"kind": "dialogue", "content": "display attempt"},
            )
        assert resp.status_code == 403
        assert characters.get_inputs(session_id) == []
