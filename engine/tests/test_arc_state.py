"""
Tests for architecture-aligned arc models and placeholder StateChart flow.
"""

import json
from pathlib import Path

import pytest

from engine.arc import ArcDefinition, ArcStateChart, BeatDefinition, transition_name_for
from engine.session.models import QualityTier

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def sample_beat() -> BeatDefinition:
    return BeatDefinition(
        beat_id="introduction",
        beat_name="Introduction",
        beat_type="introduction",
        story_circle_step=1,
        structural_function="establish_comfort",
        emotional_target="curious",
        information_goal="Players understand the premise",
        tension_target=0.2,
        character_emphasis=["host"],
        generative_triggers=["killer_assignment"],
        entry_conditions=[],
        exit_conditions=["all_players_ready"],
        pacing_config={"stall_threshold_seconds": 180},
        audience_targets=["all"],
    )


@pytest.fixture
def sample_arc_definition(sample_beat: BeatDefinition) -> ArcDefinition:
    investigation_beat = BeatDefinition(
        beat_id="investigation",
        beat_name="Investigation",
        beat_type="investigation",
        story_circle_step=[2, 3, 4, 5, 6],
        structural_function="surface_disruption",
        emotional_target="tense",
        information_goal="Players gather clues",
        tension_target=0.7,
        character_emphasis=["suspects"],
        generative_triggers=["clue_content"],
        entry_conditions=["all_players_ready"],
        exit_conditions=["core_clues_revealed"],
        pacing_config={"stall_threshold_seconds": 300},
        audience_targets=["all", "specific_player"],
    )
    reveal_beat = BeatDefinition(
        beat_id="reveal",
        beat_name="Reveal",
        beat_type="reveal",
        story_circle_step=8,
        structural_function="deliver_resolution",
        emotional_target="satisfied",
        information_goal="Players learn the killer identity",
        tension_target=0.95,
        character_emphasis=["killer"],
        generative_triggers=["narrator_dialogue"],
        entry_conditions=["core_clues_revealed"],
        exit_conditions=["session_complete"],
        pacing_config={"stall_threshold_seconds": 120},
        audience_targets=["all"],
    )
    return ArcDefinition(
        arc_id="test_arc",
        name="Test Arc",
        min_players=4,
        max_players=10,
        character_mode="generated",
        aesthetic_config={
            "selection_model": {},
            "asset_generation": {"background_art": "pre_produced_per_theme"},
        },
        setting_constraint="social_gathering",
        arc_structure="story_circle",
        play_mode="imposter",
        narrator={
            "type": "host_persona",
            "surface": "shared_display",
            "persona_mode": "fixed",
            "behavior_triggers": ["beat_transition"],
            "omniscient": True,
            "player_addressable": True,
        },
        quality_tier_default=QualityTier.standard,
        characters=[],
        beats=[sample_beat, investigation_beat, reveal_beat],
        beat_graph={
            "introduction": ["investigation"],
            "investigation": ["reveal"],
            "reveal": [],
        },
        generative_elements={"killer_assignment": True},
        content_rails={
            "prohibited_categories": ["csam", "graphic_violence"],
            "thematic_warnings": ["murder_mystery"],
            "age_floor": 18,
        },
        knowledge_rules={
            "killer_knows_they_did_it": True,
            "narrator_omniscient": True,
            "clues_private_until_shared": True,
        },
        pacing_config={
            "premium_threshold": 0.75,
            "w_time": 0.3,
            "w_action": 0.3,
            "w_suspicion": 0.2,
            "w_coverage": 0.2,
        },
        victim_config={"selection_mode": "generated"},
        kill_config={"assignment_mode": "ai_assigned"},
        murder_timing_range=[1, 3],
        session_duration_range=[60, 120],
        revelation_step_range=[7, 8],
        tone_config={"genre": "murder_mystery"},
    )


