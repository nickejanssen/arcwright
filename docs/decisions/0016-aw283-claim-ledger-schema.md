# ADR-0016: AW-283 claim ledger gets a dedicated database schema

**Status**: Accepted

**Date**: 2026-07-19

## Context

AW-283 needs claim provenance to be queryable per session — an acceptance criterion that AW-282 and AW-287 didn't have, since both stayed entirely in-memory (`InteractionDirector`, `ResourceResolver`) with no DB persistence at all. AW-283's claim ledger is different: it must survive to feed the end-of-session reveal accounting, and it is explicitly named the platform's headline differentiated mechanic ("suspects remember what they said, and catching a lie is a provenance query" — AW-283's own Why-This-Matters framing) and the labeled continuity data source for AW-272 evals and the future Daily Case wedge (D-034).

Two options were considered:

1. **Reuse the existing `events` table.** Every claim becomes a row with `event_type="claim_recorded"` and a JSONB payload, following the pattern `engine/telemetry/obligations.py` and `engine/telemetry/resources.py` already use for telemetry signals. Zero migration, immediately available.
2. **Add dedicated `claims` and `contradiction_flags` tables** with real typed, indexed columns.

The founder explicitly delegated the choice ("do what is best for a world class architecture, product, gameplay, design, user experience and a billion dollar game") rather than picking between the two presented options.

## Decision

We add dedicated `claims` and `contradiction_flags` tables (migration `0006_claims_contradiction_flags`), not the generic `events` table.

Per `docs/architecture/11-telemetry.md`, the `events` table's stated purpose is append-only audit/analytics telemetry — its own documented concern includes GDPR deletion handling (`content_text` nullification) and is optimized for write-once, read-rarely analysis. Claims are the opposite access pattern: they are queried on the hot path, every time any player flags a statement, for the lifetime of a session, and they are the direct input to a live gameplay decision (confirmed vs. rejected), not a downstream analytics signal. Conflating the two would mean a core gameplay-state read competing with, and architecturally indistinguishable from, generic telemetry writes in the same table — and would require JSONB containment queries in place of indexed foreign-key lookups (`session_id, speaker_character_id`, `session_id, beat_id`) for a mechanic explicitly billed as this platform's flagship differentiator.

Telemetry *about* claims (recording that a claim was generated, that a flag resolved a certain way, for later analysis) still uses the generic `events` table via `engine/telemetry/claims.py`, following the existing `engine/telemetry/obligations.py`/`resources.py` pattern exactly — this ADR does not change that. Only the canonical, live-queried claim/flag *state* gets its own schema.

## Consequences

### Positive consequences
- Reliable, efficiently queryable, typed access for AW-272 evals and the eventual Daily Case wedge, both of which need structured ground-truth claim data, not JSONB parsing.
- Claim and contradiction-flag data has real foreign keys to `sessions`, `characters`, `session_participants` — referential integrity the generic `events` table doesn't offer.
- Keeps the `events` table's purpose (audit/analytics) uncontaminated by hot-path gameplay-state reads.

### Negative consequences
- A real migration (schema surface, downgrade path) to maintain, versus zero new schema for the events-table alternative.
- Two new tables to reason about alongside the existing `events`/`obligations` pattern, rather than one unified telemetry sink.

### Trade-offs
- We gained query performance and referential integrity for the platform's headline mechanic, at the cost of migration/schema maintenance overhead that the events-table alternative would have avoided entirely.

## References

- `docs/product/decisions-log.csv` D-078 (approval record)
- `docs/roadmap/tasks/AW-283-suspect-answer-generation-and-contradiction-detection.md`
- `docs/superpowers/plans/2026-07-19-aw283-suspect-answer-generation.md` (implementation plan, Task 2)
- `docs/architecture/11-telemetry.md` (the `events` table's documented purpose)
- `engine/telemetry/obligations.py`, `engine/telemetry/resources.py` (the telemetry pattern this ADR does NOT change)
