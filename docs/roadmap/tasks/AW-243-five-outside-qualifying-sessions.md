# AW-243: Five Outside Qualifying Sessions

**Milestone / Epic:** M6 / M6-B  
**Size:** L  
**Status:** Planned

## Plain-English Summary

Run five or more qualifying Nightcap sessions with outside groups at 4 to 6 players.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/02-requirements.md Success criteria` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Run five or more qualifying Nightcap sessions with outside groups at 4 to 6 players. Likely files affected: GitHub issue comments, docs/playtest notes if created.

## Human Collaboration Contract

**Interaction profile:** Facilitated live operation.

**Founder input:** Recruitment and scheduling constraints, readiness for each
session, live go or no-go decisions, observed results, and debrief feedback.

**Required phases for each session:**

1. Prepare participants, environment, and evidence collection.
2. Run preflight checks and explain what the founder must inspect, record, and
   treat as blocking.
3. Conduct a guided walkthrough or smoke test and capture feedback.
4. Pause for the founder's explicit go or no-go decision.
5. Facilitate the live session with visible checkpoints and stop conditions.
6. Debrief with focused interactive questions and summarize findings.
7. Propose remediation options and obtain approval before the next session.

**Gate:** Each qualifying session has its own explicit readiness approval. A
prior approval does not authorize a later session, and failed blockers return
the task to preparation.

**Evidence:** Preserve per-session preflight output, walkthrough result, go or
no-go, observations, debrief responses, remediation decision, dates, and owner
actions.

## Acceptance Criteria

- [ ] Five or more outside-group sessions are attempted and documented.
- [ ] Each session records completion status, replay intent, personalization perception evidence, player count, and telemetry status.
- [ ] All qualifying sessions use 4 to 6 players.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-242

## Likely Files Affected

GitHub issue comments, docs/playtest notes if created

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/prd/02-requirements.md Success criteria
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
