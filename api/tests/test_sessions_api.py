"""Integration tests for the session lifecycle REST API endpoints (AW-217).

Exercises routes at the HTTP level via starlette.testclient.TestClient to prove
that routers are mounted, auth dependencies are wired, and handlers return the
documented HTTP status codes and response shapes.

Firebase is mocked so tests run without GCP credentials. The module-level
_session_service singleton is replaced per-test for isolation.
"""

from __future__ import annotations

from unittest.mock import patch
from uuid import uuid4

import pytest
from starlette.testclient import TestClient

import api.routers.sessions as sessions_module
from api.auth import (
    ApiCaller,
    JwtClaims,
    require_api_key,
    require_api_key_or_host_jwt,
    require_host_jwt,
)
from api.main import app
from engine.session.service import SessionService

_FAKE_TOKEN = b"fake-firebase-custom-token"


@pytest.fixture()
def fresh_svc(monkeypatch: pytest.MonkeyPatch) -> SessionService:
    """Replace the sessions-router singleton with a clean SessionService."""
    svc = SessionService()
    monkeypatch.setattr(sessions_module, "_session_service", svc)
    return svc


@pytest.fixture()
def client(fresh_svc: SessionService) -> TestClient:
    """TestClient with auth dependencies overridden and Firebase calls mocked."""
    with (
        patch("api.routers.sessions._ensure_firebase_app"),
        patch("firebase_admin.auth.create_custom_token", return_value=_FAKE_TOKEN),
    ):
        app.dependency_overrides[require_api_key] = lambda: ApiCaller(
            api_key="test-key"
        )
        app.dependency_overrides[require_host_jwt] = lambda: JwtClaims(
            uid="host-uid", session_id=None, player_id=uuid4(), role="host"
        )
        app.dependency_overrides[require_api_key_or_host_jwt] = lambda: ApiCaller(
            api_key="test-key"
        )
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()


class TestCreateSession:
    def test_returns_201_with_required_fields(self, client: TestClient) -> None:
        resp = client.post("/v1/sessions", json={"arc_id": "nightcap-v1"})

        assert resp.status_code == 201
        body = resp.json()
        assert "session_id" in body
        assert "host_token" in body
        assert "host_join_token" in body
        assert "join_url" in body

    def test_missing_arc_id_returns_422(self, client: TestClient) -> None:
        resp = client.post("/v1/sessions", json={})
        assert resp.status_code == 422


class TestGetSession:
    def test_known_session_returns_200(
        self, client: TestClient, fresh_svc: SessionService
    ) -> None:
        session, _ = fresh_svc.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        resp = client.get(f"/v1/sessions/{session.session_id}")

        assert resp.status_code == 200
        assert resp.json()["session_id"] == str(session.session_id)

    def test_unknown_session_returns_404(self, client: TestClient) -> None:
        resp = client.get(f"/v1/sessions/{uuid4()}")
        assert resp.status_code == 404


class TestStartSession:
    def test_start_returns_active_status(
        self, client: TestClient, fresh_svc: SessionService
    ) -> None:
        session, _ = fresh_svc.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        resp = client.post(f"/v1/sessions/{session.session_id}/start")

        assert resp.status_code == 200
        assert resp.json()["status"] == "active"

    def test_unknown_session_returns_404(self, client: TestClient) -> None:
        resp = client.post(f"/v1/sessions/{uuid4()}/start")
        assert resp.status_code == 404

    def test_double_start_returns_409(
        self, client: TestClient, fresh_svc: SessionService
    ) -> None:
        session, _ = fresh_svc.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        client.post(f"/v1/sessions/{session.session_id}/start")
        resp = client.post(f"/v1/sessions/{session.session_id}/start")
        assert resp.status_code == 409


class TestPauseResumeSession:
    def test_pause_returns_paused_status(
        self, client: TestClient, fresh_svc: SessionService
    ) -> None:
        session, _ = fresh_svc.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        fresh_svc.start_session(session.session_id, uuid4())
        resp = client.post(f"/v1/sessions/{session.session_id}/pause")

        assert resp.status_code == 200
        assert resp.json()["status"] == "paused"

    def test_resume_returns_active_status(
        self, client: TestClient, fresh_svc: SessionService
    ) -> None:
        session, _ = fresh_svc.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        fresh_svc.start_session(session.session_id, uuid4())
        fresh_svc.pause_session(session.session_id, uuid4())
        resp = client.post(f"/v1/sessions/{session.session_id}/resume")

        assert resp.status_code == 200
        assert resp.json()["status"] == "active"


class TestEndSession:
    def test_end_returns_completed_status(
        self, client: TestClient, fresh_svc: SessionService
    ) -> None:
        session, _ = fresh_svc.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        fresh_svc.start_session(session.session_id, uuid4())
        resp = client.post(f"/v1/sessions/{session.session_id}/end")

        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_unknown_session_returns_404(self, client: TestClient) -> None:
        resp = client.post(f"/v1/sessions/{uuid4()}/end")
        assert resp.status_code == 404


class TestAddPlayer:
    def test_returns_201_with_join_token(
        self, client: TestClient, fresh_svc: SessionService
    ) -> None:
        session, _ = fresh_svc.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        resp = client.post(f"/v1/sessions/{session.session_id}/players")

        assert resp.status_code == 201
        body = resp.json()
        assert "participant_id" in body
        assert "join_token" in body
        assert "join_url" in body

    def test_unknown_session_returns_404(self, client: TestClient) -> None:
        resp = client.post(f"/v1/sessions/{uuid4()}/players")
        assert resp.status_code == 404


class TestJoinSession:
    def test_valid_token_returns_player_token(
        self, client: TestClient, fresh_svc: SessionService
    ) -> None:
        session, _ = fresh_svc.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        _, join_token = fresh_svc.add_player(session.session_id)
        resp = client.get(f"/v1/sessions/{session.session_id}/join?token={join_token}")

        assert resp.status_code == 200
        assert "player_token" in resp.json()

    def test_invalid_token_returns_403(
        self, client: TestClient, fresh_svc: SessionService
    ) -> None:
        session, _ = fresh_svc.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        resp = client.get(
            f"/v1/sessions/{session.session_id}/join?token=not-a-real-token"
        )
        assert resp.status_code == 403
