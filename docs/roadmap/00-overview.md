# 12-Build-Roadmap-v1.1

**Version:** 1.1  
**Date:** May 2026  
**Status:** Active, with Nightcap authority migration in progress under issue #303  
**Derived from:** 06-PRD-v1.3 and 07-Technical-Architecture-v1.3  
**Primary audiences:** Founder, AI coding agents, future technical co-founder

## How To Use This Roadmap

This is the execution layer beneath the PRD and Technical Architecture.

- The PRD says what and why.
- The Architecture says how the system is shaped.
- This roadmap says what gets built, in what order, by whom, and how each piece is verified.

For **current Nightcap game-design intent**, `docs/gdd/nightcap/` has priority under ADR-0023 / D-108. This roadmap preserves execution history and existing task sequencing, but older Couch Race product assumptions do not override the current GDD. If an active roadmap task conflicts with the GDD, treat that as reconciliation work rather than silently following the older rule.

Three layers:

- **Milestones** group work and end at a verifiable gate.
- **Epics** are coherent chunks of work inside a milestone.
- **Tasks** are sized for a single AI agent session.

Source-of-truth rule: tasks reference Architecture and PRD sections rather than restating schemas. If a task and the Architecture doc disagree, the Architecture doc wins; fix the task. For Nightcap-specific gameplay/product behavior, the Master GDD now wins over superseded Story Bible, PRD, and Couch Race roadmap language.

Decomposition policy: Milestone 1 is complete. AW-201 decomposes Milestones 2 through 6 into epics and agent-sized task specs so the path to first qualifying Nightcap playtests is executable. M4 implementation tasks are anchored to the AW-202 Nightcap web experience runtime decision before runtime-specific work begins.

## Master GDD Retarget (August 31, 2026)

ADR-0023 and D-108 establish `docs/gdd/nightcap/` as the current Nightcap product/game-design authority. This supersedes the **product-design authority** of the July Couch Race retarget below while preserving the work built from it as implementation history.

Current Nightcap design implications for roadmap reconciliation:

- Two-player support is mandatory and first-class in V1.
- Four players is a reference configuration, not a floor.
- The V1 upper player-count bound remains OPEN and must not be inferred from the former 2–8 Couch Race range.
- Current gameplay is governed by the GDD loop and authoritative system pages rather than a fixed six-beat Couch Race product contract.
- The V1 endgame direction is deterministic Structured Reconstruction, with no numerical or subjective Case Strength determining the winner and no player winner when nobody solves the murder.
- Existing Couch Race implementation, tests, task history, and closed gates remain historical evidence. GitHub issue #303 owns the explicit implementation/spec reconciliation instead of this document pretending that old code already matches the GDD.

Until #303 is reconciled, milestone text below that names eight beats, six beats, fixed 2–8 support, old scoring, or Couch Race-specific implementation describes the baseline that existed when those milestones/tasks were written. It is not authorization to reintroduce those rules into new Nightcap design work.

## Historical Couch Race Retarget (July 15, 2026)

Per ADR-0013 and D-071, Nightcap was retargeted at that time to Couch Race (`docs/archive/nightcap-story-bibles/nightcap-couch-race.md`): all players as investigators racing to solve a murder committed by an AI suspect, 2–8 players, 20–40 minutes, six-beat arc. Consequences recorded for that roadmap version:

- Rehearsal 1 retargeted to a Couch Race thin slice (AW-286). Historical milestone gates that already closed against the eight-beat arc (M2, M3) were unaffected.
- Epic [M5-I: Nightcap Couch Race Arc And Interrogation Layer](./epics/M5-I-nightcap-couch-race-arc-and-interrogation.md) carried the new work (AW-281 through AW-286).
- D-069 narrative tasks (AW-276–AW-280) carried over, aligned to the six-beat arc.
- The then-current M6 exit gate used a two-player floor and fixed 2–8 range. The floor survives as first-class two-player support; the fixed upper bound does not. Current V1 upper bound is OPEN.

## M0 Gate Override

PRD v1.3 Section 9 defined a Wizard-of-Oz manual validation phase before significant production code. That gate has been explicitly overridden by the founder.

Build sequence: Engine, Platform, Game, live test with real users, iterate.

Risk accepted: production engineering begins before the personalization layer has been validated with real users. If M6 reveals the personalization thesis fails, more engineering will need revisiting than if a Wizard-of-Oz phase had caught it earlier.

## Milestone Map

| ID | Milestone | Build-order coverage | Exit gate |
| --- | --- | --- | --- |
| M0 | Wizard-of-Oz validation | none (manual, no code) | Overridden, May 2026 |
| M1 | Deterministic platform core | #1 session models, #2 knowledge graph, #3 routing, harness scaffold | KG unit tests pass; routing swaps with zero code change; `alembic upgrade head` clean; arc-testable harness skeleton runs |
| M2 | Arc engine + Nightcap arc + safety | #4 arc execution, #5 safety, #7 character behavior | **Historical gate:** Nightcap arc runs all eight beats in harness; killer assigned through the constrained-random v1 assignment interface; reveal fires; AI dialogue never leaks knowledge state; L1 hard stops + L2 classification fire pre-generation. Current Nightcap behavior is governed by the GDD; closed M2 evidence remains historical. |
| M3 | Events, API, persistence, telemetry | #6 events, #8 API + auth, #9 persistence, #10 telemetry, #11 full harness | Full session runs through API; events routed by target audience with no leakage; interrupt/resume restores to nearest beat; 5 telemetry signals logging; batch harness runs 10 headless sessions |
| M4 | Nightcap experience layer | none (experience layer, PRD-required) | Real humans play end-to-end on real devices; join under 30s; private info never on shared display |
| M5 | Hardening + proof prerequisites | none (PRD MVP done-criteria) | Adversarial safety playtest complete and blocking issues resolved; per-session gross margin known at each supported human player count; Daily Case second arc schema designed with post-M6 executable follow-through queued; live knowledge graph inspection surface live; the continuity and coherence eval suite (AW-272) runs against a synthetic session batch and reports knowledge-leak rate and contradiction count |
| M6 | First qualifying sessions | none (the actual H1 proof) | 5+ completed sessions with outside groups; replay enthusiasm; personalization perception in 2+; representative player-count validation includes first-class two-player evidence. Additional supported V1 counts are established through current GDD validation; the upper bound remains OPEN until evidence closes it. |

## Sequencing Note

Architecture S15.9 lists the simulation harness as component #11, but the arc execution engine acceptance criteria require a harness. The roadmap therefore splits the harness:

- a minimal arc-runnable skeleton lands at the end of M1
- the full batch and deterministic harness lands in M3

## Operational Companions

- [operations/github-project-setup.md](./operations/github-project-setup.md)
- [operations/working-model.md](./operations/working-model.md)
