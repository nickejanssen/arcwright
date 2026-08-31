# Nightcap — Paper Test #2 v2.2 Handoff Requirements

**Status:** COMPLETED DIAGNOSTIC TEST SPEC — historical validation record, not game canon  
**Purpose:** Preserve the requirements used to build and run the already-completed v2.2 external test harness.

## Infrastructure state

The external testing infrastructure exists outside the GDD:

- GitHub Pages paper-test harness;
- Jotform post-play survey;
- harness/telemetry integration.

This file does not own or redesign that infrastructure.

## Result

Paper Test #2 v2.2 is complete as a diagnostic test and **did not pass Gate 1 — Representative Time-to-Fun / Cohesion**.

The fixture, *The Last Toast*, remains **NON-CANON**. Do not patch it into the next canonical design or reuse it as the next validation case.

The post-test GDD reconciliation is captured in the current Decision Ledger and authoritative system pages. Current validation status lives in `98-validation-state-and-remaining-plan.md`.

## Original v2.2 direction

The test was designed as a fuller representative slice:

- fresh purpose-built microcase;
- fixture title: **The Last Toast**;
- simple crime with layered proof;
- 4 meaningful suspects;
- 1 real solo tester + 1 visible authored rival with bounded deterministic reactions;
- scene-first observation as the investigation entry;
- 5 major investigation decisions;
- no explicit theory checkpoints during play;
- one short story-wrapped minigame contesting first access to a newly exposed lead;
- one minimal-but-real Leverage / information-warfare decision;
- strong story reactivity and fast re-entry;
- short Case File-style commitment before the survey;
- target roughly 15–20 minutes of meaningful play.

## Original critical experience requirement

The intended pattern was:

**observe → choose → discover → wonder → act → consequence → new question**

rather than:

**choose option → receive clue card → choose another option**

The actual tester feedback showed that the fixture still too often interpreted discoveries for the player and used system-style vocabulary, which is why the current GDD now makes player-owned inference, rich observation, contextual onboarding, and player-facing language boundaries more explicit.

## Test-only rival boundary

The authored rival created competitive pressure for Gate 1 only.

It is **not multiplayer evidence** and must never be used to claim that real two-player or larger-group social play has been validated. The current GDD's rival-visibility rules concern real Nightcap player rivalry; Rhea remains fixture-specific research scaffolding.

## Evidence limitations

The three survey submissions did not verify the full QA/path matrix. Telemetry contracts were inconsistent across submissions. Survey handoff was explicitly evidenced in only one telemetry stream and post-survey reveal return was not verified in any submission.

Do not use this test to claim validation of:

- alternate proof-route equivalence;
- red-herring fairness;
- minigame-loss satisfaction;
- multiplayer competition;
- exact runtime;
- exact memory-support requirement;
- production Structured Reconstruction UX.

## Successor rule

The next Gate 1 test must be a **brand-new non-canon mystery/story fixture** built from the revised current GDD, with a new immutable fixture/instrument version and one canonical telemetry contract. Define its hypotheses and validation contract before authoring/publishing it.

No next-case content is authorized by this historical file.