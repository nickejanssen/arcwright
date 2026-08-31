# Nightcap — Arcwright Runtime Boundary

**Status:** Foundational integration direction DECIDED; implementation details follow Arcwright architecture  
**Type:** Authoritative GDD/platform-boundary one-pager

## Purpose

Nightcap is **one authored arc definition on the Arcwright narrative runtime**.

This page prevents two opposite failures:

1. rebuilding Arcwright capabilities as Nightcap-specific systems, and
2. allowing platform implementation details to silently decide Nightcap's game design.

Arcwright provides narrative-runtime primitives. Nightcap's GDD defines how those primitives become a fair, competitive murder-mystery experience.

## Runtime Contract

For Nightcap, Arcwright resolves authored arc state **deterministically before generative expression**. Fairness-critical mystery truth is resolved by the authored state model; a language or content model may express that state, but it does not get to invent a different culprit, retroactively alter what happened, or change proof truth because a generated line would be more dramatic.

Arcwright provides the following shared primitives described by the creator:

- a **per-character knowledge graph** queried before generation,
- a **unified character model** in which human-controlled and AI-driven roles are the same underlying kind of object,
- **surface-agnostic content events** that carry their own audience targeting,
- deterministic resolution of authored arc state followed by generative expression of that resolved state.

## What This Means in Nightcap

### Interrogation

Interrogation is the character knowledge graph made visible as gameplay. What a suspect can truthfully know, falsely believe, conceal, misunderstand, or express must remain consistent with resolved case state and that character's knowledge.

The Nightcap investigation system still owns **what the player can choose to pursue, how those choices are bounded, and how much inference remains player-owned**. Arcwright supplies the state and character knowledge underneath it.

### Public answers and private tells

A public response and a private tell do not require separate narrative systems. They are content events with different audience targeting over the same resolved state.

The Nightcap GDD owns when unequal/private information is fair and interesting. Arcwright owns the delivery primitive.

### Fresh-but-fair cases

Fresh presentation can come from generative expression while fairness-critical truth, evidence relationships, knowledge state, proof eligibility, and resolved consequences remain deterministic.

> **Deterministic resolution wearing generative dressing.**

Generation may make a case feel alive; it may not move the goalposts.

### AI-driven suspects

Whether a suspect is AI-driven rather than human-controlled is a field/configuration of the unified character model, not a separate engine architecture. Nightcap should not duplicate core character logic merely because one role is controlled by a model.

## Ownership Boundary

### Arcwright runtime owns

- resolved arc/runtime state,
- character knowledge state and knowledge-graph queries,
- common character representation,
- audience-targeted content-event delivery,
- presentation-independent event primitives,
- invoking generative expression after state resolution.

### Nightcap arc + GDD own

- canonical murder truth and fair-play constraints,
- case-specific authored structure,
- legitimate evidence/proof architecture,
- what investigation choices mean as gameplay,
- competitive opportunities and consequences,
- deterministic solve conditions, tie-breaking, and victory,
- player-count and difficulty rules,
- Nightcap-specific pacing, comedy, suspense, and social experience.

### Existing Nightcap system pages own player-facing behavior

- `02-investigation-deduction.md` — what players investigate and how reasoning remains theirs,
- `03-case-board-memory.md` — memory/reasoning-support boundary,
- `04-minigame-competitive-pulse.md` — competition,
- `05-last-call-case-file.md` — Last Call and Structured Reconstruction,
- `06-story-reactivity-reentry.md` — consequences and re-entry,
- `07-espionage-leverage-update.md` — information warfare,
- `08-truth-verdict-postmortem.md` — closing experience,
- `09-player-count-scaling.md` — social/player-count adaptation,
- `10-difficulty-accessibility.md` — challenge/accessibility constraints.

## Internal Investigation Graph / Case Topology

Nightcap's investigation has a **hidden authored graph topology** that Arcwright should be able to track and analyze.

This is **not player-facing UI**. Players experience people, places, conversations, objects, records, events, opportunities, and consequences — not a node map that tells them how the mystery works.

Conceptually:

- all players in the same Case Challenge begin from the same authored baseline/root state,
- investigation choices move them through different connected opportunities and knowledge states,
- different branches may expose different facts, claims, contradictions, private tells, or proof routes,
- multiple routes can eventually establish the essential truths needed to solve the case,
- players may take inefficient routes, follow red herrings, revisit earlier material, miss useful branches, or fail to reach the solution.

The semantic requirement is a **graph/state model**, not a mandate to use a particular storage technology. Arcwright may implement it with a graph database, adjacency structures, event/state projections, or another architecture that preserves the same topology.

This is **not a neural-network requirement**. Mystery truth, reachability, and fairness should remain explicit and inspectable rather than learned or probabilistically inferred.

## Three Related Graph Views

Arcwright should distinguish at least conceptually between:

1. **Canonical case/solution graph** — authored truth and causal relationships that define what happened and what essential truths constitute a solve.
2. **Investigation opportunity graph** — discoverable routes, prerequisites, branches, interactions, and alternate paths by which truths or useful misleading information may be encountered.
3. **Per-character knowledge state/graph** — the subset of facts, claims, observations, and events that a specific player/character has legitimately learned at a given moment.

These views may share implementation primitives, but they serve different purposes. A player's knowledge graph must never be treated as proof that the player personally inferred the correct implication.

## Structured Reconstruction Integration

At Last Call, Structured Reconstruction uses this architecture directly:

- the player selects a culprit and assembles a short causal theory from concepts they legitimately know,
- Arcwright verifies the submitted structure against the authored solution graph and accepted equivalent routes,
- generative presentation may turn the resolved structure into natural dialogue or a cinematic proclamation,
- the model does not grade prose, invent missing logical steps, or decide the winner.

## Authoring & Complexity Analytics

Arcwright should eventually expose case-authoring diagnostics derived from the graph so Nightcap creators can understand complexity before and after playtesting.

Useful candidate measures include:

- node and edge counts,
- branching factor,
- depth from shared start state to essential truths,
- shortest and representative valid solution-path lengths,
- number of independent routes to each essential truth,
- bottlenecks / single points of failure,
- dead ends or low-value branches,
- route overlap and path diversity,
- clue/fact centrality or over-reliance,
- where players branch, backtrack, stall, or converge,
- which nodes are frequently skipped or disproportionately decisive,
- actual player traversal compared with authored expected routes.

The exact metric set and thresholds are **TESTING**. These diagnostics inform authors and researchers; they do not automatically change the case, secretly help a struggling player, or surface a solution path to players.

This capability may also become an Arcwright platform feature beyond Nightcap: authored narrative experiences can be inspected as traversable state/knowledge graphs rather than treated as opaque generated text.

## Opening / WATCH Ownership

The opening scene and its initial observations are authored **arc events/state**, expressed through Arcwright's event and targeting primitives. Nightcap does not need a second standalone WATCH engine.

The case/arc definition determines what opening state exists and who can receive which initial event. The Investigation GDD owns how players subsequently pursue people, places, objects, claims, and irregularities. Story Reactivity owns how meaningful actions change the world afterward.

This is deliberately a boundary clarification rather than a new gameplay subsystem.

## Fairness Boundary

No generative expression may contradict fairness-critical resolved state. In particular, presentation must not silently change:

- the culprit,
- canonical event history,
- what a character could know,
- whether evidence is authentic/forged/mistaken as authored,
- proof ownership,
- required proof relationships,
- already-resolved competitive consequences.

If a generative surface cannot preserve those invariants reliably, use more constrained authored expression rather than weakening Nightcap's mystery contract.
