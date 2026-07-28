import socket
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from scripts import rehearsal

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_rehearsal_scripts_target_the_couch_race_arc() -> None:
    rehearsal = (REPO_ROOT / "scripts" / "rehearsal.py").read_text(encoding="utf-8")
    smoke = (REPO_ROOT / "scripts" / "rehearsal_smoke.py").read_text(encoding="utf-8")

    assert 'DEFAULT_ARC_ID = "nightcap-couch-race-v1"' in rehearsal
    assert 'DEFAULT_ARC_ID = "nightcap-couch-race-v1"' in smoke


def test_rehearsal_scripts_require_firebase_token_signing_configuration() -> None:
    rehearsal = (REPO_ROOT / "scripts" / "rehearsal.py").read_text(encoding="utf-8")
    smoke = (REPO_ROOT / "scripts" / "rehearsal_smoke.py").read_text(encoding="utf-8")

    for key in (
        "FIREBASE_PROJECT_ID",
        "FIREBASE_TOKEN_SIGNING_SERVICE_ACCOUNT",
        "FIREBASE_WEB_API_KEY",
    ):
        assert f'"{key}"' in rehearsal
        assert f'"{key}"' in smoke


def test_repo_make_wrapper_exposes_rehearsal_start() -> None:
    make_cmd = (REPO_ROOT / "make.cmd").read_text(encoding="utf-8")

    assert 'if /I "%~1"=="rehearsal-start" goto rehearsal-start' in make_cmd
    assert ":rehearsal-start" in make_cmd
    assert "scripts\\rehearsal_start.py" in make_cmd


def test_rehearsal_display_url_carries_host_control_in_fragment() -> None:
    rehearsal = (REPO_ROOT / "scripts" / "rehearsal.py").read_text(encoding="utf-8")

    assert "build_display_url" in rehearsal
    assert '"host_token"' in rehearsal
    assert "host_fragment = urllib.parse.urlencode" in rehearsal
    assert "DISPLAY URL" in rehearsal


def test_rehearsal_smoke_covers_authenticated_player_actions_and_beat() -> None:
    smoke = (REPO_ROOT / "scripts" / "rehearsal_smoke.py").read_text(encoding="utf-8")

    assert '"player-token-exchange-1"' in smoke
    assert '"player-action-1"' in smoke
    assert '"beat-transition-pour-to-scene"' in smoke
    assert '("last_call", "truth"' in smoke
    assert '"is_terminal"' in smoke


def test_rehearsal_rejects_an_occupied_service_port(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]

        with pytest.raises(SystemExit):
            rehearsal.ensure_port_available("API", port)

    error = capsys.readouterr().err
    assert f"port {port} is already in use" in error


def test_rehearsal_readiness_rejects_an_exited_child(
    capsys: pytest.CaptureFixture[str],
) -> None:
    class ExitedProcess:
        returncode = 1

        @staticmethod
        def poll() -> int:
            return 1

    with pytest.raises(SystemExit):
        rehearsal.wait_http(
            "API",
            "http://127.0.0.1:8000/health",
            1,
            "read the API output",
            process=ExitedProcess(),  # type: ignore[arg-type]
        )

    error = capsys.readouterr().err
    assert "exited before becoming ready (code 1)" in error


def test_rehearsal_uses_one_ipv4_loopback_endpoint_for_local_services() -> None:
    rehearsal_source = (REPO_ROOT / "scripts" / "rehearsal.py").read_text(
        encoding="utf-8"
    )

    assert '"--host", "127.0.0.1"' in rehearsal_source
    assert 'f"http://127.0.0.1:{WEB_PORT}"' in rehearsal_source


def test_display_url_carries_public_tunnel_origin_for_phone_join_qr() -> None:
    display_url = rehearsal.build_display_url(
        session_id="session-123",
        host_token="host-token",
        tunnel_url="https://example.trycloudflare.com",
    )
    parsed = urlsplit(display_url)

    assert parse_qs(parsed.query)["join_base_url"] == [
        "https://example.trycloudflare.com"
    ]
    assert parsed.fragment == "host_token=host-token"

    display_source = (
        REPO_ROOT / "dashboard" / "src" / "screens" / "DisplayScreen.tsx"
    ).read_text(encoding="utf-8")
    assert "join_base_url" in display_source


def test_rehearsal_allows_for_windows_api_cold_start() -> None:
    assert rehearsal.API_STARTUP_TIMEOUT_S >= 120


def test_rehearsal_allows_for_remote_session_token_signing() -> None:
    assert rehearsal.SESSION_BOOTSTRAP_TIMEOUT_S >= 60


def test_rehearsal_reports_http_timeouts_without_a_traceback(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def raise_timeout(*args: object, **kwargs: object) -> None:
        raise TimeoutError

    monkeypatch.setattr(rehearsal.urllib.request, "urlopen", raise_timeout)

    with pytest.raises(SystemExit):
        rehearsal.http_json("Session bootstrap", "POST", "http://127.0.0.1:8000")

    error = capsys.readouterr().err
    assert "request timed out" in error


def test_rehearsal_entrypoint_always_tears_down_children() -> None:
    rehearsal_source = (REPO_ROOT / "scripts" / "rehearsal.py").read_text(
        encoding="utf-8"
    )

    assert "finally:\n        teardown()" in rehearsal_source
