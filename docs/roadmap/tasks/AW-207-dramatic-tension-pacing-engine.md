# AW-207: Dramatic Tension Pacing Engine

**Milestone / Epic:** M2 / M2-B  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Compute dramatic tension and trigger pacing interventions from session signals.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/03-arc-execution.md S3.3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Compute dramatic tension and trigger pacing interventions from session signals. Likely files affected: engine/arc, engine/telemetry, engine/tests.

## Acceptance Criteria

- [ ] The implementation satisfies the scope described in `docs/architecture/03-arc-execution.md S3.3`.
- [ ] The work is small enough for one agent implementation session or is split before coding.
- [ ] Tests or verification evidence prove the task-specific behavior.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-204

## Likely Files Affected

engine/arc, engine/telemetry, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/03-arc-execution.md S3.3
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
