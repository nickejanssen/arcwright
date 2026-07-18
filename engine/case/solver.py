"""Synthetic detective, a bounded rational-actor solver for resolved cases.

The solver reads a ``ResolvedCase`` from a single player's point of view
and reports whether that player, given only the evidence text actually
delivered to them, can uniquely identify the culprit. This is the
Level-3 leg of AW-281's fairness proof stack.

Non-circularity
----------------
The solver never reads ``EvidenceEntry.points_toward`` or
``points_away_from``. Those fields are the resolver's own bookkeeping,
written by the same code that already knows who the culprit is, and
are consumed only by ``engine/case/invariants.py``'s
``solvability_check`` (a different, internal-consistency check). If the
solver read those fields too, it would just be checking the resolver's
labels against themselves, proving nothing about whether a human could
actually deduce the culprit from the clue text on the cards.

Instead the solver derives suspicion purely from evidence TEXT: it
scans each piece of evidence visible to the given participant for a
suspect's display name, and counts a hit as one point of suspicion
against that suspect. A case where the evidence text is meaningless,
blank, or never names anyone gives the solver nothing to work with and
it correctly reports no win, this is exactly the negative case a
fairness proof must be able to fail.

Visibility
----------
``ResolvedCase.visible_evidence_for(participant_id)`` returns only the
evidence a specific participant would actually see: group-delivered
evidence plus their own private evidence. Interrogation answers are
modeled as group-delivered (the suspect answers aloud, per the story
bible), so a full round of table interrogation is folded into every
viewpoint automatically without this module needing to simulate
interrogation rounds itself, that mechanic belongs to AW-282.
"""

from __future__ import annotations

import re
from collections import Counter

from pydantic import BaseModel, ConfigDict

from engine.case.models import ResolvedCase


class SolverVerdict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    culprit_id: str
    confidence: float
    won: bool


def synthetic_detective(
    case: ResolvedCase, viewpoint_participant_id: str
) -> SolverVerdict:
    """Solve ``case`` from one participant's actually-delivered evidence.

    Args:
        case: The resolved case to evaluate.
        viewpoint_participant_id: The participant whose visible evidence
            set the solver is restricted to. Required, there is no
            omniscient mode, an omniscient solver proves a different
            and weaker claim than "a player can solve this."
    """
    visible = case.visible_evidence_for(viewpoint_participant_id)
    suspects = case.members_by_role("suspect")
    scores: Counter[str] = Counter()

    for entry in visible:
        if entry.truth_value != "genuine":
            continue
        for suspect in suspects:
            pattern = r"\b" + re.escape(suspect.display_name) + r"\b"
            if re.search(pattern, entry.text):
                scores[suspect.member_id] += 1

    if not scores:
        return SolverVerdict(culprit_id="", confidence=0.0, won=False)

    ranked = scores.most_common()
    top_score = ranked[0][1]
    top_ids = [member_id for member_id, s in ranked if s == top_score]

    if len(top_ids) != 1:
        return SolverVerdict(culprit_id=top_ids[0], confidence=0.0, won=False)

    runner_up_score = ranked[1][1] if len(ranked) > 1 else 0
    confidence = top_score / (top_score + runner_up_score + 1e-9)
    won = top_ids[0] == case.culprit_id
    return SolverVerdict(culprit_id=top_ids[0], confidence=confidence, won=won)
