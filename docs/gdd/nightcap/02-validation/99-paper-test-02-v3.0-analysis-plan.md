---
id: nightcap.gdd.nightcap.02-validation.99-paper-test-02-v3.0-analysis-plan
namespace: nightcap
title: Nightcap — Paper Test #2 v3.0 Analysis Plan
owner: Nico Janssen
status: active
review_by: "2027-03-27"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Nightcap — Paper Test #2 v3.0 Analysis Plan

**Status:** APPROVED — 2026-09-28, founder

## Dataset boundary

- **Fixture:** `nightcap-paper-test-02-v3.0`, fixture version 3.0, route `https://nickejanssen.github.io/arcwright/nightcap/paper-test-02/v3.0/`.
- **Instrument:** Jotform form `262397917027062`, instrument version 2.2. v3.0 uses this existing instrument; the telemetry's `prototype_version` must equal `3.0`.
- **Window:** opens on the date of the first invite and closes at the stopping rule below.
- **Target:** 6–8 included sessions from new, representative players, as defined below.

## Inclusion and exclusion

Include one completed, v3.0 submission for each eligible tester. A new player has never played v2.1 or v2.2 and has not seen the design. A representative player plays party games, mystery games, or murder-mystery nights and is not the founder's close friend or family member; friends-of-friends qualify. If a person submits more than once, retain only their first eligible completed submission.

Exclude the QA #16 survey-open run `811b3eff-afcc-4b72-b67b-1298ca93a980`, the founder's labeled smoke run and any partial entry it creates, founder or team runs, repeat runs after the first eligible completion, unfinished entries, and submissions whose `prototype_version` is not exactly `3.0` or is missing. Match exclusions by `run_id` where available. Keep tester names and the invited/started/submitted tracker private and outside the repository; report only counts from it.

## Stopping rule

Stop at 8 included sessions, or 3 weeks after the first invite if at least 6 sessions are included. If fewer than 6 are included after 3 weeks, the founder decides whether to extend. Do not send invites until this plan is approved.

## Completion rate

Calculate included completed submissions divided by testers reported as having started in the founder's private tracker. Report numerator, denominator, and percentage; do not put tracker identities in this repository. Proposed threshold: at least 75% completion.

## Hypotheses and proposed thresholds

Evaluate each percentage over the included sessions. A required response or telemetry field that is missing makes that session unmeasurable for that metric and does not count toward meeting its threshold; report missingness separately. Use medians for numeric ratings and elapsed time. Report counts alongside percentages because the sample is small.

| Hypothesis | Measure and source | v2.2 baseline | Proposed bar |
|---|---|---|---|
| **H1 Detective agency** | Telemetry only: first `investigation_choice` target per included session from `event_sequence`; report target distribution and any missing streams. The survey has no dedicated agency/autonomy rating. Q3 detective feeling is reported under H5, not treated as a separate H1 measure. | Three Q3 ratings were 3, 2, 2 (median 2). Only one v2.2 event stream is available; it contains one first target (`mara_document`), so a multi-player target spread baseline is unavailable. | No single first-move target is selected by more than 75% of included players. |
| **H2 Clarity without handholding** | Q5, “How clear was what you could do next?” Report each option. Q8 free-text feedback is a non-gating diagnostic for over-signposting. | Q5: 2/3 “Mostly clear”; 1/3 “Mostly confusing”. | At least 75% choose “Very clear” or “Mostly clear”; no more than one chooses “Mostly confusing” or “Very confusing”. |
| **H3 Observation before interpretation** | Telemetry only: share of included sessions with at least one `inference_action` in `event_sequence`. Q8 comments may explain over-signposting but are descriptive, not a separate numeric gate. | Only one v2.2 event stream is available and it contains 0 `inference_action` events; the other two streams are missing. Baseline is incomplete. | At least 75% of included players make one or more `inference_action` events. |
| **H4 Competitive cohesion** | Telemetry only: share with a `leverage_choice` (spend or save) and median `post_lock_return_seconds`, derived from elapsed times in `event_sequence`. Report missing streams and unmeasurable intervals. | Only one v2.2 event stream is available; it records one saved Leverage choice. Its events lack timestamps, so post-lock return time is unavailable. | At least 75% make a Leverage choice; median post-lock return is at most 60 seconds. |
| **H5 Pull** | Q2 fun rating; Q3 detective-feeling rating; Q4 “Would you want to keep playing?”; completion rate from the private tracker. | Q2: 3, 3, 3 (median 3). Q3: 3, 2, 2 (median 2). Q4: 1/3 “Yes”, 2/3 “Maybe”. Completion rate baseline unavailable because no started-player denominator is recorded here. | Median Q2 at least 4; median Q3 at least 4; at least 50% answer “Yes” to Q4; completion rate at least 75%. |

## Gate 1 mapping

- **Pass:** all five hypotheses meet their approved thresholds and at least 6 eligible sessions are included.
- **Narrow v3.x successor:** H5 meets its approved threshold, but one or more of H1–H4 does not.
- **Larger design correction:** H5 does not meet its approved threshold.
- **Inconclusive:** fewer than 6 eligible sessions are included when the window closes. Record neither pass nor fail; the founder decides the next step.
- Also report the Case File solve rate (`case_commitment.correct`) as descriptive context; it is not a gate.

## Founder approval

The founder approved the v3.0 thresholds and analysis plan on 2026-09-28. The approved numeric rules above remain the v3.0 historical contract. No further approval request or draft-status condition applies to this version.
