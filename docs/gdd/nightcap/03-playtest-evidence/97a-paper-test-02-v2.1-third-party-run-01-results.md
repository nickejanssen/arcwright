# Nightcap — Paper Test #2 v2.1 Third-Party Run 01 Results

**Status:** TEST FINDING / supporting evidence, not canon  
**Gate:** REVISE AND RERUN

## Run Metadata

- **Fixture:** The Room With No Door
- **Protocol:** Paper Test #2 v2.1 game-first baseline
- **Participant:** 1 third-party participant
- **Environment:** chat-based interactive exploratory gate
- **Multiplayer/social validation:** not tested
- **Timing caution:** chat timing is exploratory only

## Observed Telemetry

- First meaningful choice: **47s**
- Investigation path: **Bookcase → Fox cufflink → Service corridor → Celia statement 1 → Mae statement 1**
- Information retained: Bookcase; Fox cufflink; Service corridor; Celia statement 1; Mae statement 1
- Post-interruption commitment interval: **80s**

The participant used all five actions and sampled physical investigation, movement investigation, and interviews rather than remaining inside one branch.

## In-Game Commitment

- Prime suspect: **Mae**
- Wanted to pursue next: **More movement/timeline investigation**
- Most useful discovery: **Service corridor**

## Player Report

- Fun: **2/5**
- Detective feeling: **2/5**
- Wanted to continue: **Maybe**
- Action clarity: **Mostly confusing**
- Most interesting/fun: no qualitative response supplied
- Boring/confusing/interface-like: no qualitative response supplied
- Over-signposted: no qualitative response supplied
- Wanted but unavailable: no qualitative response supplied
- Memory difficulty: no qualitative response supplied
- Single biggest improvement: no qualitative response supplied

## Evidence Classification

### OBSERVATION

- The participant used the full five-action budget.
- They explored more than one investigation family.
- They ended without strong enough confidence to establish a well-supported causal case in the available slice.
- Re-entry/commitment after the interruption took 80 seconds in this chat execution.

### PLAYER REPORT

- The slice was low-fun (2/5).
- It produced weak detective identification (2/5).
- Desire to continue was only "Maybe."
- Action clarity was only "Mostly confusing."

### DESIGN INFERENCE

- Increasing the action budget from three to five and exposing interviews immediately was **not sufficient** to pass the Time-to-Fun gate.
- The participant's varied action path means the failure cannot be reduced to "not enough options" alone.
- The current prototype representation still does not reliably convert investigation choices into a strong detective fantasy.
- Because qualitative answers were left blank, this run does **not establish why** the participant found the experience low-fun or confusing.
- The result does **not establish that Nightcap's intended core game is unfun**. The prototype still omits major established Nightcap pillars including cinematic presentation, multiplayer rivalry, information warfare, minigames, Leverage, social bluffing, and story reactivity.

### RECOMMENDATION

Do not proceed to Memory Support A/B testing yet.

Do not keep tuning only action count, labels, or clue formatting. The next baseline should test a more representative **game-first micro-loop** in which discoveries create an immediate playable consequence: a contradiction opportunity, suspect response, tactical choice, or other visible state change.

Keep the test small, but stop reducing Nightcap to a menu of evidence cards. The baseline must first demonstrate that the investigation loop itself creates a satisfying moment of play.

## Gate Decision

**REVISE AND RERUN.**

The v2.1 baseline fails its stated gate:

- investigative feeling was below **Mostly**;
- desire to continue was not clearly positive;
- no naturally reported detective peak was captured;
- action clarity remained weak.

No GDD decision is changed by this run.
