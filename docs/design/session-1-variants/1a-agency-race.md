---
id: nightcap.design.session-1-variants.1a-agency-race
namespace: nightcap
title: "Version 1a: The Agency Race (Core, Maximize Fun)"
owner: Nico Janssen
status: draft
review_by: "2027-02-20"
sensitivity: internal
source: authored
x-scope-evidence: D-146
tags: [session-1, variants, agency-race]
supersedes: []
---

# Version 1a: The Agency Race (Core, Maximize Fun)

Part of [the version overview](README.md). The founder approved the list of versions and the skill names on 20 November 2026 ("Approve versions and names", issue #429). The details below are still open to his edits. Founder's words (D-146): "a detective agency version that has the building to a final race because everyone is competitive in the dysfunctional agency and they are trying to race the others to the solution. It could be a mix of trivia and caSE QUESTIONS. I like this version to test a lot!"

## What it is

The same murder case, played as a competition between rivals at a dysfunctional private detective agency. Mini-games are the main event: quick trivia and case-question races that build round by round to a final race, which flows straight into Last Call, where each player privately locks a theory. This is the core version: the founder's 1 December end-to-end test plays it on case 1.

## Who it targets

Competitive players who enjoy beating their friends at quick games: the Jackbox and Mario Party crowd. Group 1 in the run order (competitive friends) plays it first.

## How it is composed

| Part | Setup (a starting point, not a rule; D-145) |
| --- | --- |
| Framing | The host presents the group as agents of an agency that competes for one client. Written as a wrapper in host and arc lines (AW-319), not a different case |
| Round 1 | Scene, investigate, then Battle of Wits: easy trivia |
| Round 2 | Scene, investigate, then Search and Find (control), then Battle of Wits with case questions |
| Round 3 | Scene, investigate, then Battle of Wits: logic and mental math |
| Final race | Battle of Wits, mixed questions, bigger prize; runs back to back with Last Call (founder answer 11) |
| Last Call and ending | Unchanged: private theory lock, reveal, verdict, recap |

Five mini-games in three rounds, `mini_game_pick: listed`, so Battle of Wits may repeat (the founder lifted no-repeat for this version only). Every mini-game win earns one extra investigation, as in every version (D-126).

## The goal

Make the game as fun as possible for players who want to compete. Success is that players say they want another round, want to beat the others, and still care about the case at the end.

## How it is different from the others

| Compared with | Difference |
| --- | --- |
| 1b Newcomers | More games, more pressure, a final race, less explanation |
| 1c Story and intrigue | Games are the main event, not interruptions; the score is shown loudly |
| 1d Deduction and puzzles | Questions reward speed and knowledge, not careful reasoning about the case |

It is also the only version that repeats a mini-game.

## What is being tested

- Does racing make people want to beat each other and keep playing?
- Does one game kind returning each round drag (the founder's D-136 worry)? Versions 1b to 1d keep the no-repeat rule, so the groups' answers can be compared.
- Do case questions keep players thinking about the case, or feel like a quiz about something else?
- Does the final race flowing into Last Call feel like one ending?

## Why this variation

It is the founder's stated priority and his best guess at the version people enjoy most ("I like this version to test a lot"). It is also the cheapest fun test: one text-only mini-game (Battle of Wits) carries most of it, and the arc file only arranges it. If it fails, the result says whether the fault is the repetition, the race, or the quiz content, because the other versions change one of each.

## Mini-games and side games

| Role | Game | Status |
| --- | --- | --- |
| Cohort (main) | Battle of Wits, repeated four times with different question mixes | New, text only; played on its own first (AW-348, founder answer 3) |
| Control | Search and Find, once in round 2 | New; one drawn scene; provisional |
| Side games | None. The race is the point | |

Alternates if a slot needs filling (see [the candidate list](minigame-slotting.md)): Crime Scene Smash and Room Service Roulette.

## What the survey adds

The shared questions of the overview, plus "How much did you want to beat the others? (1 to 5)" and "Did the same kind of game coming back each round get dull? (1 to 5)".

## What it costs

| Part | Cost |
| --- | --- |
| Arc setup (slots, final race before Last Call, `listed`) | Arc file only (verified by reading: phases and `mini_game_pick` exist after AW-344) |
| Battle of Wits | New mechanic, text only: phone answers, a timer, ranking by correct then fast, no art |
| Search and Find | New mechanic and one drawn scene (art) |
| Question banks | Writing. Questions written by a person need no approval; model-written ones would need a prompt (hard rule) |
| Case questions | Writing per case, from facts players can see; each checked so none gives away the solution |
| Agency host lines | Writing (AW-319; the founder made the agency framing a condition of D-123) |

## Ready if (1 December)

Screens built, case 1 loaded and fair, Battle of Wits and Search and Find built and Battle of Wits played on its own first, question bank and host lines written. The final race can be cut first, and the control swapped for a fixed Battle of Wits round, so the version still runs.

## What it looks like (invented example)

The host opens: "The Pelican Detective Agency has a new client and no budget, so you will all be competing for the only desk." On each phone the player is an agent with a rivalry card. Round 1's Battle of Wits runs ten seconds a question on every phone at once: "Which animal's fingerprints resemble a human's?" The TV shows last place to first. In round 2 the questions turn to the case: "Who signed the hotel register before nine?" (invented), answered from facts the players have already seen. After round 3 comes the final race, and Last Call opens on the same TV with its countdown.

## Prior art

Jackbox *Trivia Murder Party*: rounds of trivia, mini-games between them and a final race to the exit (verified at excerpt level, jackboxgames.fandom.com). *Mario Party*: a mini-game after each round with big swings (reset audit, section 3). Inference: repetition is tolerable in the Jackbox game because the final race changes the stakes; whether that holds here is what this version tests.
