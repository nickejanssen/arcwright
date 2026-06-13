# 0003 - Nightcap Web Experience Runtime

**Date:** 2026-06-08
**Status:** Accepted
**Architecture reference:** `docs/architecture/01-overview.md`, `docs/architecture/08-event-system.md`, `docs/architecture/09-developer-api.md`, `docs/architecture/15-development-guide.md`
**Spec reference:** `docs/specs/0022-aw-202-nightcap-web-experience-runtime-decision.md`
**Scope:** Nightcap Layer 3 browser experience runtime for M4

---

# Context

AW-202 exists because `docs/product/decisions-log-additions-may2026.md` Entry 3 already decided that Nightcap's experience layer will be outside Arcwright core and will connect to Arcwright through its API. That prior decision protects surface agnosticism: Arcwright emits structured events and the experience layer renders them.

The remaining decision is not whether to use a third-party app builder. The remaining decision is which web runtime hosts the custom browser experience for the shared display and each player phone.

Nightcap needs:

- Browser-based player devices with no app install
- A shared display for narrator and group-visible story moments
- QR or code join under 30 seconds
- Real-time room coordination for the Nightcap v1 four-human-player floor and additional supported human players
- Private event delivery that never leaks one player's information to another player or to the shared display
- A runtime boundary that keeps Arcwright authoritative for session state, knowledge state, safety, telemetry, arc execution, and event audience targeting

Alternatives considered:

- Build the Nightcap experience as part of Arcwright core. Rejected because it violates the surface-agnostic platform boundary and turns a Nightcap display choice into platform architecture.
- Use a no-code or low-code app builder. Rejected because the product needs custom browser clients, real-time room behavior, scoped auth, reconnect behavior, and strict privacy guarantees.
- Build and host a separate conventional web app on the same GCP stack as Arcwright. Rejected for M4 because it gives less edge-native room coordination and does not improve the Arcwright core boundary.
- Use Cloudflare Pages, Workers, and Durable Objects, with PartyKit allowed as a room abstraction. Accepted because it fits the browser-first, room-oriented Nightcap UX while keeping Arcwright core unchanged.

---

# Decision

Nightcap's browser-based host, shared-display, and player-phone experience uses Cloudflare Pages, Workers, and Durable Objects as its web experience runtime. PartyKit may be used as an optional room abstraction on top of Durable Objects.

This is not a decision to build Nightcap in a third-party app builder. This is not a decision to move Arcwright engine, API, session state, knowledge graph, safety, model routing, telemetry, or persistence off the Arcwright backend.

Arcwright remains the source of truth for:

- Session lifecycle and canonical session state
- Arc execution and deterministic transitions
- Knowledge state and character state
- Content safety and model routing
- Telemetry and event persistence
- `ContentEvent.target_audience` and private event authorization

The Nightcap web experience runtime owns:

- Browser rendering for shared display, host controls, and player phones
- QR or code join UI
- Ephemeral room presence
- Reconnect UX and client coordination
- Presentation state derived from Arcwright events
- Deployment of the custom Nightcap web experience

## Integration contract

API assumptions:

- The Nightcap runtime consumes Arcwright REST lifecycle and input endpoints.
- The Nightcap runtime consumes Arcwright event delivery through the TypeScript SDK or an equivalent typed REST/SSE client.
- Host controls call Arcwright API endpoints. They do not bypass Arcwright session lifecycle or arc execution.

SDK assumptions:

- The TypeScript SDK remains a typed Arcwright API and SSE client.
- The SDK contains no arc execution logic, game rules, or rendering assumptions.
- Nightcap rendering code imports or wraps the SDK from the Cloudflare-hosted client.

Auth assumptions:

- Hosts authenticate through Arcwright's host auth path.
- Players join anonymously through scoped session join tokens.
- Player clients receive only the token and session context needed for their assigned participant.
- Secrets and API keys are not embedded in browser clients.

Event assumptions:

- `ContentEvent.target_audience` remains authoritative.
- `specific_player` events must only be delivered to the intended player device.
- `shared_display` events must never include private clue text.
- `host_only` events must not be rendered to player devices or the shared display.
- Presentation hints are rendering inputs only. They do not change engine state.

Privacy assumptions:

- The preferred delivery pattern is scoped Arcwright event streams per authorized client.
- If a Worker or Durable Object proxies event traffic, it must proxy scoped streams or equivalent Arcwright-authorized payloads.
- The Nightcap runtime must not ingest an all-events stream and reimplement private filtering as its primary privacy boundary.

Deployment assumptions:

- Cloudflare Pages hosts static browser assets.
- Cloudflare Workers handle lightweight join, bootstrap, and runtime coordination routes.
- Durable Objects or PartyKit rooms handle ephemeral session-room presence and reconnect coordination.
- Arcwright core remains deployed according to the existing backend architecture.

Performance and cost assumptions:

- Workers and Durable Objects stay thin. They do not run LLM calls, heavy generation, or canonical state transitions.
- Durable Objects store only ephemeral coordination state needed by the browser experience.
- WebSocket hibernation or sparse room activity should be used where M4 implementation requires long-lived room connections.
- H1 UI infrastructure cost is expected to be small relative to LLM cost, but measured gross margin remains the responsibility of AW-234.

---

# Consequences

## Positive consequences

- M4 can decompose against a concrete browser runtime instead of a TBD external platform.
- Nightcap gets a custom web experience suited to shared display plus phone play without native apps.
- Arcwright preserves surface agnosticism because all authoritative game and platform state remains behind Arcwright APIs.
- Durable Objects or PartyKit provide a natural place for ephemeral room presence and reconnect coordination.

## Negative consequences

- The system now has two deployment surfaces: Arcwright backend and Nightcap web runtime.
- M4 implementers must understand both Arcwright's event contract and Cloudflare's room-runtime model.
- Local development and observability will need explicit setup for the Cloudflare side during M4.

## Trade-offs

- We gain a browser-first, room-oriented runtime for Nightcap without polluting Arcwright core.
- We accept an additional runtime boundary and integration contract that must be tested on real devices.
- We keep core session authority in Arcwright and give up the simplicity of putting all Nightcap UI behavior in one backend stack.

---

# References

- `docs/product/decisions-log-additions-may2026.md` Entry 3
- `docs/prd/02-requirements.md`
- `docs/architecture/08-event-system.md`
- `docs/architecture/09-developer-api.md`
- `docs/roadmap/00-overview.md`
- `docs/roadmap/milestones/M4-nightcap-experience-layer.md`
- `docs/roadmap/tasks/AW-202-external-nightcap-platform-decision.md`
- `docs/product/decisions-log.csv` D-052
- Cloudflare Workers pricing: https://developers.cloudflare.com/workers/platform/pricing/
- Cloudflare Durable Objects pricing: https://developers.cloudflare.com/durable-objects/platform/pricing/
- Cloudflare Durable Objects WebSockets: https://developers.cloudflare.com/durable-objects/best-practices/websockets/
- PartyKit: https://www.partykit.io/
