# AW-211: Behavior Profile Assembly

**Milestone / Epic:** M2 / M2-E  
**Size:** M  
**Status:** Complete

## Plain-English Summary

Build runtime character context from behavior profile and live relationships.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/07-character-behavior.md S7.2` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build runtime character context from behavior profile and live relationships. Likely files affected: engine/characters, engine/tests.

## Acceptance Criteria

- [ ] Runtime character context includes personality, goals, secrets, tells, and relationship dispositions.
- [ ] Human-controlled and AI-driven characters use the same platform character object model.
- [ ] Tests cover context assembly for killer and non-killer characters.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-205
- AW-206

## Likely Files Affected

engine/characters, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/architecture/07-character-behavior.md S7.2
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
