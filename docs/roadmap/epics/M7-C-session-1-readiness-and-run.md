---
id: productroadmap.roadmap.epics.m7-c-session-1-readiness-and-run
namespace: product-roadmap
title: "M7-C: Session 1 Readiness And Run"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
tags: []
supersedes: []
x-scope-evidence: D-112
---

# M7-C: Session 1 Readiness And Run

**Milestone:** M7  

## Plain-English Summary

Get from a build that passes headless tests to friends playing at the founder's house: the founder's own TV run, the preflight, and session 1 itself.

## Why This Matters

A scheduled session is not a passed session. Only real players can say whether the game is fun and whether they feel like detectives.

## Tasks

- [AW-308: Session 1 Preflight: Reconnect, Private Information And The Host Cheat Sheet](../tasks/AW-308-session-1-preflight-reconnect-private-information-and-the-host-cheat-sheet.md)
- [AW-365: Keep Phones Updating During The Mini-Game When The Live Stream Is Unavailable](../tasks/AW-365-keep-phones-updating-during-the-mini-game-without-a-live-stream.md)
- [AW-366: Stop The Dashboard Dev Server Serving Case Files To Phones](../tasks/AW-366-stop-the-dashboard-dev-server-serving-case-files.md)
- [AW-367: Start A Case 1 (1a) Game With One Command That Survives One Part Crashing](../tasks/AW-367-start-a-case-1-game-with-one-safe-command.md)
- [AW-368: Close Two Ways A Live Game Can Get Stuck: Half-Made Seats And Resume](../tasks/AW-368-close-two-ways-a-live-game-can-get-stuck.md)
- AW-240 (existing task; see `docs/roadmap/index.json`)
- AW-241 (existing task; see `docs/roadmap/index.json`)
- AW-242 (existing task; see `docs/roadmap/index.json`)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- Any open decision is recorded before dependent work starts.

## Dependencies

- Parent milestone: M7
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not bypass the architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.
