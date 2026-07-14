"""Unit tests for api/auth Firebase dependencies (AW-269 host identity bridge).

Firebase Admin is mocked so these run without GCP credentials. Focuses on
require_firebase_account: valid account tokens, expired/invalid tokens,
wrong-project tokens, and missing tokens. require_host_jwt's existing
session-claim behavior is exercised separately in test_sessions_api.py
against the new authenticated host session path.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from firebase_admin import exceptions as firebase_exceptions

from api.auth import (
    FirebaseAccount,
    FirebaseMisconfiguredError,
    _ensure_firebase_app,
    require_firebase_account,
)


def _credentials(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


class TestRequireFirebaseAccount:
    @pytest.mark.asyncio
    async def test_valid_token_returns_firebase_account(self) -> None:
        with (
            patch("api.auth._ensure_firebase_app"),
            patch(
                "firebase_admin.auth.verify_id_token",
                return_value={"uid": "firebase-uid-123", "email": "host@example.com"},
            ),
        ):
            account = await require_firebase_account(_credentials("valid-token"))

        assert account == FirebaseAccount(
            uid="firebase-uid-123", email="host@example.com"
        )

    @pytest.mark.asyncio
    async def test_valid_token_without_email_returns_none_email(self) -> None:
        with (
            patch("api.auth._ensure_firebase_app"),
            patch(
                "firebase_admin.auth.verify_id_token",
                return_value={"uid": "firebase-uid-456"},
            ),
        ):
            account = await require_firebase_account(_credentials("valid-token"))

        assert account.uid == "firebase-uid-456"
        assert account.email is None

    @pytest.mark.asyncio
    async def test_expired_token_raises_401(self) -> None:
        with (
            patch("api.auth._ensure_firebase_app"),
            patch(
                "firebase_admin.auth.verify_id_token",
                side_effect=firebase_exceptions.InvalidArgumentError("Token expired"),
            ),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await require_firebase_account(_credentials("expired-token"))

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_wrong_project_token_raises_401(self) -> None:
        # Firebase Admin raises the same FirebaseError family for audience
        # (project) mismatches as it does for any other invalid token.
        with (
            patch("api.auth._ensure_firebase_app"),
            patch(
                "firebase_admin.auth.verify_id_token",
                side_effect=firebase_exceptions.InvalidArgumentError(
                    "Firebase ID token has incorrect audience"
                ),
            ),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await require_firebase_account(_credentials("wrong-project-token"))

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_token_raises_401(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            await require_firebase_account(None)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_session_scoped_token_is_rejected(self) -> None:
        """A player/display token exchanged to a real ID token still carries
        arcwright_role — it must not be usable as an account token."""
        with (
            patch("api.auth._ensure_firebase_app"),
            patch(
                "firebase_admin.auth.verify_id_token",
                return_value={
                    "uid": "session:abc:player:def",
                    "arcwright_role": "player",
                    "arcwright_session_id": "abc",
                    "arcwright_player_id": "def",
                },
            ),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await require_firebase_account(_credentials("player-session-token"))

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_host_session_scoped_token_is_rejected(self) -> None:
        with (
            patch("api.auth._ensure_firebase_app"),
            patch(
                "firebase_admin.auth.verify_id_token",
                return_value={
                    "uid": "session:abc:host",
                    "arcwright_role": "host",
                    "arcwright_session_id": "abc",
                },
            ),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await require_firebase_account(_credentials("host-session-token"))

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_anonymous_sign_in_token_is_rejected(self) -> None:
        """The identity project has Anonymous auth enabled for the rehearsal
        phone-sign-in flow — without this check, signInAnonymously() would
        mint host sessions with no real account behind them."""
        with (
            patch("api.auth._ensure_firebase_app"),
            patch(
                "firebase_admin.auth.verify_id_token",
                return_value={
                    "uid": "anon-uid-789",
                    "firebase": {"sign_in_provider": "anonymous"},
                },
            ),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await require_firebase_account(_credentials("anonymous-token"))

        assert exc_info.value.status_code == 401


class TestEnsureFirebaseApp:
    """The expected Firebase project varies per deployment (production is
    arcwright-prod per docs/roadmap/operations/cloud-deploy-runbook.md
    §5.1; disposable rehearsal deployments use their own project). These
    checks only require both settings to be explicitly configured, not
    that either equals one hardcoded value."""

    def test_raises_when_project_id_unset(self, monkeypatch) -> None:
        monkeypatch.delenv("FIREBASE_PROJECT_ID", raising=False)
        monkeypatch.setenv(
            "FIREBASE_TOKEN_SIGNING_SERVICE_ACCOUNT",
            "sa@example.iam.gserviceaccount.com",
        )
        with patch("firebase_admin._apps", []):
            with pytest.raises(FirebaseMisconfiguredError):
                _ensure_firebase_app()

    def test_raises_when_signing_service_account_unset(self, monkeypatch) -> None:
        monkeypatch.setenv("FIREBASE_PROJECT_ID", "any-configured-project")
        monkeypatch.delenv("FIREBASE_TOKEN_SIGNING_SERVICE_ACCOUNT", raising=False)
        with patch("firebase_admin._apps", []):
            with pytest.raises(FirebaseMisconfiguredError):
                _ensure_firebase_app()

    def test_accepts_the_deployments_own_configured_project_id(
        self, monkeypatch
    ) -> None:
        monkeypatch.setenv("FIREBASE_PROJECT_ID", "arcwright-prod")
        monkeypatch.setenv(
            "FIREBASE_TOKEN_SIGNING_SERVICE_ACCOUNT",
            "sa@example.iam.gserviceaccount.com",
        )
        with (
            patch("firebase_admin._apps", []),
            patch("firebase_admin.initialize_app") as init_app,
        ):
            _ensure_firebase_app()

        init_app.assert_called_once_with(
            options={
                "projectId": "arcwright-prod",
                "serviceAccountId": "sa@example.iam.gserviceaccount.com",
            }
        )
