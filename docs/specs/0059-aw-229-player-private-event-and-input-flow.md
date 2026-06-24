# AW-229: Player Private Event And Input Flow

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-23

---

# References

- Related ADRs: `docs/decisions/0003-nightcap-web-experience-runtime.md`
- Architecture sections: `docs/architecture/08-event-system.md` §8.1, §8.4, §8.6, `docs/architecture/09-developer-api.md` §9.2, §9.4, `docs/architecture/15-development-guide.md` §15.6, §15.9
- Related specs: `docs/specs/0058-aw-228-player-join-flow-under-30-seconds.md`, `docs/specs/0060-aw-230-real-device-privacy-matrix.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap tasks: `docs/roadmap/tasks/AW-229-player-private-event-and-input-flow.md`

---

# Overview

Extend the Cloudflare-hosted Nightcap player surface so private `specific_player` events render only on the intended player device, player input submits through the typed SDK/API path, and reconnect restores the private player session without leaking clue or host content to other participants.

---

# In Scope

- `nightcap-web/src/ui.ts`
  - Private player surface rendering for private events
  - Player input submission from the browser surface
  - Reconnect-safe player session persistence
  - Self-contained inline event helpers for serialized browser scripts
  - Join-token exchange before bearer-authenticated API calls
- `nightcap-web/src/worker.ts`
  - Player event and character proxy routes
  - Player input proxy route
  - Player join-token exchange proxy route
- `nightcap-web/src/runtime.ts`
  - Player session state normalization for reconnect
- `nightcap-web/tests/*.ts`
  - Coverage for private event helper output, player input path, token exchange, and reconnect behavior

---

# Out of Scope

- Arc execution logic in TypeScript
- Host session lifecycle or shared-display rendering changes beyond what this player flow requires
- Any second filtering authority for `ContentEvent.target_audience`
- App installs, Firebase account creation, or hardcoded Firebase API keys
- New dependencies, model strings, or provider strings

---

# Acceptance Criteria

- [ ] Specific-player events render only on the intended player device.
- [ ] Player input is submitted through the existing typed SDK/API path after the player session has been exchanged into a bearer token.
- [ ] The browser never persists the join custom token as the authenticated session token.
- [ ] Private event handling survives reconnect without leaking payloads to other devices.
- [ ] Serialized event helpers used by the browser script are self-contained and do not reference module-local helpers that are absent from the page script.
- [ ] Tests cover helper output, token exchange, and reconnect privacy with the smallest useful automated coverage.

---

# Test Plan

- Unit tests: helper output for private event bodies and labels, worker-side token exchange, and browser-surface rendering strings.
- Integration tests: worker proxy route for private character lookup, private input submission, and event stream replay.
- Manual testing: join a session on a phone-like browser, confirm the browser signs in before loading private data, and verify reconnect resumes private state without exposing raw clue text on other surfaces.

---

# Risks and Unknowns

**Risks**:

- If the browser stores the join custom token instead of the exchanged bearer token, authenticated player endpoints will fail on the first private request.
- If inline event helpers keep calling module-local functions, the serialized browser script will throw on the first rendered event.

**Unknowns**:

- The player token exchange path must stay server-side in the Nightcap runtime and must not introduce a second authority for event filtering.

---

# Open Questions

- None. The implementation path is defined by the approved runtime contract and the existing auth model.
