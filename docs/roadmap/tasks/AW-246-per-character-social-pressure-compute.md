# AW-246: Per-Character Social Pressure Compute

**Milestone / Epic:** M5 / M5-E
**Size:** M
**Status:** Complete

## Plain-English Summary

Add a per-character `social_pressure` score, distinct from session-level `dramatic_tension_score`, and wire it into initiative threshold modulation and `crumble_threshold` so tells intensify under stress.

## Why This Matters

`docs/architecture/07-character-behavior.md S7.4` defines `social_pressure` as a per-character, weighted-sum compute over recent accusations, directed questions, gaze signals, and alliance isolation. AW-213 shipped initiative using session-level `dramatic_tension_score` as a forward-compatible proxy. This task delivers the actual §7.4 compute and wires it into both initiative scheduling and tell expression. Without it, the killer never becomes more themselves under suspicion — the moment §7.4 says is the sign of a session that worked.

## Player Impact

When suspicion piles on the killer, behavior should shift: more over-precise answers, more aggressive deflection, small errors consistent with `under_pressure_style`. Players paying attention notice. Players not paying attention miss it. This task makes that dynamic real.

## Business Value

Closes a v1 architecture commitment. Hardens the killer experience for M6 qualifying sessions where the personalization-perception proof signal depends on differentiated character behavior under stress.

## Technical Scope

- Add `compute_social_pressure(character_id, session_state)` returning a float in 0.0-1.0 in `engine/characters/` (or alongside pacing if cleaner).
- Inputs follow §7.4: weighted sum of recent accusations, directed questions at this character, and alliance isolation. Gaze-signal input may be stubbed as a zero-weighted slot at v1 since no surface sends it yet.
- Wire `social_pressure` into the `InitiativeScheduler` threshold (currently uses session tension via `tension_score` only): scheduler accepts a per-character social-pressure map.
- Wire `social_pressure` into prompt assembly so the speaker's prompt includes a pressure modulation block when `social_pressure >= crumble_threshold` from `behavior_profile`.
- No new routing-table entries, no new model strings, no schema changes.

## Acceptance Criteria

- [ ] `compute_social_pressure` returns a float 0.0-1.0 as a weighted sum aligned with §7.4 inputs.
- [ ] Initiative scheduling accepts per-character social-pressure input and modulates effective threshold accordingly.
- [ ] Generation prompt assembly includes an explicit pressure block when `social_pressure >= crumble_threshold`.
- [ ] Tests prove pressure crossing `crumble_threshold` changes the assembled prompt; sub-threshold pressure leaves the prompt unchanged.
- [ ] No regression on AW-213 tests; same `dramatic_tension_score` behavior preserved for callers that do not pass per-character pressure.

## Tests/Verification

- Unit tests cover the weighted-sum compute with deterministic inputs.
- Unit tests cover scheduler behavior with and without per-character pressure overrides.
- Unit tests cover prompt assembly above and below `crumble_threshold`.
- Run `python -m pytest engine/tests/test_social_pressure.py -q` (file name indicative; final path at implementation time).

## Dependencies

- AW-211 (`behavior_profile` including `crumble_threshold`)
- AW-213 (`InitiativeScheduler` to modulate)
- AW-207 (`DramaticTensionScore` pattern to mirror)

## Likely Files Affected

engine/characters, engine/arc, engine/tests

## Must Not Do

- Do not collapse `social_pressure` into `dramatic_tension_score`. §7.4 treats them as distinct on purpose.
- Do not change `crumble_threshold` semantics or the `behavior_profile` schema.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.
- Do not implement gaze-signal collection at v1; the input slot exists but stays zero-weighted until a surface emits it.

## Architecture References

- docs/architecture/07-character-behavior.md S7.4
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task hardens the killer-under-suspicion dynamic that the M6 personalization-perception proof signal depends on. State at completion which readiness gate it unlocks.
