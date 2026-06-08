# AW-216: SSE Fanout Filtering And Replay

**Milestone / Epic:** M3 / M3-A  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Deliver events to connected clients based on target audience and replay missed events.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/08-event-system.md S8.4-S8.6` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Deliver events to connected clients based on target audience and replay missed events. Likely files affected: engine/events, api/routers, engine/tests.

## Acceptance Criteria

- [ ] Specific-player events are delivered only to the matching player connection.
- [ ] Host-only, shared-display, and all-player events route to the documented connection sets.
- [ ] Reconnect replay uses sequence numbers to deliver missed events without duplicating already-seen events.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-215

## Likely Files Affected

engine/events, api/routers, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.

## Architecture References

- docs/architecture/08-event-system.md S8.4-S8.6
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
