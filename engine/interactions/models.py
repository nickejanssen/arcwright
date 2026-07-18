from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ResolutionVisibility(str, Enum):
    public = "public"
    private = "private"


class WindowStatus(str, Enum):
    selecting = "selecting"
    locked = "locked"
    resolved = "resolved"


class InteractionOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    option_id: str = Field(min_length=1)
    prompt_key: str = Field(min_length=1)
    required_evidence_ids: list[str] = Field(default_factory=list)
    resolution_visibility: ResolutionVisibility = ResolutionVisibility.public

    @model_validator(mode="after")
    def validate_evidence_ids(self) -> "InteractionOption":
        if len(self.required_evidence_ids) != len(set(self.required_evidence_ids)):
            raise ValueError("required evidence IDs must be unique")
        if any(not evidence_id for evidence_id in self.required_evidence_ids):
            raise ValueError("required evidence IDs must be non-empty")
        return self


class InteractionLimit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_players: int = Field(default=2, ge=1)
    max_players: int = Field(default=8, ge=1)
    default_selections_per_player: int = Field(default=1, ge=1)
    selections_per_player_by_count: dict[int, int] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_range_and_overrides(self) -> "InteractionLimit":
        if self.min_players > self.max_players:
            raise ValueError("min_players must not exceed max_players")
        invalid_counts = [
            count
            for count in self.selections_per_player_by_count
            if count < self.min_players or count > self.max_players
        ]
        if invalid_counts:
            raise ValueError("selection allowance counts must be within player range")
        if any(value < 1 for value in self.selections_per_player_by_count.values()):
            raise ValueError("selection allowances must be positive")
        return self

    def selections_for(self, player_count: int) -> int:
        if not self.min_players <= player_count <= self.max_players:
            raise ValueError("player count is outside the interaction limit")
        return self.selections_per_player_by_count.get(
            player_count, self.default_selections_per_player
        )


class InteractionDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interaction_id: str = Field(min_length=1)
    options: list[InteractionOption] = Field(min_length=3)
    baseline_option_ids: list[str] = Field(default_factory=list)
    limit: InteractionLimit = Field(default_factory=InteractionLimit)

    @model_validator(mode="after")
    def validate_option_catalog(self) -> "InteractionDefinition":
        option_ids = [option.option_id for option in self.options]
        if len(option_ids) != len(set(option_ids)):
            raise ValueError("option IDs must be unique")
        prompt_keys = [option.prompt_key for option in self.options]
        if len(prompt_keys) != len(set(prompt_keys)):
            raise ValueError("prompt keys must be unique")
        if len(self.baseline_option_ids) != len(set(self.baseline_option_ids)):
            raise ValueError("baseline option IDs must be unique")
        if len(self.baseline_option_ids) != 3:
            raise ValueError("exactly three baseline options are required")
        if not set(self.baseline_option_ids).issubset(option_ids):
            raise ValueError("baseline option IDs must refer to options")
        baseline_options = {option.option_id: option for option in self.options}
        if any(
            baseline_options[option_id].required_evidence_ids
            for option_id in self.baseline_option_ids
        ):
            raise ValueError("baseline options cannot require evidence")
        return self


class InteractionTarget(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    target_id: str = Field(min_length=1)


class InteractionSelection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    selection_id: str = Field(min_length=1)
    participant_id: UUID
    target_id: str = Field(min_length=1)
    option_id: str = Field(min_length=1)


class InteractionWindow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    window_id: str = Field(min_length=1)
    interaction_id: str = Field(min_length=1)
    beat_id: str = Field(min_length=1)
    round_index: int = Field(ge=0)
    participant_ids: list[UUID] = Field(min_length=1)
    eligible_targets: list[InteractionTarget] = Field(min_length=1)
    menus_by_participant: dict[UUID, list[str]]
    remaining_selections: dict[UUID, int]
    selections: dict[str, InteractionSelection] = Field(default_factory=dict)
    status: WindowStatus = WindowStatus.selecting
    staged_target_id: str | None = None
    authorized_knowledge_context_ref: str | None = None
    claim_reference_ids: tuple[str, ...] = ()
    evidence_reference_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_window_membership(self) -> "InteractionWindow":
        if len(self.participant_ids) != len(set(self.participant_ids)):
            raise ValueError("participant IDs must be unique")
        target_ids = [target.target_id for target in self.eligible_targets]
        if len(target_ids) != len(set(target_ids)):
            raise ValueError("target IDs must be unique")
        participant_set = set(self.participant_ids)
        if set(self.menus_by_participant) != participant_set:
            raise ValueError("menus must be provided for every participant")
        if set(self.remaining_selections) != participant_set:
            raise ValueError(
                "remaining selections must be provided for every participant"
            )
        if any(remaining < 0 for remaining in self.remaining_selections.values()):
            raise ValueError("remaining selections cannot be negative")
        if (
            self.staged_target_id is not None
            and self.staged_target_id not in target_ids
        ):
            raise ValueError("staged target must be eligible")
        return self


class PublicInteractionGroup(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    group_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    option_id: str = Field(min_length=1)
    selection_ids: tuple[str, ...] = Field(min_length=1)


class InteractionResolution(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    window_id: str = Field(min_length=1)
    round_index: int = Field(ge=0)
    beat_id: str = Field(min_length=1)
    staged_target_id: str | None = None
    ordered_selections: tuple[InteractionSelection, ...] = ()
    public_groups: tuple[PublicInteractionGroup, ...] = ()
    private_selections: tuple[InteractionSelection, ...] = ()
    authorized_knowledge_context_ref: str | None = None
    claim_reference_ids: tuple[str, ...] = ()
    evidence_reference_ids: tuple[str, ...] = ()
