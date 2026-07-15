# 12-Build-Roadmap-v1.1

**Version:** 1.1  
**Date:** May 2026  
**Status:** Active  
**Derived from:** 06-PRD-v1.3 and 07-Technical-Architecture-v1.3  
**Primary audiences:** Founder, AI coding agents, future technical co-founder

## How To Use This Roadmap

This is the execution layer beneath the PRD and Technical Architecture.

- The PRD says what and why.
- The Architecture says how the system is shaped.
- This roadmap says what gets built, in what order, by whom, and how each piece is verified.

Three layers:

- **Milestones** group work and end at a verifiable gate.
- **Epics** are coherent chunks of work inside a milestone.
- **Tasks** are sized for a single AI agent session.

Source-of-truth rule: tasks reference Architecture and PRD sections rather than restating schemas. If a task and the Architecture doc disagree, the Architecture doc wins; fix the task.

Decomposition policy: Milestone 1 is complete. AW-201 decomposes Milestones 2 through 6 into epics and agent-sized task specs so the path to first qualifying Nightcap playtests is executable. M4 implementation tasks are anchored to the AW-202 Nightcap web experience runtime decision before runtime-specific work begins.

## Couch Race Retarget (July 15, 2026)

Per ADR-0013 and D-071, the Nightcap v1 launch experience is Couch Race (`docs/story-bibles/nightcap-couch-race.md`): all players are investigators racing to solve a murder committed by an AI suspect, 2–8 players, 20–40 minutes, six-beat arc. Consequences for this roadmap:

- Rehearsal 1 retargets to a Couch Race thin slice (AW-286). Historical milestone gates that already closed against the eight-beat arc (M2, M3) are unaffected.
- Epic [M5-I: Nightcap Couch Race Arc And Interrogation Layer](./epics/M5-I-nightcap-couch-race-arc-and-interrogation.md) carries the new work (AW-281 through AW-286).
- D-069 narrative tasks (AW-276–AW-280) carry over, aligned to the six-beat arc.
- The M6 exit gate is unchanged in spirit; qualifying sessions run Couch Race, and the four-player minimum in session composition drops to two per the amended PRD scope.

## M0 Gate Override

PRD v1.3 Section 9 defined a Wizard-of-Oz manual validation phase before significant production code. That gate has been explicitly overridden by the founder.

Build sequence: Engine, Platform, Game, live test with real users, iterate.

Risk accepted: production engineering begins before the personalization layer has been validated with real users. If M6 reveals the personalization thesis fails, more engineering will need revisiting than if a Wizard-of-Oz phase had caught it earlier.

## Milestone Map

| ID | Milestone | Build-order coverage | Exit gate |
| --- | --- | --- | --- |
| M0 | Wizard-of-Oz validation | none (manual, no code) | Overridden, May 2026 |
| M1 | Deterministic platform core | #1 session models, #2 knowledge graph, #3 routing, harness scaffold | KG unit tests pass; routing swaps with zero code change; `alembic upgrade head` clean; arc-testable harness skeleton runs |
| M2 | Arc engine + Nightcap arc + safety | #4 arc execution, #5 safety, #7 character behavior | Nightcap arc runs all eight beats in harness; killer assigned through the constrained-random v1 assignment interface; reveal fires; AI dialogue never leaks knowledge state; L1 hard stops + L2 classification fire pre-generation |
| M3 | Events, API, persistence, telemetry | #6 events, #8 API + auth, #9 persistence, #10 telemetry, #11 full harness | Full session runs through API; events routed by target audience with no leakage; interrupt/resume restores to nearest beat; 5 telemetry signals logging; batch harness runs 10 headless sessions |
| M4 | Nightcap experience layer | none (experience layer, PRD-required) | Real humans play end-to-end on real devices; join under 30s; private info never on shared display |
| M5 | Hardening + proof prerequisites | none (PRD MVP done-criteria) | Adversarial safety playtest complete and blocking issues resolved; per-session gross margin known at each supported human player count; Daily Case second arc schema designed with post-M6 executable follow-through queued; live knowledge graph inspection surface live; the continuity and coherence eval suite (AW-272) runs against a synthetic session batch and reports knowledge-leak rate and contradiction count |
| M6 | First qualifying sessions | none (the actual H1 proof) | 5+ completed sessions with outside groups; replay enthusiasm; personalization perception in 2+; run at 4-6 players |

## Sequencing Note

Architecture S15.9 lists the simulation harness as component #11, but the arc execution engine acceptance criteria require a harness. The roadmap therefore splits the harness:

- a minimal arc-runnable skeleton lands at the end of M1
- the full batch and deterministic harness lands in M3

## Operational Companions

- [operations/github-project-setup.md](./operations/github-project-setup.md)
- [operations/working-model.md](./operations/working-model.md)
