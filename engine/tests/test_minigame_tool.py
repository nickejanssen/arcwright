import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

import pytest

from engine.mini_games.authoring import LocalAuthoringWorkspace, ReadinessState

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL = (
    REPO_ROOT
    / "docs"
    / "skills"
    / "arcwright-minigame"
    / "scripts"
    / "minigame_tool.py"
)
SOURCE = Path(__file__).parent / "fixtures" / "browser_minigames" / "tmst-canary"
DESTINATION = "nightcap-couch-race-v1"

TOOL_SPEC = importlib.util.spec_from_file_location("arcwright_minigame_tool", TOOL)
assert TOOL_SPEC is not None and TOOL_SPEC.loader is not None
MINIGAME_TOOL = importlib.util.module_from_spec(TOOL_SPEC)
TOOL_SPEC.loader.exec_module(MINIGAME_TOOL)


@dataclass(frozen=True)
class ToolResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def json(self) -> dict:
        return json.loads(self.stdout)


@pytest.fixture
def run_tool(capsys: pytest.CaptureFixture[str]):
    def run(*args: str) -> ToolResult:
        try:
            returncode = MINIGAME_TOOL.main([*map(str, args)])
        except SystemExit as exc:
            returncode = int(exc.code)
        captured = capsys.readouterr()
        return ToolResult(
            returncode=returncode,
            stdout=captured.out,
            stderr=captured.err,
        )

    return run


def test_onboard_browser_defaults_to_managed_destination_first(run_tool, tmp_path):
    result = run_tool(
        "onboard-browser",
        SOURCE,
        "--destination",
        DESTINATION,
        "--workspace",
        tmp_path / "workspace",
        "--json",
    )

    assert result.returncode == 0
    assert result.json["hosting_preference"] == "managed"
    assert result.json["recommended_path"] == "destination_first"
    assert result.json["state_label"] == "Imported"
    assert result.json["state_explanation"]
    assert result.json["blockers"]
    assert result.json["next_action"]
    assert result.json["permission_prompt"]
    assert len(result.json["adaptation_alternatives"]) == 3


def test_generation_requires_explicit_permission(run_tool, tmp_path):
    result = run_tool(
        "onboard-browser",
        SOURCE,
        "--destination",
        DESTINATION,
        "--workspace",
        tmp_path / "workspace",
        "--non-interactive",
    )

    assert result.returncode == 2
    assert "generation permission required" in result.stderr
    assert "State: Imported" in result.stdout


def test_non_interactive_accepts_versioned_answers_and_persists_confirmations(
    run_tool,
    tmp_path,
):
    workspace = tmp_path / "workspace"
    answers = tmp_path / "answers.json"
    answers.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "confirmations": {
                    "story_affordance": "A social opener that reveals player preferences.",
                    "participation_model": "All players answer one prompt privately.",
                    "result_meaning": "Answers are preview-only social context.",
                    "placement_authority": "The authored destination policy decides.",
                },
                "generation_permission": {
                    "approved_categories": ["code", "configuration"],
                    "denied_asset_refs": ["source/index.html"],
                    "remember_for_project": False,
                    "approved_by": "task-4-test",
                },
            }
        ),
        encoding="utf-8",
    )

    started = run_tool(
        "onboard-browser",
        SOURCE,
        "--destination",
        DESTINATION,
        "--workspace",
        workspace,
        "--non-interactive",
        "--answers",
        answers,
        "--json",
    )
    resumed = run_tool(
        "resume",
        started.json["session_id"],
        "--workspace",
        workspace,
        "--json",
    )

    assert started.returncode == 0
    assert started.json["state_label"] == "Imported"
    assert started.json["pending_questions"] == []
    assert started.json["generation_permission"]["approved_categories"] == [
        "code",
        "configuration",
    ]
    assert resumed.returncode == 0
    assert resumed.json == started.json


def test_non_interactive_rejects_missing_high_impact_confirmations(
    run_tool,
    tmp_path,
):
    answers = tmp_path / "answers.json"
    answers.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "confirmations": {"story_affordance": "A social opener."},
                "generation_permission": {
                    "approved_categories": [],
                    "approved_by": "task-4-test",
                },
            }
        ),
        encoding="utf-8",
    )

    result = run_tool(
        "onboard-browser",
        SOURCE,
        "--destination",
        DESTINATION,
        "--workspace",
        tmp_path / "workspace",
        "--non-interactive",
        "--answers",
        answers,
    )

    assert result.returncode == 2
    assert "high-impact confirmations required" in result.stderr


def test_status_reports_saved_session_without_advancing_it(run_tool, tmp_path):
    workspace = tmp_path / "workspace"
    started = run_tool(
        "onboard-browser",
        SOURCE,
        "--destination",
        DESTINATION,
        "--workspace",
        workspace,
        "--json",
    )

    status = run_tool(
        "status",
        started.json["session_id"],
        "--workspace",
        workspace,
        "--json",
    )

    assert status.returncode == 0
    assert status.json == started.json


@pytest.mark.parametrize(
    ("state", "label"),
    [
        (ReadinessState.imported, "Imported"),
        (ReadinessState.reusable, "Reusable"),
        (ReadinessState.playtest_ready, "Playtest-ready"),
        (ReadinessState.production_ready, "Production-ready"),
    ],
)
def test_progressive_states_use_plain_labels(run_tool, tmp_path, state, label):
    workspace_root = tmp_path / "workspace"
    started = run_tool(
        "onboard-browser",
        SOURCE,
        "--destination",
        DESTINATION,
        "--workspace",
        workspace_root,
        "--json",
    )
    session = LocalAuthoringWorkspace().load(
        UUID(started.json["session_id"]),
        workspace_root,
    )

    payload = MINIGAME_TOOL._session_payload(
        session.model_copy(update={"state": state})
    )

    assert payload["state_label"] == label


def test_resume_asks_and_saves_one_focused_question_at_a_time(
    run_tool,
    tmp_path,
    monkeypatch,
):
    workspace = tmp_path / "workspace"
    started = run_tool(
        "onboard-browser",
        SOURCE,
        "--destination",
        DESTINATION,
        "--workspace",
        workspace,
        "--json",
    )
    prompts: list[str] = []

    def answer_once(prompt: str) -> str:
        prompts.append(prompt)
        if len(prompts) == 1:
            return "A social opener."
        raise EOFError

    monkeypatch.setattr("builtins.input", answer_once)
    resumed = run_tool(
        "resume",
        started.json["session_id"],
        "--workspace",
        workspace,
    )
    status = run_tool(
        "status",
        started.json["session_id"],
        "--workspace",
        workspace,
        "--json",
    )

    assert resumed.returncode == 0
    assert prompts == [
        "What story purpose should this mini-game serve?\n> ",
        "How should players participate?\n> ",
    ]
    assert status.json["revision"] == started.json["revision"] + 1
    assert status.json["pending_questions"][0]["key"] == "participation_model"


def test_help_keeps_legacy_commands_and_lists_guided_commands(run_tool):
    result = run_tool("--help")

    assert result.returncode == 0
    for command in ("scaffold", "validate", "onboard-browser", "resume", "status"):
        assert command in result.stdout
