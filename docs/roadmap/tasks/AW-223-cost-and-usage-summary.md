# AW-223: Cost And Usage Summary

**Milestone / Epic:** M3 / M3-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Expose cost and usage summaries from generation logs.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/13-cost-model.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Expose cost and usage summaries from generation logs. Likely files affected: engine/telemetry, engine/routing, api/routers.

## Acceptance Criteria

- [ ] The implementation satisfies the scope described in `docs/architecture/13-cost-model.md`.
- [ ] The work is small enough for one agent implementation session or is split before coding.
- [ ] Tests or verification evidence prove the task-specific behavior.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-222

## Likely Files Affected

engine/telemetry, engine/routing, api/routers

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.
- Do not put arc execution logic in FastAPI route handlers.

## Architecture References

- docs/architecture/13-cost-model.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
