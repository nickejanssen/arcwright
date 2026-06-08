# AW-201: M2-M6 Roadmap and Tracker Bootstrap

**Milestone / Epic:** M2 / Roadmap bootstrap  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Create the canonical roadmap docs, AW-201 spec, tracker config, GitHub milestones, and GitHub issues for M2 through M6.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/specs/0006-roadmap-organization.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Create the canonical roadmap docs, AW-201 spec, tracker config, GitHub milestones, and GitHub issues for M2 through M6. Likely files affected: docs/roadmap/**, docs/specs/0020-aw-201-m2-m6-roadmap-and-tracker-bootstrap.md, .github/tracker/*.json.

## Acceptance Criteria

- [ ] Roadmap docs exist for every planned M2-M6 epic and AW-201 through AW-244 task.
- [ ] `docs/specs/0020-aw-201-m2-m6-roadmap-and-tracker-bootstrap.md` exists.
- [ ] `docs/roadmap/index.json` validates and includes all new docs and live GitHub issue references.
- [ ] GitHub labels, milestones, epics, and task issues are created without modifying closed M1 issues.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- M1 complete

## Likely Files Affected

docs/roadmap/**, docs/specs/0020-aw-201-m2-m6-roadmap-and-tracker-bootstrap.md, .github/tracker/*.json

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/specs/0006-roadmap-organization.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
