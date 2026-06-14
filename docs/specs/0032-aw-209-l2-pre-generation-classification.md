# AW-209 L2 Pre-Generation Classification

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-14

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/10-content-safety.md`, `docs/architecture/06-model-routing.md`, `docs/architecture/11-telemetry.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0014-aw-107-litellm-routing-layer.md`, `docs/specs/0028-aw-208-l1-hard-stops.md`
- PRD sections: `docs/prd/01-overview.md`
- Roadmap task: `docs/roadmap/tasks/AW-209-l2-pre-generation-classification.md`
- GitHub issue: `https://github.com/nickejanssen/arcwright/issues/62`

---

# Overview

This spec defines Layer 2 pre-generation safety classification for the current runtime generation boundary. L2 runs after deterministic L1 hard stops and before every main routed generation call.

---

# In Scope

- Add a small `engine.safety` L2 module for classification prompt construction, result parsing, event payloads, and blocked-call sentinel results.
- Integrate L2 into `engine.routing.logging.generate`.
- Route classification through the existing routing abstraction using task type `safety_classification`.
- Log classification model usage through `generation_logs`.
- Log L2 classification outcomes to `events` with confidence data and no raw prompt or player content.
- Block the main generation call when classification says the prompt is prohibited.
- Preserve AW-208 L1 ordering so L1 blocks before any model call.
- Add tests for ordering, routing abstraction use, blocked behavior, confidence logging, and safe generation.

---

# Out of Scope

- New provider, model, dependency, schema, or migration changes.
- Dashboard safety visibility.
- Post-generation L4 filtering.
- L3 policy injection and generated neutral bridge copy.
- Changing `config/routing_table.json` unless tests reveal the existing `safety_classification` entry is missing.
- Full semantic safety tuning or eval-suite expansion.

---

# Design

`engine.routing.logging.generate` remains the only approved runtime generation entrypoint. The order is:

1. Evaluate L1 hard stops.
2. If L1 blocks, log `safety_hard_stop` and return the existing L1 neutral sentinel.
3. Route an L2 classification call through `route_generation` with task type `safety_classification`.
4. Log the L2 classification call to `generation_logs`.
5. Log an `events` row with `event_type = "safety_classification"` and payload containing `layer`, `blocked`, `confidence`, `category`, and `code`.
6. If L2 blocks, return an L2 neutral sentinel without calling the requested main task.
7. If L2 allows, route and log the requested main generation call normally.

The L2 classifier must not call a provider directly. It must not contain provider or model strings. It must not store raw prompt content, raw player content, or raw classifier output in the event payload.

`generate` accepts optional `safety_policy_context` so future arc runtime code can pass `ArcDefinition.content_rails` or an equivalent serialized policy context. Until the arc coordinator passes that data, the default policy context is the platform and Nightcap safety boundary described in `docs/architecture/10-content-safety.md`.

`task_type = "safety_classification"` skips self-classification to avoid recursive classification if this task is called directly in tests or tooling.

---

# Acceptance Criteria

- [ ] L2 safety classification runs after L1 and before every main generation call made through `engine.routing.logging.generate`.
- [ ] L1 hard stops still prevent all model calls, including L2 classification.
- [ ] L2 classification uses `route_generation` with task type `safety_classification` and never calls a provider directly.
- [ ] Allowed L2 classifications permit the requested main generation call.
- [ ] Blocked L2 classifications prevent the requested main generation call.
- [ ] L2 classification calls are logged to `generation_logs`.
- [ ] L2 classification outcomes are logged to `events` with confidence data and without raw prompt or player content.
- [ ] No provider or model string is added outside `config/routing_table.json` or `engine/routing/router.py`.

---

# Test Plan

- Unit tests: parse classifier JSON output into allowed and blocked decisions.
- Integration tests: `generate` calls L2 before the main route when L1 allows.
- Integration tests: L1 block does not call L2 or the main route.
- Integration tests: blocked L2 writes a safe `safety_classification` event and does not call the main route.
- Integration tests: allowed L2 writes classification usage and then logs the main generation.
- Static test: production generation paths still do not bypass the logging-aware entrypoint.
- Commands:
  - `python -m pytest engine/tests/test_safety_l2.py engine/tests/test_generation_logging.py -q`
  - `python -m ruff check engine/safety engine/routing engine/tests`
  - `python -m ruff format --check engine/safety engine/routing engine/tests`

---

# Risks and Unknowns

**Risks**:
- Classifier output format can vary. The parser treats missing or malformed structured output as blocked so unsafe content does not fall through to the main generation call.
- The current runtime does not yet pass full arc `content_rails` into `generate`. The API is prepared for it, but full coordinator wiring belongs to later arc and character behavior work.

**Unknowns**:
- Specific output shape from the selected safeguard model remains an integration detail behind the routing abstraction.
- Groq safeguard pricing and output rate remain tracked in `docs/product/open-questions-log.csv`.

---

# Open Questions

- None blocking AW-209 implementation.
