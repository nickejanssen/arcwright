# Nightcap — Current Design State

## Promise

**A cinematic competitive murder mystery where everyone gets to be the detective.**

## Player Fantasy

**Be the smartest, strangest detective in the room: observe, deduce, manipulate, compete, and prove your case.**

## Core Loop

**WATCH → HUNT → THINK → PLAY → REACT**  
Repeat until **LAST CALL → CASE FILE → THE TRUTH → THE VERDICT → THE POSTMORTEM**.

## Arcwright Runtime Contract

Nightcap is an authored arc on Arcwright. Arcwright deterministically resolves authored state, character knowledge, and audience-targeted events; generative models express that resolved state rather than deciding the canonical murder.

A per-character knowledge graph supports interrogation, the unified character model allows human-controlled and AI-driven roles to use the same underlying object, and surface-agnostic events support public/private delivery without Nightcap inventing separate engine paths. The Nightcap GDD still owns what those primitives mean as investigation, competition, story, proof, and endgame play.

## World, Host & Content

Nightcap cases live inside a legible **social-gathering** frame even as era, occasion, location, and wrapper vary. **Vesper** remains the specialist Host authority through `docs/design/the-host.md`; `docs/design/nightcap-art-direction.md` remains the specialist visual authority. Both are subordinate to the GDD on gameplay, truth, fairness, and current product structure.

Nightcap can be irreverent, strange, suspenseful, and darkly funny while taking the murder seriously. Graphic gore, sexual content, real-person targeting, identity-based hate/slurs, harmful content involving minors, and player-directed psychological horror remain outside the content territory. The old fully-generative-everything rule is superseded by the current hybrid-content, deterministic-state-first model.

## Investigation & Deduction

V1 investigation is authored and bounded but **diegetic-first**. Players pursue concrete people, places, objects, claims, behaviors, and irregularities while the game keeps the rails mostly invisible.

A meaningful action may simply reveal fair information. The game presents observations; **the player owns the implication**.

THINK is continuous rather than a recurring quiz. Player-generated hypotheses may feed bounded verification, comparison, confrontation, or challenge actions.

## Evidence Economy

Fairness means viable routes to the truth, not identical information or equal outcomes. Everyone must have a legitimate opportunity to win; Nightcap should not add catch-up help or protective guardrails merely because someone is investigating poorly. Losing through your own reasoning and choices is part of the game.

- **Equal solvability, unequal information.**
- **Redundant truth, nonredundant experience.**
- **Knowledge ≠ Proof.** Nightcap automatically tracks which proof each player legitimately owns; ownership visibility cannot become relevance guidance.
- The fiction may lie; the game must play fair.

## Case Board & Memory

Memory retrieves what the player legitimately encountered. The optional Case Board supports the player's own model of the case.

Objective factual organization is allowed; meaningful deductive relationships remain player-owned. Baseline transcript, attribution, and review are DECIDED. Advanced provenance/re-entry/search/filter remain TESTING.

## Minigames

Minigames are the competitive pulse. Major beats must reconnect to murder-facing state, are **opportunity-first**, and emerge through story-triggered competitive windows.

They create big tactical swings with short half-lives and cannot substitute for legitimate murder proof. A temporary privilege may expire while information legitimately learned through it remains known; the short half-life applies to the advantage mechanism, not to player memory.

## Espionage

Leverage manipulates the information race through **information + opportunity**, not generic PvP damage. Players can also gain ordinary investigative leverage simply by finding or understanding useful information first; not every advantage needs to become a formal resource. Minigames may grant Leverage or temporary advantages, but they must not become the primary gateway to espionage or let repeated wins dominate the whole investigation. Exact Leverage sourcing remains **TESTING**, and player-facing bookkeeping should stay minimal. Bluffing, red herrings, lies, and fair deception are part of the mystery vocabulary.

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
**The Postmortem** turns actual, observable player behavior into truthful, exaggerated social comedy. It may use theories or changes in thinking only when the player externalized them through an interaction the game could actually observe.

After every final theory locks, Nightcap first reveals **only each player's accused culprit** for the social commitment moment. It then runs **Truth → Verdict → Postmortem**. Players do not present speeches or argue their cases to the room.

## Player Count

Two-player support is mandatory and first-class. Two players receive the same core Nightcap fantasy with a tighter, more directly adversarial social geometry; the full core loop remains meaningful.

Four players remains the best-understood reference configuration. V1 upper bound remains OPEN.

## Difficulty / Accessibility / Onboarding

Nightcap separates Case Challenge, Investigation Pressure, and Accessibility.

Accessibility is lean and mostly invisible: remove avoidable barriers while preserving the same mystery, reasoning ownership, proof requirements, competitive meaning, story quality, humor, and fun.

## Arcwright Case Graph

Nightcap cases are authored internally as traversable graph/state structures. Players begin from the same baseline state but may investigate along different connected routes. Arcwright tracks canonical truth, investigation opportunities, and each character's legitimately learned knowledge separately enough to support deterministic Structured Reconstruction and authoring analytics.

The graph is hidden from players. It is an authoring, fairness, telemetry, and Arcwright-platform capability. Candidate diagnostics include path depth, branching, alternate solution routes, bottlenecks, dead ends, route overlap, and actual player traversal.

## Current Validation State

Paper Test #2 has not yet passed the representative Time-to-Fun / Cohesion baseline.

The external GitHub Pages harness, Jotform survey, and telemetry/handoff infrastructure are built separately from the GDD. v2.2 is the active test direction.

Memory Support remains blocked until Gate 1 passes.

## Approximate Status

- Foundational GDD definition: **~90%**.
- End-to-end design + validation plan: **~80%**.

These planning estimates are intentionally unchanged. The integration architecture is materially clearer, but major empirical validation remains unfinished.
