# AW-214: M2 Headless Nightcap Exit Harness

**Milestone / Epic:** M2 / M2-B  
**Size:** M  
**Status:** Complete

## Plain-English Summary

Prove the full M2 exit gate offline.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Prove the full M2 exit gate offline. Likely files affected: engine/tests, docs/roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md.

## Acceptance Criteria

- [ ] Headless harness completes all eight Nightcap Story Circle beats.
- [ ] Harness trace shows killer assignment, reveal firing, safety pre-generation checks, and no knowledge leaks.
- [ ] Harness path uses mocked routing and spends no real provider tokens.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-206
- AW-207
- AW-212
- AW-213

## Likely Files Affected

engine/tests, docs/roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
