---
id: productroadmap.roadmap.tasks.aw-343-let-a-phone-read-back-its-mini-game-rewards
namespace: product-roadmap
title: "AW-343: Let A Phone Read Back Its Mini-Game Rewards"
owner: Nico Janssen
status: active
review_by: "2027-02-18"
sensitivity: internal
source: authored
x-scope-evidence: D-126
tags: []
supersedes: []
---

# AW-343: Let A Phone Read Back Its Mini-Game Rewards

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-11-28

## Plain-English Summary

When a player wins a mini-game they get one more investigation (D-126). Today the only way their phone learns this is a live message, and a live message can be missed: the phone was locked, the send failed, or the server restarted. Make the reward readable from the phone's menu read, from the rows already saved, so the phone always finds it, however it reconnects. The live message stays as the fast path.

## Why This Matters

- Found in the reviews of pull requests #417 (AW-328) and #419 (AW-338) on 2026-11-18. A reward message is marked `told` when it is queued. If its send fails ten times, or the API restarts before it is sent, the player is never told. The orchestrator then found a wider gap: the live event stream is in memory only, so a phone that is disconnected at that moment misses the message even when the send succeeds. The extra investigation itself is always saved.
- The founder's direction, 2026-11-18, in the orchestrator session. Asked whether to accept the lost message as cosmetic for session 1, he answered "fix, don't accept". Asked how, he chose "Readable from a route (Recommended)" over "Resend until confirmed" and "Both".
- It follows spec 0095 decision 5 (draft): every screen rebuilds itself from routes, because the event stream is lost on restart. Screen 12 (mini-game result) needs exactly this read.

## Technical Scope

- An engine read in `engine/session/` that returns, for one participant, their mini-game reward grants from the existing `budget_grant` decision rows with `source` `mini_game_reward`. For each: an ID that stays the same across reads, the run, the beat, the amount and the kind. It reads saved rows only.
- The player's menu read (`GET /v1/sessions/{session_id}/me/menu`, `api/routers/rounds.py`) also returns that list, through a thin handler. The build plan may propose a better-placed read, for example the round or holdings read, with a reason (D-127).
- The live `mini_game_reward_granted` event carries the same grant ID, so a phone can match the message to the read and never show one reward twice.
- No change to how the reward is given (AW-328), to the budget, or to the `told` flag's meaning, unless the plan shows the flag is no longer needed; then say so.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. Crosses `engine/session` and `api`, an AGENTS.md hard rule, so the founder approves the plan explicitly. The founder approves in the build session itself or by a comment on this task's issue; a build session must not act on an approval relayed by another session.

- Direction chosen by the founder on 2026-11-18 (see Why This Matters).
- Next gate: the build session writes a plan and stops for the founder's approval.

## Acceptance Criteria

- [x] After a mini-game ends, the rewarded player's menu read lists the reward with its amount; other players' reads do not list it.
- [x] The list is the same after every service object is rebuilt over the same database (the restart case), and the same when read twice.
- [x] A reward whose live message was never sent (publisher that fails, or none) is still in the read.
- [x] The live event and the read carry the same grant ID.
- [x] A player who won nothing gets an empty list; an arc with no reward setting behaves as before.
- [x] No other player's reward, and no case content, appears in any player's read; the shared screen gets nothing new.
- [x] Route handlers contain no rule; each calls one engine function.
- [x] No table change, no migration, no new dependency, no model call, no murder-mystery word added to `engine/`.

## Tests/Verification

- `python -m pytest engine/tests api/tests -q`
- `python -m ruff check engine api` and `python -m ruff format --check engine api`
- Merged, deployed and seen in play are separate. Seen in play: the founder TV run, when the phone's result screen (AW-332) reads it.

## Dependencies

- AW-328 (merged, `8ea4bc1`), AW-338 (merged, `21afcf3`).
- Decision: D-126. Spec: `docs/specs/0093-engine-spine-for-the-thin-version.md` "Q1 Answered" and Part D; `docs/specs/0095-screens-for-the-thin-version.md` (draft) decision 5 and screen 12.

## Must Not Do

- Do not add a table or column; the grant rows already hold what is needed.
- Do not compute the budget in the route or on the phone.
- Do not show anything new on the TV.
- Do not open any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md` and this task. Confirm AW-328 and AW-338 are merged. Write a plan with the exact file list and the tests you will write first, post it on this task's issue, and stop for the founder's approval. Wait for CI `verify` before reporting done.
