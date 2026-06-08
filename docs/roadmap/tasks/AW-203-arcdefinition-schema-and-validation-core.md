# AW-203: ArcDefinition Schema And Validation Core

**Milestone / Epic:** M2 / M2-B  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Implement the full Pydantic arc definition schema and validation behavior.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/09-developer-api.md S9.3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Implement the full Pydantic arc definition schema and validation behavior. Likely files affected: engine/arc/models.py, engine/tests, docs/specs.

## Acceptance Criteria

- [ ] ArcDefinition and nested models cover the fields documented in `docs/architecture/15-development-guide.md` S15.4.
- [ ] Validation rejects missing required fields, invalid beat graph references, invalid player counts, invalid pacing weight sums, and invalid narrator triggers.
- [ ] Tests include at least one valid arc fixture and at least five invalid arc fixtures tied to documented validation rules.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-201

## Likely Files Affected

engine/arc/models.py, engine/tests, docs/specs

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/09-developer-api.md S9.3
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
