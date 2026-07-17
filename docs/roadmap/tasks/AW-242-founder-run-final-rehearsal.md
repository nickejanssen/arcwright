# AW-242: Founder-Run Final Rehearsal

**Milestone / Epic:** M6 / M6-A  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Run the final non-qualifying rehearsal before outside groups.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/roadmap/milestones/M6-first-qualifying-sessions.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Run the final non-qualifying rehearsal before outside groups. Likely files affected: GitHub issue comments, docs/playtest notes if created.

## Human Collaboration Contract

**Interaction profile:** Facilitated live operation.

**Founder input:** Rehearsal readiness, walkthrough feedback, live go or no-go,
host experience, and the final debrief.

**Required phases:**

1. Prepare the environment and show the evidence collected.
2. Run preflight checks and explain what the founder must inspect, record, and
   treat as blocking.
3. Conduct a guided walkthrough or smoke test and capture feedback.
4. Pause for the founder's explicit go or no-go decision.
5. Facilitate the live rehearsal with visible checkpoints and stop conditions.
6. Debrief with focused interactive questions and summarize findings.
7. Propose remediation options and obtain approval before another live run.

**Gate:** The final rehearsal does not begin until the founder explicitly
approves readiness. Any failed blocking check returns the task to preparation.

**Evidence:** Preserve preflight output, walkthrough feedback, go or no-go,
session observations, debrief responses, remediation decision, dates, and owner
actions.

## Acceptance Criteria

- [ ] Final rehearsal completes or records blockers with owner and severity.
- [ ] Telemetry and all four inspection surfaces are verified during rehearsal.
- [ ] No blocker remains untriaged before AW-243 starts.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-241

## Likely Files Affected

GitHub issue comments, docs/playtest notes if created

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/roadmap/milestones/M6-first-qualifying-sessions.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
