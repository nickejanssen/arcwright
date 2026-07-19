# Nightcap Leverage Advantages And Sabotages

> Current version: v0.1
> Last updated: 2026-07-18
> Status: Proposed design direction
> Canonical path: docs/product/nightcap-leverage-advantages-sabotages.md

**Author**: Codex, founder-directed design session

## References

- [AW-282: Interrogation Round Loop And Question Intents](../../roadmap/tasks/AW-282-interrogation-round-loop-and-question-intents.md)
- [Nightcap Couch Race v1 parent spec](../../specs/0072-nightcap-couch-race-v1.md)
- [Nightcap Couch Race story bible](../../story-bibles/nightcap-couch-race.md)
- [AW-281 Couch Race arc and deterministic case resolution](../../roadmap/tasks/AW-281-couch-race-arc-definition-and-case-generation.md)
- [Architecture: Arc Execution](../../architecture/03-arc-execution.md)
- [Architecture: Event System](../../architecture/08-event-system.md)
- [Architecture: Telemetry](../../architecture/11-telemetry.md)
- [Product decisions log](../../product/decisions-log.csv)
- [Nightcap Couch Race design](2026-07-15-nightcap-couch-race-design.md)

## Overview

This document records the complete research catalog and design filtering for a new earned resource that players can spend to gain an advantage or interfere with another player. The working name for the resource is **Leverage**.

Leverage is separate from question allowances:

- **Questions remaining** controls how many questions a player may ask in a beat.
- **Leverage** is earned through mini-games and other accomplishments, then spent on advantages or sabotage.

The recommended design authors five advantage families and five sabotage families, but exposes only three or four families in an individual session. This preserves learnability while creating replay variation.

This is a proposed design record, not implementation approval. AW-282 may provide a narrow, platform-neutral interaction-modifier seam. A later approved product decision or implementation spec must own the Leverage economy, privacy rules, telemetry, and Nightcap scope.

## Product and architecture boundary

AW-282 currently defines per-beat question-token scarcity, deterministic question menus, and structured interrogation rounds. The Couch Race story bible currently says there is no player interference and that false signals remain falsifiable. This design therefore expands the product surface and must not be silently folded into AW-282 implementation.

The future capability must preserve these boundaries:

- The Python engine remains authoritative for resource balances, eligibility, targeting, effect resolution, and persistence.
- The engine remains game agnostic. Nightcap supplies names, copy, dramatic presentation, and authored effect configuration.
- The engine never changes case truth, deletes evidence, or lets a model decide whether a sabotage succeeded.
- AI may dramatize a deterministic result after resolution. It may not infer session state or choose targets.
- Public answers and private observations retain explicit event audiences.
- Knowledge-state checks remain mandatory before every AI character generation.
- Games that do not configure Leverage ignore the capability.

## Design goals

Every idea was judged against the following criteria:

1. **Detective fantasy**: Does it make the player feel observant, clever, and personally involved?
2. **Agency**: Does the player make a meaningful choice?
3. **Counterplay**: Can the target anticipate, resist, or recover?
4. **Fairness**: Does the case remain solvable and trustworthy?
5. **Table drama**: Will people react, celebrate, accuse, or remember the moment?
6. **Replayability**: Does the effect interact differently with changing evidence and theories?
7. **Clarity**: Can a new player understand it in one sentence?
8. **Pacing**: Does it preserve a 20 to 40 minute experience?
9. **Scalability**: Does it work from 2 to 8 players?
10. **Platform fit**: Can other games use the mechanic without Nightcap-specific engine logic?
11. **Cost**: Does it avoid uncontrolled additional model calls?
12. **Anti-snowballing**: Can a mini-game winner gain an edge without becoming unstoppable?

## Initial catalog: 25 advantages

