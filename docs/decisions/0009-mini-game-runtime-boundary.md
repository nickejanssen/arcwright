# 0009 - Mini-game Runtime Boundary

**Date:** 2026-06-20
**Status:** Accepted
**Architecture reference:** `docs/architecture/03-arc-execution.md`, `docs/architecture/08-event-system.md`, `docs/architecture/15-development-guide.md`
**Spec reference:** `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md`
**Scope:** Nightcap v1 mini-game authoring and future runtime ownership

---

# Context

D-058 makes timed, puzzle-gated mini-games a core Nightcap v1 interaction
layer. The existing `BeatDefinition.mini_games` field is an untyped list, and
the repository has no stable place to author, validate, version, or promote
mini-games.

Mini-games span a platform/game boundary. Deterministic timing, submissions,
scoring, outcomes, and clue unlocking affect canonical session state. Assets
and browser rendering are Nightcap presentation concerns. Mixing those concerns
would violate surface agnosticism and make future experience reuse harder.

## Alternatives considered

- Store games in dev, test, and prod directories. Rejected because promotion
  would move paths, duplicate content, and create configuration drift.
- Put scoring and timers in browser modules. Rejected because TypeScript cannot
  own arc execution or canonical session state.
- Keep `mini_games` as unvalidated dictionaries. Rejected because invalid IDs,
  versions, and package paths would fail late at runtime.

---

# Decision

Mini-game packages use stable per-game directories, semantic versions, and
lifecycle metadata: `draft`, `playtest`, `active`, and `retired`.

The Python engine owns the generic authoring schema. Versioned arc bindings
refer to a game ID and version. Nightcap owns package definitions, assets, and
presentation prototypes under `nightcap/mini_games/`.

Future runtime work follows these boundaries:

- Python owns authoritative timers, submission validation, scoring, outcomes,
  clue unlocking, and persistence.
- Web clients render authorized state and submit actions only.
- Authored, generative, and hybrid content resolves before deterministic
  execution. AI never chooses outcomes or mutates canonical state.
- v1 stores neutral metrics and deterministic, game-scoped observations.
  Behavioral output does not affect killer assignment or cross-session behavior
  until approved v1.1 work.
- Every definition has an authored delayed clue fallback so timeout or failure
  cannot make the mystery unsolvable.
- Future persistence uses `mini_game_runs` for canonical run state and
  append-only `mini_game_submissions` for player actions.

AW-249 establishes authoring contracts only. It does not implement the future
runtime, persistence, API, SDK, or browser rendering.

---

# Consequences

## Positive consequences

- Game developers get one stable, validated place to work on mini-games.
- The engine contract is reusable without importing Nightcap rendering choices.
- Session outcomes remain deterministic and replayable.
- Lifecycle promotion does not change package paths.

## Negative consequences

- Each package carries a manifest plus versioned definition files.
- Runtime, persistence, transport, and rendering require separate tasks.
- Playtest definitions become immutable and require a new version for changes.

## Trade-offs

- We accept more explicit authoring metadata to avoid late runtime failures.
- We defer executable integration while preserving a decision-complete path for
  future work.

---

# References

- `docs/product/decisions-log.csv` D-058 and D-059
- `docs/prd/02-requirements.md`
- `docs/story-bibles/nightcap-murder-mystery.md` Sections 4 and 7
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- GitHub issues #142 through #148
