"""ContentEvent and presentation-hint models for the multi-surface event system.

Schema source of truth: docs/architecture/08-event-system.md S8.2.
Layered classification rationale: docs/decisions/0008-content-event-type-layering.md.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class AudienceTarget(str, Enum):
    all = "all"
    host_only = "host_only"
    specific_player = "specific_player"
    shared_display = "shared_display"


class EventCategory(str, Enum):
    narrative = "narrative"
    character_dialogue = "character_dialogue"
    private_delivery = "private_delivery"
    acknowledgement = "acknowledgement"
    state_transition = "state_transition"
    input_request = "input_request"
    system = "system"


class PresentationHints(BaseModel):
    emotion: Optional[str] = None
    urgency: Optional[str] = None
    voice_hint: Optional[str] = None
    animation_hint: Optional[str] = None
    lighting_hint: Optional[str] = None
    pause_before_ms: int = 0


class ContentEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    timestamp: datetime
    category: EventCategory
    event_type: str = Field(min_length=1)
    actor_id: Optional[UUID] = None
    target_audience: AudienceTarget
    target_player_id: Optional[UUID] = None
    payload: dict[str, Any] = Field(default_factory=dict)
    presentation_hints: PresentationHints = Field(default_factory=PresentationHints)
    sequence_number: int = 0

    @model_validator(mode="after")
    def _check_specific_player_target(self) -> "ContentEvent":
        if (
            self.target_audience is AudienceTarget.specific_player
            and self.target_player_id is None
        ):
            raise ValueError(
                "target_player_id is required when target_audience is specific_player"
            )
        if (
            self.target_audience is not AudienceTarget.specific_player
            and self.target_player_id is not None
        ):
            raise ValueError(
                "target_player_id may only be set when target_audience is specific_player"
            )
        return self
