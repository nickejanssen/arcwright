# Interrogation Paper Test — Protocol

> Current version: v0.1 DRAFT — ready to run
> Last updated: 2026-07-21
> Status: The concrete de-risk the interrogation memo recommended and
> the founder approved (2026-07-21). A ~30-minute table test, no engine,
> that resolves the single highest-risk untested assumption in the
> product — is AI-suspect interrogation actually fun — and validates the
> held design questions (competition model, G1 menus, G2 quoting, G4
> conflict) before any engineering spend.
> Canonical path: docs/design/authoring/interrogation-paper-test.md
> Inputs: `couch-race-competition-model.md`, `interrogation-experience-review.md`,
> `line-libraries/seance-1928.md`, `line-libraries/liar-texture-samples.md`
> Not a milestone reinstatement: M0 (Wizard-of-Oz) stays overridden. This
> is one narrow, one-evening use of the technique on one assumption.

## What This Tests (and what it does not)

**Tests:** whether asking-and-catching AI suspects is enjoyable; which
competition model (A/B) feels right; whether strategy verbs (G1) beat
data queries; whether quoting suspects to each other (G2) is the payoff
we think; whether room-conflict verbs (G4) add or distract.

**Does NOT test:** audiovisual quality (paper can't — that is the
separate hard gate, D-090, tested in Rehearsal 1), generated-case
variety, or the full six-beat arc. Keep scope to the Grill loop.

## Setup (10 minutes, one-time)

- **Facilitator** = 1 person, plays Vesper + all suspects, reading from
  scripts. Ideally the founder (you feel the loop fastest by running it).
- **Players** = 2 to 4 on a couch.
- **Materials:** printed suspect sheets (below), two printed intent
  menus per player (a "strategy" menu and a "query" menu — see G1 test),
  private evidence cards, a token bowl (poker chips), a scorepad.
- **Case:** use the authored control case from `liar-texture-samples.md`
  — Dr. Lowell (killer, poisoned the second glass, **smooth** liar) and
  Edith Harrow (innocent, **brittle**, hiding a pawned brooch), plus two
  more suspects the facilitator improvises lightly. The killer and the
  authorized lies are fixed on the sheet before play — never decided in
  the room (mirrors deterministic resolution).

## The Suspect Sheet (facilitator-only, per suspect)

Each sheet states, fixed in advance:
- What the suspect knows (their knowledge state).
- What they will lie about, and the exact lie (authorized falsehood).
- Their lie texture: **smooth** (answers clean; catchable only by
  cross-reference), **brittle** (holds, then cracks on a second press),
  **leaky** (over-explains, visibly uncomfortable).
- The one piece of evidence that falsifies each lie.

The facilitator answers strictly from the sheet — never invents facts a
suspect wouldn't know. This is the human standing in for the
knowledge-graph constraint.

## Private Evidence (the competitive engine)

Deal each player 1-2 private evidence cards at the start (the "Beat 2
asymmetry"). Example cards for the control case:
- "You saw Lowell's gloves on the hall table — still buttoned."
- "The decanter's stopper is missing; a crystal stopper sits in the
  conservatory that doesn't match it."
- "Edith left the music room at 10:50; you saw her return at 11:20."

A player may only **flag a contradiction** they can back with a held
card or a prior recorded answer. Flagging without backing = false flag =
lose a token. This is the whole competitive spine — test whether it
bites.

## The Loop (run 2-3 suspects, ~15 minutes)

Per suspect on the "stage":
1. Facilitator reads a Vesper stinger (from `seance-1928.md`, e.g.
   st-d-2 or st-de-6) to introduce them.
2. Players spend tokens to ask. **Run each competition model for at
   least one suspect** (see below).
3. Facilitator answers from the sheet, aloud, to the whole room.
4. Any player may flag a contradiction (backed). Facilitator confirms or
   penalises. Confirmed catch = points; Vesper reads a squirm line.
5. Record what happened against the measurements below.

## The Four Experiments (this is the point)

Run these deliberately and note reactions:

**E1 — G1 menu: strategy vs query.** Suspect 1: hand players the
**query** menu ("Where were you at 11?", "What was your relationship to
the victim?"). Suspect 2: hand the **strategy** menu ("Let them ramble",
"Rattle them", "Press the timeline", "Quote someone at them"). Ask the
room which was more fun and why. *Measures G1.*

**E2 — Competition model.** For one suspect, score it as **co-opetition**
(everyone hears answers, individual catches score). Ask: did the catch
feel earned by the catcher, or communal? Did private cards make players
feel they were racing? *Measures Model A vs B.*

**E3 — G2 quoting.** Give one player the option "Tell Suspect B what
Suspect A said." Facilitator makes Suspect B react per their sheet
(deny, fluster, or contradict). Ask the room: was that the best moment?
*Measures G2 — the candidate killer mechanic.*

**E4 — G4 conflict verbs.** Give players "Follow that up" (piggyback the
current asker) and "I don't buy it" (challenge the asker's read).
Watch: does the couch argue more? Is it fun or chaotic? *Measures G4.*

## Measurements (the scorepad's real job)

For each experiment, the facilitator notes:
- **Lean-in moments:** when did the whole room physically engage?
- **Best moment of the night:** unprompted — what do players cite?
- **Boredom moments:** when did someone check out or reach for a phone?
- **The catch feeling:** when a contradiction was caught, was it a spike
  or a shrug?
- **Talk vs heads-down:** did players argue with each other, or silently
  work menus?
- **"Again?":** at the end, do they want another suspect / case?

## Decision Outputs (what the evening resolves)

Feed directly back into the held decisions:
- **Competition model** → confirm Model A or revise (`couch-race-competition-model.md`).
- **G1** → strategy vs query vs hybrid, decided on real reactions.
- **G2** → greenlight the build (AW-292) or defer.
- **G4** → design now or defer.
- **The viability verdict** → if the catch consistently spikes on paper,
  the mechanic is sound and the remaining risk is purely presentation
  (D-090 hard gate). If the catch shrugs even on paper, stop and
  redesign before building anything.

## Why This Is High-Leverage

Discovering "asking is boring" or "co-opetition doesn't race" during
Rehearsal 1 costs a rehearsal and real engineering. Discovering it here
costs one evening and a printer. This is the cheapest possible test of
the most expensive possible mistake.

## Founder Checklist To Run It

1. Print: 4 suspect sheets, 2 intent menus × player count, ~8 evidence
   cards, this protocol.
2. Grab a bowl of chips (tokens) and a notepad.
3. 2-4 friends, one evening.
4. Run E1-E4, take notes against the measurements.
5. Bring the notes back — they resolve the held questions and update
   this doc's decision outputs.
