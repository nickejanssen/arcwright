# Nightcap — Difficulty + Accessibility Adversarial Pass #1

**Status:** TEST EVIDENCE / DESIGN REVIEW, not canon by itself

## Result

**PASS WITH CONSTRAINTS.**

The Difficulty + Accessibility architecture is internally coherent, but implementation can still undermine deduction, pacing, competition, or product simplicity.

## Attacks and Findings

### Cognitive support becomes reasoning assistance
**Risk:** Retrieval/search/organization quietly identifies what matters.  
**Constraint:** Support may retrieve, remember, review, organize, and compare discovered information. It may not rank significance, identify an undiscovered contradiction, recommend the correct action, or infer conclusions.  
**Status:** TESTING at UX level.

### Accessibility degrades cinematic quality
**Risk:** Alternate presentation becomes a stripped-down lesser version.  
**Constraint:** Preserve authored scenes and adapt access around them.  
**Status:** Boundary DECIDED.

### Individual accommodations create individual difficulty levels
**Risk:** Selected players receive easier mystery or competition.  
**Constraint:** Simplify/redesign the mechanic before making it easier for one player than another.  
**Status:** Boundary DECIDED.

### Accessible minigames become homogeneous
**Risk:** Universal accommodation requirements flatten variety.  
**Constraint:** Filter to room-compatible minigames rather than require every minigame to support every configuration.  
**Status:** TESTING; library breadth must be validated.

### Minigame filtering reveals private accessibility needs
**Risk:** Repeated absence of a mechanic exposes why the room was filtered.  
**Constraint:** Player settings remain private; surface neutral room compatibility only.  
**Status:** TESTING.

### Rescue becomes optimal easy mode
**Risk:** Free rescue is routinely invoked to reduce ambiguity.  
**Constraint:** Player-proposed, unanimous, shared, authored, non-inferential, recorded. No winner penalty.  
**Status:** Exact frequency/amount/presentation TESTING.

### Readiness gates become pacing sludge
**Risk:** Frequent room confirmation destroys momentum.  
**Constraint:** Information persists; gates are selective and reserved for important transitions.  
**Status:** TESTING.

### Two-player scaling becomes two-player easy mode
**Risk:** Structural scaling accidentally lowers intellectual challenge.  
**Constraint:** Preserve selected Case Challenge; scale opportunity architecture rather than presumed player capability.  
**Status:** TESTING.

### Broad skill expression fails to preserve mixed-skill competition
**Risk:** One strong deductive player dominates despite multiple systems.  
**Constraint:** No hidden rubber-banding; validate whether observation, investigation choices, bluffing, espionage, minigames, and Leverage create legitimate counterplay.  
**Status:** Requires real mixed-skill playtesting.

### Difficulty configuration violates time-to-fun
**Risk:** Sophisticated architecture creates pre-game configuration overhead.  
**Constraint:** Recommended one-tap setup; deeper configuration remains optional.  
**Status:** Prototype UX validation required.

## Primary Validation Questions

1. Can first-time players start investigating without understanding the difficulty architecture?
2. Does baseline memory support reduce friction without performing deduction?
3. Does room-compatible minigame filtering retain enough variety and skill expression?
4. Do selective readiness gates protect comprehension without slowing the room?
5. Is group rescue rare and genuinely restorative rather than optimal play?
6. Can the same Case Challenge remain fair and comparably demanding at two and four players through opportunity scaling alone?
7. Do mixed-skill groups remain competitively engaged without loser bonuses?
8. Do accessibility-equivalent presentations preserve the same useful information without adding inference?

## Evidence Rule

Conceptual survival of this adversarial pass is not empirical proof. These questions require paper tests, Wizard-of-Oz testing, prototype testing, and accessibility review before implementation details are hardened.
