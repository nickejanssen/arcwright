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

The build roadmap's Phase 7 lists "synthetic players, seeded runs, batch statistics." Current repo state supports only the first two layers after AW-110 and AW-111. This task should finish the deterministic and batch execution pieces without overreaching into telemetry pipelines or dashboards.

Epic D also matters here: any generation seam used during batch runs must stay mockable, and any routing-aware tests must continue deriving behavior from helper boundaries instead of embedding provider/model literals.

---

# In Scope

- Add a deterministic trace canonicalizer and comparer, such as `engine/harness/replay.py`
- Add a batch execution entrypoint, such as `engine/harness/batch.py`
- Support repeated scenario execution from explicit seeds
- Produce a structured batch summary containing at minimum:
  - run index
  - seed
  - scenario id
  - pass/fail result
  - failure reason when determinism breaks
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
def canonicalize_trace(trace: list[HarnessTraceEntry]) -> list[dict[str, Any]]: ...


def traces_equal(left: list[HarnessTraceEntry], right: list[HarnessTraceEntry]) -> bool: ...


class BatchRunner:
    def run(self, scenario: HarnessScenario, *, runs: int, base_seed: int) -> BatchSummary: ...
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
