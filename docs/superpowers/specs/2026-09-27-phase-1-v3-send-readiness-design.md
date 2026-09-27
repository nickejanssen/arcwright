---
id: playtestops.superpowers.specs.2026-09-27-phase-1-v3-send-readiness-design
namespace: playtest-ops
title: Phase 1 v3.0 Send-Readiness Design
owner: Nico Janssen
status: active
review_by: "2027-03-27"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Phase 1 v3.0 Send-Readiness Design

> Status: Approved design, 2026-09-27 (the founder approved each of the five sections in session)
> Canonical path: docs/superpowers/specs/2026-09-27-phase-1-v3-send-readiness-design.md

## Purpose

Nightcap Paper Test #2 v3.0 (*A Knock at Midnight*) is about to go to 6–8 external players. Each tester can play only once: after they have seen the mystery, their feedback cannot be collected again. A broken path or lost survey data wastes that tester permanently. That happened in v2.2, where 15 of the 18 hidden telemetry fields arrived empty in Jotform.

Phase 1 has two goals:

1. confirm nothing is broken before any tester sees v3.0;
2. fix how the results will be judged before they arrive.

Phase 1 ends when the founder gives the go-ahead to send invites. Running the sessions is Phase 2.

## Founder decisions (2026-09-27)

- Jotform access is through the Jotform connector, **read-only**.
- Sample: **6–8 new players**. "New" means they never played v2.1 or v2.2 and have not seen the design.
- Representative tester: **people who play party games, mystery games or murder-mystery nights, who are not close friends or family** of the founder. Friends-of-friends qualify.
- Results are judged against **decision rules with thresholds that the founder approves before the first invite**.
- Out of Phase 1: #207's incorrect status and #303's missing milestone move to the Phase 2 reconciliation audit. The engine `duration_seconds` telemetry bug moves to the Arcwright engine phase.
- The founder plays the smoke run on a real phone.
- Executor: a fresh **Claude Code** session. It needs the built-in browser and the Jotform connector.

## Facts this design relies on (checked 2026-09-27)

- Live routes return HTTP 200: `/nightcap/paper-test-02/v3.0/` and `/nightcap/paper-test-02/v2.2/`. `playtests/catalog.json` marks v3.0 current.
- All 31 v3.0 fixture tests pass (`node --test playtests/nightcap-paper-test-02-v3.0/tests/*.test.mjs`).
- The live root page forwards `?reveal=1` to `/arcwright/nightcap-paper-test-02-v3.0/?reveal=1`, which serves *A Knock at Midnight*. The Jotform post-submit redirect target itself has not been verified.
- `scripts/build_playtest_site.py` publishes each fixture directory in full, README included, so the fixture README is part of the published artifact.
- The fixture has no server. Runs that are abandoned before the survey leave no record anywhere.
- The survey's question wording exists only in Jotform (form `262397917027062`, 31 questions; the 18 hidden telemetry fields are listed in `JOTFORM_FIELD_MAP` in `playtests/nightcap-paper-test-02-v3.0/runtime.js`).
- The Jotform connector is in the MCP registry and is not yet connected.

## Guardrails (all sections)

- **Jotform: read-only.** The allowed connector tools are listing forms, fetching form details and settings, searching, and reading submissions. `create_form`, `edit_form`, `create_submission`, `assign_form` and every other write tool are forbidden.
- **No survey, fixture or catalog changes.** Nothing under `playtests/` changes, including the fixture README (it is published). No Jotform question, field or redirect setting changes.
- **Tester data stays private.** No names, emails, IP addresses, device identifiers or verbatim free-text answers go in the repository. Free-text answers are recorded as paraphrased themes only. The founder's invite tracker stays outside the repository.
- **No submission by the agent.** The only survey submission in Phase 1 is the founder's labeled smoke run.
- Skills to follow: `docs/skills/arcwright-playtest-harness/SKILL.md` for Sections 1 and 2, and `docs/skills/arcwright-playtest-research/SKILL.md` for Sections 3 and 4.

## Section 1: Pre-send QA (agent)

The agent plays the **live** v3.0 in the built-in browser and works through the fixture README's pre-send checklist:

