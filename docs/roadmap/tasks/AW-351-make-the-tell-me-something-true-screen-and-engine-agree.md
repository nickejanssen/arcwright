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

**Status: Draft, not approved for implementation.** On 2026-11-21 the founder
asked to expand PR #472 to design a privacy-safe completed-run read and result
lifecycle. Asked how the game should proceed, the founder selected: "Pause for
results (Recommended): show the result, then continue when players are ready or a
clock expires." This is direction for the design, not approval of its details or
permission to implement. No duration has been approved.

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
result-hold direction; the details below remain proposed.

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
  or host move-on; a hold with no eligible players does not auto-advance on an
  empty all-ready set. Reject ready submissions from anyone outside that set.
- A valid standing has at least one nonempty tier, names each ranked human seat
  exactly once, contains no other seat and permits ties. Reject malformed tiers,
  duplicates and omissions instead of exposing or silently repairing them. This
  follows `build_standing`, which already includes unranked eligible seats.
- Give each opted-in mini-game phase a positive authored result-hold duration.
  Phases without this setting retain the existing immediate-advance behavior.
  The Nightcap phased arc must opt in so the requested hold actually runs. The
  proposed initial value is **15 seconds**, adjustable after playtesting and not
  a claim about ideal pacing. The founder must explicitly approve or change it.
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

**Gate:** The founder must approve this design, including the cross-module and
arc schema changes, and choose an initial hold duration before implementation.
The earlier approval to investigate the public lobby mapping does not approve
these additions. The implementation plan will identify exact files and checks
after the design is accepted. AW-332 still owns the other round and result screens.
