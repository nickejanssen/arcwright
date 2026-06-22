# AW-255: REST-Backed Nightcap Session Loop

**Milestone / Epic:** M3 / M3-D
**Size:** L
**Depends on:** AW-218, AW-220, AW-222, AW-224

## Plain-English Summary

Move the remaining Nightcap proof work out of the test-only harness and into the live REST session path. The production input flow must advance beat state, emit the required telemetry, and collect replay intent without relying on a detached `HarnessRunner` to force the story to the reveal.

## Why This Matters

M3 only closes when a real session path proves the API can carry Nightcap from start to finish. The current harness and telemetry work do not yet prove that the REST surface itself advances beats or records live-session telemetry, so this follow-up keeps that debt visible and scheduled.

## Technical Scope

- Advance Nightcap beat state from the live REST session flow, not from a test-only harness.
- Persist the new beat position and write `beat_transition` from the production path.
- Emit live-session `tension_update`, `pacing_intervention`, and `pacing_intervention_outcome` rows when the pacing engine triggers them.
- Add the host-facing replay-intent endpoint backed by `SessionService.write_replay_intent()`.
- Replace the detached `HarnessRunner` beat forcing in the batch harness with the same REST-backed path used by live sessions.

## Acceptance Criteria

- [ ] The Nightcap REST input flow advances persisted beat state through production code, and `sessions.current_beat_id` reflects the new beat after the flow runs.
- [ ] The live progression path writes `beat_transition` rows without using `engine.harness.HarnessRunner` to move the chart.
- [ ] When the live pacing path triggers, it writes `tension_update`, `pacing_intervention`, and `pacing_intervention_outcome` rows from the same live session flow.
- [ ] `POST /v1/sessions/{session_id}/replay-intent` writes a `replay_intent` row via `SessionService.write_replay_intent()` and stays separate from `end_session()`.
- [ ] `api/tests/test_batch_harness.py` runs 10 seeded Nightcap sessions through the same REST-backed progression path used by live sessions, records seed and pass/fail status, and no longer depends on a detached `HarnessRunner` to force the truth beat.
- [ ] The batch harness still uses mocked generation and consumes no real provider tokens.
- [ ] `host_bypass` remains local test metadata only and is not added to the API schema.

## Tests/Verification

- Add or update API integration tests that drive the live Nightcap flow through the REST input path and verify persisted beat advancement and telemetry writes.
- Add a replay-intent endpoint test that verifies the `replay_intent` Event row is written through the dedicated API path.
- Update the batch harness test so it no longer advances Nightcap through direct harness-only beat forcing.

## Must Not Do

- Do not reintroduce provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.
- Do not put arc execution logic in FastAPI route handlers.
- Do not widen the API schema with `host_bypass` or other test-only controls.

## Architecture References

- `docs/architecture/09-developer-api.md`
- `docs/architecture/11-telemetry.md`
- `docs/architecture/12-build-plan.md`
- `docs/architecture/15-development-guide.md`

