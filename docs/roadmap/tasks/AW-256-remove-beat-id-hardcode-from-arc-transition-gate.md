---
id: productroadmap.roadmap.tasks.aw-256-remove-beat-id-hardcode-from-arc-transition-gate
namespace: product-roadmap
title: "AW-256: Remove Game-Specific Beat ID Hardcode from Arc Transition Gate"
owner: Nico Janssen
status: active
review_by: "2027-01-13"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# AW-256: Remove Game-Specific Beat ID Hardcode from Arc Transition Gate

**Milestone / Epic:** M5 / M5-C
**Size:** S
**Scope note:** Delivered by GitHub issue #156 and `docs/specs/0062-aw-256-remove-beat-id-hardcode.md`. This task file was missing from the repository; created from that spec to restore the roadmap index's task-file link.

## Plain-English Summary

Remove two hardcoded beat ID string literals (`"arrival"`) from the Arcwright engine, replacing them with generic derivation from `arc_definition.beats[0].beat_id`, so any arc whose first beat has a different name works without engine code changes.

## Why This Matters

Game-agnosticism is a non-negotiable platform principle. A hardcoded beat ID in the engine layer ties the arc-transition gate to Nightcap's specific arc shape and blocks any second arc (Daily Case, Monster RPG) whose first beat is not literally named `"arrival"`.

## Player Impact

No direct player-facing change; this removes an engine-layer blocker to shipping non-Nightcap arcs.

## Business Value

Unblocks AW-245 (Second Arc Minimal Executable Product) and the platform's second-game validation path described in `docs/architecture/14-architecture-validation.md`.

## Technical Scope

- `engine/harness/runner.py`: remove `_ARRIVAL_BEAT_ID = "arrival"` constant; derive initial beat from arc definition in `_resolve_introduction_setup`.
- `engine/harness/runner.py`: add `arc_definition: ArcDefinition | None` constructor parameter so tests can supply a synthetic arc directly.
- `engine/session/service.py`: remove `_DEFAULT_INITIAL_BEAT_ID = "arrival"` constant; derive initial beat from arc definition in `create_session`.
- `engine/arc/models.py`: add `min_length=1` to `ArcDefinition.beats` field.

Full scope, out-of-scope boundary, and acceptance criteria: `docs/specs/0062-aw-256-remove-beat-id-hardcode.md`.

## Human Collaboration Contract

**Interaction profile:** Independent execution. No founder taste, private knowledge, or live judgment required; the fix is a mechanical constant-to-derivation change with a clear acceptance test.

## Acceptance Criteria

- [x] `grep -rn '"arrival"' engine/ --include="*.py" | grep -v test | grep -v "#"` returns zero hits.
- [x] `engine/tests/test_aw256_beat_hardcode.py` exists and passes with a synthetic arc using `"lobby"` as its first beat.
- [x] `docs/architecture/03-arc-execution.md` documents the generic derivation.

## Tests/Verification

`engine/tests/test_aw256_beat_hardcode.py`, per the spec's acceptance criteria.

## Dependencies

- AW-203
- AW-204

## Likely Files Affected

engine/harness/runner.py, engine/session/service.py, engine/arc/models.py

## Must Not Do

- Do not implement product code outside this task scope.
- Do not modify `nightcap/arc.json`.
- Do not hardcode secrets or API keys.

## Architecture References

- `docs/architecture/03-arc-execution.md` §3.2 (Generic exit-condition evaluation contract)
- `docs/specs/0062-aw-256-remove-beat-id-hardcode.md`

## Playtest Relevance

Blocks AW-245 (Second Arc Minimal Executable Product); protects the M5-C exit gate for platform game-agnosticism.
