# Nightcap Paper Test #2 v3.1 - A Knock at Midnight

**Status:** Draft successor fixture. Local implementation and validation are in progress. Founder artifact review, publishing, phone smoke, and external tester release remain separate gates.

**Fixture ID:** `nightcap-paper-test-02-v3.1`
**Fixture version:** `3.1`
**Proposed route:** `/nightcap/paper-test-02/v3.1/`
**Case:** _A Knock at Midnight_
**Canon:** NON-CANON RESEARCH FIXTURE
**Instrument:** Jotform form `262397917027062`, version `2.2`; fields, scales, hidden names, and redirect are unchanged.

This draft is registered in the local Playtest Lab catalog with `published: null`. The investigation, lock, Case File and recovery changes have local automated coverage. Browser, founder and external evidence remain tracked in `docs/gdd/nightcap/03-playtest-evidence/99-paper-test-02-v3.1-validation.md`. `current_tests.nightcap` still points to v3.0.

The solo lock race, one test-granted Leverage, deterministic authored rival, four/five-fact Case File, and fixed mystery truth are research scaffolding. They do not validate production multiplayer balance, final Case Board or Structured Reconstruction UI, full accessibility, real-phone behavior, final minigame pool, production runtime, or player enjoyment.

The fixture records anonymous, session-scoped ordered events. `prototype_version` is `3.1`; the unchanged survey instrument version is `2.2`. The analysis protocol is `docs/gdd/nightcap/02-validation/99-paper-test-02-v3.1-analysis-plan.md`. Private tester notes and debrief responses stay out of telemetry and this repository.

The lock ready screen is untimed. Start begins the four-pin race and Nora's 19-second clock. An input at exactly 19 seconds belongs to Nora; the 45-second defensive timeout normally cannot be reached. Decline releases cylinder 43 publicly with no minigame duration. A human win permits an explicit Leverage save; a rival win permits Listen In or an explicit save when Leverage remains. First look closes after the next new major investigation or entering Last Call. Review and earned questions do not close it.

The moving marker remains the core interaction even with reduced-motion preferences. Focus is restored to Set pin between pins, and pin/result text is announced without announcing every frame. Decline is an exit with public evidence, not an equivalent accessible race. Keyboard, assistive technology, first-use timing and physical-device fairness need human observation before accessibility or difficulty claims. Nora's Quill accusation follows her authored observation of Quill controlling the trumpet, not the lock winner; her path is deterministic solo research scaffolding.

A local static build or test run does not verify Jotform submission, redirect, reveal return, or live Pages behavior. The read-only Jotform connector does not expose the actual form return target, and historical submissions cannot establish the landing page. No survey mutation or submission is part of this draft.

## Local checks

From the repository root, run `python scripts/playtest_tool.py --json validate` and `python scripts/playtest_tool.py --json build --output _site`. The local build contains the historical v2.2 and v3.0 routes plus the draft v3.1 route. A merge of this catalog entry could expose the draft route through Pages, even while the current pointer remains v3.0; release needs a separate decision.

Run `node --test` from this fixture for its full suite or `node --test tests/qa-contract.test.mjs` for the visibility contract. The Pages workflow names every historical and successor test file explicitly. This checkout's Node binary may emit `MODULE_TYPELESS_PACKAGE_JSON` for JavaScript ES modules. The research helpers in `research.js` are offline analysis only and are not imported by the game.

For local browser QA, serve `_site` with `python -m http.server 8765 --directory _site` from the repository root and open `http://localhost:8765/nightcap/paper-test-02/v3.1/`. Label each browser run as QA and record the viewport, browser, input method, observed action and run label in the validation ledger. Check desktop and 360 CSS-pixel layouts, keyboard focus, free earned questions at the action cap, refresh, visibility return after the lock deadline, and intact and missing-state reveal. Warn before starting a timed lock. A CSS viewport is not a physical phone or assistive-technology assessment.

The owner phone smoke requires separate readiness approval. On a real phone, play the draft in a normal same-tab session, enter `SMOKE TEST - exclude` in the first free-text survey field, submit, capture the landing page, and report approximate time. Read-only submission verification must then confirm version, run identity and hidden fields, and record the excluded run ID. A long-run transport submission requires its own approval. Do not treat the local 1,000-miss URL round trip as Jotform acceptance or a verified survey return.
