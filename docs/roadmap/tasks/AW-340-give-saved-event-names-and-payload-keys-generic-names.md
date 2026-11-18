---
id: productroadmap.roadmap.tasks.aw-340-give-saved-event-names-and-payload-keys-generic-names
namespace: product-roadmap
title: "AW-340: Give Saved Event Names And Payload Keys Generic Names"
owner: Nico Janssen
status: active
review_by: "2027-03-01"
sensitivity: internal
source: authored
x-scope-evidence: D-115
tags: []
supersedes: []
---

# AW-340: Give Saved Event Names And Payload Keys Generic Names

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Arcwright  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-12-31

## Plain-English Summary

Some of the engine's saved records still carry one game's words: a saved event called `accusation_submitted`, another called `mini_game_clue_delivery`, a field called `killer_identified`. Any other game built on Arcwright would inherit those names. Give each a generic name, without losing the old rows or breaking the screens that read them. This is not needed for the 12 December session; it is the tail of D-115.

## Why This Matters

D-115: play data is captured at engine level in one shape for every game, and game-specific words in records become game configuration. AW-304 (pull request #412) made the six play facts generic and added a test that stops any new game-worded name, but it left the names that already existed, listed in `engine/tests/test_record_vocabulary.py` (`EXISTING_GAME_WORDED_NAMES`). Renaming saved event types needs no database migration (they are data in `events.event_type`), but other code reads some of them. Table and column renames do need a migration and stay with AW-274 (issue #220).

## Technical Scope

Names in scope, with who reads them (searched 2026-11-17, labelled verified by text search; not run):

| Name | Written in | Read by |
| --- | --- | --- |
| Event `contradiction_*` (the outcome is the suffix) | `engine/claims/events.py`, `engine/telemetry/claims.py` | Engine tests; `evals/continuity_thresholds.json` and `evals/runners/test_continuity_evals.py` |
| Event `accusation_submitted`, `last_call_triggered` | `engine/telemetry/scoring.py` | `engine/scoring/resolver.py`, engine tests |
| Event `mini_game_clue_delivery`, `mini_game_clue_acknowledged` | `engine/mini_games/runtime.py` | `nightcap-web/tests/couch-race-display-projection.test.ts`, engine tests |
| Event `race_track_motion` | `engine/scoring/events.py` | Nothing found outside the writer |
| Payload key `killer_identified` (event `session_completed`) and the end-session API body field | `engine/telemetry/session.py`, `engine/session/service.py`, `api/routers/sessions.py`, `api/schemas/__init__.py` | `nightcap-web/src/connector.ts`, `src/ui.ts` and their tests; API and telemetry tests |

Steps:

1. Choose the generic names with the founder (one question at a time, with a recommendation). Keep a game's own words in that game's configuration, not in `engine/`.
2. Write each new name; keep reading the old name for rows already saved (a small alias map in one place), so old sessions stay readable.
3. For the API body field, accept both names for one release, then drop the old one.
4. Update the readers listed above and the evals; run `nightcap-web` tests.
5. Remove each renamed name from `EXISTING_GAME_WORDED_NAMES` and lower the baselines in `engine/tests/test_record_vocabulary.py`.

Out of scope: renaming tables or columns (`accusations`, `suspect_locks`, `contradiction_flags`, `clue_unlock_record`, `claims.round_index`) needs a migration and founder approval, and stays with AW-274 (#220). Also listed and not decided here: `case_cast_seated`, `engine/case/`, `round_view` (D-113: "round" is not an engine concept).

## Human Collaboration Contract

**Interaction profile:** Decision interview, then independent execution. The founder picks the generic names; a build session does the rest. Touches `engine/`, `api/` and `nightcap-web/`, so it crosses modules and needs plan approval.

## Acceptance Criteria

- [ ] Each name in the table has a generic replacement, chosen by the founder and recorded.
- [ ] Old saved rows are still read correctly (a test with rows under the old names).
- [ ] The vocabulary test allow-list is shorter by exactly the renamed names, and no new game word was added.
- [ ] `nightcap-web` tests and the evals that read these names pass.
- [ ] No database migration in this task; any table or column rename is split out under AW-274.

## Tests/Verification

- `python -m pytest engine/tests api/tests -q`
- `python -m pytest evals/runners -q`
- `cd nightcap-web && npm test`
- `python -m ruff check engine api`

## Dependencies

- AW-304 merged (pull request #412): it adds the vocabulary test this task shortens.
- Related: AW-274 (#220) for table and column renames.
- Not on the critical path for the 12 December session; run after it.

## Must Not Do

- No migration. No table or column rename.
- No change to what any screen shows.
- Do not remove the old name from readers until old rows are no longer needed.
