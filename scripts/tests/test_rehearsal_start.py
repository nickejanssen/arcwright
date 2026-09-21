"""Contract tests for the CLI fallback that starts a rehearsal session.

The script's job is narrow: read the saved session, exchange the host token,
call POST /start, and refuse to report success unless the session actually
reached `active`. Every test below drives that contract with the network
stubbed out.
"""

import json
import urllib.error

import pytest

from scripts import rehearsal_start


@pytest.fixture(autouse=True)
def _isolate_repo_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(rehearsal_start, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setattr(
        rehearsal_start, "SHARED_ENV_FILE", tmp_path / "shared" / ".env"
    )
    monkeypatch.setattr(
        rehearsal_start, "STATE_FILE", tmp_path / ".rehearsal" / "current-session.json"
    )


def write_state(path, **overrides):
    details = {"session_id": "sess-1", "host_token": "custom-token"}
    details.update(overrides)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(details), encoding="utf-8")


class TestReadEnv:
    def test_missing_env_file_fails(self, capsys):
        with pytest.raises(SystemExit) as exc:
            rehearsal_start.read_env()
        assert exc.value.code == 1
        assert "missing .env" in capsys.readouterr().err

    def test_blank_web_api_key_fails_because_the_exchange_cannot_run(self, capsys):
        rehearsal_start.ENV_FILE.write_text(
            "FIREBASE_WEB_API_KEY=\nOTHER=value\n", encoding="utf-8"
        )
        with pytest.raises(SystemExit):
            rehearsal_start.read_env()
        assert "FIREBASE_WEB_API_KEY" in capsys.readouterr().err

    def test_falls_back_to_the_shared_env_outside_a_worktree(self):
        rehearsal_start.SHARED_ENV_FILE.parent.mkdir(parents=True)
        rehearsal_start.SHARED_ENV_FILE.write_text(
            "FIREBASE_WEB_API_KEY=shared-key\n", encoding="utf-8"
        )
        assert rehearsal_start.read_env()["FIREBASE_WEB_API_KEY"] == "shared-key"

    def test_skips_comments_and_blank_lines(self):
        rehearsal_start.ENV_FILE.write_text(
            "# comment\n\nnovalue\nFIREBASE_WEB_API_KEY=abc\n", encoding="utf-8"
        )
        env = rehearsal_start.read_env()
        assert env == {"FIREBASE_WEB_API_KEY": "abc"}


class FakeResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def stub_urlopen(monkeypatch, module, payload=None, error=None):
    calls = []

    def fake(request, timeout=None):
        calls.append(request)
        if error is not None:
            raise error
        return FakeResponse(payload or {})

    monkeypatch.setattr(module.urllib.request, "urlopen", fake)
    return calls


class TestExchangeHostToken:
    def test_returns_the_id_token_and_targets_the_supplied_key(self, monkeypatch):
        calls = stub_urlopen(
            monkeypatch, rehearsal_start, payload={"idToken": "id-token-value"}
        )
        token = rehearsal_start.exchange_host_token("custom", "web-key")
        assert token == "id-token-value"
        assert "key=web-key" in calls[0].full_url
        assert json.loads(calls[0].data)["token"] == "custom"

    def test_a_response_without_an_id_token_is_a_failure_not_a_none_token(
        self, monkeypatch, capsys
    ):
        """Returning None here would push an `Authorization: Bearer None` header
        at the API and surface as a confusing 401 instead of this message."""
        stub_urlopen(monkeypatch, rehearsal_start, payload={"error": "nope"})
        with pytest.raises(SystemExit) as exc:
            rehearsal_start.exchange_host_token("custom", "web-key")
        assert exc.value.code == 1
        assert "did not include idToken" in capsys.readouterr().err

    def test_unreachable_identity_service_fails_with_the_reason(
        self, monkeypatch, capsys
    ):
        stub_urlopen(
            monkeypatch,
            rehearsal_start,
            error=urllib.error.URLError("name resolution failed"),
        )
        with pytest.raises(SystemExit):
            rehearsal_start.exchange_host_token("custom", "web-key")
        assert "name resolution failed" in capsys.readouterr().err


class TestCallStart:
    def test_posts_to_the_session_start_route_with_the_bearer_token(self, monkeypatch):
        calls = stub_urlopen(monkeypatch, rehearsal_start, payload={"status": "active"})
        result = rehearsal_start.call_start("sess-9", "id-token")
        assert result == {"status": "active"}
        request = calls[0]
        assert request.full_url.endswith("/v1/sessions/sess-9/start")
        assert request.get_method() == "POST"
        assert request.get_header("Authorization") == "Bearer id-token"

    def test_a_down_api_points_at_make_rehearsal(self, monkeypatch, capsys):
        stub_urlopen(
            monkeypatch,
            rehearsal_start,
            error=urllib.error.URLError("connection refused"),
        )
        with pytest.raises(SystemExit):
            rehearsal_start.call_start("sess-9", "id-token")
        assert "is `make rehearsal` running?" in capsys.readouterr().err


class TestMain:
    def test_refuses_to_report_success_when_the_session_did_not_go_active(
        self, monkeypatch, capsys
    ):
        """The whole point of the script. If /start returns 200 but leaves the
        session in the lobby, the founder must not be told the arc began."""
        write_state(rehearsal_start.STATE_FILE)
        rehearsal_start.ENV_FILE.write_text(
            "FIREBASE_WEB_API_KEY=k\n", encoding="utf-8"
        )
        monkeypatch.setattr(
            rehearsal_start, "exchange_host_token", lambda *_: "id-token"
        )
        monkeypatch.setattr(
            rehearsal_start, "call_start", lambda *_: {"status": "lobby"}
        )
        with pytest.raises(SystemExit) as exc:
            rehearsal_start.main()
        captured = capsys.readouterr()
        assert exc.value.code == 1
        assert "expected status 'active', got 'lobby'" in captured.err
        assert "The arc has begun" not in captured.out

    def test_reports_success_once_the_session_is_active(self, monkeypatch, capsys):
        write_state(rehearsal_start.STATE_FILE, session_id="sess-42")
        rehearsal_start.ENV_FILE.write_text(
            "FIREBASE_WEB_API_KEY=k\n", encoding="utf-8"
        )
        monkeypatch.setattr(
            rehearsal_start, "exchange_host_token", lambda *_: "id-token"
        )
        monkeypatch.setattr(
            rehearsal_start, "call_start", lambda *_: {"status": "active"}
        )
        rehearsal_start.main()
        assert "session sess-42 is now active" in capsys.readouterr().out

    def test_passes_the_saved_host_token_to_the_exchange(self, monkeypatch):
        write_state(rehearsal_start.STATE_FILE, host_token="saved-host-token")
        rehearsal_start.ENV_FILE.write_text(
            "FIREBASE_WEB_API_KEY=web-key\n", encoding="utf-8"
        )
        seen = {}

        def record_exchange(custom_token, web_api_key):
            seen["custom_token"] = custom_token
            seen["web_api_key"] = web_api_key
            return "id-token"

        monkeypatch.setattr(rehearsal_start, "exchange_host_token", record_exchange)
        monkeypatch.setattr(
            rehearsal_start, "call_start", lambda *_: {"status": "active"}
        )
        rehearsal_start.main()
        assert seen == {"custom_token": "saved-host-token", "web_api_key": "web-key"}

    def test_missing_session_state_tells_the_founder_to_run_make_rehearsal(
        self, capsys
    ):
        with pytest.raises(SystemExit) as exc:
            rehearsal_start.main()
        assert exc.value.code == 1
        assert "run `make rehearsal` first" in capsys.readouterr().err
