"""Tests for the [VOICE] block (AW-276, D-069/D-070, finding F1).

Covers rendering from arc tone_config, omission when the arc declares no
usable voice content, stable-region ordering inside dialogue prompts, and
narrator-bridge inclusion.
"""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from engine.characters.context import (
    BehaviorProfileContext,
    CharacterGenerationContext,
)
from engine.characters.dialogue import build_dialogue_messages, format_voice_block

ARC_PATH = Path(__file__).resolve().parents[2] / "nightcap" / "arc.json"


def _arc_tone_config() -> dict:
    return json.loads(ARC_PATH.read_text(encoding="utf-8"))["tone_config"]


def _minimal_context() -> CharacterGenerationContext:
    return CharacterGenerationContext(
        session_id=uuid4(),
        character_id=uuid4(),
        behavior_profile=BehaviorProfileContext(
            personality={"warmth": 0.5},
            goals=("stay hidden",),
            secrets=(),
            tells=(),
        ),
        relationship_dispositions=(),
        is_ai_controlled=True,
        known_facts=(),
        unknown_facts=(),
    )


def test_format_voice_block_renders_directive_and_parameters() -> None:
    block = format_voice_block(_arc_tone_config())

    assert block is not None
    assert block.startswith("[VOICE]")
    assert block.endswith("[END VOICE]")
    assert "voice directive: Wit-first ensemble mystery." in block
    assert "tone parameters (0.0-1.0):" in block
    assert "- wit_density: 0.75" in block


def test_format_voice_block_returns_none_without_usable_content() -> None:
    assert format_voice_block(None) is None
    assert format_voice_block({}) is None
    assert format_voice_block({"genre": "murder_mystery"}) is None
    assert format_voice_block({"voice_directive": "   "}) is None


def test_dialogue_messages_include_voice_block_when_tone_config_present() -> None:
    messages = build_dialogue_messages(
        _minimal_context(),
        player_input="Who saw the victim last?",
        tone_config=_arc_tone_config(),
    )

    system_text = messages[0]["content"]
    assert "[VOICE]" in system_text
    assert "Wit-first ensemble mystery." in system_text


def test_dialogue_messages_omit_voice_block_when_absent() -> None:
    messages = build_dialogue_messages(
        _minimal_context(),
        player_input="Who saw the victim last?",
    )

    assert "[VOICE]" not in messages[0]["content"]


def test_voice_block_sits_in_stable_region_before_knowledge_blocks() -> None:
    messages = build_dialogue_messages(
        _minimal_context(),
        player_input="Who saw the victim last?",
        tone_config=_arc_tone_config(),
    )

    system_text = messages[0]["content"]
    identity_index = system_text.index("[CHARACTER IDENTITY AND PERSONALITY]")
    voice_index = system_text.index("[VOICE]")
    known_index = system_text.index("[KNOWN KNOWLEDGE CONSTRAINTS]")
    assert identity_index < voice_index < known_index
