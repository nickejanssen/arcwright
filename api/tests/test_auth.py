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

from api.auth import FirebaseAccount, require_firebase_account


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
