# AW-230: Real-Device Privacy Matrix

**Milestone / Epic:** M4 / M4-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Verify all event audiences across real devices.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/08-event-system.md S8.4-S8.5` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Verify all event audiences across real devices. Likely files affected: test docs, external platform integration files.

## Acceptance Criteria

- [ ] The implementation satisfies the scope described in `docs/architecture/08-event-system.md S8.4-S8.5`.
- [ ] The work is small enough for one agent implementation session or is split before coding.
- [ ] Tests or verification evidence prove the task-specific behavior.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-227
- AW-229

## Likely Files Affected

test docs, external platform integration files

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not start this implementation until AW-202 selects the external Nightcap platform.

## Architecture References

- docs/architecture/08-event-system.md S8.4-S8.5
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
