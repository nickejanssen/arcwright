# Nightcap — Full-GDD Adversarial / Cohesion Pass 02

**Status:** SUPPORTING DESIGN-CONTROL RECORD — not game canon by itself  
**Checkpoint:** 05 / Session B

## Purpose

Preserve the material findings from the full-authoritative-GDD audit and their current resolution state without turning audit commentary into canon.

Authoritative changes live in `00-decision-ledger.md` and the relevant system pages.

## Resolved / Reframed During This Pass

### Minigame wins compounding into Espionage control

**Finding:** Leverage was a major Espionage input while earlier wording made minigames its primary source, creating a snowball risk and making PLAY more strategically central than intended.

**Resolution:** The primary-source rule was reopened. Natural information advantage does not have to become formal Leverage. Minigames may still create Leverage or temporary advantage, but exact sourcing is **TESTING** and repeated minigame wins may not become the main gateway to Espionage.

### Last Call fairness ambiguity

**Finding:** “Fair solvability” could be misread as requiring the game to make sure each player personally assembled a viable case.

**Resolution:** Fairness means the case architecture gave every player a legitimate opportunity to win from a fair starting point. It does not guarantee correct investigation, corrective opportunities, equal Case Files, or protection from losing.

### Postmortem claiming unobserved thinking

**Finding:** The Postmortem referenced abandoned theories even though Nightcap deliberately does not require players to externalize all reasoning.

**Resolution:** Postmortem may characterize only behavior/thinking actually externalized or objectively observed by the game. It may exaggerate truthfully; it may not invent an internal belief.

### Group Rescue wording contradiction

**Finding:** The ledger said rescue “does not affect the winner” while the accessibility page correctly said it does not change winner calculation. Shared new evidence can naturally change an eventual outcome.

**Resolution:** Rescue applies no winner-specific bonus, penalty, or alternate victory calculation. Because it changes shared case state, it may naturally affect who ultimately wins.

### WATCH / opening runtime ownership

**Finding:** WATCH was a first-class loop beat but lacked a clear authoritative owner.

**Resolution:** `11-arcwright-runtime-boundary.md` now clarifies that Nightcap is an authored arc on Arcwright. Opening state/events are authored arc state delivered through Arcwright primitives; Investigation owns player-facing pursuit and Story Reactivity owns downstream consequence/re-entry. No second WATCH gameplay engine is added.

### Case File reveal timing

**Finding:** Case Files locked privately, but the GDD did not specify when accusations became public.

**Resolution:** After simultaneous lock, reveal only each player's accused culprit. Then run The Truth → The Verdict → The Postmortem. Supporting proof/case quality stays private until selectively surfaced by The Verdict. Players do not give case presentations.

### Proof admissibility as hidden player bookkeeping

**Finding:** Knowledge ≠ Proof is strategically useful but could force players to remember which evidence they legally own.

**Resolution:** Nightcap automatically tracks factual proof ownership/admissibility. It may show what a player legitimately owns but may not tell them whether that evidence is relevant or persuasive.

### Social-play ownership scattered across pages

**Finding:** Social play spans Investigation, Minigames, Story Reactivity, Espionage, Player Count, Accessibility, Case File, and Postmortem. Creating another canonical system risks duplicate rules, while leaving it scattered makes holistic balance review difficult.

**Resolution:** `98c-social-play-cohesion-view.md` consolidates the social layer as a supporting audit view. Canonical rules remain with their existing owners.

## Resolved / Reframed in Decisions 9–12

### Temporary advantage versus permanent knowledge

**Resolution:** “Big swings, short half-life” applies to mechanical privilege such as temporary access, priority, protection, or timing advantage. Legitimate information learned through that privilege remains learned; Nightcap does not pretend players forget information when the privilege expires.

### Last Call pressure versus interface speed

**Resolution:** Last Call pressures commitment and decision-making, not typing or menu dexterity. The final Case File remains concise and structured, and the hard countdown must provide enough time to operate that interface without making interface speed a competitive skill.

### Concentrated targeting / dogpiling

**Resolution:** Nightcap does not automatically intervene merely because multiple opponents choose to target the same player. Concentrated targeting, retaliation, and temporary coalitions are valid social strategy. Ordinary rules apply equally to everyone. Intervention is warranted only if testing exposes a repeatable mechanic that materially prevents a player from continuing to participate in the investigation; fix that mechanic rather than granting pity immunity or hidden catch-up.

### Clear navigation with open investigation

**Resolution:** Nightcap should make the available investigative space legible — who, where, and what can currently be explored — without turning the experience into a checklist of prescribed actions. The interface clarifies possibilities; the player still chooses how to explore, what to pursue, and what the resulting observations mean.

## Remaining Material Cohesion Questions

- Whether memory/re-entry/accessibility wording should be consolidated further to reduce future drift without changing behavior.
- Exact Structured Reconstruction interaction grammar and acceptable complexity.
- Whether the cinematic confrontation/proclamation augmentation materially improves payoff after the core endgame is validated.
- Exact Spotlight distribution/calibration at larger player counts.
- V1 upper player-count bound remains OPEN.

## Resolved / Reframed in Decisions 13–17

### Truth / Verdict explanation burden

**Finding:** The earlier "strongest Case File" and numerical Case Strength direction risked making the winner feel subjective and forcing Nightcap to justify why one argument beat another.

**Resolution:** V1 uses deterministic **Structured Reconstruction**. Players choose the culprit and construct a short causal theory from legitimately learned concepts. The authored solution graph defines the essential truths. A generative model may express the result but may not grade persuasion or decide the winner. Numerical Case Strength is removed from winner determination.

If one player solves the murder, that player wins. If several solve it, use the established competitive tie-break direction. If nobody solves it, no player receives a fabricated murder victory; the murderer/case beats the table.

**PARKED fallback:** Culprit + Decisive Facts if Structured Reconstruction is too fiddly.  
**PARKED augmentation:** cinematic detective proclamation/confrontation after deterministic resolution.  
**PARKED:** witness/interview contradiction mechanics unless testing indicates interviews need improvement.

### Spotlight definition

**Resolution:** Spotlight is deliberately managed public story attention, particularly at larger player counts. Its job is to preserve ensemble visibility and room-level involvement, not to equalize evidence, difficulty, outcomes, or chances to win. Exact distribution remains TESTING.

### Rare auctions

**Resolution:** PARKED. Remove from active V1 testing until a concrete gameplay problem or case gives the mechanic a purpose.

### Hidden case topology / Arcwright analytics

**Resolution:** Arcwright should represent Nightcap cases with explicit graph/state semantics: shared baseline start, branching investigation routes, canonical solution relationships, and per-character knowledge state. The graph stays hidden from players. Arcwright should be able to measure authored complexity and actual traversal, including path depth, branching, alternate routes, bottlenecks, dead ends, overlap, and player movement through the case. This is a platform/authoring/analytics capability, not a player-facing hint system.

## Evidence Boundary

None of the unresolved items above becomes a new Nightcap law from this audit alone. Creator decisions and representative gameplay evidence remain required where they would materially change player experience.
