# AW-233: Safety Findings Remediation

**Milestone / Epic:** M5 / M5-A  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Resolve or explicitly defer adversarial safety findings.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/conventions/review-checklist.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Resolve or explicitly defer adversarial safety findings. Likely files affected: GitHub issues, docs/roadmap, engine/safety if fixes are created in later tasks.

## Acceptance Criteria

- [ ] Every blocking adversarial finding has a linked fix or explicit human-approved deferral.
- [ ] Resolved findings have retest evidence.
- [ ] No high-severity unresolved safety blocker remains before M6 begins.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-232

## Likely Files Affected

GitHub issues, docs/roadmap, engine/safety if fixes are created in later tasks

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/conventions/review-checklist.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
