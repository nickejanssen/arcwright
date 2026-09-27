---
id: playtestops.superpowers.plans.2026-09-27-phase-1-v3-send-readiness
namespace: playtest-ops
title: Phase 1 v3.0 Send-Readiness Implementation Plan
owner: Nico Janssen
status: active
review_by: "2027-03-27"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Phase 1 v3.0 Send-Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:executing-plans to implement this plan task-by-task in this session. The work needs the built-in browser, the Jotform connector, and a founder present at gates, so do **not** hand tasks to subagents. Also follow `docs/skills/arcwright-playtest-harness/SKILL.md` (Tasks 1, 2, 5) and `docs/skills/arcwright-playtest-research/SKILL.md` (Tasks 3, 4). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Nightcap Paper Test #2 v3.0 safe to send to 6–8 external testers: bug-test the live fixture, prove survey data arrives, record the v2.2 baseline, and have the founder approve the pass bar before any invite goes out.

**Architecture:** Evidence and documentation only. The agent plays the live static fixture in the built-in browser, reads the Jotform survey read-only through the connector, and writes four new documents plus one status update under `docs/gdd/nightcap/`. No fixture, survey, catalog, Pages, engine, or tooling file changes.

**Tech Stack:** Built-in browser tools (`mcp__Claude_Browser__*`: `navigate`, `javascript_tool`, `find`, `computer`, `resize_window`, `read_network_requests`), Jotform connector (read tools only), Markdown, git, `gh`.

**Spec:** `docs/superpowers/specs/2026-09-27-phase-1-v3-send-readiness-design.md` (approved; read it before starting)

**User decisions (already made):**
- "Connect the connector": Jotform is read through the connector, read-only only.
- "6–8 new players": new means they never played v2.1 or v2.2 and have not seen the design.
- "Likely players, not close": people who play party or mystery games who are not close friends or family; friends-of-friends qualify.
- "A. Rules + thresholds": the founder approves the pass bar before the first invite.
- "Yes, move them": #207, #303, and the engine `duration_seconds` bug are out of Phase 1.
- "Yes, I'll do it": the founder does the smoke run on a real phone.
- "Yes, do it": the agent bug-tests the live v3.0 first.
- "Yes": the agent writes the v2.2 baseline.
- "Yes, write the spec": the invite kit, order, and fresh Claude Code session were approved.

---

## Founder steps (what Nico does, in order)

The agent asks for each step at the right moment. Nothing else needs the founder.

| # | When | What to do | Time |
|---|---|---|---|
| F1 | Start | Open a new Claude Code session in the arcwright repo and paste the handoff prompt. | 1 min |
| F2 | During Task 1 lock runs (the agent will say "lock runs starting") | Keep the Claude app open on screen with the **Browser pane showing**. Don't minimize the app or switch the pane away: the lock minigame only animates while visible. | about 10 min |
| F3 | Before Task 2 | In claude.ai, open **Settings → Connectors**, find **Jotform**, click **Connect**, sign in to the Jotform account that owns the Nightcap survey, and allow access. Then tell the session `Jotform connected`. If you can't find it, say `show me the Jotform connect button`. | 2 min |
| F4 | Task 4 gate | Open the analysis-plan link the agent sends and read it (1 page). Ask yourself: "If v3.0 scored exactly at these bars, would I honestly call it a pass?" Reply `approved`, or name the numbers to change. | 10 min |
| F5 | Task 5 gate | On your **phone**, in a normal (not private) browser tab, open `https://nickejanssen.github.io/arcwright/nightcap/paper-test-02/v3.0/`. Play to the end. **Stay in that tab** the whole time. When the survey opens, answer anything, but in the **first free-text box** type exactly `SMOKE TEST - exclude`. Submit, then screenshot the page you land on. Send the session `smoke run done`, the screenshot, and roughly when you submitted. Correct landing page: *A Knock at Midnight* and its solution. | 25 min |
| F6 | Task 6 | Review and merge the Phase 1 PR the agent opens. | 5 min |
| F7 | Task 6 gate | When the agent reports every check done, reply `go` to start Phase 2. | 1 min |

---

## Ground rules for the executor