class TestBeatDefinition:
    def test_beat_definition_exposes_architecture_fields(
        self, sample_beat: BeatDefinition
    ):
        assert sample_beat.beat_name == "Introduction"
        assert sample_beat.story_circle_step == 1
        assert sample_beat.structural_function == "establish_comfort"
        assert sample_beat.pacing_config.stall_threshold_seconds == 180


class TestArcDefinition:
    def test_arc_definition_is_pydantic_and_complete(
        self, sample_arc_definition: ArcDefinition
    ):
        assert sample_arc_definition.arc_id == "test_arc"
        assert sample_arc_definition.character_mode.value == "generated"
        assert sample_arc_definition.play_mode.value == "imposter"
        assert sample_arc_definition.narrator.type == "host_persona"
        assert sample_arc_definition.quality_tier_default == QualityTier.standard
        assert (
            sample_arc_definition.aesthetic_config.asset_generation["background_art"]
            == "pre_produced_per_theme"
        )

    def test_nightcap_arc_json_validates(self):
        arc_payload = json.loads((REPO_ROOT / "nightcap" / "arc.json").read_text())
        parsed = ArcDefinition(**arc_payload)
        assert parsed.arc_id == "nightcap"
        assert len(parsed.beats) == 8
        assert "dig" in parsed.beat_graph


def _beat(
    beat_id: str,
    *,
    entry_conditions: list[str] | None = None,
    exit_conditions: list[str] | None = None,
) -> BeatDefinition:
    return BeatDefinition(
        beat_id=beat_id,
        beat_name=beat_id.replace("_", " ").title(),
        beat_type=beat_id,
        story_circle_step=1,
        structural_function="test_function",
        emotional_target="curious",
        information_goal="Test information goal",
        tension_target=0.5,
        character_emphasis=[],
        generative_triggers=[],
        entry_conditions=entry_conditions or [],
        exit_conditions=exit_conditions or [],
        pacing_config={"stall_threshold_seconds": 180},
        audience_targets=["all"],
    )


def _arc_for_graph(
    beat_ids: list[str],
    beat_graph: dict[str, list[str]],
    *,
    entry_conditions: dict[str, list[str]] | None = None,
    exit_conditions: dict[str, list[str]] | None = None,
) -> ArcDefinition:
    return ArcDefinition(
        arc_id="graph_test",
        name="Graph Test",
        min_players=4,
        max_players=10,
        character_mode="generated",
        aesthetic_config={
            "selection_model": {},
            "asset_generation": {"background_art": "pre_produced_per_theme"},
        },
        setting_constraint="social_gathering",
        arc_structure="story_circle",
        play_mode="imposter",
        narrator={
            "type": "host_persona",
            "surface": "shared_display",
            "persona_mode": "fixed",
            "behavior_triggers": ["beat_transition"],
            "omniscient": True,
            "player_addressable": True,
        },
        quality_tier_default=QualityTier.standard,
        characters=[],
        beats=[
            _beat(
                beat_id,
                entry_conditions=(entry_conditions or {}).get(beat_id),
                exit_conditions=(exit_conditions or {}).get(beat_id),
            )
            for beat_id in beat_ids
        ],
        beat_graph=beat_graph,
        generative_elements={"killer_assignment": True},
        content_rails={
            "prohibited_categories": ["csam", "graphic_violence"],
            "thematic_warnings": ["murder_mystery"],
            "age_floor": 18,
        },
        knowledge_rules={
            "killer_knows_they_did_it": True,
            "narrator_omniscient": True,
            "clues_private_until_shared": True,
        },
        pacing_config={
            "premium_threshold": 0.75,
            "w_time": 0.3,
            "w_action": 0.3,
            "w_suspicion": 0.2,
            "w_coverage": 0.2,
        },
        victim_config={"selection_mode": "generated"},
        kill_config={"assignment_mode": "ai_assigned"},
        murder_timing_range=[1, 3],
        session_duration_range=[60, 120],
        revelation_step_range=[7, 8],
        tone_config={"genre": "murder_mystery"},
    )


