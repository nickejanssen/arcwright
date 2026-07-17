#!/usr/bin/env python3
"""Verify Arcwright's human-collaboration contract and task profiles."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE_HEADING = "# Agent Operating Guide"

GLOBAL_REQUIREMENTS = {
    "docs/conventions/human-collaboration.md": (
        "## Interaction Profiles",
        "## Interview Contract",
        "## Approval Semantics",
        "## Required Phase Gates",
        "## Checkpoint Review Package",
    ),
    "AGENTS.md": ("## Human Collaboration Contract",),
    "docs/conventions/ai-contributions.md": ("human-collaboration",),
    "docs/conventions/review-checklist.md": ("collaboration profile",),
    "docs/agents/README.md": ("Collaboration Intake",),
    "docs/agents/product-steward.md": ("Human Collaboration",),
    "docs/agents/business-steward.md": ("Human Collaboration",),
    "docs/agents/system-architect.md": ("Human Collaboration",),
    "docs/agents/planner.md": ("Human Collaboration",),
    "docs/agents/spec-author.md": ("Human Collaboration",),
    "docs/agents/scribe.md": ("Human Collaboration",),
    "docs/skills/github-task-implementer/SKILL.md": ("Classify Human Collaboration",),
    "docs/skills/arcwright-reviewer/SKILL.md": ("Verify Human Collaboration Evidence",),
    "docs/specs/0000-template.md": ("# Human Collaboration Contract",),
    "docs/roadmap/operations/working-model.md": ("collaboration profile",),
    "docs/agents/USAGE.md": ("interactive", "numbered-choice fallback"),
}

RETROFIT_REQUIREMENTS: dict[str, tuple[str, ...]] = {}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def instruction_body(text: str) -> str:
    _, marker, body = text.partition(GUIDE_HEADING)
    if not marker:
        return ""
    return marker + body


def check_requirements(
    requirements: dict[str, tuple[str, ...]],
) -> list[str]:
    failures: list[str] = []
    for path, tokens in requirements.items():
        candidate = ROOT / path
        if not candidate.exists():
            failures.append(f"missing file: {path}")
            continue
        content = candidate.read_text(encoding="utf-8")
        for token in tokens:
            if token not in content:
                failures.append(f"{path}: missing token {token!r}")
    return failures


def check_mirror() -> list[str]:
    agents = instruction_body(read("AGENTS.md"))
    copilot = instruction_body(read(".github/copilot-instructions.md"))
    if not agents or not copilot:
        return ["instruction mirror is missing the Agent Operating Guide heading"]
    if agents != copilot:
        return ["AGENTS.md and Copilot instruction bodies differ"]
    return []


def run(phase: str) -> int:
    failures: list[str] = []
    if phase in {"global", "all"}:
        failures.extend(check_requirements(GLOBAL_REQUIREMENTS))
        failures.extend(check_mirror())
    if phase in {"retrofit", "all"}:
        failures.extend(check_requirements(RETROFIT_REQUIREMENTS))
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 2
    print(f"Human collaboration verification passed for phase: {phase}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--phase",
        choices=("global", "retrofit", "all"),
        default="all",
    )
    args = parser.parse_args()
    return run(args.phase)


if __name__ == "__main__":
    raise SystemExit(main())
