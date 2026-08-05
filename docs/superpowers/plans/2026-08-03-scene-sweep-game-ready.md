# Scene Sweep Game-ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the merged Scene Sweep backend while producing a reusable browser package, an independently versioned 2-to-8-player Nightcap adaptation, polished phone, shared-focus, and host presentation, deterministic Scene rotation with Crime Scene Smash, local Playtest-ready evidence, and gated Production-ready evidence.

**Architecture:** PR #273 and PR #274 are the authoritative backend and design baseline. Do not rebuild the evidence-search-race plugin or mechanic-specific API behavior. First characterize the merged behavior. Then use the approved package, adaptation, placement, authority, design-system, and readiness contracts. Python remains authoritative for board selection, real-object identity, claim ordering, deadline, reveal, result, clue fallback, and consequences. Browser code renders authorized projections and submits claims only.

**Tech Stack:** Python 3.11, Pydantic 2, FastAPI, TypeScript, mini-game renderer kit, esbuild, happy-dom, pytest, Node test runner, Ruff.

## Global Constraints

- Required founder-approved design: `docs/superpowers/specs/2026-08-02-nightcap-scene-sweep-mini-game-design.md`.
- Required game spec: `docs/specs/0086-scene-sweep-game-ready.md`.
- Required completed dependencies: browser golden path, capability and trust platform, and creator and readiness labs.
- Required merged baseline: PR #273 and PR #274 at or after commit `d26d7b8dee2aafa59ef6a0fd985da5bea771dbf1`.
- Stop before source changes until the founder gives the separate implementation go-ahead.
- Stop again before selecting the 2-to-3-player adaptation, generating presentation assets, and Production-ready promotion.
- Preserve race-to-claim, exactly one real object, no early completion when the real object is claimed, staged end reveal, deterministic arbitration, delayed clue fallback, and 4-to-8-player object scaling.
- Never expose real or decoy identity before finalization on phone, shared-focus, or host surfaces.
- Never trust browser claims for winner, score, clue, or story authority.
- Do not duplicate the Scene Sweep plugin, package, API projection, design document, or merged tests.
- Do not decide Leverage payout or final score weight in this plan. Use a typed bounded seam and return for economy tuning after end-to-end session proof.
- Do not add cloud deployment, marketplace, billing, new dependencies, or external authority.

---

### Task 1: Refresh Mainline, Characterize the Merged Baseline, and Stop

**Files:**

- Read: `docs/product/mini-game-readiness/mainline-safety-report.md`
- Read: `docs/superpowers/specs/2026-08-02-nightcap-scene-sweep-mini-game-design.md`
- Read: `docs/superpowers/plans/2026-08-02-scene-sweep-engine-and-api.md`
- Read: `docs/specs/0086-scene-sweep-game-ready.md`
- Modify: `engine/tests/test_scene_sweep_runtime_integration.py`
- Modify: `api/tests/test_scene_sweep_api.py`
- Create: `nightcap-web/tests/scene-sweep-characterization.test.ts`

- [ ] **Step 1: Refresh and inspect merged work**

```powershell
git fetch origin --prune
gh pr view 273 --json number,title,state,mergedAt,mergeCommit,files,url
gh pr view 274 --json number,title,state,mergedAt,mergeCommit,files,url
git diff --name-status d26d7b8dee2aafa59ef6a0fd985da5bea771dbf1..origin/main
git status --short --branch
```

- [ ] **Step 2: Add characterization assertions before refactoring**

Cover deterministic slot subset, exactly one real object, 4-to-8 object counts, first accepted claim, same-object conflict, no early end, deadline, full-board exhaustion, hidden truth, staged reveal, full clue, reduced fallback clue, behavioral outputs, pause, resume, and replay.

- [ ] **Step 3: Run the merged baseline**

```powershell
python -m pytest engine/tests/test_evidence_search_race_runtime.py engine/tests/test_scene_sweep_runtime_integration.py api/tests/test_scene_sweep_api.py -q
npm --prefix nightcap-web test
```

- [ ] **Step 4: Record baseline ownership**

Update the readiness report to name exact files and tests owned by PR #273 and #274. Mark them `preserve`, not `rebuild`.

- [ ] **Step 5: Stop for implementation approval**

