from pathlib import Path

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

    assert "#host_token=" in rehearsal
    assert "DISPLAY URL" in rehearsal


def test_rehearsal_smoke_covers_authenticated_player_actions_and_beat() -> None:
    smoke = (REPO_ROOT / "scripts" / "rehearsal_smoke.py").read_text(encoding="utf-8")

    assert '"player-token-exchange-1"' in smoke
    assert '"player-action-1"' in smoke
    assert '"beat-transition-pour-to-scene"' in smoke
