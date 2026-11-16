---
id: productroadmap.roadmap.tasks.aw-328-give-the-mini-game-winner-one-extra-investigation
namespace: product-roadmap
title: "AW-328: Give The Mini-Game Winner One Extra Investigation"
owner: Nico Janssen
status: active
review_by: "2027-02-16"
sensitivity: internal
source: authored
x-scope-evidence: D-112, D-113, D-124, D-126
tags: []
supersedes: []
---

# AW-328: Give The Mini-Game Winner One Extra Investigation

**Milestone / Epic:** M7 / M7-B
**Size:** S
**Product:** Shared (Arcwright and Nightcap)
**Owner:** One AI build session (Claude or Codex)
**Target date:** 2026-11-30

## Plain-English Summary

When a mini-game ends, the player or players who placed first get one more investigation to spend. Nobody gets a clue from the mini-game itself. The reward is a setting in the arc file, so it can be changed after a playtest without changing code.

## Why This Matters

- Today a finished mini-game releases the same clue to every player and the winner gets nothing extra, so winning does not matter.
- The founder chose this on 2026-11-16 (D-126): "Go with your mini-game recommendation." It is the game design document's own example of a reward, and it does not replace detective work.
- A mini-game's result is a free-form record today. There is no standard "who placed where", so nothing can name a winner. The endgame's tie-break (spec 0094, Part I) needs the same thing.
- Filed under D-119 when the founder answered Q1 of spec 0093 on 2026-11-16: no existing task covered the reward.

## Technical Scope

- A **standing** on every finished mini-game run: the players in order, with ties allowed. A mechanic that cannot rank its players records them all as tied. One added field in the run's saved outcome and a small change in each of the four mechanics (spec 0094, Part I).
- A reward setting on a beat's mini-game binding in the arc file: what is given, how much, and to whom. An arc that sets none behaves exactly as today.
- When a run ends, the engine gives the reward by rule: each top-ranked participant's investigation budget (spec 0093, Part D) goes up by the set amount. It is saved, and it is given once even if the end of the run is processed twice.
- A way for an arc's mini-game to release no case information. The session 1 arc uses it. How it is switched off is settled in the plan.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. The change crosses engine modules (`mini_games`, `session`, `arc`), which is a hard rule in `AGENTS.md`.

- Blocked until AW-303 and AW-325 are merged.
- The build session writes a plan and stops for the founder's approval before code.
- The founder's answer chose the reward. The design in "Q1 Answered" at the end of spec 0093 is a proposal; if the build session finds a simpler way that keeps the reward a setting, it says so in its plan (D-127).

## Acceptance Criteria

- [ ] Headless test: after a mini-game ends, each top-ranked participant has one more investigation left than before, and every other participant's budget is unchanged.
- [ ] A tie at the top rewards each tied participant.
- [ ] Every finished run of each of the four mechanics records a standing that names every eligible player once.
- [ ] The reward is given once when the end of the run is processed twice, and is still there after the session is loaded again from saved records.
- [ ] An arc file with no reward setting behaves as before; both registered arc files run unchanged and no existing test is edited to make it pass.
- [ ] With releases switched off in the test arc, no participant receives case content when the mini-game ends.
- [ ] Changing the amount in the test arc file changes the reward with no code change.
- [ ] No table change, no new dependency, no model call. If one is needed, the session stops and asks.
- [ ] No murder-mystery word is added to `engine/`.

## Tests/Verification

- `python -m pytest engine/tests -q`
- `python -m pytest api/tests -q`
- `python -m ruff check engine api`

## Dependencies

- AW-303, AW-325
- Decision: D-126. Spec: `docs/specs/0093-engine-spine-for-the-thin-version.md`, "Q1 Answered" and Parts D and E; `docs/specs/0094-endgame-for-the-thin-version.md`, Part I.

## Must Not Do

- Do not give case information as a reward.
- Do not hardcode the reward's size or who gets it; both come from the arc file.
- Do not change the points code in `engine/scoring/` or the old arc files.
- Do not use time or order of arrival to rank players unless the mechanic already does.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, "Q1 Answered" in `docs/specs/0093-engine-spine-for-the-thin-version.md` and Part I of `docs/specs/0094-endgame-for-the-thin-version.md`. Confirm that AW-303 and AW-325 are merged; if not, stop. Task AW-328: record a standing on every finished mini-game run, and give each top-ranked participant the reward set in the arc file. Write the tests first from the acceptance criteria. Write a plan and stop for founder approval, because this crosses engine modules.
