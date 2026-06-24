# AW-230: Real-Device Privacy Matrix

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-23

---

# References

- Related ADRs: `docs/decisions/0003-nightcap-web-experience-runtime.md`
- Architecture sections: `docs/architecture/08-event-system.md` §8.4, §8.5, `docs/architecture/15-development-guide.md` §15.9
- Related specs: `docs/specs/0059-aw-229-player-private-event-and-input-flow.md`
- PRD sections: `docs/prd/01-overview.md`, `docs/prd/02-requirements.md`
- Roadmap tasks: `docs/roadmap/tasks/AW-230-real-device-privacy-matrix.md`

---

# Overview

Validate the Nightcap web runtime's privacy boundary with the smallest useful role matrix before first qualifying real-device playtests.

---

# In Scope

- Role-scoped matrix coverage for `all`, `specific_player`, `host_only`, and `shared_display`
- Assertions that Player A never sees Player B private event content
- Assertions that the shared display never renders private clue text
- Tests that reuse the existing Nightcap connector and browser runtime harness
- Documentation notes that keep the trust boundary with Arcwright's scoped event delivery

---

# Out Of Scope

- New event filtering authority in the Nightcap runtime
- Arc execution changes in TypeScript
- New player, host, or shared-display product behavior beyond privacy validation
- New dependencies, auth providers, or model routing changes

---

# Acceptance Criteria

- [ ] The privacy matrix proves routing for `all`, `specific_player`, `host_only`, and `shared_display`
- [ ] The matrix explicitly proves Player A never receives Player B private content
- [ ] The matrix explicitly proves the shared display never receives private clue text
- [ ] The tests stay minimal and preserve Arcwright as the authoritative event filter

---

# Test Plan

- Unit tests: role-scoped matrix assertions, player copy checks, and session-expiry helpers
- Integration tests: worker proxy behavior for player auth, token exchange, and reconnect handling
- Manual testing: validate on phone, host, and shared-display surfaces during real-device rehearsal

---

# Risks and Unknowns

**Risks**:
- If Arcwright stops sending scoped streams, the browser runtime would not be the correct place to reimplement filtering.
- If player tokens expire without a recovery path, reconnect behavior can degrade during a live rehearsal.

**Unknowns**:
- Exact device timing for reconnect in a crowded room
- Final playtest device mix and network quality

---

# Open Questions

- None
