---
id: productroadmap.roadmap.tasks.aw-360-keep-a-held-finding-from-covering-the-mini-game
namespace: product-roadmap
title: "AW-360: Keep A Held Finding From Covering The Mini-Game On The Phone"
owner: Nico Janssen
status: draft
review_by: "2027-02-21"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-360: Keep A Held Finding From Covering The Mini-Game On The Phone

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Nightcap  
**Owner:** One Codex build session, after founder approval of its plan  
**GitHub issue:** [#483](https://github.com/nickejanssen/arcwright/issues/483)  
**Target date:** before the founder's end-to-end test on 1 December 2026 (D-149)

## Plain-English Summary

If a player's investigation finding is still being held when a mini-game starts, their phone shows the finding instead of the game until they tap OK. The finding never expires, so a player who misses OK can lose the whole mini-game. The game must stay playable.

## Why This Matters

- Found while merging pull request #478 and recorded on #477. It is the same pattern as the hidden Ready button fixed there.
- Version 1a is built around mini-games, so a phone stuck on an old finding hurts the founder's first test.

## Technical Scope

All in `dashboard/`.

1. `dashboard/src/screens/round/MiniGamePhone.tsx` reads `peekHeldFinding(sessionId)` once at mount and shows it in place of the game.
2. Show the game at all times. Show a held finding beside or above it, and drop it when `heldFindingMsLeft` reaches zero, as `EyesUpPhone.tsx` does since pull request #478.
3. Tapping OK still clears the finding early.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. The founder approves the plan in his own words, in the build session or in his own issue comment.

## Acceptance Criteria

1. With a held finding, the mini-game is mounted and playable from the first render.
2. The finding disappears when its hold ends, with no tap and no reload.
3. OK clears it early and it does not return after a re-render or under React StrictMode.
4. A finding whose hold has already ended is not shown at all.
5. Each new test fails on `main` before the change and passes after it.

## Tests/Verification

- `npm test --prefix dashboard`, `npm run typecheck --prefix dashboard`, `npm run build --prefix dashboard`.
- All six pull request checks pass, and every review thread is answered and resolved.

## Dependencies

- AW-332 part B (pull request #480) and AW-359 (pull request #478), both merged.

## Must Not Do

- Do not change `engine/`, `api/`, `nightcap/`, `sdk/`, `dashboard/src/mini-games/client.ts`, `dashboard/src/shell/copy.ts` or `package.json`.
- Do not change the notebook. Its grouping matches spec 0095 screen 9.
- Do not change how long a finding is held.

## Kickoff Prompt

> Implement AW-360 (#483). Read `AGENTS.md`, `HANDOVER.md` and this task. Post the plan on the issue and wait for the founder's own approval. Tests first. Do not merge.
