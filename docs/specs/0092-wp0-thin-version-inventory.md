---
id: nightcap.specs.0092-wp0-thin-version-inventory
namespace: nightcap
title: "Spec 0092 Work Package 0: Thin-Version Inventory Of The Current Build"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-123
tags: []
supersedes: []
---

# Spec 0092 Work Package 0: Thin-Version Inventory Of The Current Build

**Status**: Reviewed by the founder on 2026-11-16 ("Inventory reviewed", issue #353). That permits writing the three rebuild specs (AW-302). It approves no spec, no code and none of the decisions in section 10. One correction was added after the review; see the end.

**Author**: Claude Code | **Date**: 2026-11-15 | **Task**: AW-300 | **Snapshot**: main at `bd7f32c`

**Canonical path**: `docs/specs/0092-wp0-thin-version-inventory.md`

## Plain-language goal

A list of what exists in the code today, checked against the thin first version of Nightcap, with each part marked **keep**, **change**, **build** or **retire**. It exists so that the three rebuild specs (AW-302) start from what the code really does and nobody rebuilds something that is already there.

"Retire" means the thin version does not use it. Nothing is deleted, moved or unregistered by this document (spec 0092, Q9).

## How it was checked, and its limits

- **Checked by reading code:** which engine modules the API imports, every API route, how a live session moves from beat to beat, what calls the mini-game engine, the arc file fields, and the two screen codebases' file lists and API calls.
- **Checked by search only:** the rows that say "no code found". The search covered `engine/`, `api/`, `sdk/src/`, `dashboard/src/` and `nightcap-web/src/`, excluding tests.
- **Not done:** the build was not run on a TV and phones (AW-301), so the screen rows have no play evidence. The two largest screen files (`nightcap-web/src/ui.ts`, `dashboard/src/screens/DisplayScreen.tsx`) were sized and searched, not read line by line. No case solution file was opened.
- **Line numbers** are from the snapshot above and will drift.

## 1. The finding that changes the plan

**Much of the engine is built and tested but cannot be reached from a running game.**

A running game talks to the engine only through the API. The API imports nine engine modules: `arc`, `characters`, `db`, `events`, `knowledge`, `mini_games`, `narrator`, `session`, `telemetry`. It imports none of these: `interactions` (investigation choices and limits), `scoring` (accusations, points, the countdown), `case` (the case and the fairness check), or the working parts of `claims` and `resources`. Those are exercised by tests and by the headless harness only.

What a live session can do today:

1. Create a session, join by code, start, pause, resume, end (`api/routers/sessions.py`, `api/routers/lobby.py`).
2. A player types something as their character. When every player has typed once in the current beat, the session moves to the next beat (`engine/characters/service.py:164`, `engine/session/service.py:332`). Every condition the arc author wrote is treated as met (`engine/session/service.py:790`).
3. An AI character answers, limited by what it knows, and the answer is recorded (`engine/characters/service.py:250`, `engine/characters/dialogue.py:242`).
4. A screen can read an active mini-game run and send answers to it, but nothing ever creates a run (section 6).

So the thin version is less "rewrite the engine" and more "connect what exists, in a new shape, and build the endgame". That is good news for the date and it moves the risk: the work is wiring and screens, which only a played session can prove.

## 2. The thin version, feature by feature

| Must-have | What exists | Works in a live session | Disposition | Where |
| --- | --- | --- | --- | --- |
| Join with a room code, two to four players | Join code, lobby, join token | Yes | **Keep** | `api/routers/lobby.py:78`; `api/routers/sessions.py:241`, `:265`; `engine/session/service.py:437`, `:562` |
| Opening: who you are and why you are here | An opening beat with written content, for the old game | Yes | **Change**: new arc file and content | `nightcap/couch-race.arc.json`, beat `pour` |
| Three beats, each one round | The arc engine runs any beat graph, loops included. The live rule for leaving a beat is "everyone typed once" and always takes the first exit | Partly | **Change**: a real rule for when a round ends and which exit is taken | `engine/arc/arc_state.py`; `engine/session/service.py:332`, `:772` |
| Six investigations per player | A per-player limit on choices exists, per beat, held in memory only | No | **Change**: a budget across the whole game, saved, with an API route | `engine/interactions/models.py` (`InteractionLimit`); `engine/interactions/director.py:35` |
| A simple notebook of what you found | No notebook. Two records it can be built from: evidence delivered to each player, and who said what to whom | The second, yes. The first, no | **Build**, small, on those records | `engine/claims/evidence.py:15`, `:40`; `engine/db/orm.py:762` |
| A story-wrapped mini-game each round | The mini-game engine, four packages, and a place in the arc file to attach one to a beat | Answers yes; starting, timing out and returning no | **Change** (AW-303, section 6) | `engine/mini_games/runtime.py`; `engine/arc/models.py` (`BeatDefinition.mini_games`) |
| Last Call: countdown and a private lock | Countdown arithmetic and a table of locks, both inside the points-scoring code | No | **Change**: lift them out of scoring | `engine/scoring/calculator.py:86`; `engine/scoring/resolver.py:30`; `engine/db/orm.py:902` |
| Final theory: culprit plus a short causal chain | No code found | No | **Build** | Search only |
| A rule-based check of the final theory | A solver and a fairness check, written for generated cases | No | **Build** new; reuse the idea | `engine/case/solver.py`; `engine/case/invariants.py:19` |
| A written case that passes a fairness check | The case module builds cases from skeletons and a taxonomy. Only the harness calls it | No | **Build** the written-case format; keep the fairness rules as a pattern | `engine/case/resolver.py`; `engine/harness/runner.py:235` |
| Reveal, Truth, Verdict, short Postmortem | A narrator bridge between beats; end-of-game awards inside scoring | The bridge, yes | **Change** the bridge's content; **build** Verdict and Postmortem | `engine/narrator/bridge.py`; `engine/scoring/superlatives.py` |
| Host lines written by a person, shown as text | Thirteen line files. No code reads them | No | **Build** a reader (AW-291, or a thinner one; open question) | `docs/design/line-libraries/` |
| Survey and a record of play | A replay-intent route, an events table, telemetry builders | Yes | **Keep**; rename game words (AW-304) | `api/routers/sessions.py:221`; `engine/db/orm.py:374`; `engine/telemetry/` |
| A dropped phone can rejoin | Join tokens are validated; the story position is saved on pause. What players typed is held in memory and is lost if the API restarts | Partly | **Change** (AW-308) | `engine/session/service.py:550`, `:199`; `engine/characters/service.py:79` |
| The TV never shows private information | Every event carries who may see it; a privacy test suite exists in one of the screen codebases | Yes | **Keep**, and keep the tests whichever screens survive | `engine/events/models.py` (`AudienceTarget`); `nightcap-web/tests/privacy-matrix.test.ts` |

## 3. Engine modules

Sizes are lines of Python outside tests. "Live" means the API can reach it today.

| Module | Lines | Live | Disposition | Reason |
| --- | --- | --- | --- | --- |
| `engine/arc` | 828 | Yes | **Keep**, small change | Beat graphs, loops and pacing work (`engine/tests/test_arc_state.py:328`). Change: the default arc and the game words in section 7 |
| `engine/session` | 1,318 | Yes | **Change** | Owns the beat-to-beat rule, which is the old game's simplified one |
| `engine/characters` | 1,919 | Yes | **Keep** | Knowledge-limited dialogue is the unique part and works live |
| `engine/knowledge` | 296 | Yes | **Keep** | Records who knows what and from whom (`engine/knowledge/graph.py:36`, `:245`) |
| `engine/events` | 348 | Yes | **Keep** | Audience-targeted events and the stream to screens |
| `engine/mini_games` | 3,531 | Partly | **Change** | Section 6. The largest module; its rewards are worded as clues |
| `engine/narrator` | 127 | Yes | **Keep**, new content | |
| `engine/telemetry` | 828 | Yes | **Change** | Play records use one game's words (D-115, AW-304) |
| `engine/db` | 1,178 | Yes | **Change** | Tables named `accusations`, `suspect_locks`, `contradiction_flags`. Any change is a migration and needs founder approval |
| `engine/safety`, `engine/routing` | 919, 512 | Yes | **Keep** | Not touched by the thin version |
| `engine/interactions` | 713 | **No** | **Change** | Investigation choices and limits exist but are in memory and have no route |
| `engine/claims` | 377 | Partly | **Keep** the records; **retire** contradiction flagging for the thin version | Recording a claim is live; flagging is not, and the thin version has no contradiction mechanic |
| `engine/case` | 1,226 | **No** | **Keep** as is; **build** the written format beside it (spec 0092, Q10) | |
| `engine/scoring` | 686 | **No** | **Retire** for the thin version, after lifting out the countdown and the lock | The thin version has no points (spec 0092, R12) |
| `engine/resources` | 545 | **No** | **Retire** for the thin version | It is Leverage, item 3 of the "if it fits" list |
| `engine/harness` | 819 | Tests only | **Change** | Needed for the headless full-game run; today it resolves a generated case for the old game |
| `engine/dressing` | 183 | **No** | Not decided | Nothing imports it. Its purpose was not checked |

## 4. Arc file

Two arc files are registered (`config/arcs.json`): `nightcap/couch-race.arc.json` (six beats, the playable old game) and `nightcap/arc.json` (eight beats, the older Imposter design, still the engine's default, `engine/arc/registry.py:101`).

| Arc field | Disposition for the new arc file |
| --- | --- |
| `beats`, `beat_graph`, `entry_conditions`, `exit_conditions`, `audience_targets`, `pacing_config`, `authored_content`, `tension_target` | **Keep.** Three round beats plus opening, Last Call and ending |
| `mini_games` on a beat | **Keep.** One binding per round |
| `interactions`, `interaction_ids` | **Change.** The investigation menu; the limit moves from per beat to per game |
| `min_players`, `max_players` | **Change** to 2 and 4 for play; data shapes stay valid to 8 (spec 0092, Q2) |
| `narrator`, `content_rails`, `authorial_intent`, `obligations` | **Keep** |
| `resource_effects` | **Retire** for the thin version (Leverage) |
| `play_mode` (`imposter`, `detective_race`, `cooperative`) | **Change.** Game words inside an engine list (section 7) |
| `knowledge_rules.killer_knows_they_did_it`, `victim_config`, `kill_config`, `murder_timing_range`, `revelation_step_range` | **Retire** from the new file. They are murder-mystery words in the engine's arc model (`engine/arc/models.py:119`) and belong to AW-274 |
| `generative_elements` | **Change.** The first case is written, not generated; authored lines ship first (spec 0092, Q8) |

## 5. API routes

All under `/v1`. Route handlers are thin, as the architecture requires.

| Route group | File | Disposition |
| --- | --- | --- |
| Sessions: create, host, get, start, pause, resume, end, replay-intent, players, join | `api/routers/sessions.py` | **Keep** |
| Lobby: lobby state, lobby-join | `api/routers/lobby.py` | **Keep** |
| Events stream | `api/routers/events.py` | **Keep** |
| Characters: list, get, input, add AI | `api/routers/characters.py` | **Keep**; input stops being the thing that ends a beat |
| Knowledge: assert, revoke, query | `api/routers/knowledge.py` | **Keep** |
| Mini-games: active run, display view, submissions, host commands (cancel, resolve) | `api/routers/mini_games.py` | **Keep**; add nothing here for starting a run, which belongs to the engine |
| Costs | `api/routers/costs.py` | **Keep** |
| **Missing:** choose an investigation; read my notebook; lock a final theory; read the verdict | None | **Build**, in the engine-spine and endgame specs |

## 6. What the mini-game wiring needs (input to AW-303)

| Step | State | Where |
| --- | --- | --- |
| Start a run when a round reaches its mini-game | **Missing.** Nothing outside tests calls `create_run` or `start_run` | `engine/mini_games/runtime.py:316`, `:363`. The natural trigger is beat entry, where other on-entry work already happens: `engine/session/service.py:412` |
| The clock fires | **Missing.** Nothing calls `check_timeout`, and the API has no timer task | `engine/mini_games/runtime.py:514`; `api/main.py` |
| The run ends the round | **Missing.** A finished run scores, releases facts into what characters know and publishes events, but does not tell the session to move on | `engine/mini_games/runtime.py:675` |
| Rewards | Packages release clues. The GDD wants opportunities such as first look or an extra action | `engine/mini_games/models.py` (`ClueVariant`, `DelayedClueFallback`) |

One decision for the engine-spine spec: what fires the clock. The two plain options are a timer inside the API process, or checking the deadline each time a screen asks for the active run. The second is simpler and survives a restart; the first is exact. The spec author recommends one and the founder approves it with the spec.

## 7. Game-specific words inside `engine/` (input to AW-274)

Counted outside tests: murder-mystery words (suspect, accusation, killer, murder, detective, culprit, clue, victim, contradiction, interrogation) and the game's name.

| Module | Count | Examples |
| --- | --- | --- |
| `engine/case` | 169 | `synthetic_detective`, `find_anchor_contradictions` |
| `engine/mini_games` | 143 | `ClueVariant`, `DelayedClueFallback` |
| `engine/scoring` | 119 | `AccusationResolver`, `wrong_accusation_cost` |
| `engine/telemetry`, `engine/harness` | 25 each | `build_contradiction_outcome_payload`, `_resolve_case_for_detective_race` |
| `engine/claims` | 22 | `ContradictionOutcome` |
| `engine/arc` | 21 | `PlayMode.imposter`, `killer_knows_they_did_it`, the `nightcap` default arc |
| `engine/db` | 19 | Tables `accusations`, `suspect_locks`, `contradiction_flags` |
| `engine/characters`, `engine/session` | 7 each | The transition cause `first_correct_accusation` (`engine/session/service.py:785`) |

The game's name appears 14 times in six files, mostly comments, plus the default arc. The host's name does not appear in `engine/`.

The thin version must not add to this list (spec 0092 acceptance criteria). Renaming what is there touches the database and several modules, so it is hard-rule work and stays in AW-274 and AW-304.

## 8. Screens: two codebases

| | `dashboard/` | `nightcap-web/` |
| --- | --- | --- |
| Size | 2,643 lines | 5,301 lines in `src/`, plus 20 test files |
| Built with | React 18 and Vite | No libraries. Pages are built as text in `src/ui.ts` (1,683 lines) |
| Talks to the engine through | The connection kit, `sdk/` | Its own copy of an API client, `src/connector.ts` (493 lines) |
| Started by the rehearsal script | Yes (`scripts/rehearsal.py:459`) | No |
| Used in the August rehearsal | Yes | No |
| Mini-games | One mini-game's screens written by hand into the app (`src/screens/tmst/`, 1,304 lines) | A kit any mini-game package can use, and a loader for each package's own screen code (`src/mini-game-kit/`, `src/mini-games/`) |
| Privacy tests | None found | Yes (`tests/privacy-matrix.test.ts`, `tests/mini-game-privacy-matrix.test.ts`) |
| Old-game code | The hand-written mini-game screens | `src/couch-race/display-projection.ts` |

**Recommendation, for founder review:** keep `dashboard/` as the one client. It already uses React and the connection kit, which is what ADR-0026 and the build-versus-adopt review (technology stack 2.11.7) point to, and it is the path the rehearsal script runs. Bring across from `nightcap-web/` the three parts worth keeping, all plain TypeScript: the mini-game kit, the package screen loader, and the privacy tests. Then stop using `nightcap-web/src/ui.ts`, `src/connector.ts` and the old-game projection, and replace the hand-written mini-game screens in `dashboard/` with the loader.

Two cautions. This recommendation was made without watching either client run (AW-301), and `nightcap-web/` is also the Cloudflare Worker, so its hosting role must be re-homed before session 3 (AW-269). Nothing is deleted on this recommendation.

## 9. Spec 0092's reconciliation table, row by row

| Row | Verdict | What the code shows |
| --- | --- | --- |
| R1 Repeating loop | **Corrected** | Arcs can loop (`engine/tests/test_arc_state.py:328`). Missing: a live rule for choosing which exit to take; today it is always the first (`engine/session/service.py:783`) |
| R2 Written case graph | **Confirmed**, with an addition | No written-case format. Addition: the case module is not reached by a live session at all |
| R3 Investigation and budget | **Corrected** | A per-player limit per beat exists (`InteractionLimit`). Missing: a budget across the game, saving it, and a route |
| R4 Knowledge is not proof | **Corrected** | A per-player record of delivered evidence exists (`engine/claims/evidence.py:40`). Missing: the rule that only held evidence counts in the final theory |
| R5 Notebook and memory | **Corrected** | The who-said-what record exists and is live (`engine/db/orm.py:762`). No notebook, suspect cards or private notes |
| R6 Case Board | **Confirmed** by search | No code |
| R7 Mini-game windows | **Corrected** | Section 6: three missing links the table did not list |
| R8 Rival activity | **Confirmed** by search | One unrelated mention in `engine/characters/service.py`; no feed |
| R9 Reactions and re-entry | **Confirmed** | Pacing interventions and the narrator bridge exist (`engine/arc/pacing.py`, `engine/narrator/bridge.py`) |
| R10 Leverage | **Confirmed**, with an addition | `engine/resources` exists and is not live |
| R11 Last Call | **Corrected** | The countdown and lock live inside scoring and are not live. The fairness check exists for generated cases (`engine/case/invariants.py:19`) |
| R12 No numeric score | **Confirmed** | `engine/scoring` computes points and is not live, so retiring it for the thin version removes nothing a player can see |
| R13 Reveal to Postmortem | **Confirmed** | A `truth` beat and awards in scoring; no Verdict or Postmortem |
| R14 Player count | **Confirmed** | The old game's arc allows 2 to 8; the default arc requires 4 |
| R15 Difficulty and accessibility | **Confirmed** by search | No engine code. One unrelated mention in a screen file |
| R16 Screens | **Confirmed**, with an addition | Section 8: two codebases and a recommendation |

## 10. Decisions this inventory raises

Each is asked one at a time, with a recommendation, when its spec is written. None is decided here.

1. Which screen codebase survives (section 8), and with it whether that client may add React (already an open question).
2. What happens to the old game's arc and code (spec 0092, Q9). Recommendation: leave it registered and untouched until session 1 has been played, so the August path still runs.
3. What fires the mini-game clock (section 6).
4. Whether the host's line reader is the full AW-291 or a thinner one for session 1 (already an open question).

## Your steps

1. Read section 1. It is the one finding that changes how big the rebuild is.
2. Read the "Disposition" column in section 2. Say if any must-have is marked in a way that surprises you.
3. Read the recommendation in section 8. You do not need to decide it now; say whether it sounds right.
4. Reply on issue #353 with "inventory reviewed" or with what to change. That unlocks the three rebuild specs (AW-302).

## Correction after the review (2026-11-16)

Found while writing spec 0093. It corrects one row and changes no disposition the founder was asked about.

- **Section 2, "Opening" row.** The row says the opening's written content works in a live session. It does not. The arc file holds written content for each beat (`authored_content`), but no engine or API code reads it, and the shared screen shows the beat's internal name (`dashboard/src/screens/DisplayScreen.tsx:349`). Sending a beat's written scene to the screens is build work, in spec 0093 Part C (AW-325).
- **Section 6, two additions.** A mini-game run does not record which beat it belongs to, and pausing a session does not pause its run. Both are covered by spec 0093 Parts C and E.
- **Section 2, "Last Call" row, and section 3, `engine/scoring`.** The inventory proposed lifting the countdown and the lock out of the points-scoring code. Reading that code for spec 0094 showed both are built around penalties for wrong accusations (`engine/scoring/calculator.py:77`, `engine/scoring/resolver.py:30`) and a table named for suspects. Spec 0094 proposes building Last Call on the clock from spec 0093 instead and leaving `engine/scoring` untouched and unused. This is a proposal inside a draft spec, not a decision.
