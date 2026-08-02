# Nightcap Existing Mini-games Game-ready Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to execute
> this plan task by task. Do not begin without separate founder approval.

**Goal:** Convert every existing Nightcap package, prototype, and identified
Couch Race mini-game into a tuned, themed, competitive, seamless, production
experience.

**Architecture:** Every game uses the approved hosted adapter and generic
opportunity, invocation, result, consequence, theme, and certification
contracts. Gameplay rules remain game-owned. Arcwright owns narrative
orchestration and canonical consequences.

**Current baseline:** Three authored packages, two active catalog entries, one
complete deterministic mechanic, zero production package renderers, and zero
game-ready packages. Interrogation Room is a prototype and draft spec, not a
package. The Grill is a structured interaction loop, not a package.

---

## Common Gate for Every Game

Before each game:

1. refresh origin/main and merged PR overlap;
2. create or update its canonical spec;
3. present a gameplay and session-fit artifact;
4. obtain founder direction approval;
5. obtain separate implementation approval;
6. write mechanic tests before code;
7. implement in reviewable mechanic, renderer, and integration slices;
8. run automated certification;
9. run real-device walkthrough;
10. run required real-player rehearsal;
11. reconcile the game issue, task, spec, plan, epic, and readiness report.

Do not promote from draft or playtest to active solely from automated checks.

## Task 1: Tell Me Something True Migration Canary

**Files:**

- Modify: nightcap/mini_games/tell-me-something-true/manifest.json
- Create: docs/specs/0081-tell-me-something-true-game-ready.md
- Create: nightcap/mini_games/tell-me-something-true/definitions/0.2.0.json
- Create: nightcap/mini_games/tell-me-something-true/client/renderer.ts
- Create: nightcap/mini_games/tell-me-something-true/client/styles.css
- Create: nightcap/mini_games/tell-me-something-true/client/renderer.test.ts
- Modify: engine/mini_games/plugins/_social_truth_bluff.py only for approved defects
- Modify: engine/tests/test_social_truth_bluff_runtime.py
- Modify: api/routers/mini_games.py
- Modify: api/tests/test_mini_games_api.py
- Modify: sdk/src/types.ts
- Modify: nightcap-web/src/mini-games/client.ts
- Modify: docs/roadmap/tasks/AW-262-tmst-package-authoring-and-schema-resolution.md
- Modify: docs/roadmap/tasks/AW-263-tmst-runtime-social-truth-bluff-mechanic.md
- Modify: docs/roadmap/tasks/AW-264-tmst-api-events-and-sdk.md
- Modify: docs/roadmap/tasks/AW-265-tmst-web-rendering-four-phases.md
- Modify only after the founder resolves its status:
  docs/roadmap/tasks/AW-266-rehearsal-2-tmst-real-human-session.md

**Gameplay checkpoint**

Review the existing four-phase design against Couch Race:

- session story role and beat placement;
- 2 to 3 player behavior versus its current 4-player minimum;
- total duration and dead-air risk;
- Leverage or race-score consequence;
- phone and shared-display attention rhythm;
- competition, reveal spectacle, and failure grace;
- Nightcap theme and motion.

Obtain placement and low-player fallback approval.

**TDD implementation**

1. Add failing tests for exact-version state, reconnect phase restoration,
   low-player eligibility, AFK, duplicate and late actions, consequence
   idempotency, and privacy.
2. Remove FastAPI and SDK game-ID branches by routing mechanic-specific
   validation and projections through the hosted adapter.
3. Build package-local phone, shared-display, and host renderers.
4. Add semantic theme, motion, reduced-motion, accessibility, and performance.
5. Bind only after the package passes playtest gates.

**Verification**

- social truth/bluff runtime tests;
- API and SDK tests;
- renderer snapshots and interaction tests;
- 2, 4, and 8 player deterministic runs;
- real-device phase walkthrough;
- real-human social-flow rehearsal.

Commit slices:

    feat(nightcap): migrate tell me something true
    feat(nightcap): render tell me something true
    test(nightcap): certify tell me something true

## Task 2: Crime Scene Smash

**Files:**

