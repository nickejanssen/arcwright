"""Knowledge-constrained character dialogue generation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from engine.characters.context import (
    CharacterGenerationContext,
    KnownFactContext,
    RelationshipDispositionContext,
    UnknownFactContext,
    build_character_generation_context,
)
from engine.db.orm import Event
from engine.routing import generate
from engine.safety import (
    L1_HARD_STOP_SENTINEL,
    L2_BLOCK_SENTINEL,
    L3_BLOCK_SENTINEL,
)

if TYPE_CHECKING:
    from engine.arc.models import ContentRailsConfig


@dataclass(frozen=True)
class CharacterDialogueEvent:
    event_id: UUID
    session_id: UUID
    actor_character_id: UUID | None
    event_type: str
    target_audience: str
    target_player_id: UUID | None
    content: str
    payload: dict[str, Any]


class KnowledgeConstraintViolation(ValueError):
    """Raised when generated dialogue contains a fact the character does not know."""


async def generate_character_dialogue(
    db_session: AsyncSession,
    *,
    session_id: UUID,
    character_id: UUID,
    player_input: str,
    quality_tier: str,
    target_audience: str = "all",
    target_player_id: UUID | None = None,
    current_beat_id: str | None = None,
    scene_goal: str | None = None,
    temperature: float = 0.7,
    tension_score: float | None = None,
    safety_policy_context: dict[str, Any] | str | None = None,
    content_rails: "ContentRailsConfig | None" = None,
    nightcap_mode: bool = False,
) -> CharacterDialogueEvent:
    """Generate one dialogue response after assembling knowledge constraints."""
    context = await build_character_generation_context(
        db_session,
        session_id=session_id,
        character_id=character_id,
    )
    messages = build_dialogue_messages(
        context,
        player_input=player_input,
        current_beat_id=current_beat_id,
        scene_goal=scene_goal,
    )

    result = await generate(
        db_session,
        session_id=session_id,
        task_type="character_dialogue",
        quality_tier=quality_tier,
        messages=messages,
        temperature=temperature,
        tension_score=tension_score,
        safety_policy_context=safety_policy_context,
        content_rails=content_rails,
        nightcap_mode=nightcap_mode,
    )

    if _is_safety_blocked_result(result.model_used):
        payload = _build_base_payload(
            context,
            target_audience=target_audience,
            target_player_id=target_player_id,
            quality_tier=quality_tier,
            current_beat_id=current_beat_id,
        )
        payload["safety_blocked"] = True
        payload["safety_layer"] = _safety_layer_from_sentinel(result.model_used)
        event = Event(
            session_id=session_id,
            actor_char_id=None,
            event_type="dialogue_blocked",
            payload=payload,
            content_text=None,
        )
        db_session.add(event)
        await db_session.flush()

        return CharacterDialogueEvent(
            event_id=event.event_id,
            session_id=session_id,
            actor_character_id=None,
            event_type="dialogue_blocked",
            target_audience=target_audience,
            target_player_id=target_player_id,
            content=result.content,
            payload=payload,
        )

    leaked_fact = find_unknown_fact_leak(result.content, context.unknown_facts)
    if leaked_fact is not None:
        raise KnowledgeConstraintViolation(
            f"dialogue referenced unknown fact {leaked_fact.fact_id}"
        )

    payload = _build_base_payload(
        context,
        target_audience=target_audience,
        target_player_id=target_player_id,
        quality_tier=quality_tier,
        current_beat_id=current_beat_id,
    )
    event = Event(
        session_id=session_id,
        actor_char_id=character_id,
        event_type="dialogue",
        payload=payload,
        content_text=result.content,
    )
    db_session.add(event)
    await db_session.flush()

    return CharacterDialogueEvent(
        event_id=event.event_id,
        session_id=session_id,
        actor_character_id=character_id,
        event_type="dialogue",
        target_audience=target_audience,
        target_player_id=target_player_id,
        content=result.content,
        payload=payload,
    )


def build_dialogue_messages(
    context: CharacterGenerationContext,
    *,
    player_input: str,
    current_beat_id: str | None = None,
    scene_goal: str | None = None,
) -> list[dict[str, Any]]:
    """Build prompt messages with explicit known and not-known blocks."""
    system_prompt = "\n\n".join(
        (
            _format_identity_block(context),
            _format_known_block(context.known_facts),
            _format_not_known_block(context.unknown_facts),
            _format_relationship_block(context.relationship_dispositions),
            _format_scene_block(current_beat_id, scene_goal),
        )
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": player_input},
    ]


def find_unknown_fact_leak(
    dialogue: str,
    unknown_facts: tuple[UnknownFactContext, ...],
) -> UnknownFactContext | None:
    """Return the first unknown fact whose content appears in generated dialogue."""
    normalized_dialogue = _normalize_text(dialogue)
    for fact in unknown_facts:
        for phrase in _fact_value_strings(fact.fact_content):
            normalized_phrase = _normalize_text(phrase)
            if _contains_normalized_phrase(normalized_dialogue, normalized_phrase):
                return fact
    return None


def _build_base_payload(
    context: CharacterGenerationContext,
    *,
    target_audience: str,
    target_player_id: UUID | None,
    quality_tier: str,
    current_beat_id: str | None,
) -> dict[str, Any]:
    return {
        "target_audience": target_audience,
        "target_player_id": str(target_player_id) if target_player_id else None,
        "task_type": "character_dialogue",
        "quality_tier": quality_tier,
        "current_beat_id": current_beat_id,
        "knowledge_constraint": {
            "known_fact_ids": [str(fact.fact_id) for fact in context.known_facts],
            "unknown_fact_ids": [str(fact.fact_id) for fact in context.unknown_facts],
        },
    }


def _is_safety_blocked_result(model_used: str) -> bool:
    return model_used in {
        L1_HARD_STOP_SENTINEL,
        L2_BLOCK_SENTINEL,
        L3_BLOCK_SENTINEL,
    }


def _safety_layer_from_sentinel(model_used: str) -> str:
    if model_used == L1_HARD_STOP_SENTINEL:
        return "L1"
    if model_used == L2_BLOCK_SENTINEL:
        return "L2"
    if model_used == L3_BLOCK_SENTINEL:
        return "L3"
    return "unknown"


def _format_identity_block(context: CharacterGenerationContext) -> str:
    profile = context.behavior_profile
    return "\n".join(
        (
            "[CHARACTER IDENTITY AND PERSONALITY]",
            f"character_id: {context.character_id}",
            f"is_ai_controlled: {context.is_ai_controlled}",
            f"personality: {_stable_json(profile.personality)}",
            f"goals: {_stable_json(list(profile.goals))}",
            f"secrets: {_stable_json(list(profile.secrets))}",
            f"tells: {_stable_json(list(profile.tells))}",
            "[END CHARACTER IDENTITY AND PERSONALITY]",
        )
    )


def _format_known_block(known_facts: tuple[KnownFactContext, ...]) -> str:
    lines = [
        "[KNOWN KNOWLEDGE CONSTRAINTS]",
        "The character may speak from, imply, and act on these facts.",
    ]
    if not known_facts:
        lines.append("No known facts are currently available to this character.")
    for fact in known_facts:
        lines.append(
            "- "
            f"fact_id={fact.fact_id}; "
            f"fact_type={fact.fact_type}; "
            f"confidence={fact.confidence}; "
            f"provenance_chain_length={fact.provenance_chain_length}; "
            f"content={_stable_json(fact.fact_content)}"
        )
    lines.append("[END KNOWN KNOWLEDGE CONSTRAINTS]")
    return "\n".join(lines)


def _format_not_known_block(unknown_facts: tuple[UnknownFactContext, ...]) -> str:
    lines = [
        "[NOT-KNOWN KNOWLEDGE CONSTRAINTS]",
        "The character must not state, imply, reveal, or act on these facts.",
    ]
    if not unknown_facts:
        lines.append("No session facts are outside this character's knowledge.")
    for fact in unknown_facts:
        lines.append(
            "- "
            f"fact_id={fact.fact_id}; "
            f"fact_type={fact.fact_type}; "
            f"content={_stable_json(fact.fact_content)}"
        )
    lines.append("[END NOT-KNOWN KNOWLEDGE CONSTRAINTS]")
    return "\n".join(lines)


def _format_relationship_block(
    relationships: tuple[RelationshipDispositionContext, ...],
) -> str:
    lines = ["[RELATIONSHIP CONTEXT]"]
    if not relationships:
        lines.append("No live relationship dispositions are available.")
    for relationship in relationships:
        lines.append(
            "- "
            f"target_character_id={relationship.target_character_id}; "
            f"trust={relationship.trust}; "
            f"history={relationship.history}; "
            f"current_affect={relationship.current_affect}"
        )
    lines.append("[END RELATIONSHIP CONTEXT]")
    return "\n".join(lines)


def _format_scene_block(current_beat_id: str | None, scene_goal: str | None) -> str:
    return "\n".join(
        (
            "[CURRENT SCENE]",
            f"current_beat_id: {current_beat_id}",
            f"scene_goal: {scene_goal}",
            "[END CURRENT SCENE]",
        )
    )


def _fact_value_strings(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, dict):
        values: list[str] = []
        for child in value.values():
            values.extend(_fact_value_strings(child))
        return tuple(values)
    if isinstance(value, list):
        values = []
        for child in value:
            values.extend(_fact_value_strings(child))
        return tuple(values)
    return ()


def _normalize_text(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", " ", value.casefold())
    return re.sub(r"\s+", " ", normalized).strip()


def _contains_normalized_phrase(text: str, phrase: str) -> bool:
    if not phrase:
        return False
    return f" {phrase} " in f" {text} "


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))
