# Blocker Log Template - Rehearsal 1

Copy this template into a new file at
`docs/roadmap/operations/rehearsal-1-artifacts/blockers-<YYYYMMDD>.md`
during the rehearsal. Add one entry per blocker observed. If no blockers
occurred, create the file with one entry stating "No blockers observed".

## Entry schema

Each blocker is one section using the schema below. Fill every field.

```
### Blocker NN

- Timestamp: HH:MM:SS local
- Player count at incident: N
- Device + OS: e.g. "Pixel 5a, Android 14, Chrome 126"
- What happened: 1-2 sentence factual description
- What you expected: 1-2 sentence description of expected behavior
- Severity:
  - P0 = crash, data loss, privacy leak, session ended early
  - P1 = broken UX (player blocked from continuing), wrong-path completion
  - P2 = polish (looks bad, slow, small wording issue)
- Repro steps:
  1. Step 1
  2. Step 2
- Screenshot or video link: (paste image, link to local file, or "N/A")
- Triage destination: (filled after the session - M5 hardening, M5-G polish, M6 ops, or wontfix)
- New issue link: (filled after triage)
```

## Example entry (fabricated, for template validation)

### Blocker 01

- Timestamp: 19:42:17 local
- Player count at incident: 4
- Device + OS: iPhone 12, iOS 17.5, Safari
- What happened: After submitting the Crime Scene Smash final score, the
  "Awaiting other players" screen stayed for 8 seconds before the
  leaderboard appeared on the shared display.
- What you expected: Leaderboard appears within 2 seconds of last submission.
- Severity: P1
- Repro steps:
  1. Complete Crime Scene Smash on iPhone Safari.
  2. Wait for other players to finish.
  3. Observe the delay before the shared-display leaderboard renders.
- Screenshot or video link: rehearsal-1-artifacts/blocker-01-screen-recording.mp4
- Triage destination: M5 hardening
- New issue link: (filled after triage)

## Triage rules

After the session, for each entry:

1. Pick the destination:
   - **M5 hardening** - engine, runtime, or API correctness; performance under realistic load.
   - **M5-G polish** - visual, motion, or copy that did not break the experience but felt unfinished.
   - **M6 ops** - runbook / cheat-sheet gap, deployment fragility, observability gap.
   - **wontfix** - intentional out-of-scope; document the reasoning in the entry itself.
2. Create the new GitHub issue with the right milestone label.
3. Paste the issue URL into the entry's `New issue link` field.

Do not close AW-231 until every entry's `New issue link` is filled
(or the entry is documented `wontfix`).
