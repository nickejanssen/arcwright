# AW-206: Killer Assignment And Reveal State

**Milestone / Epic:** M2 / M2-C  
**Size:** M  
**Status:** Complete

## Plain-English Summary

Resolve v1 constrained-random killer assignment behind the assignment interface and preserve reveal constraints.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/03-arc-execution.md S3.4-S3.7` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Resolve v1 constrained-random killer assignment behind the assignment interface and preserve reveal constraints. Likely files affected: engine/arc, engine/session, engine/tests.

## Acceptance Criteria

- [ ] Killer assignment uses the existing assignment interface and v1 constrained-random selection, then stores the assigned killer in session state.
- [ ] A seeded run produces the same killer assignment and reveal state when replayed with the same seed.
- [ ] Reveal cannot fire until authored reveal conditions are satisfied or a host-privileged bypass is logged.
- [ ] Mini-game behavioral signals are not wired into killer assignment in v1.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-204
- AW-205

## Likely Files Affected

engine/arc, engine/session, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/03-arc-execution.md S3.4-S3.7
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