Expected: the founder reviews current main, overlap, and characterization before Task 2.

### Task 2: Design and Approve the 2-to-3-player Participation Adaptation

**Files:**

- Create: `docs/product/mini-game-readiness/scene-sweep-participation-options.md`
- Create: `docs/product/mini-game-readiness/scene-sweep-participation-fixtures.json`
- Modify after approval: `docs/specs/0086-scene-sweep-game-ready.md`

**Interfaces:**

- Consumes: approved 4-to-8-player mechanic, Couch Race 2-to-8 session range, surface constraints, and fairness goals.
- Produces: one recommended 2-to-3-player model and at most two meaningful alternatives.

- [ ] **Step 1: Build low-cost deterministic simulations**

For 2 and 3 players, model object density, expected claims per player, simultaneous-target contention, idle time, finder concentration, timeout rate, reveal timing, and shared-display readability. Do not create finished art.

- [ ] **Step 2: Present one recommendation and up to two alternatives**

Each option must explain active-player model, object count, viewport coverage, fairness, table energy, pacing, spectator behavior, authority, and whether the original 4-to-8 mechanic changes.

- [ ] **Step 3: Ask the founder to select or revise**

No implementation follows without explicit approval. Record the selected model and rejected alternatives with rationale in spec 0086.

- [ ] **Step 4: Add failing selected-model tests**

Only after approval, encode player-count expectations in `engine/tests/test_evidence_search_race_runtime.py` and confirm they fail against the 4-player minimum.

- [ ] **Step 5: Commit the approved decision and tests**

```powershell
git add docs/product/mini-game-readiness/scene-sweep-participation-options.md docs/product/mini-game-readiness/scene-sweep-participation-fixtures.json docs/specs/0086-scene-sweep-game-ready.md engine/tests/test_evidence_search_race_runtime.py
git commit -m "docs(nightcap): approve scene sweep participation"
```

### Task 3: Version the Reusable Package and Nightcap Adaptation

**Files:**

- Modify: `nightcap/mini_games/scene-sweep/manifest.json`
- Create: `nightcap/mini_games/scene-sweep/definitions/0.2.0.json`
- Create: `nightcap/mini_games/scene-sweep/README.md`
- Create: `nightcap/mini_games/scene-sweep/adaptations/nightcap-couch-race-v1/0.1.0.json`
- Create: `nightcap/mini_games/scene-sweep/adaptations/nightcap-couch-race-v1/readiness.json`
- Modify: `engine/tests/test_mini_game_models.py`
- Modify: `engine/tests/test_evidence_search_race_runtime.py`

**Interfaces:**

- Consumes: merged 0.1.0 definition and approved participation model.
- Produces: immutable reusable package 0.2.0 and separate Nightcap adaptation 0.1.0.

- [ ] **Step 1: Add failing package and adaptation validation tests**

Assert destination-neutral affordances, exact digest, 2-to-8 session support, selected active-player behavior, result schema, presentation roles, fallback, provenance parent, preview profiles, and Nightcap-specific data only in the adaptation.

- [ ] **Step 2: Create a new definition version**

Do not edit 0.1.0. Move reusable mechanic rules and affordances into 0.2.0. Keep Nightcap beat, clue, style, and consequence mapping in the adaptation.

- [ ] **Step 3: Remove the generated `run_seed` stopgap safely**

Use the canonical invocation seed or immutable resolved snapshot identity from the capability platform. Add a regression test proving separate sessions vary while replay of one invocation is exact. Do not ask generation to invent authority state.

- [ ] **Step 4: Define typed results and bounded seams**

Include finder, accepted claims, decoys claimed, completion time, timeout, and fallback facts. Define bounded score, evidence, and Leverage-compatible profiles without choosing final Leverage or score tuning.

