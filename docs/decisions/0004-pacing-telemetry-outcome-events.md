# 0004 - Pacing Telemetry Outcome Events

**Date:** 2026-06-10
**Status:** Accepted
**Architecture reference:** `docs/architecture/03-arc-execution.md`, `docs/architecture/11-telemetry.md`
**Spec reference:** `docs/specs/0027-aw-207-dramatic-tension-pacing-engine.md`
**Scope:** AW-207 pacing telemetry events, pacing intervention descriptors, and future pacing-loop outcome emission

---

# Context

AW-207 implements the deterministic dramatic tension pacing core. The existing telemetry architecture described a single `pacing_intervention` event with `outcome_resumed_within_60s` in the same payload.

That shape conflicts with the append-only `events` table contract in `docs/architecture/11-telemetry.md`. Whether player activity resumed within 60 seconds is not known when the pacing intervention first fires. Writing the trigger event and updating it later would violate the append-only telemetry model.

AW-207 also introduces `quality_upgrade` as a pacing descriptor for peak dramatic moments. It is a pacing decision, but it does not inject a player-facing stall or misdirection intervention and has no meaningful 60-second resumed-activity outcome.

Alternatives considered:

- Keep `outcome_resumed_within_60s` on `pacing_intervention` and update the row later. Rejected because the `events` table is append-only.
- Store pacing outcomes only in `decision_logs`. Rejected because pacing intervention triggers and outcomes are one of the five MVP telemetry signals and need event-table visibility.
- Emit `pacing_intervention` events for `quality_upgrade`. Rejected because quality-tier upgrades do not have resumed-activity semantics and would pollute player-facing intervention metrics.

Constraints:

- `events` records are never updated or deleted.
- MVP telemetry Signal 2 must capture pacing intervention triggers and outcomes.
- Pacing must remain platform-generic and must not hardcode Nightcap-specific signal derivation.
- AW-207 does not include the async pacing loop that waits 60 seconds and emits follow-up outcomes.

---

# Decision

We use a two-event append-only telemetry model for player-facing pacing intervention triggers and outcomes:

1. `tension_update` is emitted on each pacing poll with `payload = {"score": float, "beat_id": str}`.
2. `pacing_intervention` is emitted at trigger time only for `stall` and `misdirection`, with `payload = {"trigger_type": "stall" | "misdirection", "tension_score_at_trigger": float, "beat_id": str}`.
3. `pacing_intervention_outcome` is emitted after the follow-up window for the same player-facing intervention, with `payload = {"trigger_type": "stall" | "misdirection", "tension_score_at_trigger": float, "beat_id": str, "outcome_resumed_within_60s": bool}`.
4. `quality_upgrade` is a pacing decision descriptor, not a `pacing_intervention` event. It is captured through tension updates, generation logs when routing integration uses the score, and decision-log payloads when persistence integration is wired.
5. AW-207 defines payload builders only. The future async pacing-loop or session coordinator integration owns waiting 60 seconds, assessing resumed activity, and emitting `pacing_intervention_outcome`.

---

# Consequences

## Positive consequences

- Pacing telemetry preserves the append-only integrity of the `events` table.
- Trigger-time and outcome-time facts are recorded when they become known.
- MVP telemetry Signal 2 remains queryable through the event stream.
- Quality-tier upgrades do not distort stall and misdirection intervention metrics.
- Future coordinator work has a clear ownership boundary for delayed outcome emission.

## Negative consequences

- Consumers must join or correlate trigger and outcome events by session, beat, trigger type, and time window instead of reading one event payload.
- Telemetry readers must know that `quality_upgrade` is found in decision logs and generation logs, not in `pacing_intervention` outcome events.

## Trade-offs

- We gain append-only correctness and clearer telemetry semantics.
- We accept a slightly richer event taxonomy and defer delayed emission wiring to the async pacing-loop work.

---

# References

- `docs/architecture/03-arc-execution.md`
- `docs/architecture/11-telemetry.md`
- `docs/specs/0027-aw-207-dramatic-tension-pacing-engine.md`
- `docs/roadmap/tasks/AW-207-dramatic-tension-pacing-engine.md`
