# AW-112 Deterministic Replay and Batch Runner

**Status**: Draft

**Author**: Codex | **Date**: 2026-05-31

---

# References

- Architecture sections: `docs/architecture/02-technology-stack.md` (§2.9), `docs/architecture/11-telemetry.md` (§11.1), `docs/architecture/12-build-plan.md` (§12.2 Phase 7), `docs/architecture/15-development-guide.md` (§15.9 #11)
- Related specs: `docs/specs/0015-aw-110-headless-session-runner-core.md`, `docs/specs/0016-aw-111-scripted-synthetic-player-driver.md`, `docs/specs/0014-aw-107-litellm-routing-layer.md`
- PRD sections: `docs/prd/02-requirements.md` (Principles 6 and 8)
- Roadmap task: `docs/roadmap/tasks/AW-112-deterministic-replay-and-batch-runner.md`
- GitHub issue: TBD

---

# Overview

Complete the Epic E acceptance bar by adding deterministic trace comparison and a headless batch runner that can execute scripted scenarios repeatedly without UI or token spend.

---

# Context From Current State

The build roadmap's Phase 7 lists "synthetic players, seeded runs, batch statistics." Current repo state supports only the first two layers after AW-110 and AW-111. This task finishes the deterministic and batch execution pieces without overreaching into telemetry pipelines or dashboards.

Epic D also matters here: any generation seam used during batch runs must stay mockable. The established mock target is `engine.routing.logging.route_generation` (patched with `AsyncMock`), exactly as done in `engine/tests/test_generation_logging.py`. Do not mock lower (`litellm.acompletion`) or higher (`engine.routing.logging.generate`) than this boundary -- the established pattern keeps the cost-tracking path exercisable without provider calls.

---

# In Scope

- Add a deterministic trace canonicalizer and comparer, such as `engine/harness/replay.py`
- Add a batch execution entrypoint, such as `engine/harness/batch.py`
- Support repeated scenario execution from explicit seeds
- `canonicalize_trace` strips exactly two categories of non-deterministic data before comparison:
  - wall-clock timestamp fields (any `datetime` or `float` that represents elapsed real time)
  - debug-only fields explicitly marked outside the equality path in AW-110 `HarnessTraceEntry`
  - it must NOT strip `step_index`, `transition_name`, `from_configuration`, `to_configuration`, or `payload` -- those are the structural assertion fields
- Produce a structured batch summary containing at minimum:
  - run index
  - seed used
  - scenario id
  - pass/fail result
  - failure reason (diff of canonical trace fields) when determinism breaks
- Keep the batch path offline and mock-friendly
- Add focused tests, expected at `engine/tests/test_harness_batch.py`

---

# Out of Scope

- Replay UI or diff viewer
- Telemetry table writes or metrics dashboards
- Performance benchmarking beyond proving 10 headless runs complete
- Real provider calls or live network usage
- Rich statistical analysis beyond a deterministic batch summary

---

# Proposed Shape

```python
def canonicalize_trace(trace: list[HarnessTraceEntry]) -> list[dict[str, Any]]:
    # Returns list of dicts keeping only: step_index, transition_name, from_configuration, to_configuration, payload
    # from_configuration and to_configuration are already sorted lists; no re-sort needed here
    # Omits any debug-only or wall-clock fields


def traces_equal(left: list[HarnessTraceEntry], right: list[HarnessTraceEntry]) -> bool:
    return canonicalize_trace(left) == canonicalize_trace(right)


class BatchRunResult(BaseModel):
    run_index: int
    seed: int
    scenario_id: str
    passed: bool
    failure_reason: str | None = None             # human-readable diff of canonical trace fields


class BatchSummary(BaseModel):
    scenario_id: str
    total_runs: int
    passed: int
    failed: int
    results: list[BatchRunResult]


class BatchRunner:
    def run(self, scenario: HarnessScenario, *, runs: int, base_seed: int) -> BatchSummary: ...
    # seeds each run as base_seed + run_index for full reproducibility
```

If a CLI is added, use stdlib `argparse`. Do not introduce a new dependency for this task.

---

# Acceptance Criteria

- [ ] Running the same scenario twice with the same seed produces an identical canonical trace
- [ ] The batch runner can execute 10 headless sessions from scripted scenarios without UI
- [ ] Batch output includes scenario id, per-run seed, and pass/fail summary
- [ ] The batch path remains offline and mock-friendly
- [ ] No provider or model string literals are introduced in batch code or tests
- [ ] `pytest engine/tests/test_harness_batch.py -v` passes

---

# Test Plan

- Unit tests: canonical trace comparison ignores non-deterministic debug-only fields
- Unit tests: same scenario plus same seed yields identical traces
- Unit tests: batch runner executes 10 runs and returns a complete summary structure
- Manual verification: run the batch entrypoint locally against a small scenario fixture and inspect the summary output

---

# Risks and Unknowns

**Risks**:
- If canonical traces include unstable ordering or wall-clock fields, determinism checks will produce false negatives.
- If the batch runner talks directly to generation code instead of mocking at the harness seam, the suite will become slow, costly, and flaky.
- If the batch summary tries to act like telemetry, this task will sprawl into a later milestone.

**Unknowns**:
- Whether future runtime randomness will make different seeds produce materially different traces. This task does not require cross-seed divergence, only same-seed repeatability.

---

# Open Questions

- None within AW-112 scope after the Epic E split.
