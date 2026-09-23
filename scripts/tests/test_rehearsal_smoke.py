"""Contract tests for the rehearsal smoke test.

`scripts/rehearsal_smoke.py` is the gate that says the local stack can run a
whole arc. These tests stand a fake stack behind it and check that it passes on
a correct one and fails on each way a real stack breaks: a start that never goes
active, a beat gate that opens on one action instead of two, a beat that stalls,
and a final beat that is not terminal.
"""

import urllib.error

import pytest

from scripts import rehearsal_smoke

BEATS = ["pour", "scene", "grill", "twist", "last_call", "truth"]


@pytest.fixture(autouse=True)
def _isolate_repo_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(rehearsal_smoke, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setattr(
        rehearsal_smoke, "SHARED_ENV_FILE", tmp_path / "shared" / ".env"
    )


SMOKE_KEYS = (
    "ARCWRIGHT_API_KEY",
    "FIREBASE_PROJECT_ID",
    "FIREBASE_TOKEN_SIGNING_SERVICE_ACCOUNT",
    "FIREBASE_WEB_API_KEY",
)


def env_text(**overrides):
    values = {key: "set" for key in SMOKE_KEYS}
    values.update(overrides)
    return "\n".join(f"{key}={value}" for key, value in values.items())


class TestReadEnv:
    @pytest.mark.parametrize("missing", SMOKE_KEYS)
    def test_each_required_key_is_actually_required(self, missing, capsys):
        rehearsal_smoke.ENV_FILE.write_text(env_text(**{missing: ""}), encoding="utf-8")
        with pytest.raises(SystemExit) as exc:
            rehearsal_smoke.read_env()
        assert exc.value.code == 1
        assert missing in capsys.readouterr().err

    def test_complete_env_is_accepted(self):
        rehearsal_smoke.ENV_FILE.write_text(env_text(), encoding="utf-8")
        assert rehearsal_smoke.read_env()["ARCWRIGHT_API_KEY"] == "set"

    def test_missing_env_file_fails(self, capsys):
        with pytest.raises(SystemExit):
            rehearsal_smoke.read_env()
        assert "missing .env" in capsys.readouterr().err


class FakeStack:
    """A minimal in-memory stand-in for the local rehearsal API.

    `actions_to_advance` and `terminal_beat` are the knobs the failure tests
    turn to reproduce a genuinely broken stack.
    """

    def __init__(
        self,
        *,
        actions_to_advance=2,
        start_status="active",
        terminal_beat="truth",
        stall_at=None,
    ):
        self.actions_to_advance = actions_to_advance
        self.start_status = start_status
        self.terminal_beat = terminal_beat
        self.stall_at = stall_at
        self.beat_index = 0
        self.pending_actions = 0
        self.steps = []

    @property
    def beat(self):
        return BEATS[self.beat_index]

    def __call__(self, step, method, path, *, body=None, headers=None, timeout=15):
        self.steps.append(step)
        if path == "/health":
            return {"status": "ok"}
        if path == "/v1/sessions" and method == "POST":
            return {"session_id": "sess-1", "host_token": "host-custom-token"}
        if path == "/v1/lobby-join":
            index = sum(1 for s in self.steps if s.startswith("player-join"))
            return {
                "player_token": f"player-custom-{index}",
                "character_id": f"char-{index}",
            }
        if path.endswith("/start"):
            return {"status": self.start_status}
        if path.endswith("/input"):
            self._record_action()
            return {"accepted": True}
        if path.endswith("/lobby"):
            return {
                "join_code": "ABCD",
                "current_beat_id": self.beat,
                "is_terminal": self.beat == self.terminal_beat,
            }
        raise AssertionError(f"unexpected call: {method} {path}")

    def _record_action(self):
        if self.beat == self.stall_at:
            return
        self.pending_actions += 1
        if self.pending_actions >= self.actions_to_advance:
            self.pending_actions = 0
            if self.beat_index + 1 < len(BEATS):
                self.beat_index += 1


def install_stack(monkeypatch, stack):
    rehearsal_smoke.ENV_FILE.write_text(env_text(), encoding="utf-8")
    monkeypatch.setattr(rehearsal_smoke, "ensure_python", lambda: None)
    monkeypatch.setattr(rehearsal_smoke, "call", stack)
    monkeypatch.setattr(
        rehearsal_smoke,
        "exchange_firebase_token",
        lambda step, custom_token, web_api_key: f"id-for-{custom_token}",
    )
    return stack


class TestMainAgainstAHealthyStack:
    def test_walks_every_beat_and_reports_smoke_pass(self, monkeypatch, capsys):
        stack = install_stack(monkeypatch, FakeStack())
        rehearsal_smoke.main()
        out = capsys.readouterr().out
        assert "SMOKE PASS" in out
        assert stack.beat == "truth"

    def test_checks_every_beat_transition_in_the_arc(self, monkeypatch):
        stack = install_stack(monkeypatch, FakeStack())
        rehearsal_smoke.main()
        assert "beat-transition-pour-to-scene" in stack.steps
        for source, target in zip(BEATS[1:], BEATS[2:]):
            assert f"beat-transition-{source}-to-{target}" in stack.steps

    def test_sends_each_player_its_own_exchanged_token(self, monkeypatch):
        """A smoke test that reused one player's token would pass while the
        two-player beat gate was broken, because both actions would be one
        player's."""
        stack = install_stack(monkeypatch, FakeStack())
        seen = []

        def recording_call(step, method, path, *, body=None, headers=None, timeout=15):
            if path.endswith("/input"):
                seen.append((path, (headers or {}).get("Authorization")))
            return stack(
                step, method, path, body=body, headers=headers, timeout=timeout
            )

        monkeypatch.setattr(rehearsal_smoke, "call", recording_call)
        rehearsal_smoke.main()
        characters = {path.split("/characters/")[1].split("/")[0] for path, _ in seen}
        tokens = {auth for _, auth in seen}
        assert characters == {"char-1", "char-2"}
        assert tokens == {
            "Bearer id-for-player-custom-1",
            "Bearer id-for-player-custom-2",
        }


class TestMainAgainstABrokenStack:
    def test_catches_a_start_that_never_goes_active(self, monkeypatch, capsys):
        install_stack(monkeypatch, FakeStack(start_status="lobby"))
        with pytest.raises(SystemExit) as exc:
            rehearsal_smoke.main()
        assert exc.value.code == 1
        assert "expected status 'active', got 'lobby'" in capsys.readouterr().err

    def test_catches_a_beat_gate_that_opens_on_one_action(self, monkeypatch, capsys):
        """The regression this script exists for: the pour beat must hold until
        both players have acted. A gate that advances on one action is a
        determinism bug in arc execution, and the smoke test must go red."""
        install_stack(monkeypatch, FakeStack(actions_to_advance=1))
        with pytest.raises(SystemExit) as exc:
            rehearsal_smoke.main()
        assert exc.value.code == 1
        err = capsys.readouterr().err
        assert "beat-hold-after-one-action" in err
        assert "expected pour, got 'scene'" in err

    def test_catches_a_beat_that_never_advances(self, monkeypatch, capsys):
        install_stack(monkeypatch, FakeStack(stall_at="grill"))
        with pytest.raises(SystemExit) as exc:
            rehearsal_smoke.main()
        assert exc.value.code == 1
        assert "beat-transition-grill-to-twist" in capsys.readouterr().err

    def test_catches_a_final_beat_that_is_not_terminal(self, monkeypatch, capsys):
        install_stack(monkeypatch, FakeStack(terminal_beat="never"))
        with pytest.raises(SystemExit) as exc:
            rehearsal_smoke.main()
        assert exc.value.code == 1
        assert "expected the truth beat to be terminal" in capsys.readouterr().err


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class TestExchangeFirebaseToken:
    def test_a_response_without_an_id_token_fails(self, monkeypatch, capsys):
        monkeypatch.setattr(
            rehearsal_smoke.urllib.request,
            "urlopen",
            lambda request, timeout=None: FakeResponse(b'{"error": "bad token"}'),
        )
        with pytest.raises(SystemExit) as exc:
            rehearsal_smoke.exchange_firebase_token("step", "custom", "key")
        assert exc.value.code == 1
        assert "did not include idToken" in capsys.readouterr().err

    def test_returns_the_id_token(self, monkeypatch):
        monkeypatch.setattr(
            rehearsal_smoke.urllib.request,
            "urlopen",
            lambda request, timeout=None: FakeResponse(b'{"idToken": "abc"}'),
        )
        assert rehearsal_smoke.exchange_firebase_token("step", "custom", "key") == "abc"


class TestCall:
    def test_a_down_api_points_at_make_rehearsal(self, monkeypatch, capsys):
        def refuse(request, timeout=None):
            raise urllib.error.URLError("connection refused")

        monkeypatch.setattr(rehearsal_smoke.urllib.request, "urlopen", refuse)
        with pytest.raises(SystemExit):
            rehearsal_smoke.call("api-health", "GET", "/health")
        assert "is `make rehearsal` running?" in capsys.readouterr().err