| # | Player-facing name | Effect |
|---:|---|---|
| 1 | Deep Read | Make your next private observation more specific while still avoiding a truth verdict. |
| 2 | Second Look | Revisit a previous answer and notice one additional behavioral detail. |
| 3 | Follow the Thread | Ask an immediate contextual follow-up unlocked by the answer just heard. |
| 4 | Sharpen the Question | Upgrade an evidence-based question into a stronger authored variation. |
| 5 | Compare Notes | Compare two claims and surface matching or conflicting names, times, places, or objects. |
| 6 | Pin the Timeline | Reveal one verified ordering relationship between known events. |
| 7 | Clear a Name | Eliminate one suspect or explanation from a bounded authored set. |
| 8 | Call the Next Witness | Move an eligible character earlier in the interrogation sequence. |
| 9 | Take the Floor | Resolve your locked question next. |
| 10 | Hold the Floor | Resolve two of your interactions consecutively. |
| 11 | Join the Pressure | Join another player's public question and receive your own private read. |
| 12 | Quiet Word | Receive one answer privately instead of publicly. |
| 13 | Stay Untouchable | Block the next sabotage aimed at you. |
| 14 | Turn the Tables | Reflect a sabotage back at its source. |
| 15 | Accusation Insurance | Reduce the penalty or lockout caused by one incorrect accusation. |
| 16 | Double Down | Stake Leverage for a larger reward if a contradiction or theory proves correct. |
| 17 | Bank a Question | Carry an unused question allowance into the next beat. |
| 18 | One More Question | Buy an additional question beyond the normal allowance. |
| 19 | Peek at the File | Preview the category of an upcoming evidence release. |
| 20 | Choose the Lead | Choose which of several authored evidence branches appears next. |
| 21 | Recover a Missed Clue | Reopen an earlier evidence opportunity. |
| 22 | Build Rapport | Make one character less guarded toward your next question. |
| 23 | Refresh the Menu | Replace current question choices with another eligible set. |
| 24 | Borrow an Angle | Temporarily use a question unlocked by another player's evidence. |
| 25 | Hot Streak | A mini-game victory discounts the next Leverage expenditure. |

## Initial catalog: 25 sabotages

| # | Player-facing name | Effect |
|---:|---|---|
| 1 | Rattle the Witness | Make a character more guarded during a rival's next question without changing factual content. |
| 2 | Cut In | Move your own interaction ahead of a rival's. |
| 3 | Make Them Wait | Move a rival's interaction later in the current round. |
| 4 | Close the Angle | Temporarily close one evidence-based question option and provide a valid replacement. |
| 5 | Jam the File | Prevent one held evidence item from unlocking questions for a single selection. |
| 6 | Listen In | Receive a copy of a rival's next private observation. |
| 7 | Leak the Lead | Reveal the category of evidence driving a rival's investigation. |
| 8 | Show Their Hand | Reveal a rival's selected target or question before it resolves. |
| 9 | Pick Their Pocket | Transfer one Leverage from a rival to yourself. |
| 10 | Raise the Stakes | Increase the cost of a rival's next advantage by one. |
| 11 | Cool Their Streak | Remove a mini-game victory discount. |
| 12 | Cancel the Favor | Cancel an advantage another player just activated. |
| 13 | Redirect the Question | Change a rival's target. |
| 14 | Scramble the Menu | Replace a rival's available questions. |
| 15 | Muffle the Read | Make a rival's next private observation less precise. |
| 16 | Plant a Red Herring | Add an authored, falsifiable decoy to a rival's private information. |
| 17 | Start a Rumor | Publicly associate a rival with a suspicious theory or suspect. |
| 18 | Challenge Duel | Force a short head-to-head mini-game for priority or information. |
| 19 | Crowd the Witness | Add pressure that makes a public answer more evasive. |
| 20 | Shadow Their Winnings | Gain Leverage when a chosen rival next earns it. |
| 21 | Hold the Evidence | Delay a rival's newly unlocked question until the next window. |
| 22 | Burn the Clock | Shorten a rival's selection time. |
| 23 | Lock the Door | Prevent a rival from selecting one character. |
| 24 | Cross the Wires | Swap the resolution order of two rivals. |
| 25 | Steal the Spotlight | Replace a rival's chosen opening character with your choice. |

## First filter: top 15

The first filter removed ideas that acted as automatic purchases, directly revealed the solution, cancelled turns, punished accessibility needs, caused uncontrolled AI generation, or created obvious rich-get-richer loops.

### Top 15 advantages

