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

## Proposed Completed-Result Design

**Status: Design approved; implementation plan and durable recording pending.** On 2026-11-21 the founder
asked to expand PR #472 to design a privacy-safe completed-run read and result
lifecycle. Asked how the game should proceed, the founder selected: "Pause for
results (Recommended): show the result, then continue when players are ready or a
clock expires." After reviewing the complete design, including the proposed
15-second initial value and cross-module and arc schema changes, the founder
answered "Approve!" on 2026-11-21. This approves the design, not an
implementation plan or an exception to the decision-log restriction.

### Problem and scope

The recorded scoreboard reply is seeded as an active run. The real mechanic
completes the run as it produces its scoreboard, and the active-run route excludes
completed runs. A reload therefore cannot recover that result. Spec 0095 screen
10 requires the standing, and its decision 5 requires screens to rebuild after a
reconnect. Spec 0093 Part E currently says every ended run immediately ends the
mini-game phase. This proposal changes that rule for runs with a result hold; it
does not change scoring, rewards, submissions, or any package definition.

**Approaches considered:** (1) A saved result hold controlled by the engine,
then advance on all-ready or deadline. Recommended because a reload and multiple
consecutive games have one authoritative answer. (2) Keep advancing immediately
and offer a history read. This preserves current phase rules but does not give the
group time to see the result before the next step. (3) Hold only in the browser.
This does not survive a restart or synchronize clients. The founder chose the
result-hold direction and subsequently approved the details below.

### Proposed lifecycle

- A mini-game visit remains the same beat and phase visit while its saved state
  changes from playing to a result hold. The engine records the hold and its
  deadline durably, and binds it to that visit's run. It does not restart, rescore,
  or grant the reward twice on repeated ticks, reconnects, or retries.
- Completed and timed-out runs with a valid saved standing enter the hold.
  Cancelled runs and runs without a valid standing skip it and continue under the
  existing fallback rules. The precise fallback presentation is not changed here.
- Only during the hold may seated players mark that visit ready. The hold ends
  when every eligible player is ready, its deadline expires, or the host uses the
  existing move-on control. A stale ready request for another visit is ignored
  and returns the current state, matching the existing ready route.
  The normal next phase starts once. Pause and resume freeze and restore the hold
  clock and preserve its ready marks.
- Snapshot the eligible set at hold entry using the existing round rule: human
  player seats, including a player who holds the host role, excluding AI and a
  standalone host seat. A disconnected player remains eligible until the clock
  or host move-on. With no eligible players there is no valid standing, so no
  hold starts; a malformed existing hold with an empty set must not pass the
  all-ready check. Reject ready submissions from anyone outside that set.
- A valid standing has at least one nonempty tier, names each ranked human seat
  exactly once, contains no other seat and permits ties. Reject malformed tiers,
  duplicates and omissions instead of exposing or silently repairing them. This
  follows `build_standing`, which already includes unranked eligible seats.
- Give each opted-in mini-game phase a positive authored result-hold duration.
  Phases without this setting retain the existing immediate-advance behavior.
  The Nightcap phased arc must opt in so the requested hold actually runs. The
  initial value is **15 seconds**, adjustable after playtesting and not a claim
  about ideal pacing. The founder approved this initial value with the design.
  This adds an arc phase schema
  field and is a separate approval-gated schema change, not a package definition
  change. No database table or migration is proposed.

### Proposed read and screens

- Add a generic shared-result read for the current session visit. The engine
  identifies the current hold and its bound run by session, beat and phase visit;
  it never selects a run solely because it is the latest. When no hold is current,
  or the run is missing, ambiguous, from another session, or has an invalid
  standing, return no result. The existing active-run endpoint keeps its meaning.
- Construct a public response from an explicit allowlist: run and game identity
  for routing, hold identity and deadline, and validated standing tiers containing
  only participants in the session. The display resolves participant IDs to
  public lobby names and never renders internal IDs. Do not return raw saved
  state, outcome, submissions, statements, truth declarations, phone prompts,
  private rewards, behavioral signals, or unrestricted presentation. A phone's
  own reward remains on its existing authenticated menu read.
- The dashboard loads the current result when the engine reports a hold, mounts
  the appropriate package result view, and rereads it after reload, reconnect, or
  server restart. Once the hold ends, the next engine phase owns the screen. The
  TV needs no player sign-in. Rendering and wording remain client-owned; all
  progression, eligibility and scoring decisions stay in Python.
- Each eligible phone shows the result and a Ready control, sends the saved
  visit identity through the existing authenticated ready route, and restores
  its ready state after reconnect. The TV shows the shared standing and the
  existing ready count. Precise copy and visual styling follow the approved
  screen samples; this proposal does not introduce a new visual design.

### Tests required before implementation is accepted

- Drive the real engine through input, spotlight, completion and result hold,
  then verify all-ready, deadline and host move-on paths; repeated ticks, pauses,
  restarts and stale ready requests must not duplicate rewards or skip phases.
- Exercise eligible, disconnected, unauthorized and zero-player cases; check
  that phone Ready and TV ready count recover after reconnect.
