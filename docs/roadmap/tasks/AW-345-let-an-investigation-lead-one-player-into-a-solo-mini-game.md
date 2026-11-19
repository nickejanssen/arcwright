---
id: productroadmap.roadmap.tasks.aw-345-let-an-investigation-lead-one-player-into-a-solo-mini-game
namespace: product-roadmap
title: "AW-345: Let An Investigation Lead One Player Into A Solo Mini-Game"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: D-136, D-137
tags: []
supersedes: []
---

# AW-345: Let An Investigation Lead One Player Into A Solo Mini-Game

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** Founder design interview first, then one AI build session  
**Target date:** 2026-12-01

## Plain-English Summary

When a player investigates something particular, they can stumble into a mini-game that only they play, privately on their phone. Nightcap's case and arc files decide which investigations lead to one and what it gives; the engine starts and runs it for that one player.

## Why This Matters

- Founder direction on 19 November 2026, recorded as D-136: "Some mini-games could also only be for one player if they stumble onto something other players havent." He asked for it in session 1, as an optional variant to A/B test (D-137).
- Verified in code on main `a528cad`: only a round's `mini_game` phase starts a mini-game, for every player; nothing lets a choice start one, and no run is limited to one player.
- It rewards the curiosity the investigation loop is built on, and fits D-128 (private thinking on the phone).

## Technical Scope

- Design first (founder interview, one question at a time): what a solo mini-game gives (a concept, an extra investigation, or nothing but the experience); whether it uses the player's investigation budget; what the TV and the other phones show meanwhile (D-134: the TV stays quiet; D-128: private wins); whether a solo mini-game can pause or delay the round's clock.
- Then the engine: an authored trigger on an investigation opportunity (Nightcap's case or arc file) starts a mini-game run for one participant only. Its events go to that player only, it times out by itself, and it is recorded in the play record (D-115).
- Mechanics may suit one player (Evidence Locker #402 declares exactly one); AW-337 owns which mechanics exist.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration and decision interview for the design, then independent execution after plan approval. Crosses engine modules (hard rule). The founder approves the plan in the build session himself, or by his own comment on this task's issue. A build session must not act on an approval relayed or posted for him by another session.

## Acceptance Criteria

- [ ] The founder's design answers are recorded on this task's issue before code.
- [ ] Choosing the triggering investigation starts one private run for that player; nobody else receives its events or content.
- [ ] The run ends on its own clock and returns the player to the round; the round's own phases are not broken by it.
- [ ] An arc with no solo trigger behaves as today; no existing test edited to pass.
- [ ] No table change, dependency or model call; no game word added to `engine/`.

## Tests/Verification

- `python -m pytest tests engine/tests api/tests -q`
- A privacy test that scans every event of a run with a solo mini-game.
- Seen in play: a session 1 variant (AW-346).

## Dependencies

- AW-303, AW-325 (merged); AW-344 if a solo run shares its code. AW-337 for the mechanic.
- Decisions: D-128, D-134, D-136, D-137. Spec: 0093 Parts D and E; 0095 "Q4 Answered".

## Must Not Do

- Do not give case information that another player cannot also reach by investigating (case fairness, spec 0093 Part A); the plan says how.
- Do not start building before the design answers are recorded.
- Do not open any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task and D-136. Interview the founder one question at a time on the design points in Technical Scope, with options and a recommendation, and record each answer on this task's issue. Then write a plan, post it on the issue, and stop for approval.
