# AW-270: Authorial Intent Block and Intent Fidelity Telemetry (post-M6)

**Milestone / Epic:** M5 / M5-H
**Size:** M
**Status:** Planned (post-M6)

## Plain-English Summary

Add an optional `authorial_intent` block to the ArcDefinition schema carrying
theme, tone, and per-beat emotional targets (a target tension value per beat).
The engine injects the block into generation context assembly and logs
realized-versus-intended tension per beat so arc authors can see whether
sessions delivered the emotional shape they designed.

## Why This Matters

ADR-0012 identified this as the missing structured representation of soft
authorial logic. The pacing engine computes a live dramatic tension score
today but has no authored target curve to compare it against. This deepens
human arc primacy: the author declares intended emotional shape, the runtime
measures fidelity to it.

## Player Impact

Indirect. Sessions track closer to the emotional arc the author designed,
and future arc tuning is driven by fidelity data instead of guesswork.

## Business Value

Realized-versus-intended tension curves are an additional Tier 2 training
signal collected at near-zero marginal cost, strengthening the proprietary
session-data moat described in `docs/architecture/11-telemetry.md`.

## Technical Scope

- Extend ArcDefinition schema validation (AW-203 lineage) with an optional
  `authorial_intent` block: `theme` (string), `tone` (string),
  `emotional_targets` (list of `{beat_id, target_tension, note}`).
- Schema validation rejects `emotional_targets` entries whose `beat_id` is
  not in the arc's beat graph and `target_tension` outside [0.0, 1.0].
- Context assembly includes the block in generation prompts as a cacheable
  context layer per the prompt-caching requirement.
- When `emotional_targets` is present, `tension_update` telemetry events
  gain a `target_score` payload field, and beat exit emits
  `intent_fidelity_summary` with `{beat_id, target_score, mean_score,
  mean_abs_deviation}`.
- Existing arcs without the block remain valid; no behavior change when the
  block is absent.

## Human Collaboration Contract

**Interaction profile:** Independent execution.

**Why independent:** Decision 0012 and
`docs/specs/0064-aw-270-authorial-intent-block.md` constrain the intent block,
telemetry semantics, authority boundary, and verification requirements.

**Required flow:** After normal plan approval, implement the approved contract,
explain the telemetry and authority behavior clearly, and verify the acceptance
criteria without widening the signal set.

**Reclassification gate:** Stop and switch to Decision interview before changing
the intent model, telemetry meaning, privacy posture, schema, or implementation
sequence.

**Evidence:** Preserve plan approval, canonical-source references, tests,
telemetry verification, dates, and owner actions.

## Acceptance Criteria

- [ ] ArcDefinition schema accepts and validates the optional
  `authorial_intent` block per spec 0064.
- [ ] An arc without the block validates and runs unchanged.
- [ ] With the block present, `tension_update` events carry `target_score`
  and beat exits emit `intent_fidelity_summary`.
- [ ] Unit tests cover schema validation, context assembly inclusion, and
  both telemetry payloads.

## Tests/Verification

- `pytest engine/tests/` passes with new schema and telemetry tests.
- Headless harness run with an intent-bearing arc shows both new event
  types in the events log.

## Dependencies

- `docs/specs/0064-aw-270-authorial-intent-block.md`
- ADR-0012, `docs/architecture/03-arc-execution.md` Section 3.8

## Must Not Do

- Do not let intent fields override deterministic state transitions; intent
  is generation context and telemetry comparison only.
- Do not make the block mandatory for any arc.
- Do not hardcode any game-specific beat IDs or theme vocabulary in the
  engine.
- Do not start implementation before M6 exit unless the founder re-sequences.

## Architecture References

- `docs/decisions/0012-authorial-intent-obligations-continuity-evals.md`
- `docs/architecture/03-arc-execution.md` Sections 3.3 and 3.8
- `docs/architecture/11-telemetry.md` Section 11.8

## Playtest Relevance

Post-M6. Provides the fidelity instrumentation used to tune arcs after the
first qualifying sessions.
