"""Session-facing Pydantic models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


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


class SessionParticipant(BaseModel):
    participant_id: UUID
    session_id: UUID
    character_id: UUID
    account_id: Optional[UUID] = None
    join_token: str
    surface_type: str
    is_ai_controlled: bool