| Rank | Advantage | Reason |
|---:|---|---|
| 1 | Deep Read | Expresses the observational detective fantasy directly. |
| 2 | Follow the Thread | Makes character conversations feel responsive and alive. |
| 3 | Compare Notes | Rewards memory and deduction without revealing truth. |
| 4 | Sharpen the Question | Makes evidence strategically useful. |
| 5 | Call the Next Witness | Gives players meaningful control over investigation direction. |
| 6 | Take the Floor | Creates racing tension with little complexity. |
| 7 | Join the Pressure | Turns overlapping theories into social play. |
| 8 | Stay Untouchable | Supplies understandable protection. |
| 9 | Double Down | Adds risk, commitment, and memorable victories. |
| 10 | Accusation Insurance | Makes bold play less punishing. |
| 11 | Choose the Lead | Reinforces player-led investigation. |
| 12 | Second Look | Fits the observation fantasy and reuses prior material. |
| 13 | Pin the Timeline | Helps players organize complicated cases. |
| 14 | Build Rapport | Has strong fictional flavor. |
| 15 | Peek at the File | Creates anticipation without revealing the answer. |

Removed from the advantages at this stage:

- Clear a Name was too close to a truth machine.
- Hold the Floor encouraged turn monopolization.
- Quiet Word weakened the shared TV moment.
- Turn the Tables created excessive reaction chains.
- Bank a Question and One More Question threatened pacing and AI cost.
- Recover a Missed Clue belongs in graceful engine fallback behavior.
- Refresh the Menu felt mechanical rather than dramatic.
- Borrow an Angle weakened private evidence ownership.
- Hot Streak was passive and amplified the leader.

### Top 15 sabotages

| Rank | Sabotage | Reason |
|---:|---|---|
| 1 | Rattle the Witness | Feels natural inside an interrogation scene. |
| 2 | Make Them Wait | Creates race tension without deleting an action. |
| 3 | Close the Angle | Disrupts a plan while preserving alternatives. |
| 4 | Jam the File | Temporarily changes strategy without deleting evidence. |
| 5 | Listen In | Creates an exciting information-theft moment. |
| 6 | Leak the Lead | Turns private investigation into social vulnerability. |
| 7 | Show Their Hand | Creates anticipation and countermoves. |
| 8 | Pick Their Pocket | Makes the Leverage economy tangible. |
| 9 | Raise the Stakes | Pressures the economy without stealing a turn. |
| 10 | Cancel the Favor | Provides direct counterplay, although it risks frustration. |
| 11 | Muffle the Read | Attacks observation without changing truth. |
| 12 | Challenge Duel | Connects the main game to short competitive contests. |
| 13 | Shadow Their Winnings | Encourages prediction about who will perform well. |
| 14 | Hold the Evidence | Delays value without permanently removing it. |
| 15 | Steal the Spotlight | Creates control over staging and tempo. |

Removed from the sabotages at this stage:

- Cut In overlapped with Make Them Wait.
- Redirect the Question and Lock the Door violated player agency.
- Scramble the Menu felt arbitrary.
- Plant a Red Herring threatened the fairness contract.
- Start a Rumor lacked a clear mechanical consequence.
- Crowd the Witness could punish every player hearing the public answer.
- Burn the Clock created accessibility problems.
- Cross the Wires overlapped with sequencing effects.

## Second filter: first top 10

The second filter favored mechanics that create prediction and counterprediction, produce a visible table moment, scale from 2 to 8 players, have a clear recovery path, support multiple strategies, and resolve through deterministic state.

### First top 10 advantages

1. Deep Read
2. Follow the Thread
3. Compare Notes
4. Sharpen the Question
5. Call the Next Witness
6. Take the Floor
7. Join the Pressure
8. Stay Untouchable
9. Accusation Insurance
10. Choose the Lead

The five removed here were Second Look, Pin the Timeline, Build Rapport, Peek at the File, and Double Down. They were redundant, too informationally direct, too passive, or insufficiently connected to sabotage.

### First top 10 sabotages

1. Rattle the Witness
2. Make Them Wait
3. Close the Angle
4. Jam the File
5. Listen In
6. Leak the Lead
7. Show Their Hand
8. Pick Their Pocket
9. Raise the Stakes
10. Challenge Duel

The five removed here were Cancel the Favor, Muffle the Read, Shadow Their Winnings, Hold the Evidence, and Steal the Spotlight. Direct cancellation felt poor because the victim pays an opportunity cost and receives nothing.

## Twenty new ideas inspired by the first top 10

