"""Read a written case from disk and refuse it if it is unfair."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from engine.case.authored.models import AuthoredCase
from engine.case.authored.rules import (
    DEFAULT_CHOICE_BUDGET,
    MALFORMED,
    RULE_NAMES,
    AuthoredCaseRefused,
    CaseCheck,
    RuleOutcome,
    check_case,
)


def _malformed(problems: tuple[str, ...]) -> AuthoredCaseRefused:
    outcome = RuleOutcome(
        MALFORMED, RULE_NAMES[MALFORMED], "fail", len(problems), problems
    )
    return AuthoredCaseRefused(
        CaseCheck(outcomes=(outcome,), participant_counts=(), min_paid_choices=None)
    )


def parse_authored_case(raw: str | dict[str, Any]) -> AuthoredCase:
    """Build the models from JSON text or a dict, or refuse as malformed.

    Only the location and kind of each error is kept, never the offending
    value, because the value may be case text.
    """
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
        return AuthoredCase.model_validate(data)
    except json.JSONDecodeError as exc:
        raise _malformed(
            (f"not valid JSON at line {exc.lineno} column {exc.colno}",)
        ) from exc
    except ValidationError as exc:
        raise _malformed(
            tuple(
                f"{'.'.join(str(part) for part in e['loc'])}: {e['type']}"
                for e in exc.errors()
            )
        ) from exc


def check_authored_case_file(
    path: Path,
    *,
    beat_order: Sequence[str],
    budget: int = DEFAULT_CHOICE_BUDGET,
) -> tuple[AuthoredCase | None, CaseCheck]:
    """Read and check a case file. Returns the case (None if malformed) and
    the full check, whether it passed or not."""
    try:
        case = parse_authored_case(path.read_text(encoding="utf-8"))
    except AuthoredCaseRefused as refused:
        return None, refused.check
    return case, check_case(case, beat_order=beat_order, budget=budget)


def load_authored_case(
    path: Path,
    *,
    beat_order: Sequence[str],
    budget: int = DEFAULT_CHOICE_BUDGET,
) -> AuthoredCase:
    """Return the case, or raise ``AuthoredCaseRefused`` naming the first rule
    it breaks."""
    case, check = check_authored_case_file(path, beat_order=beat_order, budget=budget)
    if case is None or not check.passed:
        raise AuthoredCaseRefused(check)
    return case
