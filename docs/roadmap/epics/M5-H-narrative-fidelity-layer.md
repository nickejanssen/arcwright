# M5-H: Narrative Fidelity Layer

**Milestone:** M5  
**Status:** Planned

## Plain-English Summary

Adopt the three ADR-0012 narrative fidelity improvements: a continuity and
coherence eval suite (pre-M6), an optional authorial intent block in the
ArcDefinition schema with intent fidelity telemetry (post-M6), and a
narrative obligations model with a generic reveal-readiness condition
(post-M6).

## Why This Matters

ADR-0012 compared the platform against the dissertation-derived story-logic
framework and adopted three gaps as scope: no structured soft authorial
logic, no durable tracking of narrative obligations (including
pacing-injected misdirection), and no offline verification that generation
respected knowledge-state constraints. This epic closes them without
touching the M6 qualifying-session critical path.

## Player Impact

Sessions deliver the emotional shape the author designed, dangling threads
get resolved before the reveal, and continuity regressions are caught on
synthetic sessions before real groups play.

## Business Value

Intent fidelity curves and obligation lifecycle data are additional Tier 2
training signals; the eval suite is a repeatable narrative-quality gate that
raises confidence going into qualifying sessions.

## Tasks

- [AW-272: Continuity and Coherence Eval Suite](../tasks/AW-272-continuity-coherence-eval-suite.md)
- [AW-270: Authorial Intent Block and Intent Fidelity Telemetry](../tasks/AW-270-authorial-intent-block-and-fidelity-telemetry.md) (post-M6)
- [AW-271: Narrative Obligations Model and Reveal-Readiness Condition](../tasks/AW-271-narrative-obligations-model.md) (post-M6)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- AW-272 completes before M6 qualifying sessions; AW-270 and AW-271 remain
  sequenced post-M6 unless the founder re-sequences.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task
  issue.
- Verify the parent milestone exit gate still matches
  `docs/roadmap/00-overview.md`.

## Dependencies

- Parent milestone: M5
- ADR-0012 (`docs/decisions/0012-authorial-intent-obligations-continuity-evals.md`)

## Must Not Do

- Do not let intent or obligation features introduce AI-managed session
  state; state transitions stay deterministic.
- Do not turn game-specific vocabulary into platform assumptions.
- Do not block M6 on AW-270 or AW-271.

## Architecture References

- `docs/decisions/0012-authorial-intent-obligations-continuity-evals.md`
- `docs/architecture/03-arc-execution.md`
- `docs/architecture/11-telemetry.md`

## Playtest Relevance

AW-272 strengthens the measurement quality of the M6 qualifying sessions;
the other two tasks harden the platform for the sessions after proof.
