---
id: productroadmap.roadmap.tasks.aw-373-make-the-game-mini-game-and-playtest-toolkit-a-product
namespace: product-roadmap
title: "AW-373: Make The Game, Mini-Game And Playtest Toolkit A Product"
owner: Nico Janssen
status: draft
review_by: "2027-02-27"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-373: Make The Game, Mini-Game And Playtest Toolkit A Product

**Milestone / Epic:** M7 / M7-B  
**Size:** L (inferred; this task is the design and plan, later builds get their own tasks)  
**Product:** Shared (Arcwright tooling for every game; Nightcap is the first user)  
**Owner:** One planning session, then build sessions per approved piece  
**GitHub issue:** [#523](https://github.com/nickejanssen/arcwright/issues/523)  
**Target date:** To be scheduled by the founder. Inventory and proposal now (read-only, no code). The tooling freeze does not hold this work (D-159); each build still needs its plan approved

## Plain-English Summary

Arcwright already has tools for making and testing games, but they are scattered and only some agents can find them. The founder wants them turned into one practical, documented toolkit for the whole lifecycle of Arcwright games, mini-games and stories: brainstorm, create, port, configure, test, playtest, research and publish.

## Why This Matters

- Founder, 27 November 2026: "This needs to be a solid part of the product. Brainstorming, creating, porting, testing, playtesting, configuring, researching, publishing, of Arcwright games and minigames is important and we already have things built. We should make it productized, easy to use, documented with guides, etc. this will allow us to move faster and standardize the key featureset related to arcwright games, minigames, and playtesting any of the games. It should be intuitive, practical, amazingly useful, and improve our development lifecycle and the lifecycle of creating stories and the lifcycle of creating games."
- A standard toolkit means each new game, mini-game or case reuses the same steps instead of new one-off scripts (inferred).

## What Exists Today (verified 27 November 2026)

| Tool | Where | What it does |
|---|---|---|
| Mini-game skill | `docs/skills/arcwright-minigame/` (450-line guide plus `scripts/minigame_tool.py`) | Scaffold, validate, onboard, resume, status, playtest evidence for a mini-game package |
| Playtest harness skill | `docs/skills/arcwright-playtest-harness/` | Preflight, fixture, telemetry and evidence checks |
| Playtest steward skill | `docs/skills/arcwright-playtest-steward/` | Organises Playtest Lab work and routes it to the other playtest skills |
| Playtest research skill | `docs/skills/arcwright-playtest-research/` | Versions research instruments and reports tester findings |
| Playtest publishing skill | `docs/skills/arcwright-playtest-publishing/` | Builds and checks the Playtest Lab catalogue and static pages |
| Battle of Wits Wi-Fi room | `scripts/play_battle_of_wits.py` (PR #506) | Plays one mini-game on phones over Wi-Fi |

Gaps found (verified):

1. Codex sees these skills through `.agents/skills/`, but Claude Code has no command for them (`.claude/commands/` holds only doc-review, implement, review-pr and scribe), so Claude sessions do not offer them.
2. The `.agents/skills/` files are short pointers on purpose, so the missing `scripts/` and `agents/` folders are expected. Some pointer descriptions have drifted from their sources (corrected 27 November; see the proposal's evidence page).
3. There is no founder-facing guide that walks the whole lifecycle, and no single entry point that tells you which tool to use next.
4. Game-level and story-level steps (brainstorm a game, author or port a case, configure a version) have no matching skills yet (inferred from the inventory).

## Technical Scope

1. **Inventory and journeys (first, read-only).** Map every existing tool, script and doc above, plus related tasks (AW-312, AW-322, AW-349, AW-372). Write the end-to-end journeys for a game, a mini-game and a story, marking each step as built, partly built or missing.
2. **Proposal for founder approval.** One toolkit design: names, one entry point, one guide set, the same skills for Claude Code and Codex from one source, and an ordered list of build tasks, each sized and filed. AW-372 (`play` command) becomes the first piece.
3. **Builds** follow as separate tasks after approval.

## Human Collaboration Contract

**Interaction profile:** Decision interview, then creative collaboration. The planner interviews the founder one question at a time on the journeys and priorities before proposing. Plan approval and each build's approval are separate.

## Acceptance Criteria

1. An inventory and journey map in the repo, each step labelled built, partly built or missing, with file paths.
2. A toolkit proposal the founder approves in his own words, naming the entry point, the guides, how Claude Code and Codex share one source, and the ordered build tasks.
3. Each approved build piece filed as its own task and GitHub issue.
4. Nothing game-specific enters `engine/`; the toolkit works for any Arcwright game.

## Dependencies

- Related: AW-312 (where agent and skill definitions live), AW-372 (play command), AW-349 (browser mini-game port).

## Must Not Do

- No code in the inventory and proposal step.
- Do not read or quote files in `nightcap/cases/` (D-153).
- No new dependency, deploy or spending without approval.
