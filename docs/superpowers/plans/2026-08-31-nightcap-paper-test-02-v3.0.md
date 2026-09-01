# Nightcap Paper Test #2 v3.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a new immutable Playtest Lab fixture for the approved non-canon case **A Knock at Midnight**, preserving Paper Test #2 v2.2 while re-running Gate 1 with stronger detective agency, player-owned inference, visible rivalry, a story-wrapped lock-picking pulse, bounded Leverage, stable telemetry, refresh/re-entry safety, and deterministic endgame resolution.

**Architecture:** Reuse the dependency-free static Playtest Lab shell from `playtests/nightcap-paper-test-02-v2.2/`, but create a separate `playtests/nightcap-paper-test-02-v3.0/` source tree. Keep case truth, evidence topology, rival state, lock-picking outcome, Leverage state, and Case File options authored and deterministic in fixture configuration/runtime code. Do not modify production Nightcap, engine, API, SDK, dashboard, or mini-game packages. Do not overwrite v2.2, promote v3.0 to current, edit Jotform, or publish without separate founder approval.

**Tech Stack:** Static HTML, CSS, vanilla JavaScript, Node built-in test runner, Python standard-library Playtest Lab catalog/build scripts.

**Spec:** Approved founder checkpoints in the project conversation plus `docs/gdd/nightcap/00-governance/02-current-design-state.md`, `docs/gdd/nightcap/02-validation/98-validation-state-and-remaining-plan.md`, `docs/specs/nightcap-external-playtest-harness.md`, `playtests/AGENTS.md`, `docs/skills/arcwright-playtest-harness/SKILL.md`, and `docs/skills/arcwright-playtest-research/SKILL.md`.

## Global Constraints

- Base authority commit is `d62f01c37194721c07db019e8d1431df582e4174` until the reconciliation branch is merged.
- Fixture is non-canon and must not reuse The Last Toast characters, murder, clues, or narrative structure.
- Published v2.2 files, route, ID, and catalog substance remain untouched.
- v3.0 working ID is `nightcap-paper-test-02-v3.0`; working source directory is `playtests/nightcap-paper-test-02-v3.0`; working route is `/nightcap/paper-test-02/v3.0/`.
- `current_tests.nightcap` remains `nightcap-paper-test-02-v2.2` until separate promotion approval.
- Do not hand-edit `playtests/catalog.json` in this environment because `playtests/AGENTS.md` requires metadata scaffolding through `scripts/playtest_tool.py`; catalog creation remains a local/CLI handoff unless that command can be run.
- No Jotform mutation, verification submission, Pages deployment, PR comment, or promotion without separate action-time approval.
- One canonical ordered event stream is the telemetry source of truth. Legacy summary fields may be derived for compatibility but may not become a second authoritative event model.
- The static harness may simulate a simultaneous lock-picking race for research, but must label it as a fixture hypothesis. Existing production Evidence Locker supports one selected active picker in 2–8-player sessions and must not be represented as already supporting simultaneous pickers.
- Essential murder proof must remain reachable after lock win, loss, break, timeout, abort, and refresh/re-entry.
- Player-facing copy states observations and consequences, not deductions.
- Final names: Gideon March, Clara Hensley, Lenora Quill, Edwin Rusk, Beatrice Ashcombe.
- Canonical culprit: Clara Hensley.
- Canonical murder: Clara kills Gideon in the writing room before the séance, substitutes cylinder 43 into Quill's concealed playback apparatus, and Quill unknowingly plays the recording during the séance, creating a false later-alive impression.
- The Locked Box consequence is temporary private first access to cylinder 43, followed by normal availability; fallback makes the cylinder public.
- The fixture begins the human tester with exactly one test-granted Leverage so the Gate 1 instrument tests comprehension/choice without asserting a production Leverage sourcing rule.
- No em dashes in player-facing copy.

---

### Task 1: Freeze the approved case and research contract

**Files:**
- Create: `playtests/nightcap-paper-test-02-v3.0/README.md`
- Create: `playtests/nightcap-paper-test-02-v3.0/case.json`
- Test: `playtests/nightcap-paper-test-02-v3.0/tests/fixture.test.mjs`

