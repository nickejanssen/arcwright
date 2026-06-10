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

    entry = runner.apply_action(
        HarnessAction(
            transition_name=INVESTIGATION_TO_REVEAL,
            payload=REVEAL_CONTEXT,
        )
    )

    assert entry.to_configuration == ["reveal"]


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
