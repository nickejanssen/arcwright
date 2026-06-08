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

## Acceptance Criteria

- [ ] The implementation satisfies the scope described in `docs/prd/03-scope.md Visual Storyworld Roadmap`.
- [ ] The work is small enough for one agent implementation session or is split before coding.
- [ ] Tests or verification evidence prove the task-specific behavior.

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
