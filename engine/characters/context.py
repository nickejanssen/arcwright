"""Generation-time character context assembly."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import (
    Character,
    Fact,
    RelationshipState,
    Session,
    SessionParticipant,
)
from engine.knowledge import get_character_knowledge

logger = logging.getLogger(__name__)

# Tier thresholds derived from docs/architecture/07-character-behavior.md §7.5.
# Larger groups: more surface tells (more eyes); smaller groups: more mid/deep tells (harder game).
_SMALL_GROUP_MAX = 4  # <= 4 players: all tiers active
_MID_GROUP_MAX = 7  # 5-7 players: surface + mid only; >= 8: surface only


def select_active_tells(tells_raw: list[Any], player_count: int) -> tuple[str, ...]:
    """Return the active tell subset for the given player count.

    Plain-string tells pass through unconditionally (backward-compatible).
    Tier-annotated tells ({"text": str, "tier": "surface"|"mid"|"deep"}) are
    filtered by the player-count thresholds defined in §7.5:
      - player_count <= 4: surface + mid + deep
      - 5 <= player_count <= 7: surface + mid
      - player_count >= 8: surface only
    """
    if player_count >= _MID_GROUP_MAX + 1:
        active_tiers: frozenset[str] = frozenset({"surface"})
    elif player_count >= _SMALL_GROUP_MAX + 1:
        active_tiers = frozenset({"surface", "mid"})
    else:
        active_tiers = frozenset({"surface", "mid", "deep"})

    result: list[str] = []
    for item in tells_raw:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict):
            text = item.get("text")
            tier = item.get("tier")
            if isinstance(text, str) and tier in active_tiers:
                result.append(text)
    return tuple(result)


@dataclass(frozen=True)
class KnownFactContext:
    fact_id: UUID
    fact_type: str
    fact_content: dict[str, Any]
    confidence: float
    provenance_chain: tuple[str, ...]
    provenance_chain_length: int


@dataclass(frozen=True)
class UnknownFactContext:
    fact_id: UUID
    fact_type: str
    fact_content: dict[str, Any]


@dataclass(frozen=True)
class BehaviorProfileContext:
    personality: dict[str, Any]
    goals: tuple[str, ...]
    secrets: tuple[dict[str, Any], ...]
    tells: tuple[str, ...]
    crumble_threshold: float = 1.0


@dataclass(frozen=True)
class RelationshipDispositionContext:
    target_character_id: UUID
    trust: float
    history: str | None
    current_affect: str | None


@dataclass(frozen=True)
class CharacterGenerationContext:
    session_id: UUID
    character_id: UUID
    behavior_profile: BehaviorProfileContext
    relationship_dispositions: tuple[RelationshipDispositionContext, ...]
    is_ai_controlled: bool | None
    known_facts: tuple[KnownFactContext, ...]
    unknown_facts: tuple[UnknownFactContext, ...]


async def build_character_generation_context(
    session: AsyncSession,
    *,
    session_id: UUID,
    character_id: UUID,
    player_count: int | None = None,
) -> CharacterGenerationContext:
    """Build the only sanctioned generation-time character context."""
    if player_count is None:
        db_session = await session.get(Session, session_id)
        player_count = db_session.player_count if db_session is not None else 0

    character = await session.get(Character, character_id)
    profile_data = dict(character.behavior_profile) if character is not None else {}
    behavior_profile = _build_behavior_profile_context(
        profile_data, player_count=player_count
    )

    participant_result = await session.execute(
        select(SessionParticipant)
        .where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.character_id == character_id,
        )
        .order_by(SessionParticipant.participant_id)
    )
    participant = participant_result.scalars().first()

    relationships_result = await session.execute(
        select(RelationshipState)
        .where(
            RelationshipState.session_id == session_id,
            RelationshipState.source_char_id == character_id,
        )
        .order_by(RelationshipState.target_char_id)
    )
    relationships = tuple(
        RelationshipDispositionContext(
            target_character_id=relationship.target_char_id,
            trust=relationship.trust_level,
            history=relationship.history_tag,
            current_affect=relationship.current_affect,
        )
        for relationship in relationships_result.scalars().all()
    )

    known_states = await get_character_knowledge(
        session,
        session_id=session_id,
        character_id=character_id,
    )
    known_fact_ids = {state.fact_id for state in known_states}

    all_facts_result = await session.execute(
        select(Fact).where(Fact.session_id == session_id).order_by(Fact.fact_id)
    )
    all_session_facts = list(all_facts_result.scalars().all())

    known_facts = tuple(
        KnownFactContext(
            fact_id=state.fact_id,
            fact_type=state.fact.fact_type,
            fact_content=dict(state.fact.fact_content),
            confidence=state.confidence,
            provenance_chain=tuple(str(item) for item in state.provenance_chain),
            provenance_chain_length=len(state.provenance_chain),
        )
        for state in known_states
    )
    unknown_facts = tuple(
        UnknownFactContext(
            fact_id=fact.fact_id,
            fact_type=fact.fact_type,
            fact_content=dict(fact.fact_content),
        )
        for fact in all_session_facts
        if fact.fact_id not in known_fact_ids
    )

    return CharacterGenerationContext(
        session_id=session_id,
        character_id=character_id,
        behavior_profile=behavior_profile,
        relationship_dispositions=relationships,
        is_ai_controlled=(
            participant.is_ai_controlled if participant is not None else None
        ),
        known_facts=known_facts,
        unknown_facts=unknown_facts,
    )


def _build_behavior_profile_context(
    profile_data: dict[str, Any],
    player_count: int = 0,
) -> BehaviorProfileContext:
    personality = profile_data.get("personality")
    goals = profile_data.get("goals")
    secrets = profile_data.get("secrets")
    tells = profile_data.get("tells")

    secrets_list: tuple[dict[str, Any], ...] = (
        tuple(dict(item) for item in secrets if isinstance(item, dict))
        if isinstance(secrets, list)
        else ()
    )
    for s in secrets_list:
        raw = s.get("crumble_threshold")
        if raw is not None and not isinstance(raw, (int, float)):
            logger.warning(
                "crumble_threshold has non-numeric type %s; defaulting to 1.0 for this secret",
                type(raw).__name__,
            )
    crumble_threshold = min(
        (
            float(s["crumble_threshold"])
            for s in secrets_list
            if isinstance(s.get("crumble_threshold"), (int, float))
        ),
        default=1.0,
    )

    return BehaviorProfileContext(
        personality=dict(personality) if isinstance(personality, dict) else {},
        goals=tuple(item for item in goals if isinstance(item, str))
        if isinstance(goals, list)
        else (),
        secrets=secrets_list,
        tells=select_active_tells(tells, player_count)
        if isinstance(tells, list)
        else (),
        crumble_threshold=crumble_threshold,
    )
