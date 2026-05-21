# Chat-6-Claude-Code-Handoff

**Version:** 1.0

**Date:** May 11, 2026

**Purpose:** Dense reference card for Claude Code. Under 1,000 words. No prose padding. Everything needed to start building without asking the founder to explain decisions.

---

## Identity

You are building Arcwright: a narrative runtime middleware platform. Layer 2 between foundation models (Anthropic, Groq) and experience clients (Nightcap game, future arcs). Your first deliverable is a working Nightcap session: 4-10 players, murder mystery, three beats, one reveal.

---

## First File

`engine/session/models.py` — Session, SessionParticipant, ArcDefinition Pydantic models. Everything depends on this. Write it first.

---

## Tech Stack (locked, do not re-litigate)

| Concern | Choice |
| --- | --- |
| Language | Python 3.11+ (engine, API), TypeScript 5.x (SDK, dashboard) |
| API framework | FastAPI 0.111+ |
| Database | Cloud SQL PostgreSQL 15 + pgvector |
| ORM | SQLAlchemy 2.0 async + asyncpg |
| Migrations | Alembic |
| Arc execution | python-statemachine 3.0+ (use `StateChart`, not `StateMachine`) |
| AI routing | LiteLLM 1.30+ in-process |
| Auth | Firebase Auth (dashboard/host) + API keys (devs) + session JWTs (players) |
| Cloud | GCP: Cloud Run + Cloud SQL + Firebase Auth |

---

## Hard Rules

1. No model name or provider string anywhere outside `config/routing_table.json` and `engine/routing/router.py`. Violation = bug.
2. No AI character response generated without first calling `get_character_knowledge(session_id, character_id)`. Non-negotiable.
3. No arc execution logic in FastAPI route handlers. Routes validate input, call engine, return response.
4. No session runs without telemetry active. Sessions without telemetry are cost with no data return.
5. Knowledge state management is not optional. No arc on this platform produces incoherent knowledge state.
6. Safety pipeline (L1 + L2 + L3) is always active. No generation happens without all three layers.
7. No surface type (TV, phone, browser) in any engine code. Engine emits `ContentEvent` objects only.

---

## Key Schemas

```python
# Routing call (the only way to call AI)
response = await router.generate(
    task_type="character_dialogue",  # or: narrative_generation | pacing_decision | safety_classification | knowledge_inference | killer_assignment | narrator_bridge
    quality_tier="standard",         # or: "premium" (set by dramatic_tension_score >= 0.85)
    messages=[...],
    temperature=0.7
)

# Knowledge assertion
await assert_knowledge(
    session_id, character_id,
    fact_type="clue",
    fact_content={...},
    source_character_id=None,
    provenance_chain=[source_id, ...],  # append-only chain of character IDs
    confidence=1.0
)

# Content event emission
ContentEvent(
    session_id=..., event_type=...,
    target_audience=AudienceTarget.SPECIFIC_PLAYER,
    target_player_id=...,
    payload={...},
    presentation_hints=PresentationHints(emotion="tense", urgency="high")
)
```

---

## Database: 16 Tables, This Order

1. Enable pgvector
2. accounts
3. consent_records
4. characters (behavior_profile JSONB, embedding VECTOR(1536) NULL)
5. facts (embedding VECTOR(1536) NULL)
6. knowledge_states (provenance_chain JSONB)
7. relationships
8. locations
9. objects
10. decisions
11. events (append-only, embedding VECTOR(1536) NULL)
12. sessions
13. session_participants
14. arc_beat_states
15. generation_logs (prompt_text NULL, output_text NULL — populated only when CONTENT_LOGGING_ENABLED=true)
16. decision_logs

---

## Build Order (dependencies drive sequence)

1. DB schema + Pydantic models
2. Knowledge graph (assert / revoke / query) + unit tests
3. Model routing + safety pipeline (L1/L2/L3) + unit tests
4. Arc execution engine (StateChart + pacing + coordinator loop)
5. Character behavior engine (7-step pipeline)
6. Event system + SSE fan-out + FastAPI endpoints
7. Session persistence (interrupt/resume)
8. Telemetry wiring + simulation harness

Do not start step N+1 until step N has passing unit tests.

---

## Routing Table (config/routing_table.json)

```json
{
  "character_dialogue":    {"standard": "anthropic/claude-haiku-4-5-20251001", "premium": "anthropic/claude-sonnet-4-6"},
  "narrative_generation":  {"standard": "anthropic/claude-haiku-4-5-20251001", "premium": "anthropic/claude-sonnet-4-6"},
  "pacing_decision":       {"standard": "groq/llama-3.1-8b-instant"},
  "safety_classification": {"standard": "groq/gpt-oss-safeguard-20b"},
  "knowledge_inference":   {"standard": "groq/llama-3.1-8b-instant", "premium": "groq/llama-3.3-70b-versatile"},
  "killer_assignment":     {"standard": "groq/llama-3.1-8b-instant"},
  "narrator_bridge":       {"standard": "anthropic/claude-haiku-4-5-20251001"}
}
```

---

## MVP Done (all must be true)

- Nightcap playable end-to-end by real group (4-10 players, not founder's circle)
- All three beats complete through to reveal
- Knowledge state enforcement: no player receives information they should not have
- Session persistence: interruption restores from nearest beat
- Provider-agnostic routing: no model name outside routing_table.json
- Five telemetry signals live from first session
- Per-session cost calculable from generation_logs
- Safety rails active
- One non-Nightcap arc schema designed (proves format is general)

---

## Architecture Document

Full 15-section architecture: [07-Technical-Architecture-v1](07-Technical-Architecture-v1%203%2035db7de354a881618e59e65c8e12caf6.md)

When a decision here conflicts with that document, the architecture document wins. When something is not in this handoff, the architecture document has the answer.