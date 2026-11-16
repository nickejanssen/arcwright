"""The fairness rules A1 to A6 for a written case (spec 0093, Part A).

The check is pure rules and search. No model is called. Every rule returns
a ``RuleOutcome``; the author's detail lives in ``problems`` and is never
part of the founder's summary (see ``reports.py``).
"""

from __future__ import annotations

import heapq
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import count

from engine.case.authored.models import (
    AuthoredAnswer,
    AuthoredCase,
    AuthoredSlot,
)

DEFAULT_CHOICE_BUDGET = 6

MALFORMED = "A0"
RULE_NAMES: dict[str, str] = {
    "A0": "malformed_file",
    "A1": "ids_duplicate_or_unknown",
    "A2": "truth_not_redundant",
    "A3": "case_not_solvable_in_budget",
    "A4": "deception_not_exposable",
    "A5": "opportunity_unreachable_or_beat_thin",
    "A6": "answer_unobtainable_or_slot_too_easy",
}


@dataclass(frozen=True)
class RuleOutcome:
    rule: str
    name: str
    status: str
    """``pass``, ``fail`` or ``not_run`` (an earlier rule failed first)."""
    checked: int
    problems: tuple[str, ...]

    @property
    def problem_count(self) -> int:
        return len(self.problems)


@dataclass(frozen=True)
class CaseCheck:
    outcomes: tuple[RuleOutcome, ...]
    participant_counts: tuple[int, ...]
    min_paid_choices: int | None

    @property
    def passed(self) -> bool:
        return all(o.status == "pass" for o in self.outcomes)

    @property
    def first_failure(self) -> RuleOutcome | None:
        return next((o for o in self.outcomes if o.status == "fail"), None)


class AuthoredCaseRefused(Exception):
    """A case was refused. ``str()`` is the rule's name only, so logs stay clean.

    The author's detail is on ``check``.
    """

    def __init__(self, check: CaseCheck) -> None:
        failure = check.first_failure
        assert failure is not None
        super().__init__(failure.name)
        self.check = check
        self.rule = failure.rule
        self.name = failure.name


def check_case(
    case: AuthoredCase,
    *,
    beat_order: Sequence[str],
    budget: int = DEFAULT_CHOICE_BUDGET,
) -> CaseCheck:
    """Run A1 to A6. ``beat_order`` is the arc's beats, first to last."""
    ids_outcome = _a1_ids(case, beat_order)
    outcomes = [ids_outcome]
    min_paid: int | None = None
    if ids_outcome.status == "fail":
        outcomes.extend(_not_run(rule) for rule in ("A2", "A3", "A4", "A5", "A6"))
    else:
        order = tuple(beat_order)
        outcomes.append(_a2_redundancy(case, order))
        a3, min_paid = _a3_solvable(case, order, budget)
        outcomes.append(a3)
        outcomes.append(_a4_deceptions(case, order))
        outcomes.append(_a5_reachable(case, order))
        outcomes.append(_a6_answers(case, order))
    return CaseCheck(
        outcomes=tuple(outcomes),
        participant_counts=tuple(case.supported_participant_counts),
        min_paid_choices=min_paid,
    )


def _not_run(rule: str) -> RuleOutcome:
    return RuleOutcome(rule, RULE_NAMES[rule], "not_run", 0, ())


def _outcome(rule: str, checked: int, problems: list[str]) -> RuleOutcome:
    return RuleOutcome(
        rule,
        RULE_NAMES[rule],
        "fail" if problems else "pass",
        checked,
        tuple(problems),
    )


# --- A1: ids -----------------------------------------------------------------


