# 0055 - AW-225: Nightcap Web Experience Runtime Connector Scaffold

**Status**: Done

**Author**: Nicolas Janssen | **Date**: 2026-06-22

---

# References

- Related ADRs: `docs/decisions/0003-nightcap-web-experience-runtime.md`
- Architecture sections: `docs/architecture/08-event-system.md`, `docs/architecture/09-developer-api.md`
- Related specs: `docs/specs/0022-aw-202-nightcap-web-experience-runtime-decision.md`, `docs/specs/0054-aw-255-rest-backed-nightcap-session-loop.md`
- PRD sections: `docs/prd/03-scope.md`
- Task: `docs/roadmap/tasks/AW-225-external-platform-connector-scaffold.md`

---

# Overview

Scaffold the Cloudflare-hosted Nightcap web experience runtime connector: a Worker entry point, Durable Object room, typed connector client, and Wrangler deployment configuration that satisfies the AW-202 integration contract without adding any arc execution logic to the TypeScript layer.

---

# Cloudflare Revisit Note (ADR 0003 requirement)

ADR 0003 mandates a comparison against a GCP-only implementation before introducing the first Cloudflare-specific dependency. That comparison was performed at the start of AW-225 implementation.

`docs/product/decisions-log.csv` contains a prior entry (dated May 7, 2026) that reads: "Cloudflare Workers rejected: constrains language to TS/JS, time limits problematic for AI calls." That entry applies to the **Arcwright engine and API layer** (Python, long-lived LLM calls), not to the Nightcap experience layer. ADR 0003 records the correct superseding decision: Cloudflare Pages, Workers, and Durable Objects are the approved web experience runtime for the Nightcap browser clients, which are TypeScript-only and never run LLM calls. The decisions-log entry and ADR 0003 are not in conflict once the scope boundary is clear.

GCP-only alternative (Cloud Run + Firebase Realtime Database) was considered and rejected for M4 because it gives less edge-native room coordination and offers no improvement to the Arcwright core boundary. Cloudflare remains the default per ADR 0003.

---

# In Scope

- `nightcap-web/` directory: Cloudflare Worker entry point (`src/worker.ts`), Durable Object room (`src/room.ts`), typed connector client (`src/connector.ts`), shared types (`src/types.ts`)
- `nightcap-web/wrangler.toml` deployment configuration
- `nightcap-web/package.json`, `tsconfig.json` build configuration
- Unit tests covering Worker route dispatch, bootstrap authorization, room join/leave/snapshot, and connector SSE retry logic
- Export of `NightcapRoom` for Wrangler Durable Object binding

---

# Out of Scope

- Any arc execution logic (stays in Python engine)
- Nightcap UI rendering (separate task)
- Production secret configuration (values are placeholders; set via Cloudflare dashboard)
- SDK changes (TypeScript SDK remains unchanged)
- Schema or database changes

---

# Acceptance Criteria

- [x] Before adding a Cloudflare-specific dependency, Worker, Durable Object, or deployment configuration, compare ADR 0003 against a GCP-only implementation using then-current Cloud Run and Firebase capabilities; Cloudflare remains the default unless superseded by a founder decision. (Done — see Cloudflare Revisit Note above. ADR 0003 revisit trigger satisfied. Cloudflare confirmed.)
- [x] Connector can create or attach to a Nightcap session using the AW-202 runtime contract. (Done — `NightcapConnector.createSession` and `attachToSession` implement the lifecycle contract; `bootstrapSession` and `loadSession` expose it via the Worker.)
- [x] Connector subscribes to Arcwright events without requiring engine surface assumptions. (Done — `subscribeToEvents` consumes the SSE stream at `/v1/sessions/{id}/events`; no rendering logic or surface knowledge in the connector or types.)
- [x] Connector keeps Arcwright authoritative for session state, event audience targeting, safety, and telemetry. (Done — the Worker proxies all session lifecycle through Arcwright API calls; the Durable Object stores only ephemeral room presence; `target_audience` filtering is not reimplemented in the runtime layer.)

---

# Test Plan

- Unit tests: `nightcap-web/src/tests/` covers Worker route dispatch (bootstrap, load-session, room delegate, 404), `authorizeBootstrapSession` edge cases (missing token, whitespace-only, mismatch, valid), `NightcapConnector` (`createSession`, `getSession`, `attachToSession`), `subscribeToEvents` SSE parsing and retry logic (success, malformed payload, retry exhaustion, cancellation), and `NightcapRoom` join/leave/snapshot operations.
- Integration tests: not in scope for this scaffold; covered by the M4 exit harness.
- Manual testing: local `wrangler dev` with real Arcwright API base URL.

---

# Risks and Unknowns

**Risks**:
- Wrangler CLI version drift may require `compatibility_date` updates before production deployment.
- Durable Object WebSocket hibernation is not yet implemented; long-lived rooms will hold a persistent WebSocket connection until a follow-up task.

**Unknowns**:
- Production `ARCWRIGHT_API_BASE_URL` and `ARCWRIGHT_API_KEY` values are not set in this scaffold; they must be configured via Cloudflare dashboard or `wrangler secret` before any real deployment.

---

# Open Questions

None blocking. The ADR 0003 revisit trigger is now closed for AW-225 scope.
