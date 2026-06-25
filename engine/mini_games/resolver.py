"""Mini-game content resolution into one immutable runtime snapshot."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from engine.mini_games.loader import LoadedMiniGame, load_mini_game_package
from engine.mini_games.models import (
    BehavioralOutputDeclaration,
    ContentMode,
    DelayedClueFallback,
    MiniGameDefinition,
)
from engine.routing import generate
from engine.safety import (
    L1_HARD_STOP_SENTINEL,
    L2_BLOCK_SENTINEL,
    L3_BLOCK_SENTINEL,
    SafetyHardStopResult,
    evaluate_l1_hard_stops,
)

if TYPE_CHECKING:
    from engine.arc.models import ContentRailsConfig


class MiniGameContentResolutionError(ValueError):
    """Raised when mini-game content cannot be resolved safely."""


class ResolvedMiniGameSnapshot(BaseModel):
    """One versioned contract consumed by future deterministic runtime work."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    snapshot_schema_version: str = "1.0"
    game_id: str
    definition_version: str
    source_content_mode: ContentMode
    mechanic_type: str
    participation_mode: str
    min_players: int
    max_players: int
    duration_seconds: int
    rules: dict[str, Any]
    behavioral_outputs: tuple[BehavioralOutputDeclaration, ...]
    clue_fallback: DelayedClueFallback
    resolved_content: dict[str, Any]
    presentation: dict[str, Any] = Field(default_factory=dict)


class _GeneratedMiniGamePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: dict[str, Any] = Field(default_factory=dict)
    presentation: dict[str, Any] = Field(default_factory=dict)


async def resolve_mini_game_package_snapshot(
    db_session: AsyncSession,
    *,
    session_id: UUID,
    package_path: Path,
    quality_tier: str,
    content_rails: "ContentRailsConfig | None" = None,
    adaptation_context: Mapping[str, Any] | None = None,
    session_context: Mapping[str, Any] | None = None,
    safety_policy_context: Mapping[str, Any] | str | None = None,
    nightcap_mode: bool = False,
    temperature: float = 0.3,
) -> ResolvedMiniGameSnapshot:
    loaded_game = load_mini_game_package(package_path)
    return await resolve_loaded_mini_game_snapshot(
        db_session,
        session_id=session_id,
        loaded_game=loaded_game,
        quality_tier=quality_tier,
        content_rails=content_rails,
        adaptation_context=adaptation_context,
        session_context=session_context,
        safety_policy_context=safety_policy_context,
        nightcap_mode=nightcap_mode,
        temperature=temperature,
    )


async def resolve_loaded_mini_game_snapshot(
    db_session: AsyncSession,
    *,
    session_id: UUID,
    loaded_game: LoadedMiniGame,
    quality_tier: str,
    content_rails: "ContentRailsConfig | None" = None,
    adaptation_context: Mapping[str, Any] | None = None,
    session_context: Mapping[str, Any] | None = None,
    safety_policy_context: Mapping[str, Any] | str | None = None,
    nightcap_mode: bool = False,
    temperature: float = 0.3,
) -> ResolvedMiniGameSnapshot:
    definition = loaded_game.definition
    authored_content = _json_object(definition.authored_content)
    presentation: dict[str, Any] = {}

    if definition.content_mode is ContentMode.authored:
        resolved_content = authored_content
    else:
        generated_payload = await _resolve_generated_payload(
            db_session,
            session_id=session_id,
            definition=definition,
            quality_tier=quality_tier,
            content_rails=content_rails,
            authored_content=authored_content,
            adaptation_context=adaptation_context,
            session_context=session_context,
            safety_policy_context=safety_policy_context,
            nightcap_mode=nightcap_mode,
            temperature=temperature,
        )
        presentation = _json_object(generated_payload.presentation)
        if definition.content_mode is ContentMode.generative:
            if not generated_payload.content:
                raise MiniGameContentResolutionError(
                    "generative mini-game resolution returned empty content"
                )
            resolved_content = _json_object(generated_payload.content)
        else:
            resolved_content = _merge_hybrid_content(
                authored_content,
                generated_payload.content,
            )

    snapshot = ResolvedMiniGameSnapshot(
        game_id=definition.game_id,
        definition_version=definition.version,
        source_content_mode=definition.content_mode,
        mechanic_type=definition.mechanic_type,
        participation_mode=definition.participation_mode.value,
        min_players=definition.min_players,
        max_players=definition.max_players,
        duration_seconds=definition.duration_seconds,
        rules=_json_object(definition.rules),
        behavioral_outputs=tuple(definition.behavioral_outputs),
        clue_fallback=definition.clue_fallback,
        resolved_content=resolved_content,
        presentation=presentation,
    )
    _validate_snapshot_output(snapshot)
    return snapshot