- [ ] **Step 5: Run and commit**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/scene-sweep
python -m pytest engine/tests/test_mini_game_models.py engine/tests/test_evidence_search_race_runtime.py engine/tests/test_scene_sweep_runtime_integration.py -q
git add nightcap/mini_games/scene-sweep engine/tests/test_mini_game_models.py engine/tests/test_evidence_search_race_runtime.py engine/tests/test_scene_sweep_runtime_integration.py
git commit -m "feat(nightcap): version scene sweep adaptation"
```

### Task 4: Approve the Destination Presentation Direction

**Files:**

- Create: `docs/product/mini-game-readiness/scene-sweep-presentation-brief.md`
- Create: `docs/product/mini-game-readiness/scene-sweep-wireframes.md`
- Modify after approval: `docs/specs/0086-scene-sweep-game-ready.md`

- [ ] **Step 1: Prepare low-cost surface artifacts**

Show phone viewport and minimap, shared full scene, host status, claim acknowledgement, progress, countdown, timeout, final reveal, captions, audio cues, reduced motion, reconnect, and fallback. Label private and public information explicitly.

- [ ] **Step 2: Map Nightcap's experience design system**

Specify semantic tokens, typography, art direction, object readability, motion, audio, copy voice, intensity, accessibility, and asset budgets. Keep CSS and device names out of engine contracts.

- [ ] **Step 3: Ask generation permission**

Request separate permission for code, art, animation, audio, copy, and configuration. Name source assets, locked roles, proposed replacements, and preservation behavior. Record denial as a first-class outcome.

- [ ] **Step 4: Ask the founder to approve the presentation artifact**

No final renderer or generated asset work begins until the founder approves the direction and allowed categories.

- [ ] **Step 5: Commit the approved brief**

```powershell
git add docs/product/mini-game-readiness/scene-sweep-presentation-brief.md docs/product/mini-game-readiness/scene-sweep-wireframes.md docs/specs/0086-scene-sweep-game-ready.md
git commit -m "docs(nightcap): approve scene sweep presentation"
```

### Task 5: Implement Phone, Shared-focus, and Host Renderers

**Files:**

- Create: `nightcap/mini_games/scene-sweep/client/renderer.ts`
- Create: `nightcap/mini_games/scene-sweep/client/styles.css`
- Create: `nightcap/mini_games/scene-sweep/client/renderer.test.ts`
- Create approved assets under: `nightcap/mini_games/scene-sweep/assets/`
- Modify: `nightcap/mini_games/scene-sweep/manifest.json`
- Modify: `nightcap-web/tests/mini-game-registry.test.ts`
- Create: `nightcap-web/tests/scene-sweep-renderer.test.ts`
- Create: `nightcap-web/tests/scene-sweep-privacy.test.ts`
- Create: `nightcap-web/tests/scene-sweep-performance.test.ts`

**Interfaces:**

- Consumes: generic authorized invocation projection and exact 0.2.0 definition plus 0.1.0 adaptation.
- Produces: `MiniGameRenderer` with phone, shared-display, and host handlers.

- [ ] **Step 1: Add failing discovery, surface, privacy, and reduced-motion tests**

Test exact-version loading, independent phone pan, minimap, full shared scene, host progress, claim acknowledgement, live unlabeled claim markers, staged reveal, timeout, reconnect, reset, captions, keyboard access, screen-reader labels, contrast, and reduced motion.

- [ ] **Step 2: Implement phone presentation**

Use the renderer kit. The phone may pan its own viewport, show minimap location, show the archetype list and claimed markers, and acknowledge the player's own accepted or rejected claim. It never learns truth before finalization.

- [ ] **Step 3: Implement shared-focus presentation**

Show the full scene, collective progress, unlabeled claim markers, countdown, transition, and staged final reveal. Never identify a real object early through color, animation, timing, accessibility text, or event order.

- [ ] **Step 4: Implement host presentation**

Show progress, time, connection health, fallback state, pause, resume, and cancel controls without pre-reveal truth. Host controls call existing authorized commands.

- [ ] **Step 5: Enforce asset and performance budgets**

Test initial and total bundle sizes, image dimensions, decode time, interaction responsiveness, pan frame budget, low-end viewport, and shared-display layout. Use approved reduced assets when budgets fail.

- [ ] **Step 6: Run and commit**

```powershell
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/scene-sweep
git add nightcap/mini_games/scene-sweep/client nightcap/mini_games/scene-sweep/assets nightcap/mini_games/scene-sweep/manifest.json nightcap-web/tests
git commit -m "feat(nightcap): render scene sweep"
```

### Task 6: Route Scene Sweep Through Generic Transport and Authoritative Results

**Files:**

- Modify only if characterization remains green: `api/routers/mini_games.py`
- Modify: `api/tests/test_scene_sweep_api.py`
- Modify: `nightcap-web/src/mini-games/client.ts`
- Modify: `nightcap-web/tests/mini-game-client.test.ts`
- Modify: `engine/tests/test_scene_sweep_runtime_integration.py`

- [ ] **Step 1: Add generic transport equivalence tests**

Assert the generic projection carries board, public object state, progress, deadline, and audience-specific data with no mechanic union in the API schema. Preserve every merged Scene Sweep privacy property.

- [ ] **Step 2: Remove only the duplicated router projection**

If the capability plan already moved Scene Sweep projection behind a plugin, make no API source change. Otherwise move existing logic intact behind the generic projection interface and delete the router branch only after equivalence tests pass.

- [ ] **Step 3: Prove authoritative claim ordering**

Run concurrent claim tests through API, runtime, and reducer. Browser timestamps, local score, and client winner fields are ignored. The accepted engine or managed-transcript order is canonical.

- [ ] **Step 4: Run and commit**

```powershell
python -m pytest api/tests/test_scene_sweep_api.py engine/tests/test_scene_sweep_runtime_integration.py -q
npm --prefix nightcap-web test
git add api/routers/mini_games.py api/tests/test_scene_sweep_api.py nightcap-web/src/mini-games/client.ts nightcap-web/tests/mini-game-client.test.ts engine/tests/test_scene_sweep_runtime_integration.py
git commit -m "refactor(api): use generic scene sweep transport"
```

### Task 7: Add Deterministic Scene Rotation with Crime Scene Smash

**Files:**

- Modify: `nightcap/couch-race.arc.json`
- Create: `nightcap/mini_games/placement-policies/scene-discovery/1.0.0.json`
- Modify: `engine/tests/test_couch_race_arc_json.py`
- Modify: `engine/tests/test_mini_game_placement.py`
- Create: `engine/tests/test_scene_minigame_rotation.py`

**Interfaces:**

- Consumes: approved Scene candidate pool, session seed, eligibility, lookback, exact adaptations, and fallback.
- Produces: one persisted deterministic Scene selection and explanation.

- [ ] **Step 1: Add failing candidate-pool and replay tests**

Assert the pool contains only approved Crime Scene Smash and Scene Sweep adaptation versions, no immediate repeat when another candidate is eligible, exact replay, deterministic fallback, and no package name in engine selection code.

- [ ] **Step 2: Replace the legacy Scene binding with one placement policy**

The designer delegates selection only within the two-candidate Scene discovery pool. Preserve the authored Scene anchor, consequence profile, time budget, public context, and fallback.

- [ ] **Step 3: Test eligibility changes**

Retirement, unsupported player count, missing surface role, unavailable profile, or failed readiness removes a candidate with a visible reason. The other candidate runs when valid. If none is valid, the authored story fallback advances.

- [ ] **Step 4: Run and commit**

```powershell
python -m pytest engine/tests/test_couch_race_arc_json.py engine/tests/test_mini_game_placement.py engine/tests/test_scene_minigame_rotation.py -q
python -m json.tool nightcap/couch-race.arc.json
git add nightcap/couch-race.arc.json nightcap/mini_games/placement-policies/scene-discovery/1.0.0.json engine/tests/test_couch_race_arc_json.py engine/tests/test_mini_game_placement.py engine/tests/test_scene_minigame_rotation.py
git commit -m "feat(nightcap): rotate scene minigames"
```

### Task 8: Reach Local Playtest-ready and Run Device and Player Gates

**Files:**

- Create: `docs/roadmap/operations/scene-sweep-device-walkthrough.md`
- Create: `docs/roadmap/operations/scene-sweep-playtest.md`
- Create: `docs/product/mini-game-readiness/scene-sweep-0.2.0.json`
- Modify: `nightcap/mini_games/scene-sweep/adaptations/nightcap-couch-race-v1/readiness.json`
- Modify: `docs/specs/0086-scene-sweep-game-ready.md`

- [ ] **Step 1: Run local lab scenarios**

Run 2, 3, 4, 6, and 8 simulated players across success, timeout, full-board exhaustion, duplicate claim, simultaneous claim, pause, resume, reconnect, host loss, fallback, reset, replay, and rotation.

- [ ] **Step 2: Record Playtest-ready evidence**

Include package validation, exact versions, surfaces, privacy, accessibility, performance, authority, fallback, rotation, simulation ledger, and blockers. Mark preview authority clearly.

- [ ] **Step 3: Pause at the real-device gate**

Test representative phones, shared display, LAN join, orientation, pan performance, minimap clarity, claim latency, reconnect, audio, captions, contrast, and reduced motion. Record missing devices as not run.

- [ ] **Step 4: Pause at the real-player gate**

Measure search clarity, accidental claims, finder concentration, fairness, idle time, shared spectacle, reveal satisfaction, story return, timeout rate, and replay desire. Recalibrate duration and object density through a new version, never by editing a playtested definition.

- [ ] **Step 5: Run verification and commit evidence**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/scene-sweep
python -m pytest engine/tests/test_evidence_search_race_runtime.py engine/tests/test_scene_sweep_runtime_integration.py engine/tests/test_scene_minigame_rotation.py api/tests/test_scene_sweep_api.py -q
npm --prefix nightcap-web test
git diff --check
git add docs/roadmap/operations/scene-sweep-device-walkthrough.md docs/roadmap/operations/scene-sweep-playtest.md docs/product/mini-game-readiness/scene-sweep-0.2.0.json nightcap/mini_games/scene-sweep/adaptations/nightcap-couch-race-v1/readiness.json docs/specs/0086-scene-sweep-game-ready.md
git commit -m "test(nightcap): record scene sweep readiness"
```

