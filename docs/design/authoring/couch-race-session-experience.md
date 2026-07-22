# Couch Race — Whole-Session Experience & Gameplay Integration

> Current version: v0.1 DRAFT — the missing connective-tissue design
> Last updated: 2026-07-21
> Status: The holistic gameplay design that ties every Couch Race system
> into one designed night. Created after the founder flagged (2026-07-21)
> that the project had accumulated strong components (narration,
> interrogation) with no whole-session design holding them together.
> This doc is the design authority the per-beat and per-mechanic work
> hangs off. It folds in the competition-model examination
> (`couch-race-competition-model.md`) because scoring is the integrator.
> Canonical path: docs/design/authoring/couch-race-session-experience.md
> Authority: `docs/story-bibles/nightcap-couch-race.md` (the arc);
> `nightcap/couch-race.arc.json` (the shipped beat structure)
> Changes no shipped behaviour; locks no scope. Feeds AW-284, AW-285,
> AW-286, AW-288, AW-289, AW-292 and the paper test.

## Why This Exists

We have been building vertically — deep on Vesper narration (6 wrapper
libraries) and deep on interrogation (design + paper test) — without
ever designing the night as a whole. The result is real components with
no integrated experience. A Couch Race session is a **variety show
across six beats**, not a narration reel with one mechanic. This doc
designs the whole show and names where the systems connect, where they
are thin, and where they are missing.

## Integration Audit (grounded in the code, 2026-07-21)

**What is wired:**

- Six beats exist with tension targets, minigame slots, and interaction
  slots (`nightcap/couch-race.arc.json`).
- Three minigames exist: Crime Scene Smash (Scene), Evidence Locker
  (Twist), Tell Me Something True (not yet beat-bound). Trivia planned
  (AW-289).
- Minigames have an integration hook: `behavioral_outputs` (e.g.
  `final-score`) plus `clue_fallback` (play well → earn a clue; skip →
  reduced clue after 30s, host override). So minigame performance
  **already gates clue delivery** — the plumbing is real.
- Interrogation (AW-282/283): claim ledger, contradiction flagging,
  deterministic catches.
- Scoring (AW-284, planned): arc-configurable deterministic scoring,
  accusation state, first-correct trigger, superlatives (Best
  Interrogator, Lie Detector, Most Confidently Wrong).

