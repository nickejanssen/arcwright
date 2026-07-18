# AW-272: Continuity and Coherence Eval Suite

**Status**: Approved

**Author**: Founder + Claude (ADR-0012 rollout) | **Date**: 2026-07-11

---

# References

- Related ADRs: `docs/decisions/0012-authorial-intent-obligations-continuity-evals.md`
- Architecture sections: `docs/architecture/04-knowledge-graph.md` Section 4.3, `docs/architecture/11-telemetry.md` Sections 11.6 and 11.8
- Related task: `docs/roadmap/tasks/AW-272-continuity-coherence-eval-suite.md`
- Epic: M5-H (Narrative Fidelity Layer)

---

# Overview

Defines the continuity and coherence eval suite for AW-272.

---

# In Scope

- Runner `evals/runners/test_continuity_evals.py`; deterministic checks only in v1.
- Checks:
  1. Knowledge-leak: for every generated character output in a session log, compare referenced fact payloads against the character's knowledge state at generation time; any reference to a fact outside the state is a leak.
  2. Contradiction: a character output referencing a fact the character holds with a superseding revocation (per the revoke operation in `docs/architecture/04-knowledge-graph.md` Section 4.3) counts as a contradiction.
- Report JSON:

```json
{
  "batch_id": "string",
  "sessions": [
    {
      "session_id": "string",
      "knowledge_leaks": 0,
      "contradictions": 0,
      "generations_checked": 0
    }
  ],
  "aggregate": {
    "knowledge_leak_rate": 0.0,
    "contradiction_count": 0
  }
}
```

- Thresholds from a config file (`evals/continuity_thresholds.json`), defaults `knowledge_leak_rate <= 0.0` and `contradiction_count == 0` fail-fast values, adjustable without code changes.

---

# Out of Scope

- Model-graded rubric evals (cost policy; revisit at Tier 2).
- Runtime enforcement (this is the ADR-0012 watchpoint open question).
- Intent-fidelity evals (depends on AW-270, post-M6).

---

# Human Collaboration Contract

**Interaction profile:** Independent execution.

This spec and Decision 0012 fully constrain eval cases, grading, thresholds,
and reporting. After normal plan approval, the agent may execute and must
explain what each signal means, how to review it, and what requires attention.

Stop and reclassify to Creative collaboration or Decision interview before
changing narrative quality criteria, thresholds, telemetry meaning, privacy
behavior, or eval scope. Record plan approval, eval results, threshold evidence,
dates, and owner actions.

# Acceptance Criteria

- [ ] `pytest evals/runners/test_continuity_evals.py -q` runs against a recorded or freshly generated synthetic session batch and produces the JSON report.
- [ ] A seeded session with a deliberate injected leak is detected (true-positive test); a clean session reports zero leaks (false-positive guard).
- [ ] Thresholds are configurable without code changes.
- [ ] Report format documented in this spec.

---

# Test Plan

- Seeded true-positive session fixture with a deliberate injected knowledge leak.
- Clean-session false-positive guard reporting zero leaks.
- Batch aggregation test over 10 synthetic sessions.

---

# Risks and Unknowns

**Risks**:
- Fact-payload string matching misses paraphrased leaks: accepted v1 limitation, documented in the report header; classifier upgrade is the ADR-0012 watchpoint.

**Unknowns**:
- None blocking.

---

# Open Questions

- Whether eval batches run in CI on every PR or nightly. Default: nightly plus pre-playtest manual run.
