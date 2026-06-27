# AW-257: Promote Crime Scene Smash and Evidence Locker to active

**Milestone / Epic:** M4 / M4-E
**Size:** M
**Status:** Planned

## Plain-English Summary

Promote the two existing draft Nightcap mini-game packages (Crime Scene Smash
and Evidence Locker) to the active lifecycle so Rehearsal 1 has two
production-quality games to verify on real devices.

## Why This Matters

AW-254 cannot start without at least one production-lifecycle mini-game
package. D-062 names Crime Scene Smash as the first production package; this
task fulfills D-062 and extends approval to Evidence Locker so Rehearsal 1
covers both a multi-player (Crime Scene Smash) and a solo (Evidence Locker)
mechanic.

## Player Impact

Real humans get two distinct mini-game experiences in Rehearsal 1, exercising
both the solo-clue-recovery and multi-player-leaderboard surfaces of the
Nightcap experience.

## Business Value

Two production-ready mini-games covers more of the M4 exit gate than a single
game and surfaces more blockers per rehearsal session.

## Technical Scope

- Draft copy for the `[final authored copy needed]` placeholders in
  `nightcap/mini_games/crime-scene-smash/definitions/0.1.0.json` (narrator
  intro, success line, fallback line, tie line, leaderboard callouts).
- Run AW-250 content and safety review on both packages.
- Bump `nightcap/mini_games/crime-scene-smash/manifest.json` lifecycle to
  `active`.
- Bump `nightcap/mini_games/evidence-locker-402/manifest.json` lifecycle to
  `active`.
- Bind both packages into `nightcap/arc.json` at the founder-chosen beat
  positions.
- Confirm each package declares an authored delayed clue fallback per
  AW-249 / D-059 / ADR-0009.

## Acceptance Criteria

- [ ] Crime Scene Smash copy placeholders replaced with founder-approved copy.
- [ ] Both packages validate against the AW-249 schema and loader.
- [ ] Both packages pass AW-250 content and safety review.
- [ ] Founder signs off on Crime Scene Smash authored copy before lifecycle
  promotion.
- [ ] Both manifests are at lifecycle `active`.
- [ ] Both packages are bound into `nightcap/arc.json` at founder-named beats.
- [ ] D-062 record is updated to also name Evidence Locker as an approved
  production package.

## Tests/Verification

- Run the AW-249 schema validator against both packages.
- Run the AW-250 safety review on both packages.
- Confirm `nightcap/arc.json` parses and references both package IDs.

## Dependencies

- AW-249 mini-game authoring foundation (complete)
- AW-250 mini-game content resolution and safety (complete)
- D-061 founder direction
- D-062 first production package decision

## Must Not Do

- Do not promote `_fixtures/*` or `_template` packages.
- Do not invent or ship content without founder approval.
- Do not modify runtime, persistence, transport, or rendering code.

## Architecture References

- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md`
- `docs/specs/0047-aw-250-mini-game-content-resolution-and-safety.md`
- `docs/story-bibles/nightcap-murder-mystery.md`

## Playtest Relevance

Produces the two production packages AW-254 needs to verify on real devices
before AW-231 runs the rehearsal.
