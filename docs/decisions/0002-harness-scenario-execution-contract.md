# 0002 — Harness Scenario Execution Contract

**Date:** 2026-06-01
**Status:** Accepted
**Architecture reference:** [docs/architecture/02-technology-stack.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/architecture/02-technology-stack.md), [docs/architecture/03-arc-execution.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/architecture/03-arc-execution.md), [docs/architecture/12-build-plan.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/architecture/12-build-plan.md), [docs/architecture/15-development-guide.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/architecture/15-development-guide.md)
**Spec reference:** [docs/specs/0016-aw-111-scripted-synthetic-player-driver.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/specs/0016-aw-111-scripted-synthetic-player-driver.md)
**Scope:** `engine/harness/` scripted synthetic player execution for AW-111

---

# Context

AW-111 adds a declarative scripted scenario layer on top of the AW-110 harness runner. The spec left three implementation details unresolved enough that the code needed a stable repo-local contract:

- `HarnessRun` had no participant storage, but AW-111 required stable synthetic player IDs to survive into downstream harness tooling.
- The spec described `expected_beat` as a post-transition assertion, but also required wrong-beat errors to be caught before live execution starts.
- The runner contract had no per-transition payload schema, but the scenario layer still needed basic validation.

Alternatives considered:

- Store participant IDs in a separate scenario-only lookup object. Rejected because AW-112 and later harness tooling need a canonical place on the run artifact itself.
- Try to statically predict beat outcomes without running transitions. Rejected because the existing source of truth is the AW-110 runner and `ArcStateChart`, not a parallel static analyzer.
- Invent required payload schemas for Nightcap transitions. Rejected because no such contract exists yet in the runner or coordinator design, and adding one now would ossify a premature API.

Constraints:

- Scenario execution must go through `HarnessRunner.apply_action`, not a second transition path.
- Synthetic player IDs must remain stable strings, not generated UUIDs.
- The scenario layer must stay offline and small, and must not introduce transport or provider concerns.

---

# Decision

We use the following harness scenario execution contract for AW-111:

1. `HarnessRun` includes `participants: list[str]`, populated with synthetic `player_id` values in input order during scenario execution.
2. `ScenarioExecutor` performs preflight validation by running the scripted steps through a throwaway `HarnessRunner` instance before starting the real run. `expected_beat` checks are evaluated during this preflight pass, and failures raise `ScenarioValidationError`.
3. Scenario payload validation remains intentionally narrow. The scenario layer validates actor existence, non-empty action type, and non-empty `expected_beat` when provided. Payload stays opaque and is passed through directly to `HarnessAction`.

---

# Consequences

## Positive consequences

- Stable synthetic player IDs now live on the run artifact that downstream replay and batch tooling already consumes.
- Wrong-beat scenarios fail before the live execution mutates the canonical run, while still using the real runner behavior as the source of truth.
- The scenario DSL stays small and engine-local, which matches the current harness scope and avoids inventing a premature public input contract.

## Negative consequences

- Preflight doubles the number of runner executions for successful scenarios.
- `HarnessRunner` remains the only authoritative transition validator, so scenario validation cannot be cheaper than a real step-through.
- If transition payload requirements are added later, this ADR will need to be superseded with a more explicit payload contract.

## Trade-offs

- We gain determinism, clear failures, and a canonical participant location.
- We give up a lighter-weight preflight and defer richer payload semantics until the runtime contract actually exists.

---

# References

- [docs/specs/0015-aw-110-headless-session-runner-core.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/specs/0015-aw-110-headless-session-runner-core.md)
- [docs/specs/0016-aw-111-scripted-synthetic-player-driver.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/specs/0016-aw-111-scripted-synthetic-player-driver.md)
- [docs/roadmap/tasks/AW-111-scripted-synthetic-player-driver.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/roadmap/tasks/AW-111-scripted-synthetic-player-driver.md)
- Future follow-up: pre-existing `make type` failures in `engine/arc/arc_state.py` and `engine/harness/runner.py` should be resolved before M1 is marked complete.
