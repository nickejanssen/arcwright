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

# Version 1a: The Agency Race

Part of [the version overview](README.md). Proposed, not approved. Founder's words (D-146): "a detective agency version that has the building to a final race because everyone is competitive in the dysfunctional agency and they are trying to race the others to the solution. It could be a mix of trivia and caSE QUESTIONS."

## Who it is for

Competitive players who enjoy beating their friends at a quick game: the Jackbox and Mario Party crowd. This is the core version: the founder's end-to-end test on 1 December plays it on case 1.

## What players do and see (invented example, not from a real case)

The host, Vesper, opens: "The Pelican Detective Agency has a new client and no budget, so you will all be competing for the only desk." On their phones each player is an agent with a rivalry card. Round 1 starts with a Battle of Wits: ten seconds a question, every phone at once. "Which animal's fingerprints resemble a human's?" Faster correct answers rank higher, and the TV shows last place to first. The winner earns one extra investigation. In round 2 the questions turn to the case: "Who signed the hotel register before nine?" (invented). These answer from facts the players have already seen, never from the solution. Round 3 adds logic and mental math. After round 3 comes the final race: a mixed set of questions with a bigger prize, then Last Call opens straight away on the same TV with the countdown, and each player privately locks a theory.

## Mini-games (a starting setup, not a rule; D-145)

| Round | Mini-games | Notes |
| --- | --- | --- |
| 1 | Battle of Wits (easy trivia) | Rule-teaching round |
| 2 | Search and Find (control), then Battle of Wits (case questions) | Two slots; the control game is identical in every version |
| 3 | Battle of Wits (logic and math) | |
| Final | Battle of Wits (mixed, bigger prize), then Last Call | Back to back (founder answer 11) |

Five mini-games in three rounds, with `mini_game_pick: listed` so Battle of Wits may repeat (the founder lifted the no-repeat rule for this version only). The set stays adjustable: nothing in the engine fixes the count (D-145, D-147).

## What it tests

- Does racing make people want to beat each other and keep playing?
- Does repeating one game kind drag (the founder's D-136 worry)? 1b to 1d keep the no-repeat rule, so the survey can compare.
- Do case questions keep players thinking about the case, or do they feel like a quiz about something else?
- Does the final race flowing into Last Call feel like one ending?

## What the survey adds

The shared questions of the overview, plus: "How much did you want to beat the others? (1 to 5)" and "Did the same kind of game coming back each round get dull? (1 to 5)".

## What it costs

| Part | Cost |
| --- | --- |
| Arc setup (rounds, slots, final race before Last Call, `listed`) | Arc file only (verified: phases and `mini_game_pick` exist after AW-344) |
| Battle of Wits mechanic | New mechanic, text only. Phone answers, a timer, ranking by correct then fast; no art. Must be played on its own first (AW-348), at the founder's word |
| Search and Find (control) | New mechanic and one drawn scene (art) |
| Question bank | Writing. Questions written by a person need no approval. Questions written by a model would need a prompt, which is an AGENTS.md hard rule |
| Case questions | Writing per case, from facts players can see. Each case's questions must be checked so no question gives away the solution |
| Agency framing in host lines | Writing (AW-319). Founder's D-123 condition. Proposed here as a wrapper in host and arc lines, not a different case, so any case can be played in any version |

## Ready if (1 December)

Screens built, case 1 loaded and fair, Battle of Wits and Search and Find built and Battle of Wits played on its own, the question bank written, agency host lines written. The final race can be cut first (cut order) and the control swapped for a fixed Battle of Wits round, so the version still runs.

## Prior art

Jackbox *Trivia Murder Party*: rounds of trivia, mini-games between them and a final race to the exit (verified at excerpt level, jackboxgames.fandom.com). *Mario Party*: a mini-game after each round with big swings (reset audit, section 3). Inference: repetition is tolerable in the Jackbox game because the final race changes the stakes; whether that holds here is what this version tests.
