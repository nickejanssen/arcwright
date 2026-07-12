# AW-222: Five MVP Telemetry Signals

**Milestone / Epic:** M3 / M3-D  
**Size:** M  
**Status:** Complete

## Plain-English Summary

Wire all five minimum telemetry signals.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/11-telemetry.md S11.3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Wire all five minimum telemetry signals. Likely files affected: engine/telemetry, engine/events, engine/tests.

## Acceptance Criteria

- [ ] Beat transition, pacing intervention, knowledge constraint, session completion, and replay intent signals log with documented payload fields.
- [ ] A complete mocked session contains all five MVP telemetry signals.
- [ ] Required telemetry writes do not depend on `CONTENT_LOGGING_ENABLED=true`.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-220

## Likely Files Affected

engine/telemetry, engine/events, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/11-telemetry.md S11.3
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
