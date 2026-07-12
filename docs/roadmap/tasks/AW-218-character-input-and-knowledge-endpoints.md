# AW-218: Character Input And Knowledge Endpoints

**Milestone / Epic:** M3 / M3-B  
**Size:** M  
**Status:** Complete

## Plain-English Summary

Add player input and internal knowledge endpoint surfaces.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/09-developer-api.md S9.2` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Add player input and internal knowledge endpoint surfaces. Likely files affected: api/routers, api/schemas, engine/knowledge.

## Acceptance Criteria

- [ ] Player input endpoint accepts typed character action or dialogue input.
- [ ] Knowledge assert, revoke, and query endpoints are available only to host or internal engine callers as documented.
- [ ] Tests prove player clients cannot query another character private knowledge state.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-217

## Likely Files Affected

api/routers, api/schemas, engine/knowledge

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.

## Architecture References

- docs/architecture/09-developer-api.md S9.2
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
