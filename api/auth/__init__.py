"""FastAPI auth dependencies for the Arcwright API.

Architecture: docs/architecture/09-developer-api.md §9.2.

Auth tiers:
  - API key (X-Api-Key header, value from ARCWRIGHT_API_KEY env var):
      developer-facing endpoints (create session, get session state)
  - Host JWT (Authorization: Bearer <firebase-id-token>):
      session control endpoints (start, pause, resume, end)
  - Public (no auth):
      join endpoint

Firebase Admin is initialised lazily using Application Default Credentials.
No credentials or service-account JSON appear in this file.
On GCP (Cloud Run), ADC resolves automatically via the metadata server.
Locally, set GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON path.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import firebase_admin
from fastapi import Header, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth
from firebase_admin import exceptions as firebase_exceptions

logger = logging.getLogger(__name__)

_bearer = HTTPBearer(auto_error=False)


def _ensure_firebase_app() -> None:
    """Initialise Firebase Admin app using ADC if not already initialised.

    Two settings matter when the runtime service account lives in a
    different GCP project than the Firebase Auth project (e.g. a
    disposable Cloud Run project verifying tokens from arcwright-53ea3):

    - ``projectId`` (FIREBASE_PROJECT_ID): without it, ADC infers the
      Firebase project from the runtime's own project, and verify_id_token
      rejects every real token with an "incorrect aud claim" error.
    - ``serviceAccountId`` (FIREBASE_TOKEN_SIGNING_SERVICE_ACCOUNT):
      Firebase's signInWithCustomToken rejects tokens signed by a service
      account outside the Firebase project, regardless of IAM roles
      granted on that project — this is a hard Google-side restriction,
      not a permissions gap. Without it, create_custom_token silently
      signs as the runtime's own (wrong-project) service account and the
      client-side token exchange fails with CREDENTIAL_MISMATCH. Setting
      it makes the Admin SDK sign custom tokens via IAM signBlob
      impersonation of a service account that actually belongs to the
      Firebase project; the runtime service account needs
      roles/iam.serviceAccountTokenCreator on that target service account.
    """
    if not firebase_admin._apps:
        options: dict[str, str] = {}
        project_id = os.environ.get("FIREBASE_PROJECT_ID")
        if project_id:
            options["projectId"] = project_id
        signing_service_account = os.environ.get(
            "FIREBASE_TOKEN_SIGNING_SERVICE_ACCOUNT"
        )
        if signing_service_account:
            options["serviceAccountId"] = signing_service_account
        firebase_admin.initialize_app(options=options or None)


@dataclass(frozen=True)
class ApiCaller:
    api_key: str


@dataclass(frozen=True)
class JwtClaims:
    uid: str
    session_id: UUID | None
    player_id: UUID | None
    role: str  # "host" | "player" | "display"


@dataclass(frozen=True)
class FirebaseAccount:
    """A verified Firebase account identity, not scoped to any session.

    Distinct from JwtClaims: account tokens come directly from the
    Firebase client SDK (Email/Password, Google, or Phone sign-in) and
    carry no ``arcwright_role`` custom claim. They authenticate "this is
    a specific human account" for host session creation, not "this
    token is authorized for session X".
    """

    uid: str
    email: str | None


async def require_api_key(
    x_api_key: str = Header(alias="X-Api-Key"),
) -> ApiCaller:
    """Dependency: require a valid API key in the X-Api-Key header."""
    expected = os.environ.get("ARCWRIGHT_API_KEY", "")
    if not expected or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return ApiCaller(api_key=x_api_key)


async def require_firebase_account(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> FirebaseAccount:
    """Dependency: require a Firebase ID token identifying a human account.

    Unlike ``require_host_jwt``, this does not require an
    ``arcwright_role`` custom claim: it accepts any valid Firebase ID
    token issued directly by the client SDK (Email/Password, Google, or
    Phone sign-in). Used to authenticate host session creation by a
    stable Firebase account identity rather than a session-scoped
    custom token. Token verification (signature, expiry, project
    audience) is identical to the other dependencies in this module.
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header required")
    decoded = _decode_bearer(credentials.credentials)
    return FirebaseAccount(uid=decoded["uid"], email=decoded.get("email"))


