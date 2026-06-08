# AW-232: Adversarial Safety Playtest Protocol

**Milestone / Epic:** M5 / M5-A  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Create and run the adversarial safety playtest protocol.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/03-scope.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Create and run the adversarial safety playtest protocol. Likely files affected: docs/roadmap/tasks, GitHub issues/comments, docs/specs if needed.

## Acceptance Criteria

- [ ] Protocol covers dark-content edge cases, tone breaks, embarrassment attempts, prompt injection, and real-world harm probes.
- [ ] At least one adversarial safety run is completed before qualifying sessions.
- [ ] Findings are documented with severity, reproduction notes, and blocking status.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-231

## Likely Files Affected

docs/roadmap/tasks, GitHub issues/comments, docs/specs if needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/prd/03-scope.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
