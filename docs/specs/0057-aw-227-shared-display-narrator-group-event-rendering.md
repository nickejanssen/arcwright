# AW-227: Shared Display Narrator And Group Event Rendering

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-22

---

# References

- Related ADRs: `docs/decisions/0003-nightcap-web-experience-runtime.md`
- Architecture sections: `docs/architecture/08-event-system.md` §8.1, §8.4, §8.5, `docs/architecture/09-developer-api.md`, `docs/architecture/15-development-guide.md` §15.6
- Related specs: `docs/specs/0055-aw-225-nightcap-web-runtime-connector-scaffold.md`, `docs/specs/0056-aw-226-host-session-creation-and-shared-display-flow.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap tasks: `docs/roadmap/tasks/AW-227-shared-display-narrator-and-group-event-rendering.md`

---

# Overview

Render narrator and group-visible `ContentEvent`s in the Nightcap shared-display runtime without leaking private clue content or host-only content. Arcwright stays authoritative for `target_audience`; the web runtime only renders the scoped payload it receives.

---

# In Scope

- `nightcap-web/src/ui.ts`
  - Shared-display event rendering for narrator and group-visible `ContentEvent`s
  - Safe extraction of visible text from `payload`
  - Display-only rendering of `presentation_hints`
- `nightcap-web/src/filters.ts`
  - Reuse of canonical audience-filter values
- `nightcap-web/src/index.ts`
  - Package entry-point exports for shared-display and host-visible audience constants
- `nightcap-web/tests/ui.test.ts`
  - Coverage for narrator text rendering, privacy-safe fallback handling, and display-only presentation hints

---

# Out Of Scope

- Arc execution logic in TypeScript
- Any second privacy or audience-filter authority in the web runtime
- Exact D-054 host seed questions or join prompts
- Host lifecycle changes, room presence changes, or worker route changes
- New dependencies, provider strings, model strings, or auth changes

---

# Acceptance Criteria

- [ ] Narration events render from `ContentEvent` payloads on the shared display.
- [ ] Group-visible events render without private clue content.
- [ ] Presentation hints are consumed only as display hints and do not change session or engine state.

---

# Test Plan

- Unit tests: `nightcap-web/tests/ui.test.ts` covers narrator text extraction, safe fallback handling for `private_delivery` payloads, and display-only presentation hints.
- Integration tests: `npm run typecheck` and `npm test` in `nightcap-web`.
- Manual testing: open the shared-display runtime shell and verify visible events show narrator text or a safe placeholder rather than raw private payload fields.

---

# Risks and Unknowns

**Risks**:
- Inline script helpers remain bundled through server-rendered source serialization until the runtime asset structure is revisited.
- Future event payload variants may require new whitelisted display fields or a richer display contract.

**Unknowns**:
- Whether a future Nightcap web asset bundle should replace inline helper serialization in this runtime.
- Whether additional group-visible event categories will need richer shared-display presentation metadata later.

---

# Open Questions

- None blocking.
