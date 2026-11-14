---
id: nightcap.design.authoring.case-method-logs.001-the-lido
namespace: nightcap
title: "Case Method Log 001: The Lido"
owner: Nico Janssen
status: draft
review_by: "2027-05-13"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Case Method Log 001: The Lido

> Current version: v0.1 DRAFT
> Last updated: 2026-11-13
> Status: Draft working record of one case. Not a universal method. Not build scope.
> Canonical path: docs/design/authoring/case-method-logs/001-the-lido.md
> Index and purpose of these logs: `README.md` in this folder.
> Companion: `../writing-for-living-stories.md` teaches how to write each line and character well.
> Authority: the Nightcap GDD at `docs/gdd/nightcap/` wins wherever this file disagrees with it.

## What this file is

A record of how one case, the first for the GDD rebuild (spec `docs/specs/0092-nightcap-gdd-rebuild.md`), is being built, written down as it happens. It describes the method used for this case only. Other cases may be built differently and get their own log.

It separates two things on purpose:

- **Done:** steps that have been carried out on a real case, with what was learned.
- **Planned:** steps that are intended but not yet tried. Nothing in the planned section is proven. Each step moves to "done" only after it has been used, with a note on whether it worked.

This file contains no solution material for any case. It may be read by someone who intends to play.

## The quality bar

Set by the founder on 2026-11-13, in his words: a "BBC Sherlock quality mystery" that "does not feel or look like AI slop".

Asked which part of that matters most, he chose **the reveal that recasts**: the answer makes players rethink scenes they already watched. The detail was in plain sight and meant something else.

## Done so far

### Step 1. Get the bar in the author's own words, then narrow it to one quality

A named reference such as a television show does several things well, and they pull a case in different directions. Ask which single quality leads. Here the choice was between "the reveal that recasts" and "reading people from detail". The lead quality decides what the case is built around; the others still appear, in support.

*Learned:* offering two concrete readings of the reference got a decision in one reply. An open "what do you mean by quality?" would not have.

### Step 2. Decide who is allowed to know the solution

Decide this before any solution exists, because it changes every later review. The founder chose to stay unspoiled so he can play the case blind.

Consequences that follow from that choice:

- The author approves premise, cast, tone and sample scenes only.
- Solution material lives in one file marked as spoilers and is never stated in chat, commit messages, pull requests or summaries.
- Review of the solution is delegated to automated case checks plus a separate reviewer who did not write it.
- Sample scenes shown to the unspoiled reader must not single out the detail that matters.

*Learned:* the cost is real and should be said plainly. The first true test of whether the solution lands is the first live session.

### Step 3. Pitch premises as "gathering, death, impossible thing" before designing any solution

Each pitch has exactly three parts:

1. **The gathering.** People in a room with relationships and friction already in place. The GDD requires a social-gathering frame.
2. **The death.** Who, where, and in what state they are found.
3. **The impossible thing.** One image or fact that should not be possible, stated in a sentence.

No solution is designed at this stage. That keeps the pitches honest for an unspoiled reader and stops the author from falling for a trick before the premise has earned it.

Three were pitched across different settings so the choice also revealed setting taste:

| Premise | Setting | The impossible thing |
|---|---|---|
| The Tasting | Modern supper club | Everyone in the room was blindfolded for nine minutes; nobody saw anything |
| The Lido | August 1976, municipal pool, drought | A soaking-wet body at the bottom of a drained pool |
| Round Seven | Modern village quiz night | A sealed answer sheet with a wrong answer, and a perfect score on an unseen round |

The founder chose **The Lido**, against the author's recommendation of The Tasting.

*Learned:* the pitch the author recommended was the one that best served the mechanism. The one chosen had the strongest single image. When the two differ, the image won. Worth watching whether that holds for later cases.

### Step 4. Give the detectives a reason to be there that creates private knowledge

Two options were offered: detectives hired separately before the death by different people over different small matters, or party guests with a reputation for sleuthing who step up. The founder chose **hired separately**.

