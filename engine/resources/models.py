from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EffectFamily(str, Enum):
    insight = "insight"
    access = "access"
    tempo = "tempo"
    counterplay = "counterplay"
    risk_and_reward = "risk_and_reward"
    witness_pressure = "witness_pressure"
    information_control = "information_control"
    economy = "economy"
    mind_game = "mind_game"


class ResourceBalance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    current_amount: int = Field(default=0, ge=0)
    bank_cap: int = Field(ge=0)
    protected_floor: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_floor_below_cap(self) -> "ResourceBalance":
        if self.protected_floor > self.bank_cap:
            raise ValueError("protected_floor cannot exceed bank_cap")
        return self


class ResourceGrant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    amount: int = Field(gt=0)
    source: str | None = None
    beat_id: str = Field(min_length=1)
    timestamp: datetime


class ResourceSpend(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    amount: int = Field(gt=0)
    effect_key: str = Field(min_length=1)
    beat_id: str = Field(min_length=1)
    timestamp: datetime


class EffectDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    effect_key: str = Field(min_length=1)
    family: EffectFamily
    cost: int = Field(gt=0)
    requires_target: bool
    is_offensive: bool = False
    is_information_control: bool = False


class EffectActivation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    effect_key: str = Field(min_length=1)
    activator_id: str = Field(min_length=1)
    target_id: str | None = None
    interaction_window_id: str = Field(min_length=1)
    resolved_at: datetime | None = None
    source_reveal_at: datetime | None = None
