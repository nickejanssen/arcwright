"""API request and response schemas for the Arcwright REST API.

Architecture: docs/architecture/09-developer-api.md §9.2.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, TypeAdapter

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


class AddAiCharacterRequest(BaseModel):
    behavior_profile: Optional[dict[str, Any]] = None


class AddAiCharacterResponse(BaseModel):
    participant_id: UUID
    character_id: UUID
    is_ai_controlled: bool


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


class ReplayIntentRequest(BaseModel):
    intent: Literal["yes", "no", "maybe", "not_asked"]
    collection_method: Literal["host_report", "in_app_prompt"]


class TmstVoteBreakdown(BaseModel):
    truth: int = Field(ge=0)
    lie: int = Field(ge=0)
    abstain: int = Field(ge=0)


class TmstInputActionPayload(BaseModel):
    action: Literal["input"]
    statement_text: str = Field(min_length=1, max_length=4000)
    declared_truth: bool


class TmstVoteActionPayload(BaseModel):
    action: Literal["vote"]
    target_character_id: UUID
    vote: Literal["truth", "lie"]


class TmstPresenceActionPayload(BaseModel):
    action: Literal["presence"]
    connected: bool


TmstSubmissionPayload = Annotated[
    Union[
        TmstInputActionPayload,
        TmstVoteActionPayload,
        TmstPresenceActionPayload,
    ],
    Field(discriminator="action"),
]
TMST_SUBMISSION_PAYLOAD_ADAPTER: TypeAdapter[TmstSubmissionPayload] = TypeAdapter(
    TmstSubmissionPayload
)


class TmstPhaseStartedPayload(BaseModel):
    phase: Literal["input"]
    deadline: datetime
    participant_count: int = Field(ge=0)


class TmstPrivatePromptReadyPayload(BaseModel):
    phase: Literal["input"]


class TmstInputPhaseState(BaseModel):
    phase: Literal["input"]
    deadline_at: Optional[datetime] = None
    prompt_ready: bool
    submitted: bool


class TmstSpotlightStartedPayload(BaseModel):
    phase: Literal["spotlight"]
    target_character_id: UUID
    eligible_voter_ids: list[UUID]
    deadline: datetime


class TmstSpotlightSkippedPayload(BaseModel):
    target_character_id: UUID
    reason: Literal["disconnected"]


class TmstSpotlightPhaseState(BaseModel):
    phase: Literal["spotlight"]
    deadline_at: Optional[datetime] = None
    target_character_id: UUID
    connected_character_ids: list[UUID]
    eligible_voter_ids: list[UUID]
    is_spotlighted_player: bool
    can_vote: bool
    has_voted: bool


class TmstRevealResolvedPayload(BaseModel):
    phase: Literal["reveal"]
    target_character_id: UUID
    declared_truth: bool
    statement_text: str
    vote_breakdown: TmstVoteBreakdown
    abstaining_character_ids: list[UUID]


class TmstScoreboardReadyPayload(BaseModel):
    phase: Literal["scoreboard"]
    scores: dict[str, int]
    all_truth_round: bool
    all_lie_round: bool
    deflection_tendency: dict[str, dict[str, int]]


TmstPhaseState = Annotated[
    Union[TmstInputPhaseState, TmstSpotlightPhaseState],
    Field(discriminator="phase"),
]


class MiniGameSubmissionResponse(BaseModel):
    submission_id: str
    is_accepted: bool
    rejection_reason: Optional[str] = None


class MiniGameRunResponse(BaseModel):
    run_id: UUID
    game_id: str
    status: str
    mechanic_type: Optional[str] = None
    deadline_at: Optional[datetime] = None
    phase_state: Optional[TmstPhaseState] = None
    my_submissions: list[MiniGameSubmissionResponse]


class MiniGameSubmissionRequest(BaseModel):
    submission_id: str = Field(min_length=1, max_length=256)
    payload: dict[str, Any]


class HostCommandRequest(BaseModel):
    command: Literal["cancel", "resolve", "release_fallback"]
    params: dict[str, Any] = Field(default_factory=dict)


class HostCommandResponse(BaseModel):
    run_id: UUID
    game_id: str
    status: str


class TaskTypeCostRow(BaseModel):
    task_type: str
    generation_count: int
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal


class PlayerCountCostRow(BaseModel):
    player_count: int
    session_count: int
    generation_count: int
    cost_usd: Decimal


class CostSummaryResponse(BaseModel):
    # AC3: only actual logged values from generation_logs.
    # Pricing fields (revenue, margin, price_per_session, profit) are absent because
    # pricing design is deferred — see docs/architecture/13-cost-model.md §13.5.
    total_cost_usd: Decimal
    total_input_tokens: int
    total_output_tokens: int
    total_generation_count: int
    session_id: Optional[UUID] = None
    arc_id: Optional[str] = None
    by_task_type: list[TaskTypeCostRow]
    by_player_count: list[PlayerCountCostRow]


class LobbyPlayerEntry(BaseModel):
    participant_id: UUID
    display_name: Optional[str] = None


class LobbyStateResponse(BaseModel):
    session_id: UUID
    join_code: Optional[str]
    status: str
    player_count: int
    players: list[LobbyPlayerEntry]


class LobbyJoinRequest(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    join_code: str = Field(min_length=1, max_length=8)


class LobbyJoinResponse(BaseModel):
    participant_id: UUID
    session_id: UUID
    display_name: str
    character_id: UUID
