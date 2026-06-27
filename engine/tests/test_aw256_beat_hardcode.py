"""AW-256: Engine must not hardcode any arc's beat IDs.

Regression guard: if the engine ever reverts to checking ``"arrival"``
by name, this test fails because the synthetic arc uses ``"lobby"`` as
its initial beat.
"""

from __future__ import annotations

import pytest

from engine.arc.models import (
    AestheticConfig,
    ArcDefinition,
    BeatDefinition,
    BeatPacingConfig,
    CharacterMode,
    ContentRailsConfig,
    GenerativeConfig,
    KnowledgeRuleSet,
    NarratorConfig,
    PacingConfig,
    PlayMode,
)
from engine.harness import HarnessAction, HarnessRunner
from engine.session.models import QualityTier


def _synthetic_arc(initial_beat_id: str = "lobby") -> ArcDefinition:
    """Build a minimal valid ArcDefinition whose first beat is not 'arrival'."""
    second_beat_id = "investigation"
    return ArcDefinition(
        arc_id="test-arc",
        name="Test Arc",
        min_players=4,
        max_players=8,
        character_mode=CharacterMode.generated,
        aesthetic_config=AestheticConfig(),
        arc_structure="linear",
        play_mode=PlayMode.cooperative,
        narrator=NarratorConfig(
            type="ai",
            surface="display",
            persona_mode="narrator",
            behavior_triggers=[],
            omniscient=True,
            player_addressable=True,
        ),
        quality_tier_default=QualityTier.standard,
        beats=[
            BeatDefinition(
                beat_id=initial_beat_id,
                beat_name="The Lobby",
                beat_type="introduction",
                story_circle_step=1,
                structural_function="gather_players",
                exit_conditions=["all_players_ready"],
                pacing_config=BeatPacingConfig(),
            ),
            BeatDefinition(
                beat_id=second_beat_id,
                beat_name="Investigation",
                beat_type="investigation",
                story_circle_step=2,
                structural_function="investigate",
                pacing_config=BeatPacingConfig(),
            ),
        ],
        beat_graph={initial_beat_id: [second_beat_id], second_beat_id: []},
        generative_elements=GenerativeConfig(killer_assignment=True),
        content_rails=ContentRailsConfig(),
        knowledge_rules=KnowledgeRuleSet(),
        pacing_config=PacingConfig(
            w_time=0.25,
            w_action=0.25,
            w_suspicion=0.25,
            w_coverage=0.25,
        ),
    )


# ---------------------------------------------------------------------------
# HarnessRunner: initial beat derived from arc definition, not hardcoded
# ---------------------------------------------------------------------------


class TestHarnessRunnerInitialBeat:
    def test_set_participants_succeeds_when_initial_beat_is_not_arrival(self) -> None:
        """With first beat = 'lobby', set_participants must not raise."""
        arc = _synthetic_arc(initial_beat_id="lobby")
        runner = HarnessRunner(arc_definition=arc, seed=42)
        runner.start()
        run = runner.set_participants(["p1", "p2", "p3", "p4"])
        assert run.runtime_state.role_assignments.get("killer") in [
            "p1",
            "p2",
            "p3",
            "p4",
        ]

    def test_configuration_starts_at_declared_initial_beat(self) -> None:
        """The runner's initial configuration is beats[0].beat_id."""
        arc = _synthetic_arc(initial_beat_id="lobby")
        runner = HarnessRunner(arc_definition=arc, seed=0)
        run = runner.start()
        assert run.configuration == ["lobby"]

    def test_set_participants_raises_when_past_initial_beat(self) -> None:
        """Calling set_participants for the first time after advancing past the
        initial beat raises a RuntimeError naming the initial beat."""
        from engine.arc.arc_state import transition_name_for

        arc = _synthetic_arc(initial_beat_id="lobby")
        runner = HarnessRunner(arc_definition=arc, seed=0)
        runner.start()
        # Advance WITHOUT calling set_participants first (killer not yet assigned).
        runner.apply_action(
            HarnessAction(
                transition_name=transition_name_for("lobby", "investigation"),
                payload={"context": {"all_players_ready": True}},
            )
        )
        with pytest.raises(RuntimeError, match="initial beat"):
            runner.set_participants(["p1", "p2", "p3", "p4"])
