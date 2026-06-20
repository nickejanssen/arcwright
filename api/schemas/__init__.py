"""API request and response schemas for the Arcwright REST API.

Architecture: docs/architecture/09-developer-api.md §9.2.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

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


class CharacterSummaryResponse(BaseModel):
    character_id: UUID
    participant_id: UUID
    surface_type: str
    is_ai_controlled: bool


class CharacterListResponse(BaseModel):
    session_id: UUID
    characters: list[CharacterSummaryResponse]


class CharacterDetailResponse(BaseModel):
    session_id: UUID
    character_id: UUID
    participant_id: UUID
    surface_type: str
    is_ai_controlled: bool


class PlayerInputRequest(BaseModel):
    kind: Literal["action", "dialogue"]
    content: str = Field(min_length=1, max_length=4000)


class PlayerInputResponse(BaseModel):
    input_id: UUID
    session_id: UUID
    character_id: UUID
    participant_id: UUID
    kind: Literal["action", "dialogue"]
    content: str
    submitted_at: datetime


class KnowledgeAssertRequest(BaseModel):
    character_id: UUID
    fact_type: str = Field(min_length=1, max_length=64)
    fact_content: dict[str, Any]
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_character_id: Optional[UUID] = None


class KnowledgeFactResponse(BaseModel):
    fact_id: UUID
    session_id: UUID
    character_id: UUID
    fact_type: str
    fact_content: dict[str, Any]
    confidence: float
    source_character_id: Optional[UUID] = None
    asserted_at: datetime
    revoked_at: Optional[datetime] = None


class CharacterKnowledgeResponse(BaseModel):
    session_id: UUID
    character_id: UUID
    facts: list[KnowledgeFactResponse]


class EndSessionRequest(BaseModel):
    completion_type: Literal["full_arc", "interrupted", "abandoned"] = "full_arc"
    killer_identified: bool = False
