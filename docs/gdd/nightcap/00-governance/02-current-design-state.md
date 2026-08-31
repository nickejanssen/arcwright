# Nightcap — Current Design State

## Promise

**A cinematic competitive murder mystery where everyone gets to be the detective.**

## Player Fantasy

**Be the smartest, strangest detective in the room: observe, deduce, manipulate, compete, and prove your case.**

## Core Loop

**WATCH → HUNT → THINK → PLAY → REACT**  
Repeat until **LAST CALL → CASE FILE → THE TRUTH → THE VERDICT → THE POSTMORTEM**.

## Arcwright Runtime Contract

Nightcap is an authored arc on Arcwright. Arcwright deterministically resolves authored state, character knowledge, investigation opportunity topology, and audience-targeted events; generative models express that resolved state rather than deciding the canonical murder.

A per-character knowledge graph supports interrogation and the factual notebook, the unified character model allows human-controlled and AI-driven roles to use the same underlying object, and surface-agnostic events support public/private delivery without Nightcap inventing separate engine paths. The Nightcap GDD owns what those primitives mean as investigation, competition, story, proof, and endgame play.

The hidden case graph separates at least three concepts clearly enough for deterministic play and analysis:

1. canonical case/solution relationships;
2. investigation opportunities and routes; and
3. per-character/player knowledge and proof state.

The graph is not exposed to players as an answer map.

## World, Host & Content

Nightcap cases live inside a legible **social-gathering** frame even as era, occasion, location, and wrapper vary. **Vesper** remains the specialist Host authority through `docs/design/the-host.md`; `docs/design/nightcap-art-direction.md` remains the specialist visual authority. Both are subordinate to the GDD on gameplay, truth, fairness, and current product structure.

Nightcap can be irreverent, strange, suspenseful, and darkly funny while taking the murder seriously. Graphic gore, sexual content, real-person targeting, identity-based hate/slurs, harmful content involving minors, and player-directed psychological horror remain outside the content territory. The old fully-generative-everything rule is superseded by the current hybrid-content, deterministic-state-first model.

Player-facing prose should be specific, human, context-aware, and consistent. Internal system terminology does not automatically belong on screen.

Arcwright should use high-confidence, high-quality, appropriately licensed open-source writing/editorial skills when useful, while keeping Arcwright's GDD, graph/state, fairness rules, and founder-approved intent authoritative. Current strong references include `danjdewhurst/story-skills`, `forjd/better-writing`, and `Calliope-Editor/writing-skills`.

## Investigation & Deduction

V1 investigation is authored and bounded but **diegetic-first**. Players pursue concrete people, places, objects, claims, behaviors, and irregularities while the game keeps the rails mostly invisible.

Within the investigative middle, players should ordinarily retain **multiple meaningful possibilities** rather than be forced down a single remaining lead. Last Call is the intentional convergence point.

A meaningful action may simply reveal fair information. The game presents observations; **the player owns the implication**.

Important evidence should normally be **scene first, fact second**: something the player actually saw, heard, found, compared, or uncovered, with structured facts recorded underneath for deterministic state.

THINK is continuous rather than a recurring quiz. Player-generated hypotheses may feed bounded verification, comparison, confrontation, or challenge actions.

## Onboarding Boundary

Nightcap uses progressive contextual teaching.

Explain:

- what the player can do;
- what a mechanic/resource represents;
- what success/failure/spending changes;
- who owns information when relevant; and
- what state or opportunity changed.

Do **not** explain:

- why a clue matters;
- which suspect is important;
- which comparison should be made; or
- what conclusion the player should reach.

## Evidence Economy

Fairness means viable routes to the truth, not identical information or equal outcomes. Everyone must have a legitimate opportunity to win; Nightcap should not add catch-up help or protective guardrails merely because someone is investigating poorly. Losing through your own reasoning and choices is part of the game.

- **Equal solvability, unequal information.**
- **Redundant truth, nonredundant experience.**
- **Knowledge ≠ Proof.** Nightcap automatically tracks which proof each player legitimately owns; ownership visibility cannot become relevance guidance.
- The fiction may lie; the game must play fair.

## Detective Notebook, Case Board & Memory

The private detective notebook remembers objective player-specific state: suspects, claims, factual observations, objects/locations/times, evidence/proof state, and replayable case-critical information. Living suspect cards accumulate only what that player legitimately learns. Players may add short private notes.

Memory retrieves what the player legitimately encountered. The optional Case Board supports the player's own model of the case.

Objective factual organization is allowed; meaningful deductive relationships remain player-owned. Advanced provenance/re-entry/search/filter remain TESTING.

