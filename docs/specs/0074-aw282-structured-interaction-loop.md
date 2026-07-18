# AW-282 Structured Interaction Loop

**Status**: Approved

**Author**: Arcwright product and engineering | **Date**: 2026-07-18

---

# References

- Related ADRs: `docs/decisions/0014-structured-interaction-resolution.md`, `docs/decisions/0008-content-event-type-layering.md`
- Architecture sections: `docs/architecture/08-event-system.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0072-nightcap-couch-race-v1.md`
- Product and story context: `docs/roadmap/tasks/AW-282-interrogation-round-loop-and-question-intents.md`, `docs/story-bibles/nightcap-couch-race.md`
- Design record: `docs/superpowers/specs/2026-07-18-aw282-structured-interaction-design.md`

---

# Overview

AW-282 defines a game-agnostic structured interaction capability. Players choose authored questions and targets privately. The Python engine validates menus, evidence gates, selection allowances, deterministic resolution order, public answer groups, and private feedback delivery.

The player-facing language is Questions and Ask. The engine does not accept free text or voice questions in v1 and does not generate menus with a model.

---

# In Scope

- Pydantic schemas for interaction definitions, windows, options, targets, selections, resolutions, and limits.
- Three authored baseline options plus up to two visible evidence-gated options per menu. Additional authored evidence options remain eligible in authored order for later windows.
- Player-count allowances shared across all rounds in a beat. A new beat receives its own authored allowance.
- Private selection, revision, lock, deterministic staging, and rotated resolution order.
- Public answer groups for every selected question. Evidence-gated options may also produce private feedback for the asker.
- Immutable resolution records carrying authorized knowledge context, claim references, and evidence references for AW-283.
- ArcDefinition interaction references and Nightcap Couch Race authored configuration.
- Arc-backed InteractionRuntime and ContentEvent factories using existing fanout privacy routing.

---

# Out of Scope

- Free text or voice input.
- Model-generated menus or answer generation.
- Knowledge graph mutation, truth inference, contradiction detection, or answer prose generation. AW-283 owns answer generation.
- Leverage grants, spends, advantages, sabotages, or mini-game rewards.
- New database tables, migrations, or TypeScript surface code.

---

# Human Collaboration Contract

**Interaction profiles**: Independent execution with founder approval gate

**Classification rationale**: The founder selected the platform-neutral vocabulary and approved the structured interaction design before implementation.

**Required founder inputs**: None remaining for AW-282.

**Phase gates**:
- Design artifact review and approval before implementation.
- PR review before merge.

**Review package**: Design record, implementation plan, tests, and PR acceptance evidence.

**Approval evidence**: Founder approval in the 2026-07-18 session for the written AW-282 design and implementation plan.

**Owner actions**: Claude Code owns AW-283 follow-on implementation.

---

# Acceptance Criteria

- [x] A synthetic session opens, submits, locks, and resolves deterministic interaction windows.
- [x] Menus contain three baseline choices and no more than two visible evidence-gated choices, with deterministic authored ordering.
- [x] Additional evidence options are retained in the authored catalog rather than rejected.
- [x] Selection allowances are count-specific and shared across rounds within a beat.
- [x] Duplicate public target and option selections combine into one public answer group while every selection remains accounted for.
- [x] Every selected question creates a public answer request; authored private options also create private feedback for the asker.
- [x] Public events route to all authorized players and displays. Private feedback routes only to the selecting player.
- [x] Resolution records preserve authorized knowledge context, claim references, and evidence references and are immutable after lock.
- [x] A one-player, one-target configuration is supported for Daily Case.
- [x] No free text, model-generated menus, provider names, UI logic, or Leverage runtime behavior are added.

---

# Test Plan

- Unit tests cover model validation, semantic duplicate prevention, menu eligibility and caps, allowances, revisions, deterministic staging and ordering, and immutable resolution records.
- Integration tests cover synthetic multi-player resolution, one-player Daily Case configuration, arc-backed runtime consumption, public and private ContentEvent routing, and preserved AW-283 context references.
- Full engine verification uses the project Python environment with an explicit worktree-local pytest base directory on Windows.

---

# Risks and Unknowns

**Risks**:
- Evidence catalogs with many eligible options can feel repetitive if authored ordering is weak. Authoring review owns ordering quality.
- Private feedback generation and answer generation will increase model work in AW-283 and require cost-aware routing.

**Unknowns**:
- AW-283 will define the exact claim and contradiction metadata returned by answer generation.

---

# Open Questions

- AW-283 must define how authorized knowledge context references resolve to the canonical knowledge graph snapshot.
