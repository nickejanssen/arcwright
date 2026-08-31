# Nightcap — Difficulty + Accessibility

**Status:** Foundational direction DECIDED; implementation details TESTING  
**Type:** GDD system one-pager

## Purpose

Keep Nightcap easy to start and accessible to operate **without making the mystery easier for selected competitors or watering down the game**.

> **Making Nightcap easier to operate is not the same as making the mystery easier to solve.**

Accessibility is primarily a **design constraint**, not a major gameplay subsystem.

## Player Experience Law

Nightcap should feel like:

> **Pick a case → join → investigate.**

- Low barrier to entry.
- Shallow initial learning curve.
- Minimal time-to-fun.
- Teach mechanics progressively through play, not through a rules dump.
- Recommended first cases are real Nightcap cases, not tutorial levels.
- Normal setup targets a one-tap recommendation; deeper configuration is optional. Exact one-tap calibration remains TESTING.

## Difficulty Architecture

Nightcap separates:

1. **Case Challenge** — intellectual difficulty of the mystery.
2. **Investigation Pressure** — scarcity, opportunities, and investigative tempo.
3. **Accessibility** — how players perceive and operate the same underlying game.

### Case Challenge

Each case has an authored baseline. Alternate challenge variants exist only when deliberately authored and validated.

Challenge may vary through:
- reasoning-chain depth,
- clue/proof redundancy,
- ambiguity and contradiction subtlety,
- red-herring / alternative-theory complexity.

### Investigation Pressure

Pressure may tune investigation actions, opportunity pressure, and pacing.

**Pressure is not reading-speed pressure.** Case Challenge and Investigation Pressure lock when the case begins.

## Competitive Accessibility Law

> **Simplify or redesign the mechanic before making the game easier for one player than another.**

Individual accessibility may change presentation, input, and memory access. It may not change:
- canonical truth or culprit,
- fair solvability or evidence validity,
- victory standard or proof requirement,
- detective agency or reasoning ownership,
- competitive meaning of shared mechanics,
- the target quality of story, cinema, immersion, humor, or fun.

Players are choosing a competitive game. Accessibility removes avoidable barriers; it does not create individualized easy modes.

## Reasoning Boundary

Nightcap may help players **retrieve, remember, review, organize, and compare** information they legitimately discovered. Automatic organization may use objective factual metadata; meaningful deductive relationships remain player-owned.

Nightcap may not:
- rank significance,
- choose the important comparison,
- identify an undiscovered contradiction,
- recommend the correct investigative action,
- infer the conclusion for the player.

**Baseline memory support:**
- persistent dialogue / claim transcript,
- clear speaker / suspect attribution,
- replay / review of earned case-critical information.

Provenance displays, re-entry cues, and search/filtering remain **TESTING** and must prove they improve the game before entering the V1 baseline.

## Accessible Information & Presentation

All **competitively meaningful case information** must have an accessibility-equivalent presentation. Flavor-only details may remain modality-specific.

Equivalent presentation must preserve the same information **without adding interpretation**.

Preserve authored cinematics and adapt access around them. Accessibility should not default to replacing Nightcap's cinematic experience with a lesser summary version.

## Competitive Systems

- Minigames should be accessibility-compatible by construction where practical.
- Active settings filter the **room's** minigame pool; do not give one player a secretly easier version.
- Individual accessibility settings remain private.
- Earned information persists and remains reviewable.
- Use shared readiness gates only for important transitions.
- Last Call keeps a hard shared countdown; any extra time is a group-level setting.
- **Speed is not a standard endgame tie-breaker.**

## Group Rescue

If genuinely stuck, any player may propose an authored rescue and **all active players must agree**.

Rescue may add evidence or reopen opportunity. It may not state the inference or identify the important comparison. It is shared equally and adds no winner-specific bonus, penalty, or alternate winner calculation. Because it changes the shared case state, it may naturally affect who ultimately wins. It is recorded for case-completion/mastery context.

Exact rescue frequency, amount, and presentation remain **TESTING**.

## Mixed Skill & Player Count

Nightcap uses **broad investigator skill expression + volatile tactical state**, not loser bonuses or hidden rubber-banding.

Two-player support remains first-class. The selected Case Challenge keeps the same intellectual target; player-count scaling may adjust opportunity architecture and evidence delivery to preserve fair play, not automatically make the mystery easier.

## V1 Scope

V1 accessibility should be **lean and mostly invisible**:
- avoid common barriers by default,
- provide essential presentation/input settings,
- preserve equivalent access to competitively meaningful information,
- keep only essential memory support in baseline UX,
- redesign brittle mechanics before adding accessibility-specific machinery.

## TESTING

- Case Challenge variant construction and Investigation Pressure calibration.
- Baseline memory support vs. accidental auto-solving.
- Optional provenance / re-entry / search-filter value.
- Room-compatible minigame breadth and variety.
- Readiness-gate pacing cost.
- Group-rescue exploitability.
- Two-player same-challenge scaling.
- Mixed-skill competitiveness without rubber-banding.

## Validation Rule

**Prototype before adding more accessibility machinery.** If a support makes Nightcap less fun, less cinematic, less competitive, or easier for selected players, redesign the mechanic rather than silently accepting the tradeoff.