## Minigames

Minigames are the competitive pulse. Major beats must reconnect to murder-facing state, are **opportunity-first**, and emerge through story-triggered competitive windows.

A major minigame should feel like an investigative action occurring in the fiction rather than an unexplained generic mode. First-use framing should make clear what players are doing, what is contested, and what the result changes afterward without interpreting the clue.

They create big tactical swings with short half-lives and cannot substitute for legitimate murder proof. A temporary privilege may expire while information legitimately learned through it remains known.

## Rivalry & Espionage

Rival detectives should feel active throughout the case without exposing their private theories. Players may see that rivals investigated, reached opportunities, earned/spent resources, or changed shared state while private notebooks and final reasoning stay private.

Leverage manipulates the information race through **information + opportunity**, not generic PvP damage. It may change access, priority, timing, ordering, or visibility, but cannot change truth, erase learned facts, delete every route to required proof, or let a model decide competitive resolution.

Exact Leverage sourcing remains **TESTING**, and player-facing bookkeeping should stay minimal.

## Story Reactivity

REACT is a cross-cutting response layer, not a standalone mode.

Reactions are **naturalistic but legible**, may create real tactical consequences, and can be shared/private/hybrid. Re-entry surfaces **state, not inference**.

## Last Call & Case File — Structured Reconstruction

Last Call uses authored dramatic timing constrained by minimum fair solvability. The threshold asks whether the case offered a legitimate opportunity to solve it, not whether every player personally found the right evidence or built a strong answer.

V1 uses **Structured Reconstruction**: each player chooses the culprit and builds a short causal theory from case concepts legitimately available in their character state. Arcwright validates that structure deterministically against the authored solution graph and accepted equivalent routes. No model grades persuasive writing, and no numerical Case Strength chooses the winner.

One solver wins. Multiple solvers tie on the murder and proceed to the established competitive tie-break direction. If nobody solves it, the murderer/case beats the table and no player receives a fabricated murder victory.

The simpler **Culprit + Decisive Facts** interaction is PARKED as a fallback if Structured Reconstruction proves too fiddly. A cinematic detective-style confrontation/proclamation is PARKED as a presentation augmentation after deterministic resolution.

## Endgame

**The Truth** provides evidence-led narrative catharsis.  
**The Verdict** confirms the deterministic result and surfaces only the decisive factual difference when explanation is needed.  
**The Postmortem** turns actual, observable player behavior into truthful, exaggerated social comedy.

After every final theory locks, Nightcap first reveals **only each player's accused culprit** for the social commitment moment. It then runs **Truth → Verdict → Postmortem**. Players do not present speeches or argue their cases to the room.

## Player Count

Two-player support is mandatory and first-class. Two players receive the same core Nightcap fantasy with a tighter, more directly adversarial social geometry; the full core loop remains meaningful.

Four players remains the best-understood reference configuration. V1 upper bound remains OPEN.

## Difficulty / Accessibility

Nightcap separates Case Challenge, Investigation Pressure, and Accessibility.

Accessibility is lean and mostly invisible: remove avoidable barriers while preserving the same mystery, reasoning ownership, proof requirements, competitive meaning, story quality, humor, and fun.

## Current Validation State

Paper Test #2 v2.2 is **complete as diagnostic evidence and did not pass the representative Time-to-Fun / Cohesion gate**.

Dataset: N=3 survey submissions, all Fun = 3/5, Detective Feeling = 2/5, 2/5, and 3/5; replay intent = one Yes and two Maybe, with one Maybe reading qualitatively like a soft No. Telemetry was inconsistent and cannot support robust pacing/path conclusions.

Strongest within-sample findings:

- detective agency was too low;
- the fixture too often supplied conclusions instead of evidence;
- system terminology/copy hurt comprehension and immersion;
- replay pull was too weak.

The evidence strengthened rather than reversed the core GDD direction. It drove explicit revisions around bounded-open agency, rich raw observation, progressive contextual onboarding, factual notebook/living suspect cards, rival legibility, story-wrapped minigame context, and player-facing terminology.

The next representative test should use a **brand-new non-canon case** built from this revised GDD. Do not patch or reuse *The Last Toast* as the next validation case.

Formal Memory Support comparison remains a later validation question, but the factual notebook / living-suspect-card baseline is now DECIDED; future memory testing asks how much additional support helps before it starts doing the reasoning.

## Approximate Status

- Foundational GDD definition: **~93%**.
- End-to-end design + validation plan: **~85%**.

These remain planning estimates, not development progress. Major empirical validation is still unfinished.