def _a1_ids(case: AuthoredCase, beat_order: Sequence[str]) -> RuleOutcome:
    problems: list[str] = []
    checked = 0

    id_groups: dict[str, list[str]] = {
        "cast": [c.cast_id for c in case.cast],
        "subject": [s.subject_id for s in case.subjects],
        "concept": [c.concept_id for c in case.concepts],
        "opportunity": [o.opportunity_id for o in case.opportunities],
        "essential truth": [t.truth_id for t in case.essential_truths],
        "solution slot": [s.slot_id for s in case.solution],
        "beat": list(beat_order),
    }
    for kind, ids in id_groups.items():
        checked += len(ids)
        for item, number in Counter(ids).items():
            if number > 1:
                problems.append(f"duplicate {kind} id {item!r} ({number} times)")

    cast_ids = set(id_groups["cast"])
    subject_ids = set(id_groups["subject"])
    concept_ids = set(id_groups["concept"])
    beat_ids = set(beat_order)

    def known(kind: str, known_ids: set[str], where: str, ref: str) -> None:
        nonlocal checked
        checked += 1
        if ref not in known_ids:
            problems.append(f"{where} refers to unknown {kind} {ref!r}")

    for cast in case.cast:
        for ref in cast.knows:
            known("concept", concept_ids, f"cast {cast.cast_id!r}", ref)
    for ref in case.opening:
        known("concept", concept_ids, "opening", ref)
    for opp in case.opportunities:
        where = f"opportunity {opp.opportunity_id!r}"
        known("subject", subject_ids, where, opp.subject_id)
        for ref in opp.beats:
            known("beat", beat_ids, where, ref)
        for ref in [*opp.requires, *opp.gives]:
            known("concept", concept_ids, where, ref)
    for truth in case.essential_truths:
        for number, route in enumerate(truth.routes, start=1):
            for ref in route.concepts:
                known(
                    "concept",
                    concept_ids,
                    f"truth {truth.truth_id!r} route {number}",
                    ref,
                )
    for deception in case.deceptions:
        where = f"deception {deception.concept_id!r}"
        known("concept", concept_ids, where, deception.concept_id)
        for ref in deception.exposed_by:
            known("concept", concept_ids, where, ref)
    for slot in case.solution:
        where = f"slot {slot.slot_id!r}"
        value_ids = cast_ids if slot.kind == "cast" else concept_ids
        for answer in slot.accepted:
            known(slot.kind, value_ids, where, answer.value)
            for ref in answer.needs:
                known("concept", concept_ids, where, ref)
    return _outcome("A1", checked, problems)


# --- shared search helpers -----------------------------------------------------


def _reach(
    case: AuthoredCase,
    beat_order: Sequence[str],
    removed: frozenset[str] = frozenset(),
) -> tuple[frozenset[str], frozenset[str]]:
    """Everything a player could ever hold, and every opportunity they could
    ever take, ignoring the budget but obeying beats and prerequisites."""
    held = set(case.opening)
    taken: set[str] = set()
    for beat in beat_order:
        changed = True
        while changed:
            changed = False
            for opp in case.opportunities:
                oid = opp.opportunity_id
                if oid in removed or oid in taken or beat not in opp.beats:
                    continue
                if set(opp.requires) <= held:
                    taken.add(oid)
                    held.update(opp.gives)
                    changed = True
    return frozenset(held), frozenset(taken)


def _answer_needs(slot: AuthoredSlot, answer: AuthoredAnswer) -> set[str]:
    needs = set(answer.needs)
    if slot.kind == "concept":
        needs.add(answer.value)
    return needs


def _route_done(case: AuthoredCase, held: frozenset[str]) -> bool:
    return all(
        any(set(route.concepts) <= held for route in truth.routes)
        for truth in case.essential_truths
    )


def _slots_done(case: AuthoredCase, held: frozenset[str]) -> bool:
    return all(
        any(_answer_needs(slot, a) <= held for a in slot.accepted)
        for slot in case.solution
    )


# --- A2: redundancy ----------------------------------------------------------


def _a2_redundancy(case: AuthoredCase, beat_order: Sequence[str]) -> RuleOutcome:
    problems: list[str] = []
    full_held, _ = _reach(case, beat_order)
    reach_without = {
        opp.opportunity_id: _reach(case, beat_order, frozenset({opp.opportunity_id}))[0]
        for opp in case.opportunities
    }
    for truth in case.essential_truths:
        if len(truth.routes) < 2:
            problems.append(f"truth {truth.truth_id!r} has fewer than two routes")
            continue
        if not any(set(r.concepts) <= full_held for r in truth.routes):
            continue
        for oid, held in reach_without.items():
            if not any(set(r.concepts) <= held for r in truth.routes):
                problems.append(
                    f"truth {truth.truth_id!r}: every route needs opportunity {oid!r}"
                )
    return _outcome("A2", len(case.essential_truths), problems)


# --- A3: solvable by one player within the budget ------------------------------


def _a3_solvable(
    case: AuthoredCase, beat_order: Sequence[str], budget: int
) -> tuple[RuleOutcome, int | None]:
    best = _min_paid_choices(case, beat_order, budget)
    problems: list[str] = []
    if best is None:
        paid = sum(1 for o in case.opportunities if o.cost > 0)
        needed = _min_paid_choices(case, beat_order, paid)
        detail = (
            "cannot be solved at all"
            if needed is None
            else f"needs {needed} paid choices, budget is {budget}"
        )
        problems.extend(
            f"participant count {n}: {detail}"
            for n in case.supported_participant_counts
        )
    return (
        _outcome("A3", len(case.supported_participant_counts), problems),
        best,
    )


