---
id: nightcap.gdd.nightcap.02-validation.99-paper-test-02-v3.1-analysis-plan
namespace: nightcap
title: Nightcap Paper Test 2 v3.1 Analysis Plan
owner: Nico Janssen
status: active
review_by: "2027-04-01"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Nightcap Paper Test 2 v3.1 Analysis Plan

**Status:** Research rules approved by founder, 2026-10-01; no v3.1 player outcomes yet.
**Fixture:** `nightcap-paper-test-02-v3.1`, version `3.1`, proposed route `/nightcap/paper-test-02/v3.1/`.
**Instrument:** Jotform `262397917027062`, version `2.2`. Physical fields, scales, hidden names and redirect remain unchanged.
**Authority:** `docs/specs/0091-nightcap-v3.1-improvements.md` section 2. The approved v3.0 analysis plan remains the historical contract for its own cohort.

## Cohort and stopping rule

Include the first completed v3.1 submission from each of 6 to 8 eligible, representative new players. The window opens on first invite and closes at 8 included submissions, or three weeks after first invite if at least 6 are included. Fewer than 6 at three weeks require a founder decision on extension. Exclude QA, founder, team, smoke, repeat, incomplete, and prior-case-exposed players; exposure to v3.0, solution or design material disqualifies. Reject missing or non-`3.1` `prototype_version`. Keep identities and the started/invited tracker private. Record only counts and anonymous run IDs needed to deduplicate or exclude. Do not mix v2.2 or v3.0 runs into the v3.1 cohort.

Completion rate is verified completed v3.1 submissions divided by privately tracked eligible starts. Report numerator and denominator. Gameplay completion, verified form submission and observed reveal return are three distinct states. A local `survey_handoff` is not a verified submission, and a submitted form is not proof of reveal return. The form return target remains unverified; release needs a separately approved smoke/read-back.

## Decision rules

For every metric report included, measured and missing counts, observed values, and uncertainty bounds. Missing observations never count as success. If a missing value can change a conclusion, the affected hypothesis is inconclusive. All five hypotheses must pass and at least six eligible players must be included for an overall pass. An inconclusive hypothesis prevents an overall pass and an automatic design-failure classification; it calls for research follow-up. If H5 fails on adequate evidence, the v3.0 mapping calls for a larger design correction. If H5 passes and H1-H4 fail on adequate evidence, it calls for a narrow successor. Neither mapping applies to inconclusive evidence.

| Hypothesis | Measure | Approved bar and missingness rule |
|---|---|---|
| H1 Detective agency | First `investigation_choice` target in each included `event_sequence`. Report observed target distribution and missing streams. | For included `N`, missing first targets `U`, and largest observed target count `C`, pass only when at least one target is observed and `(C+U)/N <= 0.75`. Fail when `C/N > 0.75`. Otherwise inconclusive. `research.js::firstTargetGate` implements the bound. Q3 remains under H5. |
| H2 Clarity | Q5 categories; Q8 is descriptive diagnostic only. | At least 75% Very clear or Mostly clear and no more than one Mostly confusing or Very confusing. Bound favorable and confusing counts across missing Q5 responses. Pass only if both bars hold in the adverse bound; fail if any required bar cannot be met even under the favorable bound; otherwise inconclusive. |
| H3 Inference-action uptake | At least one `inference_action` in each included stream. | At least 75%. Bound missing streams as zero or one action. A click shows uptake, not deduction. Ask privately after play, “What made you change your theory?” Record the description outside Jotform until an instrument change is separately approved. |
| H4 Competitive cohesion | Explicit `leverage_choice` spend/save in included streams; attempted-lock result to next investigation/inference interval. | At least 75% explicit choices and median post-lock return at most 60 seconds. Bound missing choice streams. Report spend, explicit save and final unused balance separately; unused balance alone is no choice. Require at least six measured attempted-lock intervals and zero missing attempted-lock intervals. `research.js::postLockTimingGate` implements this timing submeasure. A decline is excluded before that call, counted separately, and has no invented duration. If either submeasure is inconclusive, H4 is inconclusive unless the other conclusively fails. |
| H5 Pull | Pre-reveal Q2 fun, Q3 detective feeling, Q4 keep playing, plus verified submission completion. | Median Q2 at least 4; median Q3 at least 4; at least 50% Yes on Q4; completion at least 75%. Bound missing ratings and responses over their allowed scales/options; missingness that could change any bar is inconclusive. Report each component and observed reveal returns separately. |

Calculate medians from observed numeric values in order; for missing survey ratings, report the lowest and highest possible median using the instrument's actual scale. Do not substitute zero or a neutral rating. For `post_lock_return_seconds`, the start is an attempted lock result and the end is the next investigation or inference event. If no such event exists, the interval is missing. Invalid negative or nonfinite seconds are missing. Five measured intervals are insufficient even if their median is low. Keep the existing v3.0 numeric bars; this plan adds explicit missingness handling and interpretation.

## Non-gating context

Report Case File solve rate descriptively, never as a gate. Report distinct first targets, lock outcomes, declined windows, and device contexts. Do not infer a physical phone from a 360 CSS-pixel desktop viewport. Do not infer accessible competitive equivalence from a decline control. A static build, browser simulation, or transport URL round-trip is not a human response or form read-back.

## Private feedback and device templates

Store private responses outside the repository and telemetry. A public summary may use anonymous run IDs only where needed for deduplication and may omit the exact run when reidentification is plausible.

| Encounter | Observed problem | Supporting evidence | Likely cause | Class (Game/Fidelity/Harness) | Confidence | Affected hypothesis | Smallest fix | Acceptance check | What would disprove diagnosis |
|---|---|---|---|---|---|---|---|---|---|
| Pending observation | Pending | Pending | Hypothesis only | Pending | Pending | Pending | Pending | Pending | Pending |

Device context template: physical device type; browser family/version; operating system; viewport CSS width; input method; assistive technology if volunteered; approximate network conditions; session stage; whether the browser was emulated; observation date. Do not store device fingerprints or identity.

Debrief prompts after play: “What made you change your theory?” and “What felt satisfying or unresolved after the reveal?” Record answers privately as descriptive context, with no survey field or scale change. Keep pre-reveal ratings before showing the truth.

## Approval and release boundary

The founder approved the research rules on 2026-10-01. This does not approve publication, changing Jotform, invitation, live-session claims, or treating results as product decisions. Local checks and draft fixture work continue under the approved six-task plan; external return verification and phone smoke remain separate gates.
