# AW-202: Nightcap Web Experience Runtime Decision

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-08

---

# References

- Related ADRs: `docs/decisions/0003-nightcap-web-experience-runtime.md`
- Architecture sections: `docs/architecture/01-overview.md`, `docs/architecture/08-event-system.md`, `docs/architecture/09-developer-api.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0020-aw-201-m2-m6-roadmap-and-tracker-bootstrap.md`
- PRD sections: `docs/prd/01-overview.md`, `docs/prd/02-requirements.md`
- Roadmap sections: `docs/roadmap/00-overview.md`, `docs/roadmap/milestones/M4-nightcap-experience-layer.md`, `docs/roadmap/tasks/AW-202-external-nightcap-platform-decision.md`

---

# Overview

This spec defines the documentation-only decision work for AW-202. It selects the Nightcap web experience runtime that will host the browser-based shared display and player-phone clients, and it defines the integration contract with Arcwright APIs.

This is not a decision to build Nightcap in a third-party app builder. It is also not a decision to move Arcwright engine, API, session state, knowledge graph, safety, or telemetry ownership out of Arcwright.

---

# In Scope

- Record an ADR naming the selected Nightcap web experience runtime
- Document the integration contract between the Nightcap web experience and Arcwright REST/SSE APIs
- Clarify that Arcwright remains authoritative for session state, knowledge state, safety, telemetry, arc execution, and event audience targeting
- Update M4 task files so they reference the selected runtime and no longer treat the experience runtime as TBD
- Preserve M4 task dependencies on AW-225, AW-226, AW-227, AW-228, AW-229, AW-230, and AW-231 as already decomposed by AW-201

---

# Out Of Scope

- Product code in `engine/`, `api/`, `sdk/`, `dashboard`, `nightcap`, or `migrations`
- Implementing the Nightcap Cloudflare app, Worker, Durable Object, or PartyKit room
- Changing Arcwright API schemas, event schemas, auth behavior, or persistence behavior
- Moving Arcwright core infrastructure from GCP to Cloudflare
- Introducing a no-code or low-code app builder into the product architecture
- Changing AI routing, prompts, safety policy, or telemetry schemas
- Adding dependencies

---

# Acceptance Criteria

- [ ] A decision record names the selected Nightcap web experience runtime, or explicitly blocks M4 if no runtime is acceptable
- [ ] The decision record states that the selected runtime is not a third-party app builder and not Arcwright core infrastructure
- [ ] The integration contract lists API, SDK, auth, event, deployment, privacy, state ownership, and performance assumptions
- [ ] M4 task files `AW-225` through `AW-231` reference the selected runtime or contract and are no longer blocked on a TBD platform decision
- [ ] The M4 milestone exit gate remains unchanged: real humans play end-to-end on real devices, join under 30 seconds, and private information never appears on the shared display
- [ ] No product code, dependencies, schema, prompt, routing, eval, secret, or auth implementation changes are made

---

# Test Plan

- Validate `docs/roadmap/index.json` if it changes
- Review `docs/decisions/0003-nightcap-web-experience-runtime.md` for the required contract sections
- Review M4 task docs for references to the selected runtime and removal of TBD platform blocking language
- Search changed files for em dash characters
- Inspect `git status` for intended documentation changes only

---

# Risks And Unknowns

**Risks**:
- The phrase external platform can be misread as a no-code app builder. The ADR must use the more precise term Nightcap web experience runtime.
- Durable Objects or PartyKit could accidentally become a second session authority if the contract is weak. The ADR must state that Arcwright owns canonical state and event audience filtering.
- A Worker or Durable Object proxy that ingests all events and re-filters them could create a privacy risk. The contract must require scoped streams or equivalent Arcwright-authorized delivery.

**Unknowns**:
- Whether M4 implementation will use PartyKit directly or only Cloudflare Durable Objects. The decision allows PartyKit as an optional room abstraction, not a mandatory dependency.
- Exact Cloudflare cost at real playtest volume. The H1 expectation is low UI infrastructure cost relative to LLM cost, but AW-234 remains responsible for measured gross margin.
- The detailed visual rendering system remains deferred to M4 implementation tasks.

---

# Open Questions

- None for AW-202. Implementation details are intentionally deferred to M4 tasks.
