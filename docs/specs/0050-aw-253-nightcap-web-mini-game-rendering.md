# AW-253: Nightcap Web Mini-game Rendering And Device Integration

**Status**: Draft

**Author**: Codex | **Date**: 2026-06-20

---

# References

- Related ADRs: `docs/decisions/0003-nightcap-web-experience-runtime.md`, `docs/decisions/0009-mini-game-runtime-boundary.md`
- Related specs: `docs/specs/0049-aw-252-mini-game-api-events-and-sdk.md`
- GitHub issue: #147

---

# Overview

Render mini-games in the Nightcap web experience while Arcwright remains the
only canonical state authority.

---

# In Scope

- Renderer registry keyed by presentation identifiers
- Individual, collaborative, and group fixture renderers
- Authorized SDK event/state consumption and action submission
- Touch, keyboard, reduced-motion, loading, timeout, error, and reconnect states
- Shared-display and private-device privacy verification
- Cloudflare Pages, Workers, and Durable Objects integration after the revisit
  gate

---

# Out Of Scope

- Arc execution, timers, scoring, clue unlocking, or canonical state in the web
  runtime
- Production game selection

---

# Acceptance Criteria

- [ ] The ADR 0003 revisit comparison is recorded before the first
  Cloudflare-specific dependency or deployment configuration.
- [ ] All three fixture modes render on their intended surfaces.
- [ ] Clients submit actions through the SDK and cannot resolve outcomes locally.
- [ ] Reconnect restores authorized presentation state.
- [ ] Private payloads never reach another player or the shared display.
- [ ] Accessibility and degraded-network states pass documented checks.

---

# Test Plan

- Component tests for renderer registration and all visual states
- Mocked SDK integration tests
- Real-device privacy and reconnect matrix feeding AW-230

---

# Risks and Unknowns

**Risks**: Durable Objects must remain ephemeral and cannot become a second
session authority.

**Unknowns**: The Cloudflare revisit gate may produce a superseding ADR. The
current approved default remains Cloudflare.

---

# Open Questions

- Which room abstraction is selected after the revisit gate?
