"""Tests for AW-246: per-character social pressure compute, scheduler wiring,
and prompt assembly integration."""

from __future__ import annotations

from uuid import uuid4

import pytest

from engine.characters.context import BehaviorProfileContext, CharacterGenerationContext
from engine.characters.dialogue import build_dialogue_messages
from engine.characters.initiative import (
    CharacterInitiativeProfile,
    InitiativeScheduler,
    InitiativeSessionState,
    build_npc_npc_messages,
    modulate_threshold_for_pressure,
)
from engine.characters.pressure import (
    SocialPressureSignals,
    SocialPressureWeights,
    compute_social_pressure,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_context(crumble_threshold: float = 1.0) -> CharacterGenerationContext:
    profile = BehaviorProfileContext(
        personality={"traits": ["evasive"]},
        goals=("Protect the secret",),
        secrets=({"content": "the truth", "crumble_threshold": crumble_threshold},),
        tells=("Pauses when nervous",),
        crumble_threshold=crumble_threshold,
    )
    return CharacterGenerationContext(
        session_id=uuid4(),
        character_id=uuid4(),
        behavior_profile=profile,
        relationship_dispositions=(),
        is_ai_controlled=True,
        known_facts=(),
        unknown_facts=(),
    )


# ---------------------------------------------------------------------------
# compute_social_pressure — weighted sum
# ---------------------------------------------------------------------------


def test_compute_social_pressure_weighted_sum_matches_spec() -> None:
    # §7.4: accusations*0.5 + directed_questions*0.3 + alliance_isolation*0.2
    signals = SocialPressureSignals(
        accusation_weight=0.8,
        question_intensity=0.6,
        alliance_isolation=0.4,
    )
    result = compute_social_pressure(signals)
    expected = 0.8 * 0.5 + 0.6 * 0.3 + 0.4 * 0.2
    assert result == pytest.approx(expected)


def test_compute_social_pressure_clamps_to_one() -> None:
    signals = SocialPressureSignals(
        accusation_weight=1.0,
        question_intensity=1.0,
        alliance_isolation=1.0,
    )
    assert compute_social_pressure(signals) == pytest.approx(1.0)


def test_compute_social_pressure_all_zero_returns_zero() -> None:
    signals = SocialPressureSignals(
        accusation_weight=0.0,
        question_intensity=0.0,
        alliance_isolation=0.0,
    )
    assert compute_social_pressure(signals) == pytest.approx(0.0)


def test_compute_social_pressure_gaze_signal_zero_weighted_by_default() -> None:
    signals_no_gaze = SocialPressureSignals(
        accusation_weight=0.5,
        question_intensity=0.5,
        alliance_isolation=0.5,
        gaze_signal=0.0,
    )
    signals_with_gaze = SocialPressureSignals(
        accusation_weight=0.5,
        question_intensity=0.5,
        alliance_isolation=0.5,
        gaze_signal=1.0,
    )
    # Default weights give gaze_signal weight 0.0 — should produce same score
    assert compute_social_pressure(signals_no_gaze) == pytest.approx(
        compute_social_pressure(signals_with_gaze)
    )


def test_compute_social_pressure_custom_weights_applied() -> None:
    signals = SocialPressureSignals(
        accusation_weight=1.0,
        question_intensity=0.0,
        alliance_isolation=0.0,
        gaze_signal=1.0,
    )
    weights = SocialPressureWeights(
        accusation=0.25,
        directed_questions=0.25,
        alliance_isolation=0.25,
        gaze_signal=0.25,
    )
    result = compute_social_pressure(signals, weights)
    assert result == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# modulate_threshold_for_pressure
# ---------------------------------------------------------------------------


def test_modulate_threshold_zero_pressure_unchanged() -> None:
    assert modulate_threshold_for_pressure(0.6, 0.0) == pytest.approx(0.6)


def test_modulate_threshold_full_pressure_collapses_to_zero() -> None:
    assert modulate_threshold_for_pressure(0.6, 1.0) == pytest.approx(0.0)


def test_modulate_threshold_proportional_reduction() -> None:
    # 0.6 * (1 - 0.5) = 0.3
    assert modulate_threshold_for_pressure(0.6, 0.5) == pytest.approx(0.3)


def test_modulate_threshold_never_negative() -> None:
    assert modulate_threshold_for_pressure(0.3, 2.0) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# InitiativeScheduler — social pressure modulates effective threshold
# ---------------------------------------------------------------------------


def test_scheduler_social_pressure_lowers_threshold_enabling_action() -> None:
    scheduler = InitiativeScheduler()
    actor_id = uuid4()
    state = InitiativeSessionState(
        seconds_since_last_player_action=30.0,
        current_beat_id="the_dig",
        tension_score=0.0,
    )
    # score = 0.6 * 0.5 + 0.4 * 0.0 = 0.30
    profile = CharacterInitiativeProfile(
        character_id=actor_id,
        is_ai_controlled=True,
        initiative_threshold=0.6,
    )

    # Without pressure: score 0.30 < threshold 0.60 → no action
    assert scheduler.evaluate([profile], state) == []

    # With full pressure: threshold collapses to 0.0 → action produced
    actions = scheduler.evaluate(
        [profile],
        state,
        social_pressure_by_character={actor_id: 1.0},
    )
    assert len(actions) == 1
    assert actions[0].initiating_character_id == actor_id


def test_scheduler_no_social_pressure_preserves_aw213_behavior() -> None:
    scheduler = InitiativeScheduler()
    actor_id = uuid4()
    state = InitiativeSessionState(
        seconds_since_last_player_action=120.0,
        current_beat_id="the_dig",
        tension_score=0.9,
    )
    profile = CharacterInitiativeProfile(
        character_id=actor_id,
        is_ai_controlled=True,
        initiative_threshold=0.6,
    )
    # AW-213 callers pass no social_pressure_by_character — behavior must be identical
    actions = scheduler.evaluate([profile], state)
    assert len(actions) == 1
    assert actions[0].initiative_score >= 0.6


def test_scheduler_pressure_zero_for_absent_character_has_no_effect() -> None:
    scheduler = InitiativeScheduler()
    actor_id = uuid4()
    other_id = uuid4()
    state = InitiativeSessionState(
        seconds_since_last_player_action=5.0,
        current_beat_id="the_dig",
        tension_score=0.0,
    )
    profile = CharacterInitiativeProfile(
        character_id=actor_id,
        is_ai_controlled=True,
        initiative_threshold=0.6,
    )
    # Pressure map exists but actor not in it — defaults to 0.0, no modulation
    actions = scheduler.evaluate(
        [profile],
        state,
        social_pressure_by_character={other_id: 1.0},
    )
    assert actions == []


# ---------------------------------------------------------------------------
# Prompt assembly — pressure block at/above crumble_threshold
# ---------------------------------------------------------------------------


def test_build_dialogue_messages_pressure_block_included_at_threshold() -> None:
    context = _make_context(crumble_threshold=0.7)
    messages = build_dialogue_messages(
        context,
        player_input="Where were you?",
        social_pressure=0.7,
    )
    system_prompt = messages[0]["content"]
    assert "[SOCIAL PRESSURE]" in system_prompt
    assert "[END SOCIAL PRESSURE]" in system_prompt


def test_build_dialogue_messages_pressure_block_included_above_threshold() -> None:
    context = _make_context(crumble_threshold=0.7)
    messages = build_dialogue_messages(
        context,
        player_input="Where were you?",
        social_pressure=0.95,
    )
    system_prompt = messages[0]["content"]
    assert "[SOCIAL PRESSURE]" in system_prompt


def test_build_dialogue_messages_pressure_block_absent_below_threshold() -> None:
    context = _make_context(crumble_threshold=0.7)
    messages = build_dialogue_messages(
        context,
        player_input="Where were you?",
        social_pressure=0.69,
    )
    system_prompt = messages[0]["content"]
    assert "[SOCIAL PRESSURE]" not in system_prompt


def test_build_dialogue_messages_no_pressure_arg_no_block() -> None:
    context = _make_context(crumble_threshold=0.5)
    messages = build_dialogue_messages(
        context,
        player_input="Where were you?",
    )
    system_prompt = messages[0]["content"]
    assert "[SOCIAL PRESSURE]" not in system_prompt


def test_build_dialogue_messages_existing_blocks_always_present() -> None:
    context = _make_context(crumble_threshold=0.7)
    messages = build_dialogue_messages(
        context,
        player_input="Where were you?",
        social_pressure=0.9,
    )
    system_prompt = messages[0]["content"]
    assert "[CHARACTER IDENTITY AND PERSONALITY]" in system_prompt
    assert "[KNOWN KNOWLEDGE CONSTRAINTS]" in system_prompt
    assert "[NOT-KNOWN KNOWLEDGE CONSTRAINTS]" in system_prompt
    assert "[RELATIONSHIP CONTEXT]" in system_prompt
    assert "[CURRENT SCENE]" in system_prompt


def test_build_dialogue_messages_pressure_block_before_scene_block() -> None:
    context = _make_context(crumble_threshold=0.5)
    messages = build_dialogue_messages(
        context,
        player_input="Where were you?",
        social_pressure=0.8,
    )
    system_prompt = messages[0]["content"]
    pressure_pos = system_prompt.index("[SOCIAL PRESSURE]")
    scene_pos = system_prompt.index("[CURRENT SCENE]")
    assert pressure_pos < scene_pos


# ---------------------------------------------------------------------------
# build_npc_npc_messages — pressure block for speaker
# ---------------------------------------------------------------------------


def test_build_npc_npc_messages_speaker_pressure_above_threshold() -> None:
    speaker = _make_context(crumble_threshold=0.6)
    partner = _make_context(crumble_threshold=0.6)
    messages = build_npc_npc_messages(
        speaker_context=speaker,
        partner_context=partner,
        current_beat_id="the_dig",
        scene_goal=None,
        prior_turns=[],
        speaker_social_pressure=0.8,
    )
    system_prompt = messages[0]["content"]
    assert "[SOCIAL PRESSURE]" in system_prompt


def test_build_npc_npc_messages_speaker_pressure_below_threshold() -> None:
    speaker = _make_context(crumble_threshold=0.6)
    partner = _make_context(crumble_threshold=0.6)
    messages = build_npc_npc_messages(
        speaker_context=speaker,
        partner_context=partner,
        current_beat_id="the_dig",
        scene_goal=None,
        prior_turns=[],
        speaker_social_pressure=0.3,
    )
    system_prompt = messages[0]["content"]
    assert "[SOCIAL PRESSURE]" not in system_prompt


def test_build_npc_npc_messages_no_pressure_arg_no_block() -> None:
    speaker = _make_context(crumble_threshold=0.1)
    partner = _make_context(crumble_threshold=0.1)
    messages = build_npc_npc_messages(
        speaker_context=speaker,
        partner_context=partner,
        current_beat_id="the_dig",
        scene_goal=None,
        prior_turns=[],
    )
    system_prompt = messages[0]["content"]
    assert "[SOCIAL PRESSURE]" not in system_prompt


# ---------------------------------------------------------------------------
# BehaviorProfileContext crumble_threshold extraction
# ---------------------------------------------------------------------------


def test_crumble_threshold_default_one_when_no_secrets_have_threshold() -> None:
    from engine.characters.context import _build_behavior_profile_context

    profile = _build_behavior_profile_context(
        {"secrets": [{"content": "hidden thing"}]}
    )
    assert profile.crumble_threshold == pytest.approx(1.0)


def test_crumble_threshold_reads_minimum_across_secrets() -> None:
    from engine.characters.context import _build_behavior_profile_context

    profile = _build_behavior_profile_context(
        {
            "secrets": [
                {"content": "a", "crumble_threshold": 0.8},
                {"content": "b", "crumble_threshold": 0.4},
            ]
        }
    )
    assert profile.crumble_threshold == pytest.approx(0.4)


def test_crumble_threshold_default_one_when_no_secrets() -> None:
    from engine.characters.context import _build_behavior_profile_context

    profile = _build_behavior_profile_context({})
    assert profile.crumble_threshold == pytest.approx(1.0)
