"""AI initiative scheduling and NPC-NPC exchange generation (AW-213)."""

from __future__ import annotations

import asyncio
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Literal
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from engine.characters.context import (
    CharacterGenerationContext,
    RelationshipDispositionContext,
    build_character_generation_context,
)
from engine.characters.dialogue import (
    CharacterDialogueEvent,
    KnowledgeConstraintViolation,
    _format_identity_block,
    _format_known_block,
    _format_not_known_block,
    _format_pressure_block,
    _format_relationship_block,
    _format_scene_block,
    find_unknown_fact_leak,
    generate_character_dialogue,
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


_DEFAULT_INITIATIVE_THRESHOLD = 0.6
_IDLE_NORMALIZATION_SECONDS = 60.0
_W_IDLE = 0.6
_W_TENSION = 0.4


@dataclass(frozen=True)
class CharacterInitiativeProfile:
    character_id: UUID
    is_ai_controlled: bool
    initiative_threshold: float = _DEFAULT_INITIATIVE_THRESHOLD


@dataclass(frozen=True)
class InitiativeSessionState:
    seconds_since_last_player_action: float
    current_beat_id: str
    tension_score: float


@dataclass(frozen=True)
class ScheduledInitiativeAction:
    initiating_character_id: UUID
    target_character_id: UUID | None
    target_type: Literal["npc", "player_group"]
    initiative_score: float


@dataclass(frozen=True)
class NpcNpcExchangeTurn:
    event_id: UUID
    actor_character_id: UUID
    content: str
    turn_index: int
    safety_blocked: bool = False
    safety_layer: str | None = None


@dataclass(frozen=True)
class NpcNpcExchangeEvent:
    exchange_id: UUID
    session_id: UUID
    initiating_character_id: UUID
    target_character_id: UUID
    turns: tuple[NpcNpcExchangeTurn, ...]


def compute_initiative_score(session_state: InitiativeSessionState) -> float:
    """Combine idle time and tension into a 0.0-1.0 initiative score."""
    normalized_idle = min(
        max(session_state.seconds_since_last_player_action, 0.0)
        / _IDLE_NORMALIZATION_SECONDS,
        1.0,
    )
    score = _W_IDLE * normalized_idle + _W_TENSION * session_state.tension_score
    return min(max(score, 0.0), 1.0)


def effective_initiative_threshold(
    character_profile: CharacterInitiativeProfile,
    threshold_overrides: dict[UUID, float] | None,
) -> float:
    """Return the per-call effective threshold for one character."""
    if (
        threshold_overrides is not None
        and character_profile.character_id in threshold_overrides
    ):
        return threshold_overrides[character_profile.character_id]
    return character_profile.initiative_threshold


def modulate_threshold_for_pressure(threshold: float, social_pressure: float) -> float:
    """Lower effective threshold proportionally to social pressure.

    High pressure makes characters more likely to act (deflect, redirect).
    """
    return max(0.0, threshold * (1.0 - social_pressure))


def select_initiative_target(
    *,
    initiating_character_id: UUID,
    eligible_target_ids: list[UUID],
    beat_character_emphasis: list[UUID] | None,
    relationships: list[RelationshipDispositionContext],
) -> UUID | None:
    """Pick an NPC target deterministically. Returns None when no AI target fits.

    Caller is responsible for passing ``relationships`` ordered by recency,
    most-recent first. Recency is read from list position, so a stable input
    order yields a stable output.
    """
    eligible_set = {
        target_id
        for target_id in eligible_target_ids
        if target_id != initiating_character_id
    }
    if not eligible_set:
        return None

    if beat_character_emphasis:
        emphasized = [
            target_id
            for target_id in beat_character_emphasis
            if target_id in eligible_set
        ]
        if emphasized:
            eligible_set = set(emphasized)

    relationship_by_target = {
        relationship.target_character_id: relationship for relationship in relationships
    }
    recency_index_by_target = {
        relationship.target_character_id: index
        for index, relationship in enumerate(relationships)
    }
    recency_floor = len(relationships)

    def sort_key(target_id: UUID) -> tuple[float, int, str]:
        relationship = relationship_by_target.get(target_id)
        strength = abs(relationship.trust - 0.5) if relationship is not None else -1.0
        recency = recency_index_by_target.get(target_id, recency_floor)
        return (-strength, recency, str(target_id))

    return min(eligible_set, key=sort_key)


class InitiativeScheduler:
    """Decide which AI characters should act on a given session tick."""

    def evaluate(
        self,
        character_profiles: list[CharacterInitiativeProfile],
        session_state: InitiativeSessionState,
        *,
        threshold_overrides: dict[UUID, float] | None = None,
        eligible_targets_by_character: dict[UUID, list[UUID]] | None = None,
        beat_character_emphasis: list[UUID] | None = None,
        relationships_by_character: (
            dict[UUID, list[RelationshipDispositionContext]] | None
        ) = None,
        social_pressure_by_character: dict[UUID, float] | None = None,
    ) -> list[ScheduledInitiativeAction]:
        score = compute_initiative_score(session_state)
        eligible_targets_lookup = eligible_targets_by_character or {}
        relationships_lookup = relationships_by_character or {}

        actions: list[ScheduledInitiativeAction] = []
        sorted_profiles = sorted(
            character_profiles, key=lambda profile: str(profile.character_id)
        )
        for profile in sorted_profiles:
            if not profile.is_ai_controlled:
                continue
            threshold = effective_initiative_threshold(profile, threshold_overrides)
            if social_pressure_by_character is not None:
                pressure = social_pressure_by_character.get(profile.character_id, 0.0)
                threshold = modulate_threshold_for_pressure(threshold, pressure)
            if score < threshold:
                continue

            target_character_id = select_initiative_target(
                initiating_character_id=profile.character_id,
                eligible_target_ids=eligible_targets_lookup.get(
                    profile.character_id, []
                ),
                beat_character_emphasis=beat_character_emphasis,
                relationships=relationships_lookup.get(profile.character_id, []),
            )
            if target_character_id is None:
                target_type: Literal["npc", "player_group"] = "player_group"
            else:
                target_type = "npc"

            actions.append(
                ScheduledInitiativeAction(
                    initiating_character_id=profile.character_id,
                    target_character_id=target_character_id,
                    target_type=target_type,
                    initiative_score=score,
                )
            )
        return actions


def build_npc_npc_messages(
    *,
    speaker_context: CharacterGenerationContext,
    partner_context: CharacterGenerationContext,
    current_beat_id: str | None,
    scene_goal: str | None,
    prior_turns: list[NpcNpcExchangeTurn],
    speaker_social_pressure: float | None = None,
) -> list[dict[str, Any]]:
    """Assemble the combined two-character system prompt for one NPC-NPC turn."""
    speaker_identity = (
        _format_identity_block(speaker_context)
        .replace(
            "[CHARACTER IDENTITY AND PERSONALITY]",
            "[INITIATING CHARACTER IDENTITY AND PERSONALITY]",
        )
        .replace(
            "[END CHARACTER IDENTITY AND PERSONALITY]",
            "[END INITIATING CHARACTER IDENTITY AND PERSONALITY]",
        )
    )
    speaker_known = (
        _format_known_block(speaker_context.known_facts)
        .replace(
            "[KNOWN KNOWLEDGE CONSTRAINTS]",
            "[INITIATING CHARACTER KNOWN KNOWLEDGE]",
        )
        .replace(
            "[END KNOWN KNOWLEDGE CONSTRAINTS]",
            "[END INITIATING CHARACTER KNOWN KNOWLEDGE]",
        )
    )
    speaker_unknown = (
        _format_not_known_block(speaker_context.unknown_facts)
        .replace(
            "[NOT-KNOWN KNOWLEDGE CONSTRAINTS]",
            "[INITIATING CHARACTER NOT-KNOWN KNOWLEDGE]",
        )
        .replace(
            "[END NOT-KNOWN KNOWLEDGE CONSTRAINTS]",
            "[END INITIATING CHARACTER NOT-KNOWN KNOWLEDGE]",
        )
    )

    partner_identity = (
        _format_identity_block(partner_context)
        .replace(
            "[CHARACTER IDENTITY AND PERSONALITY]",
            "[TARGET CHARACTER IDENTITY AND PERSONALITY]",
        )
        .replace(
            "[END CHARACTER IDENTITY AND PERSONALITY]",
            "[END TARGET CHARACTER IDENTITY AND PERSONALITY]",
        )
    )
    partner_known = (
        _format_known_block(partner_context.known_facts)
        .replace(
            "[KNOWN KNOWLEDGE CONSTRAINTS]",
            "[TARGET CHARACTER KNOWN KNOWLEDGE]",
        )
        .replace(
            "[END KNOWN KNOWLEDGE CONSTRAINTS]",
            "[END TARGET CHARACTER KNOWN KNOWLEDGE]",
        )
    )

    relationship_block = _format_relationship_block(
        speaker_context.relationship_dispositions
        + partner_context.relationship_dispositions
    )
    scene_block = _format_scene_block(current_beat_id, scene_goal)

    blocks = [
        speaker_identity,
        speaker_known,
        speaker_unknown,
        partner_identity,
        partner_known,
        relationship_block,
    ]
    if (
        speaker_social_pressure is not None
        and speaker_social_pressure
        >= speaker_context.behavior_profile.crumble_threshold
    ):
        blocks.append(
            _format_pressure_block(
                speaker_social_pressure,
                speaker_context.behavior_profile.crumble_threshold,
            )
        )
    blocks.append(scene_block)

    system_prompt = "\n\n".join(blocks)

    messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
    if not prior_turns:
        messages.append(
            {
                "role": "user",
                "content": (
                    "You are addressing the target character directly in this scene. "
                    "Speak in character, consistent with your goals and personality. "
                    "Stay within your knowledge state."
                ),
            }
        )
    else:
        for turn in prior_turns:
            messages.append(
                {
                    "role": "assistant"
                    if turn.actor_character_id == speaker_context.character_id
                    else "user",
                    "content": turn.content,
                }
            )
    return messages


async def generate_npc_npc_exchange(
    db_session: AsyncSession,
    *,
    session_id: UUID,
    initiating_character_id: UUID,
    target_character_id: UUID,
    quality_tier: str,
    max_turns: int = 1,
    current_beat_id: str | None = None,
    scene_goal: str | None = None,
    temperature: float = 0.7,
    tension_score: float | None = None,
    safety_policy_context: dict[str, Any] | str | None = None,
    content_rails: "ContentRailsConfig | None" = None,
    nightcap_mode: bool = False,
    social_pressure_by_character: dict[UUID, float] | None = None,
) -> NpcNpcExchangeEvent:
    """Generate an NPC-to-NPC exchange of one or more alternating turns.

    Both characters' knowledge state is re-queried per turn. Knowledge
    constraints are enforced on whichever character is the current speaker.
    A safety-blocked turn ends the exchange early.
    """
    if max_turns < 1:
        msg = "max_turns must be at least 1"
        raise ValueError(msg)

    exchange_id = uuid4()
    turns: list[NpcNpcExchangeTurn] = []
    speaker_rotation = (
        (initiating_character_id, target_character_id),
        (target_character_id, initiating_character_id),
    )

    for turn_index in range(max_turns):
        speaker_id, partner_id = speaker_rotation[turn_index % 2]

        speaker_context = await build_character_generation_context(
            db_session,
            session_id=session_id,
            character_id=speaker_id,
        )
        partner_context = await build_character_generation_context(
            db_session,
            session_id=session_id,
            character_id=partner_id,
        )

        speaker_pressure = (
            social_pressure_by_character.get(speaker_id)
            if social_pressure_by_character is not None
            else None
        )
        messages = build_npc_npc_messages(
            speaker_context=speaker_context,
            partner_context=partner_context,
            current_beat_id=current_beat_id,
            scene_goal=scene_goal,
            prior_turns=turns,
            speaker_social_pressure=speaker_pressure,
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
            safety_layer = _safety_layer_from_sentinel(result.model_used)
            payload = _build_turn_payload(
                exchange_id=exchange_id,
                turn_index=turn_index,
                speaker_context=speaker_context,
                partner_context=partner_context,
                initiating_character_id=initiating_character_id,
                target_character_id=target_character_id,
                quality_tier=quality_tier,
                current_beat_id=current_beat_id,
            )
            payload["safety_blocked"] = True
            payload["safety_layer"] = safety_layer
            event = Event(
                session_id=session_id,
                actor_char_id=None,
                event_type="npc_npc_exchange_blocked",
                payload=payload,
                content_text=None,
            )
            db_session.add(event)
            await db_session.flush()
            turns.append(
                NpcNpcExchangeTurn(
                    event_id=event.event_id,
                    actor_character_id=speaker_id,
                    content=result.content,
                    turn_index=turn_index,
                    safety_blocked=True,
                    safety_layer=safety_layer,
                )
            )
            break

        leaked_fact = find_unknown_fact_leak(
            result.content, speaker_context.unknown_facts
        )
        if leaked_fact is not None:
            msg = f"npc-npc turn referenced unknown fact {leaked_fact.fact_id}"
            raise KnowledgeConstraintViolation(msg)

        payload = _build_turn_payload(
            exchange_id=exchange_id,
            turn_index=turn_index,
            speaker_context=speaker_context,
            partner_context=partner_context,
            initiating_character_id=initiating_character_id,
            target_character_id=target_character_id,
            quality_tier=quality_tier,
            current_beat_id=current_beat_id,
        )
        event = Event(
            session_id=session_id,
            actor_char_id=speaker_id,
            event_type="npc_npc_exchange_turn",
            payload=payload,
            content_text=result.content,
        )
        db_session.add(event)
        await db_session.flush()
        turns.append(
            NpcNpcExchangeTurn(
                event_id=event.event_id,
                actor_character_id=speaker_id,
                content=result.content,
                turn_index=turn_index,
            )
        )

    return NpcNpcExchangeEvent(
        exchange_id=exchange_id,
        session_id=session_id,
        initiating_character_id=initiating_character_id,
        target_character_id=target_character_id,
        turns=tuple(turns),
    )


def schedule_initiative_tasks(
    session_factory: Callable[[], AbstractAsyncContextManager[AsyncSession]],
    actions: list[ScheduledInitiativeAction],
    *,
    session_id: UUID,
    quality_tier: str,
    max_turns: int = 1,
    current_beat_id: str | None = None,
    scene_goal: str | None = None,
    tension_score: float | None = None,
    safety_policy_context: dict[str, Any] | str | None = None,
    content_rails: "ContentRailsConfig | None" = None,
    nightcap_mode: bool = False,
    social_pressure_by_character: dict[UUID, float] | None = None,
) -> list[asyncio.Task[NpcNpcExchangeEvent | CharacterDialogueEvent]]:
    """Dispatch each action as its own asyncio task. Returns immediately.

    Each task opens its own ``AsyncSession`` through ``session_factory`` so the
    coordinator's session is never shared. The caller may await the returned
    handles later, store them, or fire and forget.
    """
    tasks: list[asyncio.Task[NpcNpcExchangeEvent | CharacterDialogueEvent]] = []
    for action in actions:
        coro = _run_initiative_action(
            session_factory,
            action,
            session_id=session_id,
            quality_tier=quality_tier,
            max_turns=max_turns,
            current_beat_id=current_beat_id,
            scene_goal=scene_goal,
            tension_score=tension_score,
            safety_policy_context=safety_policy_context,
            content_rails=content_rails,
            nightcap_mode=nightcap_mode,
            social_pressure_by_character=social_pressure_by_character,
        )
        tasks.append(asyncio.create_task(coro))
    return tasks


async def _run_initiative_action(
    session_factory: Callable[[], AbstractAsyncContextManager[AsyncSession]],
    action: ScheduledInitiativeAction,
    *,
    session_id: UUID,
    quality_tier: str,
    max_turns: int,
    current_beat_id: str | None,
    scene_goal: str | None,
    tension_score: float | None,
    safety_policy_context: dict[str, Any] | str | None,
    content_rails: "ContentRailsConfig | None",
    nightcap_mode: bool,
    social_pressure_by_character: dict[UUID, float] | None = None,
) -> NpcNpcExchangeEvent | CharacterDialogueEvent:
    async with session_factory() as db_session:
        if action.target_type == "npc" and action.target_character_id is not None:
            exchange = await generate_npc_npc_exchange(
                db_session,
                session_id=session_id,
                initiating_character_id=action.initiating_character_id,
                target_character_id=action.target_character_id,
                quality_tier=quality_tier,
                max_turns=max_turns,
                current_beat_id=current_beat_id,
                scene_goal=scene_goal,
                tension_score=tension_score,
                safety_policy_context=safety_policy_context,
                content_rails=content_rails,
                nightcap_mode=nightcap_mode,
                social_pressure_by_character=social_pressure_by_character,
            )
            await db_session.commit()
            return exchange

        character_pressure = (
            social_pressure_by_character.get(action.initiating_character_id)
            if social_pressure_by_character is not None
            else None
        )
        dialogue = await generate_character_dialogue(
            db_session,
            session_id=session_id,
            character_id=action.initiating_character_id,
            player_input=(
                "You are speaking now on your own initiative. Address the group "
                "in character, consistent with your goals and personality. Stay "
                "within your knowledge state."
            ),
            quality_tier=quality_tier,
            target_audience="all",
            current_beat_id=current_beat_id,
            scene_goal=scene_goal,
            tension_score=tension_score,
            safety_policy_context=safety_policy_context,
            content_rails=content_rails,
            nightcap_mode=nightcap_mode,
            social_pressure=character_pressure,
        )
        await db_session.commit()
        return dialogue


def _build_turn_payload(
    *,
    exchange_id: UUID,
    turn_index: int,
    speaker_context: CharacterGenerationContext,
    partner_context: CharacterGenerationContext,
    initiating_character_id: UUID,
    target_character_id: UUID,
    quality_tier: str,
    current_beat_id: str | None,
) -> dict[str, Any]:
    return {
        "exchange_id": str(exchange_id),
        "turn_index": turn_index,
        "initiating_character_id": str(initiating_character_id),
        "target_character_id": str(target_character_id),
        "speaker_character_id": str(speaker_context.character_id),
        "partner_character_id": str(partner_context.character_id),
        "task_type": "character_dialogue",
        "quality_tier": quality_tier,
        "current_beat_id": current_beat_id,
        "speaker_knowledge_constraint": {
            "known_fact_ids": [
                str(fact.fact_id) for fact in speaker_context.known_facts
            ],
            "unknown_fact_ids": [
                str(fact.fact_id) for fact in speaker_context.unknown_facts
            ],
        },
        "partner_knowledge_constraint": {
            "known_fact_ids": [
                str(fact.fact_id) for fact in partner_context.known_facts
            ],
            "unknown_fact_ids": [
                str(fact.fact_id) for fact in partner_context.unknown_facts
            ],
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
