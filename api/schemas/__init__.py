"""API request and response schemas for the Arcwright REST API.

Architecture: docs/architecture/09-developer-api.md §9.2.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from engine.session.models import QualityTier, SessionStatus


class CreateSessionRequest(BaseModel):
    arc_id: str
    quality_tier: QualityTier = QualityTier.standard


class CreateSessionResponse(BaseModel):
    session_id: UUID
    join_url: str
    host_token: str
    host_join_token: str


class SessionStateResponse(BaseModel):
    session_id: UUID
    arc_id: str
    status: SessionStatus
    current_beat_id: str
    player_count: int
    quality_tier: QualityTier
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cost_consumed_usd: float = 0.0


class AddPlayerResponse(BaseModel):
    participant_id: UUID
    join_token: str
    join_url: str


class JoinSessionResponse(BaseModel):
    session_id: UUID
    player_id: UUID
    character_id: UUID
    player_token: str
