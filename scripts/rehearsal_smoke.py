"""Smoke test against the live local rehearsal stack."""

from __future__ import annotations

import json
import os
import sys
import time
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
DEFAULT_ARC_ID = "nightcap-v1"


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
    for key in ("ARCWRIGHT_API_KEY", "FIREBASE_WEB_API_KEY"):
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
        fail(step, f"{exc.reason} — is `make rehearsal` running?")
    return {}


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
    print("[ok] host-token-exchange -> 200")
    return str(token)


def wait_for_event(session_id: str, timeout_s: int = 30) -> dict[str, Any]:
    request = urllib.request.Request(f"{BASE}/v1/sessions/{session_id}/events?since=0")
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            deadline = time.monotonic() + timeout_s
            while time.monotonic() < deadline:
                line = response.readline().decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload:
                    event = json.loads(payload)
                    print("[ok] read-events -> 200")
                    return event
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        fail("read-events", f"HTTP {exc.code}\n{detail}")
    except urllib.error.URLError as exc:
        fail("read-events", str(exc.reason))
    fail("read-events", f"timed out waiting for first event after {timeout_s}s")
    return {}


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

    call(
        "player-join-1",
        "POST",
        "/v1/lobby-join",
        body={"name": "Smoke One", "join_code": join_code},
    )
    call(
        "player-join-2",
        "POST",
        "/v1/lobby-join",
        body={"name": "Smoke Two", "join_code": join_code},
    )

    host_id_token = exchange_host_token(
        str(session["host_token"]), env["FIREBASE_WEB_API_KEY"]
    )
    call(
        "start-session",
        "POST",
        f"/v1/sessions/{session_id}/start",
        headers={"Authorization": f"Bearer {host_id_token}"},
    )

    event = wait_for_event(session_id)
    print(f"[ok] first-event-type -> {event.get('event_type', 'unknown')}")
    print("SMOKE PASS")


if __name__ == "__main__":
    main()
