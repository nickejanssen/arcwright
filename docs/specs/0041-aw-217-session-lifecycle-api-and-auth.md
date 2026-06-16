---
spec_id: "0041"
title: "AW-217: Session Lifecycle API And Auth"
issue: 70
milestone: M3
epic: M3-B
status: in-progress
created: 2026-06-15
author: claude-code
---

# AW-217: Session Lifecycle API And Auth

## Context

AW-216 landed the SSE fanout layer (`engine/events/fanout.py`, `api/routers/events.py`).
The events endpoint stubs identity: `player_id` and `connection_type` are trusted as raw
query parameters. This spec adds the session lifecycle REST endpoints and the Firebase Auth
middleware that replaces that stub.

## Architecture References

- `docs/architecture/09-developer-api.md` §9.2 — endpoint catalog and auth tiers
- `AGENTS.md` — hard rules (no arc logic in handlers; secrets/auth requires approval)

## Scope

### In scope

- `engine/session/service.py` — `SessionService`: in-memory lifecycle state for single-process MVP
- `api/auth/__init__.py` — `require_api_key`, `require_host_jwt`, `require_api_key_or_host_jwt`
- `api/schemas/__init__.py` — `CreateSessionRequest/Response`, `SessionStateResponse`,
  `JoinSessionResponse`
- `api/routers/sessions.py` — thin handlers for the seven lifecycle endpoints (§9.2)
- `api/routers/events.py` — replace query-param trust with JWT-extracted identity

### Out of scope

- ORM/Postgres persistence (in-memory store only; persistence is a later M3 task)
- Character assignment, knowledge state, arc execution (separate tasks)
- Character management, knowledge state, usage endpoints (§9.2 rows 2–3 and 5–6)
- Firebase credential loading code (ADC / env-var pattern only; no service-account JSON in code)

## Acceptance Criteria

- [ ] AC1: Endpoints `POST /sessions`, `POST /sessions/{id}/start`, `GET /sessions/{id}`,
      `POST /sessions/{id}/pause`, `POST /sessions/{id}/resume`, `POST /sessions/{id}/end`,
      `GET /sessions/{id}/join` exist with documented request and response schemas.
- [ ] AC2: Route handlers validate input, call engine service functions, and return responses;
      no arc execution logic appears in any handler.
- [ ] AC3: `POST /sessions` is gated by `X-Api-Key`; `start/pause/resume/end` are gated by
      host JWT (Firebase custom token exchanged for an ID token); `GET /sessions/{id}` accepts
      API key or host JWT; `GET /sessions/{id}/join` is unauthenticated.
- [ ] AC4: `GET /sessions/{id}/events` (AW-216 SSE endpoint) extracts `player_id` and role from
      JWT claims; the `player_id`/`connection_type` query-param trust model is removed.
- [ ] AC5: `SessionService` unit tests cover the full lifecycle state machine and join-token
      validation.

## Token Flow

```
Developer (API key)
  → POST /v1/sessions                          returns session_id, join_url, host_token
  → distribute join_url + per-player tokens out of band

Host (host_token = Firebase custom token)
  → exchanges host_token for Firebase ID token via Firebase client SDK
  → POST /v1/sessions/{id}/start              Authorization: Bearer <id_token>

Player (per-player join token)
  → GET /v1/sessions/{id}/join?token=<token>  returns player_token (Firebase custom token)
  → exchanges player_token for Firebase ID token
  → GET /v1/sessions/{id}/events              Authorization: Bearer <id_token>
```

Custom token claims:
- Host:   `{ arcwright_role: "host",   arcwright_session_id: "<uuid>" }`
- Player: `{ arcwright_role: "player", arcwright_session_id: "<uuid>", arcwright_player_id: "<uuid>" }`
- Display: `{ arcwright_role: "display", arcwright_session_id: "<uuid>", arcwright_player_id: "<uuid>" }`

## Playtest Gate

Unlocks M3 gate: first live Nightcap session can be created, started, and ended via the API.
