---
id: productroadmap.product.nightcap-status
namespace: product-roadmap
title: "Nightcap: Where Things Stand"
owner: Nico Janssen
status: active
review_by: "2027-02-14"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

> Current version: v2.1
> Last updated: 2026-11-26
> Status: Current
> Canonical path: docs/product/nightcap-status.md

# Nightcap: Where Things Stand

One page that says what is playable, what the plan is, what is next, and what the founder needs to do. It is updated whenever a decision is recorded or a milestone lands. It does not replace the task tracker: whether a task is open or closed is answered on GitHub (`python scripts/roadmap_status.py --milestone M7`).

## In one paragraph

As of 26 November 2026, the rebuilt Nightcap runs a whole game of case 1, version 1a, from start to finish without screens: at two and at four players, through the rounds, Battle of Wits, Last Call, the Verdict, the Postmortem and the survey, with no AI call deciding anything (Codex runs, reported on #362). Every screen for that game is built and tested in code, but they have not been played together in a browser or seen on a TV yet. A Codex dress rehearsal in a browser is running now, and the founder's first TV run is planned for 29 or 30 November. Battle of Wits can also be played on its own over home Wi-Fi (PR #506). The targets are the founder's end-to-end test on 1 December, beta-capable with case 2 written on 5 December, and all versions testable by 15 December (D-149). Technology comes first, then story tooling, then story iteration (D-156).

## What is proven, and how far

"Reported" means a build session's report on the linked issue, not re-run by the orchestrator.

| Thing | Built | Auto-tested | Played in a browser | Seen on TV and phones | Seen with real players |
| --- | --- | --- | --- | --- | --- |
| Arcwright engine core | Yes | Yes, about 1,750 Python tests (reported on PR #506) | Does not apply | No | No |
| Case 1, version 1a, converted and fair | Yes, local only, never in Git (D-153) | Fairness checks A0 to A6 pass at 2, 3 and 4 players (reported, #358) | Does not apply | No | No |
| Full game without screens | Yes | Start to survey passes at 2 and 4 players (reported, #362) | Does not apply | No | No |
| Round and Last Call screens | Yes (AW-332, #480, #478) | Yes | Not yet | No | No |
| Endgame screens: Verdict, result, Postmortem, survey | Yes (AW-333 part B, #503) | Yes | Not yet | No | No |
| Battle of Wits mini-game | Yes (AW-337, #494) | Yes | Yes, its own Wi-Fi room (PR #506); real phone not yet | No | No |
| Battle of Wits real questions | No, three sample questions | Does not apply | Does not apply | No | No |
| Old Couch Race game | Yes, superseded | Yes | Yes | Partly, 2026-08-01 | No |
| Online paper test v3.0 and v3.1 | Yes | Yes | Online, unlisted | Does not apply | No; paused (D-111) |

Player evidence so far is three people from the v2.2 paper test: fun 3 of 5, "felt like a detective" 2 to 3 of 5. The fun-quickly gate (Gate 1) is still NOT PASSED.

## The plan: three sessions

| Session | Target | Where | It must prove |
| --- | --- | --- | --- |
| Founder end-to-end test | 2026-12-01 | Founder's house, TV and phones, case 1, version 1a | The game runs start to finish (D-149) |
| Beta-test capable | 2026-12-05 | Founder's house | The founder's feedback is fixed and case 2 is written (D-149) |
| 1 | By 2026-12-15 | Founder's house, two groups of two to four friends | People understand it, enjoy it and finish; versions testable with live groups (D-149, run order D-150) |
| 2 | About 2027-01-09 | Founder's house | The fixes worked; a second case written in a story tool (D-117) |
| 3 | Late January 2027 | Friends' house, without the founder | It works with nobody to help. Needs cloud hosting (AW-269) |

Planning assumption: 10 to 15 founder hours a week, which depends on AI usage limits, on the harness working, and on how much hand-holding the build needs.

## What session 1 contains

**Must have**

- Join with a room code, two to four players.
- Opening: who you are and why you are here.
- Three beats. Each beat is one round (D-113): watch a scene, investigate, review your notes, play one or more mini-games up to a cap set per round (D-136), skinned to the story when that is natural and openly a game when not (D-143), see the story react. No mini-game mechanic repeats in a playthrough; an investigation can also lead one player into a solo mini-game (D-136).
- Session 1 is played as five playthrough versions, each for a kind of player (D-148): 1a Agency race (the core, needed for the 1 December test), 1b Newcomers, 1c Story and intrigue, 1d Deduction and puzzles, 1e Variety. The two planned groups both play 1b on case 1, then 1a on case 2 (D-150). Slipped work drops versions, never the dates (D-149). Sheets: `docs/design/session-1-variants/`.
- Six investigations per player across the game. Review is free.
- A simple notebook: a list of what you personally found.
- Last Call with a countdown and a private lock.
- Final theory: fill a short written account of what happened with pieces you found yourself, and pin one proof; the winner's proof is shown on the TV at the Verdict (D-138).
- The accused reveal, the Truth, the Verdict, and a short Postmortem.
- The host's lines are written by a person and shown as text.
- A debrief survey, and a record of what happened in play (D-115).

**If it fits, in this order**

1. A voice for the host.
2. Living suspect cards.
3. Leverage, earned only, capped at 2.
4. A feed of what rivals are doing.
5. Motion on the TV.
6. Case Board.
7. Difficulty settings.
8. Reading and changing the story graphically in the adopted story tool, plus a viewer for what that tool cannot show (AW-306, AW-317).
9. Friends' recorded voices for characters (AW-320). Only after everything above and every must-have is done; first to cut. Recorded lines, no voice cloning.

**Stretch, in the writing lane.** The detective agency framing: the players are a dysfunctional private investigations agency whose members compete to solve each mystery first (AW-319). It is writing, not build work, so it takes no place in the order above. The founder made it a condition of approving spec 0092 that the thin version includes it as a stretch goal (D-123). Whether it replaces the approved invitation framing is still his choice inside AW-319.

**Not before session 3:** Counterintel, five or more players, cloud hosting.

## Critical path by week

Estimates are inferred, not measured. "Build days" means focused AI build sessions. The dates changed on 2026-11-20 (D-149: 1, 5 and 15 December); the week rows below predate that and are kept for the build estimates.

| Week | Work | Tasks | Build days | Founder hours |
| --- | --- | --- | --- | --- |
| To 2026-11-21 | Agents fixed; index rebuilt; checks required; spec 0092 approved for the thin version; inventory; screen walkthrough; build-versus-adopt | AW-296 to AW-301, AW-309, issue #303 | 4 to 6 | 10 to 12, mostly the case |
| 2026-11-22 to 28 | Three combined specs; case loaded and fair; mini-games start, time out and return; headless full game at two and four players | AW-302, AW-324, AW-325, AW-303, AW-305 | 5 to 7 | 8 to 10 |
| 2026-11-29 to 12-05 | Endgame; screens; play records; story-tool importer; **founder TV run** | AW-328, AW-326, AW-327, AW-304, AW-306, AW-242 | 7 to 9 | 12 to 15 |
| 2026-12-06 to 12 | Fix what the TV run found; preflight; "if it fits" items; **session 1** | AW-308, AW-240, AW-241 | 4 to 6 | 12 to 15 |

Total: about 20 to 29 build days in four weeks, roughly one productive build session every day.

## What must be true

**Before the founder's 1 December test**

- Done: case 1 converted and passing the fairness checks (AW-305, #358; still open for its remaining items).
- Done: a headless run completes at two and four players with no AI call deciding anything (#362).
- Done: every mini-game in the 1a run starts, ends on its own clock, and hands back to the story (AW-303, #356; open only for its TV check).
- Done: Battle of Wits plays on its own, with Nightcap off (AW-348, PR #506).
- In progress: a full game played in a browser with a TV window and phone windows (Codex dress rehearsal, #354).
- Waiting on the founder: Battle of Wits questions and host lines (AW-355, #464, due 30 November); ten sample recap lines (AW-327, #389); four new endgame copy lines (PR #503).
- Not started: the founder's first run on a real TV and two phones (AW-301, #354), planned for 29 or 30 November.
- Later, not needed for 1 December: reusing a ported browser mini-game in an Arcwright experience (AW-349, #444; moved after the 1 December test by D-158); the full theory sentence after the Verdict (AW-364, #504).

**Before session 1**

- The founder has played it start to finish once.
- A dropped phone can rejoin and keeps its private notes (AW-308, #362; automated check in progress).
- The TV never shows private information. Checked by looking, not only by tests (AW-308).
- The survey is ready and the play record is being saved.
- A one-page host cheat sheet exists for when something breaks (AW-308; draft in progress).

## How we will know it worked

The pass bar the founder approved for the paper test on 2026-09-28 is reused as the starting point ([v3.0 analysis plan](../gdd/nightcap/02-validation/99-paper-test-02-v3.0-analysis-plan.md)):

| Question | Bar |
| --- | --- |
| Did they enjoy it? | Median fun at least 4 of 5 |
| Did they feel like detectives? | Median detective feeling at least 4 of 5 |
| Would they play again? (D-116) | At least half answer yes, and note whether anyone asks unprompted |
| Did it finish? | At least three in four reach the end, inside 60 minutes |
| Did they know what to do? | How often the founder had to explain a rule; where players stalled |

A scheduled session is not a passed session. If fun or detective feeling scores below 3, the next step is the core loop, not more features.

## If a gate slips

| Signal | Response |
| --- | --- |
| A version is not ready for its date | Drop versions, never the dates (D-149): cut 1e, then 1d, then 1c; the cut order is in `docs/design/session-1-variants/README.md` |
| Case 1 not approved by 2026-11-28 | Raise it with the founder at once; case 1 is the critical path for the 1 December test |
| Build sessions run short | Cut in this order: the Postmortem becomes fixed text; three mini-games become two; three beats become two; the story-tool importer moves to after session 1 |

## Mini-games inside a real session

Updated 2026-11-26. The 2026-11-14 gaps (nothing started a mini-game, nothing fired its clock, nothing returned to the story) were closed by AW-303 (#413, merged 2026-11-18). In the 1a arc, Battle of Wits stands in for Search and Find until that package exists (PR #500). The headless runs on #362 play it inside the game. It has not been seen on a TV yet.

## Paused: the online paper test

Paper Test #2 is paused (D-111). v3.0 and v3.1 stay online exactly as they are, unlisted. No testers were invited and no outside results exist. Restarting it needs a new decision.

## The tooling freeze

Since 2026-09-27, work on AI helper tooling and the knowledge base has been limited to fixing things that break (D-110). It ends when the rebuilt game's first TV session is played (D-111). Fixing the specialist agents (AW-296) and refreshing the index (AW-297) are break-fixes and are allowed.

## Your steps

1. **Now.** Play Battle of Wits on your phone: in your main folder run `git pull`, then `python -m scripts.play_battle_of_wits`, and open the printed link. Tell the orchestrator what feels wrong.
2. **By 30 November.** Write or approve the Battle of Wits questions and host lines (AW-355, #464).
3. **When asked.** Review the ten recap lines on #389 and the four endgame copy lines on PR #503.
4. **29 or 30 November, about an hour.** First run on a real TV and two phones (AW-301), using the host cheat sheet once it is merged.
5. **1 December.** Play case 1, version 1a, start to finish.
