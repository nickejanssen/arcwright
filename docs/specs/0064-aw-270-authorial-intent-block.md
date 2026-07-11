# AW-270: Authorial Intent Block and Intent Fidelity Telemetry

**Status**: Approved

**Author**: Founder + Claude (ADR-0012 rollout) | **Date**: 2026-07-11

---

# References

- Related ADRs: `docs/decisions/0012-authorial-intent-obligations-continuity-evals.md`
- Architecture sections: `docs/architecture/03-arc-execution.md` Section 3.8, `docs/architecture/11-telemetry.md` Section 11.8
- Related task: `docs/roadmap/tasks/AW-270-authorial-intent-block-and-fidelity-telemetry.md`
- Epic: M5-H (Narrative Fidelity Layer)

---

# Overview

Defines the optional `authorial_intent` ArcDefinition block and the intent fidelity telemetry contract for AW-270.

---

# In Scope

- Schema block, validation rules, context-assembly injection, telemetry payloads.
- The JSON contract:

```json
"authorial_intent": {
  "theme": "string, required if block present",
  "tone": "string, required if block present",
  "emotional_targets": [
    {
      "beat_id": "string, must exist in beat_graph",
      "target_tension": "float in [0.0, 1.0]",
      "note": "string, optional"
    }
  ]
}
```

- Validation rules: block optional; if present, `theme` and `tone` required, `emotional_targets` optional; every `beat_id` must exist in the arc's beat graph; `target_tension` in [0.0, 1.0]; unknown keys rejected.
- Telemetry: `tension_update` payload gains optional `target_score`; beat exit emits `intent_fidelity_summary` with `{beat_id, target_score, mean_score, mean_abs_deviation}` only for beats with a declared target.

---

# Out of Scope

- Any AI-side interpretation of intent that mutates state.
- Intent versioning or editing UI.
- Runtime intent-drift interventions (open question in ADR-0012).

---

# Acceptance Criteria

- [ ] ArcDefinition schema accepts and validates the optional `authorial_intent` block per the contract above.
- [ ] An arc without the block validates and runs unchanged.
- [ ] With the block present, `tension_update` events carry `target_score` and beat exits emit `intent_fidelity_summary`.
- [ ] Unit tests cover schema validation, context assembly inclusion, and both telemetry payloads.

---

# Test Plan

- Unit tests for the validation matrix: absent block, valid block, bad `beat_id`, out-of-range `target_tension`, unknown key.
- Context-assembly snapshot test confirming the block is injected as a cacheable layer.
- Telemetry payload tests for `target_score` and `intent_fidelity_summary`.
- One headless harness integration run with an intent-bearing arc.

---

# Risks and Unknowns

**Risks**:
- Prompt-layer growth vs caching: mitigated because the block is a static, cacheable context layer.
- Badly authored target curves: mitigated because telemetry reveals fidelity, it does not enforce it.

**Unknowns**:
- None blocking.

---

# Open Questions

- Per-beat tone overrides are deferred; not required for this spec's acceptance criteria.
