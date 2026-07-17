# AW-235: Second Arc Schema Design

**Milestone / Epic:** M5 / M5-C  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Design Daily Case, a non-Nightcap solo daily interrogation arc, to validate platform-clean architecture and prepare post-M6 executable follow-through.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/14-architecture-validation.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Design Daily Case as the canonical second arc: a solo, asynchronous, sub-10-minute daily interrogation experience with one AI suspect, week-long memory, contradiction accumulation, and final accusation. Likely files affected: docs/specs, docs/story-bibles, docs/roadmap/tasks.

## Human Collaboration Contract

**Interaction profile:** Independent execution.

**Why independent:** `docs/specs/0039-aw-235-daily-case-second-arc-schema-design.md`,
the Daily Case story bible, and Architecture 14 constrain the design and the
post-M6 boundary.

**Required flow:** After normal plan approval, implement the documented schema
design, explain validation gaps and deliverables clearly, and verify against the
canonical constraints.

**Reclassification gate:** Stop and switch to Creative collaboration or
Decision interview before inventing new story direction, expanding product
scope, changing the post-M6 sequence, or selecting a new schema policy.

**Evidence:** Preserve plan approval, canonical-source references, validation
results, identified gaps, dates, and owner actions.

## Acceptance Criteria

- [ ] A canonical Daily Case design exists as a story bible and implementation spec.
- [ ] The schema validates against ArcDefinition or documents exact validation gaps.
- [ ] The design identifies the minimum persisted state for cross-day suspect memory, contradiction tracking, and accusation resolution.
- [ ] The design states which capability gaps Daily Case closes beyond Nightcap and Monster RPG.
- [ ] The schema identifies the minimal executable product to be built after M6 proof.
- [ ] No second game implementation is added before M6 proof.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-203

## Likely Files Affected

docs/specs, docs/story-bibles, docs/roadmap/tasks

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/14-architecture-validation.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
