# AW-111 Scripted Synthetic Player Driver

**Status**: Draft

**Author**: Codex | **Date**: 2026-05-31

---

# References

- Architecture sections: `docs/architecture/02-technology-stack.md` (§2.9), `docs/architecture/03-arc-execution.md` (§3.6, §3.7), `docs/architecture/12-build-plan.md` (§12.2 Phase 7), `docs/architecture/15-development-guide.md` (§15.9 #11)
- Related specs: `docs/specs/0015-aw-110-headless-session-runner-core.md`, `docs/specs/0013-aw-106-pre-generation-knowledge-constraint-hook.md`, `docs/specs/0014-aw-107-litellm-routing-layer.md`
- PRD sections: `docs/prd/02-requirements.md` (Principles 2 and 5)
- Roadmap task: `docs/roadmap/tasks/AW-111-scripted-synthetic-player-driver.md`
- GitHub issue: TBD

---

# Overview

Build the declarative scenario layer on top of the AW-110 runner core. Synthetic players should be describable as scripted actors whose actions drive the Nightcap scaffold without UI, network transport, or real model calls.

---

# Context From Current State

This task must respect two current-state constraints:

1. There is no canonical player-input API yet. The script layer should target the harness runner's action contract, not invent a public REST or SSE schema early.
2. Epic D completed the routing abstraction and established the testing rule that provider and model literals stay out of new harness tests. If this task needs generation seams for future extensibility, mock at `engine.routing.logging.generate` or inject a fake callable.

---

# In Scope

- Add a scenario model layer such as `engine/harness/scenario.py`
- Define a small declarative schema for:
  - synthetic players
  - initial runner seed
  - ordered scenario steps
  - optional expected beat checkpoints
- Implement a scenario executor that maps scenario steps to AW-110 runner actions
- Ensure deterministic participant identity assignment and action ordering
- Validate invalid scenarios early with clear errors:
  - unknown player id
  - invalid action type
  - step applied from the wrong beat
  - missing required payload fields
- Add focused tests, expected at `engine/tests/test_harness_scenarios.py`

---

# Out of Scope

- Batch execution and multi-run determinism summaries
- Replay diff visualization or UI
- FastAPI integration, browser simulation, or transport-level contracts
- Real AI generation or token-spending tests
- Scenario statistics beyond what is needed to prove one scripted run works

---

# Proposed Shape

```python
class ScenarioStep(BaseModel):
    actor_id: str
    action_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    expected_beat: str | None = None


class HarnessScenario(BaseModel):
    scenario_id: str
    seed: int
    players: list[SyntheticPlayer]
    steps: list[ScenarioStep]


class ScenarioExecutor:
    def run(self, scenario: HarnessScenario) -> HarnessRunResult: ...
```

The schema should stay intentionally small. It is an engine test harness contract, not the public API.

---

# Acceptance Criteria

- [ ] A declarative scenario schema exists for scripted synthetic players and ordered actions
- [ ] A scripted scenario can drive the current Nightcap scaffold from session start through reveal without UI
- [ ] Scenario execution uses AW-110 runner actions rather than inventing a separate runtime path
- [ ] Invalid or out-of-order scenario steps raise clear harness errors
- [ ] Scenario execution stays offline and mock-friendly
- [ ] No provider or model string literals are introduced in scenario code or tests
- [ ] `pytest engine/tests/test_harness_scenarios.py -v` passes

---

# Test Plan

- Unit tests: scenario model validation for missing actors, invalid actions, and wrong-beat steps
- Unit tests: happy-path scripted scenario completes the current Nightcap scaffold end-to-end
- Unit tests: participant identities and action ordering are deterministic across repeated runs
- Manual verification: run one small scenario fixture and inspect the resulting runner trace

---

# Risks and Unknowns

**Risks**:
- If the DSL becomes too expressive now, it will ossify the wrong abstraction before the real session coordinator exists.
- If scenarios bypass the AW-110 runner and call chart transitions directly, later determinism checks will be split across two code paths.
- If scenario fixtures carry provider details or raw routing assumptions, the harness will regress on Epic D's abstraction guarantees.

**Unknowns**:
- None within AW-111 scope after constraining the DSL to runner-local actions.

---

# Open Questions

- None within AW-111 scope after the Epic E split.