**Interfaces:**
- Consumes: approved Gate 1 test-intent contract and Founder Gates 2–5.
- Produces: immutable fixture metadata, canonical truth/evidence graph, event IDs, suspect knowledge boundaries, and explicit deferred research claims used by all later tasks.

- [ ] **Step 1: Write the fixture test first**

Create assertions that load `case.json` and require:

```js
assert.equal(caseData.fixture_id, "nightcap-paper-test-02-v3.0");
assert.equal(caseData.fixture_version, "3.0");
assert.equal(caseData.non_canon, true);
assert.equal(caseData.culprit_id, "clara-hensley");
assert.equal(caseData.suspects.length, 4);
assert.equal(caseData.essential_truths.length, 4);
assert.ok(caseData.investigation.opening_opportunities.length >= 4);
assert.equal(caseData.competition.game_id, "the-locked-box");
assert.equal(caseData.leverage.starting_amount, 1);
assert.equal(caseData.leverage.source_claim, "test-granted; production sourcing not validated");
assert.ok(caseData.fallbacks.lock_failure_releases_cylinder_publicly);
```

Also assert that all four essential truths have at least two evidence routes and that no route marks the lock minigame as required.

- [ ] **Step 2: Run the focused fixture test and confirm it fails because `case.json` does not exist**

Run:

```bash
node --test playtests/nightcap-paper-test-02-v3.0/tests/fixture.test.mjs
```

Expected: FAIL with file-not-found/module-load error for `case.json`.

- [ ] **Step 3: Create `case.json` with the approved canonical architecture**

Encode:

```text
Opening opportunities: writing room, Gideon's materials, séance room/apparatus, people.
Essential truths:
T1 later voice was prerecorded;
T2 murder occurred before the apparent live voice;
T3 Clara leaked Gideon's confidential research to Quill and Gideon discovered it;
T4 Clara killed Gideon and staged the later-alive impression.
Key object chain: Gideon -> Clara -> Quill apparatus -> Edwin Rusk -> locked box -> finder/public fallback.
Suspect secrets: Quill fraud; Rusk hotel complicity/evidence concealment; Beatrice threat/eavesdropping/private letters; Clara leak/murder/recording substitution.
```

Do not encode a player-facing conclusion string for any evidence item.

- [ ] **Step 4: Create README with the immutable research boundary**

Document fixture/version, non-canon status, hypotheses H1–H5, explicit exclusions, solo authored-rival limitation, lock-race research abstraction, telemetry contract, survey/reveal-return blocker, and the rule that v2.2 is untouched.

