---
id: nightcap.design.session-1-variants.minigame-slotting
namespace: nightcap
title: "Candidate Mini-Games And Where Each Version Would Use Them"
owner: Nico Janssen
status: draft
review_by: "2027-02-20"
sensitivity: internal
source: authored
x-scope-evidence: D-146
tags: [session-1, variants, minigames, candidates]
supersedes: []
---

# Candidate Mini-Games And Where Each Version Would Use Them

Part of [the version overview](README.md). The founder approved the list of versions and the skill names on 20 November 2026 ("Approve versions and names", issue #429). The details below are still open to his edits. Written because the founder said: "we should discuss the list of candidate minigames we want to try out. I'm thinking it's at least 10 between what has been built and not built, but if we can slot the minigames per variation, then we can plan what minigames need to be built and playtested independent of nightcap."

## Words used here

| Word | Meaning |
| --- | --- |
| Control game | The one mini-game every version plays with identical rules. Search and Find, provisionally. It is a role inside a version, not a version |
| Main game | A group mini-game that belongs to a version's cohort and fills a round slot |
| Anytime game | A mini-game that can occur at any time during a session, not at a fixed point. Example: Lock Picking when a player finds a locked box. Founder, 20 November 2026, word for word: "Any time game referred to games like lock picking that could occur at any time as opposed to the other mini games that have fixes points during the play of Nightcap session." |
| Fixed-point game | A mini-game at a fixed point in a session, such as the slot after a round |
| Side game | The version sheets' name for an anytime game that one player or a pair finds (solo or pair), outside a round slot |
| Standalone | Playable on its own, on a phone or laptop, with Nightcap off (AW-348) |

## The candidate list: 14 games

Status is **built** (a package exists in `nightcap/mini_games/`, verified by reading its manifest), **new** (a design only), or **idea** (a card in the [idea bank](../../gdd/nightcap/04-supporting-design/minigame-idea-bank.md), a recommendation not yet validated). Player ranges for built games are what their packages declare (spec: D-142 says each game declares its own range). No shipped game declares 2 or 3 players (HANDOVER), so every built game that needs 4 or more is skipped at 2 or 3 by the `fitting` rule (D-147).

| # | Game | What it is | Status | Declared players | Build class | Primary skill | Also uses |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **Search and Find** | Everyone searches the same busy scene on their phone and taps hidden items | New. Nearest built: Scene Sweep (evidence search race, draft, 4 to 8, 105 s, no screen) | Target 1 to 8 | One drawn scene, a phone screen | Observation | - |
| 2 | **Battle of Wits** | Timed trivia, logic, mental math and case questions; fastest correct ranks first | New | Target 1 to 8 | Text only, plus written questions | Deduction | Expertise |
| 3 | **Lock Picking** | Pick a lock on your phone; solo, pair or group | New. Nearest built: Evidence Locker #402 (clue-gated lock breach, 1 player, 60 s, active) | Built: 1. Target 1 to 8 | Adapt the built game; a group start | Tradecraft | - |
| 4 | **Crime Scene Smash** | Match-3 clue race with a shared leaderboard | Built, active | 4 to 8, 90 s | Needs a 2 to 4 range | Observation | - |
| 5 | **Tell Me Something True** | Truth-and-lie bluffing with a spotlight on one player | Built, draft | 4 to 8, 240 s | Needs a 2 to 4 range; a screen mismatch is filed as AW-351 | Interrogation | Undercover |
| 6 | The Emergency Seating Committee | Two swaps to satisfy as many seating demands as possible | Idea (card 6) | Solo to 8 as written | Paper first; light screen | Deduction | - |
| 7 | The Counterfeit Concierge | Spend limited checks to spot forged guest credentials | Idea (card 12) | Solo to 8 as written | Text and small cards | Deduction | Observation |
| 8 | The Séance Has Been Double-Booked | Untangle two spirits' clues and reunite objects | Idea (card 8) | Solo to 8 as written | Illustrated deck | Deduction | Observation |
| 9 | Switchboard After Midnight | Connect hotel calls from partial descriptions | Idea (card 9) | Solo to 8 as written | Text and routing | Deduction | Observation |
| 10 | The Clockmaker Pleads the Fifth | Watch four disagreeing clocks and find the one that skips | Idea (card 14) | Solo to 8 as written | A small animation | Observation | Deduction |
| 11 | Of Course I Work Here | Hidden-role bluff: who missed the staff briefing | Idea (card 4) | Best from 4 players; solo and 2 as written | Hidden-role logic; the hardest | Undercover | Interrogation |
| 12 | An Entirely Normal Walk | Tail a bellhop across a lobby; choose cover or shortcut | Idea (card 1) | Solo to 8 as written | A route screen | Infiltration | Observation |
| 13 | The Witness Protection Sketch Artist | Build a funny portrait from a tray of faces and accessories | Idea (card 17) | Solo to 8 as written | Art tray | Observation | - |
| 14 | Room Service Roulette | Everyone secretly picks lift, stairs or corridor; congestion decides | Idea (card 13) | Solo to 8 as written | Simultaneous-choice rules | Interrogation | Deduction |

The idea cards' ranking in the bank reflects predicted appeal and has not been tested (the bank says so). I picked rows 6 to 14 for the cohorts they fit, not only for their rank.

## Skill labels

Each game has a **primary skill** (what mainly decides who does well) and an **also uses** skill. The vocabulary has two families, because the founder said both Sherlock Holmes and James Bond skills are needed to play the games (20 November 2026): the detective's skills for working a case out, and the spy's skills for getting at it. The labels are my first pass from each game's description. No game has been played, so none is validated, and the founder can change any label or add one. A dash means no second skill.

**Detective skills (Holmes)**

| Skill | What the person does | Games where it is primary |
| --- | --- | --- |
| Observation | Notices details at a scene and spots what does not belong | 1 Search and Find, 4 Crime Scene Smash, 10 The Clockmaker, 13 The Sketch Artist |
| Deduction | Reasons from evidence to a conclusion, by logic and elimination | 2 Battle of Wits, 6 The Emergency Seating Committee, 7 The Counterfeit Concierge, 8 The Séance, 9 Switchboard |
| Interrogation | Reads people, spots lies and anticipates what others will do | 5 Tell Me Something True, 14 Room Service Roulette |
| Expertise | Specialist knowledge that cracks a case, like a remembered fact | None as primary; Battle of Wits uses it as a second skill |

**Spy skills (Bond)**

| Skill | What the person does | Games where it is primary |
| --- | --- | --- |
| Tradecraft | Practical field skills and gadgets, such as picking a lock | 3 Lock Picking |
| Infiltration | Moves unseen and gets in without being noticed | 12 An Entirely Normal Walk |
| Undercover | Holds a cover story and bluffs as someone else | 11 Of Course I Work Here |
| Risk | Nerve at the table: pushing luck and betting against others | None among the 14 |
| Pursuit | Chases, evades and keeps going under pressure | None among the 14 |
| Codebreaking | Cracks ciphers and codes | None among the 14 |

**What the labels show (inferred):**
- Versions 1a to 1d between them use Observation, Deduction and Tradecraft, plus Expertise as a second skill in Battle of Wits. None uses an Undercover, Infiltration or Interrogation game as a main game.
- 1e's bluffing game is the only December game with Interrogation (and Undercover) in it.
- Risk, Pursuit and Codebreaking have no game among the 14. Idea-bank cards outside the 14 that would fill them: Bid Me Goodnight (card 15) and Going Down? (card 3) for Risk, Mind the Carriage Gap (card 16) for Pursuit, and The Floor Is Listening (card 18) for Infiltration. I found no card for Codebreaking, so that label may need a new game or may be dropped. This mapping is my reading of the cards, not tested.
- Direction 1's four skills were eyes, wits, reading people and hands (the orchestrator's labels, not the founder's). They map to Observation, Deduction, Interrogation and Tradecraft. The founder said the first names did not sound like an investigator's skills.

## Where each version would use them

C is the control, M a main game, S a side game (an anytime game), A an alternate if a slot needs filling, and a dash means not used.

| # | Game | 1a Agency race | 1b Newcomers | 1c Story and intrigue | 1d Deduction and puzzles | 1e Variety |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Search and Find | C | C | C | C | C |
| 2 | Battle of Wits | M, repeated | M, easy questions | A | M, logic only | M (mixed) |
| 3 | Lock Picking | A | - | S (solo find) | M (everyone), S | S (anytime) |
| 4 | Crime Scene Smash | A | - | - | - | - |
| 5 | Tell Me Something True | - | - | A | - | M (bluffing) |
| 6 | The Emergency Seating Committee | - | A | - | A | - |
| 7 | The Counterfeit Concierge | - | - | - | A | - |
| 8 | The Séance Has Been Double-Booked | - | - | - | A | - |
| 9 | Switchboard After Midnight | - | - | - | A | - |
| 10 | The Clockmaker Pleads the Fifth | - | - | - | A | - |
| 11 | Of Course I Work Here | - | - | A (deferred) | - | A |
| 12 | An Entirely Normal Walk | - | - | A | - | - |
| 13 | The Witness Protection Sketch Artist | - | A | - | - | - |
| 14 | Room Service Roulette | A | - | - | - | - |

## What this means for building and testing

Three games carry versions 1a to 1d in December: Search and Find, Battle of Wits and Lock Picking. Version 1e adds a fourth, the bluffing game (Tell Me Something True adapted to 2 to 4 players). Everything else is an alternate, so the others can wait without breaking a version.

| Wave | Games | Why | Standalone test first? |
| --- | --- | --- | --- |
| 1 (needed for 1 December, 1a) | Battle of Wits, Search and Find | They carry 1a, and Search and Find is the control in every version | Yes. The founder said Battle of Wits "must" be playtested on its own first |
| 2 (needed for 15 December, 1c and 1d) | Lock Picking, adapted from Evidence Locker #402 | It is the solo side game and 1d's puzzle; a built game exists to start from | Yes |
| Paper trials (no build) | The Emergency Seating Committee, The Counterfeit Concierge, The Séance Has Been Double-Booked | The idea bank calls the seating game the cheapest paper trial; these three are the best candidates to give 1d more puzzles | Paper, then decide whether to build |
| 2 (1e only) | Bluffing game: Tell Me Something True adapted to 2 to 4 players | 1e needs it; built, so a starting point exists | Yes |
| Later | Of Course I Work Here, Crime Scene Smash at 2 to 4, An Entirely Normal Walk, Room Service Roulette, Switchboard, The Clockmaker, The Sketch Artist | They need a new range, new rules or art, and no version needs them | After the first group sessions |

Inference, not measured: waves 1 and 2 are the work that can fit before 15 December. The standalone path for each is AW-348 (play it with Nightcap off) and AW-349 (port and reuse); the mechanic design and build is AW-337.

## Decisions for the founder (none recorded yet; question 1 was answered "Right list, move on" on issue #429)

1. Is this the right candidate list, and what is missing or should go?
2. Should the paper trials in the table run before any of the 'later' games are built?
3. Answered: see the definition of anytime game above.