def _send(chart, source: str, target: str) -> None:
    chart.send(transition_name_for(source, target))


class TestArcStateChart:
    @pytest.fixture
    def chart(self, sample_arc_definition: ArcDefinition):
        return ArcStateChart(sample_arc_definition)

    def test_chart_initialization(self, chart, sample_arc_definition: ArcDefinition):
        assert chart.arc_definition == sample_arc_definition
        assert chart.session_context == {}

    def test_chart_initial_state(self, chart):
        assert sorted(chart.configuration_values) == ["introduction"]

    def test_chart_context_management(self, chart):
        chart.update_context("killer_id", "character_001")
        assert chart.get_context("killer_id") == "character_001"
        assert chart.get_context("missing", "default") == "default"

    def test_linear_graph_reaches_reveal(self):
        arc = _arc_for_graph(
            ["introduction", "investigation", "reveal"],
            {
                "introduction": ["investigation"],
                "investigation": ["reveal"],
                "reveal": [],
            },
        )
        chart = ArcStateChart(arc)

        _send(chart, "introduction", "investigation")
        _send(chart, "investigation", "reveal")

        assert sorted(chart.configuration_values) == ["reveal"]

    def test_branching_graph_can_take_authored_branch(self):
        arc = _arc_for_graph(
            ["introduction", "investigation", "reveal"],
            {
                "introduction": ["investigation", "reveal"],
                "investigation": ["reveal"],
                "reveal": [],
            },
        )
        chart = ArcStateChart(arc)

        _send(chart, "introduction", "reveal")

        assert sorted(chart.configuration_values) == ["reveal"]

    def test_converging_graph_supports_multiple_sources_to_target(self):
        arc = _arc_for_graph(
            ["introduction", "clue_path", "social_path", "reveal"],
            {
                "introduction": ["clue_path", "social_path"],
                "clue_path": ["reveal"],
                "social_path": ["reveal"],
                "reveal": [],
            },
        )

        clue_chart = ArcStateChart(arc)
        _send(clue_chart, "introduction", "clue_path")
        _send(clue_chart, "clue_path", "reveal")

        social_chart = ArcStateChart(arc)
        _send(social_chart, "introduction", "social_path")
        _send(social_chart, "social_path", "reveal")

        assert sorted(clue_chart.configuration_values) == ["reveal"]
        assert sorted(social_chart.configuration_values) == ["reveal"]

    def test_loop_graph_can_return_to_earlier_beat(self):
        arc = _arc_for_graph(
            ["introduction", "investigation"],
            {
                "introduction": ["investigation"],
                "investigation": ["introduction"],
            },
        )
        chart = ArcStateChart(arc)

        _send(chart, "introduction", "investigation")
        _send(chart, "investigation", "introduction")

        assert sorted(chart.configuration_values) == ["introduction"]

    def test_transition_guard_requires_source_exit_and_target_entry_conditions(self):
        arc = _arc_for_graph(
            ["introduction", "investigation"],
            {
                "introduction": ["investigation"],
                "investigation": [],
            },
            exit_conditions={"introduction": ["players_ready"]},
            entry_conditions={"investigation": ["clues_seeded"]},
        )
        chart = ArcStateChart(arc)
        transition = transition_name_for("introduction", "investigation")

        chart.send(transition)
        assert sorted(chart.configuration_values) == ["introduction"]

        chart.satisfy_condition("players_ready")
        chart.send(transition)
        assert sorted(chart.configuration_values) == ["introduction"]

        chart.satisfy_condition("clues_seeded")
        chart.send(transition)
        assert sorted(chart.configuration_values) == ["investigation"]

    def test_generated_chart_does_not_expose_custom_graph_traversal(self, chart):
        assert not hasattr(chart, "can_transition_to")
        assert transition_name_for("introduction", "investigation") in (
            chart.transition_names
        )
