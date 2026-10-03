---
id: nightcap.gdd.nightcap.03-playtest-evidence.98-paper-test-02-v2.2-results
namespace: nightcap
title: Nightcap — Paper Test #2 v2.2 Results (Baseline)
owner: Nico Janssen
status: active
review_by: "2027-03-27"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Nightcap — Paper Test #2 v2.2 Results (Baseline)

**Status:** TEST EVIDENCE — baseline for v3.0 comparison; not canon

## Dataset boundary

- **Fixture:** Nightcap Paper Test #2 v2.2, *The Last Toast*.
- **Instrument:** Jotform form `262397917027062`, instrument version 2.2.
- **Date window:** 2026-08-28 00:00 through 2026-08-30 23:59, inclusive; submissions were selected by `created_at`, not `prototype_version` because that field is empty in v2.2 data.
- **In-window submissions:** 3, ordered below by creation time.
- **Outside the window:** none found in the connector results.
- **Source:** raw submission data fetched 2026-09-27 via Jotform connector (read-only).
- **Response labels:** R1, R2, and R3 are anonymous labels in chronological order, not Jotform identifiers.

## Results by question

Question wording and response scales are from the read-only inspection of the same instrument recorded in the v3.0 pre-send QA evidence. Free-text answers below are paraphrased; no identifying information or verbatim response text is included.

| # | Exact wording | Type and scale/options | R1 · Aug 28 | R2 · Aug 29 | R3 · Aug 30 |
|---|---|---|---|---|---|
| 2 | Overall, how fun was this prototype? | Radio scale; 1 is Not fun, 5 is Very fun (1–5) | 3 | 3 | 3 |
| 3 | How much did you feel like a detective? | Radio scale; 1 is Not at all, 5 is Very much (1–5) | 3 | 2 | 2 |
| 4 | Would you want to keep playing? | Radio choice; Yes / Maybe / No | Yes | Maybe | Maybe |
| 5 | How clear was what you could do next? | Radio choice; Very clear / Mostly clear / Mostly confusing / Very confusing | Mostly clear | Mostly confusing | Mostly clear |
| 6 | What was the most interesting or fun moment? | Text area; free text | Enjoyed choosing actions. | Selecting clues was engaging, though the overall experience felt muddled. | Valued moments that offered more autonomy and navigation choices. |
| 7 | What felt confusing, boring, repetitive, or too much like operating an interface? | Text area; free text | Action feedback felt too direct and lacked descriptive depth; wanted more challenge and note-taking support. | Feedback was shared during the live session. | The experience felt linear; phrasing and prompts reduced agency, some ending questions felt tedious, and mechanics or introductions lacked context. |
| 8 | Did anything feel over-signposted or like the prototype told you what to think? | Text area; free text | Some clues were easy to find and their meaning was stated too explicitly. | Feedback was shared during the live session. | Clues and deductions felt handed to the player instead of earned; the writing felt more like a report than an immersive story. |
| 9 | Was there anything you wanted to investigate, say, accuse, use, or do but could not? | Text area; free text | Wanted more exploration options. | Feedback was shared during the live session. | Wanted substantially more freedom to act independently. |
| 10 | How difficult was it to remember useful information while playing? | Radio choice; Very easy / Mostly easy / Neutral / Mostly difficult / Very difficult | Mostly difficult | Neutral | Mostly easy |
| 11 | What single change would most improve this experience? | Text area; free text | Add narrative depth and descriptive detail to support independent exploration. | Improve logical flow and consistency. | Improve writing and flow while giving players more independence and clearer expectations. |
| 12 | Anything else you want us to know? | Text area; free text | Blank | Feedback was shared during the live session. | Reported losing interest and not wanting to return. |

## Telemetry health

The 18 hidden telemetry fields and their populated state in each submission:

| Hidden field | R1 · Aug 28 | R2 · Aug 29 | R3 · Aug 30 |
|---|---|---|---|
| `prototype_version` | Empty | Empty | Populated |
| `run_id` | Empty | Empty | Populated |
| `started_at` | Empty | Empty | Populated |
| `completed_at` | Empty | Empty | Populated |
| `duration_seconds` | Empty | Empty | Populated |
| `action_sequence` | Empty | Empty | Populated |
| `investigation_branches` | Empty | Empty | Populated |
| `discoveries` | Empty | Empty | Populated |
| `pulse_result` | Empty | Empty | Populated |
| `case_commitment` | Empty | Empty | Populated |
| `final_next_interest` | Empty | Empty | Populated |
| `device_class` | Empty | Empty | Populated |
| `browser_class` | Empty | Empty | Populated |
| `completion_status` | Empty | Empty | Populated |
| `time_to_first_investigation_seconds` | Empty | Populated | Empty |
| `major_investigations` | Empty | Populated | Empty |
| `event_sequence` | Empty | Populated | Empty |
| `abandonment_point` | Empty | Empty | Empty |

R1 has all 18 fields empty. R2 has only `time_to_first_investigation_seconds`, `major_investigations`, and `event_sequence` populated. R3 has the first 14 fields populated and the four later-added fields empty. Telemetry is inconsistent across the three records; the connector analysis indicates survey handoff is explicitly visible in only one event stream, and reveal return is unverified for all three.

## Free-text themes

- **Agency and exploration:** R1 and R3 wanted more freedom, exploration, and player-led interpretation. R2's feedback was provided during the live session.
- **Writing and immersion:** R1 and R3 asked for greater descriptive depth; R3 also described the experience as linear, overly guided, and unevenly introduced.
- **Clarity and flow:** R2 asked for more logical consistency. R3 called out abrupt mechanics and introductions and tedious end-of-case prompts.
- **Replay signal:** R1 selected “Yes” for wanting to continue. R2 and R3 selected “Maybe”; R3's final free-text response also reported lost interest.

## Discrepancies with existing records

The raw connector results show 3 submissions in the specified window, all dated between 2026-08-28 21:49:44 and 2026-08-30 20:32:55. This matches `docs/gdd/nightcap/02-validation/98-validation-state-and-remaining-plan.md`, which reports 3, and differs from `docs/specs/nightcap-external-playtest-harness.md`, which reports 2 as of 2026-08-30. The harness specification was not edited; the discrepancy remains documented.

## Evidence limits

- **N = 3; exploratory only.** These responses support descriptive comparison, not population estimates or causal claims.
- The fun rating is 3 for all three respondents; detective feeling is 3, 2, and 2; replay intent is one “Yes” and two “Maybe.”
- Clarity responses are two “Mostly clear” and one “Mostly confusing.” Information-recall difficulty spans “Mostly difficult,” “Neutral,” and “Mostly easy.”
- Most telemetry fields are missing or inconsistent, so these records cannot support a complete run-level behavioral comparison. `prototype_version` is empty in two submissions and was not used to determine eligibility.
- The post-survey reveal return was not verified for any of the three submissions. No identifying details or verbatim tester comments are preserved here.