- Verify two consecutive mini-games and repeated visits always read the run bound
  to the current hold. Cover missing, invalid, cancelled and timed-out results.
- Through real routes, prove the unsigned TV response contains the correct
  standing but none of several distinct private markers, prompts or behavioral
  data; retain the existing AW-347 privacy tests unchanged.
- Through the dashboard loader, prove the result is visible on a live event,
  reload and reconnect and disappears when the engine enters the next phase.
  A seeded active scoreboard fixture alone is not evidence of the real lifecycle.

**Gate:** The design, including the cross-module and arc schema changes and the
15-second initial value, is approved. The implementation plan needs separate
approval. AW-332 still owns the other round and result screens.
Spec 0093 Part E and the durable product approval record must be reconciled before
implementation because the proposed hold changes the approved advancement rule.
The founder explicitly allowed a narrow exception to the earlier prohibition on
editing `docs/product/decisions-log.csv`: record this approved decision only.
That exception does not approve the implementation plan or other log edits.

## Completed-Result Implementation Plan

> **Execution:** Use `superpowers:executing-plans` in this session after the
> founder approves this plan and the required protected-record exception.

**Goal:** Restore the correct public mini-game result during an engine-owned
hold, including after reconnect, without revealing private player information.

**Architecture:** Persist a result-hold substate on the existing mini-game
phase visit. The session engine selects its bound run and exposes a generic,
allowlisted result read. Clients show that result and submit readiness; Python
owns timing, eligibility, transitions and rewards.

**Tech stack:** Python 3.11, FastAPI, existing SQLAlchemy event and run records,
TypeScript dashboard and existing Node tests. No new dependency or table.

**Spec:** The approved design immediately above, plus specs 0093 Part E, 0094
Part I and 0095 screens 10 to 12. The existing immediate-advance sentence in
0093 must be reconciled before code is treated as approved.

### Review focus

- A late lobby response must eventually show the name without blocking the game.
- A solo or unbound run must never be exposed as a shared round result.
- Repeated games, overlapping reads and stale visits must never show the wrong run.
- A disconnect, pause or restart must preserve the hold and readiness safely.
- Rewards and public result reads must not leak private information or duplicate grants.

### Preconditions and file boundaries

- [x] The founder permitted a narrow exception to edit `docs/product/decisions-log.csv`
  solely to record the approved result-hold decision. Record it as D-155; the
  exception does not authorize unrelated log edits.
- [ ] After plan approval, update `docs/specs/0093-engine-spine-for-the-thin-version.md`
  to reflect the approved opt-in hold. Do not alter the open-questions log or
  `HANDOVER.md`. The task file remains the design and plan record.
- [ ] **Live configuration gap:** the two arcs currently registered in
  `config/arcs.json`, `nightcap/arc.json` and `nightcap/couch-race.arc.json`,
  contain no phased mini-games. AW-305 owns the real session-1 arc. Do not edit
  a case file or convert either legacy arc. The 15-second opt-in and live
  acceptance remain blocked until the owning work provides a phased arc and its
  author configures it. The tests below use an invented phased fixture and do
  not establish that the real Nightcap game is configured or playable.
- [ ] Touch only the approved cross-module areas: `engine/arc/models.py`,
  `engine/session/phases.py`, `engine/session/mini_game_phase.py`, existing
  reward/room read code if needed, `api/routers/mini_games.py`, the relevant
  `api/schemas/` response types, dashboard mini-game loader and kit, the
  Tell Me Something True renderer, and focused tests. Existing package definition
  JSON, auth, secrets, dependencies and database schemas stay unchanged. Any
  new path or additional engine submodule not justified by the approved plan is
  a stop for scope review.

### 1. Authored opt-in and saved hold

**Files:** `engine/arc/models.py`, `engine/session/phases.py`,
`engine/session/mini_game_phase.py`, `engine/session/mini_game_reward.py`;
tests in `engine/tests/test_phases.py`, `engine/tests/test_mini_game_phase.py`,
`engine/tests/test_mini_game_reward.py` and `engine/tests/rounds_support.py`.

- [ ] Write failing tests for `PhaseDefinition.result_hold_seconds: int | None`:
  absent means the old immediate advance; a positive value is allowed only on
  `mini_game`; zero, negative and use on other phases are refused. Add a separate
  `result_public: bool = False` field. For this shared-result implementation,
  require a positive hold and `result_public: true` together; reject a hold with
  no public-result opt-in or the flag without a hold, so an author cannot create
  a blank shared hold by accident. Private holds remain outside this task. The
  invented Nightcap-like group fixture opts in with 15 seconds and the flag.
- [ ] Write failing real-transition tests: a completed or timed-out bound run
  with a valid standing enters one hold on the same visit, saves its run ID,
  eligible human participant IDs and a new deadline, and does not start the next
  phase. Two ticks and a process-state reread must not reset the deadline or
  create two holds. A cancelled run or invalid/empty standing skips the hold;
  an invalid standing produces a host-only, content-free diagnostic once.
