# AW-236: Live Knowledge Graph Inspection

**Milestone / Epic:** M5 / M5-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Build read-only live knowledge graph inspection.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/03-scope.md Visual Storyworld Roadmap` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build read-only live knowledge graph inspection. Likely files affected: dashboard, api, engine/knowledge.

This is the only Visual Storyworld inspection surface required for the M5 exit gate. Read-only arc structure, live event stream, and character state inspection may ship as logs or defer until after proof.

## Human Collaboration Contract

**Interaction profile:** Independent execution.

**Why independent:** `docs/prd/03-scope.md`, Architecture 04, dashboard privacy
rules, and the current acceptance criteria constrain this read-only inspection
surface.

**Required flow:** After normal plan approval, implement the constrained
diagnostic surface, explain what it exposes and how to inspect it, and verify
privacy behavior.

**Reclassification gate:** Stop and switch to Creative collaboration or
Decision interview before choosing a new visual direction, exposing additional
private state, adding editing capability, or expanding beyond the M5 exit gate.

**Evidence:** Preserve plan approval, privacy checks, representative inspection
evidence, test results, dates, and owner actions.

## Acceptance Criteria

- [ ] Read-only live knowledge graph inspection surface exists.
- [ ] Surface shows current knowledge state enough to diagnose clue and leak issues.
- [ ] Private information handling follows dashboard privacy rules.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-222

## Likely Files Affected

dashboard, api, engine/knowledge

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.
- Do not build Visual Storyworld editing in Phase 1.

## Architecture References

- docs/prd/03-scope.md Visual Storyworld Roadmap
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