- [ ] **Step 5: Run the focused fixture test**

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add playtests/nightcap-paper-test-02-v3.0/README.md playtests/nightcap-paper-test-02-v3.0/case.json playtests/nightcap-paper-test-02-v3.0/tests/fixture.test.mjs
git commit -m "test(nightcap): freeze paper test v3 case contract"
```

### Task 2: Build the dependency-free investigation runtime shell

**Files:**
- Create: `playtests/nightcap-paper-test-02-v3.0/index.html`
- Create: `playtests/nightcap-paper-test-02-v3.0/styles.css`
- Create: `playtests/nightcap-paper-test-02-v3.0/runtime.js`
- Create: `playtests/nightcap-paper-test-02-v3.0/app.js`
- Create: `playtests/nightcap-paper-test-02-v3.0/.nojekyll`
- Test: `playtests/nightcap-paper-test-02-v3.0/tests/runtime.test.mjs`

**Interfaces:**
- Consumes: `case.json` IDs and research contract from Task 1.
- Produces: state machine, event stream, session persistence, bounded-open investigation rendering, evidence ownership, rival activity, Last Call, Case File, survey handoff, and reveal mode.

- [ ] **Step 1: Write runtime tests for initial state and event ordering**

Require `createInitialState()` to return a state containing:

```js
{
  fixtureVersion: "3.0",
  phase: "opening",
  runId: <non-empty string>,
  leverage: 1,
  discoveries: [],
  investigatedTargets: [],
  eventSequence: [],
  lock: { status: "unavailable", winner: null, firstLookClaimed: false },
  caseFile: { culprit: null, pieces: [] }
}
```

Require `recordEvent(state, event)` to append monotonically increasing `sequence`, elapsed milliseconds, `phase`, `event_type`, `target`, `choice`, and `outcome`.

- [ ] **Step 2: Run runtime tests and confirm failure**

Run:

```bash
node --test playtests/nightcap-paper-test-02-v3.0/tests/runtime.test.mjs
```

Expected: FAIL because runtime exports do not exist.

- [ ] **Step 3: Implement minimal state/runtime functions**

Export deterministic helpers for:

```js
createInitialState
recordEvent
persistState
restoreState
completeOpening
chooseInvestigation
recordDiscovery
triggerRivalActivity
openLockWindow
resolveLock
resolveFirstLook
spendLeverage
enterLastCall
commitCaseFile
buildSurveyUrl
isRevealMode
```

Persist exact state in `sessionStorage` under a v3-specific key. Re-entry must not duplicate investigation choices, lock resolution, first-look delivery, Leverage spend, Last Call, or Case File commitment.

- [ ] **Step 4: Build the player-facing app shell**

Render:

```text
short cinematic opening -> four concrete opening opportunities -> discoveries/follow-ups -> visible rival actions -> Locked Box -> Leverage decision -> continued bounded-open investigation -> Last Call -> compact Structured Reconstruction -> survey handoff -> reveal page
```

Use natural labels such as `Writing Room`, `Gideon's Things`, `Séance Room`, and suspect names. Do not display `HUNT`, `THINK`, `PLAY`, `Leverage family`, `proof route`, or graph terminology as unexplained UI labels.

- [ ] **Step 5: Add responsive styles**

Keep touch targets at least 44 CSS pixels, avoid color-only meaning, support reduced motion, keep the primary investigation choices visible without horizontal scrolling at 360 CSS-pixel width, and preserve readable contrast.

- [ ] **Step 6: Run runtime tests**

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add playtests/nightcap-paper-test-02-v3.0/index.html playtests/nightcap-paper-test-02-v3.0/styles.css playtests/nightcap-paper-test-02-v3.0/runtime.js playtests/nightcap-paper-test-02-v3.0/app.js playtests/nightcap-paper-test-02-v3.0/.nojekyll playtests/nightcap-paper-test-02-v3.0/tests/runtime.test.mjs
git commit -m "feat(nightcap): add v3 investigation runtime shell"
```

### Task 3: Implement The Locked Box and bounded Leverage consequence

**Files:**
- Modify: `playtests/nightcap-paper-test-02-v3.0/runtime.js`
- Modify: `playtests/nightcap-paper-test-02-v3.0/app.js`
- Modify: `playtests/nightcap-paper-test-02-v3.0/styles.css`
- Modify: `playtests/nightcap-paper-test-02-v3.0/tests/runtime.test.mjs`
- Modify: `playtests/nightcap-paper-test-02-v3.0/tests/fixture.test.mjs`

**Interfaces:**
- Consumes: lock trigger IDs from `case.json`, state/event helpers from Task 2.
- Produces: research-only simultaneous lock-race abstraction, deterministic solo-rival outcome path, first-look consequence, public fallback, and Listen In / Follow the Thread choices.

- [ ] **Step 1: Add failing tests for all lock outcomes**

Test:

```text
human win -> human private first look -> cylinder later public
rival win -> Leverage Listen In offered -> spend copies observation / save preserves point
break -> public cylinder fallback
 timeout -> public cylinder fallback
