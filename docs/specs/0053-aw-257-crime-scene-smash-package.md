# AW-257: Crime Scene Smash Mini-game Package

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-24

---

# References

- Related ADRs: `docs/decisions/0009-mini-game-runtime-boundary.md`
- Related specs: `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md`, `docs/specs/0047-aw-250-mini-game-content-resolution-and-safety.md`
- Story bible: `docs/story-bibles/nightcap-murder-mystery.md`
- Product decisions: `docs/product/decisions-log.csv` D-058, D-059, D-060, D-061, D-062

---

# Overview

Author and validate the first production Nightcap mini-game package,
`crime-scene-smash`, as a Nightcap-tailored match-3 clue gate with per-player
boards and a shared leaderboard.

---

# In Scope

- Package files under `nightcap/mini_games/crime-scene-smash/`
- Draft lifecycle metadata and versioned definition files
- Presentation-only client mock and package README
- Hybrid content mode declaration with authored rules and generative flavor
- Delayed clue fallback declaration
- Neutral behavioral outputs for score and session telemetry
- Nightcap-specific surface contract for phone, shared display, and host

---

# Out Of Scope

- Runtime timing, scoring, clue unlocking, persistence, or transport
- API endpoints, SDK methods, or web runtime authority
- Killer assignment wiring from behavioral output
- Any new dependency, database migration, or provider/model string
- Promotion to `active`

---

# Acceptance Criteria

- [x] The package validates with the mini-game loader.
- [x] The manifest and definition agree on `crime-scene-smash` and `0.1.0`.
- [x] The package uses the engine-supported `individual` participation mode.
- [x] The rules contract documents per-player boards and a shared leaderboard.
- [x] The definition declares hybrid content and a delayed clue fallback.
- [x] The package README and client README state that the browser is presentation only.
- [x] The package includes placeholder markers for final authored copy.
- [x] No runtime authority, dependency, or schema change is introduced here.

---

# Test Plan

- `python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/crime-scene-smash`
- `pytest engine/tests/test_mini_game_models.py -q`
- Manual review of the package manifest, definition, and presentation mock

---

# Risks and Unknowns

**Risks**:
- Final authored narrator and leaderboard copy is still pending.
- The interactive runtime is not yet built, so the browser mock cannot prove playability.

**Unknowns**:
- Whether future runtime work will expose additional per-player telemetry for the end-of-game award.

---

# Open Questions

- None for the approved package envelope.
