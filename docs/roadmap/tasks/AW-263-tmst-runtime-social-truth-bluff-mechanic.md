# AW-263: TMST Runtime - social-truth-bluff Mechanic

**Milestone / Epic:** M5 / M5-F
**Size:** M
**Status:** Complete

## Plain-English Summary

Add the closed-registry `social-truth-bluff` mechanic to the AW-251
mini-game runtime so the Python engine deterministically owns every state
transition Tell Me Something True requires.

## Why This Matters

Per ADR-0009 and the engine constraints in AGENTS.md, all canonical state
transitions must be deterministic and live in Python. TMST's four-phase
flow introduces input timing, spotlight ordering, vote acceptance, and
truth reveal logic that does not exist in the runtime yet.

## Player Impact

Indirect. Players experience a TMST round that behaves consistently across
sessions because the runtime, not the AI, decides what counts as a
submission, a vote, or a skipped turn.

## Business Value

Keeps TMST inside the closed-mechanic registry. Prevents arc configuration
or AI calls from inventing new mechanic shapes that bypass schema or safety
review.

## Technical Scope

- Register `social-truth-bluff` as a closed mechanic in the AW-251 runtime;
  reject unknown mechanic types before run creation.
- Python owns: input deadline, AFK auto-truth, accepted submissions,
  spotlight order, disconnect skip, vote acceptance, abstentions, truth
  reveal, score computation, signal computation, run completion.
- No AI call may decide truth, score, votes, signals, or outcomes.
- Emit structured events the API layer (AW-264) consumes; do not emit any
  surface-specific payloads.

## Acceptance Criteria

- [ ] `social-truth-bluff` mechanic registered; unknown mechanic types
  rejected before run creation.
- [ ] Input deadline, AFK auto-truth, and disconnect skip behave per
  spec 0061.
- [ ] Spotlight ordering, vote acceptance, abstentions, and truth reveal
  are deterministic.
- [ ] Score and signal computation produce identical output for identical
  input fixtures.
- [ ] Unit tests cover the four phases plus every edge case named in
  spec 0061.

## Tests/Verification

- Unit tests for each phase transition.
- Property-style test confirming determinism across repeated runs of the
  same fixture.
- Test confirming unknown mechanic types are rejected before run creation.

## Dependencies

- AW-262 (TMST package authored)
- AW-251 mini-game runtime, persistence, and clue gating (complete)

## Must Not Do

- Do not call AI to decide truth, score, votes, signals, or outcomes.
- Do not emit surface-specific or rendering-specific payloads.
- Do not add new mechanic enum values outside the closed registry.

## Architecture References

- `docs/specs/0061-aw-258-tell-me-something-true.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/architecture/15-development-guide.md`
- `AGENTS.md`

## Playtest Relevance

Provides the deterministic runtime AW-266 will exercise with real humans.
