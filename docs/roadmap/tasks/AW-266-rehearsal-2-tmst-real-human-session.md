# AW-266: Rehearsal 2 - TMST Real-Human Session

**Milestone / Epic:** M5 / M5-F
**Size:** M
**Status:** Planned

## Plain-English Summary

Promote Tell Me Something True to the active lifecycle and run a real-human
rehearsal of the full TMST flow on real devices, applying the same runbook
and blocker-triage discipline as Rehearsal 1.

## Why This Matters

TMST is the first net-new mechanic family to ship through the full Nightcap
pipeline after the M4 close path. A second real-human rehearsal data point
validates that the platform handles a richer four-phase flow under live
conditions and surfaces M5-F-specific blockers.

## Player Impact

At least four humans play the TMST social opener end-to-end, experiencing
the four-phase rhythm, the spotlight order, and the narrator-led reveal.

## Business Value

Adds the second real-human rehearsal data point. Confirms the M5-F epic
delivered a working flow before any M6 qualifying session reuses it.

## Technical Scope

- Promote `nightcap/mini_games/tell-me-something-true/` lifecycle to
  `active` after AW-262 to AW-265 close.
- Update the AW-260 rehearsal runbook with TMST-specific pre-flight,
  in-session, and wrap steps.
- Run the rehearsal per the updated runbook with founder plus at least
  three invitees (4-player floor).
- Record join timing, privacy spot-checks, phase completion, and every
  blocker (using the AW-260 blocker template).
- Triage every blocker into a new GitHub issue with milestone assignment
  (M5 hardening, M5-G polish, M6 ops, or wontfix) before AW-266 closes.

## Acceptance Criteria

- [ ] TMST package lifecycle is `active`.
- [ ] Runbook updated for TMST specifics.
- [ ] Rehearsal occurred with at least 4 real humans on real devices.
- [ ] All recorded data (join timing, privacy, phase completion, blockers)
  is saved in the blocker log.
- [ ] Every blocker has a corresponding new GitHub issue with milestone
  assignment.

## Tests/Verification

- Rehearsal artifacts archived under
  `docs/roadmap/operations/rehearsal-2-artifacts/`.
- Triage table linking each blocker entry to its created issue.

## Dependencies

- AW-265 (web rendering)
- AW-259 (Rehearsal 1 closure, so Rehearsal 1 fixes are folded back first)

## Must Not Do

- Do not bypass the runbook; if the runbook is wrong, fix the runbook.
- Do not run Rehearsal 2 with fixtures only.
- Do not close AW-266 without triaging every blocker.

## Architecture References

- `docs/specs/0061-aw-258-tell-me-something-true.md`
- `docs/roadmap/operations/rehearsal-1-runbook.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `AGENTS.md`

## Playtest Relevance

Second real-human rehearsal data point and the M5-F epic exit gate.
