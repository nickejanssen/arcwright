"""The two reports on a checked case (spec 0093, Part A).

The full report is for the case's author and names IDs. The summary is for
anyone who must stay unspoiled: it holds only each rule's name, pass or fail,
and counts. It never reads a label, text, ID or title from the case file.
"""

from __future__ import annotations

from engine.case.authored.rules import CaseCheck

_STATUS = {"pass": "PASS", "fail": "FAIL", "not_run": "NOT RUN"}


def _render(check: CaseCheck, *, title: str, with_detail: bool) -> str:
    lines = [title]
    for outcome in check.outcomes:
        lines.append(
            f"{outcome.rule} {outcome.name}: {_STATUS[outcome.status]} "
            f"(checked {outcome.checked}, problems {outcome.problem_count})"
        )
        if with_detail:
            lines.extend(f"    - {problem}" for problem in outcome.problems)
    counts = ", ".join(str(n) for n in check.participant_counts) or "none"
    lines.append(f"Participant counts checked: {counts}")
    if check.min_paid_choices is not None:
        lines.append(
            f"Fewest paid choices that solve the case: {check.min_paid_choices}"
        )
    lines.append("Result: " + ("PASS" if check.passed else "REFUSED"))
    return "\n".join(lines)


def summary_report(check: CaseCheck) -> str:
    """Rule names, pass or fail, and counts only."""
    return _render(
        check,
        title="Written case check (summary: names and counts only)",
        with_detail=False,
    )


def full_report(check: CaseCheck) -> str:
    """Everything, including IDs from the case file. For the author."""
    return _render(
        check,
        title="Written case check (full report, for the author)",
        with_detail=True,
    )
