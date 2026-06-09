"""Tests for arc-definition schema validation."""

from __future__ import annotations

from copy import deepcopy

import pytest
from pydantic import ValidationError

from engine.arc.models import ArcDefinition


def valid_arc_payload() -> dict:
    return {
        "arc_id": "test_arc",
        "name": "Test Arc",
        "min_players": 4,
        "max_players": 10,
        "character_mode": "generated",
        "aesthetic_config": {
            "selection_model": {
                "era": {"type": "host_select", "allow_random": True},
            },
            "asset_generation": {
                "background_art": "pre_produced_per_theme",
                "narrator_dialogue": "generative_runtime",
            },
        },
        "setting_constraint": "social_gathering",
        "arc_structure": "story_circle",
        "play_mode": "imposter",
        "narrator": {
            "type": "host_persona",
            "surface": "shared_display",
            "persona_mode": "aesthetic_linked",
            "behavior_triggers": [
                "beat_transition",
                "clue_release",
                "tension_threshold",
                "player_inaction",
            ],
            "omniscient": True,
            "player_addressable": True,
        },
        "quality_tier_default": "standard",
        "characters": [],
        "beats": [
            {
                "beat_id": "introduction",
                "beat_name": "The Arrival",
                "beat_type": "introduction",
                "story_circle_step": 1,
                "structural_function": "establish_comfort",
                "dramatic_purpose": "Introduce the gathering.",
                "emotional_target": "curious",
                "information_goal": "Players understand the premise.",
                "tension_target": 0.2,
                "character_emphasis": ["host"],
                "authored_content": {},
                "generative_triggers": ["killer_assignment"],
                "entry_conditions": [],
                "exit_conditions": ["all_players_ready"],
                "pacing_config": {"stall_threshold_seconds": 180},
                "audience_targets": ["all"],
                "mini_games": [],
            },
            {
                "beat_id": "investigation",
                "beat_name": "The Search",
                "beat_type": "investigation",
                "story_circle_step": [2, 3, 4, 5, 6],
                "structural_function": "surface_disruption",
                "dramatic_purpose": "Drive clue exchange.",
                "emotional_target": "tense",
                "information_goal": "Players gather clues.",
                "tension_target": 0.7,
                "character_emphasis": ["suspects"],
                "authored_content": None,
                "generative_triggers": ["clue_content"],
                "entry_conditions": ["all_players_ready"],
                "exit_conditions": ["core_clues_revealed"],
                "pacing_config": {"stall_threshold_seconds": 300},
                "audience_targets": ["all", "specific_player"],
                "mini_games": [],
            },
            {
                "beat_id": "reveal",
                "beat_name": "The Reveal",
                "beat_type": "reveal",
                "story_circle_step": 8,
                "structural_function": "deliver_resolution",
                "dramatic_purpose": "Resolve the case.",
                "emotional_target": "satisfied",
                "information_goal": "Players learn the killer identity.",
                "tension_target": 0.95,
                "character_emphasis": ["killer"],
                "authored_content": None,
                "generative_triggers": ["narrator_dialogue"],
                "entry_conditions": ["core_clues_revealed"],
                "exit_conditions": ["session_complete"],
                "pacing_config": {"stall_threshold_seconds": 120},
                "audience_targets": ["all"],
                "mini_games": [],
            },
        ],
        "beat_graph": {
            "introduction": ["investigation"],
            "investigation": ["reveal"],
            "reveal": [],
        },
        "generative_elements": {
            "killer_assignment": True,
            "character_generation": True,
            "clue_content": True,
            "narrator_dialogue": True,
        },
        "content_rails": {
            "prohibited_categories": ["csam", "graphic_violence"],
            "thematic_warnings": ["murder_mystery"],
            "age_floor": 18,
        },
        "knowledge_rules": {
            "killer_knows_they_did_it": True,
            "narrator_omniscient": True,
            "clues_private_until_shared": True,
        },
        "pacing_config": {
            "stall_threshold": 0.25,
            "misdirection_threshold": 0.80,
            "premium_threshold": 0.85,
            "w_time": 0.3,
            "w_action": 0.3,
            "w_suspicion": 0.2,
            "w_coverage": 0.2,
        },
        "victim_config": {
            "eligibility_mode": "player_count_governed",
        },
        "kill_config": {
            "base_kills": 1,
        },
        "murder_timing_range": [1, 3],
        "session_duration_range": [30, 75],
        "revelation_step_range": [2, 4],
        "tone_config": {
            "voice_directive": "Wit-first ensemble mystery.",
        },
    }


def assert_invalid(payload: dict, message: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        ArcDefinition.model_validate(payload)
    assert message in str(exc_info.value)


def test_valid_arc_payload_validates() -> None:
    arc = ArcDefinition.model_validate(valid_arc_payload())

    assert arc.arc_id == "test_arc"
    assert arc.aesthetic_config.selection_model["era"].type == "host_select"
    assert arc.pacing_config.w_time == 0.3


def test_missing_required_field_is_rejected() -> None:
    payload = valid_arc_payload()
    del payload["arc_id"]

    assert_invalid(payload, "Field required")


@pytest.mark.parametrize(
    "section",
    [
        "generative_elements",
        "content_rails",
        "knowledge_rules",
    ],
)
def test_missing_required_arc_sections_are_rejected(section: str) -> None:
    payload = valid_arc_payload()
    del payload[section]

    assert_invalid(payload, "Field required")


def test_invalid_beat_graph_reference_is_rejected() -> None:
    payload = valid_arc_payload()
    payload["beat_graph"]["introduction"] = ["missing_beat"]

    assert_invalid(payload, "beat_graph references undefined beat ids")


def test_invalid_player_count_order_is_rejected() -> None:
    payload = valid_arc_payload()
    payload["min_players"] = 11
    payload["max_players"] = 10

    assert_invalid(payload, "min_players cannot exceed max_players")


def test_invalid_pacing_weight_sum_is_rejected() -> None:
    payload = valid_arc_payload()
    payload["pacing_config"]["w_coverage"] = 0.9

    assert_invalid(payload, "pacing weights must sum to 1.0")


def test_invalid_narrator_trigger_is_rejected() -> None:
    payload = valid_arc_payload()
    payload["narrator"]["behavior_triggers"] = ["beat_transition", "bad_trigger"]

    assert_invalid(payload, "invalid narrator behavior triggers")


def test_invalid_generative_element_key_is_rejected() -> None:
    payload = valid_arc_payload()
    payload["generative_elements"]["unsupported_element"] = True

    assert_invalid(payload, "Extra inputs are not permitted")


def test_authored_mode_requires_characters() -> None:
    payload = valid_arc_payload()
    payload["character_mode"] = "authored"
    payload["characters"] = []

    assert_invalid(payload, "authored character mode requires at least one character")


def test_imposter_mode_requires_three_players() -> None:
    payload = valid_arc_payload()
    payload["min_players"] = 2

    assert_invalid(payload, "imposter play mode requires at least 3 players")


def test_legacy_aesthetic_mode_is_migrated_for_minimal_fixtures() -> None:
    payload = deepcopy(valid_arc_payload())
    del payload["aesthetic_config"]
    payload["aesthetic_mode"] = "fixed"

    arc = ArcDefinition.model_validate(payload)

    assert arc.aesthetic_config.asset_generation["legacy_mode"] == "fixed"