- Modify: nightcap/mini_games/crime-scene-smash/manifest.json
- Create: docs/specs/0082-crime-scene-smash-game-ready.md
- Create: nightcap/mini_games/crime-scene-smash/definitions/0.2.0.json
- Replace reference-only behavior under: nightcap/mini_games/crime-scene-smash/client
- Modify: engine/mini_games/plugins/_match_3_clue_race.py
- Create: engine/tests/test_match_3_clue_race_runtime.py
- Create: nightcap/mini_games/crime-scene-smash/client/renderer.ts
- Create: nightcap/mini_games/crime-scene-smash/client/renderer.test.ts

**Gameplay checkpoint**

Lock:

- board generation and replay seed;
- valid move and match rules;
- input payload;
- score and combo formula;
- deterministic tie-break replacing tie_break: narrative;
- 2 to 8 player scaling;
- shared-display leaderboard rhythm;
- Leverage, score, or investigative-edge reward;
- 90 to 120 second ceiling;
- theme, graphics, animation, sound, and final-five countdown.

**TDD implementation**

1. Write failing board, match, score, tie, concurrency, timeout, and replay tests.
2. Implement authoritative plugin without client-calculated score.
3. Normalize clues or consequence semantics to the approved runtime contract.
4. Build production renderer from the HTML prototype's useful visual and input
   ideas, not its client authority.
5. Add privacy, reconnect, accessibility, performance, and asset tests.
6. Run 2 and 8 player load and legibility checks.

Do not leave an active lifecycle on a package that raises NotImplementedError.

Commit slices:

    feat(nightcap): implement crime scene smash
    feat(nightcap): render crime scene smash
    test(nightcap): certify crime scene smash

## Task 3: Evidence Locker 402

**Files:**

- Modify: nightcap/mini_games/evidence-locker-402/manifest.json
- Create: docs/specs/0083-evidence-locker-402-game-ready.md
- Create: nightcap/mini_games/evidence-locker-402/definitions/0.2.0.json
- Replace reference-only behavior under: nightcap/mini_games/evidence-locker-402/client
- Modify: engine/mini_games/plugins/_evidence_locker_breach.py
- Create: engine/tests/test_evidence_locker_breach_runtime.py
- Create: nightcap/mini_games/evidence-locker-402/client/renderer.ts
- Create: nightcap/mini_games/evidence-locker-402/client/renderer.test.ts

**Gameplay checkpoint**

Lock:

- deterministic puzzle generation and answer model;
- how one active player is selected fairly;
- what other players do and watch;
- handoff and disconnect behavior;
- success, failure, timeout, and abort;
- story edge and fallback;
- repeatability;
- shared-display spectacle;
- theme and accessibility.

**TDD implementation**

1. Write failing participant-selection tests for 2 to 8 players.
2. Write puzzle, payload validation, completion, tie, timeout, reconnect, and
   exact-version tests.
3. Implement the hosted mechanic.
4. Replace success_clue and fallback_clue drift with approved normalized
   result semantics or runtime clue shape.
5. Build phone, shared-display, and host renderers.
6. Test selected-player privacy and non-selected-player engagement.

Commit slices:

    feat(nightcap): implement evidence locker 402
    feat(nightcap): render evidence locker 402
    test(nightcap): certify evidence locker 402

## Task 4: The Grill

**Files:**

- Create: docs/specs/0084-the-grill-interrogation-minigame.md
- Create: nightcap/mini_games/the-grill-interrogation
- Reuse and modify as approved: engine/interactions
- Reuse and modify as approved: engine/claims
- Reuse and modify as approved: engine/mini_games
- Modify: nightcap/couch-race.arc.json
- Create: engine/tests/test_the_grill_minigame.py
- Create: nightcap/mini_games/the-grill-interrogation/client/renderer.ts
- Create: nightcap/mini_games/the-grill-interrogation/client/renderer.test.ts

**Locked behavior**

- Beat 3 is titled The Grill.
- The mini-game is player-facing The Grill.
- Beat and mini-game remain separate typed objects.
- It runs automatically in Beat 3.
- Contracts may reserve a generic optional-request policy.
- No currency deduction, request UI, refunds, price, or cross-beat optional
  invocation is implemented now.

