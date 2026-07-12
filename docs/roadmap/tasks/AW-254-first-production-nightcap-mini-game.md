# AW-254: Verify Two Promoted Mini-games on Real Devices

**Milestone / Epic:** M4 / M4-E
**Size:** M
**Status:** Complete
**Parent:** AW-259

## Repurpose Note

This task's scope was rewritten on 2026-06-26 per
`docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`. Original
scope (promote one founder-selected mini-game) is fulfilled by AW-257. This
task now owns the device-matrix verification of the two production
mini-games AW-257 promotes (Crime Scene Smash + Evidence Locker). Original
acceptance criteria are preserved and extended for dual-game coverage.

## Plain-English Summary

Verify both production Nightcap mini-games end-to-end on the real-device
matrix before the rehearsal session runs.

## Why This Matters

Both games must work on the actual phones / tablets / shared-display
browsers real humans will use, with both clue paths (normal completion +
authored delayed fallback) covered. This is the last gate before AW-231
puts the games in front of real humans.

## Player Impact

Players hit games that have been verified on their device class instead of
games that worked once in a developer's localhost browser.

## Business Value

Catches device-specific bugs before they become rehearsal blockers.

## Technical Scope

- End-to-end run of Crime Scene Smash on the device matrix:
  iOS Safari (latest), Android Chrome (latest), mid-range Android
  (Pixel 5a or equivalent), shared-display browser (1080p Chrome).
- End-to-end run of Evidence Locker on the same matrix.
- Both clue paths verified for each game: normal completion AND authored
  delayed-clue fallback.
- Privacy, reconnect, pause and resume, behavioral output, and
  accessibility verification per the AW-230 matrix.
- Tier 1 polish bar: zero crashes, loading / error / reconnect states
  present on every screen, 60fps target on mid-range Android, basic
  accessibility (color contrast WCAG AA, screen reader landmarks,
  keyboard navigation).

## Acceptance Criteria

- [ ] All AW-230 matrix cells pass for both games.
- [ ] Both clue paths (normal + delayed fallback) verified for both games.
- [ ] Tier 1 polish gates pass: no crashes during verification, every
  screen has loading / error / reconnect, mid-range Android holds 60fps,
  WCAG AA color contrast holds on shared display + player device, screen
  reader landmarks present, keyboard navigation works.
- [ ] Founder demos both games end-to-end on a recorded call.

## Tests/Verification

- Run the AW-230 device matrix for each game.
- Record the founder demo call.
- Capture any failures into AW-260 blocker template format.

## Dependencies

- AW-257 (production packages promoted to active)
- AW-261 (ADR-0003 validation decision recorded so cloud-path ambiguity
  does not contaminate verification scope)
- AW-230 (privacy matrix; complete)
- AW-253 (web mini-game rendering; complete)

## Must Not Do

- Do not activate non-shipping fixtures.
- Do not bypass the AW-202 web runtime contract.
- Do not author new game content (AW-257 owns content).
- Do not add art / animation / sound polish (M5-G scope).

## Architecture References

- `docs/specs/0051-aw-254-first-production-nightcap-mini-game.md` (original
  spec, preserved for reference)
- `docs/specs/0060-aw-230-real-device-privacy-matrix.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`

## Playtest Relevance

Last verification gate before AW-231 puts the games in front of real
humans.
