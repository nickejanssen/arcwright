# AW-226: Host Session Creation And Shared Display Flow

**Milestone / Epic:** M4 / M4-B  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Build host controls and shared display flow on the selected platform.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/02-requirements.md Host experience` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build host controls and shared display flow on the selected platform. Likely files affected: external platform integration files, sdk if needed.

## Acceptance Criteria

- [ ] Host can create, start, pause, resume, and end a session through the selected platform.
- [ ] Shared display shows only public or shared-display ContentEvents.
- [ ] Host controls use API lifecycle endpoints rather than bypassing the platform API.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-225

## Likely Files Affected

external platform integration files, sdk if needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not start this implementation until AW-202 selects the external Nightcap platform.
- Do not put arc execution logic in TypeScript.

## Architecture References

- docs/prd/02-requirements.md Host experience
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