- **Branch:** work on `claude/phase-1-v3-send-readiness`, which already holds the spec and this plan. First run `git fetch origin && git rebase origin/main` (Phase 0 merged to `main` after this branch was cut).
- **Never `cd` in Bash.** The repository's PreToolUse hook runs `python scripts/hooks/guard_kb_agents.py` by relative path, so after a `cd` into a subfolder every Bash call fails. Use absolute paths or `git -C`. If it happens anyway, recover with the PowerShell tool: `Set-Location <repo root>`.
- **Jotform is read-only.** Use only read tools: listing forms, fetching a form or its settings, searching, reading submissions. Never call `create_form`, `edit_form`, `create_submission`, `assign_form`, or any other tool that writes.
- **Never submit the survey, and never type into it.** The only submission in Phase 1 is the founder's smoke run.
- **Change nothing under `playtests/`.** That includes the fixture README, which is published. No catalog, Pages, or survey changes.
- **Tester privacy:** no names, emails, IPs, device identifiers, or verbatim free-text answers in the repository. Paraphrase themes only.
- **D-110 freeze:** don't touch `team-ai/`, `.claude/`, `docs/agents/`, `docs/skills/`, or hooks, even to fix the relative-path hook. Report it instead.
- **Stop and ask the founder** whenever a check fails outside the two documented gaps (#6 timeout, #14 abandonment), whenever a Jotform setting differs from the spec, or whenever this plan and the spec don't answer something.
- **The browser tool's 45-second limit:** `javascript_tool` calls time out after 45 seconds. Keep each call short: do navigation clicks in one call, and run the lock helper in its own call.

## File map

| File | Change | Task |
|---|---|---|
| `docs/gdd/nightcap/03-playtest-evidence/99-paper-test-02-v3.0-pre-send-qa.md` | Create: QA results, instrument inspection, smoke run | 1, 2, 5 |
| `docs/gdd/nightcap/03-playtest-evidence/98-paper-test-02-v2.2-results.md` | Create: v2.2 baseline | 3 |
| `docs/gdd/nightcap/02-validation/99-paper-test-02-v3.0-analysis-plan.md` | Create: pass bar (founder-approved) | 4 |
| `docs/gdd/nightcap/02-validation/99a-paper-test-02-v3.0-tester-brief.md` | Create: invite kit | 6 |
| `docs/gdd/nightcap/02-validation/98-validation-state-and-remaining-plan.md` | Modify: "Before external distribution" status (lines 130–138) | 6 |

Every new document starts with this front matter (fill in `id` and `title`):

```yaml
---
id: nightcap.gdd.nightcap.<folder>.<filename-without-.md>
namespace: nightcap
title: <Title>
owner: Nico Janssen
status: active
review_by: "2027-03-27"
sensitivity: internal
source: authored
tags: []
supersedes: []
---
```

For example, the QA file's id is `nightcap.gdd.nightcap.03-playtest-evidence.99-paper-test-02-v3.0-pre-send-qa`.

---

## Browser toolkit (used by Task 1)

Live URL: `https://nickejanssen.github.io/arcwright/nightcap/paper-test-02/v3.0/`. The fixture keeps its state in `sessionStorage` under `nightcap-paper-test-02-v3.0-state`.

**K0 Visibility check.** Run it before any lock helper. If the result is not `visible`, ask the founder for step F2 and wait.
```js
document.visibilityState
```

**K1 New run (reset).** After this call, the next call must wait for the page to load. K2's `waitFor` handles that.
```js
sessionStorage.removeItem('nightcap-paper-test-02-v3.0-state'); location.reload(); 'reset'
```

**K2 Click helpers.** Paste this at the top of every navigation script:
```js
const wait = (ms) => new Promise(r => setTimeout(r, ms));
const waitFor = async (sel, ms = 8000) => { const end = Date.now() + ms; while (Date.now() < end) { const el = document.querySelector(sel); if (el) return el; await wait(100); } throw new Error('timed out waiting for ' + sel); };
const click = async (sel) => { (await waitFor(sel)).click(); await wait(300); };
```

Selectors:
- `#startInvestigation`
- routes: `[data-route="writing-room"]`, `[data-route="gideon-materials"]`, `[data-route="seance-room"]`
- `#peopleChoice`, then a suspect: `[data-suspect="clara-hensley"]`, `[data-suspect="lenora-quill"]`, `[data-suspect="edwin-rusk"]`, `[data-suspect="beatrice-ashcombe"]`
- a suspect you already visited shows a "Revisit" button with the same `data-suspect`
- scene actions: `#backToCase`, `#challengeClaim` ("Challenge that claim"), `#followThread` ("Spend 1 Leverage: …")
- lock: `#openLock` ("Crack the box"), `#setPin`, `#abortLock` ("Back off")
- after the lock: `#returnFromLock`, `#listenIn`, `#saveLeverage`
- Last Call and Case File: `#enterLastCall` ("Lock my theory"), `#culpritSelect`, `input[name="evidence"][value="<id>"]`, `#commitTheory`
- survey: `#openSurvey`

To choose the culprit:
```js
const sel = await waitFor('#culpritSelect'); sel.value = 'clara-hensley'; sel.dispatchEvent(new Event('change'));
```
To tick a fact: `(await waitFor('input[name="evidence"][value="e-cylinder-transcript"]')).click();`

**K3 Event check.** Run this after every milestone in a run. It lists events in order and reports duplicates of once-only events.
```js
(() => {
  const s = JSON.parse(sessionStorage.getItem('nightcap-paper-test-02-v3.0-state'));
  const once = ['opening_complete','competitive_window_opened','minigame_started','minigame_result','first_look_closed','last_call','case_file_commitment','completion','survey_handoff','reveal_return'];
  const keyed = ['investigation_choice','discovery','rival_activity','leverage_choice','inference_action'];
  const counts = {};
  for (const e of s.eventSequence) {
    const k = once.includes(e.event_type) ? e.event_type : keyed.includes(e.event_type) ? `${e.event_type}:${e.target}:${e.choice ?? ''}` : null;
    if (k) counts[k] = (counts[k] ?? 0) + 1;
  }
  return {
    run_id: s.runId, phase: s.phase, leverage: s.leverage, lock: s.lock.status, lock_outcome: s.lock.outcome,
    events: s.eventSequence.map(e => `${e.sequence}:${e.event_type}${e.target ? '(' + e.target + ')' : ''}${e.outcome ? '=' + e.outcome : ''}`),
    duplicates: Object.entries(counts).filter(([, n]) => n > 1),
    abandonment_events: s.eventSequence.filter(e => e.event_type === 'abandonment').length
  };
})()
```
**Pass condition for K3:** `duplicates` is `[]`.

**K4 Lock helper.** Run it in its own call, after `#openLock` and after K0 returns `visible`. `mode` is `'win'` or `'break'`. It presses the game's real "Set pin" button when the moving marker is inside the current pin's band (`win`) or in a red end zone (`break`). Pin targets are from `case.json`: 22, 68, 41, 82, tolerance ±7, red below 7 and above 93. The helper uses ±4 so its presses land safely inside the game's band.
```js
const mode = 'win';
const KEY = 'nightcap-paper-test-02-v3.0-state';
const TARGETS = [22, 68, 41, 82];
const t0 = Date.now();
const result = await new Promise((resolve) => {
  let presses = 0;
  const step = () => {
    const s = JSON.parse(sessionStorage.getItem(KEY));
    if (!s || s.lock.status !== 'active') return resolve({ outcome: s?.lock?.outcome ?? null, presses });
    const marker = document.querySelector('#marker');
    const button = document.querySelector('#setPin');
    if (marker && button) {
      const v = parseFloat(marker.style.left);
      const hit = mode === 'win' ? Math.abs(v - TARGETS[s.lock.currentPin]) <= 4 : (v <= 4 || v >= 96);
      if (hit) { button.click(); presses += 1; }
    }
    if (presses > 12 || Date.now() - t0 > 30000) return resolve({ outcome: 'helper-gave-up', presses });
    requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
});
({ ...result, seconds: ((Date.now() - t0) / 1000).toFixed(1), heading: document.querySelector('h2')?.textContent })
```
Expected: `win` → `outcome: 'human-win'` within about 15s, heading "You get the box open first."; `break` → `outcome: 'break'`, heading "The lock wins the argument." If it returns `helper-gave-up` or `rival-win`, check K0. If the page was visible and it still failed, stop and report: the helper is unproven on the live site, and this is its first real test.

**K5 Refresh.** Call `mcp__Claude_Browser__navigate` with the same live URL. `sessionStorage` survives in the same tab. Then run K3.

---

### Task 1: Pre-send QA on the live v3.0

**Goal:** Every situation in the spec's 16-row checklist is tested on the live fixture, and the results are written to the QA evidence file.

**Files:**
- Create: `docs/gdd/nightcap/03-playtest-evidence/99-paper-test-02-v3.0-pre-send-qa.md`

**Acceptance Criteria:**
- [ ] Runs A–F below are executed on the live URL, and K3 reports `duplicates: []` at every checkpoint.
- [ ] Situations 1–5, 7–13, 15 and 16 are recorded as PASS with their `run_id`, viewport, and event list.
- [ ] #6 (timeout) and #14 (abandonment) are recorded as documented gaps, with the observed evidence: rival-win at about 19s with no pins set, and `abandonment_events: 0`.
- [ ] #16's `run_id` is listed under "Excluded run_ids".
- [ ] The 360px run (#15) has screenshots of the opening, choices, lock, and Last Call screens, plus the measured results: `scrollWidth <= innerWidth`, and every button at least 44px tall.
- [ ] No survey was submitted and nothing was typed into the survey.

**Verify:** The evidence file's results table has 16 rows: 14 PASS and 2 GAP. `git -C <repo> diff --stat` shows only that new file.

**Steps:**

- [ ] **Step 1: Run A (#1 human win + keep Leverage, #12 refresh after the lock result, #16 survey handoff). Desktop.**
  1. K1. Then, in one K2 script: `#startInvestigation` → `[data-route="gideon-materials"]` → `#backToCase` → `[data-route="seance-room"]` → `#backToCase` → `#openLock`.
  2. Tell the founder "lock runs starting" (F2). Run K0, then K4 with `mode='win'`. Expect `human-win`.
  3. K3. Expect `minigame_result(the-locked-box)=human-win` and `discovery(e-cylinder-43)=private`.
  4. **#12:** K5 (refresh on the result screen). Expect the page still to show "You get the box open first.", and K3 to show no duplicates and still exactly one `minigame_result`.
  5. K2 script: `#returnFromLock` → `#peopleChoice` → `[data-suspect="edwin-rusk"]` → `#backToCase`. K3: expect `first_look_closed(e-cylinder-43)=public` exactly once.
  6. K2 script: `[data-route="writing-room"]` → `#backToCase` → `#peopleChoice` → `[data-suspect="clara-hensley"]` → `#backToCase`. **Do not click `#followThread`.**
  7. **#1:** K3 must show `leverage: 1` and no `leverage_choice` event.
  8. K2 script: `#enterLastCall` → choose culprit `clara-hensley` → tick `e-cylinder-43`, `e-cylinder-transcript`, `e-service-route`, `e-clara-access` → `#commitTheory`. K3: `case_file_commitment` appears once.
  9. **#16:** click `#openSurvey`. The tab navigates to `form.jotform.com`. **Type nothing.** Read the URL with `javascript_tool`: `location.href`. If that's blocked on Jotform's origin, use `read_network_requests` with `urlPattern: "jotform"`. Parse the query string.
     - Present and non-empty: `q13_textbox11=3.0`, `q14_textbox12` (the run_id), `q15`–`q25`, `q26_textbox24=completed`, `q28_time_to_first_investigation_seconds`, `q29_major_investigations`, `q30_event_sequence`.
     - Absent: `q31_abandonment_point`.
  10. Record this `run_id` as **excluded**. Navigate the tab back to the live URL.

- [ ] **Step 2: Run B (#2 human win, then use Leverage; #13 refresh during a partial Case File). Desktop.**
  1. K1. K2 script: `#startInvestigation` → `[data-route="gideon-materials"]` → `#backToCase` → `[data-route="seance-room"]` → `#backToCase` → `#openLock`.
  2. K0, then K4 `win`. Then a K2 script: `#returnFromLock` → `#peopleChoice` → `[data-suspect="clara-hensley"]` → `#followThread`.
  3. **#2:** K3 must show `leverage_choice(follow-the-thread)=follow-the-thread` once, an `inference_action(clara-hensley)`, and `leverage: 0`.
  4. K2 script: `#backToCase` → `[data-route="writing-room"]` → `#backToCase` → `#peopleChoice` → `[data-suspect="beatrice-ashcombe"]` → `#backToCase` → `#enterLastCall` → choose culprit `clara-hensley` → tick `e-cylinder-43` and `e-cylinder-transcript` only.
  5. **#13:** K5 (refresh). Check with `javascript_tool` that `#culpritSelect` has the value `clara-hensley` and exactly those two boxes are ticked. K3 shows no duplicates and exactly one `last_call`.
  6. Tick `e-service-route` and `e-clara-evasion` → `#commitTheory`. K3: one `case_file_commitment`. Stop at the survey screen and **do not** click `#openSurvey`.

- [ ] **Step 3: Run C (#11 refresh during the lock, #3 rival win then Listen In, #6 timeout gap). Desktop.**
  1. K1. K2 script: `#startInvestigation` → `[data-route="gideon-materials"]` → `#backToCase` → `[data-route="seance-room"]` → `#backToCase` → `#openLock`. Note the time.
  2. **#11:** after about 5 seconds, K5 (refresh). K3 must show `lock: 'active'` with exactly one `minigame_started`. The lock screen shows the pin stage again.
  3. Set no pins. Wait until about 20 seconds after `#openLock` (use `javascript_tool` with `await wait(...)` in calls under 45s). K3: `minigame_result(the-locked-box)=rival-win`.
  4. **#6 gap evidence:** no pins set, and the outcome is `rival-win` rather than `timeout`. Record as GAP.
  5. **#3:** K2 script: `#listenIn`. K3: `leverage_choice(listen-in)=listen-in` once, `discovery(e-cylinder-43)=private`, `leverage: 0`.

- [ ] **Step 4: Run D, the 360px full playthrough (#15, #8 red herring first, #4 rival win then save Leverage, #9 Case File without winning the lock, #10 Rusk route without Beatrice testimony, #14 gap).**
  1. `mcp__Claude_Browser__resize_window` to `width: 360, height: 780`. Reload the page.
  2. K1. Play this run with **real clicks** (`find` to get a ref, then `computer` `left_click`) so layout problems would show. For the culprit `<select>`, use `form_input` rather than a click. Take a screenshot at: the opening, the first choice grid, the lock stage, and Last Call.
     - **Leverage rule for this run:** the only "Spend 1 Leverage" button you click is on the Beatrice *revisit* in sub-step 7. Beatrice's first visit, Rusk's scene, and Clara's scene all offer one. Leave those alone, or the Leverage needed for sub-step 7 is gone.
     - **Also don't click "Challenge that claim" on the Beatrice revisit.** It would add her testimony, which #10 must avoid.
  3. **#8:** the first move is Question Someone → **Beatrice Ashcombe**, then Back to the case.
  4. Move 2: Gideon's Things → Back. The lock callout appears → Crack the box. Set no pins, and wait for rival-win (about 19s).
  5. **#4:** click "Save it and keep investigating". K3: `leverage_choice(listen-in)` with `choice` save once, and `leverage: 1`.
  6. Move 3: The Séance Room → Back. Move 4: Question Someone → Edwin Rusk → "Challenge that claim" → Back. Move 5: Question Someone → Clara Hensley → Back.
  7. Question Someone → "Revisit Beatrice Ashcombe" → "Spend 1 Leverage: …" (Follow the Thread) → Back.
  8. K3 must show discoveries `e-cylinder-transcript`, `e-service-route`, `e-rusk-sighting`, `e-clara-transcribed-43`, and `e-private-detail-match`.
  9. Lock my theory → culprit **Clara Hensley** → tick exactly `e-cylinder-transcript`, `e-rusk-sighting`, `e-private-detail-match`, `e-clara-transcribed-43`, `e-service-route` → Commit theory.
  10. **#9 and #10:** K3 shows `case_file_commitment(clara-hensley)=solved`, no committed piece id starts with `e-beatrice-`, and the lock outcome was `rival-win`.
  11. **#15:** run `({ sw: document.documentElement.scrollWidth, iw: innerWidth, small: [...document.querySelectorAll('button')].filter(b => b.offsetParent && b.getBoundingClientRect().height < 44).map(b => b.textContent.trim()) })` on the opening, choice, lock, and Last Call screens. Expect `sw <= iw` and `small: []` each time. Record the numbers.
  12. **#14 gap evidence:** K3 `abandonment_events: 0`. Record as GAP.
  13. Stop at the survey screen. `resize_window` preset `desktop`.

- [ ] **Step 5: Run E (#5 lock break). Desktop.** K1 → K2 script to `#openLock`, the same as Run A step 1. K0, then K4 `mode='break'`. Expect `outcome: 'break'` and the heading "The lock wins the argument." Then K2: `#returnFromLock` → `#peopleChoice` → `[data-suspect="edwin-rusk"]` → `#backToCase`. K3 shows `discovery(e-cylinder-43)=public` and `first_look_closed=public`, no duplicates.

- [ ] **Step 6: Run F (#7 lock abort). Desktop.** K1 → K2 script to `#openLock` → `#abortLock`. K3: `minigame_result=abort`. Then `#returnFromLock` → `[data-route="writing-room"]` → `#backToCase`. K3 shows `e-cylinder-43` public and no duplicates.

- [ ] **Step 7: Write the evidence file** with this structure:

```markdown
# Nightcap — Paper Test #2 v3.0 Pre-Send QA

**Status:** TEST EVIDENCE — harness QA, not player evidence; not canon
**Fixture:** nightcap-paper-test-02-v3.0 (fixture version 3.0) · **Live URL tested:** https://nickejanssen.github.io/arcwright/nightcap/paper-test-02/v3.0/
**Date:** <YYYY-MM-DD> · **Method:** Claude Code built-in browser; automated clicks through the fixture's own UI; lock pins pressed by an in-page helper timing the real "Set pin" button

## Results

| # | Situation | Result | Run | run_id | Viewport | Evidence |
|---|---|---|---|---|---|---|
| 1 | Human wins the lock, then saves Leverage | PASS | A | ... | desktop | human-win; leverage 1 at commitment; no leverage_choice |
<one row per situation 1–16, using the spec's wording; #6 and #14 use Result "GAP">

## Documented gaps (not blockers)
- #6 Timeout unreachable: <evidence>. Source: `app.js` `renderLock` checks `rival_finish_seconds` (19) before `duration_seconds` (45).
- #14 Abandonment never recorded: <evidence>. Source: `markAbandoned` in `runtime.js` is never imported by `app.js`.

## Event streams
<per run: run_id and the K3 `events` list at the final checkpoint>

## 360px layout
<per screen: scrollWidth/innerWidth, buttons under 44px, screenshot taken (yes/no)>

## Excluded run_ids
- <Run A run_id> — QA #16 opened the survey (no submission); exclude any Jotform entry carrying it.
- <Runs B–F run_ids> — QA runs; never reached Jotform.

## Survey instrument (read-only inspection)
<filled by Task 2>

## Smoke run
<filled by Task 5>
```

- [ ] **Step 8: Commit.**
```bash
git -C C:/Users/nicke/OneDrive/Desktop/arcwright/.claude/worktrees/arcwright-nightcap-phase-plan-a023ca add docs/gdd/nightcap/03-playtest-evidence/99-paper-test-02-v3.0-pre-send-qa.md
git -C C:/Users/nicke/OneDrive/Desktop/arcwright/.claude/worktrees/arcwright-nightcap-phase-plan-a023ca commit -m "docs(nightcap): v3.0 pre-send QA evidence"
```
(If the session's repo root differs, substitute it. The point is to use `git -C`, not `cd`.)

**If any situation fails** (other than #6 and #14): stop. Report the situation, the run_id, the K3 output, and a screenshot. Do not edit fixture files. The founder decides between a v3.0.1 and a v3.1.

---

### Task 2: Read the survey instrument (read-only)

**Goal:** The QA evidence file's "Survey instrument" section records the form's redirect target, partial-submission setting, and every visible question's wording and scale, plus any partial entry left by QA #16.

**Files:**
- Modify: `docs/gdd/nightcap/03-playtest-evidence/99-paper-test-02-v3.0-pre-send-qa.md` ("Survey instrument (read-only inspection)" section)

**Acceptance Criteria:**
- [ ] Form `262397917027062`'s title, enabled state, and question count are recorded.
- [ ] Every visible (non-hidden) question is listed with its number, exact wording, type, and scale or options.
- [ ] The first free-text question is identified.
- [ ] The post-submit redirect target is recorded, or recorded as "not exposed by the connector".
- [ ] The partial-submission setting is recorded, or recorded as "not exposed".
- [ ] The result of searching submissions for Run A's `run_id` is recorded, and any hit is listed as excluded.
- [ ] Only Jotform read tools were called.

**Verify:** The section exists with all the items above. The session transcript shows no Jotform write-tool call.

**Steps:**

- [ ] **Step 1: Wait for founder step F3.** Ask the founder to connect Jotform, and wait for `Jotform connected`. Then load the connector's tools (use `ToolSearch` with the query `jotform` if they are deferred).
- [ ] **Step 2: Fetch the form.** Fetch form `262397917027062` and its properties or settings with read tools. Record the title, enabled state, question count, and each visible question (number, wording, type, scale or options). The 18 hidden telemetry fields are already known from `JOTFORM_FIELD_MAP`; list them by name only.
- [ ] **Step 3: Record the redirect and partial settings.** Record the thank-you/redirect URL.
  - **Acceptable:** `https://nickejanssen.github.io/arcwright/?reveal=1`, or the v3.0 route with `?reveal=1`. The live root forwards `?reveal=1` to the current test, verified 2026-09-27.
  - **Anything else:** stop and report to the founder. Changing it is a survey edit and needs a founder decision.
  - **Not exposed by the connector:** record "not exposed; Task 5 smoke run is the proof".
  - Record whether partial or unfinished submissions are saved.
- [ ] **Step 4: Search for QA #16's run_id.** Search or read the form's submissions for Run A's `run_id` (field `q14_textbox12`). Record found or not found. If found, add it to "Excluded run_ids".
- [ ] **Step 5: Commit.** `git -C <repo> commit -am "docs(nightcap): record v3.0 survey instrument (read-only)"`

---

### Task 3: v2.2 baseline results

**Goal:** A v2.2 results file records, per survey question, the actual v2.2 answers from Jotform, anonymized, as the baseline v3.0 is compared against.

**Files:**
- Create: `docs/gdd/nightcap/03-playtest-evidence/98-paper-test-02-v2.2-results.md`

**Acceptance Criteria:**
- [ ] The dataset boundary is stated: form id, instrument version 2.2, the window 2026-08-28 00:00 to 2026-08-30 23:59, the count of submissions in the window, and "raw data fetched <date> via Jotform connector (read-only)".
- [ ] Submissions outside the window are listed by id only, and not used.
- [ ] Each visible question has its exact wording, scale, and per-response values.
- [ ] Telemetry health lists which of the 18 hidden fields were populated per submission.
- [ ] Free text appears only as paraphrased themes. No names, emails, IPs, or verbatim quotes.
- [ ] The count is compared with the two existing documents (2 in `docs/specs/nightcap-external-playtest-harness.md`, 3 in `98-validation-state-and-remaining-plan.md`), and any disagreement is stated. Neither document is edited.

**Verify:** The file exists with the sections above. `git -C <repo> diff --stat HEAD~1` shows only this file.

**Steps:**

- [ ] **Step 1: Read the submissions.** Read form `262397917027062`'s submissions (read tool). Select them by `created_at` inside the window. Do not rely on `prototype_version`, which v2.2 left empty.
- [ ] **Step 2: Write the file** with the front matter and these sections:
  - Title: `# Nightcap — Paper Test #2 v2.2 Results (Baseline)`
  - Status line: `TEST EVIDENCE — baseline for v3.0 comparison; not canon`
  - Dataset boundary
  - Results by question (a table: question number, wording, scale, response 1, response 2, response 3, …)
  - Telemetry health
  - Free-text themes (paraphrased)
  - Discrepancies with existing records
  - Evidence limits: N is 2–3, exploratory only, per `98-validation-state-and-remaining-plan.md`
- [ ] **Step 3: Commit.** `git -C <repo> add <file>` and `git -C <repo> commit -m "docs(nightcap): v2.2 results baseline"`

---

### Task 4: Analysis plan and pass bar (founder gate)

**Goal:** A one-page analysis plan fixes, before any invite, how v3.0's results will be judged, and the founder has approved it.

> **USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Files:**
- Create: `docs/gdd/nightcap/02-validation/99-paper-test-02-v3.0-analysis-plan.md`

**Acceptance Criteria:**
- [ ] The file covers: dataset boundary, inclusion, exclusion (including Run A's run_id, the smoke run, founder, team, repeat, and partial entries), stopping rule, completion rate, per-hypothesis measures and thresholds (H1–H5) with v2.2 baselines, and the Gate 1 mapping, including "inconclusive".
- [ ] Every threshold names a specific survey question number (from Task 2) or a specific telemetry field or event.
- [ ] The founder replied `approved` (or gave changes, which were applied and then approved).
- [ ] The status line reads `APPROVED — <YYYY-MM-DD>, founder`.

**Verify:** Grep for `APPROVED — ` in `docs/gdd/nightcap/02-validation/99-paper-test-02-v3.0-analysis-plan.md` finds exactly one line, and git history shows a commit after the founder's reply.

**Steps:**

- [ ] **Step 1: Draft the plan** with status `DRAFT — awaiting founder approval` and these sections:
  - **Dataset boundary**
  - **Inclusion and exclusion**
  - **Stopping rule:** 8 included sessions; or 3 weeks after the first invite if at least 6; under 6 at 3 weeks means the founder decides.
  - **Completion rate:** included submissions ÷ testers reported as started, from the founder's private tracker.
  - **Hypotheses and thresholds**
  - **Gate 1 mapping:**
    - all five met → pass;
    - H5 met but any of H1–H4 missed → narrow v3.x;
    - H5 missed → larger design correction;
    - under 6 included → inconclusive.
  - **Reported but not gating:** the solve rate (`case_commitment.correct`).

  Starting proposals for thresholds. Map each to the real question numbers from Task 2. If a hypothesis has no matching survey question, measure it by telemetry alone and say so.

  | Hypothesis | Measure | v2.2 baseline | Proposed bar |
  |---|---|---|---|
  | H5 Pull | Fun rating; Detective-feeling rating; replay answer; completion rate | Fun 3,3,3; Detective 2,2,3; replay 1 Yes / 2 Maybe | median Fun ≥ 4; median Detective ≥ 4; ≥ 50% replay "Yes"; completion ≥ 75% |
  | H1 Agency | agency/autonomy question if present; first `investigation_choice` target spread | from Task 3 | ≥ 75% at the top two agreement options; no single first move chosen by more than 75% of players |
  | H2 Clarity | action-clarity question | v2.1: "Mostly confusing" | ≥ 75% in the two clearest options; at most 1 player at "Mostly confusing" or worse |
  | H3 Inference | `inference_action` events per player; `time_to_first_inference_seconds` | n/a (v2.2 telemetry missing) | ≥ 75% of players make ≥ 1 `inference_action` |
  | H4 Competition | rival/competition question if present; a `leverage_choice` event (spend or save); post-lock return (`post_lock_return_seconds` from `event_sequence`) | from Task 3 | ≥ 75% of players make a Leverage choice; median post-lock return ≤ 60s |
- [ ] **Step 2: Commit the draft** and push, so the link works: `git -C <repo> push`.
- [ ] **Step 3: Gate (founder step F4).** Send the founder the GitHub link to the file on this branch, with a 3-line summary of the bars. Wait. Apply any changes they ask for. When they reply `approved`, set the status line to `APPROVED — <date>, founder`, commit, and push.

---

### Task 5: Smoke run verification (founder gate)

**Goal:** The founder's real-phone smoke submission is confirmed in Jotform, with its hidden fields passing the spec's telemetry field rule and the reveal landing observed, and it is recorded as excluded.

> **USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Files:**
- Modify: `docs/gdd/nightcap/03-playtest-evidence/99-paper-test-02-v3.0-pre-send-qa.md` ("Smoke run" section)

**Acceptance Criteria:**
- [ ] The founder reported `smoke run done` with a screenshot showing *A Knock at Midnight*'s truth page.
- [ ] The submission is found (by time plus the text `SMOKE TEST - exclude`), and its `run_id` is recorded.
- [ ] These 15 fields are non-empty:
  - `prototype_version` equal to `3.0`
  - `run_id`, `started_at`, `completed_at`, `duration_seconds`, `action_sequence`, `investigation_branches`, `discoveries`, `case_commitment`, `device_class`, `browser_class`
  - `completion_status` equal to `completed`
  - `time_to_first_investigation_seconds`, `major_investigations`, `event_sequence`
- [ ] `abandonment_point` is empty. `pulse_result` and `final_next_interest` match the rule in the spec's Section 1.
- [ ] `event_sequence` parses as JSON and contains `survey_handoff`.
- [ ] The smoke `run_id` is added to "Excluded run_ids".

**Verify:** The "Smoke run" section lists all 18 field names with PASS against the rule, the landing-page result, and the excluded run_id.

**Steps:**

- [ ] **Step 1: Gate (founder step F5).** Send the founder the F5 instructions verbatim. Wait for `smoke run done` and the screenshot.
- [ ] **Step 2: Read the submission.** Read the matching submission (read tool) and check each field. In the repository, record only field names with PASS or FAIL, plus the values of `run_id`, `prototype_version`, and `completion_status`.
- [ ] **Step 3: If any check fails, or the landing page is wrong,** stop and report to the founder. Do not change the survey.
- [ ] **Step 4: Commit.** `git -C <repo> commit -am "docs(nightcap): v3.0 smoke run verified"`

---

### Task 6: Tester brief, status update, PR, and go-ahead (founder gate)

**Goal:** The invite kit exists, the validation plan shows pre-distribution checks complete (Gate 1 still NOT PASSED), a PR is open and merged by the founder, and the founder has replied `go`.

> **USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Files:**
- Create: `docs/gdd/nightcap/02-validation/99a-paper-test-02-v3.0-tester-brief.md`
- Modify: `docs/gdd/nightcap/02-validation/98-validation-state-and-remaining-plan.md` (lines 130–138)

**Acceptance Criteria:**
- [ ] The tester brief contains: who qualifies, an invite message with the fixed v3.0 URL, player instructions, and the founder's test-window rules (private tracker; don't promote another test).
- [ ] The validation plan marks pre-distribution steps 2, 4, and 5 verified (citing the QA file) and step 6 provided for (citing the analysis plan), and still reads `**STATUS: NOT PASSED.**`.
- [ ] The PR is open against `main` containing exactly the 5 files in the file map plus this branch's spec, plan, and plan `.tasks.json` (8 paths). Its CI checks pass.
- [ ] The founder merged the PR and replied `go`.

**Verify:** `gh pr view <n> --json state,mergedAt` → `MERGED`; `git -C <repo> diff --name-only origin/main...HEAD` before merge lists only the expected files.

**Steps:**

- [ ] **Step 1: Write the tester brief** with the front matter and these sections:
  - Title: `# Nightcap — Paper Test #2 v3.0 Tester Brief`
  - Status line: `PROCESS — invite kit for Phase 2; not canon`
  - **Who qualifies:** plays party games, mystery games, or murder-mystery nights; not a close friend or family member of the founder (friends-of-friends are fine); has never played v2.1 or v2.2 and hasn't seen the design.
  - **Invite message** (ready to paste):
    > Hi! I'm testing a short murder-mystery game I'm building and I'd love your honest take. It's about 20 minutes, solo, on your phone or computer: https://nickejanssen.github.io/arcwright/nightcap/paper-test-02/v3.0/ — play it in one sitting, don't look anything up or talk about it with anyone until you're done, and fill in the short survey at the end *before* the solution is shown. Blunt feedback is the most useful kind. Thank you!
  - **Player instructions:** the same rules as a bullet list.
  - **Founder rules during the test window:**
    - keep a private tracker (name, invited date, started yes/no, submitted yes/no) outside the repository;
    - don't promote or publish any other Nightcap test until the window closes, because the reveal after the survey follows the current test;
    - stop per the approved analysis plan's stopping rule.
- [ ] **Step 2: Update the validation plan.** In `98-validation-state-and-remaining-plan.md`, under "Before external distribution is treated as fully ready:", append to items 2, 4, and 5: ` — verified <date>; see 03-playtest-evidence/99-paper-test-02-v3.0-pre-send-qa.md`. Append to item 6: ` — exclusion rule in 02-validation/99-paper-test-02-v3.0-analysis-plan.md`. Leave `**STATUS: NOT PASSED.**` unchanged.
- [ ] **Step 3: Commit and push, then open the PR.**
```bash
git -C <repo> add docs/gdd/nightcap/02-validation/99a-paper-test-02-v3.0-tester-brief.md docs/gdd/nightcap/02-validation/98-validation-state-and-remaining-plan.md
git -C <repo> commit -m "docs(nightcap): v3.0 tester brief and pre-distribution status"
git -C <repo> push
gh pr create --base main --title "docs(nightcap): Phase 1: v3.0 send-readiness evidence, pass bar, tester brief" --body-file <scratch>/pr-body.md
```
  The PR body lists each spec "Done when" item with its evidence file, both documented gaps, the excluded run_ids, and a link to the approved analysis plan.
- [ ] **Step 4: Gates (founder steps F6, F7).** Ask the founder to review and merge. After the merge, report the summary and ask for `go`. Phase 1 ends when they reply `go`.

---

## Spec coverage

| Spec item | Task |
|---|---|
| Section 1 QA, all 16 situations, pass rule, telemetry field rule, #16 exclusion, stop rule, output file | 1 |
| Section 2 steps 1–2 (connect; redirect, questions, first free-text question, partial setting) | 2 |
| Section 2 steps 3–5 (founder smoke run, field check, exclusion) | 5 |
| Section 3 v2.2 baseline, date-only identification, discrepancies | 3 |
| Section 4 analysis plan, thresholds, Gate 1 mapping including inconclusive, approval | 4 |
| Section 5 tester brief, completion status update | 6 |
| Founder steps | Founder steps table (F1–F7), plus gates in Tasks 1, 2, 4, 5, 6 |
| Guardrails (read-only Jotform, no submissions, no `playtests/` changes, privacy) | Ground rules; per-task acceptance criteria |
| Documented gaps #6 and #14 | 1 |
