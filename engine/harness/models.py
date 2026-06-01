"""Pydantic models for deterministic harness runs."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class HarnessAction(BaseModel):
    transition_name: str
    payload: dict[str, Any] = Field(default_factory=dict)


class HarnessTraceEntry(BaseModel):
    step_index: int
    transition_name: str
    from_configuration: list[str]
    to_configuration: list[str]
    payload: dict[str, Any] = Field(default_factory=dict)


class HarnessSnapshot(BaseModel):
    step_index: int
    configuration: list[str]
    seed: int
    session_id: UUID


class HarnessRun(BaseModel):
    seed: int
    session_id: UUID
    arc_id: str
    configuration: list[str]
    step_index: int
    participants: list[str] = Field(default_factory=list)
    trace: list[HarnessTraceEntry]
