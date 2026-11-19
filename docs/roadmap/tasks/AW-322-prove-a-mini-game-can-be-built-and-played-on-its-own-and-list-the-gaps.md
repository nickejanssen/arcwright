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

## Findings So Far (2026-11-15, headless half only)

Run from a worktree with no case, no session, no database and no model call. Nothing was seen on a TV or a phone, and no new mini-game was added.

- `python -m pytest engine/tests/test_mini_game_models.py engine/tests/test_mini_game_onboarding.py engine/tests/test_mini_game_resolution.py engine/tests/test_mini_game_runtime.py engine/tests/test_mini_game_runtime_aw252.py engine/tests/test_minigame_tool.py -q`: 93 passed, 1 skipped (needs a database), 28 seconds.
- `node nightcap-web/scripts/playtest-mini-game.mjs --session aw322-check --scenario happy-path --players 2 --json`: exit 0. It mounted the mini-game's screen code for phone, shared display and host in a simulated browser and recorded two phone submissions.
- **Gap 1, game-agnostic.** The standalone script is a preview, and says so (`NON_AUTHORITATIVE_PREVIEW`). It steps through a fixed list of states written in JavaScript. The Python rules, clock and scoring do not run. So today there is no way to play a mini-game on its own with the real rules.
- **Gap 2, game-agnostic.** With `--serve-ms` the script serves one page that prints the evidence as text. It is not a screen a person can play on a TV or a phone.
- **Gap 3, tied to Nightcap.** The script reads packages only from `nightcap/mini_games/`, and its default adaptation is the superseded Couch Race one.
- The script needs the repository's root `node_modules` (esbuild and happy-dom), which a fresh worktree does not have; it worked here only because Node found the main checkout's copy.

Still to do: the TV and two phones run, the trivial new mini-game with its time, sizing each gap, and the founder's decision on each.

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

## Standalone follow-through

Use a direct mobile or desktop browser launch with Nightcap offline as the founder’s live target. Keep the existing TV check as a surface-specific observation. Record what the current tools can establish, the missing step and its owner; close discovery on documented gaps without waiting for downstream implementation. [AW-348](https://github.com/nickejanssen/arcwright/issues/443) owns the live player; [AW-349](https://github.com/nickejanssen/arcwright/issues/444) owns the port and cross-experience proof.

## Dependencies

- None. Related: AW-300 (inventory), AW-303 (mini-games inside a session).

## Must Not Do

- Do not build a new framework, editor or test harness in this task.
- Timing, validation and scoring stay in Python; nothing in `engine/` may name Nightcap.
- Do not add a dependency without the founder's approval.
- Do not let this delay AW-303 or the first case.
