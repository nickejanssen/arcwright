# Nightcap — Investigation & Deduction

**Status:** Foundational direction DECIDED; implementation details TESTING  
**Type:** GDD system one-pager

## Purpose

Make players feel like detectives because **they choose what to pursue and they decide what it means**.

Nightcap uses strong invisible authorship: the case is securely bounded and solvable, but the surface should preserve high perceived autonomy.

## Investigation Law

V1 investigation is authored and bounded, but should be **diegetic-first**.

Players should normally pursue concrete things in the fiction — people, places, objects, claims, behaviors, irregularities, records, routes — rather than feel like they are selecting abstract database categories.

Underlying structure may remain visible where needed for clarity, accessibility, navigation, or re-entry, but it should recede behind the fiction whenever practical. Players should have a clear, legible way to see **what people, places, objects, or areas are available to explore**. Entering one of those spaces should still feel like investigation rather than choosing from a conveyor belt of prescribed buttons. The interface can explain what is available; it must not rank significance, identify the right lead, or explain what an observation means.

## Bounded-Open Agency

Within an authored investigation state, players should **ordinarily retain multiple meaningful investigative possibilities** rather than be marched through a single designer-prescribed chain.

Possible actions may include people, places, objects, claims, records, evidence-unlocked follow-ups, or other case-specific opportunities. Prior discoveries and competitive events may open, alter, delay, or close possibilities, but the ordinary investigative middle should not routinely collapse to one meaningful remaining action merely because the player declined an earlier lead.

Last Call is the deliberate convergence point. Before then, the case graph should support genuine path choice while preserving deterministic solvability.

This is not an unlimited simulation requirement. Nightcap optimizes for **freedom of reasoning, not unlimited freedom of input**.

## Meaningful Investigation

A valid investigation action may simply reveal fair, relevant information.

It does **not** need to manufacture a world-state consequence merely to justify itself.

The important distinction is:

> **The game presents observations. The player owns their implications.**

A lead must not collapse into an interface that automatically explains why the discovered information matters.

## Rich Observation, Minimal Interpretation

Evidence presentation should be rich enough to investigate without becoming an answer key.

Prefer:

- concrete sensory or situational details;
- specific statements and behavior;
- discoverable objects, records, places, times, and relationships;
- enough narrative texture for players to notice patterns themselves.

Avoid automatically translating those observations into conclusions such as *suspicious*, *important*, *this contradicts the alibi*, *this proves opportunity*, or equivalent designer inference unless the player has explicitly performed a game action that establishes that relationship.

A useful authoring rule is:

> **Give players a better crime scene, not a better answer key.**

## Scene First, Fact Second

The player should normally experience an important discovery as something they **saw, heard, found, compared, or uncovered**. Arcwright may record structured factual atoms underneath the presentation for knowledge state, provenance, solvability, and deterministic resolution.

Player-facing prose is presentation. Canonical state should never depend on parsing generated prose back into truth.

## Progressive Contextual Teaching

Nightcap teaches the game without teaching the deduction.

When a mechanic first matters, explain in plain contextual language:

- what the player can do;
- what the mechanic/resource represents;
- what success, failure, spending, or commitment changes;
- whether information is private/shared when relevant; and
- what state or opportunity changed afterward.

Do **not** use onboarding to explain:

- why a discovered clue matters;
- which suspect the player should pursue;
- which comparison is important;
- what conclusion they should reach; or
- whether their emerging theory is correct.

This resolves the apparent tension between "more onboarding" and "less hand-holding": explain **affordances and consequences**, not **evidence meaning**.

## Autonomy

Players choose their own investigative path within authored possibilities. The game should avoid unnecessary hand-holding, significance ranking, or designer-authored conclusions.

Paper Test #2 v2.2 strengthened this direction: positive moments clustered around choosing actions, choosing clues, multiple options, and autonomy, while the strongest negative signal was the prototype supplying conclusions instead of letting players investigate. This is high-confidence within the small exploratory sample, not population-level validation.

## THINK

Deduction is continuous rather than a mandatory recurring quiz.

Selected moments may give players intentional opportunities to:

- organize information,
- compare claims,
- connect evidence,
- challenge a statement,
- act on a theory.

Avoid routine essay prompts or forced explanations of reasoning during play.

## Acting on Hypotheses

Player-generated hypotheses may feed **bounded authored actions** where supported by the case, such as:

- verification,
- comparison,
- confrontation,
- challenge,
- targeted follow-up.

This lets deduction affect play without requiring unrestricted free-form simulation in V1.

## Evidence & Fairness

Existing Nightcap laws remain:

- **Equal solvability, unequal information.**
- **Redundant truth, nonredundant experience.**
- **Knowledge ≠ Proof.**
- Big proof dimensions are known early.
- No correctness confirmation before final commitment.

## TESTING

- exact investigation-action budgets;
- exact balance between diegetic presentation and visible structure;
- alpha-player / quarterbacking countermeasures;
- how often hypothesis-driven actions should appear;
- action clarity under high perceived autonomy;
- how many simultaneous meaningful options feel legible rather than overwhelming;
- runtime and pacing.

## Design Checks

For an investigation action, ask:

> **Did the player choose to pursue this, did they discover something fair, and did the game leave the meaningful inference to them?**

For a player-facing clue, ask:

> **Am I showing what happened, or am I quietly telling the player what to think about it?**