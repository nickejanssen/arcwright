# AW-224: Full API Batch Harness

> Current version: v0.1
> Last updated: 2026-06-21
> Status: Draft
> Canonical path: docs/specs/0053-aw-224-full-api-batch-harness.md

**Author**: Codex

---

# References

- Architecture: `docs/architecture/09-developer-api.md` §9.2
- Architecture: `docs/architecture/11-telemetry.md` §11.3
- Architecture: `docs/architecture/12-build-plan.md` §12.4
- Architecture: `docs/architecture/15-development-guide.md` §15.7 and §15.9
- Existing harness: `engine/harness/runner.py`
- Existing logging entrypoint: `engine/routing/logging.py`
- API test pattern: `api/tests/test_sessions_api.py`
- Session routes: `api/routers/sessions.py`
- Nightcap arc: `nightcap/arc.json`
- Related spec: `docs/specs/0052-aw-223-cost-and-usage-summary.md`
- GitHub issue: #77

---

# Overview

AW-224 defines the API-level batch harness that runs 10 seeded complete Nightcap sessions through the HTTP layer, not through direct engine calls. This task completes M3-D and satisfies the simulation harness gate in `docs/architecture/12-build-plan.md` §12.4 because simulation harness scripting and telemetry schema design are both complete.

---

# In Scope

- Add `api/tests/test_batch_harness.py` as the primary test file.
- Use `TestClient` plus `dependency_overrides` in the same pattern as `api/tests/test_sessions_api.py`.
- Run 10 parameterized cases with `seed` values `0` through `9`.
- Seed the run with `random.seed(seed)` before each session case.
- Mock `engine.routing.logging.generate` with `AsyncMock`.
- Return a fixed RouteResult-like object from the mock with:
  - `content="[mocked]"`
  - `cost_usd=Decimal("0.001")`
  - `input_tokens=100`
  - `output_tokens=50`
  - `model_used="test-model"`
  - `quality_tier="standard"`
- Verify the Nightcap arc at `nightcap/arc.json` is the arc under test.
- Use the existing session lifecycle API only.
- No new database schema, no new migration, and no new production endpoint.

## Complete Session Flow

Each parameterized case must run this exact flow:

1. `POST /v1/sessions` to create a Nightcap session.
2. `POST /v1/sessions/{id}/start`.
3. `POST /v1/sessions/{id}/characters/{cid}/input` using the standard player-input API body. The harness carries the `host_bypass` sentinel locally as test metadata and does not widen the API request schema.
4. `POST /v1/sessions/{id}/end` with `completion_type="full_arc"` and `killer_identified=True`.
5. Assert every HTTP response is `2xx`.
6. Query `events` for `session_completed`.
7. Query `generation_logs` for at least one row for that session.

## Output Format

- The record for each run is the built-in pytest case result for seeds `0` through `9`.
- No separate JSON artifact.
- No new database table.
- Telemetry presence is asserted inside each test case, not emitted as a separate log file.

---

# Out of Scope

- New API routes or route renames.
- Direct engine harness execution without HTTP.
- New telemetry schema work.
- New persistence tables or migrations.
- Changes to `CONTENT_LOGGING_ENABLED` behavior.
- Any provider or model string outside `config/routing_table.json` and `engine/routing/router.py`.

---

# Acceptance Criteria

- [ ] **AC1**: `api/tests/test_batch_harness.py` parameterizes seeds `0` through `9` and each case executes the complete Nightcap session flow through the HTTP API.
- [ ] **AC2**: Each case records pass/fail through pytest output and asserts telemetry presence by checking for a `session_completed` event plus at least one `generation_logs` row for the session.
- [ ] **AC3**: The harness mocks `engine.routing.logging.generate` with `AsyncMock`, uses deterministic fixture values, and consumes no real provider tokens.

---

# Test Plan

File: `api/tests/test_batch_harness.py`

- Follow the `TestClient` and `dependency_overrides` pattern from `api/tests/test_sessions_api.py`.
- Create the session, start it, send the truth-transition input, and end it in one parameterized test.
- Use `random.seed(seed)` at the start of each case.
- Assert `2xx` on every HTTP call.
- Assert the session has a `session_completed` row in `events`.
- Assert the session has at least one `generation_logs` row.
- Keep the mock target pinned to `engine.routing.logging.generate` only.

---

# Risks and Unknowns

**Risks**

- The API input route currently accepts standard player input only, so the test fixture must carry the `host_bypass` sentinel without expanding the route contract or relying on request parsing.
- SQLite stores `Numeric(10,6)` as float, so any `cost_usd` assertion must use approximate comparison.
- A bad mock target could bypass the safety and logging path, which would defeat the point of the harness.

**Unknowns**

- Whether the batch harness will stay as a pure test file or grow a reusable helper after implementation.

---

# Open Questions

None. The task contract, route catalog, and telemetry requirement are concrete enough to implement directly.