Each detective therefore starts with a client, a private thread and a reason to distrust the others. That supplies the GDD's "shared baseline plus private unlocks" from the fiction, before any investigation happens.

*Learned:* framing the choice by what each player knows at minute one, not by flavour, made the trade-off clear.

### Step 5. Fix the session length before sizing the mystery

The GDD marks runtime as TESTING, so it was asked. Founder: "60 minutes max we should be able to play in 30 minutes or less though". Recorded reading: a session should normally finish in 30 minutes or less, and must never exceed 60. This is the author's reading of the sentence and is to be confirmed.

That is shorter than either option offered (about an hour, or a full evening), so the case is sized down: about four suspects and three essential truths, one trick, no mid-case turn.

*Learned:* ask length before pitching sizes. Both options offered were too long.

## Freshness record

First log, so there is no earlier case to differ from. Dimensions set so far, for later logs to compare against:

- Setting and era: English municipal outdoor pool, August 1976, drought.
- Social world: a volunteer committee and council politics.
- Kind of impossible thing: a physical state that contradicts the scene (wet body, drained pool, rationed water).
- Player framing: detectives hired separately beforehand over unrelated small matters.
- Length: 30 minutes or less, 60 at most.

## Planned for this case, not yet proven

These are the intended next steps for this case. Treat them as hypotheses.

### Step 6. Build backwards from one trick

Write the true sequence of events first, minute by minute. Then write the false story the room believes. The trick is the gap between them, and it must fit in one sentence. If it needs two tricks to work, it is two cases.

### Step 7. The recast test

List three to five things every player witnesses early. Each must have an innocent reading and a true reading. Each must be shown plainly, never hidden or withheld. The reveal changes what the facts mean, never what the facts were.

A recast fails the test if it depends on information the player could not have had, or on the game having described something misleadingly in its own voice. The fiction may lie; the game must play fair.

### Step 8. Name the essential truths and chart the routes

A small set of truths specific to this case, not a universal "who, weapon, motive, room" template. Each must be reachable by at least two legitimate routes, so no single clue is a hidden point of failure. Chart the dumbest sufficient path explicitly: which facts, in which order, force the conclusion.

### Step 9. Build the cast from pressure

Each suspect gets: something they want tonight, a secret unrelated to the death that explains their suspicious behaviour, and at most one lie. Write people, not prompts: a sheet is good when a line can be judged as something that person would never say.

### Step 10. Every lie ships with its refutation

Write the evidence that exposes a false statement at the same moment the false statement is written. A lie with no refutation in the case is not authorised.

### Step 11. Distribute the case across players

Shared baseline plus private unlocks. Check equal solvability at every supported player count: each player has a legitimate route to every essential truth, without guaranteeing they take it.

### Step 12. Checks against generic writing

- **Portability test.** If a detail could be moved into a different story unchanged, cut it or make it specific.
- **Period facts are verified against sources**, not recalled, and the source is recorded.
- **No stock moves:** identical twins, secret passages, untraceable poisons, a culprit introduced late, a confession that does the detective's work, or coincidence carrying the solution.
- **Names and jobs are chosen, not defaulted.** A name should belong to that person's age, place and class.
- **One ordinary object carries the ending**, per the companion guide's "ordinary line".
- **Read every line aloud** before it is accepted.

### Step 13. Two independent reviews of the solution

- **Blind solve.** A fresh reviewer receives only what a player can obtain and must reach the solution, reporting where they got stuck or guessed.
- **Attack.** A second reviewer receives the full solution and tries to break it: a simpler explanation that fits the same facts, a truth with only one route, a recast that cheats.

The author of the case runs neither.

## Open questions this case should answer

- Does choosing the strongest image over the best mechanism make the solution harder to build? To be answered after Step 6.
- How much of Steps 8, 10 and 11 can be automated as case-graph checks? Depends on the case format in spec 0092, work package 1.
- What is the right number of early "recast" details? Three to five is a guess.
