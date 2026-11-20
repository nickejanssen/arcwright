---
id: nightcap.design.session-1-variants.1e-variety
namespace: nightcap
title: "Version 1e: Variety (Direction 1)"
owner: Nico Janssen
status: draft
review_by: "2027-02-20"
sensitivity: internal
source: authored
x-scope-evidence: D-144
tags: [session-1, variants, variety]
supersedes: []
---

# Version 1e: Variety (Direction 1)

Part of [the version overview](README.md). Proposed, not approved. Founder's words (D-144, 19 November 2026): "Direction 1 with 2 as variant 1b". Direction 1 was the orchestrator's option "a different skill every round". When asked where Direction 1 should live in the four versions, the founder answered: "Make it a fifth version" (answer 12 on issue #429).

## What it is

The mini-game set the founder first chose: every round ends in a group game that tests a different skill, with Lock Picking as an anytime game. No game kind repeats, there is no final race, and the games are the Mario Party kind of variety.

## Who it targets

Players who like a mixed bag of games and do not want to play the same thing twice: the party-game crowd that enjoys trying a new game every few minutes. This target is my proposal. The founder named the Mario Party variety himself, but he did not name a cohort for this version.

## How it is composed

| Part | Setup (a starting point, not a rule; D-145) |
| --- | --- |
| Round 1 | Scene, investigate, then Search and Find (control): eyes |
| Round 2 | Scene, investigate, then Battle of Wits, a mix of trivia and logic: wits |
| Round 3 | Scene, investigate, then a bluffing game: reading people |
| Anytime game | Lock Picking, solo, for whoever finds a locked box: hands |
| Final race | None |
| Last Call and ending | Unchanged |

Three group games, one per round, and `mini_game_pick: fitting`, so no mechanic repeats (D-136, D-147). A solo run does not count against no-repeat (founder answer 9).

## The goal

Test whether variety is what makes mini-games fun. Success is that players name different favorite games, no single kind of skill decides every round, and nobody is bored by repetition.

## How it is different from the others

| Compared with | Difference |
| --- | --- |
| 1a Agency race | The opposite bet: 1a repeats one game and builds to a race; 1e never repeats and has no climax. This is the cleanest test of the founder's no-repeat rule (D-136) |
| 1b Newcomers | Three different games with no extra explanation; harder to learn |
| 1c Story and intrigue | Games are the main event, not interruptions; the scoreboard is shown |
| 1d Deduction and puzzles | Three different skills, not three kinds of puzzle; a bluffing game and no logic-only round |

## What is being tested

- Does a different skill each round keep everyone in it, or does one skill (for example trivia) decide the winner?
- Does the same player win every round, or do wins spread?
- Does the bluffing game work with 2 to 4 players?
- Which of the four games do players name as their favorite?
- Is variety better liked than 1a's repeated game?

## Why this variation

It is the founder's original mini-game choice, and it applies the GDD's "broad skill portfolio" law (`docs/gdd/nightcap/01-authoritative-gdd/04-minigame-competitive-pulse.md`). The orchestrator also cited a Mario Party designer's documented view that plain rules let a whole family play and that a mini-game after each turn gives a chance to earn what wins the game (GameGene records quoted by the orchestrator session; I have not checked them myself). It pairs with 1a: one group of players plays one of them and then the other, so the pair tests repeat against variety directly.

## Mini-games and side games

| Role | Game | Status |
| --- | --- | --- |
| Control | Search and Find, round 1 | New; shared |
| Main game | Battle of Wits, mixed questions, round 2 | New; shared |
| Main game | A bluffing game, round 3 | Built: Tell Me Something True (draft; 4 to 8 players; needs a 2 to 4 range, and a screen fix is filed as AW-351). Alternate: Of Course I Work Here |
| Anytime game | Lock Picking, found during investigation | Built nearest: Evidence Locker #402 (one player); needs AW-345 to start from an investigation |

## What the survey adds

The shared questions, plus "Which round was your favorite?", "Did the games feel different from each other? (1 to 5)" and "Did you feel good at any of them? (yes, no)".

## What it costs

| Part | Cost |
| --- | --- |
| Arc setup | Arc file only |
| Mini-games | All four mechanics: Search and Find, Battle of Wits, a bluffing game and Lock Picking. The most build work of the five versions |
| Bluffing game | Adapt Tell Me Something True to 2 to 4 players and fix its screen (AW-351), or build Of Course I Work Here, the hardest new mechanic |
| Question bank | Writing |

## Ready if (15 December at the earliest)

All four mechanics built, the bluffing game working at 2 to 4 players, and a fifth group found. Not before: it needs the most new building (inferred).

## What it looks like (invented example)

Round 1: the TV cuts to "Search the study." Sam and Priya pinch and pan the same scene on their phones, and Sam shouts "found one!" Round 2: timed questions on every phone, trivia then logic. Round 3: each player answers a prompt, one is secretly bluffing, and everyone guesses who. Somewhere in round 2 Sam finds a locked desk drawer; only Sam's phone shows the lock. Then Last Call.

## Prior art

*Mario Party*: a mini-game after each round, and a new kind of game each time (reset audit, section 3; the orchestrator session cites GameGene records, unchecked). *It Takes Two*: most mechanics used for one scene only, which the founder endorsed for D-136. *Deception: Murder in Hong Kong* is the bluffing prior art (verified at excerpt level).
