---
id: productroadmap.roadmap.tasks.aw-372-play-any-mini-game-on-wi-fi-from-the-mini-game-tool
namespace: product-roadmap
title: "AW-372: Play Any Mini-Game On Wi-Fi From The Mini-Game Tool"
owner: Nico Janssen
status: draft
review_by: "2027-02-27"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-372: Play Any Mini-Game On Wi-Fi From The Mini-Game Tool

**Milestone / Epic:** M7 / M7-B  
**Size:** S to M (inferred)  
**Product:** Shared (Arcwright mini-game tooling; Nightcap packages are the first users)  
**Owner:** One build session, after founder approval of its plan  
**GitHub issue:** [#520](https://github.com/nickejanssen/arcwright/issues/520)  
**Target date:** To be scheduled by the founder. Recommended after the fixes the 1 December test needs (D-156)

## Plain-English Summary

Today Battle of Wits has its own launcher, `python -m scripts.play_battle_of_wits` (PR #506), separate from the mini-game tool every package already uses (`docs/skills/arcwright-minigame/scripts/minigame_tool.py`: scaffold, validate, onboard, status, playtest). The founder asked for one command set for all mini-game work: `minigame_tool.py play <package>` should start the same Wi-Fi room for any package, with one set of documentation.

## Why This Matters

- Founder, 27 November 2026: one command suite is more scalable, keeps the mini-game interaction logic in one place, and needs one set of documentation.
- Each new package would otherwise need its own launcher script and its own instructions (inferred).

## Technical Scope

1. Add a `play` command to `minigame_tool.py` that runs the Wi-Fi room for a package path, reusing the server in `scripts/play_battle_of_wits.py` with the package-specific parts (package path, game id, version check, bank error text) taken from the package itself.
2. Make the browser room generic: results and standings come from the package's resolved result, not Battle of Wits code. Package-specific presentation stays in the package's own renderer.
3. Keep `python -m scripts.play_battle_of_wits` working as a short alias, or remove it with the README updated in the same change.
4. One documentation section in the mini-game skill covering every command, including `play`.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. The founder approves the plan in his own words.

## Acceptance Criteria

1. `python docs/skills/arcwright-minigame/scripts/minigame_tool.py play nightcap/mini_games/battle-of-wits` starts the same room as PR #506, with the same tests passing.
2. A second package with a server-side resolver starts with the same command, or the plan names exactly what a package must provide and why the second one cannot yet.
3. Server-only files never reach the browser, for every package (the PR #506 tests, generalised).
4. `engine/` gains no reference to Nightcap or any game title.

## Tests/Verification

- The PR #506 room tests, run against the new command.
- `npm test --prefix dashboard`, `pytest`, and all six pull request checks; an independent review before merge.

## Dependencies

- AW-348 (PR #506).

## Must Not Do

- No new dependency, schema change or migration without approval.
- Do not read or quote files in `nightcap/cases/`.
