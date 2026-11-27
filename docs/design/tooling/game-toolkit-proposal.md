---
id: engineeringpractice.design.tooling.game-toolkit-proposal
namespace: engineering-practice
title: "Arcwright Game Toolkit: Proposal"
owner: Nico Janssen
status: draft
review_by: "2027-02-27"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# Arcwright Game Toolkit: Proposal

> Current version: v0.4 DRAFT
> Last updated: 2026-11-27
> Status: Draft, **pending founder approval**. Nothing here is approved build scope.
> Canonical path: docs/design/tooling/game-toolkit-proposal.md
> Task: [AW-373](../../roadmap/tasks/AW-373-make-the-game-mini-game-and-playtest-toolkit-a-product.md), [issue #523](https://github.com/nickejanssen/arcwright/issues/523)

## The one decision

**Approve the first slice only, and start it now?** (Recommended: yes, as long as the 1 December and 5 December targets stay safe.)

The goal is the one you gave: play testing and iterating are too difficult today. The first slice is judged on that.

| Piece | What you get | Done when | Size |
|---|---|---|---|
| **N1** Play command ([AW-372](https://github.com/nickejanssen/arcwright/issues/520), already a task) | One command in the mini-game tool opens a Wi-Fi room for a package | AW-372's own six criteria pass | 1 to 3 build days |
| **N2** One-page guide | How to change Battle of Wits, check it and put it on phones | Someone new runs the room within 15 minutes using only the guide | About 1 |
| **N3** Claude and Codex both find the mini-game skill | You say what you want; either AI runs the right steps | Five test requests in each AI lead to the expected command | About 1 |
| **N4** Tests stop depending on live settings | A changed question time can be kept without breaking tests | Changing a time in the real game leaves its tests passing | About 1 |

**The test for the whole slice:** you say one sentence ("make the choice time 15 seconds and open the room") and two phones are playing the changed game within 5 minutes.

**Why N4:** in a trial on 27 November that change made 9 of the 17 tests in the main Battle of Wits test file fail. You could play it on your PC, but it would not pass the checks for saving it to the shared copy. The file was restored afterwards.

- **Cost:** about 4 to 6 build days (my estimate from these sizes). The review's comment said 1 to 3; that was too low.
- **Files:** AW-372 already exists. Approval adds one task for N2 to N4. Nothing else is filed.
- **Not included:** a second playable game, new game mechanics, pretend players, new `arcwright` commands, story tools, publishing.
- **Limits you will still have:** only Battle of Wits plays. The room has no join code, so use it on trusted Wi-Fi.
- **Dropped first** if a December target slips: N3, then N2. N1 and N4 are kept longest. The [one-command case start, AW-367](https://github.com/nickejanssen/arcwright/issues/511), is the other half of easier play testing; it is its own task and not part of this approval.

The tooling freeze does not block this work (D-159, your decision of 27 November). Each build still needs its plan approved.

## What slice 1 looks like in use

An invented conversation. Nothing here exists yet.

```text
You:  Make the choice time in Battle of Wits 30 seconds and open the room.
AI:   One problem first. With 30 seconds, the three questions need 95 seconds,
      and the game is capped at 65.
      A) Raise the cap to 95 seconds (recommended: keeps your 30)
      B) Use 15 seconds instead, which fits the cap exactly
      C) Leave it as it is
You:  A
AI:   I will change two numbers: choice time 12 to 30, cap 65 to 95.
      Nothing has changed yet. Go ahead?
You:  Yes.
AI:   Changed and checked. Starting the room.
      On this PC:   http://localhost:8765
      On phones:    http://192.168.1.20:8765   (same Wi-Fi)
      To stop, say "stop the room".
      Later changes: if the room is open, just press Play again.
```

In slice 1 the AI does the 95-second sum because the guide tells it to. A check built into the tool comes in the next stage. Today the room would only complain when someone presses start.

## Now, next and later

Everything you will be able to do is listed in the [capability outline](game-toolkit-outline.md), each row marked with one of these.

| Stage | Pieces | Starts when |
|---|---|---|
| **Now** | N1 play command, N2 guide, N3 AI skill, N4 tests | You approve the decision above |
| **Next** | X1 pretend players with a run report; X2 change content and timing, make variants, add screens; X3 honest "ready" label with a play record, remove and copy; X4 safe preview, confirm and publish | You have used slice 1 on a real change. Each piece gets its own plan |
| **Later** | L1 one `arcwright` command; L2 standing board; L3 playtest planning and notes; L4 results and comparison; L5 porting (AW-349); L6 other games and new-game starter | A named trigger, in the [design page](game-toolkit-design.md#build-pieces) |
| **Stories** | Separate proposal, right after this one is approved (your Q6) | See [stories and creators](game-toolkit-story-and-creators.md) |

Mini-game work comes before stories and whole games; that was your answer. **Which pieces, and in what order, is my recommendation.**

## The lifecycle in one picture

```text
1 Brainstorm ─► 2 Create ─► 3 Configure ─► 4 Test ─► 5 Playtest
                   ▲             ▲                       │
  Import ──────────┘             │                       ▼
  (something that exists)        └─── learned ─── 6 Research ─► 7 Publish
                                      something
```

What exists today. **Built** means a tool or written procedure exists, not that it has been used in play.

| Step | Mini-game | Story | Whole game |
|---|---|---|---|
| Brainstorm | Partly | Partly | Missing |
| Create | Partly | Partly | Missing |
| Import | Partly | Missing | Missing |
| Configure | Partly | Partly | Partly |
| Test | Built | Built | Partly |
| Playtest | Partly | Partly | Partly |
| Research | Missing | Partly | Partly |
| Publish | Partly | Missing | Partly |

Evidence for every cell: [what exists today](game-toolkit-evidence.md#journeys).

## How you will know it works

Proposed starting targets. Measure today's figure first.

| Measure | Target | From |
|---|---|---|
| One sentence to a changed game on two phones | Under 5 minutes | Now |
| New reader of the guide to first success | Under 15 minutes | Now |
| Approved idea to playable draft, familiar mechanic | 2 build days or less | Next |
| Third variant of one mechanic | Under 2 hours, no engine change | Next |
| Your time per new mini-game | 2 hours or less | Next |
| AI cost per mini-game | Record the first two, then set a cap within the monthly limit (D-114) | Next |
| Playtest end to written summary | Same day | Later |
| Times you had to ask for help, or an AI used the wrong tool | Falls each month | Now |

**Stop and rethink** if, after two real mini-games, you still ask an AI to run raw scripts or the time from a change to play has not fallen.

**Each piece is done only when used on a real game** that December needs, with the worst three points of friction fixed. Pretend games are used only to show that nothing is tied to Nightcap.

## Risks

| Risk | What we do |
|---|---|
| Toolkit work delays 1 or 5 December | Drop it first, in the order above |
| The guide goes out of date | It changes in the same pull request as the command |
| Tools are built and not used | Real-game rule and the stop rule above |
| A second game cannot be played offline | Known: see [AW-372 corrections](game-toolkit-design.md#aw-372-plan-corrections) |
| Test content goes public by accident | Today drafts publish on merge. Until X4 fixes that, treat any merged test page as public |

**Ownership:** one build session per piece, you approve its plan, and the same session updates the guide. Anything that confused you becomes a task the same day (D-119).

## Questions for later, one at a time

Not needed today. Recommendations in brackets.

1. Run the story-tool importer, AW-306, alongside mini-game work? (Yes.)
2. Require your own merge approval for any change that publishes pages, as an exception to D-157? (Yes.)
3. May the toolkit save a short play record with no player names? (Yes, when X3 is planned.)
4. Do the "ready" checks and previews need the deferral in D-102 lifted? (Lift it for those only.)
5. In version one, is a new game mechanic an engine change made by us? (Yes.)
6. Record your six answers in the decisions log? (Yes.)

## What you have already said

Mini-games first. A written guide, "ask the toolkit" through any AI as the main way in, and terminal commands underneath, with one entry point. The tools ask, offer options and check; final story text stays yours. Built for us now, to a standard fit to sell, with scale in mind. Relabel the two unfinished "ready" games as drafts. Outline every tool before building it. Quoted [word for word](game-toolkit-evidence.md#your-answers-word-for-word).

**The proposed shape**, when all of it exists: you ask an AI, or type `arcwright <area> <verb> <name>`, and one guide in `docs/toolkit/` explains both. Each rule is written once, in `docs/skills/` for the AI and in Python for the checks.

## Word list

| Word | Meaning |
|---|---|
| Mini-game package | The folder holding one mini-game's settings, rules link, screens and content |
| Skill | Written instructions an AI follows for a job |
| Pointer | A short file that sends an AI to the real skill |
| Arc file | The file holding a game's rounds and rules |
| Label | A package's stage: draft, playtest, active (ready) or retired |
| Stub | A placeholder with no working rules |
| Pull request, merge | A proposed change, and accepting it into the shared copy |
| JSON | A text format that programs and AIs read |

## The rest of this proposal

| Page | Read it for |
|---|---|
| [Capability outline](game-toolkit-outline.md) | Everything you will be able to do. Please mark what is missing or wrong |
| [Design](game-toolkit-design.md) | How it works underneath, safeguards, build pieces |
| [Stories and creators](game-toolkit-story-and-creators.md) | Earlier story decisions and the future product for customers |
| [Evidence](game-toolkit-evidence.md) | What exists today, how it was checked, your exact words |
