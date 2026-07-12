# AW-273: Rehearsal 1 Execution - First Real-Human Nightcap Session

**Milestone / Epic:** M5 (M4 exit-gate debt; no epic)
**Size:** M
**Status:** Planned

## Plain-English Summary

Run the first real-human Nightcap session. AW-259 (#176) defined this work
but was closed on 2026-06-27 without the session being executed; the M4 exit
gate ("real humans playing end-to-end on real devices") has not actually been
passed. This task owns the actual execution using the one-command rehearsal
stack (`make rehearsal`) and the quickstart runbook.

## Definition of Done

- Founder solo smoke test completed (founder plus two phone browser tabs).
- Real-human session: founder plus at least three invitees on real devices,
  through join, host setup, shared display, private player events, both
  production mini-games (Crime Scene Smash, Evidence Locker), accusation,
  and killer reveal.
- Blocker log filled from
  `docs/roadmap/operations/blocker-log-template.md` and committed under
  `docs/roadmap/operations/`.
- Outcomes recorded on this task's GitHub issue before it is closed.

## Dependencies

- `make rehearsal` orchestrator and smoke script (this plan, Tasks 6-7)
- Quickstart runbook (this plan, Task 8)

## References

- Supersedes-for-execution: AW-259 (#176), AW-231 (#84), AW-254 (#148)
- Spec: docs/specs/0067-development-survey-and-path-to-first-playtest.md