- [ ] Write failing readiness tests for all eligible seats, disconnected seats,
  host seat, AI and unauthorized seats, zero seats, stale visit IDs, duplicate
  taps, host move-on, deadline, and pause/restart/resume. Exactly one next phase
  starts; no screen can decide progression.
- [ ] Implement the optional field and result-hold data in the existing saved
  phase event. Preserve that data through `_state_from`, `_save`, pause and resume;
  clear it only on entry to the next visit. Use the existing visit-scoped ready
  record and session lock. Apply the hold rule both from the tick and from
  `finish_mini_game_phase`; if the deadline and all-ready coincide, record the
  deadline reason consistently. Preserve old behavior for phases without the
  setting.
- [ ] Make existing rewards available during the hold by invoking the existing
  idempotent grant and outbox notification when the hold starts, rather than
  waiting until it ends. Tests must prove exactly one grant and notification
  across repeat ticks, retries, rollback, deadline and host move-on; amounts,
  recipients and private audience do not change. Run the three focused engine
  test files above and the arc model tests.

### 2. Current public result and privacy

**Files:** `engine/session/mini_game_phase.py`, `engine/session/phases.py`,
`api/routers/mini_games.py`, appropriate `api/schemas/` response types;
tests in `api/tests/test_mini_game_views_api.py` and
`engine/tests/test_mini_game_phase.py`.

- [ ] Add failing tests that exercise a real completed run and a timed-out run,
  not a seeded active scoreboard. Two consecutive runs, a changed visit, a
  different session, missing/duplicate bindings and malformed standings must
  never return the wrong result. Concurrent phase change versus read must not
  mix a visit with another run.
- [ ] Prove the unsigned result is available only for an explicitly opted-in,
  shared round-phase hold and its bound run: require both the authored hold and
  `result_public: true`, plus the matching current phase visit. With the flag
  absent or false, the public read returns 404. A solo investigation run,
  unbound run or unknown audience must fail closed. Do not infer solo or public
  scope from `participation_mode` or player count: the same mechanic can serve
  both. AW-345 owns the still-open solo visibility decision.
- [ ] Add `GET /v1/sessions/{session_id}/mini-games/result/display` with no
  player sign-in. It returns 404 when no valid current hold exists. A successful
  response contains only `run_id`, `game_id`, `definition_version`,
  `phase_entry`, `deadline_at` and validated `standing` tiers of participant IDs.
  Resolve the current visit and its bound run under a consistent session read;
  do not expose raw state, outcome, submissions, prompts, behavior or rewards.
  Preserve the existing `/active` and `/active/display` semantics.
- [ ] Add marker-based tests over the entire unsigned response, including a
  private statement, truth declaration, prompt, behavioral signal and another
  session's markers. Confirm the unchanged AW-347 audience/privacy tests pass.
  No new game-specific function under `engine/` or `api/`.

### 3. Dashboard result, ready and recovery

**Files:** `dashboard/src/mini-games/client.ts`,
`dashboard/src/mini-game-kit/wire-types.ts`, the minimal stage/phone controls,
`nightcap/mini_games/tell-me-something-true/client/renderer.ts`,
`dashboard/tests/mini-game-live-reply.test.ts` and focused stage tests.

- [ ] First write failing tests using the real completed-run route recording and
  a separate public lobby fixture. Show the correct named standing on the TV and
  a Ready control on each eligible phone; the TV has no player sign-in. A phone
  submits the existing authenticated ready route with the current visit ID and
  sees its ready state after reconnect. Rewards come only from its existing menu.
- [ ] Implement result mounting from the current result read and hide the result
  when the engine moves to the next phase. Reload, stream reconnect and API
  restart must restore the same hold; two consecutive runs must not show stale
  names or a previous standing. Map participant IDs to public lobby names and
  show a neutral fallback for a missing name, never an internal ID.
- [ ] Keep mounting independent of a slow or failed lobby read. Retry or finish
  name resolution asynchronously and update the current screen when a delayed
  public name arrives, without requiring an event-stream reconnect. Cancel or
  ignore stale lookups after unmount, run change or a newer response. Add a
  controlled delayed-success test and a stale-response test using deferred
  promises rather than a fragile real-time threshold.
- [ ] Keep result hold behavior opt-in and generic. Do not invent solo-game TV
  or other-phone behavior: AW-345 owns that direction. This phase-bound read
  does not claim standalone support, which AW-348 owns. AW-332 retains its broader
  round and result screen work. Run dashboard typecheck and tests and Nightcap
  web typecheck and tests.

### 4. Verification and handoff

- [ ] Run `python -m pytest engine/tests api/tests -q`, Python Ruff check and
  format check, dashboard typecheck and tests, Nightcap web typecheck and tests,
  the provider-leak check and the repository's required local verification.
- [ ] Report each acceptance criterion with evidence, distinguish an unavailable
  real phased arc from fixture proof, and report any skipped database test.
  Push the same branch, wait for all six CI checks, answer every review thread,
  and do not merge or deploy.

**Plan approval is pending.** The founder's design and narrow decision-log
exception do not approve this plan. The absent real phased arc is a prerequisite
gap for the live Nightcap opt-in and must not be quietly marked complete.
