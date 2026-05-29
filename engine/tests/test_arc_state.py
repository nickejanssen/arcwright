"""
Tests for architecture-aligned arc models and placeholder StateChart flow.
"""

import json
from pathlib import Path

import pytest

from engine.arc import ArcDefinition, ArcStateChart, BeatDefinition
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
    return ArcDefinition(
        arc_id="test_arc",
        name="Test Arc",
        min_players=4,
        max_players=10,
        character_mode="generated",
        aesthetic_mode="fixed",
        setting_constraint="social_gathering",
        arc_structure="dan_harmon",
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
        beats=[sample_beat],
        beat_graph={
            "introduction": ["investigation"],
            "investigation": ["reveal"],
            "reveal": [],
        },
        generative_elements={"killer_assignment_strategy": "ai_driven"},
        content_rails={"tone": "murder_mystery"},
        knowledge_rules={},
        pacing_config={"premium_threshold": 0.75},
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
        assert sample_beat.pacing_config["stall_threshold_seconds"] == 180


class TestArcDefinition:
    def test_arc_definition_is_pydantic_and_complete(
        self, sample_arc_definition: ArcDefinition
    ):
        assert sample_arc_definition.arc_id == "test_arc"
        assert sample_arc_definition.character_mode.value == "generated"
        assert sample_arc_definition.play_mode.value == "imposter"
        assert sample_arc_definition.narrator.type == "host_persona"
        assert sample_arc_definition.quality_tier_default == QualityTier.standard

    def test_nightcap_arc_json_validates(self):
        arc_payload = json.loads((REPO_ROOT / "nightcap" / "arc.json").read_text())
        parsed = ArcDefinition(**arc_payload)
        assert parsed.arc_id == "nightcap"
        assert len(parsed.beats) == 3
        assert "investigation" in parsed.beat_graph


class TestArcStateChart:
    @pytest.fixture
    def chart(self, sample_arc_definition: ArcDefinition) -> ArcStateChart:
        return ArcStateChart(sample_arc_definition)

    def test_chart_initialization(
        self, chart: ArcStateChart, sample_arc_definition: ArcDefinition
    ):
        assert chart.arc_definition == sample_arc_definition
        assert chart.session_context == {}

    def test_chart_initial_state(self, chart: ArcStateChart):
        state_ids = {state.id for state in chart.configuration}
        assert "introduction" in state_ids

    def test_chart_context_management(self, chart: ArcStateChart):
        chart.update_context("killer_id", "character_001")
        assert chart.get_context("killer_id") == "character_001"
        assert chart.get_context("missing", "default") == "default"

    def test_chart_complete_flow(self, chart: ArcStateChart):
        chart.send("begin_game")
        chart.send("motives_established")
        chart.send("investigation_begins")
        chart.send("clues_sent")
        chart.send("interrogation_complete")
        chart.send("phases_complete")
        chart.send("accusation_filed")

        state_ids = {state.id for state in chart.configuration}
        assert "reveal" in state_ids
