# AW-245: Second Arc Minimal Executable Product

**Status**: Draft

**Author**: Codex | **Date**: 2026-06-13

---

# References

- Related ADRs: None yet
- Architecture sections: `docs/architecture/14-architecture-validation.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0023-aw-203-arcdefinition-schema-validation-core.md`, `docs/specs/0039-aw-235-daily-case-second-arc-schema-design.md`
- PRD sections: `docs/prd/03-scope.md`
- Roadmap task: `docs/roadmap/tasks/AW-245-second-arc-minimal-executable-product.md`
- Product decision: `docs/product/decisions-log.csv` D-056
- Story bible: `docs/story-bibles/daily-case.md`

---

# Overview

This spec records the post-M6 commitment to build Daily Case, the second arc defined by AW-235, as a minimal executable product. It preserves sequencing: Nightcap M6 proof happens first, then this work validates platform reuse by execution.

---

# In Scope

- Convert the AW-235 second arc schema into a minimal executable product after M6 proof
- Exercise platform primitives outside Nightcap, including arc execution, knowledge graph, event delivery, safety, routing, cost tracking, and telemetry where applicable
- Build the current approved working concept unless replaced by a later approved decision: a solo daily single-suspect interrogation game where the suspect remembers prior days through the knowledge graph
- Preserve the minimum Daily Case shape from AW-235: one player, one suspect, one primary surface, week-long case, sub-10-minute daily play
- Define follow-up implementation acceptance criteria after AW-235 and AW-244 are complete

---

# Out of Scope

- Starting implementation before AW-244 records H1 proof analysis
- Expanding Nightcap v1 scope
- Replacing the AW-235 schema design step
- Adding schema, API, privacy, telemetry, dependency, or migration work without a dedicated approved spec

---

# Acceptance Criteria

- [ ] AW-244 is complete before implementation begins
- [ ] AW-235 and `docs/story-bibles/daily-case.md` define the second arc schema, product shape, and validation gaps
- [ ] A follow-up implementation spec is approved before code work begins
- [ ] The executable product validates platform reuse without Nightcap-specific engine assumptions
- [ ] The executable product preserves Daily Case's core proof shape: asynchronous return play, contradiction accumulation, and final accusation
- [ ] The work does not delay Nightcap M2-M6 delivery

---

# Test Plan

- Documentation verification before implementation: confirm AW-235 and AW-244 are complete
- Implementation test plan to be defined in the follow-up implementation spec
- Regression verification must include checks that Nightcap behavior remains unchanged

---

# Risks and Unknowns

**Risks**:
- Pulling this work forward would disrupt Nightcap's proof timeline
- Treating the working concept as final before AW-235 may skip the schema validation step

**Unknowns**:
- Final product name
- Runtime surface and delivery model details
- Persistence and privacy requirements for prior-day memory

---

# Open Questions

- What exact implementation container carries cross-day case memory?
- What memory retention and deletion rules apply to the suspect's prior-day memory?
- What is the minimum executable loop that proves platform reuse without becoming a full second game?
