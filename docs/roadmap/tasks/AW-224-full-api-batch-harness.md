# AW-224: Full API Batch Harness

**Milestone / Epic:** M3 / M3-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Run repeated complete sessions through the API path.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/12-build-plan.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Run repeated complete sessions through the API path. Likely files affected: engine/tests, api tests, scripts if needed.
The current repo state still uses a detached `HarnessRunner` in the proof path; AW-255 tracks the remaining REST-backed session loop work that closes that gap.

## Acceptance Criteria

- [ ] Batch harness runs 10 complete sessions through API-level flows.
- [ ] Each batch run records seed, pass/fail status, and telemetry signal presence.
- [ ] Batch harness uses mocked generation and spends no real provider tokens.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-219
- AW-223

## Likely Files Affected

engine/tests, api tests, scripts if needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.

## Architecture References

- docs/architecture/12-build-plan.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