async def _resolve_generated_payload(
    db_session: AsyncSession,
    *,
    session_id: UUID,
    definition: MiniGameDefinition,
    quality_tier: str,
    content_rails: "ContentRailsConfig | None",
    authored_content: dict[str, Any],
    adaptation_context: Mapping[str, Any] | None,
    session_context: Mapping[str, Any] | None,
    safety_policy_context: Mapping[str, Any] | str | None,
    nightcap_mode: bool,
    temperature: float,
) -> _GeneratedMiniGamePayload:
    messages = build_mini_game_resolution_messages(
        definition,
        authored_content=authored_content,
        adaptation_context=adaptation_context,
        session_context=session_context,
    )
    result = await generate(
        db_session,
        session_id=session_id,
        task_type="narrative_generation",
        quality_tier=quality_tier,
        messages=messages,
        temperature=temperature,
        safety_policy_context=_build_resolution_safety_policy_context(
            definition,
            content_rails,
            safety_policy_context,
        ),
        content_rails=content_rails,
        nightcap_mode=nightcap_mode,
    )
    if result.model_used in {
        L1_HARD_STOP_SENTINEL,
        L2_BLOCK_SENTINEL,
        L3_BLOCK_SENTINEL,
    }:
        raise MiniGameContentResolutionError(
            "mini-game content resolution blocked by engine safety policy"
        )

    payload = _load_json_object(result.content)
    if payload is None:
        raise MiniGameContentResolutionError(
            "mini-game content resolution did not return valid JSON"
        )
    try:
        return _GeneratedMiniGamePayload.model_validate(payload)
    except ValidationError as exc:
        raise MiniGameContentResolutionError(
            f"mini-game content resolution returned an invalid payload: {exc}"
        ) from exc


def build_mini_game_resolution_messages(
    definition: MiniGameDefinition,
    *,
    authored_content: Mapping[str, Any],
    adaptation_context: Mapping[str, Any] | None = None,
    session_context: Mapping[str, Any] | None = None,
) -> list[dict[str, str]]:
    mode_instructions = {
        ContentMode.generative: (
            "Generate the complete content object for runtime consumption. "
            "Keep all deterministic rules authored and unchanged."
        ),
        ContentMode.hybrid: (
            "Treat authored_content as canonical. Only fill missing details, "
            "add presentation-safe flavor, or replace placeholder copy markers "
            "such as [final authored copy needed]. Do not overwrite existing "
            "authored rules text or canonical content decisions."
        ),
    }
    system_prompt = "\n".join(
        [
            "You resolve Arcwright mini-game content into a runtime snapshot.",
            "Return JSON only.",
            "The JSON object must contain exactly two top-level keys: content and presentation.",
            "content must be an object. presentation must be an object.",
            "Do not include markdown fences, commentary, or extra keys.",
            "Do not alter rules, scoring, outcomes, tie logic, clue unlocks, clue fallback, timers, persistence, or canonical state.",
            "Aesthetic adaptation is presentation-only and may change wording, labels, flavor, and surface hints only.",
            mode_instructions[definition.content_mode],
        ]
    )
    request_payload = {
        "game_id": definition.game_id,
        "version": definition.version,
        "mechanic_type": definition.mechanic_type,
        "content_mode": definition.content_mode.value,
        "participation_mode": definition.participation_mode.value,
        "rules": definition.rules,
        "authored_content": authored_content or None,
        "generation_constraints": definition.generation_constraints,
        "adaptation_context": dict(adaptation_context or {}),
        "session_context": dict(session_context or {}),
    }
    return [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": json.dumps(request_payload, sort_keys=True),
        },
    ]


