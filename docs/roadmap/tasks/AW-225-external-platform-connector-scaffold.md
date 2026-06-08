# AW-225: External Platform Connector Scaffold

**Milestone / Epic:** M4 / M4-A  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Implement the selected external platform connector scaffold after AW-202.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/02-Decisions-Log-Additions-May2026.md Entry 3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Implement the selected external platform connector scaffold after AW-202. Likely files affected: external platform integration files, sdk, api docs.

## Acceptance Criteria

- [ ] Task remains blocked until AW-202 records the external platform decision.
- [ ] Connector can create or attach to a Nightcap session using the selected platform contract.
- [ ] Connector subscribes to Arcwright events without requiring engine surface assumptions.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-202
- AW-224

## Likely Files Affected

external platform integration files, sdk, api docs

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not start this implementation until AW-202 selects the external Nightcap platform.
- Do not put arc execution logic in FastAPI route handlers.
- Do not put arc execution logic in TypeScript.

## Architecture References

- docs/02-Decisions-Log-Additions-May2026.md Entry 3
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
