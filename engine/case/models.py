"""Pydantic domain models for arc-agnostic case resolution (AW-281).

Field-name policy: no murder-mystery-specific vocabulary. Strings like
``"suspect"``, ``"victim"``, ``"trace"`` live INSIDE ``role`` /
``evidence_type`` / ``topic`` string fields, populated by arc content.
See ``engine/case/README.md`` for the boundary policy.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class CastMember(BaseModel):
    model_config = ConfigDict(extra="forbid")

    member_id: str
    display_name: str
    role: str
    """Arc-defined role slot; nightcap uses ``suspect`` or ``victim``."""

    is_culprit: bool = False
    """Exactly one CastMember per case has is_culprit=True."""

    tags: list[str] = Field(default_factory=list)
    """Arc-specific tags (e.g. archetype role slot: ``intimate``, ``deflector``)."""


class EvidenceEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    evidence_type: str
    """Arc-defined family (``trace``, ``testimony``, ``document``, ``object``)."""

    text: str
    """Generated axis-5 clue text. Placeholder until later tasks."""

    points_toward: list[str]
    """CastMember member_ids this clue points toward."""

    points_away_from: list[str]
    """CastMember member_ids this clue points away from."""

    delivery: str
    """``group``, ``private``, ``split``, ``targeted`` — reused from clue architecture."""

    delivery_target: Optional[str] = None
    """Participant id for private/targeted; None for group."""

    truth_value: str = "genuine"
    """``genuine`` or ``false_signal`` — every false signal must be falsifiable."""


class AuthorizedFalsehood(BaseModel):
    model_config = ConfigDict(extra="forbid")

    falsehood_id: str
    speaker_id: str
    """CastMember member_id who tells this lie under interrogation."""

    topic: str
    """Arc-defined lie topic (``location``, ``relationship``, ``observation``, ``possession``)."""

    claim_text: str
    """The specific text of the lie (generated axis-5)."""

    contradicted_by: list[str]
    """EvidenceEntry evidence_ids that contradict this lie. Non-empty by invariant."""


class CaseSkeleton(BaseModel):
    """Axis-1..4 authored content for a case type."""

    model_config = ConfigDict(extra="forbid")

    skeleton_id: str
    archetype: str
    """Axis 1 — the shape of the crime."""

    clue_chain_pattern: dict[str, Any]
    """Axis 2 — the deduction sequence a solver must perform."""

    lie_shapes_by_role: dict[str, list[str]]
    """Axis 3 — which lie topics each suspect archetype role can carry."""

    reveal_shape: dict[str, Any]
    """Axis 4 — the rhythm of the Truth beat."""

    cast_size_override: Optional[int] = None
    """If set, force this skeleton to use a specific cast size regardless of player count."""


class ResolvedCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    arc_id: str
    seed: int
    skeleton_id: str
    cast: list[CastMember]
    culprit_id: str
    evidence: list[EvidenceEntry]
    falsehoods: list[AuthorizedFalsehood]
    reveal_shape: dict[str, Any]

    def members_by_role(self, role: str) -> list[CastMember]:
        """Return all cast members whose ``role`` string equals ``role``.

        Lets client code look up arc-defined role slots (e.g. ``"suspect"``,
        ``"victim"``, ``"witness"``) without the schema having to name them.
        """
        return [m for m in self.cast if m.role == role]
