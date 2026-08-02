# Nightcap Mini-game Opportunity Foundation Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to execute
> this plan task by task. Do not begin without separate founder approval.

**Goal:** Connect Couch Race's six authored beats to generic mini-game
opportunities, Nightcap consequences, semantic presentation, and production
phone, TV, and host bootstrap.

**Architecture:** Nightcap owns registrations, opportunity content,
consequence mappings, theme, and rendering. Arcwright owns deterministic
invocation and canonical consequences. No Couch Race beat IDs or Leverage
vocabulary enter generic engine modules.

---

## Task 1: Preflight and Placement Artifact

Execute the program safety gate and confirm contract and onboarding checkpoints.

Create a low-cost placement table for all six beats showing:

- story purpose;
- eligible games;
- automatic or deferred trigger;
- duration budget;
- repetition;
- consequence profile;
- attention target;
- fallback;
- supported player counts.

Required founder decisions:

- Pour placement;
- Last Call placement;
- Truth placement;
- which package supplies the sixth invocation if a game repeats;
- 2 to 3 player fallback for games with higher minimums.

The Grill automatic Beat 3 placement is already locked. The currency-funded
optional Grill is not part of this plan.

Pause for placement approval.

## Task 2: Author Registrations and Six Opportunities

**Files:**

- Modify: nightcap/couch-race.arc.json
- Modify: engine/tests/test_couch_race_arc_json.py
- Modify: engine/tests/test_couch_race_harness.py
- Modify: engine/tests/test_aw256_beat_hardcode.py

Write failing tests for:

- six non-empty opportunities;
- every registration references an existing exact package version;
- automatic Grill opportunity is separate from the beat object;
- no required package is used outside supported player counts;
- repetition is explicitly authored;
- fallback exists for every opportunity;
- no optional request or currency transaction behavior;
- all six beats remain reachable for 2 and 8 players.

Implement only approved placements. Verify and commit:

    git commit -m "feat(nightcap): author six minigame opportunities"

## Task 3: Map Nightcap Consequences

**Files:**

- Modify: nightcap/couch-race.arc.json
- Modify: nightcap/case_resolution_config.json only if approved spec requires
- Modify: engine/tests/test_resources_integration.py
- Modify: engine/tests/test_scoring_integration.py
- Modify: engine/tests/test_couch_race_harness.py

Write failing tests for generic mappings to:

- Leverage resource deltas;
- race-score deltas where approved;
- full and reduced investigative edges;
- public acknowledgements;
- no accusation-truth or killer-identity mutation;
- story remains solvable after every loss or timeout.

Keep Nightcap resource IDs in the arc and configuration, not generic engine
code. Verify and commit:

    git commit -m "feat(nightcap): map minigame story consequences"

## Task 4: Fix Production Stage Bootstrap

**Files:**

- Modify: nightcap-web/src/mini-games/stage.ts
- Modify: nightcap-web/src/mini-games/browser-entry.ts
- Modify: nightcap-web/src/mini-games/client.ts
- Modify: nightcap-web/src/runtime.ts
- Modify: nightcap-web/tests/mini-game-stage.test.ts
- Modify: nightcap-web/tests/mini-game-client.test.ts
- Modify: nightcap-web/tests/mini-game-client-race.test.ts

Write failing tests proving the rendered stage receives:

- session ID;
- scoped token;
- API base URL;
- exact package version;
- surface identity;
- adapter-neutral authoritative state;
- reconnect revision.

Implement without putting secrets into page content or routing private tokens
to another surface. Preserve phase state on fetch and reconnect.

Verify and commit:

    npm --prefix nightcap-web test
    npm --prefix nightcap-web run typecheck
    git commit -m "fix(nightcap): bootstrap minigame stages"

## Task 5: Add Nightcap Theme Contract

**Files:**

- Modify: nightcap-web/src/design/tokens.base.ts
- Modify: nightcap-web/src/design/themes/midnight.ts
- Modify: nightcap-web/src/mini-game-kit/types.ts
- Modify: nightcap-web/src/mini-game-kit/define-renderer.ts
- Modify: nightcap-web/tests/mini-game-define-renderer.test.ts
- Modify: nightcap-web/tests/mini-game-perf.test.ts
- Modify: docs/specs/0069-nightcap-visual-design-system.md

Use the approved spec 0069 system. Write tests for semantic tokens, theme
switching, reduced motion, couch-distance typography, phone intimacy, shared
display staging, and missing optional assets.

Do not create a second design system or hardcode one session skin inside a
game renderer.

Verify and commit:

    git commit -m "feat(nightcap): theme minigame surfaces"

## Task 6: Restore Inline-script Safety Coverage

**Files:**

- Modify: nightcap-web/tests/ui.test.ts
- Modify only if the approved fix requires: nightcap-web/src/ui.ts
- Update after pass: GitHub issue #270

Recreate the safe portion of reverted PR #271 against current main. Extract
the actual embedded scripts and execute them in an isolated VM. Prove no
ReferenceError and no private marker leak.

Only after coverage passes, decide whether issue #270's helper dedup remains
worth doing. Keep cosmetic refactoring separate from mini-game integration.

Commit:

    git commit -m "test(nightcap): cover embedded page scripts"

## Task 7: Add Six-opportunity Integration Tests

**Files:**

- Modify: engine/tests/test_couch_race_harness.py
- Modify: api/tests/test_mini_games_api.py
- Modify: nightcap-web/tests/mini-game-privacy-matrix.test.ts
- Modify: nightcap-web/tests/runtime.test.ts

Cover 2 and 8 players, every beat, fallback, reconnect, pause/resume, one
allowed repeat, exact package version, generic consequence events, and private
payload matrix. Use placeholder test adapters for games not yet game-ready;
do not mark package readiness passed from this foundation test.

## Task 8: Verify and Reconcile

Run focused engine, API, SDK, and Nightcap web checks. Update AW-285, reduced
AW-288, M5-I, AW-286, specs, and GitHub issues with exact foundation evidence.
Keep all individual game-ready criteria open. Pause for founder approval before
starting Tell Me Something True.
