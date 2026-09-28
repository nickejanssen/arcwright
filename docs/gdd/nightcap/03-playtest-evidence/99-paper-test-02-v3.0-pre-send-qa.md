---
id: nightcap.gdd.nightcap.03-playtest-evidence.99-paper-test-02-v3.0-pre-send-qa
namespace: nightcap
title: Nightcap — Paper Test #2 v3.0 Pre-Send QA
owner: Nico Janssen
status: active
review_by: "2027-03-27"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Nightcap — Paper Test #2 v3.0 Pre-Send QA

**Status:** TEST EVIDENCE — harness QA, not player evidence; not canon
**Fixture:** nightcap-paper-test-02-v3.0 (fixture version 3.0) · **Live URL tested:** https://nickejanssen.github.io/arcwright/nightcap/paper-test-02/v3.0/
**Date:** 2026-09-28 · **Method:** Claude Code built-in browser; automated clicks through the fixture's own UI (Runs A, B, C, E, F) and real pointer clicks through the rendered page (Run D, 360px); lock pins pressed by an in-page helper timing the real "Set pin" button

## Results

| # | Situation | Result | Run | run_id | Viewport | Evidence |
|---|---|---|---|---|---|---|
| 1 | Human wins the lock, then saves Leverage | PASS | A | 811b3eff-afcc-4b72-b67b-1298ca93a980 | desktop | `human-win`; `leverage: 1` at commitment; no `leverage_choice` event |
| 2 | Human wins the lock, then uses Leverage | PASS | B | 7e933637-6e94-49e4-b4e0-963cea0f08a9 | desktop | `leverage_choice(follow-the-thread)` once; `inference_action(clara-hensley)`; `leverage: 0` |
| 3 | Rival wins the lock, then spends Listen In | PASS | C | 20ba3d58-d548-4f1a-b582-5e823954a992 | desktop | `leverage_choice(listen-in)` once; `discovery(e-cylinder-43)=private`; `leverage: 0` |
| 4 | Rival wins the lock, then saves Leverage | PASS | D | 2a7c5311-dd03-4ede-ba66-bbe33f467b6e | 360px | `leverage_choice(listen-in)` choice `save` once; `leverage: 1` |
| 5 | Lock break | PASS | E | 1e3efa8b-d5a8-4734-875a-c52498a2ef53 | desktop | outcome `break`; heading "The lock wins the argument."; `discovery(e-cylinder-43)=public`; no duplicates |
| 6 | Lock timeout (documented gap) | GAP | C | 20ba3d58-d548-4f1a-b582-5e823954a992 | desktop | No pins set; resolved `rival-win` at ~19-20s rather than reaching the 45s timeout |
| 7 | Lock abort | PASS | F | 41d17908-8079-4e94-a163-c64f3df08d1d | desktop | `minigame_result=abort`; `e-cylinder-43` public; no duplicates |
| 8 | Red-herring-first investigation | PASS | D | 2a7c5311-dd03-4ede-ba66-bbe33f467b6e | 360px | First move `investigation_choice(beatrice-ashcombe)`; leverage untouched at 1 |
| 9 | Reaches the Case File without winning the lock | PASS | D | 2a7c5311-dd03-4ede-ba66-bbe33f467b6e | 360px | `case_file_commitment(clara-hensley)=solved` with `lock.outcome=rival-win` |
| 10 | Rusk route without Beatrice's testimony | PASS | D | 2a7c5311-dd03-4ede-ba66-bbe33f467b6e | 360px | No committed evidence piece id starts with `e-beatrice-` |
| 11 | Refresh during the lock | PASS | C | 20ba3d58-d548-4f1a-b582-5e823954a992 | desktop | After refresh: `lock: 'active'`, exactly one `minigame_started`, pin stage shown again |
| 12 | Refresh after the lock result / first look | PASS | A | 811b3eff-afcc-4b72-b67b-1298ca93a980 | desktop | Heading unchanged after refresh; no duplicates; same `run_id` and `lock.outcome` |
| 13 | Refresh during a partial Case File selection | PASS | B | 7e933637-6e94-49e4-b4e0-963cea0f08a9 | desktop | `#culpritSelect` and exactly the two ticked boxes survived refresh; exactly one `last_call` |
| 14 | Abandonment (documented gap) | GAP | D | 2a7c5311-dd03-4ede-ba66-bbe33f467b6e | 360px | `abandonment_events: 0` on a completed playthrough |
| 15 | Layout at a 360px-wide emulated viewport | PASS | D | 2a7c5311-dd03-4ede-ba66-bbe33f467b6e | 360px | `scrollWidth <= innerWidth` and no button under 44px tall, checked at opening, choice grid, lock stage, and Last Call |
| 16 | Survey handoff | PASS | A | 811b3eff-afcc-4b72-b67b-1298ca93a980 | desktop | Survey link carried `run_id`; all 15 required fields present, `q31_abandonment_point` absent, `completion_status=completed`; nothing typed or submitted |

