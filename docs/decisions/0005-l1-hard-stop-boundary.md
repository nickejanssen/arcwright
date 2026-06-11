# 0005 - L1 Hard Stop Boundary

**Date:** 2026-06-10
**Status:** Accepted
**Architecture reference:** `docs/architecture/10-content-safety.md`, `docs/architecture/15-development-guide.md`
**Spec reference:** `docs/specs/0028-aw-208-l1-hard-stops.md`
**Scope:** AW-208 deterministic L1 safety boundary and blocked-generation return contract

---

# Context

AW-208 adds deterministic Layer 1 safety hard stops before generation. `docs/architecture/10-content-safety.md` requires L1 to run before any model call, block unconditionally, log `safety_hard_stop`, and continue the session with a neutral narrator bridge.

The current implemented generation boundary is `engine.routing.logging.generate`. It owns model routing invocation, generation cost logging, fallback telemetry, and database access. The lower-level `engine.routing.router.route_generation` does not receive a database session and cannot log a `safety_hard_stop` event by itself.

The future session coordinator will eventually own richer bridge emission, actor attribution, and event flow. AW-208 needs a safe MVP contract that works before that coordinator path exists.

Alternatives considered:

- Raise a typed `SafetyHardStopError` and require callers to handle it. Rejected for AW-208 because current callers do not have a coordinator-owned safety bridge path yet, and an uncaught exception would turn unsafe input into a session failure.
- Put L1 in `route_generation`. Rejected because the low-level router lacks database access for `safety_hard_stop` logging and would mix routing with telemetry persistence.
- Return a neutral `RouteResult` sentinel from `generate`. Accepted because it preserves the current generation contract, avoids model calls, logs the hard stop, and keeps the session flowing.

Constraints:

- L1 cannot be disabled by arc configuration.
- L1 must not call an LLM or route through safety classification.
- L1 must not expose trigger details to players or logs.
- Production runtime code must not bypass `generate` by calling `route_generation` directly.

---

# Decision

We enforce AW-208 L1 hard stops at `engine.routing.logging.generate`.

When L1 blocks content:

1. `generate` logs `event_type = "safety_hard_stop"` with safe category/code metadata only.
2. `generate` flushes the database session.
3. `generate` does not call `route_generation`.
4. `generate` does not write a `generation_logs` row.
5. `generate` returns a neutral `RouteResult` sentinel with:
   - `content = "The narrator redirects the moment back to the story."`
   - `model_used = "l1_hard_stop"`
   - `input_tokens = 0`
   - `output_tokens = 0`
   - `latency_ms = 0`
   - `used_fallback = False`

`l1_hard_stop` is a non-provider sentinel, not a model identifier. It must never be written to `generation_logs`, cost calculation, or routing telemetry.

AW-208 also adds a static test that fails if production code outside the approved routing allowlist calls `route_generation` directly.

---

# Consequences

## Positive consequences

- Unsafe L1 content is blocked before any model call.
- Existing generation callers receive a normal-shaped result and do not crash.
- The player experience gets a neutral bridge instead of a revealing safety error.
- Safety telemetry is written at the same boundary that owns database access.
- The static test protects future runtime code from bypassing L1.

## Negative consequences

- The neutral bridge is generic until the session coordinator owns richer bridge emission.
- Callers must understand that `model_used = "l1_hard_stop"` is a sentinel, not a routed model.
- Future production wrappers around `route_generation` must update the static allowlist intentionally.

## Trade-offs

- We gain safe MVP behavior and minimal integration blast radius.
- We defer typed coordinator-level safety control flow until the coordinator exists.

---

# References

- `docs/architecture/10-content-safety.md`
- `docs/architecture/15-development-guide.md`
- `docs/specs/0028-aw-208-l1-hard-stops.md`
- `docs/roadmap/tasks/AW-208-l1-hard-stops.md`