def _decode_bearer(token: str) -> dict[str, Any]:
    _ensure_firebase_app()
    try:
        decoded: dict[str, Any] = firebase_auth.verify_id_token(token)
        return decoded
    except firebase_exceptions.FirebaseError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


async def require_host_jwt(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> JwtClaims:
    """Dependency: require a Firebase ID token with role=host."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header required")
    decoded = _decode_bearer(credentials.credentials)
    role = decoded.get("arcwright_role", "")
    if role != "host":
        raise HTTPException(status_code=403, detail="Host token required")
    session_id_str = decoded.get("arcwright_session_id")
    player_id_str = decoded.get("arcwright_player_id")
    return JwtClaims(
        uid=decoded["uid"],
        session_id=UUID(session_id_str) if session_id_str else None,
        player_id=UUID(player_id_str) if player_id_str else None,
        role=role,
    )


async def require_player_jwt(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> JwtClaims:
    """Dependency: require a Firebase ID token with role=player only."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header required")
    decoded = _decode_bearer(credentials.credentials)
    role = decoded.get("arcwright_role", "")
    if role != "player":
        raise HTTPException(status_code=403, detail="Player token required")
    session_id_str = decoded.get("arcwright_session_id")
    player_id_str = decoded.get("arcwright_player_id")
    return JwtClaims(
        uid=decoded["uid"],
        session_id=UUID(session_id_str) if session_id_str else None,
        player_id=UUID(player_id_str) if player_id_str else None,
        role=role,
    )


async def require_player_or_host_jwt(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> JwtClaims:
    """Dependency: require a Firebase ID token with role=player, host, or display."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header required")
    decoded = _decode_bearer(credentials.credentials)
    role = decoded.get("arcwright_role", "")
    if role not in ("player", "host", "display"):
        raise HTTPException(status_code=403, detail="Valid participant token required")
    session_id_str = decoded.get("arcwright_session_id")
    player_id_str = decoded.get("arcwright_player_id")
    return JwtClaims(
        uid=decoded["uid"],
        session_id=UUID(session_id_str) if session_id_str else None,
        player_id=UUID(player_id_str) if player_id_str else None,
        role=role,
    )


async def optional_player_or_host_jwt(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> "JwtClaims | None":
    """Dependency: validate a Firebase ID token if present; return None otherwise.

    Endpoints that serve both authenticated participants and unauthenticated
    display surfaces use this. A missing Authorization header returns None.
    Production auth enforcement is deferred to M5 (AW-269).
    """
    if credentials is None:
        return None
    decoded = _decode_bearer(credentials.credentials)
    role = decoded.get("arcwright_role", "")
    if role not in ("player", "host", "display"):
        raise HTTPException(status_code=403, detail="Valid participant token required")
    session_id_str = decoded.get("arcwright_session_id")
    player_id_str = decoded.get("arcwright_player_id")
    return JwtClaims(
        uid=decoded["uid"],
        session_id=UUID(session_id_str) if session_id_str else None,
        player_id=UUID(player_id_str) if player_id_str else None,
        role=role,
    )


async def require_api_key_or_host_jwt(request: Request) -> ApiCaller | JwtClaims:
    """Dependency: accept either an API key or a host JWT."""
    api_key = request.headers.get("X-Api-Key")
    if api_key:
        expected = os.environ.get("ARCWRIGHT_API_KEY", "")
        if not expected or api_key != expected:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return ApiCaller(api_key=api_key)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        decoded = _decode_bearer(token)
        role = decoded.get("arcwright_role", "")
        if role not in ("host",):
            raise HTTPException(status_code=403, detail="Host token required")
        session_id_str = decoded.get("arcwright_session_id")
        return JwtClaims(
            uid=decoded["uid"],
            session_id=UUID(session_id_str) if session_id_str else None,
            player_id=None,
            role=role,
        )
    raise HTTPException(status_code=401, detail="API key or host token required")
