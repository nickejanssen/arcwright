# AW-231: M4 Real-Human Rehearsal

**Milestone / Epic:** M4 / M4-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Run a non-qualifying real-device rehearsal and log blockers.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/roadmap/milestones/M4-nightcap-experience-layer.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Run a non-qualifying real-device rehearsal on the Nightcap web experience runtime selected by AW-202 and log blockers. Likely files affected: docs/playtest notes or GitHub issue comments, docs/roadmap if needed.

## Acceptance Criteria

- [ ] A non-qualifying real-human rehearsal is attempted on real devices.
- [ ] Join timing, privacy result, completion state, and blockers are recorded.
- [ ] Every blocker is triaged into a follow-up issue before M5 begins.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-230

## Likely Files Affected

docs/playtest notes or GitHub issue comments, docs/roadmap if needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not bypass the AW-202 Nightcap web experience runtime contract.

## Architecture References

- docs/roadmap/milestones/M4-nightcap-experience-layer.md
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
