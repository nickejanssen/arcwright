---
id: productroadmap.roadmap.tasks.aw-349-prove-browser-minigame-port-and-package-reuse
namespace: product-roadmap
title: "AW-349: Prove a browser minigame port and reuse the same package in an Arcwright experience"
owner: Nico Janssen
status: active
review_by: "2027-02-16"
sensitivity: internal
source: authored
x-scope-evidence: D-119
tags: []
supersedes: []
---

# AW-349: Prove a browser minigame port and reuse the same package in an Arcwright experience

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Shared  
**Owner:** One implementation session and founder playtest  
**Target date:** Before 2026-12-05, the founder TV run (D-141). Order: after AW-348.

## Plain-English Summary

Measure how much work it takes to port a small browser game, play it on its own, and use the same version in an Arcwright experience. Produce a repeatable author handoff from observed steps.

## Why This Matters

The existing import workflow preserves source. A successful import alone does not show whether the original decisions, timing and outcomes survive the port, or how quickly another developer can repeat it.

## Technical Scope

- Select a small owned or appropriately licensed source with the founder. Keep the original playable and record a baseline round, assets and provenance, inputs, timing, scoring and any host-specific dependencies.
- Follow the minigame intake skill, package contract and ADR 0018. Reuse compatible assets and presentation; map authority explicitly. Port one complete round, compare it with the original, then bind that package version to an Arcwright experience through a thin destination adaptation. Use Nightcap when its integration is ready.
- Record authoring steps, manual edits, reused pieces, friction and timings. Add the verified workflow and exact launch/test commands to the existing authoring guide. Link the example package and adaptation.

## Human Collaboration Contract

**Interaction profile:** Creative selection, independent port following approval, facilitated comparison. Current phase is scope capture. Next gate is founder selection of a source and review of the proposed port. Ask the founder to compare play feel and note intentional differences before promotion.

## Acceptance Criteria

- [ ] A fresh developer can follow the guide from original source to a separately playable package. Record time to first faithful round and effort to adapt it.
- [ ] Use one package version with two entry points: direct launch with Nightcap offline and destination launch. A fixed fixture and input transcript yield matching local results; only the destination maps the result to a story consequence, exactly once on retry.
- [ ] Record original-versus-port differences, real mobile/desktop evidence, player counts actually tested and remaining portability limits. Include at least one case of failure, tie or timeout applicable to the fixture.

## Tests/Verification

Keep the baseline and replay fixture, run rule tests and browser checks, and record the two launch commands and device observations. Report separately what merged, was deployed and was seen in play.

## Dependencies

AW-348 provides the live player. Coordinate the destination fixture with AW-337 and existing destination integration tasks. Order the standalone and integration proofs independently if the destination is still being built.

## Must Not Do

No duplicate scoring implementation per destination. Do not infer general-purpose automatic porting from a single sample.
