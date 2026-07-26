"""Smoke test against the live local rehearsal stack."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SHARED_ROOT = (
    REPO_ROOT.parent.parent if REPO_ROOT.parent.name == ".worktrees" else REPO_ROOT
)
ENV_FILE = REPO_ROOT / ".env"
SHARED_ENV_FILE = SHARED_ROOT / ".env"
BASE = "http://localhost:8000"
DEFAULT_ARC_ID = "nightcap-couch-race-v1"


def fail(step: str, message: str) -> None:
    print(f"[FAIL] {step}: {message}", file=sys.stderr)
    raise SystemExit(1)


def ensure_python() -> None:
    if sys.version_info >= (3, 11):
        return

    candidates = [
        REPO_ROOT / ".venv" / "Scripts" / "python.exe",
        REPO_ROOT.parent / ".aw102-venv" / "Scripts" / "python.exe",
    ]
    uv_root = REPO_ROOT / ".uv-python"
    if uv_root.exists():
        candidates.extend(sorted(uv_root.glob("*/python.exe")))

    for candidate in candidates:
        if candidate.exists():
            os.execv(str(candidate), [str(candidate), *sys.argv])

    fail("python", "Python 3.11+ is required")


def read_env() -> dict[str, str]:
    env_path = ENV_FILE if ENV_FILE.exists() else SHARED_ENV_FILE
    if not env_path.exists():
        fail(".env", "missing .env at repo root")
    env: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    for key in (
        "ARCWRIGHT_API_KEY",
        "FIREBASE_PROJECT_ID",
        "FIREBASE_TOKEN_SIGNING_SERVICE_ACCOUNT",
        "FIREBASE_WEB_API_KEY",
    ):
        if not env.get(key):
            fail(".env", f"{key} must be set for rehearsal-smoke")
    return env


def call(
    step: str,
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 15,
) -> dict[str, Any]:
    request = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        method=method,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
            data = json.loads(payload or b"{}")
            print(f"[ok] {step} -> {response.status}")
            return data
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        fail(step, f"HTTP {exc.code}\n{detail}")
    except urllib.error.URLError as exc:
        fail(step, f"{exc.reason} - is `make rehearsal` running?")
    return {}


def exchange_firebase_token(step: str, custom_token: str, web_api_key: str) -> str:
    request = urllib.request.Request(
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken"
        f"?key={web_api_key}",
        data=json.dumps({"token": custom_token, "returnSecureToken": True}).encode(
            "utf-8"
        ),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        fail(step, f"HTTP {exc.code}\n{detail}")
    except urllib.error.URLError as exc:
        fail(step, str(exc.reason))

    token = data.get("idToken")
    if not token:
        fail(step, "response did not include idToken")
    print(f"[ok] {step} -> 200")
    return str(token)


def main() -> None:
    ensure_python()
    env = read_env()

    call("api-health", "GET", "/health")

    session = call(
        "create-session",
        "POST",
        "/v1/sessions",
        body={"arc_id": DEFAULT_ARC_ID},
        headers={"X-Api-Key": env["ARCWRIGHT_API_KEY"]},
    )
    session_id = str(session["session_id"])

    lobby = call("join-code-lookup", "GET", f"/v1/sessions/{session_id}/lobby")
    join_code = str(lobby["join_code"])

    first_player = call(
        "player-join-1",
        "POST",
        "/v1/lobby-join",
        body={"name": "Smoke One", "join_code": join_code},
    )
    second_player = call(
        "player-join-2",
        "POST",
        "/v1/lobby-join",
        body={"name": "Smoke Two", "join_code": join_code},
    )

    host_id_token = exchange_firebase_token(
        "host-token-exchange",
        str(session["host_token"]),
        env["FIREBASE_WEB_API_KEY"],
    )
    started = call(
        "start-session",
        "POST",
        f"/v1/sessions/{session_id}/start",
        headers={"Authorization": f"Bearer {host_id_token}"},
    )

    # POST /start flips session status to "active" and returns the new state.
    # It does not itself publish a ContentEvent, so assert the state transition
    # rather than waiting for an event that the start path never emits.
    status = str(started.get("status"))
    if status != "active":
        fail("start-session", f"expected status 'active', got {status!r}")
    print(f"[ok] session-active -> status={status}")

    first_player_token = exchange_firebase_token(
        "player-token-exchange-1",
        str(first_player["player_token"]),
        env["FIREBASE_WEB_API_KEY"],
    )
    second_player_token = exchange_firebase_token(
        "player-token-exchange-2",
        str(second_player["player_token"]),
        env["FIREBASE_WEB_API_KEY"],
    )
    first_character_id = str(first_player["character_id"])
    second_character_id = str(second_player["character_id"])
    call(
        "player-action-1",
        "POST",
        f"/v1/sessions/{session_id}/characters/{first_character_id}/input",
        body={"kind": "action", "content": "Inspect the scene."},
        headers={"Authorization": f"Bearer {first_player_token}"},
    )
    before_second_action = call(
        "beat-hold-after-one-action",
        "GET",
        f"/v1/sessions/{session_id}/lobby",
    )
    if before_second_action.get("current_beat_id") != "pour":
        fail(
            "beat-hold-after-one-action",
            f"expected pour, got {before_second_action.get('current_beat_id')!r}",
        )
    call(
        "player-action-2",
        "POST",
        f"/v1/sessions/{session_id}/characters/{second_character_id}/input",
        body={"kind": "action", "content": "Check the glasses."},
        headers={"Authorization": f"Bearer {second_player_token}"},
    )
    after_actions = call(
        "beat-transition-pour-to-scene",
        "GET",
        f"/v1/sessions/{session_id}/lobby",
    )
    if after_actions.get("current_beat_id") != "scene":
        fail(
            "beat-transition-pour-to-scene",
            f"expected scene, got {after_actions.get('current_beat_id')!r}",
        )
    print("SMOKE PASS")


if __name__ == "__main__":
    main()
