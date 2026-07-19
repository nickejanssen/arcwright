from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ContradictionOutcome(str, Enum):
    confirmed = "confirmed"
    rejected = "rejected"


class ClaimRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    speaker_id: str = Field(min_length=1)
    asker_id: str | None = None
    round_index: int = Field(ge=0)
    beat_id: str = Field(min_length=1)
    interaction_window_id: str = Field(min_length=1)
    claim_text: str = Field(min_length=1)
    referenced_fact_ids: tuple[str, ...] = ()
    is_authorized_lie: bool = False
    falsehood_id: str | None = None
    claim_id: str | None = None
    created_at: datetime | None = None


class FlagResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(min_length=1)
    outcome: ContradictionOutcome
    evidence_id_used: str | None = None
