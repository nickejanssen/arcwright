# AW-237: Read-Only Arc Structure Inspection

**Milestone / Epic:** M5 / M5-D  
**Size:** M  
**Status:** Deferred / Post-proof optional

## Plain-English Summary

Build read-only arc structure inspection.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/03-scope.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build read-only arc structure inspection. Likely files affected: dashboard, api, engine/arc.

This task is no longer an M5 exit-gate blocker. For M5, arc structure inspection may be satisfied by logs or deferred until after proof to protect the solo-founder critical path.

## Human Collaboration Contract

**Interaction profile:** Independent execution.

**Why independent:** `docs/prd/03-scope.md`, the deferred post-proof status,
AW-236, and the read-only acceptance criteria constrain this optional surface.

**Required flow:** After normal plan approval, implement only the documented
read-only view, explain how to inspect it, and verify that editing is impossible.

**Reclassification gate:** Stop and switch to Creative collaboration or
Decision interview before choosing a new visual direction, adding editing,
changing roadmap priority, or expanding the diagnostic scope.

**Evidence:** Preserve plan approval, read-only verification, representative
inspection evidence, test results, dates, and owner actions.

## Acceptance Criteria

- [ ] Read-only arc structure view exists.
- [ ] View shows beat graph and current beat for an attached session.
- [ ] Surface cannot edit arc structure.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-222
- AW-236

## Likely Files Affected

dashboard, api, engine/arc

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.
- Do not build Visual Storyworld editing in Phase 1.

## Architecture References

- docs/prd/03-scope.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
