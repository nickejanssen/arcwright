"""Synthetic detective — bounded rational-actor solver for resolved cases.

The solver reads a ``ResolvedCase`` and reports whether a rational-actor
player, given the intended clue distribution and interrogation intents,
can uniquely identify the culprit. This is the Level-3 leg of AW-281's
fairness proof stack.

Algorithm
---------
1. Assemble a suspect-implication score for each cast member from all
   genuine evidence: each ``points_toward`` entry adds 1, each
   ``points_away_from`` entry subtracts 1.
2. For each authorized falsehood, if the solver has the contradicting
   evidence in hand, it detects the contradiction and adds a penalty
   to the speaker's suspicion score.
3. The suspect with the highest score is the solver's guess. If two
   are tied, the solver reports low confidence and no win.

The solver is deliberately dumb: it only uses information contained in
the resolved case object. Any case that a smart human could solve, the
solver should also solve — and if the solver can't, the case is
degenerate.
"""

from __future__ import annotations

from collections import Counter

from pydantic import BaseModel, ConfigDict

from engine.case.models import ResolvedCase


class SolverVerdict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    culprit_id: str
    confidence: float
    won: bool


def synthetic_detective(case: ResolvedCase) -> SolverVerdict:
    scores: Counter[str] = Counter()
    for e in case.evidence:
        if e.truth_value != "genuine":
            continue
        for member_id in e.points_toward:
            scores[member_id] += 1
        for member_id in e.points_away_from:
            scores[member_id] -= 1

    # Contradiction detection — if the solver has the contradicting
    # evidence in hand, add a suspicion penalty on the lying speaker.
    evidence_ids = {e.evidence_id for e in case.evidence}
    for lie in case.falsehoods:
        if any(eid in evidence_ids for eid in lie.contradicted_by):
            scores[lie.speaker_id] += 1

    if not scores:
        return SolverVerdict(culprit_id="", confidence=0.0, won=False)

    ranked = scores.most_common()
    top_score = ranked[0][1]
    top_ids = [mid for mid, s in ranked if s == top_score]

    if len(top_ids) != 1:
        return SolverVerdict(
            culprit_id=top_ids[0],
            confidence=0.0,
            won=False,
        )

    confidence = top_score / (
        top_score + (ranked[1][1] if len(ranked) > 1 else 0) + 1e-9
    )
    won = top_ids[0] == case.culprit_id
    return SolverVerdict(
        culprit_id=top_ids[0],
        confidence=confidence,
        won=won,
    )
