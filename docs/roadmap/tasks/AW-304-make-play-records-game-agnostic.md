---
id: productroadmap.roadmap.tasks.aw-304-make-play-records-game-agnostic
namespace: product-roadmap
title: "AW-304: Make Play Records Game-Agnostic"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-115
tags: []
supersedes: []
---

# AW-304: Make Play Records Game-Agnostic

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Arcwright  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-12-05

## Plain-English Summary

Make sure every session, for any game, saves the same six generic facts, and that the records do not use one game's vocabulary.

## Why This Matters

The founder's direction is that play data is captured at engine level so any game can learn from it (D-115). The engine already records events, decisions, generated lines, beat states, mini-game runs and consent, but some records use Nightcap words such as accusation and contradiction.

## Technical Scope

- The six facts: story units entered and left, with times; who learned what, and from whom; what each participant chose from what was offered; what each character said; tension against the author's target; cost.
- Find every game-specific word in record and table names and either make it game configuration or list it with a follow-up.
- A short query pack that answers: where did players stall, what content did nobody see, which characters drew attention, was the mini-game reward used.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. A rename that touches a database table needs a migration and founder approval (hard rule).

## Acceptance Criteria

- [ ] After one headless session, one query per fact returns rows.
- [ ] The four questions above are answerable from the record without reading game content files.
- [ ] No new game-specific word enters `engine/`; remaining ones are listed with an issue.

## Tests/Verification

- `python -m pytest engine/tests -q`

## Dependencies

- AW-302: spec 0093 approved. This task is Part F of `docs/specs/0093-engine-spine-for-the-thin-version.md`.
- AW-325, which saves the choices and phase changes these records read.
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- No graph database, dashboard or model training in this task.
- No analysis tooling beyond plain queries.

## What Was Built

Built on 2026-11-17 under spec 0093, Part F. The founder approved the plan the same day (issue #357). No table change, no migration, no new dependency, no model call.

- **Query pack.** `engine/telemetry/play_records.py`: one reader per fact (`story_unit_visits`, `learned`, `choices`, `said`, `tension`, `cost`) and four question functions (`stalled_phases`, `unchosen_opportunities`, `attention_by_subject`, `reward_use`). They read saved rows only and open no content file. Plain selects with grouping in Python, so SQLite and Postgres behave the same.
- **Saved-record changes (additive).** Typed input is now saved as an `events` row of type `player_input` (before, it lived only in memory; spec 0093 said otherwise). A choice's `decisions` row also saves `subject_id`, `subject_kind`, and `allowance` and `spent_after` in its outcome. The first menu read per player per phase visit saves a `menu_shown` row; this is a write on a read path.
- **Vocabulary guard.** `engine/tests/test_record_vocabulary.py`: per-module counts of the inventory's game words may not rise, and no saved event or decision type may carry one unless it already existed.
- **Tests.** `engine/tests/test_play_records.py` plays one scripted headless run at 2 and at 4 players and asserts one reader per fact and each question.
- **Listed, not changed (follow-up, with AW-274, #220).** Tables `accusations`, `suspect_locks`, `contradiction_flags` and their columns, and `mini_game_runs.clue_unlock_record` (renaming needs a migration; the thin version writes none of them). Saved event types `contradiction_*`, `accusation_submitted`, `last_call_triggered`, `mini_game_clue_delivery`, `mini_game_clue_acknowledged`, `race_track_motion`; payload key `killer_identified`. Also `case_cast_seated`, `engine/case/`, `claims.round_index`, `round_view` (D-113: "round" is not an engine concept).
- **Known limits.** `beat_transition.duration_seconds` is an action count, not seconds; times come from `phase_state`. Tension rows exist but the score is a formula of beat position and choice count, and the target is empty unless the arc has `authorial_intent`. An opportunity never offered to anyone is not in the record. Mini-game clue facts are saved with no source character. Question 4 ties a run to its beat by time window until AW-303 records the beat in the run.

