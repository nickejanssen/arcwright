# AW-208: L1 Hard Stops

**Milestone / Epic:** M2 / M2-D  
**Size:** S  
**Status:** Planned

## Plain-English Summary

Add deterministic hard-stop checks before generation.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/10-content-safety.md S10.2` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Add deterministic hard-stop checks before generation. Likely files affected: engine/safety, engine/tests.

## Acceptance Criteria

- [ ] All L1 hard-stop categories from `docs/architecture/10-content-safety.md` S10.2 are blocked before any model call.
- [ ] A blocked L1 event is logged as `safety_hard_stop` without exposing trigger details to the player.
- [ ] Tests prove L1 cannot be disabled by arc configuration.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-201

## Likely Files Affected

engine/safety, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/architecture/10-content-safety.md S10.2
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