These concepts were generated after the first top 10 and are not renamed entries from the original 50.

### New advantages

| # | Idea | Effect |
|---:|---|---|
| 1 | Contingency Plan | Privately lock a backup target or question that activates if the first plan is disrupted. |
| 2 | Sting Operation | Arm a trap that weakens the next sabotage against you and exposes its source. |
| 3 | Exact Wording | Mark an exact name, time, object, or phrase from a prior answer for later comparison. |
| 4 | Pattern Match | Compare two private observations and learn whether they share an authored behavior pattern. |
| 5 | Stakeout | Predict which character will become important in the next beat and earn a refund if correct. |
| 6 | Theory Wager | Privately stake Leverage on a suspect, motive, or method and earn more if later evidence supports it. |
| 7 | Mutual Favor | Offer another player a jointly funded action with a clearly stated shared payoff. |
| 8 | Counterintelligence | Learn the category and source of the last sabotage used against you. |
| 9 | Last Word | Reserve one interaction until after the other questions in the round resolve. |
| 10 | Second Chair | Invite one player to share a private observation in exchange for one of theirs. |

### New sabotages

| # | Idea | Effect |
|---:|---|---|
| 11 | Loose Lips | After a rival acts, reveal the evidence category or public theory behind the move. |
| 12 | Conditional Trap | Secretly place a trap on a target or question family that triggers only if a rival chooses it. |
| 13 | Delayed Read | Deliver a rival's private observation after one additional interaction resolves. |
| 14 | Favor Debt | The next advantage a rival uses refunds one Leverage to you. |
| 15 | Call Their Bluff | Challenge a public theory and let its owner accept a higher-risk, higher-reward commitment. |
| 16 | Witness Overload | Repeatedly questioning the same character reduces the precision of a rival's later private read. |
| 17 | Heat Transfer | Redirect the next sabotage aimed at you toward a previously marked rival. |
| 18 | Theory Bounty | Reward the first player who produces evidence against a rival's public theory. |
| 19 | Forced Trade | Make a rival choose between revealing an evidence category or paying Leverage. |
| 20 | Pressure Auction | Force a short public Leverage bid over resolution priority. |

## Swap review

| Removed | Replacement | Reason |
|---|---|---|
| Stay Untouchable | Sting Operation | A passive shield stops play. A sting creates prediction, exposure, and a memorable reversal. |
| Accusation Insurance | Theory Wager | Insurance softens failure. A wager encourages bold deductions and stronger emotional stakes. |
| Choose the Lead | Contingency Plan | Call the Next Witness already controls direction. Contingency adds sabotage counterplay. |
| Show Their Hand | Loose Lips | Revealing a move before resolution invites dogpiling. Revealing motivation afterward preserves agency. |
| Challenge Duel | Call Their Bluff | A deduction challenge belongs inside Nightcap's core fantasy more naturally than a reflex mini-game. |

Heat Transfer, Forced Trade, and Theory Bounty are not recommended for the first version because they encourage retaliation chains and table dogpiling. Pressure Auction is also deferred because it can slow every round.

## Final 10 advantages

These form five distinct families.

| Rank | Family | Advantage | Final behavior |
|---:|---|---|---|
| 1 | Insight | Deep Read | Sharpen the next private behavioral observation without identifying truth or lies. |
| 2 | Access | Follow the Thread | Ask one contextual follow-up unlocked by the answer just received. |
| 3 | Insight | Compare Notes | Compare two claims and surface specific shared or conflicting anchors. |
| 4 | Access | Sharpen the Question | Upgrade an evidence-based question to its stronger authored variation. |
| 5 | Tempo | Call the Next Witness | Move an eligible character earlier in the staged sequence. |
| 6 | Tempo | Take the Floor | Resolve the locked interaction next. |
| 7 | Access | Join the Pressure | Join another public question and receive a separate private read. |
| 8 | Counterplay | Sting Operation | Weaken the next sabotage and expose the saboteur. |
| 9 | Risk and reward | Theory Wager | Stake Leverage on a bounded theory and earn a reward if evidence validates it. |
| 10 | Counterplay | Contingency Plan | Lock a backup action that protects agency when disrupted. |

## Final 10 sabotages

These also form five distinct families.

