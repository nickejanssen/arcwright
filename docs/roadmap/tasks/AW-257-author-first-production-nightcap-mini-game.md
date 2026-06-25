# AW-257: Author First Production Nightcap Mini-game Package

**Milestone / Epic:** M4 / M4-E
**Size:** M
**Status:** Draft, blocked on founder content approval

## Plain-English Summary

Author the founder-selected Tell Me Something True production Nightcap
mini-game package so AW-254 has a shippable game to promote and rehearse. This
task produces content, not runtime code.

## Why This Task Exists

AW-254 requires a founder-selected production game ID before its rehearsal can
start. D-061 created AW-257 as the explicit precursor task because, as of
2026-06-24, no production package existed and no decision record named a
production game. D-062 now selects Tell Me Something True as the first
production Nightcap mini-game candidate and points to the locked design in
`docs/specs/0061-aw-258-tell-me-something-true.md`.

This task still requires founder content approval before authoring is marked
complete. D-062 approves the game ID and design direction, not final package
content.

## Technical Scope

- Author the `tell-me-something-true` production mini-game package under
  `nightcap/mini_games/tell-me-something-true/` using the AW-249 authoring
  schema and loader (manifest, versioned definition, assets, client prototype).
- Define an authored delayed clue fallback so timeout or failure cannot make the
  mystery unsolvable.
- Pass content, asset, safety, and schema review through the AW-250 content
  resolution and safety contract.
- Keep behavioral-read output schema-captured only; it must not feed killer
  assignment or cross-session behavior in v1.
- Promote lifecycle to `playtest`, then to `active` only on founder content
  sign-off.

## Acceptance Criteria

- [ ] Founder approval of the production game ID is recorded in D-062, and
  founder content approval is recorded before authoring is marked complete.
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
- D-062 founder selection of Tell Me Something True as the first production
  Nightcap mini-game candidate

## Must Not Do

- Do not promote a `_fixtures/*` or `_template` package as the production game.
- Do not ship package content without founder approval.
- Do not add execution, scoring, persistence, transport, or rendering logic.

## Architecture References

- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md`
- `docs/specs/0061-aw-258-tell-me-something-true.md`
- `docs/story-bibles/nightcap-murder-mystery.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

Produces the single validated production package AW-254 needs to run the first
real-device rehearsal that gates AW-231.
