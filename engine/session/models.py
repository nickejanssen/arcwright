"""Session-facing Pydantic models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    created = "created"
    active = "active"
    paused = "paused"
    completed = "completed"
    abandoned = "abandoned"


class QualityTier(str, Enum):
    standard = "standard"
    premium = "premium"


class ArcBeat(BaseModel):
    beat_id: str
    beat_name: str
    entered_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class RevealState(BaseModel):
    is_revealed: bool = False
    revealed_by: Optional[Literal["authored_conditions", "host_bypass"]] = None
    bypass_sequence: Optional[int] = None


class TransitionBypassLogEntry(BaseModel):
    sequence: int
    actor_id: str
    reason: str
    source_transition: str
    source_beat_id: str
    target_beat_id: str
    bypassed_conditions: list[str] = Field(default_factory=list)


class SessionRuntimeState(BaseModel):
    seed: int
    role_assignments: dict[str, str] = Field(default_factory=dict)
    resolved_generative_elements: dict[str, Any] = Field(default_factory=dict)
    reveal_state: RevealState = Field(default_factory=RevealState)
    transition_bypass_log: list[TransitionBypassLogEntry] = Field(default_factory=list)


class Session(BaseModel):
    session_id: UUID
    arc_id: str
    status: SessionStatus
    host_account_id: UUID
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_beat_id: str
    quality_tier: QualityTier
    player_count: int
    join_code: Optional[str] = None


class SessionParticipant(BaseModel):
    participant_id: UUID
    session_id: UUID
    character_id: UUID
    account_id: Optional[UUID] = None
    join_token: str
    surface_type: str
    is_ai_controlled: bool