| Rank | Family | Sabotage | Final behavior |
|---:|---|---|---|
| 1 | Witness pressure | Rattle the Witness | Make the character more guarded for one rival interaction while preserving required facts. |
| 2 | Tempo | Make Them Wait | Move one rival interaction later, but never beyond the current round. |
| 3 | Information control | Close the Angle | Close one evidence-based option for a single selection and provide a valid replacement. |
| 4 | Information control | Jam the File | Stop one evidence item from unlocking questions for one selection without hiding or deleting it. |
| 5 | Information control | Listen In | Receive a copy of one rival's private observation. |
| 6 | Information control | Loose Lips | Reveal the evidence category or public theory motivating a completed action. |
| 7 | Economy | Pick Their Pocket | Transfer one Leverage under strict floor, cap, and anti-leader rules. |
| 8 | Economy | Raise the Stakes | Increase the next advantage cost by one, disclosed before commitment. |
| 9 | Mind game | Conditional Trap | Secretly trap an eligible target or question family and trigger a bounded effect if selected. |
| 10 | Mind game | Call Their Bluff | Challenge a public theory, giving its owner a choice between accepting a wager or declining a small tempo advantage. |

## Interaction review

| Combination | Gameplay result |
|---|---|
| Deep Read and Rattle the Witness | The investigator can spend to overcome pressure, creating a readable contest rather than nullification. |
| Follow the Thread and Raise the Stakes | The player decides whether the follow-up is valuable enough to pay the increased cost. |
| Take the Floor and Make Them Wait | Resolution order becomes contested, but no question disappears. |
| Contingency Plan and Close the Angle | A prepared player outplays sabotage through planning. |
| Contingency Plan and Jam the File | A backup path preserves agency and rewards foresight. |
| Sting Operation and Conditional Trap | Both players try to predict the other's timing. |
| Theory Wager and Call Their Bluff | A private deduction can become a dramatic public commitment. |
| Join the Pressure and Listen In | Players can collaborate tactically while risking information leakage. |
| Call the Next Witness and Conditional Trap | Choosing the investigation path also reveals something about the player's theory. |
| Mini-game victory and Pick Their Pocket | Mini-games feed the session economy, but theft limits are essential to prevent runaway leads. |

Potentially dangerous combinations require explicit limits:

- Listen In plus Loose Lips could destroy too much privacy. Limit players to one information-control sabotage per beat.
- Pick Their Pocket plus Raise the Stakes could economically lock someone out. Keep a protected minimum balance or provide a free defensive path.
- Rattle the Witness plus Jam the File could make one action too weak. Only one offensive modifier should affect an interaction.
- Repeated sabotage against one person could create bullying. After being targeted, the player receives temporary protection until another player is targeted or the next interaction window opens.

## Final top five advantages

These five represent five different play styles.

### 1. Deep Read

**Type:** Insight

This is the strongest Nightcap advantage. It realizes the observational detective fantasy: the player notices hesitation, rhythm, word choice, object handling, or a micro-reaction, but must interpret it themselves.

### 2. Follow the Thread

**Type:** Access

This makes interrogation feel like a conversation rather than a fixed questionnaire. The follow-up must be unlocked by the resolved answer and bounded by authored case state. It should be limited to once per player per beat because it creates an additional answer-generation cost.

### 3. Call the Next Witness

**Type:** Tempo

Players already choose whom to investigate. This advantage lets one player pull an eligible target forward at a decisive moment without taking that choice away from anyone else.

### 4. Sting Operation

**Type:** Counterplay

This is better than a simple shield. The player predicts that they may be sabotaged, prepares for it, and creates consequences for the attacker.

### 5. Theory Wager

**Type:** Risk and reward

The player privately stakes Leverage on a bounded theory. Later deterministic evidence validates or rejects the wager, creating a personal investigative story and a delayed payoff.

## Final top five sabotages

### 1. Call Their Bluff

**Type:** Mind game

A player challenges a theory another player has publicly advanced. The challenged player may accept the wager for greater upside or decline and concede a small tempo benefit. It attacks reasoning, not the ability to play, and preserves the truth contract.

### 2. Rattle the Witness

**Type:** Witness pressure

The saboteur introduces fictional pressure before a rival's question. The character becomes more guarded, but still communicates every required factual constraint. It increases drama without inventing false evidence.

### 3. Listen In

**Type:** Information control

