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
    """Generated axis-5 clue text, written to be readable evidence a
    player can act on: it names the object/vessel/location and, once
    a stage narrows to a suspect, names that suspect by display name."""

    points_toward: list[str]
    """CastMember member_ids this clue points toward. Used by the
    resolver's own solvability_check invariant; the synthetic
    detective solver does not read this field (see solver.py) so the
    fairness proof is not circular with the label that produced it."""

    points_away_from: list[str]
    """CastMember member_ids this clue points away from."""

    delivery: str
    """``group``, ``private``, ``split``, ``targeted``, reused from clue architecture."""

    delivery_target: Optional[str] = None
    """Participant id for private/targeted delivery; None for group.
    Always populated (a real participant id) when delivery is
    ``private`` or ``targeted``."""

    truth_value: str = "genuine"
    """``genuine`` or ``false_signal``, every false signal must be falsifiable."""


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
    """EvidenceEntry evidence_ids that contradict this lie. Non-empty
    by invariant, and semantically tied to the lie's topic: a
    ``location`` lie is contradicted by testimony placing the speaker
    elsewhere, a ``possession`` lie by a found object, etc. (see
    resolver.py's per-topic contradiction generation)."""


class CaseSkeleton(BaseModel):
    """Axis-1..4 authored content for a case type."""

    model_config = ConfigDict(extra="forbid")

    skeleton_id: str
    archetype: str
    """Axis 1, the shape of the crime."""

    method_family_id: str
    """Axis 1, which taxonomy method family this archetype draws its
    vessel/object/location and trace flourishes from, so generated
    evidence stays coherent with the authored archetype (a poisoning
    case never draws a suffocation trace)."""

    clue_chain_pattern: dict[str, Any]
    """Axis 2, the deduction sequence a solver must perform."""

    lie_shapes_by_role: dict[str, list[str]]
    """Axis 3, which lie topics each suspect archetype role can carry."""

    reveal_shape: dict[str, Any]
    """Axis 4, the rhythm of the Truth beat."""

    cast_size_override: Optional[int] = None
    """If set, force this skeleton to use a specific cast size regardless of player count."""


class CaseFact(BaseModel):
    """A single resolved case-truth fact, arc-agnostic.

    The fact graph is the ground-truth record a resolved case carries
    beyond the player-facing evidence/lie surface: who did what and
    why, what each suspect is hiding, how each suspect relates to the
    victim, and who knows each fact at session start. Evidence and lie
    text is generated from this graph so player-facing content stays
    traceable to a single source of truth instead of being fabricated
    independently.
    """

    model_config = ConfigDict(extra="forbid")

    fact_id: str
    predicate: str
    """Arc-defined predicate, e.g. ``method``, ``motive``, ``twist``,
    ``secret``, ``relationship``. Never a game-specific type name,
    the vocabulary lives in this string value, not in the schema."""

    subject_id: str
    """CastMember member_id this fact is primarily about."""

    object_id: str = ""
    """Optional second CastMember reference, e.g. the relationship
    target or the fact's beneficiary."""

    value: str
    """The resolved content: a method-family plus vessel description,
    a motive narrative, a secret, a relationship description, etc."""

    known_by: list[str] = Field(default_factory=list)
    """CastMember member_ids who know this fact at session start. Feeds
    the mandatory pre-generation knowledge-state query (platform
    architecture principle 5) once AW-283 wires character generation
    to this graph."""


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
    facts: list[CaseFact]
    reveal_shape: dict[str, Any]

    def members_by_role(self, role: str) -> list[CastMember]:
        """Return all cast members whose ``role`` string equals ``role``.

        Lets client code look up arc-defined role slots (e.g. ``"suspect"``,
        ``"victim"``, ``"witness"``) without the schema having to name them.
        """
        return [m for m in self.cast if m.role == role]

    def facts_by_predicate(self, predicate: str) -> list[CaseFact]:
        """Return all facts whose ``predicate`` string equals ``predicate``."""
        return [f for f in self.facts if f.predicate == predicate]

    def visible_evidence_for(self, participant_id: str) -> list[EvidenceEntry]:
        """Return evidence a specific participant can actually see.

        Group-delivered evidence is visible to every participant.
        Private and targeted evidence is visible only when its
        ``delivery_target`` matches ``participant_id``. This is the
        real per-player information partition, distinct from the
        omniscient union of ``self.evidence``.
        """
        return [
            e
            for e in self.evidence
            if e.delivery == "group" or e.delivery_target == participant_id
        ]
