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

RETROFIT_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "docs/roadmap/operations/human-collaboration-open-work.md": (
        "| Issue | Task | Canonical path | Profiles | Founder input | Next gate |",
        "Missing stable task record",
    ),
    "docs/roadmap/tasks/AW-232-adversarial-safety-playtest-protocol.md": (
        "**Interaction profile:** Facilitated live operation.",
    ),
    "docs/roadmap/tasks/AW-233-safety-findings-remediation.md": (
        "**Interaction profile:** Independent execution.",
    ),
    "docs/roadmap/tasks/AW-234-gross-margin-by-player-count.md": (
        "**Interaction profile:** Decision interview.",
    ),
    "docs/roadmap/tasks/AW-235-second-arc-schema-design.md": (
        "**Interaction profile:** Independent execution.",
    ),
    "docs/roadmap/tasks/AW-236-live-knowledge-graph-inspection.md": (
        "**Interaction profile:** Independent execution.",
    ),
    "docs/roadmap/tasks/AW-237-read-only-arc-structure-inspection.md": (
        "**Interaction profile:** Independent execution.",
    ),
    "docs/roadmap/tasks/AW-238-live-event-stream-inspection.md": (
        "**Interaction profile:** Independent execution.",
    ),
    "docs/roadmap/tasks/AW-239-character-state-inspection.md": (
        "**Interaction profile:** Independent execution.",
    ),
    "docs/roadmap/tasks/AW-240-closed-playtest-operations-runbook.md": (
        "**Interaction profile:** Decision interview.",
    ),
    "docs/roadmap/tasks/AW-241-qualifying-session-instrumentation-checklist.md": (
        "**Interaction profile:** Decision interview.",
    ),
    "docs/roadmap/tasks/AW-242-founder-run-final-rehearsal.md": (
        "**Interaction profile:** Facilitated live operation.",
    ),
    "docs/roadmap/tasks/AW-243-five-outside-qualifying-sessions.md": (
        "**Interaction profile:** Facilitated live operation.",
    ),
    "docs/roadmap/tasks/AW-244-h1-proof-analysis-and-next-step-decision.md": (
        "**Interaction profile:** Decision interview.",
    ),
    "docs/roadmap/tasks/AW-245-second-arc-minimal-executable-product.md": (
        "**Interaction profile:** Independent execution.",
    ),
    "docs/roadmap/tasks/AW-266-rehearsal-2-tmst-real-human-session.md": (
        "**Interaction profile:** Facilitated live operation.",
    ),
    "docs/roadmap/tasks/AW-267-nightcap-art-direction-brief.md": (
        "**Interaction profile:** Creative collaboration.",
    ),
    "docs/roadmap/tasks/AW-268-nightcap-asset-pipeline-and-motion-system.md": (
        "**Interaction profiles:** Creative collaboration plus Decision interview.",
    ),
    "docs/roadmap/tasks/AW-269-nightcap-cloud-deploy.md": (
        "**Interaction profile:** Decision interview.",
    ),
    "docs/roadmap/tasks/AW-270-authorial-intent-block-and-fidelity-telemetry.md": (
        "**Interaction profile:** Independent execution.",
    ),
    "docs/roadmap/tasks/AW-271-narrative-obligations-model.md": (
        "**Interaction profile:** Independent execution.",
    ),
    "docs/roadmap/tasks/AW-272-continuity-coherence-eval-suite.md": (
        "**Interaction profile:** Independent execution.",
    ),
    "docs/roadmap/tasks/AW-273-rehearsal-1-execution.md": (
        "**Interaction profile:** Facilitated live operation.",
    ),
    "docs/roadmap/tasks/AW-274-platform-agnostic-role-outcome-vocabulary.md": (
        "**Interaction profile:** Decision interview.",
    ),
    "docs/roadmap/tasks/AW-275-design-system-follow-ups.md": (
        "**Interaction profile:** Independent execution.",
    ),
    "docs/roadmap/tasks/AW-276-arc-voice-block-injection.md": (
        "**Interaction profile:** Independent execution.",
    ),
    "docs/roadmap/tasks/AW-277-couch-race-narrator-transition-lines.md": (
        "**Interaction profile:** Creative collaboration.",
    ),
    "docs/roadmap/tasks/AW-278-couch-race-truth-sequence-and-reveal-accounting.md": (
        "**Interaction profile:** Creative collaboration.",
    ),
    "docs/roadmap/tasks/AW-279-detective-identity-and-opening-briefing.md": (
        "**Interaction profile:** Creative collaboration.",
    ),
    "docs/roadmap/tasks/AW-280-couch-race-clue-release-content.md": (
        "**Interaction profile:** Creative collaboration.",
    ),
    "docs/roadmap/tasks/AW-281-couch-race-arc-definition-and-case-generation.md": (
        "**Interaction profile:** Creative collaboration.",
    ),
    "docs/roadmap/tasks/AW-282-interrogation-round-loop-and-question-intents.md": (
        "**Interaction profile:** Creative collaboration.",
    ),
    "docs/roadmap/tasks/AW-283-suspect-answer-generation-and-contradiction-detection.md": (
        "**Interaction profile:** Creative collaboration.",
    ),
    "docs/roadmap/tasks/AW-284-race-scoring-and-accusation-state.md": (
        "**Interaction profile:** Creative collaboration.",
    ),
    "docs/roadmap/tasks/AW-285-couch-race-tv-and-phone-rendering.md": (
        "**Interaction profile:** Creative collaboration.",
    ),
    "docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md": (
        "**Interaction profile:** Facilitated live operation.",
    ),
    "docs/specs/0031-aw-245-second-arc-minimal-executable-product.md": (
        "# Human Collaboration Contract",
    ),
    "docs/specs/0039-aw-235-daily-case-second-arc-schema-design.md": (
        "# Human Collaboration Contract",
    ),
    "docs/specs/0064-aw-270-authorial-intent-block.md": (
        "# Human Collaboration Contract",
    ),
    "docs/specs/0065-aw-271-narrative-obligations-model.md": (
        "# Human Collaboration Contract",
    ),
    "docs/specs/0066-aw-272-continuity-coherence-evals.md": (
        "# Human Collaboration Contract",
    ),
    "docs/specs/0067-development-survey-and-path-to-first-playtest.md": (
        "# Human Collaboration Contract",
    ),
    "docs/specs/0068-game-experience-quality-bar.md": (
        "# Human Collaboration Contract",
    ),
    "docs/specs/0069-nightcap-visual-design-system.md": (
        "# Human Collaboration Contract",
    ),
    "docs/specs/0070-aw-274-platform-agnostic-role-outcome-vocabulary.md": (
        "# Human Collaboration Contract",
    ),
    "docs/specs/0072-nightcap-couch-race-v1.md": ("# Human Collaboration Contract",),
    "docs/specs/0073-aw-276-arc-voice-directive-injection.md": (
        "# Human Collaboration Contract",
    ),
    "docs/specs/0073-m5-canonical-reconciliation.md": (
        "# Human Collaboration Contract",
    ),
}


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
