# AW-235: Daily Case Second Arc Schema Design

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-14

---

# References

- Related ADRs: `docs/decisions/0006-nightcap-continuity-v11.md`
- Architecture sections: `docs/architecture/04-knowledge-graph.md`, `docs/architecture/05-session-persistence.md`, `docs/architecture/14-architecture-validation.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0031-aw-245-second-arc-minimal-executable-product.md`
- PRD sections: `docs/prd/02-requirements.md`, `docs/prd/03-scope.md`
- Story bible: `docs/story-bibles/daily-case.md`
- Roadmap task: `docs/roadmap/tasks/AW-235-second-arc-schema-design.md`
- Product decision: `docs/product/decisions-log.csv` D-056

---

# Overview

This spec defines Card 2, Daily Case, as the concrete second-arc target for AW-235. It turns the D-056 working concept into a build-ready design contract that future implementation can follow after Nightcap proof.

---

# In Scope

- Select Daily Case as the canonical second-arc design target for M5-C
- Define the player-facing product shape: solo, asynchronous, five-minute daily interrogation across a week-long case
- Define the authored versus generative boundaries for the arc
- Define the minimum required state model for suspect memory, claim history, contradiction tracking, and final accusation
- Define which platform capabilities Daily Case validates beyond Nightcap and Monster RPG
- Define the minimum post-M6 executable-product scope for AW-245
- Record any required implementation follow-up specs before code work starts

---

# Out Of Scope

- Building the executable product before AW-244
- Pulling Daily Case requirements into Nightcap v1 or v1.1
- Locking a final brand name
- Full content authoring for multiple cases
- New schema, API, privacy, telemetry, or migration work without a dedicated implementation spec

---

# Human Collaboration Contract

**Interaction profile:** Independent execution.

This spec, the Daily Case story bible, and Architecture 14 fully constrain the
schema-design task. After normal plan approval, the agent may execute and must
explain the deliverables, validation gaps, and review evidence clearly.

Stop and reclassify to Creative collaboration or Decision interview before
inventing story direction, expanding product scope, selecting a new schema
policy, or changing the post-M6 boundary. Record plan approval, validation
evidence, dates, and owner actions.

# Acceptance Criteria

- [ ] `docs/story-bibles/daily-case.md` exists as the canonical experience brief for the second arc
- [ ] The second arc is explicitly defined as a solo, asynchronous, sub-10-minute, week-long interrogation product
- [ ] The design identifies the deterministic state that AI may not own: case truth, contradiction validation, unlock cadence, and accusation outcome
- [ ] The design identifies the minimum persisted state required across days: suspect claims, player interrogation history, contradiction ledger, evidence state, and case progression
- [ ] The design states which capability gaps Daily Case closes beyond Nightcap and Monster RPG
- [ ] The design defines the minimum executable-product scope for AW-245 without expanding current Nightcap milestones
- [ ] Any unresolved implementation seam is documented as a required follow-up spec input rather than left implicit

---

# Test Plan

- Documentation review against D-056, PRD scope, and architecture guardrails
- Cross-check the roadmap task, epic, and M5 exit-gate language against this spec
- Verify the story bible, roadmap docs, and AW-245 spec all point at the same second-arc concept

---

# Risks and Unknowns

**Risks**:
- Daily Case could drift into a full second product roadmap before Nightcap proof if sequencing is not kept explicit
- Cross-session persistence needs could tempt implementation shortcuts that bypass platform-clean state design
- A vague contradiction model would weaken the core wedge and make the product feel like prompt-only memory theater

**Unknowns**:
- Whether the executable product should model the week as linked daily sessions, a long-lived paused case, or another platform-clean container
- Which additional privacy or retention rules are required once the implementation surface is chosen
- Whether the minimum executable product needs one authored case or a tiny case template set

---

# Open Questions

- What is the exact implementation container for cross-day case state: linked sessions, long-lived case instance, or another approved structure?
- Does the first executable product need dedicated accusation-review UI beyond the standard interrogation surface?
- Which privacy and deletion controls are mandatory if player question history is stored verbatim rather than normalized?
