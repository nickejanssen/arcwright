---
id: productroadmap.roadmap.tasks.aw-359-fix-the-review-findings-on-the-round-screens
namespace: product-roadmap
title: "AW-359: Fix The Review Findings On The Round Screens That Merged In AW-332 Part A"
owner: Nico Janssen
status: draft
review_by: "2027-02-21"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-359: Fix The Review Findings On The Round Screens That Merged In AW-332 Part A

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Nightcap  
**Owner:** Claude build session (the screens lane); founder approved the plan in his own words in that session on 2026-11-21 ("Yes")  
**GitHub issue:** [#477](https://github.com/nickejanssen/arcwright/issues/477)  
**Target date:** before the founder's end-to-end test on 1 December 2026 (D-149)

## Plain-English Summary

An independent review of AW-332 part A (pull request #473, merged as `b018d83`) found four real problems and one question that the merge did not fix. On the phone, a finding can hide the Ready button, a slow menu read can overwrite a newer one, a refused choice can send a request after the screen is gone, and the menu can be shown in a different order from the engine's. This task fixes those four. It also records one open question for the founder about a sentence on the TV.

## Why This Matters

- Merged is not fixed. The review read head `2ec8300`; the merge came after, without these changes (verified in code on `main`, 2026-11-21).
- The founder's test plays these screens. A stuck Ready button or a wrong menu order stops or confuses a round.
- Showing the menu in the engine's order was a hard constraint in the approved AW-332 plan.

## Technical Scope

All in `dashboard/` (the screens lane). No engine, API or package change.

1. **Held finding hides Ready (P1)** (`dashboard/src/screens/round/EyesUpPhone.tsx`). The finding is copied into state once and its 30 second hold is never checked again. Show the Ready control with the held finding, so Ready is never hidden, and drop the finding when its hold has passed.
2. **Stale menu read (P1)** (`InvestigatePhone.tsx`). Number every menu request and ignore any reply that is not from the newest request, so an older reply cannot replace a newer budget and menu.
3. **Rejected choice after the screen is gone (P2)** (`InvestigatePhone.tsx`). Check that the screen is still there on the failure path too, and start no new request and set no state after it has gone.
4. **Grouping reorders the menu (P2)** (`InvestigatePhone.tsx`). Show consecutive items about the same subject as one group, in the engine's order. A menu in the order A, B, A stays A, B, A.
5. **Open question, not built (P2):** the thinking-time TV shows "Investigate on your phones." D-134 says round title, clock and ready list only, but that sentence is line 3 of the copy sample the founder approved on #435. It stays unless the founder says to remove it (a one-line change).

## Human Collaboration Contract

**Interaction profile:** Independent execution. The founder approved the plan for items 1 to 4 in his own words in the build session. Item 5 waits on his answer.

## Acceptance Criteria

1. With a held finding on screen, the Ready control is shown, and a held finding older than its hold is not shown.
2. When two menu reads are in flight, the older reply never replaces the newer one's budget or menu.
3. A choice rejected after the screen has gone starts no request and sets no state.
4. A menu in the order A, B, A is shown as A, B, A, and no item is dropped.
5. Each new test fails on `main` before the change and passes after it.

## Tests/Verification

- `npm test --prefix dashboard`, `npm run typecheck --prefix dashboard`, `npm run build --prefix dashboard`.
- All six pull request checks pass; every review thread answered and resolved.
- Dashboard tests do not run in CI until AW-334.

## Dependencies

- AW-332 part A (pull request #473, merged as `b018d83`).

## Must Not Do

- Do not change `engine/`, `api/`, `nightcap/mini_games/`, `nightcap-web/`, `sdk/`, `auth.ts`, `seatStore.ts` or `package.json`.
- Do not put a game rule in TypeScript: no arithmetic on the budget, no right-or-wrong, no ordering or filtering of the menu.
- Do not build AW-332 part B (screens 10 to 12) under this task.

## Kickoff Prompt

> Implement AW-359 (#477). Read `AGENTS.md`, `HANDOVER.md` and this task. Tests first. Do not merge.
