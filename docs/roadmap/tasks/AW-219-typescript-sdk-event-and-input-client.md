# AW-219: TypeScript SDK Event And Input Client

**Milestone / Epic:** M3 / M3-B  
**Size:** M  
**Status:** Complete

## Plain-English Summary

Build the typed web SDK wrapper for event subscription and player input.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/09-developer-api.md S9.4` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build the typed web SDK wrapper for event subscription and player input. Likely files affected: sdk, api schemas if generation is needed.

## Acceptance Criteria

- [ ] ArcwrightClient exposes event subscription, input submission, current-character fetch, and disconnect behavior.
- [ ] Public SDK types are generated from or aligned with API schemas and avoid `any` in public interfaces.
- [ ] SDK typecheck and build pass without embedding arc execution logic.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-217
- AW-218

## Likely Files Affected

sdk, api schemas if generation is needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.
- Do not put arc execution logic in TypeScript.

## Architecture References

- docs/architecture/09-developer-api.md S9.4
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
