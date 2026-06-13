# AW-205: Nightcap Canonical Arc JSON

**Milestone / Epic:** M2 / M2-C  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Create the canonical Nightcap arc definition at `nightcap/arc.json`.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/09-developer-api.md S9.3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Create the canonical Nightcap arc definition at `nightcap/arc.json`. Likely files affected: nightcap/arc.json, engine/tests.

## Acceptance Criteria

- [ ] `nightcap/arc.json` exists and validates against the ArcDefinition schema.
- [ ] The arc defines all eight Nightcap Story Circle beats with Nightcap content rails and knowledge rules.
- [ ] The arc supports the v1 four-human-player floor and explicitly preserves the M6 first-proof focus on 4 to 6 human players.
- [ ] The arc records that two- and three-player support depends on v1.1 interrogatable AI participants.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-203

## Likely Files Affected

nightcap/arc.json, engine/tests

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