def _min_paid_choices(
    case: AuthoredCase, beat_order: Sequence[str], budget: int
) -> int | None:
    """Fewest paid choices one player needs to reach a route to every truth and
    hold an accepted answer for every slot. Exact search, no model."""

    def close_free(held: frozenset[str], beat: str) -> frozenset[str]:
        current = set(held)
        changed = True
        while changed:
            changed = False
            for opp in case.opportunities:
                if (
                    opp.cost == 0
                    and beat in opp.beats
                    and set(opp.requires) <= current
                    and not set(opp.gives) <= current
                ):
                    current.update(opp.gives)
                    changed = True
        return frozenset(current)

    layer: dict[frozenset[str], int] = {frozenset(case.opening): 0}
    for beat in beat_order:
        best: dict[frozenset[str], int] = {}
        heap: list[tuple[int, int, frozenset[str]]] = []
        tie = count()
        for held, spent in layer.items():
            closed = close_free(held, beat)
            if spent < best.get(closed, budget + 1):
                best[closed] = spent
                heapq.heappush(heap, (spent, next(tie), closed))
        while heap:
            spent, _, held = heapq.heappop(heap)
            if spent > best[held] or spent >= budget:
                continue
            for opp in case.opportunities:
                if (
                    opp.cost == 0
                    or beat not in opp.beats
                    or not set(opp.requires) <= held
                    or set(opp.gives) <= held
                ):
                    continue
                grown = close_free(held | frozenset(opp.gives), beat)
                if spent + 1 < best.get(grown, budget + 1):
                    best[grown] = spent + 1
                    heapq.heappush(heap, (spent + 1, next(tie), grown))
        layer = best

    done = [
        spent
        for held, spent in layer.items()
        if _route_done(case, held) and _slots_done(case, held)
    ]
    return min(done) if done else None


# --- A4: deceptions ------------------------------------------------------------


def _a4_deceptions(case: AuthoredCase, beat_order: Sequence[str]) -> RuleOutcome:
    problems: list[str] = []
    held, _ = _reach(case, beat_order)
    standing = {c.concept_id: c.standing for c in case.concepts}
    misleading = [c.concept_id for c in case.concepts if c.standing == "misleading"]
    by_concept = {d.concept_id: d for d in case.deceptions}
    for concept_id in misleading:
        deception = by_concept.get(concept_id)
        if deception is None or not deception.exposed_by:
            problems.append(
                f"misleading concept {concept_id!r} has nothing exposing it"
            )
            continue
        true_exposers = [e for e in deception.exposed_by if standing[e] == "true"]
        if not true_exposers:
            problems.append(f"misleading concept {concept_id!r} has no true exposer")
        elif not any(e in held for e in true_exposers):
            problems.append(f"exposers of {concept_id!r} can never be obtained")
    problems.extend(
        f"deception names {d.concept_id!r}, which is not misleading"
        for d in case.deceptions
        if standing[d.concept_id] != "misleading"
    )
    return _outcome("A4", len(misleading), problems)


# --- A5: reachable opportunities, enough choices per beat ----------------------


def _a5_reachable(case: AuthoredCase, beat_order: Sequence[str]) -> RuleOutcome:
    problems: list[str] = []
    _, taken = _reach(case, beat_order)
    problems.extend(
        f"opportunity {o.opportunity_id!r} can never become available"
        for o in case.opportunities
        if o.opportunity_id not in taken
    )
    opening = set(case.opening)
    choice_beats = [
        beat for beat in beat_order if any(beat in o.beats for o in case.opportunities)
    ]
    for beat in choice_beats:
        fresh = sum(
            1
            for o in case.opportunities
            if beat in o.beats and set(o.requires) <= opening
        )
        if fresh < 2:
            problems.append(f"beat {beat!r} offers a fresh player {fresh} choice(s)")
    return _outcome("A5", len(case.opportunities) + len(choice_beats), problems)


# --- A6: answers ---------------------------------------------------------------


def _a6_answers(case: AuthoredCase, beat_order: Sequence[str]) -> RuleOutcome:
    problems: list[str] = []
    held, _ = _reach(case, beat_order)
    for slot in case.solution:
        accepted_values = {a.value for a in slot.accepted}
        for answer in slot.accepted:
            if not _answer_needs(slot, answer) <= held:
                problems.append(
                    f"slot {slot.slot_id!r}: accepted answer {answer.value!r} "
                    "needs a concept that can never be obtained"
                )
        wrong = _wrong_answers(case, slot, accepted_values, held)
        if len(wrong) < 2:
            problems.append(
                f"slot {slot.slot_id!r} has {len(wrong)} obtainable wrong answer(s)"
            )
    return _outcome("A6", len(case.solution), problems)


def _wrong_answers(
    case: AuthoredCase,
    slot: AuthoredSlot,
    accepted_values: set[str],
    held: frozenset[str],
) -> list[str]:
    if slot.kind == "cast":
        return [
            c.cast_id
            for c in case.cast
            if c.nameable and c.cast_id not in accepted_values
        ]
    return [
        c.concept_id
        for c in case.concepts
        if c.standing == "misleading"
        and c.concept_id in held
        and c.concept_id not in accepted_values
    ]
