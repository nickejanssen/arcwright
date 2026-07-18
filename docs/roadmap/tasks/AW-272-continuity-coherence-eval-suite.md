# AW-272: Continuity and Coherence Eval Suite

**Milestone / Epic:** M5 / M5-H
**Size:** M
**Status:** Planned

## Plain-English Summary

Build a continuity eval suite on the existing eval harness and headless
session runner that replays synthetic sessions and reports, at minimum,
knowledge-leak rate (an AI character referencing a fact outside its
knowledge state) and character-contradiction count.

## Why This Matters

The mandatory pre-generation knowledge query constrains prompts, but nothing
verifies the model actually respected the constraint. ADR-0012 adopted
offline evals as the first consumer of the Tier 2 "behavior consistency
score" signal. This also contributes to the open product question requiring
narrative quality metrics before the first M3 simulation-harness batch.

## Player Impact

Knowledge leaks and character contradictions are caught on synthetic
sessions before real groups ever see them.

## Business Value

A repeatable narrative-quality gate raises confidence going into M6
qualifying sessions and produces the labeled continuity data that the
Tier 2 transition needs.

## Technical Scope

- New eval runner at `evals/runners/test_continuity_evals.py` following the
  AW-224 batch-harness and spec 0004 eval-harness patterns.
- Deterministic checks first: fact-payload matching between generated
  character output and the character's knowledge state at generation time.
  No model-graded checks in v1 (cost policy; see spec 0066).
- Metrics emitted as a JSON report: `knowledge_leak_rate`,
  `contradiction_count`, per-session and batch aggregate.
- Configurable pass thresholds; suite is runnable locally and in CI batch
  mode.

## Human Collaboration Contract

**Interaction profile:** Independent execution.

**Why independent:** Decision 0012 and
`docs/specs/0066-aw-272-continuity-coherence-evals.md` constrain the eval cases,
grading rules, thresholds, and reporting contract.

**Required flow:** After normal plan approval, implement the documented suite,
explain each signal and how to review it, and verify the acceptance criteria
without redefining quality policy.

**Reclassification gate:** Stop and switch to Creative collaboration or
Decision interview before changing narrative quality criteria, thresholds,
telemetry meaning, privacy behavior, or eval scope.

**Evidence:** Preserve plan approval, canonical-source references, eval results,
threshold evidence, dates, and owner actions.

## Acceptance Criteria

- [ ] `pytest evals/runners/test_continuity_evals.py -q` runs against a
  recorded or freshly generated synthetic session batch and produces the
  JSON report.
- [ ] A seeded session with a deliberate injected leak is detected
  (true-positive test); a clean session reports zero leaks
  (false-positive guard).
- [ ] Thresholds are configurable without code changes.
- [ ] Report format documented in spec 0066.

## Tests/Verification

- `pytest evals/runners/test_continuity_evals.py -q` passes.
- Batch run over at least 10 synthetic sessions completes and the report
  aggregates correctly.

## Dependencies

- `docs/specs/0066-aw-272-continuity-coherence-evals.md`
- Headless session runner (AW-110/AW-112) and batch harness (AW-224)

## Must Not Do

- Do not use frontier-model graded evals in v1; deterministic checks only
  per the AI cost policy.
- Do not couple checks to any game-specific fact vocabulary; operate on
  knowledge-graph structures only.
- Do not block M6 qualifying sessions on new eval infrastructure beyond the
  M5 exit-gate line added for this task.

## Architecture References

- `docs/decisions/0012-authorial-intent-obligations-continuity-evals.md`
- `docs/architecture/04-knowledge-graph.md` Section 4.3
- `docs/architecture/11-telemetry.md` Sections 11.6 and 11.8

## Playtest Relevance

Pre-M6. Runs against synthetic session batches before qualifying sessions
so continuity regressions surface before real groups play.
