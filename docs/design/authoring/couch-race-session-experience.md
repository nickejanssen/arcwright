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

## Product North Star (founder, 2026-07-21) — D-093

Couch Race is defined by three reference points, in priority order:

1. **A striking, premium murder-mystery STORY is the spine.** The story
   is the differentiator and the load-bearing element — deep, authored,
   world-class. Everything else serves it. This is what nobody else has.
2. **Mario Party minigames drive engagement, variety, and rhythm.**
   They are *swappable* modules, not story-critical. They may be
   thematically loose ("charm and personality") because they are not
   the point — the story is. Swappability is the safety valve: any
   minigame that isn't working is replaced, and nothing breaks.
3. **Jackbox Murder Mystery Trivia Party is the personality/format
   inspiration — but we go deeper.** Jackbox's accessibility, party
   energy, and trivia/minigame format are the template; its
   *lightweight, vanilla, simple* feel is explicitly what we reject. Our
   edge over Jackbox is depth, premium presentation (D-090), and a real
   story spine. "Jackbox, but not shallow."

**The load-bearing consequence — minigames give edge, not gates.**
Because minigames are swappable and the story is the spine, the mystery
must be **fully solvable without winning any minigame.** A minigame
result is an *accelerator or advantage* (a sharper clue, a head start,
bonus points), never the only path to a piece of core evidence. The
existing `clue_fallback` (you always get the clue; playing well gets a
better variant) is exactly this model — make it the universal rule.

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

**On thematic fit (reframed by the North Star, D-093):**

- Crime Scene Smash is a **time-bound "smash the most" competitive
  race** (its match-3 board is the vehicle for the smash race). That is
  a legitimate Mario-Party engagement minigame — competitive frenzy
  skinned to the crime scene. Under the North Star this is *fine*:
  minigames may be thematically loose ("charm and personality"), because
  the story is the spine and minigames are swappable. The earlier worry
  ("match-3 has nothing to do with murder") over-weighted thematic
  purity; the real bars are (a) is it *fun* and (b) does it obey the
  edge-not-gate rule. Thematic fit is a nice-to-have, tested by feel,
  and any miss is fixed by swapping the game — not by blocking the
  night.

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

Design rule (D-093, edge-not-gate): **a minigame result is an
_accelerator or advantage_ toward the investigation — a sharper clue, a
head start, bonus points — never the only path to core evidence.** The
mystery is fully solvable without winning any minigame (that is what
makes minigames swappable). Crime Scene Smash's `clue_fallback` is the
model: you always get the clue; playing well gets a better variant.
A minigame may also simply drive engagement/points (Mario-Party role)
without gating evidence at all — both are allowed; what is NOT allowed
is a *required* clue locked behind minigame success.

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

## The Thematic-Integration Question — RESOLVED by the North Star (D-093)

Earlier this was framed as abstract-vs-diegetic minigames. The North
Star resolves it: **story is the spine; minigames are swappable
engagement drivers that may be thematically loose.** So both styles are
allowed, and the deciding bars are, in order:

1. **Is it fun?** (Mario-Party-grade engagement.) Non-negotiable.
2. **Does it obey edge-not-gate?** (No required clue locked behind it.)
3. Thematic fit — a nice-to-have that adds charm, not a requirement.

Diegetic minigames (Evidence Locker, TMST lean this way) are *preferred*
where they are also fun, because they add immersion for free. Abstract
ones (Crime Scene Smash) are welcome where they carry an energy beat.
Any minigame that fails bar 1 or 2 is **swapped**, not patched — that is
the whole point of the swappable-module architecture. This is the
concrete standard; feel is confirmed in the paper test / Rehearsal 1.

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

1. ~~Evidence-economy rule~~ **RESOLVED (D-093): edge-not-gate.** A
   minigame gives advantage, never a required-clue gate; the mystery is
   solvable without any minigame; minigames may also just drive
   engagement/points.
2. **Scoring weighting** — still open. Recommendation: minigames feed
   edge/engagement, interrogation catches score moderately, accusation
   accuracy dominates — so the *story/mystery* decides the night, not
   the arcade. Confirm the ordering, and whether minigame points count
   directly toward the race at all or only as investigative edge.
3. ~~Thematic philosophy~~ **RESOLVED (D-093): story-spine + swappable
   loose-theme minigames + Jackbox-but-deeper.** Bars: fun, then
   edge-not-gate, then thematic fit as charm.
4. **Minigame homes / rhythm** — still open. Recommendation: TMST → a
   Pour/Scene social warm-up, Trivia → a Last Call speed round, giving
   ~4/6 beats a touchpoint. This is AW-288's beat-coverage decision.
5. ~~Rehearsal 1 as the whole-session test~~ **RESOLVED (D-092).**
6. **NEW — the "Jackbox but deeper" bar.** What concretely makes us
   *not* lightweight/vanilla? Candidates: story depth, premium
   audiovisual (D-090), knowledge-state suspects, real stakes/scoring.
   Worth an explicit differentiation statement (recommend it lands in
   the story bible's Strategic Role section on the next bible pass).
