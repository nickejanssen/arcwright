---
id: productroadmap.roadmap.tasks.aw-326-build-last-call-the-private-lock-the-theory-check-and-the-winner-rule
namespace: product-roadmap
title: "AW-326: Build Last Call, The Private Lock, The Theory Check And The Winner Rule"
owner: Nico Janssen
status: active
review_by: "2027-02-16"
sensitivity: internal
source: authored
x-scope-evidence: D-112, D-118, D-123
tags: []
supersedes: []
---

# AW-326: Build Last Call, The Private Lock, The Theory Check And The Winner Rule

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-12-02

## Plain-English Summary

After the last round, start a countdown, let each player privately build and lock a final theory from what they found, and decide by rule who solved the case and who wins. It is Parts G, H and I of spec 0094.

## Why This Matters

- No code exists for the final theory or for checking it. The old countdown and lock sit inside the points-scoring code, which the thin version does not use.
- The result must come from rules, the same every time, with no AI judging anything (spec 0092 acceptance criteria).
- Filed under D-119 when spec 0094 was drafted on 2026-11-16: no existing task covered the endgame build.

## Technical Scope

- **D-138 (2026-11-19):** the case format gains a short account text around the solution slots (a generic field in `engine/case/authored/`), and the theory form gains one proof field holding a concept the player holds. The proof is saved and locked with the draft; it is not judged and does not affect the winner. Amends spec 0094 Part G.
- A `commit` phase on the clock from spec 0093: private drafts, a final lock, and what happens to a player who has not locked when time runs out.
- A pure function that judges each locked theory against the case file's `solution`.
- The winner rule: one solver wins; several are split by mini-game results; none means nobody wins.
- Reads the standing (players in order, ties allowed) on every finished mini-game run. AW-328 records it; it moved there on 2026-11-16 because the mini-game reward needs it first (D-126).
- Routes with thin handlers: read my theory form, save my draft, lock.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. The change crosses engine modules (`session`, `case`, `interactions`, `mini_games`), which is a hard rule in `AGENTS.md`.

- Specs 0093 and 0094 are approved (D-124, D-125, issue #355). Unblocked 2026-11-18: AW-325 (#397), AW-303 (#413) and AW-328 (#417, `8ea4bc1`) are merged. AW-328 put a `standing` in every finished run's saved outcome (`engine/mini_games/runtime.py`, `build_standing`), which Part I reads. A build session writes a plan and stops for founder approval.
- The build session writes a plan and stops for the founder's approval before code.

## Acceptance Criteria

- [ ] The "Part G", "Part H" and "Part I" acceptance criteria of spec 0094 pass.
- [ ] No table change, no new dependency, no model call.
- [ ] Nothing under `engine/scoring/`, `sdk/`, `dashboard/` or `nightcap-web/` is changed.
- [ ] No murder-mystery word is added to `engine/`.

## Tests/Verification

- `python -m pytest engine/tests -q`
- `python -m pytest api/tests -q`
- `python -m ruff check engine api`

## Dependencies

- AW-325, AW-303, AW-328
- AW-302: specs 0093 and 0094 approved (issue #355).
- Spec: `docs/specs/0094-endgame-for-the-thin-version.md`

## Must Not Do

- Do not expose whether a theory is right before every theory is locked, to anyone, in any event or route.
- Do not use time or order of arrival to pick a winner.
- Do not narrow or order a player's choices toward the right answer.
- Do not open any real case file. Use the test fixture only.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, `docs/specs/0093-engine-spine-for-the-thin-version.md` and `docs/specs/0094-endgame-for-the-thin-version.md`. Confirm on issue #355 that both specs are approved and that AW-325, AW-303 and AW-328 are merged; if not, stop. Task AW-326: build Parts G, H and I of spec 0094. Write the tests first, one per result branch. Write a plan and stop for founder approval, because this crosses engine modules. Never open a real case file.
