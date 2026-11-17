---
id: productroadmap.roadmap.tasks.aw-337-give-small-groups-a-mini-game-that-fits
namespace: product-roadmap
title: "AW-337: Give Small Groups A Mini-Game That Fits"
owner: Nico Janssen
status: active
review_by: "2027-02-16"
sensitivity: internal
source: authored
x-scope-evidence: D-112, D-126
tags: []
supersedes: []
---

# AW-337: Give Small Groups A Mini-Game That Fits

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Nightcap  
**Owner:** Founder decision first, then one AI build session  
**Target date:** 2026-11-27

## Plain-English Summary

No mini-game in the repository can be played by two or three people. Decide how many players session 1 and the TV walkthrough will have, then make sure one mini-game fits that number.

## Why This Matters

- Verified on 2026-11-16 at commit `83795a5`, from each package's definition file under `nightcap/mini_games/`: Crime Scene Smash, Scene Sweep and Tell Me Something True each need 4 to 8 players. Evidence Locker 402 needs exactly 1.
- The walkthrough of the current build (AW-301) uses a TV and two phones. With two players, no mini-game can start.
- Reported by the screens spec session (pull request #393), not checked by the parent session: only Tell Me Something True has a working screen, and it is still a draft.
- Unknown: how many players session 1 will have. If it is four or more, the gap only affects the walkthrough and small test runs.
- Filed under D-119 on 2026-11-16.

## Technical Scope

- Record the player count for session 1 and for the walkthrough.
- If either is below four: choose one mini-game and make it work at that count, or state that the walkthrough skips the mini-game and say what that leaves unseen.
- Any change to a mini-game's rules for a smaller group is a design change and needs the founder's approval before code.

## Human Collaboration Contract

**Interaction profile:** Decision interview, then independent execution after plan approval.

- The founder answers one question first: how many players at session 1, and how many at the walkthrough.
- A mini-game's feel at a new player count is a matter of founder taste. The session proposes one low-cost option and stops.

## Acceptance Criteria

- [ ] The session 1 player count and the walkthrough player count are recorded in `docs/product/nightcap-status.md` or a decision row.
- [ ] One mini-game starts, runs and returns to the story at the walkthrough's player count, or the walkthrough plan says plainly that it skips the mini-game.
- [ ] No mini-game releases case information (D-126).

## Tests/Verification

- `python -m pytest engine/tests -q`
- `python scripts/checks/scope_evidence_check.py`

## Dependencies

- AW-303, which makes a mini-game start, time out and return inside a session.
- Related: AW-301 (the walkthrough), AW-322 (prove a mini-game can be built and played on its own), spec 0095 open question on how many mini-games need screens.

## Must Not Do

- Do not open or read any real case file.
- Do not change a mini-game's rules without the founder's approval.
- Do not build a new mini-game when changing a player-count setting on an existing one would do.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md` and this task. Task AW-337: first ask the founder how many players session 1 and the walkthrough will have, one question, with options and a recommendation. Then propose the cheapest way for one mini-game to fit that count. Write a plan and stop for founder approval.
