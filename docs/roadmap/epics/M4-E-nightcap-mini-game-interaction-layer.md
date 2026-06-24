# M4-E: Nightcap Mini-game Interaction Layer

**Milestone:** M4
**Status:** Planned

## Plain-English Summary

Add timed, puzzle-gated mini-games across Nightcap beats without moving
deterministic state or arc logic into the browser experience.

## Why This Matters

D-058 identifies mini-games as a protected Nightcap v1 interaction layer. They
gate clues, create competition, and produce investigative leads across the arc.

## Tasks

- [AW-249: Nightcap Mini-game Authoring Foundation](../tasks/AW-249-nightcap-mini-game-authoring-foundation.md)
- [AW-250: Mini-game Content Resolution And Safety](../tasks/AW-250-mini-game-content-resolution-and-safety.md)
- [AW-251: Mini-game Runtime, Persistence, And Clue Gating](../tasks/AW-251-mini-game-runtime-persistence-and-clue-gating.md)
- [AW-252: Mini-game API, Events, And TypeScript SDK](../tasks/AW-252-mini-game-api-events-and-sdk.md)
- [AW-253: Nightcap Web Mini-game Rendering And Device Integration](../tasks/AW-253-nightcap-web-mini-game-rendering.md)
- [AW-257: Author First Production Nightcap Mini-game Package](../tasks/AW-257-author-first-production-nightcap-mini-game.md)
- [AW-254: First Production Nightcap Mini-game And Rehearsal](../tasks/AW-254-first-production-nightcap-mini-game.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- Python remains authoritative for timers, scoring, submissions, outcomes, and
  clue unlocking.
- Web clients contain no arc execution or canonical mini-game state logic.
- Behavioral output does not affect killer assignment or cross-session behavior
  in v1.
- One approved production mini-game completes on real devices without private
  information leakage before the M4 rehearsal gate closes.

## Dependencies

- Parent milestone: M4
- Existing M2 and M3 arc, event, persistence, API, and SDK infrastructure

## Must Not Do

- Do not turn Nightcap presentation choices into platform assumptions.
- Do not implement v1.1 behavioral wiring or cross-campaign reads.

## Architecture References

- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/prd/02-requirements.md`
- `docs/story-bibles/nightcap-murder-mystery.md`
- `docs/architecture/03-arc-execution.md`
- `docs/architecture/08-event-system.md`

## Playtest Relevance

This epic adds the timed clue-cracking layer required for a representative
Nightcap v1 real-device rehearsal.
