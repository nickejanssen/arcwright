"""Tests for engine/harness/runner.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.arc import transition_name_for
from engine.harness import HarnessAction, HarnessRunner

ARC_PATH = Path(__file__).parents[2] / "nightcap" / "arc.json"

BEAT_SEQUENCE = [
    "arrival",
    "body",
    "opening_move",
    "dig",
    "thread",
    "reckoning",
    "close",
    "truth",
]
EXIT_CONDITIONS = {
    "arrival": "all_players_ready",
    "body": "body_discovered",
    "opening_move": "private_clues_distributed",
    "dig": "killer_revealed_to_themselves",
    "thread": "first_convergence_reached",
    "reckoning": "accusations_resolved",
    "close": "final_accusation_committed",
}

ARRIVAL_TO_BODY = transition_name_for("arrival", "body")
CLOSE_TO_TRUTH = transition_name_for("close", "truth")

PLAYERS = ["player-a", "player-b", "player-c", "player-d"]
HOST_BYPASS = {
    "host_bypass": {
        "actor_id": "host-1",
        "actor_role": "host",
        "reason": "players need manual reveal after stalled accusation",
    }
}


def _next_step_action(current_beat: str) -> HarnessAction:
    """Return an action that advances from current_beat to the next beat."""
    index = BEAT_SEQUENCE.index(current_beat)
    next_beat = BEAT_SEQUENCE[index + 1]
    exit_condition = EXIT_CONDITIONS[current_beat]
    return HarnessAction(
        transition_name=transition_name_for(current_beat, next_beat),
        payload={"context": {exit_condition: True}},
    )


def _advance_to(runner: HarnessRunner, target_beat: str) -> None:
    """Apply happy-path actions until the runner reaches target_beat."""
    target_index = BEAT_SEQUENCE.index(target_beat)
    for current_beat in BEAT_SEQUENCE[:target_index]:
        runner.apply_action(_next_step_action(current_beat))


def test_runner_initialises_from_nightcap_arc() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)

    run = runner.start()

    assert run.arc_id == "nightcap"
    assert run.seed == 110
    assert run.step_index == 0
    assert run.configuration == ["arrival"]
    assert run.trace == []


def test_apply_action_advances_configuration() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()

    entry = runner.apply_action(_next_step_action("arrival"))
    snapshot = runner.snapshot()

    assert entry.step_index == 1
    assert entry.transition_name == ARRIVAL_TO_BODY
    assert entry.from_configuration == ["arrival"]
    assert entry.to_configuration == ["body"]
    assert snapshot.step_index == 1
    assert snapshot.configuration == ["body"]


def test_killer_assignment_resolves_during_arrival_setup() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()

    run = runner.set_participants(PLAYERS)

    assert run.configuration == ["arrival"]
    assert run.step_index == 0
    assert run.runtime_state.role_assignments["killer"] in PLAYERS
    assert run.runtime_state.resolved_generative_elements["killer_assignment"] == {
        "role": "killer",
        "participant_id": run.runtime_state.role_assignments["killer"],
        "seed": 110,
        "candidate_participants": PLAYERS,
    }


def test_same_seed_and_participants_produce_same_killer_assignment() -> None:
    first_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    second_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    first_runner.start()
    second_runner.start()

    first_run = first_runner.set_participants(PLAYERS)
    second_run = second_runner.set_participants(PLAYERS)

    assert (
        first_run.runtime_state.role_assignments
        == second_run.runtime_state.role_assignments
    )
    assert (
        first_run.runtime_state.resolved_generative_elements
        == second_run.runtime_state.resolved_generative_elements
    )


def test_full_happy_path_reaches_truth() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()

    for current_beat in BEAT_SEQUENCE[:-1]:
        runner.apply_action(_next_step_action(current_beat))

    snapshot = runner.snapshot()

    assert snapshot.step_index == 7
    assert snapshot.configuration == ["truth"]
    run = runner.current_run()
    assert run.runtime_state.reveal_state.is_revealed is True
    assert run.runtime_state.reveal_state.revealed_by == "authored_conditions"
    assert run.runtime_state.reveal_state.bypass_sequence is None
    assert run.runtime_state.transition_bypass_log == []


def test_snapshot_reflects_current_step_and_configuration() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()
    runner.apply_action(_next_step_action("arrival"))

    snapshot = runner.snapshot()

    assert snapshot.step_index == 1
    assert snapshot.seed == 110
    assert snapshot.configuration == ["body"]


def test_same_seed_same_actions_identical_trace() -> None:
    first_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    second_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    first_runner.start()
    second_runner.start()

    for current_beat in BEAT_SEQUENCE[:-1]:
        action = _next_step_action(current_beat)
        scripted = HarnessAction(
            transition_name=action.transition_name,
            payload={**action.payload, "source": "scripted"},
        )
        first_runner.apply_action(scripted)
        second_runner.apply_action(scripted)

    assert first_runner.trace() == second_runner.trace()


def test_same_seed_produces_identical_killer_assignment_and_reveal_state() -> None:
    first_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    second_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    first_runner.start()
    second_runner.start()
    first_runner.set_participants(PLAYERS)
    second_runner.set_participants(PLAYERS)

    for current_beat in BEAT_SEQUENCE[:-1]:
        action = _next_step_action(current_beat)
        first_runner.apply_action(action)
        second_runner.apply_action(action)

    first_state = first_runner.current_run().runtime_state
    second_state = second_runner.current_run().runtime_state
    assert first_state.role_assignments == second_state.role_assignments
    assert first_state.reveal_state == second_state.reveal_state


def test_same_seed_produces_identical_session_id_and_snapshot() -> None:
    first_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    second_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)

    first_run = first_runner.start()
    second_run = second_runner.start()

    assert first_run.session_id == second_run.session_id
    assert first_runner.snapshot() == second_runner.snapshot()


def test_start_raises_when_called_twice() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()

    with pytest.raises(RuntimeError, match="already been called"):
        runner.start()


def test_apply_action_rejects_unknown_transition_name() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()

    with pytest.raises(ValueError, match="Unknown transition"):
        runner.apply_action(HarnessAction(transition_name="update_context"))


def test_unaccepted_action_rolls_back_context_payload_and_raises() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()

    with pytest.raises(ValueError, match="is not enabled"):
        runner.apply_action(
            HarnessAction(
                transition_name=CLOSE_TO_TRUTH,
                payload={"context": {"final_accusation_committed": True}},
            )
        )

    assert runner.snapshot().configuration == ["arrival"]
    assert runner.snapshot().step_index == 0
    assert runner.trace() == []

    runner.apply_action(_next_step_action("arrival"))
    with pytest.raises(ValueError, match="is not enabled"):
        runner.apply_action(HarnessAction(transition_name=CLOSE_TO_TRUTH))

    assert runner.snapshot().configuration == ["body"]
    assert runner.snapshot().step_index == 1
    assert runner.current_run().runtime_state.reveal_state.is_revealed is False


def test_reveal_can_fire_with_logged_host_bypass() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()
    runner.set_participants(PLAYERS)
    _advance_to(runner, "close")

    entry = runner.apply_action(
        HarnessAction(
            transition_name=CLOSE_TO_TRUTH,
            payload=HOST_BYPASS,
        )
    )
    run = runner.current_run()
    bypass_log = run.runtime_state.transition_bypass_log

    assert entry.to_configuration == ["truth"]
    assert run.runtime_state.reveal_state.is_revealed is True
    assert run.runtime_state.reveal_state.revealed_by == "host_bypass"
    assert run.runtime_state.reveal_state.bypass_sequence == 1
    assert len(bypass_log) == 1
    assert bypass_log[0].sequence == 1
    assert bypass_log[0].actor_id == "host-1"
    assert bypass_log[0].reason == HOST_BYPASS["host_bypass"]["reason"]
    assert bypass_log[0].source_transition == CLOSE_TO_TRUTH
    assert bypass_log[0].source_beat_id == "close"
    assert bypass_log[0].target_beat_id == "truth"
    assert bypass_log[0].bypassed_conditions == ["final_accusation_committed"]
    assert runner.context_value("final_accusation_committed") is None


def test_non_host_reveal_bypass_fails() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()
    runner.set_participants(PLAYERS)
    _advance_to(runner, "close")

    with pytest.raises(ValueError, match="actor_role='host'"):
        runner.apply_action(
            HarnessAction(
                transition_name=CLOSE_TO_TRUTH,
                payload={
                    "host_bypass": {
                        "actor_id": "player-a",
                        "actor_role": "player",
                        "reason": "trying to force reveal",
                    }
                },
            )
        )

    assert runner.snapshot().configuration == ["close"]
    assert runner.current_run().runtime_state.transition_bypass_log == []


def test_reveal_bypass_without_reason_fails() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()
    runner.set_participants(PLAYERS)
    _advance_to(runner, "close")

    with pytest.raises(ValueError, match="non-empty reason"):
        runner.apply_action(
            HarnessAction(
                transition_name=CLOSE_TO_TRUTH,
                payload={
                    "host_bypass": {
                        "actor_id": "host-1",
                        "actor_role": "host",
                    }
                },
            )
        )

    assert runner.snapshot().configuration == ["close"]
    assert runner.current_run().runtime_state.transition_bypass_log == []


def test_malformed_bypass_with_authored_context_fails_before_reveal() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()
    runner.set_participants(PLAYERS)
    _advance_to(runner, "close")

    with pytest.raises(ValueError, match="actor_role='host'"):
        runner.apply_action(
            HarnessAction(
                transition_name=CLOSE_TO_TRUTH,
                payload={
                    "context": {"final_accusation_committed": True},
                    "host_bypass": {
                        "actor_id": "player-a",
                        "actor_role": "player",
                        "reason": "trying to force reveal",
                    },
                },
            )
        )

    run = runner.current_run()
    assert runner.snapshot().configuration == ["close"]
    assert run.runtime_state.reveal_state.is_revealed is False
    assert run.runtime_state.transition_bypass_log == []
    assert runner.context_value("final_accusation_committed") is None


def test_apply_action_does_not_call_generation_callback() -> None:
    def fail_generate(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("generation should not be called for beat transitions")

    runner = HarnessRunner(arc_path=ARC_PATH, seed=110, generate=fail_generate)
    runner.start()

    runner.apply_action(_next_step_action("arrival"))

    assert runner.snapshot().configuration == ["body"]
