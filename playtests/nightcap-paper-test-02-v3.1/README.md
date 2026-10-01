# Nightcap Paper Test #2 v3.1 - A Knock at Midnight

**Status:** Draft successor fixture. Local implementation and validation are in progress. Founder artifact review, publishing, phone smoke, and external tester release remain separate gates.

**Fixture ID:** `nightcap-paper-test-02-v3.1`
**Fixture version:** `3.1`
**Proposed route:** `/nightcap/paper-test-02/v3.1/`
**Case:** *A Knock at Midnight*
**Canon:** NON-CANON RESEARCH FIXTURE
**Instrument:** Jotform form `262397917027062`, version `2.2`; fields, scales, hidden names, and redirect are unchanged.

This draft copies the v3.0 case as an immutable successor baseline. Task 1 changes identity and research analysis, not gameplay. The remaining implementation tasks in `docs/superpowers/plans/2026-10-01-nightcap-v3.1-improvements.md` must complete before this fixture is considered locally ready. Its catalog entry is deferred to Task 6; `current_tests.nightcap` still points to v3.0.

The solo lock race, one test-granted Leverage, deterministic authored rival, four/five-fact Case File, and fixed mystery truth are research scaffolding. They do not validate production multiplayer balance, final Case Board or Structured Reconstruction UI, full accessibility, real-phone behavior, final minigame pool, production runtime, or player enjoyment.

The fixture records anonymous, session-scoped ordered events. `prototype_version` is `3.1`; the unchanged survey instrument version is `2.2`. The analysis protocol is `docs/gdd/nightcap/02-validation/99-paper-test-02-v3.1-analysis-plan.md`. Private tester notes and debrief responses stay out of telemetry and this repository.

A local static build or test run does not verify Jotform submission, redirect, reveal return, or live Pages behavior. The actual form return target has not been confirmed. No survey mutation or submission is part of this draft.

## Local checks

Run the explicit files in `tests/` with `node --test`. This checkout's Node binary may emit `MODULE_TYPELESS_PACKAGE_JSON` for JavaScript ES modules. The research helpers in `research.js` are offline analysis only and are not imported by the game.
