# AW-271: Narrative Obligations Model and Reveal-Readiness Condition

**Status**: Approved

**Author**: Founder + Claude (ADR-0012 rollout) | **Date**: 2026-07-11

---

# References

- Related ADRs: `docs/decisions/0012-authorial-intent-obligations-continuity-evals.md`
- Architecture sections: `docs/architecture/03-arc-execution.md` Sections 3.2 and 3.8, `docs/architecture/supplemental-schemas.md` (`obligations`), `docs/architecture/11-telemetry.md` Section 11.8
- Related task: `docs/roadmap/tasks/AW-271-narrative-obligations-model.md`
- Epic: M5-H (Narrative Fidelity Layer)

---

# Overview

Defines the `obligations` table, lifecycle, reveal-readiness condition, and telemetry for AW-271.

---

# In Scope

DDL:

```sql
CREATE TABLE obligations (
    obligation_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id     UUID NOT NULL REFERENCES sessions(session_id),
    source_type    TEXT NOT NULL,   -- "authored" | "pacing_misdirection" | "generative"
    source_ref     JSONB NOT NULL DEFAULT '{}',  -- fact_id, event_id, or arc element id
    description    TEXT NOT NULL,
    mandatory      BOOLEAN NOT NULL DEFAULT false,
    status         TEXT NOT NULL DEFAULT 'open', -- "open" | "resolved" | "expired"
    created_beat   TEXT NOT NULL,
    resolved_beat  TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at    TIMESTAMPTZ
);
CREATE INDEX ON obligations (session_id, status);
```

Lifecycle: only deterministic engine paths mutate obligation state (arc-authored setups registered at session start from the arc definition; pacing misdirection injection auto-creates one record; resolution happens on deterministic triggers such as fact delivery or beat transition, per arc configuration). Session context key `all_mandatory_obligations_resolved` computed on every context refresh; arcs reference it in `exit_conditions` exactly like any other condition key (Section 3.2 contract; the engine never interprets the name). Telemetry: `obligation_created` payload `{obligation_id, source_type, mandatory, beat_id}`; `obligation_resolved` payload `{obligation_id, resolution_beat, open_duration_seconds}`.

---

# Out of Scope

- AI-graded obligation resolution.
- Obligation inference.
- UI surfaces.

---

# Acceptance Criteria

- [ ] Migration applies cleanly to empty and populated schemas.
- [ ] Pacing misdirection injection writes an obligation record.
- [ ] `all_mandatory_obligations_resolved` appears in session context and gates a test arc's exit condition correctly.
- [ ] Both telemetry events are emitted and logged to the events table.
- [ ] Unit tests cover obligation lifecycle, the session-context boolean, and telemetry emission.

---

# Test Plan

- Lifecycle unit tests covering creation, resolution, and expiration.
- Misdirection-injection integration test verifying automatic obligation creation.
- Exit-condition gating test in the headless harness.
- Migration up/down test.

---

# Risks and Unknowns

**Risks**:
- Obligation spam from repeated misdirections: mitigated because the pacing engine already rate-limits interventions.
- Schema churn: mitigated because the JSONB `source_ref` keeps references flexible.

**Unknowns**:
- None blocking.

---

# Open Questions

- Expiration semantics for non-mandatory obligations at session end. Default: mark `expired` on session completion.
