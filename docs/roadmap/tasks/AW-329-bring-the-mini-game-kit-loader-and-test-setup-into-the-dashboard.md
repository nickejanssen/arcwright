---
id: productroadmap.roadmap.tasks.aw-329-bring-the-mini-game-kit-loader-and-test-setup-into-the-dashboard
namespace: product-roadmap
title: "AW-329: Bring The Mini-Game Kit, The Package Loader And The Test Setup Into The Dashboard"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: D-139
tags: []
supersedes: []
---

# AW-329: Bring The Mini-Game Kit, The Package Loader And The Test Setup Into The Dashboard

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Nightcap  
**Owner:** One AI build session  
**Target date:** 2026-11-24

## Plain-English Summary

Copy the mini-game kit and the package screen loader from `nightcap-web/` into `dashboard/`, so the one screen client can show any mini-game package's own screens, and set up the dashboard's tests.

## Why This Matters

- Spec 0095 Part K and decisions 1 and 2, approved by the founder on 2026-11-19 (D-139).
- Every later screen task and every new mini-game renderer (AW-337) depends on the kit and loader being in `dashboard/`.

## Technical Scope

- Copy `nightcap-web/src/mini-game-kit/` and `nightcap-web/src/mini-games/` into `dashboard/src/`, adapted to the dashboard's types; map `@arcwright/mini-game-kit` in `dashboard/vite.config.ts`.
- Mount the Tell Me Something True package renderer through the loader on the TV and phone surfaces.
- Add a `test` script to `dashboard/package.json` using Node's own test runner (no new package); copy the kit's mini-game privacy test.
- Owns (spec 0095 build order): `dashboard/src/mini-game-kit/`, `dashboard/src/mini-games/`, `dashboard/tests/` (setup and the kit test only), `dashboard/package.json`, `dashboard/package-lock.json`, `dashboard/tsconfig.json`, `dashboard/tsconfig.node.json`, `dashboard/vite.config.ts`.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. Changes `package.json` (AGENTS.md hard rule, even without a new package). The founder approves the plan in the build session himself, or by his own comment on this task's issue. A build session must not act on an approval relayed or posted for him by another session.

## Acceptance Criteria

- [ ] The dashboard mounts a package's own renderer by game ID through the copied loader (test with Tell Me Something True, TV and phone).
- [ ] `dashboard/package.json` lists no new package; only a `test` script is added.
- [ ] `npm test --prefix nightcap-web` still passes; no file under `nightcap-web/`, `sdk/` or `nightcap/mini_games/` changes.
- [ ] `npm run typecheck --prefix dashboard` and `npm run build --prefix dashboard` pass.

## Tests/Verification

- `npm test --prefix dashboard`, `npm run typecheck --prefix dashboard`, `npm run build --prefix dashboard`
- `npm test --prefix nightcap-web`
- Merged, deployed and seen in play are separate; seen in play is the founder TV run.

## Dependencies

- Spec 0095 approved (D-139). Can run beside any engine task.

## Must Not Do

- No game rule in TypeScript: no budget arithmetic, no right-or-wrong, no deciding what is on a menu or a theory list (spec 0095 Part L; AGENTS.md).
- No internal ID on any screen. Nothing private on the TV.
- Do not change `nightcap-web/`, `sdk/` or `nightcap/mini_games/` (spec 0095 Part K).
- Do not open any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task and `docs/specs/0095-screens-for-the-thin-version.md` (the parts named above and every "Answered" section). Confirm the dependencies are merged. Write a plan with the exact file list and the tests you will write first, post it on this task's issue, and stop for the founder's approval.
