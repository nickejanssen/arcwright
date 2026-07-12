"""One-command local rehearsal stack.

Boots: Postgres (docker compose) -> Alembic -> API (uvicorn) ->
dashboard (Vite dev server) -> cloudflared quick tunnel.
Creates a rehearsal session once the API is up and prints the display URL
plus the player join URL for phones.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
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
ENV_EXAMPLE = REPO_ROOT / ".env.example"
STATE_DIR = REPO_ROOT / ".rehearsal"
STATE_FILE = STATE_DIR / "current-session.json"
API_PORT = 8000
WEB_PORT = 5173
DEFAULT_ARC_ID = "nightcap-v1"
REQUIRED_KEYS = (
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "ARCWRIGHT_API_KEY",
    "ANTHROPIC_API_KEY",
    "GROQ_API_KEY",
)
OPTIONAL_KEYS = ("FIREBASE_WEB_API_KEY",)
TUNNEL_URL_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")

children: list[subprocess.Popen[str]] = []
tunnel_process: subprocess.Popen[str] | None = None


def fail(layer: str, problem: str, fix: str) -> None:
    print(f"\n[FAIL] {layer}: {problem}\n  Fix: {fix}", file=sys.stderr)
    teardown()
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

    fail(
        "Python",
        f"found Python {sys.version.split()[0]}, need 3.11+",
        "create a repo-local .venv or install Python 3.11, then re-run make rehearsal",
    )


def teardown() -> None:
    for proc in reversed(children):
        if proc.poll() is None:
            proc.terminate()
    deadline = time.monotonic() + 10
    for proc in reversed(children):
        if proc.poll() is not None:
            continue
        try:
            proc.wait(timeout=max(0.1, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            proc.kill()


def read_env() -> dict[str, str]:
    if not ENV_FILE.exists():
        if SHARED_ENV_FILE.exists():
            shutil.copy(SHARED_ENV_FILE, ENV_FILE)
            print(f"[setup] Copied {SHARED_ENV_FILE} into {ENV_FILE}.")
        if ENV_EXAMPLE.exists():
            if not ENV_FILE.exists():
                shutil.copy(ENV_EXAMPLE, ENV_FILE)
                print(f"[setup] Created {ENV_FILE.name} from {ENV_EXAMPLE.name}.")
        if not ENV_FILE.exists():
            fail(
                ".env",
                "no .env or .env.example found",
                "create .env at the repo root (see rehearsal quickstart)",
            )

    env: dict[str, str] = {}
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()

    missing = [key for key in REQUIRED_KEYS if not env.get(key)]
    if missing:
        fail(
            ".env",
            f"blank required keys: {', '.join(missing)}",
            "open .env and fill the missing values, then re-run make rehearsal",
        )
    return env


def http_json(
    step: str,
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    timeout: int = 15,
) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
            return json.loads(payload or b"{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        fail(step, f"HTTP {exc.code}: {detail or exc.reason}", "see the response above")
    except urllib.error.URLError as exc:
        fail(step, str(exc.reason), "check the service status above and try again")
    return {}


def wait_http(name: str, url: str, timeout_s: int, fix: str) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if response.status < 500:
                    print(f"[ok] {name} is up ({url})")
                    return
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(1.5)
    fail(name, f"not reachable at {url} after {timeout_s}s", fix)


def run_step(name: str, cmd: list[str], fix: str, env: dict[str, str]) -> None:
    print(f"[step] {name}: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=REPO_ROOT, env={**os.environ, **env}, check=False)
    if result.returncode != 0:
        fail(name, f"exit code {result.returncode}", fix)


def spawn(
    name: str,
    cmd: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    capture_output: bool,
    fix: str,
) -> subprocess.Popen[str]:
    print(f"[start] {name}: {' '.join(cmd)}")
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env={**os.environ, **env},
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.STDOUT if capture_output else None,
            text=True,
        )
    except FileNotFoundError:
        fail(name, f"command not found: {cmd[0]}", fix)
    children.append(proc)
    return proc


def create_session(env: dict[str, str]) -> dict[str, str]:
    base = f"http://localhost:{API_PORT}"
    session = http_json(
        "Session bootstrap",
        "POST",
        f"{base}/v1/sessions",
        headers={"X-Api-Key": env["ARCWRIGHT_API_KEY"]},
        body={"arc_id": DEFAULT_ARC_ID},
    )
    session_id = str(session["session_id"])
    lobby = http_json(
        "Lobby lookup",
        "GET",
        f"{base}/v1/sessions/{session_id}/lobby",
    )
    join_code = str(lobby["join_code"])

    details = {
        "session_id": session_id,
        "join_code": join_code,
        "host_token": str(session["host_token"]),
        "host_join_token": str(session["host_join_token"]),
    }
    STATE_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(details, indent=2), encoding="utf-8")
    print(f"[ok] Session ready ({session_id}, join code {join_code})")
    return details


def exchange_host_token(custom_token: str, web_api_key: str) -> str | None:
    if not web_api_key:
        return None

    payload = http_json(
        "Host token exchange",
        "POST",
        (
            "https://identitytoolkit.googleapis.com/v1/"
            f"accounts:signInWithCustomToken?key={web_api_key}"
        ),
        body={"token": custom_token, "returnSecureToken": True},
        timeout=20,
    )
    token = payload.get("idToken")
    return str(token) if token else None


def wait_for_tunnel_url(proc: subprocess.Popen[str]) -> str:
    assert proc.stdout is not None
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.5)
            continue
        match = TUNNEL_URL_RE.search(line)
        if match:
            return match.group(0)
    fail(
        "Tunnel",
        "no trycloudflare URL after 45s",
        "check internet; retry make rehearsal",
    )
    return ""


def main() -> None:
    ensure_python()
    env = read_env()

    if shutil.which("docker") is None:
        fail(
            "Docker",
            "docker CLI not found",
            "install/start Docker Desktop, then re-run make rehearsal",
        )
    if shutil.which("cloudflared") is None:
        fail(
            "cloudflared",
            "cloudflared not found on PATH",
            "install cloudflared, then reopen the terminal",
        )

    python_bin = str(Path(sys.executable))
    npm_bin = shutil.which("npm") or shutil.which("npm.cmd")
    if npm_bin is None:
        fail(
            "Dashboard",
            "npm not found",
            "install Node.js LTS and re-run make rehearsal",
        )

    run_step(
        "Postgres",
        ["docker", "compose", "up", "-d", "--wait"],
        "open Docker Desktop; then re-run make rehearsal",
        env,
    )
    run_step(
        "Migrations",
        [python_bin, "-m", "alembic", "upgrade", "head"],
        "check POSTGRES_* values in .env match docker-compose.yml",
        env,
    )

    spawn(
        "API",
        [
            python_bin,
            "-m",
            "uvicorn",
            "api.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(API_PORT),
            "--env-file",
            ".env",
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=False,
        fix="check the API log above for the first traceback",
    )
    wait_http(
        "API",
        f"http://localhost:{API_PORT}/health",
        60,
        "read the uvicorn output above; usually a bad .env value",
    )

    session = create_session(env)

    spawn(
        "Dashboard",
        [npm_bin, "run", "dev"],
        cwd=REPO_ROOT / "dashboard",
        env=env,
        capture_output=False,
        fix="run: cd dashboard && npm install",
    )
    wait_http(
        "Dashboard",
        f"http://localhost:{WEB_PORT}",
        90,
        "run: cd dashboard && npm install, then re-run make rehearsal",
    )

    global tunnel_process
    tunnel_process = spawn(
        "Tunnel",
        ["cloudflared", "tunnel", "--url", f"http://localhost:{WEB_PORT}"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        fix="check your internet connection",
    )
    tunnel_url = wait_for_tunnel_url(tunnel_process)

    display_url = f"http://localhost:{WEB_PORT}/display/{session['session_id']}"
    player_join_url = f"{tunnel_url}/join?code={session['join_code']}"

    print("\n" + "=" * 68)
    print("READY - Nightcap rehearsal stack is up")
    print(f"DISPLAY URL (this machine): {display_url}")
    print(f"PLAYER JOIN URL (phones):  {player_join_url}")
    print(f"JOIN CODE:                 {session['join_code']}")
    if env.get("FIREBASE_WEB_API_KEY"):
        print(
            "Host start token exchange is available for rehearsal-smoke and manual lifecycle calls."
        )
    else:
        print(
            "FIREBASE_WEB_API_KEY is blank; host lifecycle smoke/start calls will fail until it is set."
        )
    print(f"Session details saved to:   {STATE_FILE}")
    print(
        "Leave this window open. Ctrl+C stops the app stack; make rehearsal-stop stops Postgres."
    )
    print("=" * 68 + "\n")

    try:
        while True:
            for proc in children:
                if proc.poll() is not None:
                    fail(
                        "Supervisor",
                        f"a child process exited (code {proc.returncode})",
                        "scroll up for its last log lines; re-run make rehearsal",
                    )
            time.sleep(2)
    except KeyboardInterrupt:
        print(
            "\n[stop] shutting down app processes (database stays up; use make rehearsal-stop to stop it)"
        )
        teardown()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    main()
