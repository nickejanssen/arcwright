# AW-281: Couch Race Arc Definition And Case Generation

**Milestone / Epic:** M5 / M5-I
**Size:** L
**Status:** Planned

## Plain-English Summary

Author the canonical Couch Race ArcDefinition (six beats: The Pour, The Scene, The Grill, The Twist, Last Call, The Truth) and the deterministic case-generation step that resolves suspect cast, killer, victim, method, motive, clue web, twist, and authorized suspect lies at session start.

## Why This Matters

This is the charter task of ADR-0013: the new arc is the v1 launch experience. Beat count is arc-level (D-053), so this is arc content plus generation templates, not engine schema change.

## Player Impact

Every session becomes a unique, fair, solvable 20–40 minute case.

## Business Value

Structural replayability is the product's differentiation; it lives in this generation step.

## Technical Scope

- New arc JSON following the AW-205 canonical-arc pattern, with six beats, beat exit conditions, and pacing targets per the bible Section 4.
- Case resolution at session start: 4–6 suspects plus victim as unified-model AI characters, exactly one killer knowledge set, per-suspect secrets and authorized falsifiable lies, genuine clue chain sufficient to solve (balance principle), deterministic twist selection.
- Clue web resolution reusing existing clue delivery types and puzzle gating; mini-game slots at Beat 2 (competitive) and Beat 4 (solo) using existing packages.
- All generative composition (names, dialogue color, case flavor) happens from resolved structured state; AI never chooses case truth.

## Acceptance Criteria

- [ ] A headless harness run completes all six beats with synthetic players at counts 2 and 8.
- [ ] Case resolution is reproducible under a fixed seed (deterministic replay per AW-112).
- [ ] Every authorized suspect lie is falsifiable against the resolved genuine evidence set (validation check in arc tests).
- [ ] Arc validates against ArcDefinition schema with zero engine schema changes, or any required schema change goes through the Hard Rules review path.

## Tests/Verification

- `pytest engine/tests/` arc tests pass, including seed-reproducibility and lie-falsifiability checks.
- Batch harness run of 10 headless Couch Race sessions completes.

## Dependencies

- `docs/specs/0072-nightcap-couch-race-v1.md`
- `docs/story-bibles/nightcap-couch-race.md`
- AW-203/AW-204/AW-205 arc infrastructure; AW-249–AW-253 mini-game layer

## Must Not Do

- Do not let any model call decide killer, victim, motive, method, clue truth values, or lie authorization.
- Do not hardcode beat IDs in engine code (AW-256 lesson).
- Do not implement teams/co-op dial positions.

## Architecture References

- `docs/architecture/03-arc-execution.md`
- `docs/decisions/0013-nightcap-couch-race-v1-launch-target.md`

## Playtest Relevance

Direct: this arc is what Rehearsal 1 (retargeted) runs.
