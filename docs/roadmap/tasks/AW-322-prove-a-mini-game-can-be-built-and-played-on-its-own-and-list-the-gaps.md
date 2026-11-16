---
id: productroadmap.roadmap.tasks.aw-322-prove-a-mini-game-can-be-built-and-played-on-its-own-and-list-the-gaps
namespace: product-roadmap
title: "AW-322: Prove A Mini-Game Can Be Built And Played On Its Own, And List The Gaps"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-119
tags: []
supersedes: []
---

# AW-322: Prove A Mini-Game Can Be Built And Played On Its Own, And List The Gaps

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex); the founder plays the result  
**Target date:** 2026-11-28

## Plain-English Summary

The founder's idea, 16 November 2026: a mini-game should be testable outside any specific game, so mini-games are quick to iterate on, and they should be easy to build. Much of this appears to exist already. This task proves what works by doing it once from start to finish, and lists what is missing. It builds nothing new.

## Why This Matters

- Session 1 needs story-wrapped mini-games after every beat (D-113), and each existing package still needs a story wrapper and a reward change (`docs/product/nightcap-status.md`). Fast iteration on a single mini-game shortens that work.
- Found in the repository on 16 November 2026, by file listing only, not run: a standalone playtest script (`nightcap-web/scripts/playtest-mini-game.mjs`, npm script `playtest:mini-game`), a mini-game kit (`nightcap-web/src/mini-game-kit/`), an authoring service (`engine/mini_games/authoring/`), an authoring guide (`docs/conventions/mini-game-authoring.md`), a mini-game skill (`docs/skills/arcwright-minigame/`) and spec 0080 on onboarding, preview and certification.
- Not verified: whether any of it still works, whether it runs without a case or a session, and how long building a new mini-game takes. The playtest script's default points at a Couch Race adaptation, which is the superseded design.
- Captured under D-119.

## Technical Scope

- Run one existing mini-game on its own, with no case loaded: first headless, then on a TV and two phones. Record the exact commands.
- Follow the authoring guide to add one trivial new mini-game. Record the time taken and every step that was unclear or broken.
- Say which parts are tied to Nightcap and which are game-agnostic. A mini-game package should be usable by any game; only its story wrapper belongs to a game.
- Write a short gap list. Each gap becomes a proposed task with a size, not a fix inside this task.
- Overlaps the inventory in AW-300; share findings instead of repeating them.

## Human Collaboration Contract

**Interaction profile:** Independent execution, then a decision interview on the gap list.

- Founder inputs: play the standalone mini-game once and say whether the loop is quick enough.
- Next gate: the founder reads the gap list and decides which gaps are worth closing before session 1.
- Approval: the founder's choices recorded on the issue.

## Acceptance Criteria

- [ ] One mini-game is played on its own on a TV and two phones, with no case loaded, and the commands are recorded on the issue.
- [ ] One trivial new mini-game is added by following the guide, with the time taken recorded.
- [ ] A gap list exists, with each gap sized and marked as tied to Nightcap or game-agnostic.
- [ ] The founder's decision on each gap is recorded.

## Tests/Verification

- `python -m pytest engine/tests -q` for the mini-game tests, and the standalone run seen on a real TV and two phones. Say separately what was run headless and what was seen in play.

## Dependencies

- None. Related: AW-300 (inventory), AW-303 (mini-games inside a session).

## Must Not Do

- Do not build a new framework, editor or test harness in this task.
- Timing, validation and scoring stay in Python; nothing in `engine/` may name Nightcap.
- Do not add a dependency without the founder's approval.
- Do not let this delay AW-303 or the first case.
