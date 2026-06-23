# AW-226: Host Session Creation And Shared Display Flow

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-22

---

# References

- Related ADRs: `docs/decisions/0003-nightcap-web-experience-runtime.md`
- Architecture sections: `docs/architecture/08-event-system.md`, `docs/architecture/09-developer-api.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0041-aw-217-session-lifecycle-api-and-auth.md`, `docs/specs/0055-aw-225-nightcap-web-runtime-connector-scaffold.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap tasks: `docs/roadmap/tasks/AW-226-host-session-creation-and-shared-display-flow.md`, `docs/roadmap/tasks/AW-227-shared-display-narrator-and-group-event-rendering.md`

---

# Overview

Build the Nightcap web runtime host-control flow and shared-display event feed on top of Arcwright's existing lifecycle APIs. The runtime may coordinate browser surfaces and ephemeral room state, but Arcwright remains authoritative for session state, lifecycle transitions, and event audience targeting.

---

# In Scope

- Browser-facing host controls in `nightcap-web/` for create, start, pause, resume, and end
- Shared-display event feed in `nightcap-web/` that renders only public or shared-display `ContentEvent`s
- Worker routes that proxy lifecycle calls to Arcwright instead of mutating session state locally
- Opaque capture of Nightcap v1 personalization intake fields without guessing the exact D-054 prompt text
- Test coverage for connector lifecycle calls, host runtime routes, and shared-display filtering

---

# Out Of Scope

- Exact D-054 question text or join prompts
- Arc execution logic in TypeScript
- Any second canonical session authority in Cloudflare
- Firebase token exchange UI or auth redesign
- New provider, model, routing, telemetry, or schema changes

---

# Acceptance Criteria

- [x] Host-facing runtime surfaces can create a session and then call Arcwright start, pause, resume, and end endpoints through the worker-backed client flow.
- [x] Shared-display rendering excludes `host_only` and `specific_player` content and only surfaces public or shared-display events.
- [x] Browser host creation captures opaque personalization intake payloads without inventing the unresolved D-054 prompt set.
- [x] Host controls and shared-display playback are implemented as thin proxies over Arcwright APIs, not as local session-state authority.
- [x] Tests cover the new host control lifecycle methods and shared-display filtering behavior.

---

# Test Plan

- Unit tests: connector lifecycle requests, shared-display audience filtering, worker route dispatch, and runtime shell rendering
- Integration tests: local worker flow against mocked Arcwright responses
- Manual testing: open the runtime shell, bootstrap a session, and verify the shared display only renders public or shared-display events

---

# Risks and Unknowns

**Risks**:

- Bootstrap and host-auth UX is still incomplete, so the runtime must not pretend the browser is the source of truth for session authority.
- If shared-display filtering is only client-side, the worker must still proxy the scoped Arcwright stream and avoid introducing a second filtering authority.

**Unknowns**:

- D-054 exact host seed questions and join prompts remain unresolved, so the runtime must treat intake as opaque data until that decision lands.
- The final host auth exchange path is still external to this task.

---

# Open Questions

- D-054 exact host seed questions and join prompts remain unresolved in canonical docs.
- Whether the browser host surface should later exchange the returned host token for an ID token internally or rely on a separate auth surface.
