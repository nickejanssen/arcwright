from __future__ import annotations

from pathlib import Path

import pytest

from engine.arc.arc_state import transition_name_for
from engine.harness.models import HarnessAction
from engine.harness.runner import HarnessRunner
from engine.scoring.resolver import accusations_locked_or_countdown_expired

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"


def _to_grill(runner: HarnessRunner) -> None:
    runner.start()
    runner.set_participants(["p1", "p2"])
    for source, target, conditions in (
        (
            "pour",
            "scene",
            {"case_resolution_complete": True, "all_players_ready": True},
        ),
        ("scene", "grill", {"evidence_wave_delivered": True}),
    ):
        runner.apply_action(
            HarnessAction(
                transition_name=transition_name_for(source, target),
                payload={"context": conditions},
            )
        )


def test_normal_grill_completion_invokes_twist_transition():
    runner = HarnessRunner(arc_path=ARC_PATH, seed=284)
    _to_grill(runner)

    entry = runner.advance_current_beat(cause="normal_completion")

    assert entry.transition_name == "advance_grill_to_twist"
    assert runner.snapshot().configuration == ["twist"]
    assert runner.transition_causes == {"grill": "normal_completion"}


def test_first_correct_accusation_invokes_grill_to_last_call_transition():
    runner = HarnessRunner(arc_path=ARC_PATH, seed=284)
    _to_grill(runner)

    entry = runner.advance_current_beat(cause="first_correct_accusation")

    assert entry.transition_name == "advance_grill_to_last_call"
    assert runner.snapshot().configuration == ["last_call"]
    assert "twist" not in runner.snapshot().configuration
    assert runner.transition_causes == {"grill": "first_correct_accusation"}


def test_orchestrator_rejects_wrong_target_for_normal_cause():
    runner = HarnessRunner(arc_path=ARC_PATH, seed=284)
    _to_grill(runner)

    with pytest.raises(ValueError, match="does not match cause"):
        runner.advance_current_beat(
            cause="normal_completion", target_beat_id="last_call"
        )

    assert runner.snapshot().configuration == ["grill"]
    assert runner.trace()[-1].transition_name == "advance_scene_to_grill"


def test_twist_exit_ready_uses_existing_last_call_edge_for_early_accusation():
    runner = HarnessRunner(arc_path=ARC_PATH, seed=284)
    _to_grill(runner)
    runner.advance_current_beat(cause="normal_completion")

    entry = runner.advance_current_beat(cause="first_correct_accusation")

    assert entry.transition_name == "advance_twist_to_last_call"
    assert runner.snapshot().configuration == ["last_call"]
    assert runner.transition_causes == {
        "grill": "normal_completion",
        "twist": "first_correct_accusation",
    }


def test_last_call_condition_becomes_true_on_natural_expiry():
    assert accusations_locked_or_countdown_expired(
        0,
        eligible_participant_ids={"p1", "p2"},
        locked_out_participant_ids=set(),
    )


def test_last_call_condition_becomes_true_when_all_active_players_locked_early():
    assert accusations_locked_or_countdown_expired(
        42,
        eligible_participant_ids={"p1", "p2"},
        locked_out_participant_ids={"p1", "p2"},
    )


def test_passive_participant_does_not_block_all_locked_condition():
    assert accusations_locked_or_countdown_expired(
        42,
        eligible_participant_ids={"p1", "p2"},
        locked_out_participant_ids={"p1", "p2"},
    )
    assert not accusations_locked_or_countdown_expired(
        42,
        eligible_participant_ids={"p1", "p2"},
        locked_out_participant_ids={"p1"},
    )
