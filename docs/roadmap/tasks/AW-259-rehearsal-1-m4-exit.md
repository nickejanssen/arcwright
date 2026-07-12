# AW-259: Rehearsal 1 - M4 Exit, First Real-Human Nightcap Session

**Milestone / Epic:** M4 (parent task; consolidates M4-D and M4-E close work)
**Size:** L
**Status:** Closed unexecuted (see AW-273)

> **Execution note (2026-07-11):** Issue #176 was closed on 2026-06-27
> without the rehearsal being run. The real-human execution is tracked by
> AW-273 (docs/roadmap/tasks/AW-273-rehearsal-1-execution.md).

## Plain-English Summary

Single body of work that closes M4 by running the first real-human Nightcap
session on real devices, using the two production mini-games promoted by
AW-257 and the runbook authored by AW-260. Supersedes GitHub issues #148
(AW-254) and #84 (AW-231) without losing their criteria; those tasks are
repurposed under this parent as the verification and execution units.

## Why This Matters

M4's exit gate is real humans playing end-to-end on real devices. This is the
first time Arcwright plus Nightcap is exercised against the H1 proof contract
outside synthetic test harnesses. The blockers it surfaces drive M5 hardening
priorities.

## Player Impact

The founder and at least three invitees play the first end-to-end Nightcap
session. Real humans encounter every layer the platform has built so far:
join flow, host setup, shared display, private player events, mini-games,
clue gating, accusation, killer reveal.

## Business Value

Closes M4. Validates the Layer-2 narrative runtime contract under live human
conditions. Establishes the rehearsal cadence and blocker-triage discipline
Rehearsal 2 (M5-F AW-266) and future qualifying sessions (M6) inherit.

## Technical Scope

Coordination task. Owns the parent issue body, the Definition of Done, and
the closure ritual. Actual technical work lives in the sub-issues.

Sub-issues:
- AW-257 (promote both games)
- AW-261 (ADR-0003 validation decision)
- AW-260 (runbook plus blocker template)
- AW-254 (device matrix verification, repurposed)
- AW-231 (rehearsal execution, repurposed)

## Acceptance Criteria

- [ ] Real humans played end-to-end on real devices.
- [ ] Join flow under 30 seconds for every player.
- [ ] Private information never appeared on the shared display.
- [ ] Both promoted mini-games completed on real devices through both normal
  and delayed-clue fallback paths.
- [ ] All Tier 1 polish criteria met: zero crashes, loading / error /
  reconnect states present on every screen, basic accessibility, 60fps
  target on mid-range Android.
- [ ] Every rehearsal blocker is recorded in the blocker log and triaged
  into a new GitHub issue with milestone assignment (M5 hardening, M5-G
  polish, M6 ops, or wontfix) before AW-259 closes.
- [ ] Roadmap manifest reflects M4 closure and M5-F plus M5-G epics exist.

## Tests/Verification

- Verify every sub-issue is closed.
- Verify M4 milestone is at status `complete` in `docs/roadmap/index.json`.
- Verify M5-F and M5-G are present in `docs/roadmap/index.json` and in the
  M5 milestone epic list.

## Dependencies

- AW-261 (sub-issue)
- AW-257 (sub-issue)
- AW-260 (sub-issue)
- AW-254 (sub-issue, repurposed)
- AW-231 (sub-issue, repurposed)

## Must Not Do

- Do not duplicate AW-254 or AW-231 scope inside this parent (they own their
  units).
- Do not close AW-259 without triaging every blocker into a new issue.

## Architecture References

- `docs/roadmap/milestones/M4-nightcap-experience-layer.md`
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`
- `AGENTS.md`

## Playtest Relevance

This task is the M4 exit gate. Its closure marks M4 complete and unblocks M5.