## Documented gaps (not blockers)

- **#6 Timeout unreachable:** with no pins set, the lock resolved `rival-win` at ~19-20 seconds after opening rather than reaching a timeout. Observed on Run C (`run_id` `20ba3d58-d548-4f1a-b582-5e823954a992`) and again on Run D at 360px. Source: `app.js` `renderLock` checks `rival_finish_seconds` (19) before `duration_seconds` (45), so the rival always resolves the lock first.
- **#14 Abandonment never recorded:** Run D was played to a full completed commitment and showed `abandonment_events: 0`. Source: `markAbandoned` exists in `runtime.js` but is never imported or called by `app.js`.

## Notes for later tasks

- **K3 checker script blind spot (not a fixture defect):** the plan's K3 duplicate-checker keys "discovery" events by target only, without the event's `outcome` field. The fixture's "first look" mechanic legitimately records the same evidence id twice — `outcome: "private"` when found during the lock, then `outcome: "public"` when later revealed (confirmed in `runtime.js:130`, `recordDiscovery(... , outcome: visibility)`). K3 (as literally specified in the plan) reports this as a "duplicate" even though it is two different, intentional events. This was observed on every run that used the human-win first-look path (Runs A and B). Treated as a checker limitation, not a QA failure, per founder discussion during this session.
- **Plan Step 5 wording vs. fixture behavior:** the plan's Run E steps say to expect a `first_look_closed` event after a lock break. The fixture's own README states "break, timeout, or abort releases the cylinder publicly" immediately, with no private first-look phase to later close — confirmed in `runtime.js` (`resolveLock`'s `break`/`timeout`/`abort` branch calls `recordDiscovery(..., visibility: "public")` directly and never calls `releaseCylinderPublicly`, which is the only function that emits `first_look_closed`). No `first_look_closed` event is correct behavior for a break, not a defect.
- **`device_class=mobile` on Run A:** Run A's survey link reported `device_class=mobile` even though the run used the default desktop viewport (no viewport emulation was set at that point). This isn't part of the Task 1 pass/fail checklist, but it may be worth a look during Task 2/3's telemetry review, since it could indicate the fixture's device-class detection doesn't behave as expected in the built-in browser's default viewport.
- **Run B was replayed twice before a clean capture:** two earlier Run B attempts (browser-only state, never reaching the survey step) were discarded in favor of a single clean run so that the `run_id`, event log, and both refresh/leverage checks (#2, #13) come from the same run. Neither discarded attempt reached Jotform, so neither created a survey entry requiring exclusion.
- **Run D's event record is checkpoint-based, not one contiguous dump:** because Run D was played with real UI clicks across many steps (per the plan's requirement to catch layout problems), its evidence here is drawn from the specific K3 checks captured at each required checkpoint (first move, lock result, discoveries before Last Call, commitment, abandonment count, layout metrics) rather than a single final `eventSequence` printout. Each checkpoint's captured values are exact, not reconstructed.

## Event streams

**Run A** — `run_id` `811b3eff-afcc-4b72-b67b-1298ca93a980` (full sequence, captured via the generated survey link's `q30_event_sequence`):
`opening_complete`, `investigation_choice(gideon-materials)`, `discovery(e-cylinder-index)=public`, `discovery(e-cylinder-transcript)=public`, `discovery(e-clara-access)=public`, `rival_activity(seance-room)`, `investigation_choice(seance-room)`, `discovery(e-service-route)=public`, `discovery(e-quill-cue-sheet)=public`, `rival_activity(edwin-rusk)`, `competitive_window_opened(the-locked-box)`, `minigame_started(the-locked-box)`, `minigame_action(pin-1..4)=set` ×4, `discovery(e-cylinder-43)=private`, `minigame_result(the-locked-box)=human-win`, `investigation_choice(edwin-rusk)`, `discovery(e-rusk-denial)=public`, `discovery(e-cylinder-43)=public`, `first_look_closed(e-cylinder-43)=public`, `investigation_choice(writing-room)`, `discovery(e-bookend)=public`, `discovery(e-gideon-final-note)=public`, `investigation_choice(clara-hensley)`, `discovery(e-clara-lie)=public`, `discovery(e-clara-transcribed-43)=public`, `last_call`, `case_file_commitment(clara-hensley)=not-solved`, `completion`, `survey_handoff`.

**Run B** — `run_id` `7e933637-6e94-49e4-b4e0-963cea0f08a9` (full sequence, 34 events, `duplicates: []`):
`opening_complete`, `investigation_choice(gideon-materials)`, `discovery(e-cylinder-index)=public`, `discovery(e-cylinder-transcript)=public`, `discovery(e-clara-access)=public`, `rival_activity(seance-room)=pursued`, `investigation_choice(seance-room)`, `discovery(e-service-route)=public`, `discovery(e-quill-cue-sheet)=public`, `rival_activity(edwin-rusk)=followed`, `competitive_window_opened(the-locked-box)`, `minigame_started(the-locked-box)`, `minigame_action(pin-1..4)=set` ×4, `discovery(e-cylinder-43)=private`, `minigame_result(the-locked-box)=human-win`, `investigation_choice(clara-hensley)`, `discovery(e-clara-lie)=public`, `discovery(e-clara-transcribed-43)=public`, `discovery(e-cylinder-43)=public`, `first_look_closed(e-cylinder-43)=public`, `leverage_choice(follow-the-thread)=spend`, `inference_action(clara-hensley)=follow-the-thread`, `discovery(e-clara-evasion)=public`, `investigation_choice(writing-room)`, `discovery(e-bookend)=public`, `discovery(e-gideon-final-note)=public`, `investigation_choice(beatrice-ashcombe)`, `discovery(e-beatrice-threat)=public`, `discovery(e-beatrice-letters)=public`, `last_call`, `case_file_commitment(clara-hensley)=not-solved`. Stopped at the survey screen; `#openSurvey` was never clicked.

**Run C** — `run_id` `20ba3d58-d548-4f1a-b582-5e823954a992` (full sequence, `duplicates: []`):
`opening_complete`, `investigation_choice(gideon-materials)`, `discovery(e-cylinder-index)=public`, `discovery(e-cylinder-transcript)=public`, `discovery(e-clara-access)=public`, `rival_activity(seance-room)`, `investigation_choice(seance-room)`, `discovery(e-service-route)=public`, `discovery(e-quill-cue-sheet)=public`, `rival_activity(edwin-rusk)`, `competitive_window_opened(the-locked-box)`, `minigame_started(the-locked-box)`, `minigame_result(the-locked-box)=rival-win`, `discovery(e-cylinder-43)=private`, `leverage_choice(listen-in)`.

**Run D** — `run_id` `2a7c5311-dd03-4ede-ba66-bbe33f467b6e` (checkpoint captures; see "Notes for later tasks"):
- First move: `investigation_choice(beatrice-ashcombe)`, `discovery(e-beatrice-threat)=public`, `discovery(e-beatrice-letters)=public`. Leverage still 1.
- Lock: resolved `rival-win` with no pins set (~19-20s).
- Post-lock: `leverage_choice(listen-in)` choice `save` once; `leverage: 1`.
- Before Last Call, discoveries included (all present): `e-beatrice-threat`, `e-beatrice-letters`, `e-cylinder-index`, `e-cylinder-transcript`, `e-clara-access`, `e-service-route`, `e-quill-cue-sheet`, `e-cylinder-43`, `e-rusk-denial`, `e-rusk-found-cylinder`, `e-rusk-sighting`, `e-clara-lie`, `e-clara-transcribed-43`, `e-private-detail-match`. Leverage 0 (spent on the Beatrice revisit's "Follow the Thread" inference).
- Committed: culprit `clara-hensley`; pieces `e-cylinder-transcript`, `e-service-route`, `e-rusk-sighting`, `e-clara-transcribed-43`, `e-private-detail-match`; `case_file_commitment(clara-hensley)=solved`.
- `abandonment_events: 0`.
- Stopped at the survey screen; `#openSurvey` was never clicked.

**Run E** — `run_id` `1e3efa8b-d5a8-4734-875a-c52498a2ef53` (full sequence, `duplicates: []`):
`opening_complete`, `investigation_choice(gideon-materials)`, `discovery(e-cylinder-index)=public`, `discovery(e-cylinder-transcript)=public`, `discovery(e-clara-access)=public`, `rival_activity(seance-room)`, `investigation_choice(seance-room)`, `discovery(e-service-route)=public`, `discovery(e-quill-cue-sheet)=public`, `rival_activity(edwin-rusk)`, `competitive_window_opened(the-locked-box)`, `minigame_started(the-locked-box)`, `minigame_action(pin-1)=break`, `discovery(e-cylinder-43)=public`, `minigame_result(the-locked-box)=break`, `investigation_choice(edwin-rusk)`, `discovery(e-rusk-denial)=public`.

**Run F** — `run_id` `41d17908-8079-4e94-a163-c64f3df08d1d` (full sequence, `duplicates: []`):
`opening_complete`, `investigation_choice(gideon-materials)`, `discovery(e-cylinder-index)=public`, `discovery(e-cylinder-transcript)=public`, `discovery(e-clara-access)=public`, `rival_activity(seance-room)`, `investigation_choice(seance-room)`, `discovery(e-service-route)=public`, `discovery(e-quill-cue-sheet)=public`, `rival_activity(edwin-rusk)`, `competitive_window_opened(the-locked-box)`, `minigame_started(the-locked-box)`, `discovery(e-cylinder-43)=public`, `minigame_result(the-locked-box)=abort`, `investigation_choice(writing-room)`, `discovery(e-bookend)=public`, `discovery(e-gideon-final-note)=public`.

## 360px layout

All four checkpoints measured `scrollWidth: 360`, `innerWidth: 360` (`sw <= iw`, pass), and zero buttons under 44px tall (`small: []`).

| Screen | scrollWidth | innerWidth | Buttons under 44px | Screenshot taken |
|---|---|---|---|---|
| Opening | 360 | 360 | none | yes |
| First choice grid | 360 | 360 | none | yes |
| Lock stage | 360 | 360 | none | yes |
| Last Call | 360 | 360 | none | yes |

## Excluded run_ids

- `811b3eff-afcc-4b72-b67b-1298ca93a980` — QA #16 opened the survey (no submission); exclude any Jotform entry carrying it.
- `7e933637-6e94-49e4-b4e0-963cea0f08a9`, `20ba3d58-d548-4f1a-b582-5e823954a992`, `2a7c5311-dd03-4ede-ba66-bbe33f467b6e`, `1e3efa8b-d5a8-4734-875a-c52498a2ef53`, `41d17908-8079-4e94-a163-c64f3df08d1d` — QA runs (B, C, D, E, F); none reached the survey screen's "Open survey" action, so none reached Jotform.

## Survey instrument (read-only inspection)
**Inspection date:** 2026-09-27 · **Method:** Jotform read-only connector metadata and rendered form view; no survey answers entered or submitted.

**Form:** `262397917027062` · **Title:** Nightcap Paper Test #2 — Post-Play Research · **Enabled:** yes (`ENABLED`) · **Question count reported by connector:** 31 · **Submission count reported by connector:** 3.

### Visible questions

| # | Exact wording | Type | Scale or options |
|---|---|---|---|
| 2 | Overall, how fun was this prototype? | Radio scale | 1 is Not fun; 5 is Very fun (1–5) |
| 3 | How much did you feel like a detective? | Radio scale | 1 is Not at all; 5 is Very much (1–5) |
| 4 | Would you want to keep playing? | Radio choice | Yes; Maybe; No |
| 5 | How clear was what you could do next? | Radio choice | Very clear; Mostly clear; Mostly confusing; Very confusing |
| 6 | What was the most interesting or fun moment? | Text area | Free text |
| 7 | What felt confusing, boring, repetitive, or too much like operating an interface? | Text area | Free text |
| 8 | Did anything feel over-signposted or like the prototype told you what to think? | Text area | Free text |
| 9 | Was there anything you wanted to investigate, say, accuse, use, or do but could not? | Text area | Free text |
| 10 | How difficult was it to remember useful information while playing? | Radio choice | Very easy; Mostly easy; Neutral; Mostly difficult; Very difficult |
| 11 | What single change would most improve this experience? | Text area | Free text |
| 12 | Anything else you want us to know? | Text area | Free text |

**First free-text question:** #6, “What was the most interesting or fun moment?”

**Hidden telemetry fields (names only):** `prototype_version`, `run_id`, `started_at`, `completed_at`, `duration_seconds`, `action_sequence`, `investigation_branches`, `discoveries`, `pulse_result`, `case_commitment`, `final_next_interest`, `device_class`, `browser_class`, `completion_status`, `time_to_first_investigation_seconds`, `major_investigations`, `event_sequence`, `abandonment_point`.

**Post-submit redirect:** Not exposed by the connector; Task 5 smoke run is the proof.

**Partial or unfinished submission setting:** Not exposed by the connector.

**QA #16 Run A lookup:** Searched the read-only submissions tool for exact `run_id` `811b3eff-afcc-4b72-b67b-1298ca93a980` (Jotform field `q14_textbox12`). The connector returned no matching submission. Run A remains listed under “Excluded run_ids”; no survey submission was made for QA.

**Run A device-class note:** The QA #16 prefill link reported `device_class=mobile` even though the run was described as desktop. The fixture source sets this value from `window.matchMedia("(max-width: 640px)")`, so the field represents CSS viewport width rather than physical device type. The QA evidence does not include Run A's measured `innerWidth`; this finding is unresolved and should not be interpreted as proof of a phone run or a telemetry defect.

## Smoke run
<filled by Task 5>
