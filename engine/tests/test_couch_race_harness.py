"""AW-281 - full 6-beat headless harness run over the Couch Race arc."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.arc.arc_state import transition_name_for
from engine.harness.models import HarnessAction
from engine.harness.runner import HarnessRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"

BEATS = ["pour", "scene", "grill", "twist", "last_call", "truth"]


def _run_full_arc(seed: int, participant_count: int) -> HarnessRunner:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=seed)
    runner.start()
    runner.set_participants([f"p{i + 1}" for i in range(participant_count)])
    for src, dst in zip(BEATS[:-1], BEATS[1:]):
        # Satisfy all exit conditions for the source beat so the guard passes.
        payload = {"context": _context_for_transition(src, dst)}
        runner.apply_action(
            HarnessAction(
                transition_name=transition_name_for(src, dst),
                payload=payload,
            )
        )
    return runner


def _context_for_transition(src: str, dst: str) -> dict[str, bool]:
    return {
        "pour_to_scene": {"case_resolution_complete": True, "all_players_ready": True},
        "scene_to_grill": {"evidence_wave_delivered": True},
        "grill_to_twist": {"interrogation_rounds_complete": True},
        "twist_to_last_call": {"twist_delivered": True},
        "last_call_to_truth": {"accusations_locked_or_countdown_expired": True},
    }[f"{src}_to_{dst}"]


@pytest.mark.parametrize("player_count", [2, 8])
def test_full_arc_completes(player_count: int) -> None:
    runner = _run_full_arc(seed=42, participant_count=player_count)
    assert sorted(runner.snapshot().configuration) == ["truth"]
    resolved = runner.current_run().runtime_state.resolved_generative_elements
    case = resolved["case_resolution"]
    assert case["arc_id"] == "nightcap-couch-race-v1"
    assert case["seed"] == 42


def test_deterministic_replay_across_runs() -> None:
    a = _run_full_arc(seed=99, participant_count=4)
    b = _run_full_arc(seed=99, participant_count=4)
    ra = a.current_run().runtime_state.resolved_generative_elements["case_resolution"]
    rb = b.current_run().runtime_state.resolved_generative_elements["case_resolution"]
    assert ra == rb


def test_cast_size_scales_at_the_harness_level() -> None:
    small = _run_full_arc(seed=1, participant_count=2)
    large = _run_full_arc(seed=1, participant_count=8)
    small_case = small.current_run().runtime_state.resolved_generative_elements[
        "case_resolution"
    ]
    large_case = large.current_run().runtime_state.resolved_generative_elements[
        "case_resolution"
    ]
    assert small_case["cast_size"] == 4
    assert large_case["cast_size"] == 6
