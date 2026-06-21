"""Typed authoring contracts for reusable mini-game packages."""

from __future__ import annotations

from enum import Enum
from pathlib import PurePosixPath
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
_SEMVER_PATTERN = (
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


class MiniGameLifecycle(str, Enum):
    draft = "draft"
    playtest = "playtest"
    active = "active"
    retired = "retired"


class ParticipationMode(str, Enum):
    individual = "individual"
    collaborative = "collaborative"
    group = "group"


class ContentMode(str, Enum):
    authored = "authored"
    generative = "generative"
    hybrid = "hybrid"


class BehavioralValueType(str, Enum):
    integer = "integer"
    number = "number"
    boolean = "boolean"
    string = "string"


class BehavioralScope(str, Enum):
    participant = "participant"
    team = "team"
    run = "run"


class ClueVariant(str, Enum):
    full = "full"
    reduced = "reduced"


class BehavioralOutputDeclaration(BaseModel):
    """A neutral metric or deterministic, game-scoped observation."""

    model_config = ConfigDict(extra="forbid")

    key: str = Field(pattern=_SLUG_PATTERN)
    description: str = Field(min_length=1)
    value_type: BehavioralValueType
    scope: BehavioralScope
    derived: bool = False


class DelayedClueFallback(BaseModel):
    """Authored fallback that prevents a failed puzzle from blocking the arc."""

    model_config = ConfigDict(extra="forbid")

    delay_seconds: int = Field(ge=0)
    clue_variant: ClueVariant = ClueVariant.reduced
    host_override: bool = True


class MiniGameManifest(BaseModel):
    """Stable package identity and lifecycle metadata."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    game_id: str = Field(pattern=_SLUG_PATTERN)
    title: str = Field(min_length=1)
    lifecycle: MiniGameLifecycle
    current_version: str = Field(pattern=_SEMVER_PATTERN)
    definition_path: str
    asset_paths: list[str] = Field(default_factory=list)

    @field_validator("definition_path")
    @classmethod
    def validate_definition_path(cls, value: str) -> str:
        return _validate_relative_package_path(value)

    @field_validator("asset_paths")
    @classmethod
    def validate_asset_paths(cls, values: list[str]) -> list[str]:
        validated = [_validate_relative_package_path(value) for value in values]
        if len(validated) != len(set(validated)):
            raise ValueError("asset_paths must not contain duplicates")
        return validated

    @model_validator(mode="after")
    def validate_definition_version_path(self) -> "MiniGameManifest":
        expected = f"definitions/{self.current_version}.json"
        if self.definition_path != expected:
            raise ValueError(
                f"definition_path must reference the current version at {expected}"
            )
        return self


class MiniGameDefinition(BaseModel):
    """Versioned rules and content inputs consumed by future runtime work."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    game_id: str = Field(pattern=_SLUG_PATTERN)
    version: str = Field(pattern=_SEMVER_PATTERN)
    mechanic_type: str = Field(pattern=_SLUG_PATTERN)
    participation_mode: ParticipationMode
    content_mode: ContentMode
    min_players: int = Field(ge=1)
    max_players: int = Field(ge=1)
    duration_seconds: int = Field(ge=1)
    rules: dict[str, Any]
    authored_content: Optional[dict[str, Any]] = None
    generation_constraints: Optional[dict[str, Any]] = None
    behavioral_outputs: list[BehavioralOutputDeclaration] = Field(default_factory=list)
    clue_fallback: DelayedClueFallback

    @model_validator(mode="after")
    def validate_player_range(self) -> "MiniGameDefinition":
        if self.min_players > self.max_players:
            raise ValueError("min_players cannot exceed max_players")
        return self

    @model_validator(mode="after")
    def validate_content_composition(self) -> "MiniGameDefinition":
        if self.content_mode in {ContentMode.authored, ContentMode.hybrid}:
            if self.authored_content is None:
                raise ValueError("authored and hybrid content require authored_content")
        if self.content_mode in {ContentMode.generative, ContentMode.hybrid}:
            if self.generation_constraints is None:
                raise ValueError(
                    "generative and hybrid content require generation_constraints"
                )
        return self

    @model_validator(mode="after")
    def validate_behavioral_output_keys(self) -> "MiniGameDefinition":
        keys = [output.key for output in self.behavioral_outputs]
        if len(keys) != len(set(keys)):
            raise ValueError("behavioral output keys must be unique")
        return self


class MiniGameBinding(BaseModel):
    """Version-pinned placement of a mini-game within an arc beat."""

    model_config = ConfigDict(extra="forbid")

    binding_id: str = Field(pattern=_SLUG_PATTERN)
    game_id: str = Field(pattern=_SLUG_PATTERN)
    version: str = Field(pattern=_SEMVER_PATTERN)


def _validate_relative_package_path(value: str) -> str:
    if not value or value in {".", ".."}:
        raise ValueError("package path must identify a relative child path")
    if "\\" in value or ":" in value:
        raise ValueError("package path must use safe POSIX-style relative segments")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".."} for part in path.parts):
        raise ValueError("package path must stay within the mini-game package")
    return value
