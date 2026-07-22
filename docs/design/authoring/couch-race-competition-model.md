# Couch Race Competition Model — Design Examination

> Current version: v0.1 DRAFT — examination, NO model locked
> Last updated: 2026-07-21
> Status: The "examine further" deliverable the founder requested when
> the interrogation interview (2026-07-21) surfaced a load-bearing
> question: with a shared TV and public suspect answers, where does
> player-vs-player competition actually come from? This doc lays out the
> options and their full gameplay consequences so the model can be
> chosen — and then validated in the paper test — rather than assumed.
> Canonical path: docs/design/authoring/couch-race-competition-model.md
> Authority: `docs/story-bibles/nightcap-couch-race.md` §6-7 (the shipped
> interrogation design); `docs/design/authoring/interrogation-experience-review.md`
> Nothing here changes shipped behaviour or locks scope.

## The Problem Statement (founder, 2026-07-21)

"Everyone is competing against each other... this can't be the only way
to find clues. There's no strategic edge or competition when everyone
has the same options. If everyone has the same menu and hears the same
answer, how do people play against each other? It's confusing."

The confusion is correct and important: **the interrogation menu is not
the competitive layer.** Making question intents richer (G1) does not,
by itself, create competition. This doc separates the two layers and
examines what competition model Couch Race should actually use.

## CORRECTION (2026-07-21, D-094): Leverage is the primary PvP layer

This doc's original version omitted the single most important
competitive system: **Nightcap Leverage** (AW-287, ADR-0015) — an earned
resource spent on **advantages** (help yourself) and **sabotages**
(interfere with a rival). Earned through minigames and accomplishments.
The "where is the player-vs-player edge?" question this doc opens is
**primarily answered by Leverage sabotages**, not only by private
evidence + race-to-flag. The correct framing: **co-opetition
(investigate together, score individually) with competitive TEETH
supplied by the Leverage advantage/sabotage economy.** Everything below
still holds, but read it as the *secondary* asymmetry layer on top of
Leverage. See `couch-race-systems-map.md` §5.

## What Already Creates Asymmetry (grounded in the bible, not invented)

`nightcap-couch-race.md` §6-7 already contains competitive structure:

1. **Divergent menus.** Each player's intent menu is baseline intents
   **plus intents unlocked by the private evidence that player holds**
   (§6). Menus are not identical.
2. **Private evidence.** Beat 2: "every player leaves the scene knowing
   something the couch does not."
3. **Private tells.** The asker alone receives a follow-up hook (§6,
   "the asymmetry economy").
4. **Scarce tokens.** Questions are limited per beat; opportunity cost
   is the strategy.
5. **The catch is the scoring event, not the ask.** A player flags a
   contradiction when an answer conflicts with a prior claim **or with
   evidence that player holds** (§6-7). First correct flag scores; a
   false flag is penalised.

**Consequence:** a *public* answer is still a competitive moment,
because only the player holding the contradicting private evidence can
safely catch it. The same sentence is a score for one player and a trap
for another. Competition = converting private information into catches
faster than rivals, on scarce tokens. The shared answer is raw
material; private holdings + speed + timing are the edge.

## The Three Models

### Model A — Co-opetition (shared investigation, individual scoring)

Players investigate together on a shared stage (public answers, open
argument) but score individually; the winner is whoever caught the most
/ accused correctly first. Pub-quiz / Jackbox social contract.

- **Information flow:** mostly public (the show is shared), with private
  evidence/tells as the individual edge.
- **Scoring:** individual — contradiction catches, accusation accuracy,
  accusation speed.
- **Turn structure:** public interrogation on the stage; private
  flag/accusation lock-in on phones.
- **G1 resolves as:** strategy verbs are fine being shared — they enrich
  the shared show; the race is who converts information into catches,
  not who has secret menus.
- **G3 (asking as performance):** strong fit — public credit fuels
  friendly rivalry without breaking warmth.
- **G4/G5 (the room):** natural home — the couch is *meant* to argue;
  "follow that up" / "I don't buy it" are pro-social conflict.
- **Pros:** protects couch warmth (the moat); two-player floor holds;
  lowest onboarding friction; the shared answer becomes a feature.
  Most addictive social loop; most differentiated.
- **Cons:** a dominant player can lead the room; "solved out loud" can
  let laggards coast (mitigate via private-evidence gating of the
  decisive catches and accusation-accuracy scoring).

### Model B — Stronger PvP (hidden tracks)

Lean into concealment: more private interrogation, less public
answering, so players genuinely race in parallel.

- **Information flow:** heavily private; the stage shrinks.
- **Scoring:** individual, zero-sum-ish.
- **Turn structure:** parallel private questioning; less shared TV.
- **G1 resolves as:** menus must diverge more to create edge; strategy
  verbs alone still don't differentiate players.
- **G3/G4/G5:** weak fit — a hidden game gives the room little to watch
  or argue about together.
- **Pros:** sharper individual competition; higher skill ceiling.
- **Cons:** breaks the "watch the TV together" magic that is the
  product's differentiator; raises onboarding friction; strains the
  two-player floor; fights D-070's shared-stage cinematics.

### Model C — Tunable dial (casual ↔ cutthroat)

A session-start dial between A and B.

- **Pros:** flexibility; serves different groups.
- **Cons:** two models to design, build, and tune; untuned dials ship
  confusing; the platform's own principle warns against speculative
  dials without a spec. Almost certainly post-Rehearsal-1 if ever.

## Recommendation (advisory — the paper test decides)

**Model A (co-opetition).** It aligns with every stated founder priority
— immersive, addictive, differentiated, easy-to-onboard, two-player
floor — and it *resolves the founder's confusion*: shared answers and
shared strategy verbs are correct because the competition lives in the
private-information → race-to-catch layer, not in the menu. It also fits
the already-shipped design (public stage + private evidence/tells +
race-to-flag) with the least change. B trades the product's actual moat
(couch warmth) for a sharper competition most couch hits deliberately
avoid. C is a post-launch luxury.

## What The Paper Test Must Measure To Decide

The competition model is cheap to test on paper (see
`interrogation-paper-test.md`). The test should measure, under Model A:

1. Does a public catch by one player feel *earned by them*, or does the
   room feel it was communal? (If communal-but-still-fun → A confirmed.)
2. Does private evidence create enough individual edge that players feel
   they're racing, not just co-oping? (If no → strengthen private-clue
   weighting, not abandon A.)
3. Do players talk to each other more, or heads-down on phones? (Talking
   = the warmth is real = A is working.)
4. Does a dominant player flatten others? (If yes → accusation-accuracy
   + private-catch scoring must carry more weight.)

## How This Gates The Interrogation Gaps

- **G1 (strategy verbs):** HELD until the model is chosen, then validated
  in the paper test (both a strategy menu and a query menu, under Model
  A). Per founder, 2026-07-21.
- **G2 (quote suspects):** prove in the paper test, then build — its
  value is highest under A (a public "catch" everyone witnesses).
- **G3 (asking as performance):** adopt under A (staging credit).
- **G4 (productive conflict):** prototype conflict verbs in the paper
  test; strongest under A.
- **G5 (room reasons to watch):** adopt now under any model (staging).

## Open Questions For The Founder (post-paper)

1. Confirm Model A, or pick B/C after seeing paper results.
2. Under A: how much scoring weight goes to catches vs accusation
   accuracy vs speed? (Determines whether a dominant player can run away
   with it.)
3. Does the winner need to be *sole* (one winner) or ranked (everyone
   placed)? Ranked softens PvP toward the co-op end.