**Creative checkpoint**

Lock the core interrogation game loop:

- suspect choice and question intent;
- clue or claim purchase;
- visible room-watch state;
- asker credit;
- contradiction catch;
- competition and score or resource effect;
- turn pacing and shared participation;
- repeat-run content and state safety;
- catch audiovisual quality gate;
- 2 to 8 player fairness.

**TDD implementation**

1. Write tests that wrap existing structured interaction behavior without
   duplicating claim, contradiction, or suspect-answer authority.
2. Add package registration and result semantics.
3. Add automatic opportunity invocation.
4. Build phone notebook, shared-display suspect stage, and host operations.
5. Implement D-090 catch audiovisual gate, G3 asker credit, and G5 room-watch.
6. Verify replay, reconnect, privacy, repeated automatic test invocation, and
   no deferred currency behavior.

Commit slices:

    feat(nightcap): package the grill interrogation
    feat(nightcap): stage the grill interrogation
    test(nightcap): certify the grill interrogation

## Task 5: Interrogation Room Trivia

**Files:**

- Modify: docs/specs/0076-aw-289-interrogation-room.md
- Modify: docs/roadmap/tasks/AW-289-couch-race-trivia-mini-game.md
- Modify after approval: GitHub issue #258
- Create after approval: nightcap/mini_games/interrogation-room
- Create: engine/mini_games/plugins/_interrogation_room.py
- Create: engine/tests/test_interrogation_room_runtime.py
- Create: nightcap/mini_games/interrogation-room/client/renderer.ts
- Create: nightcap/mini_games/interrogation-room/client/renderer.test.ts

**Creative gate before package creation**

Refresh the brief against:

- D-093 story-spine and edge-not-gate;
- the approved six-opportunity placement;
- current AW-284 scoring and Leverage economy;
- general-first trivia with sparse case callbacks;
- deterministic answer and evidence provenance;
- adaptive room-momentum bounds;
- representative content;
- narrator framing;
- 2 to 8 player behavior;
- theme, motion, sound, and public leaderboard.

Obtain explicit approval of the brief, sample, scoring table, and narrator
direction. PR #259 and prototype completion do not grant implementation
approval.

**TDD implementation**

1. Validate generated questions before delivery.
2. Reject ambiguous, ungrounded, future, hidden, private, unsafe, or invalid
   questions without player penalty.
3. Grade answers and score deterministically.
4. Bound adaptation to approved observable signals.
5. Build private answer and public resolution renderers.
6. Verify content fallback, replay, reconnect, privacy, performance, and
   supported player range.

Commit slices:

    feat(nightcap): implement interrogation room
    feat(nightcap): render interrogation room
    test(nightcap): certify interrogation room

## Task 6: Six-beat Gameplay and Presentation Pass

**Files:**

- Modify: nightcap/couch-race.arc.json
- Modify: docs/specs/0068-game-experience-quality-bar.md only for approved
  Couch Race reconciliation
- Modify: docs/specs/0069-nightcap-visual-design-system.md
- Modify: docs/roadmap/operations/fun-observation-rubric.md

Review the session as one game, not five isolated features:

- story enhancement at every opportunity;
- competition and Leverage rhythm;
- seamless transitions into and out of gameplay;
- cumulative duration within 20 to 40 minutes;
- no repeated format fatigue;
- phones versus shared-display attention;
- consistent theme, graphics, animation, audio, and accessibility;
- result spectacle;
- story remains primary and fully solvable.

Tune opportunity placement and package configuration, not generic engine code.
Any gameplay change reopens that game's artifact approval as required.

## Task 7: Final Certification and Status Closeout

Generate readiness reports for all five games. Run the program end-to-end
certification and AW-286 rehearsal. Update all related specs, tasks, epics,
milestones, plans, GitHub issues, and PR evidence.

At completion, report separately:

- package active status;
- automated contract status;
- real-device status;
- real-player status;
- founder final sign-off;
- known non-blocking follow-ups.

Do not reopen D-097 implementation until the end-to-end gate is explicitly
confirmed complete.
