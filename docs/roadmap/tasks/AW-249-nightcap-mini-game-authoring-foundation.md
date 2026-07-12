# AW-249: Nightcap Mini-game Authoring Foundation

**Milestone / Epic:** M4 / M4-E
**Size:** M
**Status:** Complete

## Plain-English Summary

Create the hosting-neutral authoring package, typed schema, loader, template,
and non-shipping fixtures for Nightcap mini-games.

## Technical Scope

- Add `engine/mini_games/` schema and loader contracts.
- Add `nightcap/mini_games/` authoring guidance, template, and fixtures.
- Replace untyped beat mini-game dictionaries with versioned bindings.
- Add focused tests and canonical decision/specification records.

## Acceptance Criteria

- [ ] Template and individual, collaborative, and group fixtures validate.
- [ ] Duplicate IDs, invalid versions, missing definitions, unsafe paths, and
  invalid lifecycle values fail validation.
- [ ] Existing Nightcap arc JSON still validates.
- [ ] No fixture or template enters the production arc.
- [ ] No AI provider or model strings, secrets, dependencies, migrations,
  runtime behavior, API, SDK, or Cloudflare implementation is added.
- [ ] Roadmap, index, specs, GitHub issues, dependencies, and ADRs agree.

## Dependencies

- D-058 product approval
- AW-203 typed arc-definition schema

## Must Not Do

- Do not implement execution, persistence, scoring, clue unlocking, transport,
  rendering, or shipping game content.

## Architecture References

- `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

Provides the validated content intake required before any mini-game reaches a
playtest session.
