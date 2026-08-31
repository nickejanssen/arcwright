# Nightcap — Case Board & Memory

**Status:** Foundational direction DECIDED; implementation details TESTING  
**Type:** GDD system one-pager

## Purpose

Support memory and reasoning without becoming the detective.

Nightcap separates two jobs:

### Memory / History

Answers:

> **What did I legitimately encounter?**

### Case Board

Answers:

> **How do I currently understand the case?**

They may share interface space, but they must not collapse into an automated reasoning system.

## Baseline Memory Support

DECIDED baseline support includes:

- persistent dialogue / claim transcript,
- clear speaker / suspect attribution,
- replay / review of earned case-critical information.

The game may help players retrieve, remember, review, organize, and compare information they legitimately discovered. Nightcap also owns the factual bookkeeping of what a player legitimately acquired, verified, heard, or merely encountered, so final-theory eligibility does not become a memory test.

It may not:

- rank significance,
- choose the important comparison,
- identify an undiscovered contradiction,
- recommend the correct investigative action,
- infer the conclusion.

Ownership/provenance may be shown as objective state. It must not be converted into a hint that the owned item is important, persuasive, contradictory, or relevant to a particular suspect.

## Automatic Organization

Nightcap may automatically organize discovered information using **objective factual metadata**, such as:

- person,
- location,
- time,
- source,
- artifact / evidence type.

Meaningful deductive relationships such as *supports*, *contradicts*, *motive*, *opportunity*, or *suspicious* normally remain player-owned unless explicitly established as factual information in the fiction.

## Player-Built Connections

The Case Board supports simple expressive tools.

Players may:

- connect information,
- group items,
- annotate them,
- optionally label their own relationships.

Avoid formal logic notation or heavy graph administration as a default requirement.

## Optional Reasoning Tool

The Case Board is not mandatory homework.

Players may use it heavily, lightly, or minimally. A player who can mentally track the case should not be forced to externalize every inference merely to continue playing.

Formal commitment becomes necessary primarily at the Case File, where V1 uses Structured Reconstruction rather than an essay or proof packet.

## Theory History

The live Case Board should stay focused on the player's current thinking.

Nightcap may retain abandoned or evolving player-authored theories that the player actually externalized through the Case Board or another explicit interaction, invisibly for:

- Postmortem,
- telemetry,
- later reflection,
- playtest research.

Historical theories should not automatically clutter or anchor the active investigation.

## State, Not Inference

> **The game may help me remember what I know. It should not tell me what I think.**

## TESTING

- Case Board UX,
- optional provenance displays,
- re-entry cues,
- search/filtering,
- friction vs. deduction impact,
- how much Case Board interaction players actually want.

Memory Support A/B remains blocked until the representative Time-to-Fun / Cohesion baseline passes.
