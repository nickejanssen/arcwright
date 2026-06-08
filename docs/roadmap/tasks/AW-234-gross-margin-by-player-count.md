# AW-234: Gross Margin By Player Count

**Milestone / Epic:** M5 / M5-B  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Produce gross-margin readiness report for 4 through 10 players.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/13-cost-model.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Produce gross-margin readiness report for 4 through 10 players. Likely files affected: docs/roadmap/tasks, engine/telemetry or dashboard if implementation needed.

## Acceptance Criteria

- [ ] Cost report covers 4, 5, 6, 7, 8, 9, and 10 player sessions.
- [ ] Report separates actual logged model and infrastructure cost from open pricing assumptions.
- [ ] Gross-margin calculation assumptions are sourced or explicitly marked as open decisions.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-223
- AW-231

## Likely Files Affected

docs/roadmap/tasks, engine/telemetry or dashboard if implementation needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not build Visual Storyworld editing in Phase 1.

## Architecture References

- docs/architecture/13-cost-model.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
