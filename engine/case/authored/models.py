"""Typed models for a written case (format version 1).

Spec 0093, Part A. Every field of the file format lives in this one module,
so a field change is an edit here and, where a rule reads the field, in
``rules.py``. The names are generic on purpose: the engine does not learn
the vocabulary of any one game.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

FORMAT_VERSION = 1


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AuthoredCast(_Strict):
    """A character in the story. Becomes one character in the engine."""

    cast_id: str
    display_name: str
    knows: list[str] = Field(default_factory=list)
    nameable: bool = False
    """Whether a player may name this character in the final theory."""


class AuthoredSubject(_Strict):
    """Something a player can look into: a person, place, object or record."""

    subject_id: str
    kind: str
    label: str


class AuthoredConcept(_Strict):
    """A unit of information a player can hold."""

    concept_id: str
    label: str
    text: str
    standing: Literal["true", "misleading"]


class AuthoredOpportunity(_Strict):
    """One investigation choice."""

    opportunity_id: str
    subject_id: str
    label: str
    content: str
    beats: list[str] = Field(min_length=1)
    requires: list[str] = Field(default_factory=list)
    cost: int = Field(ge=0, le=1)
    """1 for a normal choice, 0 for a follow-up."""
    gives: list[str] = Field(min_length=1)


class AuthoredRoute(_Strict):
    """A set of concepts that together establish a truth."""

    concepts: list[str] = Field(min_length=1)


class AuthoredTruth(_Strict):
    """Something that must be established to solve the case."""

    truth_id: str
    routes: list[AuthoredRoute]


class AuthoredDeception(_Strict):
    """A misleading concept and the true concepts that expose it."""

    concept_id: str
    exposed_by: list[str]


class AuthoredAnswer(_Strict):
    """One accepted answer for a slot.

    ``value`` is a cast ID for a cast slot, a concept ID for a concept slot.
    ``needs`` are concepts a player must hold to be able to give the answer.
    For a concept slot the value itself is also needed.
    """

    value: str
    needs: list[str] = Field(default_factory=list)


class AuthoredSlot(_Strict):
    """One slot of the final theory."""

    slot_id: str
    label: str
    kind: Literal["cast", "concept"]
    accepted: list[AuthoredAnswer] = Field(min_length=1)
    shown_first: bool = False

    @model_validator(mode="after")
    def _cast_answers_state_their_needs(self) -> AuthoredSlot:
        if self.kind == "cast" and any(not a.needs for a in self.accepted):
            msg = "an accepted answer for a cast slot must list its needs"
            raise ValueError(msg)
        return self


class AuthoredCase(_Strict):
    """A whole written case."""

    case_id: str
    format_version: Literal[1]
    title: str
    supported_participant_counts: list[int] = Field(min_length=1)
    cast: list[AuthoredCast]
    subjects: list[AuthoredSubject]
    concepts: list[AuthoredConcept]
    opening: list[str]
    opportunities: list[AuthoredOpportunity]
    essential_truths: list[AuthoredTruth] = Field(min_length=1)
    deceptions: list[AuthoredDeception]
    solution: list[AuthoredSlot] = Field(min_length=1)
    closing: list[str]

    @model_validator(mode="after")
    def _one_slot_shown_first(self) -> AuthoredCase:
        if sum(1 for slot in self.solution if slot.shown_first) != 1:
            msg = "exactly one solution slot must be marked shown_first"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _counts_are_positive(self) -> AuthoredCase:
        if any(count < 1 for count in self.supported_participant_counts):
            msg = "supported_participant_counts must all be at least 1"
            raise ValueError(msg)
        return self
