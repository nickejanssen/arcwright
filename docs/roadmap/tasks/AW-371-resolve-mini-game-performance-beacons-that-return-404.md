---
id: productroadmap.roadmap.tasks.aw-371-resolve-mini-game-performance-beacons-that-return-404
namespace: product-roadmap
title: "AW-371: Resolve Mini-Game Performance Beacons That Return 404"
owner: Nico Janssen
status: draft
review_by: "2027-02-26"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-371: Resolve Mini-Game Performance Beacons That Return 404

- **Milestone / Epic:** M7 / M7-A
- **Size:** M
- **Product:** Shared
- **Owner:** One build session after founder approval of the telemetry plan
- **GitHub issue:** [#517](https://github.com/nickejanssen/arcwright/issues/517)
- **Target date:** After the first founder rehearsal, before using browser timing data for performance decisions

## Plain-English Summary

The local TV and phone screens sent mini-game timing measurements to an API address that returned 404. Gameplay continued. Those browser timings were not saved.

## Why This Matters

- Observed in the two-phone 1a run on 2026-11-26 (#354). The dashboard's `mini-game-kit/perf.ts` explicitly leaves the receiver to a follow-up after AW-253. The API has no route for the current beacon.
- The dashboard and Nightcap web share the pattern. These timing measurements are separate from engine play records and survey answers.

## Technical Scope

1. Agree whether these browser measurements are needed and where to receive them. If useful, define a game-agnostic payload, allowed sessions, and appropriate limits under architecture section 11.
2. Stop the browser from sending requests to an absent receiver. Keep game controls working if a timing report fails.

## Human Collaboration Contract

**Interaction profile:** Decision interview, then independent execution. The founder approves the telemetry decision and plan before code. Telemetry signal and auth changes are approval-gated.

## Acceptance Criteria

- [ ] A normal TV-and-phone mini-game sends no requests to an absent timing endpoint.
- [ ] If collection is approved, tests confirm the approved data reaches its destination and excludes case content. If deferred, tests confirm the disabled behavior.
- [ ] A failed timing report cannot block or alter gameplay.

## Tests/Verification

- Dashboard tests and a loopback mini-game run with network statuses recorded. Add API tests if a receiver is approved.

## Dependencies

- AW-253 and a founder telemetry decision.

## Must Not Do

- Do not add a telemetry signal, auth change, or dependency without plan approval. Keep case details out of GitHub (D-153).
