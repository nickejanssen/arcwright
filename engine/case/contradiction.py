"""Typed contradiction detection over case anchors (AW-290).

Comparison is on typed anchor fields only. Generated prose is never read
here: platform architecture principle 2 forbids inferring what happened
from generated text, and a model call per interrogation turn would
violate principle 6's cost-aware routing. A location falsehood and a
piece of evidence contradict each other exactly when they are anchored
to the same point in the case's own time sequence but different places,
an exact comparison of ``CaseAnchor.time_ordinal`` and
``CaseAnchor.location_ref``.
"""

from __future__ import annotations

from engine.case.models import ResolvedCase


def find_anchor_contradictions(case: ResolvedCase) -> list[tuple[str, str]]:
    """Return (falsehood_id, evidence_id) pairs contradicted by anchor comparison.

    A location falsehood contradicts an evidence entry when both are
    anchored to the same ``time_ordinal`` but different ``location_ref``
    values. Same place at the same time is consistent; a different time
    proves nothing either way.
    """
    pairs: list[tuple[str, str]] = []
    for falsehood in case.falsehoods:
        if falsehood.topic != "location" or falsehood.anchor_id is None:
            continue
        claimed = case.anchor_by_id(falsehood.anchor_id)
        if claimed is None:
            continue
        for entry in case.evidence:
            if entry.anchor_id is None:
                continue
            actual = case.anchor_by_id(entry.anchor_id)
            if actual is None:
                continue
            if (
                actual.time_ordinal == claimed.time_ordinal
                and actual.location_ref != claimed.location_ref
            ):
                pairs.append((falsehood.falsehood_id, entry.evidence_id))
    return pairs
