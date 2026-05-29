"""Pydantic models for arc-definition validation and loading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

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


class NarratorConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str
    surface: str
    persona_mode: str
    behavior_triggers: List[str] = Field(default_factory=list)
    omniscient: bool
    player_addressable: bool


class BeatDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")

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
    pacing_config: Dict[str, Any] = Field(default_factory=dict)
    audience_targets: List[str] = Field(default_factory=list)
    mini_games: Optional[List[Dict[str, Any]]] = None


class ArcDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")

    arc_id: str
    name: str
    min_players: int
    max_players: int
    character_mode: CharacterMode
    aesthetic_mode: AestheticMode
    setting_constraint: Optional[str] = None
    arc_structure: str
    play_mode: PlayMode
    narrator: NarratorConfig
    quality_tier_default: QualityTier
    characters: List[Dict[str, Any]] = Field(default_factory=list)
    beats: List[BeatDefinition]
    beat_graph: Dict[str, List[str]]
    generative_elements: Dict[str, Any] = Field(default_factory=dict)
    content_rails: Dict[str, Any] = Field(default_factory=dict)
    knowledge_rules: Dict[str, Any] = Field(default_factory=dict)
    pacing_config: Dict[str, Any] = Field(default_factory=dict)
    victim_config: Dict[str, Any] = Field(default_factory=dict)
    kill_config: Dict[str, Any] = Field(default_factory=dict)
    murder_timing_range: List[int] = Field(default_factory=list)
    session_duration_range: List[int] = Field(default_factory=list)
    revelation_step_range: List[int] = Field(default_factory=list)
    tone_config: Dict[str, Any] = Field(default_factory=dict)
