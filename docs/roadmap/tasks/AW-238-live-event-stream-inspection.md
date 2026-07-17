# AW-238: Live Event Stream Inspection

**Milestone / Epic:** M5 / M5-D  
**Size:** M  
**Status:** Deferred / Post-proof optional

## Plain-English Summary

Build live event stream inspection.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/08-event-system.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build live event stream inspection. Likely files affected: dashboard, api, engine/events.

This task is no longer an M5 exit-gate blocker. For M5, event stream inspection may be satisfied by logs or deferred until after proof to protect the solo-founder critical path.

## Human Collaboration Contract

**Interaction profile:** Independent execution.

**Why independent:** Architecture 08, the deferred post-proof status, AW-236,
and the privacy acceptance criteria constrain this optional event view.

**Required flow:** After normal plan approval, implement only the documented
inspection fields, explain how to review the stream, and verify audience and
private-payload filtering.

**Reclassification gate:** Stop and switch to Creative collaboration or
Decision interview before choosing a new visual direction, exposing additional
payload data, changing roadmap priority, or expanding the diagnostic scope.

**Evidence:** Preserve plan approval, privacy checks, representative event-view
evidence, test results, dates, and owner actions.

## Acceptance Criteria

- [ ] Live event stream inspection surface exists.
- [ ] View shows sequence number, event type, target audience, and timestamp.
- [ ] Private payload handling prevents broad exposure of private clue text.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-222
- AW-236

## Likely Files Affected

dashboard, api, engine/events

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.
- Do not build Visual Storyworld editing in Phase 1.

## Architecture References

- docs/architecture/08-event-system.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
