# 0071: AI Character Dialogue in the Live Session Loop

**Status**: Approved (founder decision D-072, July 14, 2026)

**Author**: Founder + Claude | **Date**: 2026-07-14

---

# References

- Product decision: D-072 in `docs/product/decisions-log.csv`
- Architecture: `docs/architecture/06-character-behavior.md`, `docs/architecture/08-event-system.md`, `docs/architecture/10-content-safety.md`
- Prior specs: 0036 (AI initiative and NPC-NPC exchange), 0064 (authorial intent), spec-time findings: before this spec, `generate_character_dialogue` was exercised only by tests and the harness; no production path created an AI-controlled participant.

---

# Overview

Wires the existing knowledge-constrained character dialogue stack into the live REST session loop for Rehearsal 1. Two capabilities: hosts seat AI-controlled characters into a session, and a player dialogue input triggers at most one AI character response, delivered on the session event bus.

Deterministic-first ordering is preserved: `submit_input` records the input and advances arc state deterministically exactly as today; only then is generation invoked, composing from resolved state.

---

# In Scope

1. **Seat an AI character.** `SessionService.add_ai_character(db, session_id, behavior_profile=None)` creates a `Character` (with optional behavior profile) and a `SessionParticipant` with `is_ai_controlled=True`, `surface_type="ai"`. AI seats respect session capacity but do not increment `player_count` (that metric tracks supported human players per M5-B). Route: `POST /v1/sessions/{session_id}/characters/ai` (host JWT).

2. **AI response on dialogue input.** `CharacterService.generate_ai_responses(db, session_id, speaking_character_id, content)`:
   - No-op (returns `[]`, zero generation calls) unless the session is active, the arc is registered, and at least one AI-controlled participant exists other than the speaker.
   - Selects exactly one responder via `select_initiative_target` (deterministic).
   - Generates via `generate_character_dialogue` with the session's quality tier, current beat id, the arc's `content_rails`, and `authorial_intent`. Knowledge-state query runs inside (mandatory chokepoint, unchanged).
   - Safety-blocked results return the existing neutral-bridge event (`dialogue_blocked`), which is published like any other event so the experience is preserved (§10.2).
   - `KnowledgeConstraintViolation` → no event published; the violation stays engine-internal.
   - Cost guard: at most one generation call per player dialogue input; `kind=action` inputs trigger none.

3. **Publication.** The input route converts returned `CharacterDialogueEvent`s to `ContentEvent`s (`category=character_dialogue`, `actor_id=character_id`, payload carries `text` and `character_id`) and publishes them on the session bus, mirroring the resume/narrator-bridge pattern. Route handlers stay thin: validate, call engine, publish, respond.

---

# Out of Scope

- NPC-NPC exchanges in the live loop (spec 0036 machinery exists; wiring deferred until a rehearsal shows the need).
- AI takeover of a disconnected human player's character (issue #138).
- Streaming/token-level delivery; responses arrive as complete events.
- Retry-on-knowledge-violation policies.

---

# Acceptance Criteria

- [ ] Host can seat an AI character; the participant is `is_ai_controlled=True` and `player_count` is unchanged.
- [ ] A player dialogue input in a session with an AI participant produces exactly one `character_dialogue` ContentEvent on the bus, generated through `generate()` (L1→L2→L3) with the arc's rails and intent.
- [ ] Sessions with no AI participants, and `kind=action` inputs, make zero generation calls.
- [ ] Safety-blocked generation publishes the neutral-bridge event; knowledge violations publish nothing.
- [ ] Unit tests cover seating, response generation, the no-op guards, blocked and violation paths, and event conversion.

---

# Test Plan

- Engine tests with mocked `litellm.acompletion` (existing pattern): response generation end-to-end, guards, blocked path, violation path.
- API test: seat AI character route (auth, capacity, player_count unchanged).

---

# Risks and Unknowns

- **Latency**: one generation call on the input path adds response latency; acceptable for Rehearsal 1 (single response, standard tier). If it drags the room, move to background publish.
- **Cost**: bounded at one call per dialogue input; sessions without AI seats cost nothing extra.
