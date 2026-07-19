# ADR-0015: Nightcap Leverage advantages and sabotages architecture boundary

**Status**: Accepted

**Date**: 2026-07-18

## Context

`docs/product/nightcap-leverage-advantages-sabotages.md` records a founder-directed design catalog for Leverage — an earned resource, separate from question allowances, that players spend on advantages (sharpen their own investigation) or sabotages (interfere with a rival's). That document is explicitly design-only and states implementation requires a separate approved product decision and implementation spec.

D-075 (`docs/product/decisions-log.csv`) records the founder's approval to move Leverage to implementation scope, sequenced before/alongside AW-283, and resolves the design doc's remaining open unknowns (balance visibility, saboteur-reveal timing, cross-beat persistence, per-effect visibility). This is a multi-component architecture decision — it introduces new persistent resource state, deterministic effect resolution, event-audience privacy rules, mini-game reward coupling, telemetry, and constraints on generated-response behavior — which `AGENTS.md` requires an ADR for.

Two design alternatives were considered and rejected during the original catalog design (see the design doc's filtering rounds): a passive-shield defensive advantage (Stay Untouchable) was replaced with the counterplay-based Sting Operation because passive shields stop play without creating a readable moment; direct sabotage cancellation (Cancel the Favor, Turn the Tables) was excluded because the victim pays an opportunity cost and receives nothing in return.

A separate, launch-set-specific alternative was rejected during this ADR's authoring: **Call Their Bluff**, one of the design doc's originally-named six launch-set sabotages, requires challenging a "public theory" a player has publicly advanced. No public-theory state, event, or input model exists anywhere in the platform — AW-282's interaction runtime supports only authored target/question selections, with free text explicitly prohibited (spec 0074). Implementing Call Their Bluff would require inventing new unapproved state and input scope beyond this ADR's boundary. **Make Them Wait** (also one of the design doc's Final top five sabotages) replaces it in the v1 launch set: it reorders an already-queued interaction using state AW-282 already tracks, with no new input model required.

## Decision

We implement Leverage as a platform-neutral engine capability, following the same authored-configuration pattern as AW-282's interaction director:

- The engine owns a generic `ResourceBalance` state model (earned/spent/current amount, bank cap, protected floor), generic effect resolution (targeting eligibility, deterministic effect application, counterplay/protection windows), and generic event-audience routing for effect outcomes. No Nightcap-specific name (Leverage, Deep Read, Sting Operation, etc.) appears in engine class, field, or module names — only in Nightcap's arc/effect configuration, exactly as the design doc's "Future implementation shape" section specifies.
- Nightcap configures the six launch-set effects (Deep Read, Follow the Thread, Sting Operation, Rattle the Witness, Listen In, Make Them Wait) as authored effect definitions against that generic engine capability.
- Resource balances are public (visible to all players). Saboteur identity is withheld from the sabotage's target until the sabotaged interaction resolves (evaluated per-question, not per-round/turn), except Sting Operation, whose defining payoff is immediate source exposure to the Sting Operation user only (not table-wide). Leverage persists across beat transitions within a session, bounded by a bank cap. Per-effect visibility follows each effect's own documented behavior; there is no single global public/private toggle.
- The engine never lets a model choose targets, decide whether a sabotage succeeded, or change canonical case truth, delete evidence, or create an unfalsifiable clue. AI may only dramatize an already-resolved deterministic outcome.
- Full runtime contract, schemas, and test plan: `docs/specs/0075-aw287-nightcap-leverage-advantages-sabotages.md`.

## Consequences

### Positive consequences
- Other games can configure entirely different resource economies, effect catalogs, and vocabulary without engine changes, consistent with the platform's game-agnosticism principle.
- Reuses AW-282's existing public/private ContentEvent audience routing rather than inventing a new privacy primitive.
- The six-effect launch set is fully supported by state AW-282 and AW-283 already track (question/target selections, evidence, claims); no speculative new input model is introduced.

### Negative consequences
- Adds a second economy (alongside question tokens) that session pacing and cost telemetry must account for.
- Danger-combination guardrails (one offensive modifier per interaction, one information-control sabotage per player per beat, post-target protection window) add real-time eligibility-checking complexity to interaction resolution.

### Trade-offs
- We gained a deterministic, generically-named capability that fits the existing interaction-modifier seam AW-282 was built to leave open, at the cost of dropping Call Their Bluff from the v1 launch set until a public-theory contract is separately designed and approved.

## References

- `docs/product/nightcap-leverage-advantages-sabotages.md` (design catalog)
- `docs/product/decisions-log.csv` D-075 (implementation approval and resolved unknowns)
- `docs/product/aw287-discovery-and-checkpoints.md` (discovery and checkpoint record)
- `docs/specs/0075-aw287-nightcap-leverage-advantages-sabotages.md` (implementation spec)
- `docs/specs/0074-aw282-structured-interaction-loop.md`, `docs/decisions/0014-structured-interaction-resolution.md` (interaction-modifier seam this plugs into)
- `docs/roadmap/tasks/AW-287-nightcap-leverage-advantages-and-sabotages.md`
