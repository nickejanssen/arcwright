"""Tests for engine/harness/runner.py."""

from __future__ import annotations

from pathlib import Path

from engine.harness import HarnessAction, HarnessRunner

ARC_PATH = Path("nightcap/arc.json")


def test_runner_initialises_from_nightcap_arc() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)

    run = runner.start()

    assert run.arc_id == "nightcap"
    assert run.seed == 110
    assert run.step_index == 0
    assert run.configuration == ["introduction", "onboarding"]
    assert run.trace == []


def test_apply_action_advances_configuration() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()

    entry = runner.apply_action(HarnessAction(transition_name="begin_game"))
    snapshot = runner.snapshot()

    assert entry.step_index == 1
    assert entry.transition_name == "begin_game"
    assert entry.from_configuration == ["introduction", "onboarding"]
    assert entry.to_configuration == ["introduction", "killer_assignment"]
    assert snapshot.step_index == 1
    assert snapshot.configuration == ["introduction", "killer_assignment"]


def test_full_happy_path_reaches_reveal() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()

    transitions = [
        "begin_game",
        "motives_established",
        "investigation_begins",
        "clues_sent",
        "interrogation_complete",
        "phases_complete",
        "accusation_filed",
    ]

    for transition_name in transitions:
        runner.apply_action(HarnessAction(transition_name=transition_name))

    snapshot = runner.snapshot()

    assert snapshot.step_index == 7
    assert snapshot.configuration == ["reveal"]


def test_snapshot_reflects_current_step_and_configuration() -> None:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    runner.start()
    runner.apply_action(HarnessAction(transition_name="begin_game"))
    runner.apply_action(HarnessAction(transition_name="motives_established"))

    snapshot = runner.snapshot()

    assert snapshot.step_index == 2
    assert snapshot.seed == 110
    assert snapshot.configuration == ["introduction", "motive_reveal"]


def test_same_seed_same_actions_identical_trace() -> None:
    transitions = [
        "begin_game",
        "motives_established",
        "investigation_begins",
        "clues_sent",
        "interrogation_complete",
        "phases_complete",
        "accusation_filed",
    ]

    first_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    second_runner = HarnessRunner(arc_path=ARC_PATH, seed=110)
    first_runner.start()
    second_runner.start()

    for transition_name in transitions:
        action = HarnessAction(
            transition_name=transition_name,
            payload={"source": "scripted"},
        )
        first_runner.apply_action(action)
        second_runner.apply_action(action)

    assert first_runner.trace() == second_runner.trace()
