# AW-110 Headless Session Runner Core

**Status**: Draft

**Author**: Codex | **Date**: 2026-05-31

---

# References

- Architecture sections: `docs/architecture/03-arc-execution.md` (§3.1, §3.2, §3.6, §3.7), `docs/architecture/05-session-persistence.md` (§5.2-§5.4), `docs/architecture/12-build-plan.md` (§12.2 Phase 7), `docs/architecture/15-development-guide.md` (§15.3, §15.9 #11)
- Related specs: `docs/specs/0009-aw-101-repository-structure-and-python-project-setup.md`, `docs/specs/0011-aw-103-sqlalchemy-orm-models.md`, `docs/specs/0013-aw-106-pre-generation-knowledge-constraint-hook.md`, `docs/specs/0014-aw-107-litellm-routing-layer.md`
- PRD sections: `docs/prd/02-requirements.md` (Principles 2, 5, and 8)
- Roadmap task: `docs/roadmap/tasks/AW-110-simulation-harness-skeleton.md`
- GitHub issue: TBD

---

# Overview

Build the engine-local runner that the rest of Epic E depends on. It must load the current Nightcap arc scaffold, instantiate session state, advance the `ArcStateChart` from deterministic inputs, and emit a stable trace for tests without involving UI, SSE, or real provider calls.

---

# Context From Current State

Three facts constrain this task:

1. `engine/arc/arc_state.py` is the only executable arc runtime currently present. It is a scaffolded `ArcStateChart`, not yet the future generated chart from architecture §3.2.
2. `engine/events`, `engine/safety`, and `engine/telemetry` do not yet provide runnable runtime services. The harness runner must stay in-process and self-contained.
3. Epic D completed the routing abstraction. If this task touches any generation boundary, the logging-aware entrypoint is `engine.routing.logging.generate`, not `engine.routing.router.route_generation`. Prompt assembly must use `build_character_generation_context` and `CharacterGenerationContext` from `engine.characters`, which are the implemented names from Epic C.

This means AW-110 is a runner-core task, not a full session coordinator, and not a networked gameplay loop.

**Arc transition names.** The `ArcStateChart` transitions the runner must fire in happy-path order are:

| Transition | Effect |
|---|---|
| `begin_game` | introduction.onboarding → introduction.killer_assignment |
| `motives_established` | introduction.killer_assignment → introduction.motive_reveal (final) |
| `investigation_begins` | introduction → investigation |
| `clues_sent` | investigation.clue_phase.private_clues.distributing → distributed |
| `interrogation_complete` | investigation.clue_phase.interrogation.open → closed |
| `phases_complete` | investigation.clue_phase (parallel) → investigation.resolution |
| `accusation_filed` | investigation → reveal (final) |

`apply_action` calls the named transition method on the chart instance: `getattr(self._chart, action.transition_name)()`. Beat IDs from `nightcap/arc.json` are metadata only; the chart is driven by transition names.

**Session identity.** `HarnessRun` carries `session_id: UUID` directly. Do not use the ORM `Session` from `engine.db.orm` in runner state -- that model requires a live SQLAlchemy session. If tests need to exercise any generation boundary, inject a stub callable rather than wiring up a DB session; follow the `_patch_metadata_for_sqlite` pattern from `engine/tests/test_generation_logging.py` only if ORM access is unavoidable.

---

# In Scope

- Create `engine/harness/` as a new engine-local package
- Add a small run-state model layer such as `engine/harness/models.py`
- Add a runner implementation such as `engine/harness/runner.py`
- Load `nightcap/arc.json` and bind it to the existing `ArcStateChart`
- Instantiate deterministic runner state from:
  - the Nightcap arc definition
  - a `Session`-compatible session record
  - a caller-provided seed
- Expose programmatic runner operations for:
  - session bootstrap
  - session start
  - direct action application
  - current snapshot retrieval
  - immutable trace retrieval
- Record a deterministic trace of beat transitions and harness actions using step indexes, not wall-clock timestamps
- Keep AI boundaries injectable or mockable so the runner can stay offline
- Add focused tests, expected at `engine/tests/test_harness_runner.py`

---

# Out of Scope

- Declarative synthetic-player scenarios or scenario files
- Batch execution, replay diffing, or 10-run harness tooling
- SSE event delivery, FastAPI routes, or browser-facing clients
- Real provider calls or token-spending smoke tests
- Session persistence writes to `arc_beat_states`, `events`, `generation_logs`, or `decision_logs`
- Replacing the current handcrafted `ArcStateChart` with a generated chart

---

# Proposed Shape

The exact names may vary, but the implementation should stay close to this split:

```python
class HarnessAction(BaseModel):
    transition_name: str                          # e.g. "begin_game", "investigation_begins"
    payload: dict[str, Any] = Field(default_factory=dict)


class HarnessTraceEntry(BaseModel):
    step_index: int
    transition_name: str
    from_state: str                               # chart.current_state label before transition
    to_state: str                                 # chart.current_state label after transition
    payload: dict[str, Any] = Field(default_factory=dict)
    # debug_ts excluded from canonical equality path; keep outside HarnessTraceEntry if needed


class HarnessSnapshot(BaseModel):
    step_index: int
    current_state: str
    seed: int
    session_id: UUID


class HarnessRun(BaseModel):
    seed: int
    session_id: UUID
    arc_id: str
    current_state: str
    step_index: int
    trace: list[HarnessTraceEntry]


class HarnessRunner:
    def __init__(self, *, arc_path: Path, seed: int) -> None: ...
    def start(self) -> HarnessRun: ...
    def apply_action(self, action: HarnessAction) -> HarnessTraceEntry: ...
    def snapshot(self) -> HarnessSnapshot: ...
    def trace(self) -> list[HarnessTraceEntry]: ...
```

Notes:

- Use a seeded local RNG such as `random.Random(seed)` and store the seed on the run object.
- `apply_action` calls `getattr(self._chart, action.transition_name)()` on the `ArcStateChart` instance.
- `from_state` and `to_state` in trace entries must be stable string representations of chart state, not `repr()` of the state machine object.
- Do not capture `datetime.now()` anywhere on `HarnessTraceEntry`. If wall-clock timestamps are useful for debugging, add them as a separate field excluded from `canonicalize_trace` in AW-112.

---

# Acceptance Criteria

- [ ] `engine/harness/` exists with a runnable harness core
- [ ] The runner loads `nightcap/arc.json`, instantiates the current `ArcStateChart`, and starts a session without UI
- [ ] The runner can advance the Nightcap scaffold programmatically from `introduction` to `investigation` to `reveal`
- [ ] The runner stores the run seed and exposes it in run state and trace metadata
- [ ] The runner records deterministic trace entries and snapshots suitable for equality assertions
- [ ] The runner introduces no direct provider SDK usage and no provider or model string literals
- [ ] AI boundaries are injectable or mockable so the runner stays offline
- [ ] `pytest engine/tests/test_harness_runner.py -v` passes

---

# Test Plan

- Unit tests: runner initialization from Nightcap arc and seeded session state
- Unit tests: direct action stepping moves across the expected beats
- Unit tests: snapshot output reflects current beat and step index correctly
- Unit tests: repeated runs with the same seed and direct action sequence produce identical canonical traces
- Manual verification: instantiate the runner in a Python REPL and inspect the trace after a three-beat happy-path run

---

# Risks and Unknowns

**Risks**:
- The current `ArcStateChart` is scaffolded by hand and may drift from `nightcap/arc.json`. The runner should treat the current executable chart as authoritative for now and keep the binding narrow.
- If trace records include non-deterministic data such as wall-clock timestamps or unordered dict rendering, seeded equality tests will be flaky.
- Overreaching into session coordination, persistence, or SSE now would duplicate future architecture rather than scaffold it.

**Unknowns**:
- None within AW-110 scope after constraining the task to the current in-process scaffold.

---

# Open Questions

- None within AW-110 scope after the Epic E split.