abort -> public cylinder fallback
refresh during active lock -> same pin/progress state
refresh after resolution -> no second winner or second first-look event
```

Also assert that every outcome leaves at least one non-lock route to each essential truth.

- [ ] **Step 2: Run focused tests and confirm failure**

- [ ] **Step 3: Implement lock interaction**

Use a compact four-pin pressure-style lock inspired by the existing Evidence Locker package, but mark the fixture implementation as research simulation rather than production package execution. The human control reveals one pin target at a time; releasing inside tolerance sets a pin; a red-zone/wrong release breaks the pick. The deterministic authored rival advances on a fixed schedule derived only from fixture state, never from the tester's hidden theory.

- [ ] **Step 4: Implement result consequences**

Human win grants the cylinder-43 observation privately first. Rival win creates a `Listen In` opportunity. Break/timeout/abort releases the same cylinder observation publicly. After the finite first-look window, the cylinder becomes normal investigation material in every successful outcome.

- [ ] **Step 5: Implement bounded Leverage**

Expose only contextual `Listen In` and `Follow the Thread`. `Listen In` copies the rival's next private observation; `Follow the Thread` unlocks one contextual follow-up after an eligible suspect interaction. Spending cannot change truth or delete proof.

- [ ] **Step 6: Run focused runtime + fixture tests**

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add playtests/nightcap-paper-test-02-v3.0
git commit -m "feat(nightcap): integrate locked-box competitive pulse"
```

### Task 4: Add structured reconstruction, reveal, and telemetry integrity

**Files:**
- Modify: `playtests/nightcap-paper-test-02-v3.0/case.json`
- Modify: `playtests/nightcap-paper-test-02-v3.0/runtime.js`
- Modify: `playtests/nightcap-paper-test-02-v3.0/app.js`
- Modify: `playtests/nightcap-paper-test-02-v3.0/tests/runtime.test.mjs`
- Modify: `playtests/nightcap-paper-test-02-v3.0/tests/fixture.test.mjs`

**Interfaces:**
- Consumes: player-owned discoveries/evidence state.
- Produces: short deterministic Case File commitment, survey-prefill compatibility, reveal-only truth presentation, and testable telemetry derivations.

- [ ] **Step 1: Add failing Case File tests**

Require the correct reconstruction to include Clara plus a compact causal chain establishing prerecorded voice/false chronology, Clara's betrayal/motive, and Clara's murder/staging role. Allow authored equivalent evidence IDs for each essential truth. Reject a culprit-only guess and reject a theory that uses evidence the player never encountered where ownership matters.

- [ ] **Step 2: Add telemetry tests**

Assert the ordered event stream can derive:

```text
time to first investigation
time to first discovery
time to first observable inference action
route diversity
lock result and completion time
Leverage offer/spend/save
post-lock time to next murder-facing action
Last Call time
Case File commitment
completion/abandonment state
survey handoff initiation
```

Require the same `run_id` in fixture state and survey-prefill fields.

- [ ] **Step 3: Implement Case File**

Use tapping/selecting/arranging rather than free-text essays. Do not filter available pieces down to only important/correct evidence. Do not reveal correctness before lock.

- [ ] **Step 4: Implement survey handoff compatibility**

Build the Jotform URL from the existing approved field mapping without editing the form. Include fixture/version/run ID and derived legacy fields. Record `survey_handoff` before navigation.

- [ ] **Step 5: Implement reveal route behavior**

`?reveal=1` displays the canonical truth and verdict from authored data only. If the original same-tab `sessionStorage` state is available, record a local `reveal_return` event in state. Do not claim this local event is externally verified research evidence; README must keep reveal-return proof as a blocker until an approved external observation mechanism exists.

