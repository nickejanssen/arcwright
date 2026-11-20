---
id: productroadmap.roadmap.tasks.aw-347-send-mini-game-renderers-the-state-they-read
namespace: product-roadmap
title: "AW-347: Send Mini-Game Package Screens The State They Read, Safely Per Audience"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: D-139
tags: []
supersedes: []
---

# AW-347: Send Mini-Game Package Screens The State They Read, Safely Per Audience

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-11-28, before AW-332 builds the mini-game screens

## Plain-English Summary

A mini-game package draws its own screens from two pieces of data: its live game state and its presentation settings. The API's mini-game reply does not send either, so a package screen mounted in the dashboard against the live game shows only its placeholder text and cannot tell which step of the game it is on. Make the reply carry what package screens read, filtered so that each screen gets only what its audience may see.

## Why This Matters

- Found on 2026-11-19 by the AW-329 plan session and recorded in its plan on issue #432 (finding 2). The founder approved that plan with its recommendation B: copy the loader as it is, and file this gap as its own task.
- Verified by the orchestrator on main `ab763ae`: the Tell Me Something True package screen reads `state.presentation` and `state.runtimeState` (`nightcap/mini_games/tell-me-something-true/client/renderer.ts`, functions `presentation` and `runtime`). The copied loader fills them from `presentation` and `runtime_state` in the reply (`nightcap-web/src/mini-games/client.ts:201-218`). The reply type `MiniGameRunResponse` (`api/schemas/__init__.py`) sends `mechanic_type` and `phase_state`, and neither of the two fields.
- Spec 0095 decided that each package draws its own screens through the copied loader (Part K, decision 2), and D-136 asks for several new mechanics. Every one of them needs this data path. AW-332 (round screens, screens 10 to 12) cannot show a working mini-game without it.
- Also seen while checking: `api/routers/mini_games.py` holds code for one named game (`_tmst_runtime_state`, `_build_tmst_phase_state`, `_scene_sweep_runtime_state`). Game-specific logic in the API cuts against keeping Arcwright game-agnostic. This task does not have to remove it, but the plan must not add more of it, and should say whether a generic path lets it go later (AW-274's area).

## Technical Scope

- Give the active-run reads (`GET /v1/sessions/{id}/mini-games/active` with a player's sign-in, and the shared-screen display read) the run's live state and presentation in one generic shape that works for any package, not per game.
- **Privacy is the core of this task.** A run's saved live state can hold every player's private input. The engine must decide what each audience may see (the shared screen, one player, the host), using the package's declared audiences or a package rule, before anything leaves the API. The TV must never receive a player's private input, and one player must never receive another's. No filtering in TypeScript.
- Keep the existing `phase_state` and `mechanic_type` fields working, so the old dashboard screens keep running until AW-330 and AW-332 replace them.
- The plan names the exact files. Expected: `api/schemas/__init__.py`, `api/routers/mini_games.py`, and possibly one engine read in `engine/mini_games/` for the audience filter. If it needs a change across engine modules, a table change, or a change to any package's definition or screen code, stop and ask.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval.

**Classification rationale:** An engineering data path with testable privacy rules. No taste or gameplay choice. If the plan finds that a package must declare which parts of its state are public, and that needs a package format change, that is a decision for the founder.

**Required founder inputs:** approval of the plan, in the build session or by his own comment on this issue. A build session must not act on an approval relayed by another session.

**Current phase and next gate:** plan approved by the founder in the build session on 2026-11-19 (Question 1 answered A); build in progress. Follow-up filed as AW-351 (#457).

**Outstanding owner actions:** none.

## Acceptance Criteria

- [ ] The replies a real route sends, recorded at the input, spotlight and scoreboard steps, reach the Tell Me Something True package screen unchanged through the dashboard loader: the real step is in the screen's state (`runtimeState.phase`), and the generated title from `presentation` replaces the screen's fallback title. (Reworded on 2026-11-19, founder's option A on #440: the screen does not yet read the step or draw a spotlight line, so showing them is AW-351.)
- [ ] A privacy test runs a mini-game where each player submits a marker, then reads the active run as the shared screen, as each player and as the host: the shared screen gets no player's marker, and no player gets another player's marker.
- [ ] The old `phase_state` and `mechanic_type` fields are unchanged; existing mini-game and API tests pass with no assertion weakened.
- [ ] No new game-specific function is added under `api/` or `engine/`; the new shape works for any package.
- [ ] Route handlers stay thin; the audience rule lives in the engine.
- [ ] `verify` and the other checks pass.

## Tests/Verification

- `python -m pytest engine/tests api/tests -q`
- `python -m ruff check engine api` and `python -m ruff format --check engine api`
- `scripts/checks/provider_leak_check.py`
- `npm test --prefix dashboard` once AW-329 has merged
- Merged and verified in CI only until the founder TV run; nothing is deployed.

## Dependencies

- AW-329 (#432) merged, so the loader test can run in `dashboard/`. The Python half can be planned at once.
- Blocks AW-332 (#435) screens 10 to 12. AW-351 (the screen and engine mismatch) follows it and also blocks those screens.

## Must Not Do

- Do not send a run's saved live state unfiltered to any reader.
- Do not change any file under `nightcap/mini_games/`, `nightcap-web/` or `sdk/`.
- Do not open any real case file under `nightcap/cases/`.

## Kickoff Prompt

> Run `/implement AW-347`. Read `AGENTS.md`, `HANDOVER.md`, this task, the AW-329 plan on issue #432 (finding 2) and spec 0095 Part K and decision 6. Write the plan with the exact files, post it on this issue, and stop for the founder's own approval. After approval, write the privacy test first. Wait for CI `verify` before reporting done. Do not merge.
