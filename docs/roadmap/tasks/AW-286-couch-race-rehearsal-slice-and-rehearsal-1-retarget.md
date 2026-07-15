# AW-286: Couch Race Rehearsal Slice And Rehearsal 1 Retarget

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

## Plain-English Summary

Retarget Rehearsal 1 to a Couch Race thin slice: update the rehearsal runbook, quickstart, failure cheat sheet, and fun-observation rubric for the six-beat arc and interrogation loop; align the D-069 narrative tasks (AW-276–AW-280) to the new beats; run the founder rehearsal and log blockers.

## Why This Matters

ADR-0013 retargets Rehearsal 1. The rehearsal exists to surface blockers with real humans on real devices before outside groups play (D-064/D-065/D-066 posture unchanged).

## Player Impact

The first real humans to play Nightcap play the experience that will actually launch.

## Business Value

Protects the founder's validation loop: several complete cases per rehearsal evening instead of one long session.

## Technical Scope

- Update `docs/roadmap/operations/rehearsal-1-runbook.md`, `rehearsal-quickstart.md`, `rehearsal-1-failure-cheat-sheet.md`, and `fun-observation-rubric.md` for Couch Race (interrogation engagement, catch fairness, race aliveness, "another case?" conversion).
- Map AW-276–AW-280 narrative content targets onto the six beats (voice blocks, narrator beat lines, cold-open sequence, clue release, reveal accounting); record the mapping in each task's issue.
- Execute the founder rehearsal (2–5 players, local tunnel), capture blocker log, run the event-dump verification showing narrative content_text at cold open, interrogation answers, twist, and reveal.

## Acceptance Criteria

- [ ] Rehearsal operations docs updated and internally consistent with the Couch Race bible.
- [ ] AW-276–AW-280 beat alignment recorded; no orphaned eight-beat references in their scopes.
- [ ] Founder rehearsal executed end-to-end on real devices; blocker log filed.
- [ ] "Another case?" prompt observed at least once in rehearsal (replay-intent signal capture works).

## Tests/Verification

- Event-dump verification per the D-069 acceptance method, rerun against the Couch Race arc.
- Rehearsal blocker log filed per the AW-260 template.

## Dependencies

- AW-281–AW-285 complete to thin-slice level
- AW-276–AW-280 narrative pipeline tasks
- D-065 local-tunnel deployment

## Must Not Do

- Do not raise the polish bar past Tier 1 (D-066).
- Do not invite outside groups; founder-adjacent players only (Rehearsal 2+ handles outsiders).
- Do not skip the blocker log.

## Architecture References

- `docs/roadmap/operations/rehearsal-1-runbook.md`
- `docs/decisions/0013-nightcap-couch-race-v1-launch-target.md`

## Playtest Relevance

This task IS the playtest path.
