# AW-252: Mini-game API, Events, And TypeScript SDK

**Status**: Draft

**Author**: Codex | **Date**: 2026-06-20

---

# References

- Related ADRs: `docs/decisions/0008-content-event-type-layering.md`, `docs/decisions/0009-mini-game-runtime-boundary.md`
- Related specs: `docs/specs/0048-aw-251-mini-game-runtime-persistence-and-clue-gating.md`
- Architecture: `docs/architecture/08-event-system.md`, `docs/architecture/09-developer-api.md`
- GitHub issue: #146

---

# Overview

Expose mini-game state and player actions through thin FastAPI endpoints,
game-owned ContentEvent types, and typed SDK methods.

---

# In Scope

- `GET /v1/sessions/{session_id}/mini-games/active`
- `POST /v1/sessions/{session_id}/mini-games/{run_id}/submissions`
- Host command endpoint for approved cancel, resolve, or fallback actions
- Typed event payloads for availability, start, progress, completion, timeout,
  and clue-unlock acknowledgement
- SDK state fetch and idempotent submission methods

---

# Out Of Scope

- Runtime decisions in route handlers or TypeScript
- Browser rendering or Cloudflare room coordination

---

# Acceptance Criteria

- [ ] Handlers authenticate, validate, call engine services, and return typed
  responses without arc logic.
- [ ] Submissions are scoped to the authorized participant and run.
- [ ] Events preserve `target_audience` privacy and use open game-owned event
  types under existing platform categories.
- [ ] Reconnect recovers authorized active state without exposing private data.
- [ ] Public SDK types contain no `any` and no deterministic game logic.

---

# Test Plan

- API authorization, idempotency, privacy, and error tests
- ContentEvent fanout and reconnect tests
- SDK typecheck, build, and mocked transport tests

---

# Risks and Unknowns

**Risks**: Broad payloads can weaken type safety, so every event type requires a
versioned payload interface.

**Unknowns**: Host-client SDK shape may remain Nightcap-specific for M4.

---

# Open Questions

- None for the transport boundary.