**What is THIN (the founder's real worry):**

- **Minigame mechanics are thematically generic.** Crime Scene Smash is
  match-3 (swap gems). It has nothing fictionally to do with
  investigating a murder; it is an arcade skill-gate wearing a
  crime-scene skin. Whether that reads as Mario-Party variety or
  immersion-breaking filler is an unanswered design question — the same
  family as interrogation viability, and it must be answered the same
  way (test the feel).

**What is MISSING:**

- **Unified scoring across systems.** It is unspecified whether a
  minigame `final-score` feeds the race, and how it weighs against
  interrogation catches and accusation accuracy. Without this, the
  night has three disconnected scoreboards, not one race.
- **Beat rhythm / minigame coverage.** Minigames sit in only 2 of 6
  beats. D-079 ("minigames throughout, like Mario Party") wants more;
  AW-288 is meant to expand coverage — but the *rhythm* (which energy in
  which beat, and why) is not designed.
- **The through-line.** Nothing yet guarantees the mystery *drives* the
  night rather than merely framing a sequence of activities.

## The Whole Night As One Experience

The design target is a 20-40 minute variety show whose spine is a
single mystery, alternating energy so it never flatlines. Proposed
rhythm (the felt arc, tension targets from the arc in brackets):

| Beat | Energy | The player's verb | System in focus |
| --- | --- | --- | --- |
| **Pour** [0.35] | Cinematic hush | *Watch, arrive* | Narration (the hook) |
| **Scene** [0.45] | Fast, competitive | *Scramble for evidence* | Minigame → evidence economy |
| **Grill** [0.60] | Focused, social | *Read, ask, catch* | Interrogation |
| **Twist** [0.72] | Jolt, re-sort | *Re-evaluate* | Narration + minigame |
| **Last Call** [0.88] | Urgent, loud | *Commit, accuse* | Scoring + accusation |
| **Truth** [0.35] | Cathartic | *Learn, gloat, replay* | Narration + scoreboard |

The rhythm principle (Mario Party's actual secret): **alternate the
verb.** Never two "focus quietly and read" beats in a row; never two
"mash buttons" beats in a row. Scene (fast) → Grill (focused) → Twist
(jolt) → Last Call (loud) is a good alternation. This is why minigames
belong in Scene and Twist and NOT in Grill (Grill is the focused social
beat — a minigame there would step on interrogation).

## The Three Systems That Must Cohere

### System 1 — The Evidence Economy (how you GET information)

Every path to information, unified:
- **Scene minigame** → performance gates clue quality (existing
  `clue_fallback` hook). Winning earns sharper/private evidence.
- **Private evidence** dealt at the Scene (the asymmetry engine).
- **Interrogation** → suspect answers become claims; catches convert
  private evidence into points.
- **Twist minigame** (Evidence Locker) → second wave, same gating.

Design rule to lock: **minigames are not detours from the mystery; they
are how you _earn your evidence_.** A minigame that awards only points
(not information) is the failure mode. Crime Scene Smash's
`clue_fallback` shows the intended model — make it the standard: every
minigame's primary output is *investigative advantage*, points second.

### System 2 — Scoring & Competition (the integrator)

This is where the competition-model examination
(`couch-race-competition-model.md`) becomes concrete. One race,
multiple contributing systems. Under the recommended **co-opetition**
model, individual score accumulates from:

- **Contradiction catches** (interrogation) — the skill core.
- **Minigame performance** — but converted into *evidence advantage*
  first, so a strong minigame run pays off as better catches, not just
  a parallel point stream (this keeps the systems from being three
  scoreboards).
- **Accusation accuracy + speed** (Last Call) — the decisive points.

The open weighting question (how much each contributes, whether a
dominant player runs away) is exactly the competition-model open
question, now scoped to the whole night. **Recommendation:** minigames
feed evidence (not direct points), catches score moderately, accusation
accuracy dominates — so the mystery, not the arcade, decides the night.

### System 3 — Rhythm & Pacing (the variety)

- Alternate the verb every beat (table above).
- Minigame coverage: Scene + Twist confirmed; TMST (AW-288) and Trivia
  (AW-289) should slot where they *raise* energy without breaking the
  Grill's focus — candidate homes: a Pour warm-up (social ice-breaker,
  TMST) and a Last Call pressure game (Trivia as a speed round). This
  gives ~4 minigame touchpoints across 6 beats — the "Mario Party
  throughout" feel — without a minigame inside the interrogation beat.
- The pacing engine (stall thresholds already in the arc) covers dead
  air; this doc covers *designed* energy, which is different.

## The Thematic-Integration Question (the founder's worry, made a decision)

Match-3 as a crime-scene game is the test case. Two philosophies:

- **A — Abstract minigames, thematic skins (current).** Generic
  addictive mechanics (match-3, memory, reflex) skinned per case. Cheap,
  proven-fun, infinitely reusable; risk: immersion-breaking, "why am I
  playing Bejeweled at a murder."
- **B — Diegetic minigames.** The mechanic *is* an investigative act
  (reconstruct the timeline, match fingerprints, sort testimony). More
  immersive; more expensive to author; harder to make reliably fun.

**Recommendation:** B where cheap and clearly better (Evidence Locker
and TMST lean diegetic already), A tolerated where a proven arcade loop
carries a low-stakes energy beat — but every minigame must pass the
**evidence-economy rule** (its output is investigative advantage). A
match-3 that earns you a real clue is defensible; a match-3 that earns
only points is not. This is the concrete design bar. Decide in the
whole-session paper test.

## What The Whole-Session Paper Test Must Now Validate

The interrogation paper test is widened (see
`interrogation-paper-test.md`) to a **full-night** test:

- Does the *rhythm* work — does alternating verb keep energy up, or do
  minigames feel like interruptions?
- Does a minigame feel like *earning evidence* or like a detour?
- Does one unified race read clearly, or do players lose track of why
  they're winning?
- Does the mystery drive the night, or just bookend it?

## Rehearsal 1 Is The Whole-Session Test (founder, 2026-07-21)

Rehearsal 1's explicit purpose is validating the **integrated night** —
breadth across all six beats, all minigame touchpoints, unified
scoring, and the rhythm — not any single mechanic. The observation
guide and AW-286 slice are reframed to test the whole experience. A
rehearsal that only proves interrogation works would be a false pass.

## Open Decisions For The Founder

1. **Evidence-economy rule** — lock "every minigame's primary output is
   investigative advantage, points second"? (Recommended yes.)
2. **Scoring weighting** — minigames→evidence, catches moderate,
   accusation dominant? (Recommended yes — keeps the mystery decisive.)
3. **Thematic philosophy** — B-where-cheap + A-with-the-evidence-rule?
4. **Minigame homes** — TMST → Pour warm-up, Trivia → Last Call speed
   round (giving 4/6 beats a minigame touchpoint)? This is AW-288's
   beat-coverage decision; this doc recommends the placement.
5. Confirm Rehearsal 1 as the whole-session test (reframes AW-286 +
   the observation guide).
