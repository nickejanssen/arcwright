---
id: productroadmap.roadmap.tasks.aw-356-build-the-version-arc-setups-and-the-group-run-sheet
namespace: product-roadmap
title: "AW-356: Build The Version Arc Setups (1a To 1e) And The Group Run Sheet"
owner: Nico Janssen
status: active
review_by: "2027-02-20"
sensitivity: internal
source: authored
x-scope-evidence: D-146
tags: []
supersedes: []
---

# AW-356: Build The Version Arc Setups (1a To 1e) And The Group Run Sheet

**Milestone / Epic:** M7 / M7-C  
**Size:** M  
**Product:** Nightcap (arc file and playtest operations)  
**Owner:** A build session for the arc setups; the founder and an orchestrator for the run sheet  
**Target date:** 1a by 2026-12-01, 1b by 2026-12-05, 1c, 1d and 1e by 2026-12-15

## Plain-English Summary

Turn each version sheet into a real arc setup (which mini-games run in which round, the per-round cap, `listed` or `fitting`), and write the run sheet the founder uses: which group plays which version on which case, the recruiting screener and the host card.

## Why This Matters

- AW-346's sheets are only paper until each is an arc file the engine can run. Each setup is arc-file only where its mechanics exist (verified by reading: AW-344 merged the slots and `mini_game_pick`).
- The run order (two groups, matched order, reversed in a second wave) and the screener are operations the founder needs before inviting friends.

## Technical Scope

- One arc setup per version (1a to 1e), in Nightcap's arc folder (Nightcap configuration only; nothing in `engine/` names a version). 1a uses `listed`; 1b to 1e use `fitting`.
- 1a's final race runs back to back with Last Call: a last `mini_game` phase before the `commit` phase (arc file only).
- A solo run does not count against no-repeat (founder answer 9): confirm AW-345 implements this; if it does not, raise it there.
- The run sheet and screener: a plain page for the founder under `docs/design/session-1-variants/`, plus the one-page host cheat card (shared with AW-308).
- Not in this task: building the mechanics (AW-337), the survey tags (AW-354) and the questions (AW-355).

## Human Collaboration Contract

**Interaction profile:** Independent execution for the arc setups after plan approval; facilitated live operation for the run sheet (the founder chooses the groups).

**Required founder inputs:** approval of the plan; which friends form each group (private knowledge).

**Current phase and next gate:** filed; next gate is the plan.

**Outstanding owner actions:** the founder names the groups and approves the screener questions.

## Acceptance Criteria

- [ ] Each version has an arc setup that loads and runs a headless game at 2 and at 4 players, with no model call deciding anything.
- [ ] 1a repeats Battle of Wits; 1b to 1e never repeat a mechanic.
- [ ] 1a's final race runs immediately before Last Call, and its standing feeds the existing tie-break.
- [ ] The run sheet names the group, case and version for each playthrough, and the screener is approved.

## Tests/Verification

- The headless full-game test at 2 and 4 players for each setup; `python -m pytest engine/tests -q`.

## Dependencies

- AW-337, AW-344 (merged), AW-345, AW-305, AW-346, AW-354 and AW-355.
