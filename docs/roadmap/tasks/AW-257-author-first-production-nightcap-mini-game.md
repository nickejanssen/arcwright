# AW-257: Author First Production Nightcap Mini-game Package

**Milestone / Epic:** M4 / M4-E
**Size:** M
**Status:** Draft, blocked on founder content approval

## Plain-English Summary

Author one real, founder-approved production Nightcap mini-game package so
AW-254 has a shippable game to promote and rehearse. This task produces content,
not runtime code.

## Why This Task Exists

AW-254 requires a founder-selected production game ID before its rehearsal can
start. As of 2026-06-24 no production package exists: the repository contains
only non-shipping `_fixtures/*` (lifecycle `playtest`) and `_template`
(lifecycle `draft`), and no decision record names a production game. Founder
direction (D-061) is to author the first production game as an explicit
precursor rather than promote a fixture or invent content inside the rehearsal
task.

## Technical Scope

- Author one production mini-game package under `nightcap/mini_games/<game_id>/`
  using the AW-249 authoring schema and loader (manifest, versioned definition,
  assets, client prototype).
- Define an authored delayed clue fallback so timeout or failure cannot make the
  mystery unsolvable.
- Pass content, asset, safety, and schema review through the AW-250 content
  resolution and safety contract.
- Keep behavioral-read output schema-captured only; it must not feed killer
  assignment or cross-session behavior in v1.
- Promote lifecycle to `playtest`, then to `active` only on founder content
  sign-off.

## Acceptance Criteria

- [ ] Founder approves the production game ID and content before authoring is
  marked complete.
- [ ] The package validates against the AW-249 schema and loader.
- [ ] Content, asset, safety, and schema review pass via AW-250.
- [ ] The definition declares an authored delayed clue fallback.
- [ ] Behavioral output is captured but unused for killer assignment or
  cross-session behavior in v1.
- [ ] No runtime, persistence, transport, or rendering code is added here.
- [ ] Roadmap, index, AW-254 dependency, and decision records agree.

## Dependencies

- AW-249 mini-game authoring foundation
- AW-250 mini-game content resolution and safety
- D-058 product approval
- D-061 founder direction to author the first production game

## Must Not Do

- Do not promote a `_fixtures/*` or `_template` package as the production game.
- Do not invent or ship content without founder approval.
- Do not add execution, scoring, persistence, transport, or rendering logic.

## Architecture References

- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md`
- `docs/story-bibles/nightcap-murder-mystery.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

Produces the single validated production package AW-254 needs to run the first
real-device rehearsal that gates AW-231.
