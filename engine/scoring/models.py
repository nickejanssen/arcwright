from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AccusationOutcome(str, Enum):
    correct = "correct"
    wrong = "wrong"


class AccusationAttempt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1)
    accuser_participant_id: str = Field(min_length=1)
    beat_id: str = Field(min_length=1)
    accused_cast_member_id: str = Field(min_length=1)
    outcome: AccusationOutcome
    catches_banked_at_submission: int = Field(ge=0)
    points_awarded: int
    motive_correct: bool | None = None
    method_correct: bool | None = None
    repeat_offense_count: int = Field(default=0, ge=0)
    lockout_until: datetime | None = None
    used_last_word: bool = False
    triggered_last_call: bool = False
    accusation_id: str | None = None
    submitted_at: datetime | None = None


class ScoreBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_points: int = Field(ge=0)
    catch_points: int = Field(ge=0)
    accusation_points: int
    motive_bonus: int = Field(ge=0)
    method_bonus: int = Field(ge=0)
    total: int
