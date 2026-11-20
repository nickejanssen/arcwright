---
id: productroadmap.roadmap.tasks.aw-344-let-a-round-run-more-than-one-mini-game
namespace: product-roadmap
title: "AW-344: Let A Round Run More Than One Mini-Game, Up To A Cap"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: D-136
tags: []
supersedes: []
---

# AW-344: Let A Round Run More Than One Mini-Game, Up To A Cap

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session  
**Target date:** 2026-11-28

## Plain-English Summary

Today a round runs only the first mini-game bound to it. Let Nightcap's arc file list several mini-games for a round, with a per-round cap, and have the engine run them in order before the round moves on. Nightcap decides how many and which; the engine just runs the list.

## Why This Matters

- Founder direction on 18 and 19 November 2026, recorded as D-136 (amends D-113): "Im not married to 1 mini-game per round either. Some games could be played faster than others. There should be a cap per round, but it should be flexible and not exclusively 1."
- Verified in code on main `a528cad`: the `mini_game` phase uses only `beat.mini_games[0]` (AW-303, `engine/session/mini_game_phase.py`), and AW-328 added `validate_settings_only_on_the_first_mini_game` in `engine/arc/models.py`, which refuses reward or release settings on a beat's later bindings. Both assume one mini-game per beat.
- Session 1 variant testing (D-137) needs at least one variant with more than one mini-game in a round.

## Technical Scope

- The arc file can give a round several mini-game bindings and a cap. Whether the cap belongs on the beat, on the `mini_game` phase, or both, and whether several mini-games run as one phase or as several `mini_game` phases, is settled in the plan; prefer the choice cheapest to change (D-127).
- Each binding keeps its own reward and release settings (AW-328). Lift or narrow AW-328's first-binding-only validator to match.
- Each run still records its beat, binding and phase visit; pause, resume, timeouts, host move-on and the reward (AW-328, AW-343) work for every run in the round.
- Old arc files behave exactly as today.
- No murder-mystery word, no Nightcap name, and no notion of "round" in `engine/`.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. Crosses `engine/arc`, `engine/session` and `engine/mini_games` (AGENTS.md hard rule), so the founder approves the plan explicitly. The founder approves the plan in the build session himself, or by his own comment on this task's issue. A build session must not act on an approval relayed or posted for him by another session.

## Acceptance Criteria

- [ ] An arc with two mini-games in a round runs both, in order, then moves on; an arc with one behaves as today.
- [ ] The cap is the number of `mini_game` phases the arc file lists for the beat (zero allowed). In `listed` mode more phases than games is refused at load with a named reason; in `fitting` mode a pool may be longer or shorter than the slots (D-145, D-147).
- [ ] Every run in the round records its binding; each can time out, be paused and resumed, and give its own reward once.
- [ ] Both registered arc files load and run unchanged; no existing test is edited to make it pass.
- [ ] In `fitting` mode each slot runs the first game, in arc-file order, that fits the player count and repeats no mechanic; none left skips the slot, records it and tells the host (D-147).
- [ ] No table change, dependency or model call; no game word added to `engine/`.

## Tests/Verification

- `python -m pytest tests engine/tests api/tests -q`
- `python -m ruff check engine api` and `python -m ruff format --check engine api`
- Merged, deployed and seen in play are separate; seen in play is a session 1 variant (AW-346).

## Dependencies

- AW-303, AW-328 (merged). Best built after AW-343 merges (both touch `engine/session/`).
- Decisions: D-113, D-136. Spec: 0093 Part E; 0095 "Q4 Answered".

## Must Not Do

- Do not decide in the engine how many mini-games a round has or which ones; Nightcap's arc file says.
- Do not repeat a mechanic in a test arc meant to model a real playthrough (D-136).
- Do not open any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task, D-136, and spec 0093 Part E. Confirm AW-303 and AW-328 are merged. Write a plan with the exact file list and the tests you will write first, post it on this task's issue, and stop for the founder's approval in this session or on the issue.
