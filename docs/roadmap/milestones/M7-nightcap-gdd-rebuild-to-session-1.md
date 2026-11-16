---
id: productroadmap.roadmap.milestones.m7-nightcap-gdd-rebuild-to-session-1
namespace: product-roadmap
title: "M7: Nightcap GDD Rebuild To Session 1"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
tags: []
supersedes: []
x-scope-evidence: D-112
---

# M7: Nightcap GDD Rebuild To Session 1

**Build-order coverage:** none (rebuild of the experience layer to the Master GDD, plus the harness work it depends on)
**Target date:** 2026-12-13

## Summary

M7 takes Nightcap from the superseded Couch Race build to a thin, complete version of the Master GDD game, played by friends at the founder's house. It was added in the November 2026 reset (D-112). It runs before M6 finishes: M6's sessions become sessions 1 to 3 of this plan, and AW-299 rewrites the M5 and M6 exit criteria to match.

Scope, dates and the cut order live in [nightcap-status.md](../../product/nightcap-status.md). Spec 0092 is the rebuild plan. The founder approved it for the thin version on 2026-11-15 (D-123, #303), which permits the inventory (AW-300) only. Building still waits on the three combined specs (AW-302), each with its own approval. The first, the engine spine (spec 0093), was approved on 2026-11-16 (D-124).

## Epics

- [M7-A: Development Harness And Tracker Readiness](../epics/M7-A-development-harness-and-tracker-readiness.md)
- [M7-B: Thin Nightcap Rebuild](../epics/M7-B-thin-nightcap-rebuild.md)
- [M7-C: Session 1 Readiness And Run](../epics/M7-C-session-1-readiness-and-run.md)

## Exit Gate

- The specialist agents answer from a worktree session and the ten-question check is scored.
- A headless session completes at two and at four players with no AI call deciding anything.
- The founder has played the game start to finish on a TV with two phones.
- Session 1 has been played by two to four friends at the founder's house and its debrief is recorded.
- The approved pass bar is read against the result: median fun at least 4 of 5, median detective feeling at least 4 of 5, at least half answer yes to playing again, at least three in four finish.

A played session is not a passed session. If fun or detective feeling scores below 3, the next step is the core loop, not more features.

## Slip Rules

- No founder TV run by 5 December 2026: session 1 moves to 19 or 20 December.
- Case not approved by 28 November 2026: the same slip.
- Build sessions run short: cut in this order. The Postmortem becomes fixed text; three mini-games become two; three beats become two; the story-tool importer moves to after session 1.
