# AW-256: Remove Game-Specific Beat ID Hardcode from Arc Transition Gate

**Status**: Done

**Author**: Agent | **Date**: 2026-06-27

---

# References

- Architecture section: `docs/architecture/03-arc-execution.md` §3.2 (Generic exit-condition evaluation contract)
- GitHub issue: #156
- Epic: M5-C — Second Arc Schema And Executable Follow-Through
- Blocks: AW-245 (Second Arc Minimal Executable Product)
- Depends on: AW-203, AW-204

---

# Overview

Remove two hardcoded beat ID string literals (`"arrival"`) from the Arcwright engine, replacing them with generic derivation from `arc_definition.beats[0].beat_id`. This ensures any arc whose first beat has a different name works correctly without engine code changes.

---

# In Scope

- `engine/harness/runner.py`: remove `_ARRIVAL_BEAT_ID = "arrival"` constant; derive initial beat from arc definition in `_resolve_introduction_setup`.
- `engine/harness/runner.py`: add `arc_definition: ArcDefinition | None` constructor parameter so tests can supply a synthetic arc directly.
- `engine/session/service.py`: remove `_DEFAULT_INITIAL_BEAT_ID = "arrival"` constant; derive initial beat from arc definition in `create_session`.
- `engine/arc/models.py`: add `min_length=1` to `ArcDefinition.beats` field.
- New test: `engine/tests/test_aw256_beat_hardcode.py` with a synthetic arc using `"lobby"` as first beat.
- Architecture doc update: `docs/architecture/03-arc-execution.md`.

---

# Out of Scope

- `_REVEAL_BEAT_ID = "truth"` in `engine/harness/runner.py` — a separate architecture violation tracked as follow-on work.
- Generic arc registry / arc loader (currently `_load_nightcap_arc_definition` is the only loader; generalising it is deferred).
- Modifications to `nightcap/arc.json`.
- `min_players_required` typed exit-condition field on `BeatDefinition` (identified as a possible approach in the issue; not required for this spec's acceptance criteria).

---

# Acceptance Criteria

- [x] `grep -rn '"arrival"' engine/ --include="*.py" | grep -v test | grep -v "#"` returns zero hits.
- [x] The existing arc JSON (`nightcap/arc.json`) is not modified; the minimum-player gate remains encoded as `exit_conditions: ["all_players_ready"]` on the first beat.
- [x] All existing engine tests pass: 377 passed, 1 skipped.
- [x] `engine/tests/test_aw256_beat_hardcode.py` contains at least one test using a synthetic arc whose first beat is not named `"arrival"`, and that test passes.
- [x] `docs/architecture/03-arc-execution.md` documents the generic initial-beat and exit-condition evaluation contract.
- [x] `ArcDefinition.beats` has `min_length=1` to enforce the invariant that `beats[0]` is always accessible.

---

# Test Plan

- Unit: `engine/tests/test_aw256_beat_hardcode.py` — 3 tests with `initial_beat_id="lobby"`.
- Regression: full `pytest engine/tests/ -q` suite; no regressions from `test_session_lifecycle.py`, `test_harness_runner.py`, `test_harness_batch.py`, `test_harness_scenarios.py`, `test_m2_exit_harness.py`.
- Lint: `python -m ruff check engine api && python -m ruff format --check engine api`.
