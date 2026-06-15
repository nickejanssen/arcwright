# Daily Case Story Bible

> Current version: v0.1
> Last updated: 2026-06-14
> Status: Current
> Canonical path: docs/story-bibles/daily-case.md

**Working label only:** "Daily Case" is a planning label, not a committed product name.

---

## Purpose

Daily Case is the canonical second-arc target for M5-C and post-M6 executable follow-through. It is a solo, five-minutes-a-day interrogation game in which one player questions one AI suspect across a week-long case, contradictions accumulate, and the week ends in a final accusation.

This experience exists to prove Arcwright's platform reuse through execution, not just schema design. It validates the cross-session narrative-state wedge from D-034 on the smallest viable product surface.

---

## Strategic Role

Daily Case closes three named capability gaps left open by Nightcap and Monster RPG:

- asynchronous play
- very short sessions under ten minutes
- solo adaptive experience

It is the real version of the M5 second-arc deliverable described in D-056. Instead of proving reuse by document alone, Arcwright proves reuse by shipping a second executable arc that stresses knowledge provenance and cross-session memory harder than Nightcap does.

---

## Player Promise

- One suspect, one device, one short session per day.
- The suspect remembers prior questioning and prior claims.
- Contradictions do not disappear. They accumulate into evidence.
- The player can return daily without coordinating a group.
- The final accusation feels earned by memory and pattern recognition, not by random twist delivery.

---

## Experience Shape

### Core loop

Each day the player opens the case, receives a short recap or re-entry frame, and conducts a focused interrogation of a single suspect. The session should fit inside roughly five minutes.

The daily loop is:

1. Re-ground the player in the current case state.
2. Let the player ask a bounded number of questions or take a bounded number of interrogation actions.
3. Update the suspect's claim history, contradiction ledger, and player-facing evidence state.
4. End on a small reveal, tension increase, or tomorrow-hook.

### Case length

- Default structure: one week, seven calendar days.
- Days 1 through 6 are interrogation days.
- Day 7 ends in accusation and resolution.

The exact authored beat names may change later, but the week-long cadence and final accusation are part of the core shape.

---

## Arc Design Principles

### Human-authored spine

The case structure, daily unlock order, truth state, and accusation outcomes are human-authored. AI does not decide who is guilty, what canonically happened, or whether a contradiction is real. AI expresses the suspect within authored constraints and resolved state.

### Knowledge graph first

The suspect's memory must be grounded in structured knowledge state, claim history, and provenance-aware contradiction tracking. The product should make it obvious that the system remembers what was asked, what was answered, and how later statements relate to earlier ones.

### Solo adaptive pacing

The product adapts to one player's progress, confusion, and question choices without introducing multiplayer or host-management assumptions.

### Smallest viable surface

Daily Case should prove the platform on the cheapest possible experience layer:

- one player
- one suspect
- one primary surface
- text-first interrogation flow
- no Nightcap-style shared display or party coordination

---

## Deterministic And Generative Boundaries

### Deterministic

- case truth and accusation answer
- daily unlock cadence
- which evidence or follow-up topics become available
- contradiction detection rules
- end-of-day and end-of-case state transitions

### Generative

- suspect dialogue wording
- evasions, tone, and deception texture within allowed bounds
- recap phrasing
- optional flavor text for tension and atmosphere

Daily Case must not ask the model to decide canonical state. Contradictions may be surfaced by model output, but they become product state only after deterministic validation.

---

## State Model

The case must preserve state across days. At minimum, the experience needs:

- suspect claim history by day
- player question history or normalized interrogation actions
- contradiction ledger with provenance back to earlier claims
- player-facing evidence and accusation confidence state
- daily completion state and final accusation outcome

The implementation may use a long-lived case container, linked daily sessions, or another approved platform-clean structure. The product requirement is behavioral: day N must remember day N-1 and earlier with no silent resets.

---

## Knowledge And Contradiction Model

Daily Case is a provenance-driven deception product.

- The suspect should remember what they have claimed before.
- The player should be able to uncover contradictions across days.
- Contradictions should preserve references to earlier claims, not just binary flags.
- The system should distinguish between new information, repeated claims, reframed claims, and conflicts.

This design showcases why Arcwright's knowledge graph matters. A pure prompt competitor can bluff continuity for a turn or two. Daily Case should make structured memory visible over a full week.

---

## Surface And Delivery Assumptions

- Primary mode: solo, asynchronous, one-device interaction.
- Delivery can be web-based or another lightweight surface, but the engine must remain surface-agnostic.
- No multi-surface routing is required for the minimum executable product.

The absence of multi-surface complexity is a feature, not a gap. Daily Case is meant to isolate persistence, provenance, and cheap-model consistency.

---

## Telemetry And Cost Priorities

The executable product should preserve the platform's telemetry and cost discipline while staying lightweight.

Priority signals include:

- day-to-day return rate through day 7
- accusation completion rate
- contradiction discovery or usage signals
- per-day session duration
- per-case model cost and cost consistency

Cheap-model consistency is part of the product test. Daily Case should stress whether lower-cost model routing can sustain believable long-memory suspect behavior when state grounding is strong.

---

## Out Of Scope For The Minimal Executable Product

- multiplayer or shared-display support
- real-time competitive mechanics
- Nightcap continuity reuse
- art-heavy or asset-heavy presentation
- social comparison features such as leaderboards or share cards
- final product naming and brand work
- monetization design beyond basic cost awareness

These may become later product work, but they are not required to prove the second arc.

---

## Roadmap Relationship

- M5-C owns the schema and design definition.
- AW-235 defines the Daily Case schema, capability coverage, and platform implications.
- AW-245 builds the minimal executable product only after AW-244 records the Nightcap H1 proof decision.

Daily Case is not Nightcap v1 scope, not Nightcap v1.1 scope, and not a reason to pull cross-session features into current Nightcap tasks.