def _build_resolution_safety_policy_context(
    definition: MiniGameDefinition,
    content_rails: "ContentRailsConfig | None",
    explicit_context: Mapping[str, Any] | str | None,
) -> Mapping[str, Any] | str:
    if explicit_context is not None:
        return explicit_context

    extra_safety: list[str] = []
    generation_constraints = definition.generation_constraints or {}
    safety_rules = generation_constraints.get("safety")
    if isinstance(safety_rules, list):
        extra_safety.extend(str(rule) for rule in safety_rules)

    if content_rails is None:
        return {
            "permitted": [
                "fictional murder mystery mini-game content",
                f"mechanic-specific content for {definition.mechanic_type}",
            ],
            "warnings": [],
            "prohibited": extra_safety,
        }

    return {
        "permitted": [
            "fictional murder mystery mini-game content",
            f"mechanic-specific content for {definition.mechanic_type}",
        ],
        "warnings": list(content_rails.thematic_warnings),
        "prohibited": list(content_rails.prohibited_categories) + extra_safety,
    }


def _load_json_object(content: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            parsed = json.loads(content[start : end + 1])
        except json.JSONDecodeError:
            return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _merge_hybrid_content(
    authored_content: Mapping[str, Any],
    generated_content: Mapping[str, Any],
) -> dict[str, Any]:
    merged = _json_object(authored_content)
    _merge_into(merged, generated_content, path=())
    return merged


def _merge_into(
    target: dict[str, Any],
    incoming: Mapping[str, Any],
    *,
    path: tuple[str, ...],
) -> None:
    for key, incoming_value in incoming.items():
        current_path = path + (key,)
        if key not in target:
            target[key] = deepcopy(incoming_value)
            continue

        current_value = target[key]
        if isinstance(current_value, dict) and isinstance(incoming_value, Mapping):
            _merge_into(current_value, incoming_value, path=current_path)
            continue

        if current_value == incoming_value:
            continue

        if _is_replaceable_placeholder(current_value):
            target[key] = deepcopy(incoming_value)
            continue

        joined_path = ".".join(current_path)
        raise MiniGameContentResolutionError(
            f"generated content attempted to overwrite authored field {joined_path}"
        )


def _is_replaceable_placeholder(value: Any) -> bool:
    if not isinstance(value, str):
        return value is None
    normalized = value.strip().casefold()
    return (
        normalized.startswith("[")
        and normalized.endswith("]")
        and any(token in normalized for token in ("needed", "todo", "tbd"))
    )


def _validate_snapshot_output(snapshot: ResolvedMiniGameSnapshot) -> None:
    hard_stop = _evaluate_snapshot_hard_stop(snapshot)
    if hard_stop is not None:
        raise MiniGameContentResolutionError(
            f"resolved mini-game snapshot blocked by {hard_stop.code}"
        )


def _evaluate_snapshot_hard_stop(
    snapshot: ResolvedMiniGameSnapshot,
) -> SafetyHardStopResult | None:
    return evaluate_l1_hard_stops(
        [
            {
                "role": "system",
                "content": json.dumps(
                    {
                        "resolved_content": snapshot.resolved_content,
                        "presentation": snapshot.presentation,
                    },
                    sort_keys=True,
                ),
            }
        ]
    )


def _json_object(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    return deepcopy(dict(value))