| # | Situation |
|---|---|
| 1 | Human wins the lock, then saves Leverage |
| 2 | Human wins the lock, then uses Leverage |
| 3 | Rival wins the lock, then spends Listen In |
| 4 | Rival wins the lock, then saves Leverage |
| 5 | Lock break |
| 6 | Lock timeout |
| 7 | Lock abort |
| 8 | Red-herring-first investigation |
| 9 | Reaches the Case File without winning the lock |
| 10 | Rusk chronology/reconstruction route without Beatrice's testimony |
| 11 | Refresh during the lock |
| 12 | Refresh after the lock result / first look |
| 13 | Refresh during a partial Case File selection |
| 14 | Voluntary abandonment, where observable |
| 15 | Layout at a 360px-wide emulated viewport |
| 16 | Survey handoff |

Every run uses a desktop viewport except #15, which runs a full playthrough at 360px.

**Pass rule per situation:** the fixture behaves as its README describes, and the captured v3 event stream (from the fixture's `sessionStorage` record) shows no duplicated choice, discovery, rival event, lock resolution, first-look delivery, Leverage spend, Last Call, Case File commitment, completion or survey handoff.

**Survey handoff check (#16):** open the survey link the fixture generates, **without submitting**, and confirm all of the following:
- the link carries the run's `run_id`;
- all 18 `JOTFORM_FIELD_MAP` fields are present and non-empty;
- `completion_status=completed`.

**Stop rule:** if any situation fails, stop and report it to the founder with evidence. Fixture files are not edited. A fix means a founder decision on a v3.0.1 or a v3.1.

**Not claimed:** real-phone behavior, and whether Jotform stores the submitted values. Section 2 covers both.

**Output:** `docs/gdd/nightcap/03-playtest-evidence/99-paper-test-02-v3.0-pre-send-qa.md`. Per situation it records: pass or fail, the viewport, the `run_id`, the event types observed in order, and any defect. It also records the date and the live URL tested.

## Section 2: Smoke run (founder plus agent)

1. **Founder:** connect the Jotform connector in claude.ai connector settings.
2. **Agent:** read form `262397917027062` (read-only) and record:
   - the post-submit redirect target, which must be the site root with `?reveal=1` or the v3.0 route with `?reveal=1`;
   - the wording and scale of every visible question;
   - the first free-text question.

   If the redirect points anywhere else, stop and report. Changing it is a survey edit and needs a founder decision.
3. **Founder:** play v3.0 once, end to end, on a real phone, from the fixed route `https://nickejanssen.github.io/arcwright/nightcap/paper-test-02/v3.0/`. In the first free-text question, type `SMOKE TEST - exclude`. Submit, then report or screenshot the page reached. It must show *A Knock at Midnight*'s truth.
4. **Agent:** read that submission and confirm:
   - all 18 hidden fields are non-empty;
   - `prototype_version` is the v3.0 value;
   - `event_sequence` parses and contains `survey_handoff`;
   - `completion_status=completed`.
5. **Agent:** record the smoke run's `run_id` as excluded from research evidence.

**Output:** a "Smoke run" section in the Section 1 evidence file, covering the redirect target, the founder's observed landing page, the field-by-field populated check (field names only, no values beyond `run_id`, `prototype_version` and `completion_status`), and the excluded `run_id`.

## Section 3: v2.2 baseline (agent)

Read v2.2's submissions from Jotform. Identify them by submission date (2026-08-28 to 2026-08-30) together with any v2.2 `prototype_version`, and exclude anything labeled as a smoke or test run.

Write `docs/gdd/nightcap/03-playtest-evidence/98-paper-test-02-v2.2-results.md`, following the research skill's feedback structure:
- **Dataset boundary:** fixture id, instrument id and version, submission count, date range, and the fact that raw data was fetched this session.
- **Per question:** exact wording, scale, and each response as a count or list of values.
- **Telemetry health:** which hidden fields were populated.
- **Free-text themes:** paraphrased only.

**Discrepancies:** `docs/specs/nightcap-external-playtest-harness.md` reports 2 submissions as of 2026-08-30, while `docs/gdd/nightcap/02-validation/98-validation-state-and-remaining-plan.md` reports 3. Record what the raw data shows and state any disagreement explicitly. Do not silently edit either existing document.

## Section 4: Analysis plan and pass bar (agent drafts, founder approves)

Write `docs/gdd/nightcap/02-validation/99-paper-test-02-v3.0-analysis-plan.md`, drafted from the actual question wording read in Section 2:

- **Dataset boundary:**
  - fixture `nightcap-paper-test-02-v3.0`, instrument `262397917027062` v2.2, route `/nightcap/paper-test-02/v3.0/`;
  - the window opens on the date of the first invite and closes by the stopping rule.
- **Inclusion:** one completed submission per new, representative tester (per the founder decisions above). The first completed submission counts.
- **Exclusion:** the smoke run, founder runs, team runs, repeat runs, and submissions with a `prototype_version` other than v3.0. Excluded runs are identified by `run_id`.
- **Stopping rule (proposed):** stop at 8 included sessions, or 3 weeks after the first invite if at least 6 are included. If fewer than 6 are included after 3 weeks, the founder decides whether to extend.
- **Completion rate:** included submissions divided by testers who reported starting, taken from the founder's private invite tracker (count only).
- **Per hypothesis (H1–H5 from the fixture README):**
  - the survey question(s) and telemetry fields or events that measure it;
  - the v2.2 baseline value from Section 3, where a comparable question exists;
  - a proposed threshold stated as a concrete count or median.
- **Mapping to the Gate 1 call** (`98-validation-state-and-remaining-plan.md` step 5):
  - all five hypotheses meet their thresholds → **pass**;
  - H5 (fun, detective feeling, completion, replay) meets its threshold but one or more of H1–H4 does not → **narrow v3.x successor** targeting the missed hypotheses;
  - H5 does not meet its threshold → **larger design correction**.
- **Approval:** the document's status line reads `DRAFT — awaiting founder approval` until the founder approves or adjusts the thresholds and stopping rule. It then reads `APPROVED — <date>, founder`. No invite goes out before approval.

## Section 5: Tester brief and completion

Write `docs/gdd/nightcap/02-validation/99a-paper-test-02-v3.0-tester-brief.md`, containing:
- **Who qualifies:** the representative-tester definition and "new player" rule above.
- **Invite message template:** a short message linking the fixed route `https://nickejanssen.github.io/arcwright/nightcap/paper-test-02/v3.0/`.
- **Player instructions:** play alone in one sitting (about 20 minutes, phone or computer); do not look anything up or discuss the mystery until finished; complete the survey before the truth is shown.
- **Founder rules during the test window:**
  - keep a private invite tracker (invited, started, submitted) outside the repository;
  - do not promote or publish any other Nightcap test while the window is open, because the post-survey reveal follows the current test.

**Completion.** After Sections 1–4 pass and the founder approves the analysis plan, update `docs/gdd/nightcap/02-validation/98-validation-state-and-remaining-plan.md` under "Before external distribution":
- mark steps 2, 4 and 5 as verified, citing the Section 1 evidence file;
- mark step 6 as provided for by the analysis plan's exclusion rule.

Gate 1 remains **NOT PASSED**.

## Order and gates

1. Section 1 (QA). It has no dependencies and can start immediately.
2. Founder connects Jotform. Then the Section 2 form read, Section 3, and the Section 4 draft.
3. **Founder gate:** approve or adjust the thresholds and stopping rule.
4. Section 2 smoke run (founder), then the agent's verification.
5. Section 5 brief and the validation-plan status update.
6. **Founder gate:** go-ahead to send invites. Phase 2 begins.

## Done when

- The QA evidence file records all 16 situations as pass, with the smoke run section complete.
- The v2.2 results file exists.
- The analysis plan is marked APPROVED by the founder.
- The tester brief exists.
- The validation plan's pre-distribution steps are updated.
- The founder has given the go-ahead to send.

## Not in Phase 1

- Recruiting or sending invites, and running or analyzing external sessions (Phase 2).
- Any change to fixture files, the survey, the catalog, or Pages.
- #207 and #303 (Phase 2 reconciliation audit); the engine `duration_seconds` bug (Arcwright engine phase).
