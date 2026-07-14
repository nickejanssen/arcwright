"""Pydantic models for arc-definition validation and loading."""

from __future__ import annotations

from enum import Enum
from math import isclose
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from engine.mini_games.models import MiniGameBinding
from engine.session.models import QualityTier


class CharacterMode(str, Enum):
    authored = "authored"
    generated = "generated"
    hybrid = "hybrid"


class AestheticMode(str, Enum):
    fixed = "fixed"
    palette = "palette"
    generative = "generative"


class PlayMode(str, Enum):
    imposter = "imposter"
    detective_race = "detective_race"
    cooperative = "cooperative"


class SelectionModelOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    allow_random: bool = False


class AestheticConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    selection_model: Dict[str, SelectionModelOption] = Field(default_factory=dict)
    asset_generation: Dict[str, str] = Field(default_factory=dict)
    ab_test_planned: Optional[str] = None


class PacingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stall_threshold: float = 0.25
    misdirection_threshold: float = 0.80
    premium_threshold: float = 0.85
    w_time: float
    w_action: float
    w_suspicion: float
    w_coverage: float

    @model_validator(mode="after")
    def validate_weight_sum(self) -> "PacingConfig":
        total = self.w_time + self.w_action + self.w_suspicion + self.w_coverage
        if not isclose(total, 1.0, abs_tol=0.000001):
            msg = "pacing weights must sum to 1.0"
            raise ValueError(msg)
        return self


class BeatPacingConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    stall_threshold_seconds: Optional[int] = None
    acceleration_trigger: Optional[str] = None
    misdirection_trigger: Optional[str] = None


class GenerativeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    killer_assignment: bool = False
    character_generation: bool = False
    character_personality_augmentation: bool = False
    aesthetic_generation: bool = False
    clue_content: bool = False
    plot_twist: bool = False
    narrator_dialogue: bool = False


class ContentRailsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prohibited_categories: List[str] = Field(default_factory=list)
    thematic_warnings: List[str] = Field(default_factory=list)
    age_floor: int = 18
    extra_prohibitions: List[str] = Field(default_factory=list)
    """Arc-authored plain-language sentences appended to the L3 policy block.

    Lets an arc tighten its content rules beyond the category list without
    engine code changes. Arc config can only add prohibitions; the platform
    minimum policy and the L1/L2 layers are engine-owned and cannot be
    relaxed from here.
    """


class KnowledgeRuleSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    killer_knows_they_did_it: bool = False
    narrator_omniscient: bool = False
    clues_private_until_shared: bool = False


class NarratorConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    _ALLOWED_BEHAVIOR_TRIGGERS = frozenset(
        {
            "beat_transition",
            "clue_release",
            "tension_threshold",
            "player_inaction",
        }
    )

    type: str
    surface: str
    persona_mode: str
    behavior_triggers: List[str] = Field(default_factory=list)
    omniscient: bool
    player_addressable: bool

    @model_validator(mode="after")
    def validate_behavior_triggers(self) -> "NarratorConfig":
        invalid = sorted(
            trigger
            for trigger in self.behavior_triggers
            if trigger not in self._ALLOWED_BEHAVIOR_TRIGGERS
        )
        if invalid:
            msg = f"invalid narrator behavior triggers: {', '.join(invalid)}"
            raise ValueError(msg)
        return self


class BeatDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    beat_id: str
    beat_name: str
    beat_type: str
    story_circle_step: Union[int, List[int]]
    structural_function: str
    dramatic_purpose: Optional[str] = None
    emotional_target: Optional[str] = None
    information_goal: Optional[str] = None
    tension_target: Optional[float] = None
    character_emphasis: List[str] = Field(default_factory=list)
    authored_content: Optional[Dict[str, Any]] = None
    generative_triggers: List[str] = Field(default_factory=list)
    entry_conditions: List[str] = Field(default_factory=list)
    exit_conditions: List[str] = Field(default_factory=list)
    pacing_config: BeatPacingConfig = Field(default_factory=BeatPacingConfig)
    audience_targets: List[str] = Field(default_factory=list)
    mini_games: Optional[List[MiniGameBinding]] = None

    @model_validator(mode="after")
    def validate_mini_game_binding_ids(self) -> "BeatDefinition":
        if not self.mini_games:
            return self
        binding_ids = [binding.binding_id for binding in self.mini_games]
        if len(binding_ids) != len(set(binding_ids)):
            msg = f"beat {self.beat_id} has duplicate mini-game binding_ids"
            raise ValueError(msg)
        return self


class ArcDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    arc_id: str
    name: str
    min_players: int
    max_players: int
    character_mode: CharacterMode
    aesthetic_config: AestheticConfig
    aesthetic_mode: Optional[AestheticMode] = None
    setting_constraint: Optional[str] = None
    arc_structure: str
    play_mode: PlayMode
    narrator: NarratorConfig
    quality_tier_default: QualityTier
    characters: List[Dict[str, Any]] = Field(default_factory=list)
    beats: List[BeatDefinition] = Field(min_length=1)
    beat_graph: Dict[str, List[str]]
    generative_elements: GenerativeConfig
    content_rails: ContentRailsConfig
    knowledge_rules: KnowledgeRuleSet
    pacing_config: PacingConfig
    victim_config: Dict[str, Any] = Field(default_factory=dict)
    kill_config: Dict[str, Any] = Field(default_factory=dict)
    murder_timing_range: List[int] = Field(default_factory=list)
    session_duration_range: List[int] = Field(default_factory=list)
    revelation_step_range: List[int] = Field(default_factory=list)
    tone_config: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_aesthetic_mode(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        if "aesthetic_config" not in data and "aesthetic_mode" in data:
            data = dict(data)
            data["aesthetic_config"] = {
                "selection_model": {},
                "asset_generation": {
                    "legacy_mode": data["aesthetic_mode"],
                },
            }
        return data

    @model_validator(mode="after")
    def validate_player_counts(self) -> "ArcDefinition":
        if self.min_players < 1:
            msg = "min_players must be at least 1"
            raise ValueError(msg)
        if self.max_players < 1:
            msg = "max_players must be at least 1"
            raise ValueError(msg)
        if self.min_players > self.max_players:
            msg = "min_players cannot exceed max_players"
            raise ValueError(msg)
        if self.play_mode == PlayMode.imposter and self.min_players < 3:
            msg = "imposter play mode requires at least 3 players"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_authored_characters(self) -> "ArcDefinition":
        if self.character_mode == CharacterMode.authored and not self.characters:
            msg = "authored character mode requires at least one character"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_beat_graph(self) -> "ArcDefinition":
        beat_ids = {beat.beat_id for beat in self.beats}
        graph_ids = set(self.beat_graph)
        unknown_sources = sorted(graph_ids - beat_ids)
        if unknown_sources:
            msg = f"beat_graph contains unknown beat ids: {', '.join(unknown_sources)}"
            raise ValueError(msg)

        unknown_targets = sorted(
            {
                target
                for targets in self.beat_graph.values()
                for target in targets
                if target not in beat_ids
            }
        )
        if unknown_targets:
            msg = (
                "beat_graph references undefined beat ids: "
                f"{', '.join(unknown_targets)}"
            )
            raise ValueError(msg)
        return self
