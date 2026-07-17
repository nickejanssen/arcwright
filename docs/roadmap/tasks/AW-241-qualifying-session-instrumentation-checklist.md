# AW-241: Qualifying Session Instrumentation Checklist

**Milestone / Epic:** M6 / M6-A  
**Size:** S  
**Status:** Planned

## Plain-English Summary

Define the exact evidence checklist for qualifying sessions.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/02-requirements.md Qualitative gate` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Define the exact evidence checklist for qualifying sessions. Likely files affected: docs/roadmap/tasks, docs/playtest if created.

## Human Collaboration Contract

**Interaction profile:** Decision interview.

**Founder input:** Required evidence, acceptable observation burden,
qualification rules, privacy constraints, and practical recording workflow.

**Required flow:** Explain what each signal proves, how it is captured, what the
founder must inspect, and what would block qualification. Prepare a
walkthrough-ready checklist, present bounded alternatives for unresolved
instrumentation choices, and ask one focused interactive choice question at a
time.

**Gate:** The checklist cannot be declared ready for qualifying sessions until
the founder has walked through it and explicitly approved the evidence and
observation workflow.

**Evidence:** Preserve the checklist reviewed, alternatives, founder feedback,
explicit approval, approval date, and remaining owner actions.

## Acceptance Criteria

- [ ] Checklist maps completion, replay enthusiasm, personalization perception, telemetry, cost, and blockers to concrete evidence.
- [ ] Replay enthusiasm and personalization perception definitions match `docs/prd/02-requirements.md`.
- [ ] Checklist marks sessions missing telemetry evidence as non-qualifying until reviewed.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-240

## Likely Files Affected

docs/roadmap/tasks, docs/playtest if created

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/prd/02-requirements.md Qualitative gate
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
