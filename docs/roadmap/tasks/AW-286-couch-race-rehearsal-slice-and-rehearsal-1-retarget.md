# AW-286: Couch Race Rehearsal Slice And Rehearsal 1 Retarget

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

> **Ownership, decided 2026-08-05 by D-101.** AW-286 owns the remaining AW-285
> scope: six-beat mini-game integration, privacy and device checks, and
> audiovisual polish. The Mini-game Platform and Nightcap Readiness Program is a
> **supplier** to this task, not a gate on it. AW-286 does not wait for program
> completion and proceeds with whatever certified packages exist at rehearsal
> time. Size may need re-estimation by the Planner against the added scope. See
> `docs/decisions/0020-aw-286-owns-remaining-couch-race-integration.md`.

## Plain-English Summary

Retarget Rehearsal 1 to a Couch Race thin slice: update the rehearsal runbook, quickstart, failure cheat sheet, and fun-observation rubric for the six-beat arc, integrated mini-game opportunities, and interrogation loop; align the D-069 narrative tasks (AW-276–AW-280) to the new beats; run the founder rehearsal and log blockers.

## Why This Matters

ADR-0013 retargets Rehearsal 1. The rehearsal exists to surface blockers with real humans on real devices before outside groups play (D-064/D-065/D-066 posture unchanged).

## Player Impact

The first real humans to play Nightcap play the experience that will actually launch.

## Business Value

Protects the founder's validation loop: several complete cases per rehearsal evening instead of one long session.

## Technical Scope

- Update `docs/roadmap/operations/rehearsal-1-runbook.md`, `rehearsal-quickstart.md`, `rehearsal-1-failure-cheat-sheet.md`, and `fun-observation-rubric.md` for Couch Race (interrogation engagement, catch fairness, race aliveness, "another case?" conversion).
- Map AW-276–AW-280 narrative content targets onto the six beats (voice blocks, narrator beat lines, cold-open sequence, clue release, reveal accounting); record the mapping in each task's issue.
- Execute the founder rehearsal across the supported 2–8 player range when
  practical, with at least 2 players required for every qualifying run, using
  the local tunnel. Capture the blocker log and run event-dump verification
  showing narrative content_text at cold open, interrogation answers, twist,
  mini-game opportunities, and reveal.
- Own the remaining AW-285 scope carried forward from PR #269 (D-101):
  - **Six-beat mini-game integration.** `nightcap/couch-race.arc.json` binds
    only `scene` and `twist` today; `pour`, `grill`, `last_call`, and `truth`
    carry empty `mini_games` arrays. Bind each authored beat to whatever
    certified candidates exist at rehearsal time, or record the beat as
    deliberately unbound with its authored story fallback.
  - **Privacy and device checks.** Certify the shared-display privacy gate at
    `nightcap-web/src/filters.ts` and its `privacy-matrix` and
    `mini-game-privacy-matrix` suites against real devices.
  - **Audiovisual polish** on `nightcap-web/src/couch-race/display-projection.ts`
    within the Tier 1 bar, including the AW-285 Phase 2 holes: `suspectState` is
    hardcoded `null` and `leverage_balance` is declared but never produced.

## Human Collaboration Contract

**Interaction profile:** Facilitated live operation.

**Founder input:** Couch Race slice readiness, walkthrough feedback, retargeted
Rehearsal 1 go or no-go, observed experience, and the debrief assessment.

**Required phases:**

1. Prepare the slice and environment and show the evidence collected.
2. Run preflight checks and explain what the founder must inspect, record, and
   treat as blocking.
3. Conduct a guided walkthrough or smoke test and capture feedback.
4. Pause for the founder's explicit go or no-go decision.
5. Facilitate the retargeted live rehearsal with visible checkpoints and stop
   conditions.
6. Debrief with focused interactive questions and summarize findings.
7. Propose remediation options and obtain approval before another live run.

**Gate:** The retargeted rehearsal does not begin until the founder explicitly
approves slice and environment readiness. Any failed blocking check returns the
task to preparation.

**Evidence:** Preserve preflight output, walkthrough feedback, go or no-go,
session observations, debrief responses, remediation decision, dates, and owner
actions.

## Acceptance Criteria

- [ ] Rehearsal operations docs updated and internally consistent with the Couch Race bible.
- [ ] AW-276–AW-280 beat alignment recorded; no orphaned eight-beat references in their scopes.
- [ ] Founder rehearsal executed end-to-end on real devices; blocker log filed.
- [ ] "Another case?" prompt observed at least once in rehearsal (replay-intent signal capture works).
- [ ] Every authored Couch Race beat either binds a certified mini-game candidate or records a deliberate unbound decision with its story fallback.
- [ ] Shared-display privacy gate certified on real devices; no private information reaches the shared surface.
- [ ] Tier 1 audiovisual pass complete on the shared-display projection; AW-285 Phase 2 holes either closed or recorded as accepted for Rehearsal 1.

## Tests/Verification

- Event-dump verification per the D-069 acceptance method, rerun against the Couch Race arc.
- Rehearsal blocker log filed per the AW-260 template.

## Dependencies

- AW-281–AW-285 complete to thin-slice level
- AW-276–AW-280 narrative pipeline tasks
- D-065 local-tunnel deployment
- AW-288 (Tell Me Something True activation, placement, and pacing) and
  AW-289 (The Interrogation Room Last Call pressure capstone) as applicable
  to the approved opportunity pools
- The Mini-game Platform and Nightcap Readiness Program supplies certified
  mini-game packages and adaptations to this task. Per D-101 it is **not** a
  blocking dependency. AW-286 consumes what is certified at rehearsal time and
  is not held open by uncompleted program slices. The program's order 12 plan
  Task 6, "Run AW-286 Real-player Rehearsal and Remediate," does not own this
  task and cannot gate it.

## Must Not Do

- Do not raise the polish bar past Tier 1 (D-066).
- Do not invite outside groups; founder-adjacent players only (Rehearsal 2+ handles outsiders).
- Do not skip the blocker log.

## Architecture References

- `docs/roadmap/operations/rehearsal-1-runbook.md`
- `docs/decisions/0013-nightcap-couch-race-v1-launch-target.md`

## Playtest Relevance

This task IS the playtest path.
