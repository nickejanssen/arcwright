# AW-254: First Production Nightcap Mini-game And Rehearsal

**Milestone / Epic:** M4 / M4-E
**Size:** M
**Status:** Draft, blocked on AW-257 production game authoring

## Plain-English Summary

Promote one founder-selected game from playtest to active and validate it on
real devices.

## Rehearsal Gate (2026-06-24)

A pre-implementation gate check found no founder-selected production game ID in
canonical docs, specs, or decision records, and no `active`-lifecycle package in
`nightcap/mini_games/` (only non-shipping `_fixtures/*` at lifecycle `playtest`
and `_template` at lifecycle `draft`). Promoting a fixture and inventing content
are both forbidden, so this task cannot start. Founder direction (D-061) is to
author the first production game as the precursor task AW-257; AW-254 now depends
on AW-257 and stays blocked until that package is authored, reviewed, and
founder-approved.

## Acceptance Criteria

- [ ] The founder selects the production game before implementation starts.
- [ ] Rules, content, assets, safety, and schema review pass.
- [ ] The game runs end-to-end on supported devices.
- [ ] Completion and timeout fallback preserve a solvable clue path.
- [ ] Privacy, reconnect, pause/resume, behavioral output, and accessibility
  checks pass.
- [ ] Rehearsal blockers are triaged.

## Dependencies

- AW-253
- AW-230
- AW-257 authored, reviewed, founder-approved production mini-game package
- Founder selection of the first production mini-game

## Must Not Do

- Do not activate non-shipping fixtures.
- Do not invent production game content without founder approval.

## References

- `docs/specs/0051-aw-254-first-production-nightcap-mini-game.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
