# AW-251: Mini-game Runtime, Persistence, And Clue Gating

**Milestone / Epic:** M4 / M4-E
**Size:** L
**Status:** Complete

## Plain-English Summary

Implement deterministic timing, submissions, scoring, outcomes, clue gating,
behavioral output, and pause/resume persistence.

## Acceptance Criteria

- [ ] Python exclusively owns lifecycle, scoring, outcomes, and clue release.
- [ ] Runs persist in `mini_game_runs`; submissions are append-only.
- [ ] Duplicate and concurrent submissions cannot corrupt state.
- [ ] Pause/resume restores the exact run and definition snapshot.
- [ ] Timeout fallback preserves a solvable clue path.
- [ ] v1 behavioral output is not used by killer assignment or another session.
- [ ] Unknown `mechanic_type` values are rejected at runtime resolution; dispatch
  uses a closed registry of approved mechanic implementations.
- [ ] Derived behavioral outputs are validated against non-derived siblings in
  the resolved definition snapshot.

## Dependencies

- AW-250
- AW-215
- AW-220

## Must Not Do

- Do not put canonical state in TypeScript.
- Do not add cross-session behavioral aggregation.

## References

- `docs/specs/0048-aw-251-mini-game-runtime-persistence-and-clue-gating.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
