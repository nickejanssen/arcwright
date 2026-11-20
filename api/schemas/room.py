"""Reply and request shapes for the room view, seat, survey and hand-over
routes (AW-331, spec 0095 M1, M3 and M6)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RoomPlayerResponse(BaseModel):
    participant_id: str
    display_name: Optional[str] = None
    ready: bool
    locked: bool
    answered_survey: bool
    is_host: bool


class RoomResponse(BaseModel):
    """What the shared screen rebuilds itself from. Public only: nothing here is
    private to a player, and it needs no sign-in."""

    session_status: str
    round_title: Optional[str] = None
    phase: Optional[str] = None
    phase_entry: Optional[int] = None
    deadline_at: Optional[datetime] = None
    seconds_left: Optional[float] = None
    paused: bool
    paused_by: Optional[str] = None
    lines: list[dict[str, Any]] = Field(default_factory=list)
    players: list[RoomPlayerResponse]
    ready_count: int
    player_count: int
    over: bool
    closing: Optional[dict[str, Any]] = None


class SeatResponse(BaseModel):
    participant_id: UUID
    display_name: Optional[str] = None
    role: Literal["host", "player"]


class SurveyRequest(BaseModel):
    answers: dict[str, int | str]
    comment: Optional[str] = None


class SurveyResponse(BaseModel):
    answered: bool
    answers: dict[str, int | str] = Field(default_factory=dict)
    comment: Optional[str] = None


class HandOverRequest(BaseModel):
    to_participant_id: UUID


class HandOverResponse(BaseModel):
    host_participant_id: UUID
