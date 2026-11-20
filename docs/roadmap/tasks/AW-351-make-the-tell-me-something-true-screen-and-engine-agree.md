---
id: productroadmap.roadmap.tasks.aw-351-make-the-tell-me-something-true-screen-and-engine-agree
namespace: product-roadmap
title: "AW-351: Make The Tell Me Something True Screen And The Engine Agree On The Step And The Spotlight"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: D-139
tags: []
supersedes: []
---

# AW-351: Make The Tell Me Something True Screen And The Engine Agree On The Step And The Spotlight

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Nightcap (the package screen) with one small engine read  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-11-30, before AW-332 builds screens 10 to 12

## Plain-English Summary

After AW-347 the API sends the Tell Me Something True screen the real step of the game and its generated title. The screen still cannot use them. It never reads the step, and it waits for a spotlight line (`spotlight_label`) that the engine has never sent. So on the live game it shows its fallback text for the input step, the spotlight and the scoreboard. Make the screen and the engine agree on what is sent and what is drawn.

## Why This Matters

- Found on 2026-11-19 by the AW-347 planning session, recorded in its plan on issue #440 (finding 6, Question 1). The founder answered option A: reword AW-347's first criterion to what the API can truthfully do, and file this task before AW-332 builds screens 10 to 12.
- VERIFIED at main `907096d`: the screen reads `runtimeState.spotlight_label` and `presentation.title`, `prompt`, `true_label`, `lie_label` (`nightcap/mini_games/tell-me-something-true/client/renderer.ts`, lines 70 to 79 and 397). It never reads `runtimeState.phase`. Its spotlight handler reads `spotlight_label` from the event (line 450), but the engine's spotlight event carries `target_character_id`, `eligible_voter_ids`, `phase` and `deadline` and no label (`engine/mini_games/plugins/_social_truth_bluff.py`, lines 441 to 450). The word `spotlight_label` appears nowhere in `engine/` or `api/`. The screen was written against a preview-era data shape the real engine never produced.
- Spec 0095 Part K says no package's screen code changes in AW-347, so this is its own task. D-136 asks for more mechanics; each needs the same agreement between screen and engine.

## Technical Scope

- Plan with a recommendation, then choose one of:
  - **A.** The screen reads `runtimeState.phase` and the spotlight target, and draws the step and a spotlight line from them. Package-side change only.
  - **B.** The engine sends a spotlight label the screen already expects. Needs a generic, game-agnostic way to name the spotlighted player; no game-specific function in `engine/` or `api/`.
- Keep the privacy rule from AW-347: the shared screen never gets a player's private entries or the phone-only prompt.
- Extend `dashboard/tests/mini-game-live-reply.test.ts` so the recorded replies in `dashboard/tests/fixtures/mini-game-live-replies.json` show the real step and a spotlight line on the shared screen.
- If the fix changes a package definition or crosses engine modules, stop and ask.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval.

**Classification rationale:** An engineering mismatch with a testable result. If choice A or B changes what players see in a way that is a taste call (wording of the spotlight line), that part is the founder's.

**Required founder inputs:** approval of the plan, in the build session or by his own comment on this issue. A build session must not act on an approval relayed by another session.

**Current phase and next gate:** filed; next gate is the plan.

**Outstanding owner actions:** none.

## Acceptance Criteria

- [ ] With the recorded live replies, the Tell Me Something True screen mounted through the dashboard loader shows its real step (input, spotlight, scoreboard) and, in the spotlight step, a line naming the spotlighted player, instead of fallback text.
- [ ] The shared screen still gets no player's private input and no phone-only prompt (the AW-347 privacy test passes unchanged).
- [ ] No new game-specific function is added under `api/` or `engine/`.
- [ ] `verify` and the other checks pass; dashboard tests pass.

## Tests/Verification

- `python -m pytest engine/tests api/tests -q`
- `python -m ruff check engine api` and `python -m ruff format --check engine api`
- `npm run typecheck --prefix dashboard` and `npm test --prefix dashboard`
- Merged and verified in CI only until the founder TV run; nothing is deployed.

## Dependencies

- AW-347 (#440) merged: it adds the `runtime_state` and `presentation` fields and the recorded replies this task builds on.
- Blocks AW-332 (#435) screens 10 to 12.

## Must Not Do

- Do not send a run's saved live state unfiltered to any reader.
- Do not open any real case file under `nightcap/cases/`.

## Kickoff Prompt

> Run `/implement AW-351`. Read `AGENTS.md`, `HANDOVER.md`, this task and the AW-347 plan on issue #440 (finding 6). Write the plan with a recommendation between A and B, post it on this issue, and stop for the founder's own approval. After approval, extend the Node test first. Wait for CI `verify` before reporting done. Do not merge.
