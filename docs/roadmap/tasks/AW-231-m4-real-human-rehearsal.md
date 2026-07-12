# AW-231: Execute Real-Human Nightcap Rehearsal 1

**Milestone / Epic:** M4 / M4-D
**Size:** M
**Status:** Complete
**Parent:** AW-259

## Repurpose Note

This task's scope was rewritten on 2026-06-26 per
`docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`. The original
"non-qualifying real-device rehearsal" scope is preserved and extended with
explicit runbook + blocker-triage discipline (AW-260 owns the runbook;
AW-231 executes the rehearsal).

## Plain-English Summary

Run the first real-human Nightcap session using both promoted mini-games,
following the runbook, and triaging every blocker into a new GitHub issue
before closing.

## Why This Matters

This is the M4 exit gate. Real humans on real devices producing real
blockers is the only signal the platform is honest with itself.

## Player Impact

Four-plus humans play Nightcap end-to-end and provide the first ground-truth
data about the experience.

## Business Value

Closes M4. Establishes rehearsal cadence + blocker-triage discipline that
Rehearsal 2 and M6 qualifying sessions inherit. Outputs triaged blockers
that drive M5 hardening priorities.

## Technical Scope

- Run the rehearsal per `docs/roadmap/operations/rehearsal-1-runbook.md`.
- Founder + at least 3 invitees (4-player floor required for Crime Scene
  Smash).
- Record: join timing for every player, privacy results during the
  rehearsal, mini-game completion or fallback for each game, session
  completion state, every blocker (using the AW-260 blocker template).
- After the rehearsal: triage every blocker into a new GitHub issue with a
  milestone assignment (M5 hardening, M5-G polish, M6 ops, or `wontfix`).

## Acceptance Criteria

- [ ] Rehearsal occurred with at least 4 real humans on real devices.
- [ ] All recorded data (join timing, privacy, completion, blockers) is
  saved in the blocker log.
- [ ] Every blocker has a corresponding new GitHub issue with milestone
  assignment.
- [ ] M4 milestone is marked complete in `docs/roadmap/index.json`.

## Tests/Verification

- Rehearsal artifacts (blocker log, session export, recording if any) are
  archived in `docs/roadmap/operations/rehearsal-1-artifacts/`.
- Blocker triage issues exist in GitHub.

## Dependencies

- AW-254 (both games verified on device matrix)
- AW-260 (runbook + blocker template authored)

## Must Not Do

- Do not run with fixtures only.
- Do not bypass the AW-202 web runtime contract.
- Do not bypass the AW-260 runbook (if the runbook is wrong, fix the
  runbook and re-run pre-flight).
- Do not close AW-231 without triaging every blocker.

## Architecture References

- `docs/roadmap/operations/rehearsal-1-runbook.md`
- `docs/roadmap/operations/blocker-log-template.md`
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`

## Playtest Relevance

This rehearsal closes M4. Its blockers drive M5 hardening priorities and
seed Rehearsal 2.
