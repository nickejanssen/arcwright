"""Knowledge-constrained character dialogue generation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from time import perf_counter
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from engine.case.models import AuthorizedFalsehood
from engine.characters.context import (
    CharacterGenerationContext,
    KnownFactContext,
    RelationshipDispositionContext,
    UnknownFactContext,
    build_character_generation_context,
)
from engine.characters.pressure import apply_per_question_pressure_boost
from engine.claims.matcher import match_answer_content
from engine.claims.models import ClaimRecord
from engine.claims.resolver import ClaimResolver
from engine.db.orm import Event
from engine.resources.models import EffectActivation
from engine.routing import generate
from engine.safety import (
    L1_HARD_STOP_SENTINEL,
    L2_BLOCK_SENTINEL,
    L3_BLOCK_SENTINEL,
)
from engine.telemetry.claims import record_answer_latency, record_claim_recorded

if TYPE_CHECKING:
    from engine.arc.models import AuthorialIntent, ContentRailsConfig
    from engine.events.models import ContentEvent


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


def to_content_event(event: CharacterDialogueEvent) -> "ContentEvent":
    """Convert a dialogue result into a bus-publishable ContentEvent.

    Used by the live loop (spec 0071) to deliver AI character responses on
    the session event stream. Blocked results ("dialogue_blocked") convert
    the same way: their content is the neutral bridge text, so players see
    a smooth redirect rather than a gap.
    """
    from datetime import datetime, timezone

    from engine.events.models import (
        AudienceTarget,
        ContentEvent,
        EventCategory,
    )

    target_audience = AudienceTarget(event.target_audience)
    return ContentEvent(
        event_id=event.event_id,
        session_id=event.session_id,
        timestamp=datetime.now(tz=timezone.utc),
        category=EventCategory.character_dialogue,
        event_type=event.event_type,
        actor_id=event.actor_character_id,
        target_audience=target_audience,
        target_player_id=(
            event.target_player_id
            if target_audience is AudienceTarget.specific_player
            else None
        ),
        payload={
            "text": event.content,
            "character_id": (
                str(event.actor_character_id) if event.actor_character_id else None
            ),
        },
    )


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
    social_pressure: float | None = None,
    authorial_intent: "AuthorialIntent | None" = None,
    tone_config: dict[str, Any] | None = None,
    authorized_falsehoods: list[AuthorizedFalsehood] | None = None,
    authorized_falsehood_speaker_id: str | None = None,
    question_topic: str | None = None,
    asker_participant_id: UUID | None = None,
    round_index: int = 0,
    interaction_window_id: str | None = None,
    pressure_activation: EffectActivation | None = None,
    pressure_effect_key: str | None = None,
    # Starting tuning value; Rehearsal 1 telemetry should retune it.
    pressure_boost: float = 0.25,
) -> CharacterDialogueEvent:
    """Generate one dialogue response after assembling knowledge constraints."""
    generation_started = perf_counter()
    context = await build_character_generation_context(
        db_session,
        session_id=session_id,
        character_id=character_id,
        authorized_falsehoods=authorized_falsehoods,
        authorized_falsehood_speaker_id=authorized_falsehood_speaker_id,
    )
    matched_answer: AuthorizedFalsehood | None = None
    if question_topic is not None:
        falsehood_models = [
            AuthorizedFalsehood(
                falsehood_id=falsehood.falsehood_id,
                speaker_id=falsehood.speaker_id,
                topic=falsehood.topic,
                claim_text=falsehood.claim_text,
                contradicted_by=list(falsehood.contradicted_by),
            )
            for falsehood in context.authorized_falsehoods
        ]
        match = match_answer_content(
            topic=question_topic,
            falsehoods=falsehood_models,
            known_facts=context.known_facts,
        )
        if isinstance(match, AuthorizedFalsehood):
            matched_answer = match
    effective_social_pressure = social_pressure
    if pressure_activation is not None and pressure_effect_key is not None:
        effective_social_pressure = apply_per_question_pressure_boost(
            social_pressure,
            activation=pressure_activation,
            target_id=character_id,
            pressure_effect_key=pressure_effect_key,
            boost=pressure_boost,
        )
    messages = build_dialogue_messages(
        context,
        player_input=player_input,
        current_beat_id=current_beat_id,
        scene_goal=scene_goal,
        social_pressure=effective_social_pressure,
        authorial_intent=authorial_intent,
        tone_config=tone_config,
        matched_answer=matched_answer,
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
    )
    await record_answer_latency(
        db_session,
        session_id,
        latency_ms=(perf_counter() - generation_started) * 1000.0,
        quality_tier=quality_tier,
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

    delivered_content = _ensure_authorized_falsehood_text(
        result.content, matched_answer
    )
    leaked_fact = find_unknown_fact_leak(delivered_content, context.unknown_facts)
    if leaked_fact is not None:
        raise KnowledgeConstraintViolation(
            f"dialogue referenced unknown fact {leaked_fact.fact_id}"
        )

    claim = ClaimRecord(
        speaker_id=str(character_id),
        asker_id=(str(asker_participant_id) if asker_participant_id else None),
        round_index=round_index,
        beat_id=current_beat_id or "dialogue",
        interaction_window_id=interaction_window_id or "dialogue",
        claim_text=delivered_content,
        referenced_fact_ids=tuple(str(fact.fact_id) for fact in context.known_facts),
        is_authorized_lie=matched_answer is not None,
        falsehood_id=matched_answer.falsehood_id if matched_answer else None,
    )
    claim = await ClaimResolver(session_id=session_id).record_claim(
        db_session, claim=claim
    )
    await record_claim_recorded(db_session, session_id, claim)

    payload = _build_base_payload(
        context,
        target_audience=target_audience,
        target_player_id=target_player_id,
        quality_tier=quality_tier,
        current_beat_id=current_beat_id,
        claim_id=claim.claim_id,
    )
    event = Event(
        session_id=session_id,
        actor_char_id=character_id,
        event_type="dialogue",
        payload=payload,
        content_text=delivered_content,
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
        content=delivered_content,
        payload=payload,
    )


def build_dialogue_messages(
    context: CharacterGenerationContext,
    *,
    player_input: str,
    current_beat_id: str | None = None,
    scene_goal: str | None = None,
    social_pressure: float | None = None,
    authorial_intent: "AuthorialIntent | None" = None,
    tone_config: dict[str, Any] | None = None,
    matched_answer: AuthorizedFalsehood | None = None,
) -> list[dict[str, Any]]:
    """Build prompt messages with explicit known and not-known blocks."""
    blocks = [
        _format_identity_block(context),
    ]
    voice_block = format_voice_block(tone_config) if tone_config else None
    if voice_block is not None:
        # Arc-stable voice contract (D-069/AW-276). Lives in the cacheable
        # stable region alongside identity and authorial intent.
        blocks.append(voice_block)
    if authorial_intent is not None:
        # Arc-stable authoring context. Placed in the stable region of the
        # system prompt so it lives inside the cacheable context layer
        # (spec 0064; prompt-caching requirement).
        blocks.append(_format_authorial_intent_block(authorial_intent))
    blocks.extend(
        (
            _format_known_block(context.known_facts),
            _format_not_known_block(context.unknown_facts),
            _format_relationship_block(context.relationship_dispositions),
        )
    )
    if matched_answer is not None:
        blocks.append(_format_lie_block(matched_answer))
    if (
        social_pressure is not None
        and social_pressure >= context.behavior_profile.crumble_threshold
    ):
        blocks.append(
            _format_pressure_block(
                social_pressure, context.behavior_profile.crumble_threshold
            )
        )
    blocks.append(_format_scene_block(current_beat_id, scene_goal))
    return [
        {"role": "system", "content": "\n\n".join(blocks)},
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
    claim_id: str | None = None,
) -> dict[str, Any]:
    return {
        "target_audience": target_audience,
        "target_player_id": str(target_player_id) if target_player_id else None,
        "task_type": "character_dialogue",
        "quality_tier": quality_tier,
        "current_beat_id": current_beat_id,
        "claim_id": claim_id,
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


def format_voice_block(tone_config: dict[str, Any] | None) -> str | None:
    """Render the arc's voice directive and tone parameters as a prompt block.

    The block is static for the lifetime of an arc definition, so it belongs
    in the cacheable stable region of any player-facing generation prompt.
    Returns None when the arc declares no usable voice content, so callers
    can omit the block entirely.
    """
    if not tone_config:
        return None
    lines = ["[VOICE]"]
    directive = tone_config.get("voice_directive")
    if isinstance(directive, str) and directive.strip():
        lines.append(f"voice directive: {directive.strip()}")
    defaults = tone_config.get("scenario_defaults")
    if isinstance(defaults, dict) and defaults:
        lines.append("tone parameters (0.0-1.0):")
        for key in sorted(defaults):
            lines.append(f"- {key}: {defaults[key]}")
    if len(lines) == 1:
        return None
    lines.append("[END VOICE]")
    return "\n".join(lines)


def _format_authorial_intent_block(intent: "AuthorialIntent") -> str:
    """Render the arc author's declared theme, tone, and tension curve.

    The block is static for the lifetime of an arc definition, so it can sit
    in the cacheable stable region of the system prompt. It is guidance for
    generation only; it never encodes state.
    """
    lines = [
        "[AUTHORIAL INTENT]",
        f"theme: {intent.theme}",
        f"tone: {intent.tone}",
    ]
    if intent.emotional_targets:
        lines.append("intended emotional progression (beat: target tension 0.0-1.0):")
        for target in intent.emotional_targets:
            entry = f"- {target.beat_id}: {target.target_tension}"
            if target.note:
                entry += f" ({target.note})"
            lines.append(entry)
    lines.append("[END AUTHORIAL INTENT]")
    return "\n".join(lines)


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


def _format_pressure_block(social_pressure: float, crumble_threshold: float) -> str:
    return "\n".join(
        (
            "[SOCIAL PRESSURE]",
            f"social_pressure: {social_pressure:.2f}",
            f"crumble_threshold: {crumble_threshold:.2f}",
            "Your concealment is showing strain under accumulated suspicion.",
            "Express this through over-precise answers, more aggressive deflection, and small errors consistent with your tells.",
            "Do not confess. Become more yourself under stress.",
            "[END SOCIAL PRESSURE]",
        )
    )


def _format_lie_block(falsehood: AuthorizedFalsehood) -> str:
    return "\n".join(
        (
            "[AUTHORIZED FALSEHOOD]",
            f"topic: {falsehood.topic}",
            f"claim_text (render verbatim): {falsehood.claim_text}",
            "Use a subtle delivery tell: be slightly less specific, slightly too smooth, or add a small hedge.",
            "The tell is flavor only and is never a substitute for deterministic contradiction detection.",
            "[END AUTHORIZED FALSEHOOD]",
        )
    )


def _ensure_authorized_falsehood_text(
    content: str, falsehood: AuthorizedFalsehood | None
) -> str:
    """Keep the authored lie text verbatim in the delivered answer."""
    if falsehood is None or falsehood.claim_text in content:
        return content
    separator = " " if content and not content.endswith((" ", "\n")) else ""
    return f"{content}{separator}{falsehood.claim_text}"


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
