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

> Current version: v2.0
> Last updated: 2026-11-16
> Status: Current
> Canonical path: docs/product/nightcap-status.md

# Nightcap: Where Things Stand

One page that says what is playable, what the plan is, what is next, and what the founder needs to do. It is updated whenever a decision is recorded. It does not replace the task tracker: whether a task is open or closed is answered on GitHub (`python scripts/roadmap_status.py --milestone M7`).

## In one paragraph

The game you can run today is not the game being shipped. The TV-and-phones build is the older Couch Race design. The Nightcap in the Master GDD has a rebuild plan (spec 0092), approved for the thin version on 2026-11-15 (D-123), and no code yet. That approval permits the inventory of the current build (AW-300) only. The founder chose on 2026-11-14 to keep the date and ship a thin but complete version to friends at his house on 12 or 13 December 2026, with as much added as fits (D-112). The date is at risk, not safe. The two things most likely to move it are the first case and the new screens.

## What is proven, and how far

| Thing | Built | Auto-tested | Deployed | Seen on TV and phones | Seen with real players |
| --- | --- | --- | --- | --- | --- |
| Arcwright engine core | Yes | Yes, 912 tests | No | Partly, through the old game | No |
| Old Couch Race game | Yes, six fixed beats | Yes | No, local only | Partly: two players joined and moved through beats on 2026-08-01 | No |
| Master GDD Nightcap | **No** | No | No | No | No |
| Mini-games | Four packages; two bound to the old game | Yes | No | Not recorded | No |
| Online paper test v3.0 and v3.1 | Yes | Yes | Online, unlisted | Does not apply | No; never sent. Paused (D-111) |

Player evidence so far is three people from the v2.2 paper test: fun 3 of 5, "felt like a detective" 2 to 3 of 5. The fun-quickly gate (Gate 1) is still NOT PASSED.

## The plan: three sessions

| Session | Target | Where | It must prove |
| --- | --- | --- | --- |
| Founder TV run | By 2026-12-05 | Founder's house, alone with a TV and two phones | The game runs start to finish |
| 1 | 2026-12-12 or 13 | Founder's house, two to four friends | People understand it, enjoy it and finish |
| 2 | About 2027-01-09 | Founder's house | The fixes worked; a second case written in a story tool (D-117) |
| 3 | Late January 2027 | Friends' house, without the founder | It works with nobody to help. Needs cloud hosting (AW-269) |

Planning assumption: 10 to 15 founder hours a week, which depends on AI usage limits, on the harness working, and on how much hand-holding the build needs.

## What session 1 contains

**Must have**

- Join with a room code, two to four players.
- Opening: who you are and why you are here.
- Three beats. Each beat is one round (D-113): watch a scene, investigate, review your notes, play a story-wrapped mini-game, see the story react.
- Six investigations per player across the game. Review is free.
- A simple notebook: a list of what you personally found.
- Last Call with a countdown and a private lock.
- Final theory: pick the culprit, then arrange a short causal chain from what you hold.
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

Estimates are inferred, not measured. "Build days" means focused AI build sessions.

| Week | Work | Tasks | Build days | Founder hours |
| --- | --- | --- | --- | --- |
| To 2026-11-21 | Agents fixed; index rebuilt; checks required; spec 0092 approved for the thin version; inventory; screen walkthrough; build-versus-adopt | AW-296 to AW-301, AW-309, issue #303 | 4 to 6 | 10 to 12, mostly the case |
| 2026-11-22 to 28 | Three combined specs; case loaded and fair; mini-games start, time out and return; headless full game at two and four players | AW-302, AW-324, AW-325, AW-303, AW-305 | 5 to 7 | 8 to 10 |
| 2026-11-29 to 12-05 | Endgame; screens; play records; story-tool importer; **founder TV run** | AW-326, AW-327, AW-304, AW-306, AW-242 | 7 to 9 | 12 to 15 |
| 2026-12-06 to 12 | Fix what the TV run found; preflight; "if it fits" items; **session 1** | AW-308, AW-240, AW-241 | 4 to 6 | 12 to 15 |

Total: about 20 to 29 build days in four weeks, roughly one productive build session every day.

## What must be true

**Before the founder TV run**

- The first case exists in the engine's format and passes the fairness check (AW-305).
- A headless run completes at two and at four players with no AI call deciding anything.
- One set of screen code is chosen (AW-300).
- Every mini-game starts, ends on its own clock, and hands back to the story (AW-303).

**Before session 1**

- The founder has played it start to finish once.
- A dropped phone can rejoin and keeps its private notes (AW-308).
- The TV never shows private information. Checked by looking, not only by tests (AW-308).
- The survey is ready and the play record is being saved.
- A one-page host cheat sheet exists for when something breaks.

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
| No founder TV run by 2026-12-05 | Session 1 moves to 19 or 20 December |
| Case not approved by 2026-11-28 | The same slip; the case is the critical path |
| Build sessions run short | Cut in this order: the Postmortem becomes fixed text; three mini-games become two; three beats become two; the story-tool importer moves to after session 1 |

## Mini-games inside a real session

Verified in code on 2026-11-14: the mini-game engine is built and well tested, but nothing in the product starts a mini-game during a session.

| Step | State |
| --- | --- |
| Packages | Four exist. Two are marked active, two are drafts |
| Bound to a beat | The old arc file binds two packages to two beats |
| Starts when the beat is reached | **Missing.** No caller of `create_run` or `start_run` outside tests |
| Player input | Works, and ignores duplicate submissions |
| Clock owned by the engine | Deadline, pause and resume are built and tested |
| Clock actually fires | **Missing.** No caller of `check_timeout` outside tests |
| Validation and scoring | Python decides |
| Consequence | Releases a clue into what characters know, with a fallback on timeout |
| Returns to the story | **Not found.** Nothing links a finished run to the beat ending |
| Real TV and phones | No recorded proof |

The three missing links are AW-303. Separately from the plumbing, the GDD wants a mini-game to grow out of the story and give an opportunity such as first look or an extra action; today's packages release clues. Each needs a story wrapper and a reward change, with the founder's creative approval.

## Paused: the online paper test

Paper Test #2 is paused (D-111). v3.0 and v3.1 stay online exactly as they are, unlisted. No testers were invited and no outside results exist. Restarting it needs a new decision.

## The tooling freeze

Since 2026-09-27, work on AI helper tooling and the knowledge base has been limited to fixing things that break (D-110). It ends when the rebuilt game's first TV session is played (D-111). Fixing the specialist agents (AW-296) and refreshing the index (AW-297) are break-fixes and are allowed.

## Your steps

1. **Done 2026-11-15.** Merge the reset pull request (PR #348).
2. **Save the other session's work.** Open the session on branch `claude/lido-case-and-spec-followups` and send it: "Commit and push your spec 0092 edit and the case folder, and open a pull request." Until then that work can be lost.
3. **Require all checks before merge (AW-298).** GitHub, then Settings, then Branches, then edit the rule for `main`, then add `Lint, Typecheck, Test, Build, and Scan` and `team-ai` under required status checks. About ten minutes.
4. **Done 2026-11-15.** Review and merge the agent fix (PR #352, then PR #376 for decisions-log access).
5. **Done 2026-11-15.** Spec 0092 approved for the thin version, with the stretch goals as a condition (D-123, issue #303). The inventory (AW-300) started the same evening.
6. **Answer the open decisions**, one at a time, when asked: the issues labelled `needs-decision`.
7. **Keep writing the first case** with its session. It is the critical path.
