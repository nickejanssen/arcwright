# Nightcap — Difficulty + Accessibility Validation Plan

**Status:** TEST PLAN / supporting evidence, not canon  
**Purpose:** Validate the lean Difficulty + Accessibility architecture before hardening implementation details.

## Test Philosophy

Do not test whether Nightcap can accumulate accessibility features.

Test whether it can remain:
- easy to start,
- easy to operate,
- fair,
- competitive,
- cinematic,
- cognitively manageable,
- and intellectually demanding in the intended ways.

Use the cheapest credible test first. Conceptual simulation is not empirical playtest evidence.

## Test 1 — Time-to-Fun / Progressive Onboarding

### Question
Can first-time players begin meaningful detective play without understanding Nightcap's underlying difficulty architecture or receiving a rules dump?

### Prototype
Paper/Wizard-of-Oz opening using a recommended first-case structure.

Expose only the next needed action. Introduce later systems contextually.

### Observe
- time from join/start to first meaningful investigative choice,
- questions about rules before first fun moment,
- moments where facilitator explanation is required,
- whether players understand the basic win condition by the time it matters,
- whether new mechanics interrupt momentum when introduced.

### Failure signals
- players need substantial pre-game explanation,
- early decisions feel fake because players do not understand consequences,
- contextual teaching feels like repeated tutorial popups,
- players describe setup/learning rather than investigation as the opening experience.

## Test 2 — Memory Support vs. Auto-Solving

### Question
Do baseline transcript/attribution/review tools reduce avoidable memory burden without performing deduction?

### Prototype
Run the same short mystery slice with two information-support treatments:

A. basic evidence/history only,  
B. approved baseline memory support.

Do not include advanced search/filter/provenance automation unless separately tested.

### Observe
- repeated factual questions,
- mistaken speaker attribution,
- time spent recovering old information,
- number/quality of player-generated connections,
- whether players treat the interface as suggesting significance,
- re-entry time after a cinematic/minigame interruption.

### Success condition
Support reduces operating friction while player reasoning remains visibly human-owned.

## Test 3 — Same Challenge at 2 vs. 4 Players

### Question
Can a case preserve the same intellectual Case Challenge at two and four players by scaling opportunity architecture rather than making the two-player mystery easier?

### Prototype
Use one authored case slice with the same truth, ambiguity target, and reasoning target.

Adjust only approved player-count-sensitive opportunity variables such as investigation opportunities, evidence delivery/redundancy, and Spotlight load.

### Observe
- evidence coverage before Last Call,
- number of meaningful investigative choices per player,
- dead time,
- private-information value,
- theory diversity,
- proof completeness,
- perceived challenge,
- whether the two-player version feels like a real competitive duel rather than a reduced mode.

### Failure signals
- two players require easier clues rather than structural scaling,
- two-player investigation becomes deterministic,
- four-player information volume creates a fundamentally different intellectual task,
- one configuration cannot reach fair proof coverage without breaking the intended Case Challenge.

## Test 4 — Mixed-Skill Competition Without Rubber-Banding

### Question
Do broad investigator skills and volatile tactical state keep weaker deductive players engaged and dangerous without loser bonuses or hidden assistance?

### Prototype
Representative short session with deliberately mixed player strengths.

Include deduction, investigation choice, at least one competitive minigame, information warfare/social play, and finite Leverage.

### Observe
- who has meaningful decisions late in the session,
- whether a strong deductive player creates an unrecoverable runaway,
- whether non-deduction skills generate real investigative opportunities,
- whether weaker players remain capable of changing the race,
- whether players understand why advantages occurred.

### Failure signals
- one player becomes functionally unbeatable early,
- minigames become the real victory path,
- weaker players stay entertained but cease to matter competitively,
- recovery requires artificial bonuses rather than legitimate play.

## Test 5 — Group Rescue Exploit Test

### Question
Does unanimous authored rescue function as rare recovery, or does it become optimal routine play?

### Prototype
Provide a limited rescue option in a case with at least one plausible stall point.

### Observe
- when players request it,
- why they request it,
- whether players attempt to invoke it strategically rather than from genuine uncertainty,
- social friction around unanimity,
- whether the added evidence restores productive investigation without stating the inference.

### Failure signals
- groups request rescue by default,
- competitive players block rescue purely to grief the room,
- the rescue effectively tells players what comparison matters,
- rescue content requires excessive bespoke authoring.

## Test 6 — Room-Compatible Minigame Pool

### Question
Can accessibility filtering preserve enough minigame variety, spectacle, and eccentric investigator skill expression?

### Prototype
Tag a representative V1 candidate minigame set by required modalities/interaction demands, then simulate several room configurations.

### Observe
- surviving pool size,
- repeated mechanics,
- lost skill categories,
- whether filtering makes exclusions obvious enough to reveal a player's private settings,
- whether compatible alternatives retain equal entertainment value.

### Failure signals
- some common configurations collapse the pool,
- accessible alternatives are visibly lesser games,
- filtering consistently exposes why a game was excluded,
- the design begins requiring individualized easier variants to function.

## Recommended Order

1. **Time-to-Fun / Progressive Onboarding**
2. **Memory Support vs. Auto-Solving**
3. **Same Challenge at 2 vs. 4 Players**
4. **Mixed-Skill Competition Without Rubber-Banding**
5. **Group Rescue Exploit Test**
6. **Room-Compatible Minigame Pool**

The first four directly test Nightcap's foundational experience. Rescue and pool filtering can follow once the core loop is behaving correctly.

## Decision Rule

A failed test should first trigger simplification or redesign.

Do not respond to failure by:
- secretly lowering difficulty for selected players,
- adding more UI complexity,
- increasing tutorial burden,
- replacing authored cinema with summaries,
- or introducing rubber-banding without explicit design review.
