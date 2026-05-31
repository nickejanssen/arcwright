# AW-107 LiteLLM Routing Layer

**Status**: Draft

**Author**: Codex | **Date**: 2026-05-31

---

# References

- Architecture sections: `docs/architecture/06-model-routing.md` (§6.1-§6.5), `docs/architecture/15-development-guide.md` (§15.7, §15.9)
- Related specs: `docs/specs/0009-aw-101-repository-structure-and-python-project-setup.md`, `docs/specs/0013-aw-106-pre-generation-knowledge-constraint-hook.md`
- PRD sections: `docs/prd/02-requirements.md` (Principles 6 and 8), `docs/prd/03-scope.md` (MVP done criteria), `docs/prd/04-non-goals.md`
- GitHub issue: `#15 AW-107: LiteLLM routing layer`

---

# Overview

Complete the existing model-routing scaffold so every LiteLLM generation call returns structured metadata needed by downstream telemetry work, without implementing any logging or database writes in this task. The routing layer must stay provider-agnostic, use the config-defined routing table, and handle tier fallbacks in one place.

---

# In Scope

- Add a frozen `RouteResult` dataclass to `engine/routing/router.py`
- Change `route_generation` to return `RouteResult` instead of a bare string
- Measure call latency and extract prompt and completion token counts from the LiteLLM response
- Preserve and verify fallback behavior when the primary routed model call fails
- Cache the routing table at module import time rather than re-reading it on every call
- Export `RouteResult` and `route_generation` from `engine/routing/__init__.py`
- Add offline unit tests in `engine/tests/test_routing.py`
- Verify the existing `config/routing_table.json` contents against architecture §6.3 without regenerating or rewriting the file

---

# Out of Scope

- Writing `generation_logs` rows or any other telemetry persistence
- Logging fallback events or any other data to the `events` table
- Prompt caching implementation
- Direct provider SDK integration such as `anthropic` or `groq`
- Regenerating or modifying `config/routing_table.json`
- Database, ORM, or migration changes

---

# Proposed Interface

```python
@dataclass(frozen=True)
class RouteResult:
    content: str
    model_used: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    used_fallback: bool


async def route_generation(
    task_type: str,
    quality_tier: str,
    messages: list[dict],
    temperature: float = 0.7,
) -> RouteResult:
    ...
```

Notes:

- `model_used` is the routing-table key actually used for the successful call, including the fallback key when fallback fires.
- `used_fallback` is `True` only when the primary call raised and the fallback call succeeded.
- `latency_ms` is measured with `time.perf_counter()` around each LiteLLM completion attempt and converted with `int((end - start) * 1000)`.
- Token counts come from `response.usage.prompt_tokens` and `response.usage.completion_tokens`.

---

# Routing Table Contract

`config/routing_table.json` is the sole source of provider and model strings. For each MVP task type from architecture §6.3, the table must contain:

- `standard`
- `premium`
- `standard_fallback`
- `premium_fallback`

Required task types:

- `character_dialogue`
- `narrative_generation`
- `pacing_decision`
- `knowledge_inference`
- `safety_classification`
- `killer_assignment`
- `narrator_bridge`

Implementation must load this table once at module import and reuse the cached data for lookups.

---

# Acceptance Criteria

- [ ] `route_generation` returns a `RouteResult` with correct `content`, `model_used` matching the routing-table entry, non-zero `input_tokens` and `output_tokens`, positive `latency_ms`, and `used_fallback=False` on a clean call
- [ ] When the primary call raises, `route_generation` retries with the fallback model and returns `RouteResult` with `used_fallback=True` and `model_used` set to the fallback key
- [ ] When the primary raises and no `_fallback` key exists for the tier, the exception propagates with no silent failure
- [ ] `routing_table.json` contains all 7 task types from architecture §6.3, each with all four tier keys
- [ ] `RouteResult` and `route_generation` are importable as `from engine.routing import RouteResult, route_generation`
- [ ] No model name or provider string appears in any file outside `routing_table.json` and `router.py`
- [ ] `make type` and `make lint` pass

---

# Test Plan

- Unit tests: patch `engine.routing.router.litellm.acompletion` with `unittest.mock.AsyncMock`
- Unit tests: verify `route_generation` uses the model key defined in `routing_table["character_dialogue"]["standard"]`
- Unit tests: verify `RouteResult` contains content, token counts, latency, model key, and `used_fallback=False` on a clean call
- Unit tests: verify fallback model is called and `used_fallback=True` when the primary attempt raises
- Unit tests: verify the original exception propagates when no fallback entry exists for the requested tier
- Unit tests: verify `routing_table.json` contains all seven architecture task types and all four tier keys for each
- Unit tests: verify `resolve_model_key("nonexistent", "standard")` raises `KeyError`
- Manual verification: confirm no provider or model strings are introduced outside `config/routing_table.json` and `engine/routing/router.py`

---

# Risks and Unknowns

**Risks**:
- Re-reading the routing table on every lookup would violate the task contract and make the routing layer less predictable under load.
- Returning only a bare string would block downstream telemetry work from capturing model key, latency, and token metadata.
- Accidentally adding logging or persistence here would leak AW-108 scope into this task.

**Unknowns**:
- None within AW-107 scope once the issue body is treated as the authoritative source for the missing spec file.

---

# Open Questions

- None. The issue body is being transcribed into this spec as directed.
