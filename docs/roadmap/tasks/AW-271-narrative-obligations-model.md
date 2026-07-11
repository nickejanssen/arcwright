# AW-271: Narrative Obligations Model and Reveal-Readiness Condition (post-M6)

**Milestone / Epic:** M5 / M5-H
**Size:** M
**Status:** Planned (post-M6)

## Plain-English Summary

Track narrative obligations (authored setups, promises requiring payoff, and
any pacing-engine misdirection injection) as durable session state, and
expose a generic `all_mandatory_obligations_resolved` boolean in the session
context so arcs can use it as a beat exit condition.

## Why This Matters

ADR-0012 identified an untracked coherence hole: when the pacing engine
injects a generative red herring, no platform state records that the
misdirection exists and should be acknowledged or resolved before the arc's
resolution beat. Obligations close that hole with deterministic state,
consistent with the principle that AI never manages canonical session state.

## Player Impact

Sessions stop leaving dangling threads: an injected misdirection is
guaranteed to be addressed before the resolution beat when the arc marks it
mandatory.

## Business Value

Obligation lifecycle telemetry (created, resolved, expired) becomes a
coherence quality signal across sessions and a Tier 2 training input.

## Technical Scope

- New `obligations` table per `docs/architecture/supplemental-schemas.md`;
  requires an Alembic migration (schema-change hard rule: migration plus
  review per `AGENTS.md`).
- Obligation records carry `source_type` (`authored`, `pacing_misdirection`,
  `generative`), `mandatory` flag, `status` (`open`, `resolved`, `expired`),
  creating beat, and resolving beat.
- Pacing-engine misdirection injection creates an obligation record
  automatically; whether it is mandatory is arc-configurable.
- Session context exposes `all_mandatory_obligations_resolved`, evaluated
  generically like all exit conditions per the contract in
  `docs/architecture/03-arc-execution.md` Section 3.2. No beat IDs or
  obligation names in engine code.
- Telemetry: `obligation_created` and `obligation_resolved` events per
  `docs/architecture/11-telemetry.md` Section 11.8.

## Acceptance Criteria

- [ ] Migration applies cleanly to empty and populated schemas.
- [ ] Pacing misdirection injection writes an obligation record.
- [ ] `all_mandatory_obligations_resolved` appears in session context and
  gates a test arc's exit condition correctly.
- [ ] Both telemetry events are emitted and logged to the events table.
- [ ] Unit tests cover obligation lifecycle, the session-context boolean,
  and telemetry emission.

## Tests/Verification

- `pytest engine/tests/` passes with obligation lifecycle tests.
- `alembic upgrade head` applies the migration cleanly.
- Headless harness run shows an injected misdirection producing an
  obligation record and the reveal gate holding until resolution.

## Dependencies

- `docs/specs/0065-aw-271-narrative-obligations-model.md`
- ADR-0012, `docs/architecture/03-arc-execution.md` Section 3.8

## Must Not Do

- Do not let AI generation create or resolve obligations directly; only
  deterministic engine paths mutate obligation state.
- Do not hardcode game-specific obligation names or beat IDs in engine code.
- Do not skip the migration review hard rule.
- Do not start implementation before M6 exit unless the founder re-sequences.

## Architecture References

- `docs/decisions/0012-authorial-intent-obligations-continuity-evals.md`
- `docs/architecture/03-arc-execution.md` Sections 3.2 and 3.8
- `docs/architecture/supplemental-schemas.md` (`obligations`)
- `docs/architecture/11-telemetry.md` Section 11.8

## Playtest Relevance

Post-M6. Hardens coherence for the sessions that follow the first
qualifying playtests.
