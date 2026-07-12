# AW-221: Narrator Bridge On Resume

**Milestone / Epic:** M3 / M3-C  
**Size:** S  
**Status:** Complete

## Plain-English Summary

Generate and emit a narrator recap when a session resumes.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/05-session-persistence.md S5.3-S5.4` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Generate and emit a narrator recap when a session resumes. Likely files affected: engine/session, engine/routing, engine/safety, engine/events.

## Acceptance Criteria

- [ ] Resume emits a narrator bridge ContentEvent before normal play continues.
- [ ] Narrator bridge generation uses the `narrator_bridge` routing task type.
- [ ] Bridge generation passes through L1, L2, and L3 safety handling.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-220

## Likely Files Affected

engine/session, engine/routing, engine/safety, engine/events

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/architecture/05-session-persistence.md S5.3-S5.4
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
