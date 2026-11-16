"""Written-case format, loader and fairness check (spec 0093, Part A).

A case written by a person, in one JSON file. The loader refuses an unfair
case with a named reason. Separate from the generated-case resolver in
``engine.case``, which is untouched.
"""

from __future__ import annotations

from engine.case.authored.loader import (
    check_authored_case_file,
    load_authored_case,
    parse_authored_case,
)
from engine.case.authored.models import (
    FORMAT_VERSION,
    AuthoredAnswer,
    AuthoredCase,
    AuthoredCast,
    AuthoredConcept,
    AuthoredDeception,
    AuthoredOpportunity,
    AuthoredRoute,
    AuthoredSlot,
    AuthoredSubject,
    AuthoredTruth,
)
from engine.case.authored.reports import full_report, summary_report
from engine.case.authored.rules import (
    DEFAULT_CHOICE_BUDGET,
    RULE_NAMES,
    AuthoredCaseRefused,
    CaseCheck,
    RuleOutcome,
    check_case,
)

__all__ = [
    "DEFAULT_CHOICE_BUDGET",
    "FORMAT_VERSION",
    "RULE_NAMES",
    "AuthoredAnswer",
    "AuthoredCase",
    "AuthoredCaseRefused",
    "AuthoredCast",
    "AuthoredConcept",
    "AuthoredDeception",
    "AuthoredOpportunity",
    "AuthoredRoute",
    "AuthoredSlot",
    "AuthoredSubject",
    "AuthoredTruth",
    "CaseCheck",
    "RuleOutcome",
    "check_authored_case_file",
    "check_case",
    "full_report",
    "load_authored_case",
    "parse_authored_case",
    "summary_report",
]
