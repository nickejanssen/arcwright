"""Tests for AW-247: killer tell tier selection by group size.

Covers select_active_tells thresholds, _build_behavior_profile_context integration,
and _format_identity_block prompt assembly for tier-annotated tells.
"""

from __future__ import annotations

from uuid import uuid4

from engine.characters.context import (
    BehaviorProfileContext,
    CharacterGenerationContext,
    _build_behavior_profile_context,
    select_active_tells,
)
from engine.characters.dialogue import _format_identity_block

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_TIERED_TELLS: list[object] = [
    {"text": "surface tell", "tier": "surface"},
    {"text": "mid tell", "tier": "mid"},
    {"text": "deep tell", "tier": "deep"},
]


def _context_with_tells(tells: tuple[str, ...]) -> CharacterGenerationContext:
    return CharacterGenerationContext(
        session_id=uuid4(),
        character_id=uuid4(),
        behavior_profile=BehaviorProfileContext(
            personality={},
            goals=(),
            secrets=(),
            tells=tells,
        ),
        relationship_dispositions=(),
        is_ai_controlled=True,
        known_facts=(),
        unknown_facts=(),
    )


# ---------------------------------------------------------------------------
# select_active_tells — pure unit tests
# ---------------------------------------------------------------------------


def test_select_active_tells_plain_strings_always_included() -> None:
    tells_raw = ["plain tell one", "plain tell two"]
    assert select_active_tells(tells_raw, player_count=4) == (
        "plain tell one",
        "plain tell two",
    )
    assert select_active_tells(tells_raw, player_count=8) == (
        "plain tell one",
        "plain tell two",
    )


def test_select_active_tells_all_tiers_active_at_small_group() -> None:
    result = select_active_tells(_TIERED_TELLS, player_count=4)
    assert "surface tell" in result
    assert "mid tell" in result
    assert "deep tell" in result


def test_select_active_tells_deep_absent_at_mid_group() -> None:
    result = select_active_tells(_TIERED_TELLS, player_count=5)
    assert "surface tell" in result
    assert "mid tell" in result
    assert "deep tell" not in result


def test_select_active_tells_only_surface_at_large_group() -> None:
    result = select_active_tells(_TIERED_TELLS, player_count=8)
    assert "surface tell" in result
    assert "mid tell" not in result
    assert "deep tell" not in result


def test_select_active_tells_produces_different_subsets_at_4_vs_8() -> None:
    small = select_active_tells(_TIERED_TELLS, player_count=4)
    large = select_active_tells(_TIERED_TELLS, player_count=8)
    assert small != large


def test_select_active_tells_mixed_plain_and_tiered() -> None:
    tells_raw: list[object] = [
        "plain tell",
        {"text": "deep tell", "tier": "deep"},
    ]
    at_8 = select_active_tells(tells_raw, player_count=8)
    assert "plain tell" in at_8
    assert "deep tell" not in at_8

    at_4 = select_active_tells(tells_raw, player_count=4)
    assert "plain tell" in at_4
    assert "deep tell" in at_4


def test_select_active_tells_empty_input() -> None:
    assert select_active_tells([], player_count=4) == ()
    assert select_active_tells([], player_count=8) == ()


def test_select_active_tells_zero_player_count_includes_all_tiers() -> None:
    result = select_active_tells(_TIERED_TELLS, player_count=0)
    assert "surface tell" in result
    assert "mid tell" in result
    assert "deep tell" in result


def test_select_active_tells_boundary_at_4_players() -> None:
    result = select_active_tells(_TIERED_TELLS, player_count=4)
    assert "deep tell" in result


def test_select_active_tells_boundary_at_7_players() -> None:
    result = select_active_tells(_TIERED_TELLS, player_count=7)
    assert "mid tell" in result
    assert "deep tell" not in result


# ---------------------------------------------------------------------------
# _build_behavior_profile_context — integration with player_count
# ---------------------------------------------------------------------------


def test_build_behavior_profile_context_filters_tells_by_player_count() -> None:
    profile_data = {
        "personality": {"traits": ["calm"]},
        "goals": ["survive"],
        "secrets": [],
        "tells": list(_TIERED_TELLS),
    }
    ctx_small = _build_behavior_profile_context(profile_data, player_count=4)
    ctx_large = _build_behavior_profile_context(profile_data, player_count=8)

    assert "deep tell" in ctx_small.tells
    assert "deep tell" not in ctx_large.tells
    assert "surface tell" in ctx_small.tells
    assert "surface tell" in ctx_large.tells


def test_build_behavior_profile_context_plain_string_tells_backward_compat() -> None:
    profile_data = {"tells": ["Mentions exact times without being asked"]}
    ctx_small = _build_behavior_profile_context(profile_data, player_count=4)
    ctx_large = _build_behavior_profile_context(profile_data, player_count=8)
    assert ctx_small.tells == ("Mentions exact times without being asked",)
    assert ctx_large.tells == ("Mentions exact times without being asked",)


def test_build_behavior_profile_context_no_tells_key() -> None:
    ctx = _build_behavior_profile_context({}, player_count=6)
    assert ctx.tells == ()


# ---------------------------------------------------------------------------
# _format_identity_block — below-threshold tiers excluded from prompt
# ---------------------------------------------------------------------------


def test_format_identity_block_excludes_below_threshold_tiers() -> None:
    # Simulate 8-player context: only surface tell survived tier selection
    context = _context_with_tells(("surface tell",))
    output = _format_identity_block(context)
    assert "surface tell" in output
    assert "deep tell" not in output
    assert "mid tell" not in output


def test_format_identity_block_includes_all_tiers_at_small_group() -> None:
    # Simulate 4-player context: all tiers survived selection
    context = _context_with_tells(("surface tell", "mid tell", "deep tell"))
    output = _format_identity_block(context)
    assert "surface tell" in output
    assert "mid tell" in output
    assert "deep tell" in output