### Task 9: Promote Only After Production-ready Founder Approval

**Files:**

- Modify after approval: `nightcap/mini_games/scene-sweep/manifest.json`
- Modify after approval: `nightcap/mini_games/scene-sweep/adaptations/nightcap-couch-race-v1/0.1.0.json` only by creating a new version if immutable
- Modify: `docs/product/mini-game-readiness/artifact-closeout-matrix.md`
- Modify: `docs/specs/0086-scene-sweep-game-ready.md`
- Update related GitHub issue or PR status only after canonical records are correct

- [ ] **Step 1: Review the Production-ready visual lab**

Review Plays correctly, Fits the story, Feels native, Survives reality, and Approved by people. Missing human evidence cannot pass.

- [ ] **Step 2: Ask the founder for production promotion**

Approval of the design, implementation, or playtest is not production approval. Record the exact package and adaptation digests approved.

- [ ] **Step 3: Promote or record blockers**

If approved, promote exact versions. If not, keep Playtest-ready and record the smallest next action. Do not lower a gate to claim completion.

- [ ] **Step 4: Reconcile all related artifacts**

Update spec, readiness report, program plan, roadmap task, epic, milestone, closeout matrix, and GitHub issue or PR. Read back GitHub state after mutation.

- [ ] **Step 5: Run final verification**

```powershell
python -m pytest engine/tests/test_mini_game_models.py engine/tests/test_evidence_search_race_runtime.py engine/tests/test_scene_sweep_runtime_integration.py engine/tests/test_scene_minigame_rotation.py api/tests/test_scene_sweep_api.py -q
npm --prefix nightcap-web test
python -m ruff check engine api
git diff --check
```

## Acceptance Criteria Satisfied by This Plan

- PR #273 and PR #274 remain the authoritative backend and design baseline.
- Scene Sweep becomes a destination-neutral reusable package and a separate Nightcap adaptation.
- An explicitly approved participation model supports Couch Race sessions from 2 through 8 players.
- Phone, shared-focus, and host renderers preserve privacy, authority, accessibility, performance, reconnect, audio, and reduced-motion requirements.
- Local Playtest-ready testing requires no cloud deployment.
- Scene rotates Scene Sweep and Crime Scene Smash deterministically with persisted reasons and no mechanic-specific engine branch.
- Browser claims cannot determine canonical finder, score, clue, or story consequences.
- Real-device and real-player evidence gates gameplay tuning and production promotion.
- Final promotion updates every related spec, plan, roadmap record, milestone, epic, issue, and readiness artifact from canonical evidence.
