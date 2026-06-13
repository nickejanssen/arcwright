# AW-235: Second Arc Schema Design

**Milestone / Epic:** M5 / M5-C  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Design one non-Nightcap arc schema to validate platform-clean architecture and prepare post-M6 executable follow-through.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/14-architecture-validation.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Design one non-Nightcap arc schema to validate platform-clean architecture and prepare post-M6 executable follow-through. Likely files affected: docs/specs, sample arc docs, docs/roadmap/tasks.

## Acceptance Criteria

- [ ] A non-Nightcap arc schema exists as a document or sample arc.
- [ ] Schema validates against ArcDefinition or documents exact validation gaps.
- [ ] The schema identifies the minimal executable product to be built after M6 proof.
- [ ] No second game implementation is added before M6 proof.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-203

## Likely Files Affected

docs/specs, sample arc docs, docs/roadmap/tasks

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
