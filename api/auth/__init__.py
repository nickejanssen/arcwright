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

# The single Firebase Auth project for every Arcwright environment
# (production, staging, disposable rehearsals). Runtime Cloud Run projects
# vary; this does not. Matches billing_guard's FORBIDDEN_PROJECT_ID, which
# hardcodes the same constant as the project shutdown must never touch.
EXPECTED_FIREBASE_PROJECT_ID = "arcwright-53ea3"


class FirebaseMisconfiguredError(RuntimeError):
    """Raised when required cross-project Firebase settings are missing.

    Fails closed rather than silently falling back to ADC project
    inference: without ``projectId`` set correctly, ADC infers the
    Firebase project from the runtime's own (wrong) project and
    verify_id_token rejects every real token; without
    ``serviceAccountId``, create_custom_token silently signs as the
    runtime's own service account and the client-side token exchange
    fails with CREDENTIAL_MISMATCH. Both failure modes are confusing to
    debug from their downstream Firebase errors, so this checks the
    precondition explicitly at startup instead.
    """


def _ensure_firebase_app() -> None:
    """Initialise Firebase Admin app using ADC if not already initialised.

    Two settings matter because the runtime service account always lives
    in a different GCP project than the Firebase Auth project
    (arcwright-53ea3):

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

    Both settings are required and checked before initialisation: leaving
    either unset must raise immediately, not silently produce an app that
    fails to verify or sign tokens correctly.
    """
    if not firebase_admin._apps:
        project_id = os.environ.get("FIREBASE_PROJECT_ID")
        signing_service_account = os.environ.get(
            "FIREBASE_TOKEN_SIGNING_SERVICE_ACCOUNT"
        )
        if project_id != EXPECTED_FIREBASE_PROJECT_ID:
            raise FirebaseMisconfiguredError(
                "FIREBASE_PROJECT_ID must be set to "
                f"{EXPECTED_FIREBASE_PROJECT_ID!r}, got {project_id!r}"
            )
        if not signing_service_account:
            raise FirebaseMisconfiguredError(
                "FIREBASE_TOKEN_SIGNING_SERVICE_ACCOUNT must be set to the "
                "Firebase project's signing service account"
            )
        options = {
            "projectId": project_id,
            "serviceAccountId": signing_service_account,
        }
        firebase_admin.initialize_app(options=options)


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

    Rejects tokens that carry an ``arcwright_role`` claim. Player and
    display tokens are Arcwright-minted custom tokens exchanged for a
    real ID token via signInWithCustomToken, so they verify as valid
    Firebase ID tokens too — without this check, a player could use
    their own session token to call the host session-creation endpoint
    and mint host sessions without ever signing in as an account.

    Also rejects anonymous sign-in tokens. The identity project has
    Anonymous auth enabled (for the rehearsal test flow), so without this
    check any client could call getAuth().signInAnonymously(), obtain a
    valid ID token, and create host sessions with no real account behind
    them.
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header required")
    decoded = _decode_bearer(credentials.credentials)
    if decoded.get("arcwright_role"):
        raise HTTPException(
            status_code=401,
            detail="Session-scoped tokens are not valid for account authentication",
        )
    if decoded.get("firebase", {}).get("sign_in_provider") == "anonymous":
        raise HTTPException(
            status_code=401,
            detail="Anonymous sign-in is not valid for account authentication",
        )
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
