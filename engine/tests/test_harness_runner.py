"""Tests for engine/harness/runner.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.arc import transition_name_for
from engine.harness import HarnessAction, HarnessRunner

ARC_PATH = Path(__file__).parents[2] / "nightcap" / "arc.json"
INTRO_TO_INVESTIGATION = transition_name_for("introduction", "investigation")
INVESTIGATION_TO_REVEAL = transition_name_for("investigation", "reveal")
READY_CONTEXT = {"context": {"all_players_ready": True}}
REVEAL_CONTEXT = {"context": {"core_clues_revealed": True}}
PLAYERS = ["player-a", "player-b", "player-c", "player-d"]
HOST_BYPASS = {
    "host_bypass": {
        "actor_id": "host-1",
        "actor_role": "host",
        "reason": "players need manual reveal after stalled accusation",
    }
}


def test_runner_initialises_from_nightcap_arc() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)

    run = runner.start()

    assert run.arc_id == "nightcap"
    assert run.seed == 110
    assert run.step_index == 0
    assert run.configuration == ["introduction"]
    assert run.trace == []


def test_apply_action_advances_configuration() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()

    entry = runner.apply_action(
        HarnessAction(
            transition_name=INTRO_TO_INVESTIGATION,
            payload=READY_CONTEXT,
        )
    )
    snapshot = runner.snapshot()

    assert entry.step_index == 1
    assert entry.transition_name == INTRO_TO_INVESTIGATION
    assert entry.from_configuration == ["introduction"]
    assert entry.to_configuration == ["investigation"]
    assert snapshot.step_index == 1
    assert snapshot.configuration == ["investigation"]


def test_killer_assignment_resolves_during_introduction_setup() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()

    run = runner.set_participants(PLAYERS)

    assert run.configuration == ["introduction"]
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


def test_full_happy_path_reaches_reveal() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()

    actions = [
        HarnessAction(
            transition_name=INTRO_TO_INVESTIGATION,
            payload=READY_CONTEXT,
        ),
        HarnessAction(
            transition_name=INVESTIGATION_TO_REVEAL,
            payload=REVEAL_CONTEXT,
        ),
    ]

    for action in actions:
        runner.apply_action(action)

    snapshot = runner.snapshot()

    assert snapshot.step_index == 2
    assert snapshot.configuration == ["reveal"]
    run = runner.current_run()
    assert run.runtime_state.reveal_state.is_revealed is True
    assert run.runtime_state.reveal_state.revealed_by == "authored_conditions"
    assert run.runtime_state.reveal_state.bypass_sequence is None
    assert run.runtime_state.transition_bypass_log == []


def test_snapshot_reflects_current_step_and_configuration() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()
    runner.apply_action(
        HarnessAction(
            transition_name=INTRO_TO_INVESTIGATION,
            payload=READY_CONTEXT,
        )
    )

    snapshot = runner.snapshot()

    assert snapshot.step_index == 1
    assert snapshot.seed == 110
    assert snapshot.configuration == ["investigation"]


def test_same_seed_same_actions_identical_trace() -> None:
    actions = [
        HarnessAction(
            transition_name=INTRO_TO_INVESTIGATION,
            payload={**READY_CONTEXT, "source": "scripted"},
        ),
        HarnessAction(
            transition_name=INVESTIGATION_TO_REVEAL,
            payload={**REVEAL_CONTEXT, "source": "scripted"},
        ),
    ]

    first_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    second_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    first_runner.start()
    second_runner.start()

    for action in actions:
        first_runner.apply_action(action)
        second_runner.apply_action(action)

    assert first_runner.trace() == second_runner.trace()


def test_same_seed_produces_identical_killer_assignment_and_reveal_state() -> None:
    actions = [
        HarnessAction(
            transition_name=INTRO_TO_INVESTIGATION,
            payload=READY_CONTEXT,
        ),
        HarnessAction(
            transition_name=INVESTIGATION_TO_REVEAL,
            payload=REVEAL_CONTEXT,
        ),
    ]
    first_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    second_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    first_runner.start()
    second_runner.start()
    first_runner.set_participants(PLAYERS)
    second_runner.set_participants(PLAYERS)

    for action in actions:
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
                transition_name=INVESTIGATION_TO_REVEAL,
                payload=REVEAL_CONTEXT,
            )
        )

    assert runner.snapshot().configuration == ["introduction"]
    assert runner.snapshot().step_index == 0
    assert runner.trace() == []

    runner.apply_action(
        HarnessAction(
            transition_name=INTRO_TO_INVESTIGATION,
            payload=READY_CONTEXT,
        )
    )
    with pytest.raises(ValueError, match="is not enabled"):
        runner.apply_action(HarnessAction(transition_name=INVESTIGATION_TO_REVEAL))

    assert runner.snapshot().configuration == ["investigation"]
    assert runner.snapshot().step_index == 1
    assert runner.current_run().runtime_state.reveal_state.is_revealed is False

    entry = runner.apply_action(
        HarnessAction(
            transition_name=INVESTIGATION_TO_REVEAL,
            payload=REVEAL_CONTEXT,
        )
    )

    assert entry.to_configuration == ["reveal"]


def test_reveal_can_fire_with_logged_host_bypass() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()
    runner.set_participants(PLAYERS)
    runner.apply_action(
        HarnessAction(
            transition_name=INTRO_TO_INVESTIGATION,
            payload=READY_CONTEXT,
        )
    )

    entry = runner.apply_action(
        HarnessAction(
            transition_name=INVESTIGATION_TO_REVEAL,
            payload=HOST_BYPASS,
        )
    )
    run = runner.current_run()
    bypass_log = run.runtime_state.transition_bypass_log

    assert entry.to_configuration == ["reveal"]
    assert run.runtime_state.reveal_state.is_revealed is True
    assert run.runtime_state.reveal_state.revealed_by == "host_bypass"
    assert run.runtime_state.reveal_state.bypass_sequence == 1
    assert len(bypass_log) == 1
    assert bypass_log[0].sequence == 1
    assert bypass_log[0].actor_id == "host-1"
    assert bypass_log[0].reason == HOST_BYPASS["host_bypass"]["reason"]
    assert bypass_log[0].source_transition == INVESTIGATION_TO_REVEAL
    assert bypass_log[0].source_beat_id == "investigation"
    assert bypass_log[0].target_beat_id == "reveal"
    assert bypass_log[0].bypassed_conditions == ["core_clues_revealed"]
    assert runner.context_value("core_clues_revealed") is None


def test_non_host_reveal_bypass_fails() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()
    runner.set_participants(PLAYERS)
    runner.apply_action(
        HarnessAction(
            transition_name=INTRO_TO_INVESTIGATION,
            payload=READY_CONTEXT,
        )
    )

    with pytest.raises(ValueError, match="actor_role='host'"):
        runner.apply_action(
            HarnessAction(
                transition_name=INVESTIGATION_TO_REVEAL,
                payload={
                    "host_bypass": {
                        "actor_id": "player-a",
                        "actor_role": "player",
                        "reason": "trying to force reveal",
                    }
                },
            )
        )

    assert runner.snapshot().configuration == ["investigation"]
    assert runner.current_run().runtime_state.transition_bypass_log == []


def test_reveal_bypass_without_reason_fails() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()
    runner.set_participants(PLAYERS)
    runner.apply_action(
        HarnessAction(
            transition_name=INTRO_TO_INVESTIGATION,
            payload=READY_CONTEXT,
        )
    )

    with pytest.raises(ValueError, match="non-empty reason"):
        runner.apply_action(
            HarnessAction(
                transition_name=INVESTIGATION_TO_REVEAL,
                payload={
                    "host_bypass": {
                        "actor_id": "host-1",
                        "actor_role": "host",
                    }
                },
            )
        )

    assert runner.snapshot().configuration == ["investigation"]
    assert runner.current_run().runtime_state.transition_bypass_log == []


def test_apply_action_does_not_call_generation_callback() -> None:
    def fail_generate(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("generation should not be called for beat transitions")

    runner = HarnessRunner(arc_path=ARC_PATH, seed=110, generate=fail_generate)
    runner.start()

    runner.apply_action(
        HarnessAction(
            transition_name=INTRO_TO_INVESTIGATION,
            payload=READY_CONTEXT,
        )
    )

    assert runner.snapshot().configuration == ["investigation"]
