"""Start the current rehearsal session.

Run this after players have joined the lobby (the display shows
"Ready to start"). Reads the session saved by `make rehearsal`, exchanges the
host custom token for a Firebase ID token, and calls POST /start so the arc
begins. The dashboard has no host-start control, so this is the founder's
start path during a local rehearsal.
"""

from __future__ import annotations

import json
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
STATE_FILE = REPO_ROOT / ".rehearsal" / "current-session.json"
BASE = "http://localhost:8000"


def fail(step: str, message: str) -> None:
    print(f"[FAIL] {step}: {message}", file=sys.stderr)
    raise SystemExit(1)


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
    if not env.get("FIREBASE_WEB_API_KEY"):
        fail(
            ".env",
            "FIREBASE_WEB_API_KEY must be set to start a session (host token exchange)",
        )
    return env


def exchange_host_token(custom_token: str, web_api_key: str) -> str:
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
        fail("host-token-exchange", f"HTTP {exc.code}\n{detail}")
    except urllib.error.URLError as exc:
        fail("host-token-exchange", str(exc.reason))

    token = data.get("idToken")
    if not token:
        fail("host-token-exchange", "response did not include idToken")
    return str(token)


def call_start(session_id: str, id_token: str) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{BASE}/v1/sessions/{session_id}/start",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {id_token}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        fail("start-session", f"HTTP {exc.code}\n{detail}")
    except urllib.error.URLError as exc:
        fail("start-session", f"{exc.reason} — is `make rehearsal` running?")
    return {}


def main() -> None:
    if not STATE_FILE.exists():
        fail(
            "session-state",
            f"{STATE_FILE} not found — run `make rehearsal` first",
        )
    details = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    session_id = str(details["session_id"])
    host_token = str(details["host_token"])

    env = read_env()
    id_token = exchange_host_token(host_token, env["FIREBASE_WEB_API_KEY"])
    started = call_start(session_id, id_token)

    status = str(started.get("status"))
    if status != "active":
        fail("start-session", f"expected status 'active', got {status!r}")
    print(f"[ok] session {session_id} is now active. The arc has begun.")


if __name__ == "__main__":
    main()
