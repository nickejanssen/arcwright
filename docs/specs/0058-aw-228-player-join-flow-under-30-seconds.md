# AW-228: Player Join Flow Under 30 Seconds

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-22

---

# References

- Related ADRs: `docs/decisions/0003-nightcap-web-experience-runtime.md`
- Architecture sections: `docs/architecture/08-event-system.md` §8.1, §8.4, §8.6, `docs/architecture/09-developer-api.md` §9.2, `docs/architecture/15-development-guide.md` §15.1, §15.6, §15.9
- Related specs: `docs/specs/0055-aw-225-nightcap-web-runtime-connector-scaffold.md`, `docs/specs/0056-aw-226-host-session-creation-and-shared-display-flow.md`, `docs/specs/0057-aw-227-shared-display-narrator-group-event-rendering.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap tasks: `docs/roadmap/tasks/AW-228-player-join-flow-under-30-seconds.md`

---

# Overview

Build the Nightcap player join path inside the Cloudflare-hosted `nightcap-web` runtime so a player can enter by QR link or join code, arrive on the player surface, and see only their assigned character context after joining. Arcwright remains authoritative for join validation, session state, and assignment results.

---

# Prompt Set

Prompt copy is centralized in `nightcap-web/src/personalization.ts` so edits stay in one place.
The QR path pre-fills session and token values, but the player must still answer the prompts and tap Join before the worker submits the exchange.

- Host seed questions:
  - `How familiar is this group with one another?`
  - `What tone should tonight lean toward?`
  - `What group dynamic should we amplify?`
- Player join prompts:
  - `What kind of role do you usually play in a group?`
  - `What kind of character energy do you want tonight?` optional

---

# In Scope

- `nightcap-web/src/worker.ts`
  - Public player join route
  - Host-backed player-slot creation route
  - Join-token exchange proxy to Arcwright
  - Room registration for joined players as ephemeral presence only
- `nightcap-web/src/ui.ts`
  - Player join page
  - Player post-join surface shell
  - Host controls for generating and displaying QR/code-ready player join links
- `nightcap-web/src/personalization.ts`
  - Editable host seed questions and player join prompts
- `nightcap-web/src/connector.ts`
  - Player-slot creation and join-token exchange helpers
- `nightcap-web/src/runtime.ts`
  - Player join request and response shapes for the worker runtime
- `nightcap-web/src/room.ts`
  - Ephemeral room membership records for joined players, including assigned character context
- `nightcap-web/tests/*.ts`
  - Coverage for join-token creation, join exchange, room registration, and player surface rendering

---

# Out Of Scope

- Arc execution logic in TypeScript
- Firebase account creation or any app install requirement
- A second filtering authority in the web runtime
- Private event streaming or player input handling beyond the join bootstrap
- New dependencies, provider strings, model strings, or secret handling changes

---

# Acceptance Criteria

- [ ] A new player can join by QR or code in under 30 seconds in rehearsal conditions.
- [ ] Player join does not require a Firebase account or app install.
- [ ] Player join captures one to two v1 personalization prompts using the resolved prompt set in `nightcap-web/src/personalization.ts`, and the worker forwards them in the Arcwright join exchange.
- [ ] Player receives only their assigned character context after join.

---

# Test Plan

- Unit tests: connector join helpers, worker player-join routes, room membership persistence, and player surface rendering.
- Integration tests: local `nightcap-web` build and test run against mocked Arcwright responses.
- Manual testing: create a host session, mint a player join link, open it on a phone-like browser surface, and confirm the player lands on the player view without host-only or shared-display leakage.

---

# Risks and Unknowns

**Risks**:

- If the player surface reuses shared-display components, private content could leak unless the surface rendering path stays explicit.

**Unknowns**:

- Whether later player-event and input work should exchange the custom player token in the worker or in the browser.