- [ ] **Step 6: Run runtime + fixture tests**

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add playtests/nightcap-paper-test-02-v3.0
git commit -m "feat(nightcap): add v3 case commitment and telemetry"
```

### Task 5: Run writing, fairness, and harness review passes

**Files:**
- Modify as findings require: `playtests/nightcap-paper-test-02-v3.0/case.json`
- Modify as findings require: `playtests/nightcap-paper-test-02-v3.0/app.js`
- Modify as findings require: `playtests/nightcap-paper-test-02-v3.0/README.md`
- Modify as findings require: tests under `playtests/nightcap-paper-test-02-v3.0/tests/`

**Interfaces:**
- Consumes: complete v3 fixture.
- Produces: reviewed fixture with documented residual risks, not a published/current test.

- [ ] **Step 1: Story Skills continuity audit**

Check character knowledge, cylinder ownership/location, Clara's visible alibi, Quill's ignorance of the substitution, Rusk's discovery/concealment, Beatrice's eavesdropping, setup/payoff ordering, and every testimony line against hidden truth.

- [ ] **Step 2: Mystery fairness audit**

For each essential truth, trace at least two reachable routes after lock win/loss/failure and after one plausible red-herring-first route. Add a fixture assertion for any route whose fairness currently depends on prose memory.

- [ ] **Step 3: haowjy reader-experience audit**

Read as three bounded personas: mystery-literate player, casual party-game player, impatient/mobile player. Flag supplied conclusions, document homework, dead-end choices, terminology friction, and post-minigame flow breaks. Fix architecture/copy only where the audit finds a specific defect.

- [ ] **Step 4: Sepia review**

Run review-only architecture/discourse/style diagnosis. Correct over-tidy causality, thematic explanation, repetitive reveal cadence, generic AI-like copy, or over-coordinated character presentation without changing approved murder facts.

- [ ] **Step 5: Harness preflight checklist**

Verify from source/tests: refresh/re-entry, no duplicate resolution, win/loss/break/timeout/abort, Leverage spend/save, alternate investigation routes, red-herring-first route, Case File without direct cylinder path, mobile-width CSS contract, survey handoff event, and reveal-return explicitly marked unverified externally.

- [ ] **Step 6: Run all focused fixture tests**

```bash
node --test playtests/nightcap-paper-test-02-v3.0/tests/runtime.test.mjs playtests/nightcap-paper-test-02-v3.0/tests/fixture.test.mjs
```

Expected: PASS.

- [ ] **Step 7: Commit review fixes**

```bash
git add playtests/nightcap-paper-test-02-v3.0
git commit -m "test(nightcap): harden paper test v3 fixture"
```

### Task 6: Prepare Playtest Lab metadata handoff without promotion

**Files:**
- Do not hand-edit `playtests/catalog.json` in this environment.
- Read-only reference: `playtests/catalog.json`
- Read-only reference: `scripts/playtest_tool.py`

**Interfaces:**
- Consumes: completed fixture tree.
- Produces: exact metadata command for an approved local/Codex execution and a list of remaining external blockers.

- [ ] **Step 1: Define metadata values**

Use:

```text
id: nightcap-paper-test-02-v3.0
game: nightcap
version: 3.0
title: Nightcap Paper Test #2 v3.0
route: /nightcap/paper-test-02/v3.0/
source_dir: playtests/nightcap-paper-test-02-v3.0
status: draft
instrument_id: 262397917027062
instrument_version: 2.2 until an approved instrument change creates a new externally real version
published: use the actual promotion/publication date only when promotion is approved
```

Do not set `current_tests.nightcap` to v3.0.

- [ ] **Step 2: Produce the Steward CLI handoff**

Prepare the exact `python scripts/playtest_tool.py --json new ...` command supported by the current CLI after checking its argument schema. If the CLI requires a publication date for drafts, use the actual creation date only if its contract defines that field as artifact creation rather than public publication; otherwise stop and report the mismatch rather than inventing semantics.

- [ ] **Step 3: Record blockers**

Before external testing, require:

```text
catalog draft scaffold + validation
instrument/reveal-return observation decision
any required Jotform version/change approval
static site build
mobile/manual smoke evidence
promotion-to-current approval
Pages deployment approval
live route/reveal verification
```

- [ ] **Step 4: Stop before external side effects**

Do not edit Jotform, submit smoke data, promote current, publish Pages, or open a PR solely to trigger deployment without explicit founder action-time approval.

## Self-Review

- Spec coverage: all approved case truth, investigation topology, rivalry, lock-picking pulse, Leverage, Case File, telemetry, refresh/re-entry, writing-skill audits, and harness blockers map to explicit tasks.
- Placeholder scan: no implementation placeholder is authorized; remaining unverified external actions are explicit stop conditions rather than TODOs.
- Type/name consistency: fixture/version IDs, final character names, lock game ID, run ID, event stream, and Leverage amount are consistent across tasks.
