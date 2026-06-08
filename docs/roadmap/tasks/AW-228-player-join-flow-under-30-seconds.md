# AW-228: Player Join Flow Under 30 Seconds

**Milestone / Epic:** M4 / M4-C  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Build QR or code join flow for player devices.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/02-requirements.md Player experience` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build QR or code join flow for player devices. Likely files affected: external platform integration files, api join flow if needed.

## Acceptance Criteria

- [ ] The implementation satisfies the scope described in `docs/prd/02-requirements.md Player experience`.
- [ ] The work is small enough for one agent implementation session or is split before coding.
- [ ] Tests or verification evidence prove the task-specific behavior.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-225

## Likely Files Affected

external platform integration files, api join flow if needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not start this implementation until AW-202 selects the external Nightcap platform.
- Do not put arc execution logic in FastAPI route handlers.

## Architecture References

- docs/prd/02-requirements.md Player experience
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
