"""Runtime fairness invariants for resolved cases.

Two invariants are asserted before a ResolvedCase is returned from the
resolver:

1. Solvability — the intersection of clue-implication sets (over the
   genuine clue chain, applied by a rational-actor solver) uniquely
   identifies one CastMember, and that member matches ``culprit_id``.
2. Lie falsifiability — every AuthorizedFalsehood's ``contradicted_by``
   list is non-empty AND every referenced evidence_id exists in the
   case's evidence list.
"""

from __future__ import annotations

from engine.case.models import ResolvedCase


def solvability_check(case: ResolvedCase) -> tuple[bool, str]:
    """Return (ok, detail).

    Applies the genuine clue chain: intersect all ``points_toward``
    sets from genuine evidence entries. The remaining set must be
    exactly ``{culprit_id}``.
    """
    genuine = [e for e in case.evidence if e.truth_value == "genuine"]
    if not genuine:
        return False, "no genuine evidence"

    implicate_sets = [set(e.points_toward) for e in genuine if e.points_toward]
    if not implicate_sets:
        return False, "no genuine evidence points toward any cast member"

    narrowed = set.intersection(*implicate_sets)

    exonerated: set[str] = set()
    for e in genuine:
        exonerated.update(e.points_away_from)
    narrowed -= exonerated

    if narrowed == {case.culprit_id}:
        return True, "unique culprit identified"
    return False, (
        f"genuine chain narrows to {sorted(narrowed)!r}; "
        f"expected culprit {case.culprit_id!r}"
    )


def lie_falsifiability_check(case: ResolvedCase) -> tuple[bool, str]:
    evidence_ids = {e.evidence_id for e in case.evidence}
    for lie in case.falsehoods:
        if not lie.contradicted_by:
            return False, f"lie {lie.falsehood_id!r} has no contradicting evidence"
        missing = [e for e in lie.contradicted_by if e not in evidence_ids]
        if missing:
            return False, (
                f"lie {lie.falsehood_id!r} references missing evidence {missing!r}"
            )
    return True, "all lies falsifiable"
