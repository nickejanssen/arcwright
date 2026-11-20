---
id: nightcap.design.session-1-variants.1d-deduction-and-puzzles
namespace: nightcap
title: "Version 1d: Deduction And Puzzles"
owner: Nico Janssen
status: draft
review_by: "2027-02-20"
sensitivity: internal
source: authored
x-scope-evidence: D-146
tags: [session-1, variants, deduction, puzzles]
supersedes: []
---

# Version 1d: Deduction And Puzzles

Part of [the version overview](README.md). The founder approved the list of versions and the skill names on 20 November 2026 ("Approve versions and names", issue #429). The details below are still open to his edits. Founder's words (D-146): "a maximize deduction, investigation, and puzzles version".

## What it is

The same case with the mini-games turned into evidence work. Each game is a puzzle that feels like something a detective does (scan a scene, open a lock, solve a logic puzzle), and none rewards trivia or speed alone. The host helps players remember what they found, never what it means.

## Who it targets

Players who like working things out: the *Murdle* and escape-room crowd. Played only if a fourth group is found; 1e needs a fifth (run order, group 4 on case 1, then group 3 plays it on case 2).

## How it is composed

| Part | Setup (a starting point, not a rule; D-145) |
| --- | --- |
| Round 1 | Scene, investigate, then Search and Find (control), framed as scanning the scene for what does not belong |
| Round 2 | Scene, investigate, then Lock Picking for everyone, on a cash box all players can reach |
| Round 3 | Scene, investigate, then Battle of Wits in logic-only form ("Three suspects, one lies: who?") |
| Side game | A solo Lock Picking find if AW-345 is built |
| Final race | None |
| Last Call and ending | Unchanged; investigations stay at six per player (spec 0092 Q5) |

Three group mini-games, `mini_game_pick: fitting`, no repeat. A solo run does not count against no-repeat (founder answer 9).

## The goal

Make players feel they worked it out themselves. Success is a high "I worked it out myself" score and a puzzle the group names as the best part.

## How it is different from the others

| Compared with | Difference |
| --- | --- |
| 1a Agency race | Reasoning and care are rewarded, not speed and knowledge; no race |
| 1b Newcomers | Harder, with puzzles and logic questions; no hand-holding |
| 1c Story and intrigue | The solo find is a puzzle, not a private story moment; the games are the investigation, not interruptions of it |

## What is being tested

- Do puzzle-style mini-games make players feel they worked it out themselves?
- Is logic-only Battle of Wits better liked by this cohort than trivia?
- Does a lock to pick feel like detective work?
- Does a harder, quieter game still hold the group together?

## Why this variation

"Deduction, investigation and puzzles" is what the GDD says a good detective game rewards: essential proof is earned by investigating, and winning a skill challenge does not substitute for it. This version tests how far toward puzzles the mini-games can go before the game stops being about the murder. It also tests whether Battle of Wits works as a puzzle game (logic only) and not only as a quiz, which decides how much of that game's cost is shared with 1a.

## Mini-games and side games

| Role | Game | Status |
| --- | --- | --- |
| Control | Search and Find, round 1 | New; shared |
| Cohort | Lock Picking, everyone at once, round 2 | Adapt or build; the built Evidence Locker #402 (one player, verified in its manifest) is the nearest |
| Cohort | Battle of Wits, logic only, round 3 | New; shared with 1a and 1b |
| Side game (solo) | Lock Picking find | Needs AW-345 |

Alternates (see [the candidate list](minigame-slotting.md)): The Counterfeit Concierge, The Séance Has Been Double-Booked, The Clockmaker Pleads the Fifth and Switchboard After Midnight; The Emergency Seating Committee can be tried on paper first.

## What the survey adds

The shared questions, plus "Did you feel you worked it out yourself? (1 to 5)" and "Which puzzle was the best one?"

## What it costs

| Part | Cost |
| --- | --- |
| Arc setup | Arc file only |
| Lock Picking | Adapt or build (shared with 1c); the group form hands every player the same lock at once |
| Logic question bank | Writing |
| Deeper puzzle mechanics (comparing samples, rebuilding a damaged record, tracing a timeline; GDD Story Fit Rule) | Not in December; new mechanics after the first group sessions |

## Ready if (15 December)

Lock Picking built, a logic question set written, and a fourth group found.

## What it looks like (invented example)

Round 1: "Scan the hotel lobby for what does not belong." Everyone searches the same picture on their phone. Round 2: every phone shows an identical lock on a cash box; the first to open it reads what is inside. Round 3: "Three suspects, one lies. The cook says the gardener lied, the gardener says the cook lied, the maid says neither did. Who lies?" The winner of each game gets one extra investigation (D-126), never case information.

## Prior art

*Murdle*: solo, daily, pure deduction (reset audit, section 3). *Unlock!* and *Exit: The Game*: escape-room card games where puzzles gate progress and difficulty is rated (recalled). *Return of the Obra Dinn*: deducing identities from evidence with no hand-holding (recalled).
