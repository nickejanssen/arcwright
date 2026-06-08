# AW-240: Closed Playtest Operations Runbook

**Milestone / Epic:** M6 / M6-A  
**Size:** S  
**Status:** Planned

## Plain-English Summary

Create the operational runbook for qualifying playtests.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/02-requirements.md Success criteria` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Create the operational runbook for qualifying playtests. Likely files affected: docs/roadmap/tasks, docs/playtest if created.

## Acceptance Criteria

- [ ] Runbook defines outside-group eligibility, consent steps, setup, host script, observer notes, and failure handling.
- [ ] Runbook explicitly excludes founder immediate-circle sessions from qualifying status.
- [ ] Runbook is reviewed before AW-242 final rehearsal.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-233
- AW-234
- AW-239

## Likely Files Affected

docs/roadmap/tasks, docs/playtest if created

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/prd/02-requirements.md Success criteria
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