The saboteur secretly receives a copy of a rival's private observation. Nothing is deleted or falsified, but the player must now decide how to respond to stolen information.

### 4. Make Them Wait

**Type:** Tempo

The saboteur moves a rival's interaction later in the round. The question still resolves and the player still receives full value, but racing and contradiction timing become meaningful.

### 5. Raise the Stakes

**Type:** Economy

The rival's next advantage costs one additional Leverage, with the added cost visible before commitment. This creates pressure without stealing information or actions.

## Recommended launch structure

Author five advantage families and five sabotage families, but expose only three or four families in an individual session. The arc seed, beat configuration, and authored rules select the session loadout deterministically.

The first Nightcap loadout to playtest is:

**Advantages**

1. Deep Read
2. Follow the Thread
3. Sting Operation

**Sabotages**

1. Call Their Bluff
2. Rattle the Witness
3. Listen In

This gives the first playable set observation, conversational access, defense, social challenge, fictional pressure, and information theft without immediately introducing economic snowballs or complicated turn-order disputes.

## Economy guardrails

Before implementation, the Leverage economy should lock these rules:

- Every player has a protected path to earn Leverage.
- Mini-game victories may award more, but participation should not leave every non-winner permanently empty.
- Use a small bank cap to prevent hoarding.
- Powerful effects cost more or have once-per-beat limits.
- No player receives more than one offensive modifier on a single interaction.
- Recently sabotaged players receive temporary protection from dogpiling.
- Economy attacks cannot reduce a player below a protected floor.
- No effect cancels a question, deletes evidence, changes canonical truth, or creates an unfalsifiable clue.
- The engine resolves effects deterministically before AI generates dramatic presentation.
- Games that do not configure Leverage ignore the capability entirely.

## Future implementation shape

This document does not prescribe final code names. The platform should eventually expose generic concepts such as:

- Resource balance and resource grant
- Resource spend
- Advantage or interaction modifier
- Targeting eligibility
- Deterministic effect resolution
- Public versus private outcome audience
- Counterplay and protection window

Nightcap may map these to Leverage, Deep Read, Rattle the Witness, and related names. Other games should be able to configure different vocabulary and effects without engine changes.

## Acceptance criteria for a future implementation spec

- [ ] Question allowances and Leverage balances are separate state concepts.
- [ ] Leverage grants, spends, caps, floors, and expiry resolve deterministically.
- [ ] A configured advantage or sabotage cannot change canonical case truth or delete evidence.
- [ ] Every sabotage has a documented recovery or counterplay path.
- [ ] Public answers and private observations pass audience-filtering tests.
- [ ] The knowledge graph is checked before any generated character response.
- [ ] Mini-game rewards cannot create an unrecoverable lead.
- [ ] A seeded replay produces the same resource balances and effect outcomes.
- [ ] Games without Leverage configuration remain unaffected.
- [ ] Telemetry records grants, spends, targets, outcomes, counterplay, and player recovery without storing unnecessary private content.

## Risks and unknowns

**Risks**:

- Private-information sabotage could damage trust if players do not understand what was shared.
- Economy theft could create a runaway leader or make a player feel personally targeted.
- Witness pressure could be perceived as a false clue if the presentation is not clearly framed as guarded behavior.
- Too many available effects could overwhelm first-time players.
- Extra follow-up questions could increase generation cost beyond the Couch Race budget.

**Unknowns**:

- Whether Leverage should be visible to all players or only to its owner.
- Whether the saboteur's identity should be revealed immediately, after resolution, or only through counterplay.
- Whether mini-game participation grants a floor amount of Leverage or only winners receive a bonus.
- Whether Leverage should carry between beats or expire after each beat.
- Whether team or cooperative games should disable player-targeted sabotage by configuration.
- Which telemetry signals best predict that sabotage felt exciting rather than frustrating.

## Scope decision

Founder direction approves this recommendation for continued design:

- Separate Leverage from question allowances.
- Keep a five-family catalog on both sides.
- Expose three or four families per session for replay variation.
- Begin Nightcap playtesting with Deep Read, Follow the Thread, Sting Operation, Call Their Bluff, Rattle the Witness, and Listen In.

This approval records design direction only. It does not authorize implementation or override the current Couch Race story bible until a durable product decision and implementation spec are approved.
