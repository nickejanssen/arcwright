# ADR-0014: Structured interaction resolution boundary

**Status**: Accepted

**Date**: 2026-07-18

## Context

Arcwright needs menu-driven questioning for Nightcap and future games without placing game-specific logic in the engine or allowing generated prose to mutate canonical session state. Public answers and private player feedback must use the existing ContentEvent audience boundary.

## Decision

We use an authored, deterministic InteractionDefinition and InteractionDirector in Python. The director owns option eligibility, count-specific per-beat allowances, private selections, deterministic resolution order, public grouping, and immutable InteractionResolution records. Every selected question becomes a public answer request. Authored private options additionally create private feedback for the selecting player. InteractionRuntime consumes arc beat references and emits existing ContentEvent shapes. AW-283 consumes immutable resolution context and generates answer content without deciding canonical state.

## Consequences

- The engine remains surface-agnostic and provider-agnostic.
- Different games can author different options, targets, evidence gates, and player-count allowances.
- Public and private delivery stays within the existing event fanout contract.
- Answer generation and contradiction logic remain a separate follow-on boundary.
- Per-beat allowance accounting must be preserved if interaction windows are reopened for another round.

## References

- `docs/specs/0074-aw282-structured-interaction-loop.md`
- `docs/superpowers/specs/2026-07-18-aw282-structured-interaction-design.md`
- `docs/architecture/08-event-system.md`
