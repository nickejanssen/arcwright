# AW-260: Founder Rehearsal Runbook and Blocker Log

**Milestone / Epic:** M4 / M4-D
**Size:** S
**Status:** Planned

## Plain-English Summary

Author the one-page Founder Rehearsal Runbook, the Blocker Log Template, and
the Failure Cheat Sheet that make Rehearsal 1 runnable by the founder and
reportable to the executing chat.

## Why This Matters

AW-231 cannot run without a runbook. AW-240 (the M6 operations runbook) is
not yet scoped or built. This is the minimum-viable operational doc set for
a non-qualifying rehearsal.

## Player Impact

The founder can run a rehearsal session without ad-hoc setup decisions, and
players experience a session that started cleanly because the host followed
a tested procedure.

## Business Value

Establishes the blocker-capture discipline that turns rehearsal output into
prioritized M5 / M5-G / M6 work items, instead of vague impressions.

## Technical Scope

- Author `docs/roadmap/operations/rehearsal-1-runbook.md` with pre-flight,
  session setup, in-session checks, and wrap sections.
- Author `docs/roadmap/operations/blocker-log-template.md` with a single-row
  schema and one filled-in example row.
- Author `docs/roadmap/operations/rehearsal-1-failure-cheat-sheet.md` with a
  decision tree for player disconnect, mini-game timeout, shared-display
  freeze, narrator silent, tunnel dropped.

## Acceptance Criteria

- [ ] Runbook covers pre-flight (Docker up, migrations run, API keys set,
  tunnel command), session setup (URLs, codes, host check-in), in-session
  checks (privacy spot-check, mini-game launch timing), wrap (export
  session log, gather blocker notes).
- [ ] Blocker template has fields: timestamp, player count at incident,
  device plus OS, what happened, what you expected, severity (P0 crash /
  P1 broken UX / P2 polish), repro steps, screenshot or video link.
- [ ] Failure cheat sheet covers at least 5 failure modes with concrete
  recovery actions.
- [ ] Founder reads runbook cold and can execute every step without
  questions (validate by walking through it on a call).
- [ ] Blocker template field-tested by walking through one fabricated
  blocker entry end-to-end.

## Tests/Verification

- Founder walkthrough on call.
- Fabricated-blocker walkthrough.

## Dependencies

- AW-202 web runtime contract (informs tunnel and URL setup)
- AW-230 real-device privacy matrix (informs in-session privacy checks)

## Must Not Do

- Do not include outside-group operations content (that is M6 AW-240).
- Do not include cloud deployment instructions (deferred to AW-261 follow-on).

## Architecture References

- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/roadmap/epics/M4-D-real-device-privacy-and-join-validation.md`
- `AGENTS.md`

## Playtest Relevance

Unblocks AW-231. Becomes the seed document for AW-240 (M6 closed-playtest
operations runbook).
