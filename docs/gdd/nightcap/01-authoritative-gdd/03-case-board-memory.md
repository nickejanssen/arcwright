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

## Baseline Detective Notebook

The player's private phone surface should provide a lightweight factual detective notebook by default. It automatically preserves information the player legitimately learned, including where relevant:

- suspects and their known relationships;
- dialogue / claim transcript;
- clear speaker / suspect attribution;
- factual observations;
- objects, records, locations, and time anchors;
- evidence the player actually possesses or verified;
- replay / review of earned case-critical information.

The notebook is a **projection of player-specific knowledge and provenance**, not a second competing truth store. Arcwright remains authoritative for what the player legitimately encountered, heard, acquired, verified, or owns.

Players may add **short private notes**. Notes are player-authored thinking, not canonical case facts, and must never be treated as proof simply because they exist in the notebook.

## Living Suspect Cards

Suspects should remain legible without front-loading dense biographies.

A suspect card begins with only what the player should reasonably know, normally:

- identity;
- relationship to the victim or gathering; and
- one memorable human hook.

As the player legitimately learns more, the card may accumulate objective information such as statements, known relationships, observed behavior, objects, locations, or other factual state. It should feel like the player's understanding of a person becoming richer through investigation.

The card must not expose hidden biography, label a suspect guilty, rank suspicion, identify an undiscovered contradiction, or summarize a designer-authored theory of that suspect.

## Baseline Memory Support

DECIDED baseline support includes:

- persistent dialogue / claim transcript;
- clear speaker / suspect attribution;
- replay / review of earned case-critical information;
- objective organization of legitimately learned facts around understandable case entities;
- living suspect cards; and
- optional short private player notes.

The game may help players retrieve, remember, review, organize, and compare information they legitimately discovered. Nightcap also owns the factual bookkeeping of what a player legitimately acquired, verified, heard, or merely encountered, so final-theory eligibility does not become a memory test.

It may not:

- rank significance;
- choose the important comparison;
- identify an undiscovered contradiction;
- recommend the correct investigative action;
- infer the conclusion.

Ownership/provenance may be shown as objective state. It must not be converted into a hint that the owned item is important, persuasive, contradictory, or relevant to a particular suspect.

## Automatic Organization

Nightcap may automatically organize discovered information using **objective factual metadata**, such as:

- person;
- location;
- time;
- source;
- artifact / evidence type.

Meaningful deductive relationships such as *supports*, *contradicts*, *motive*, *opportunity*, or *suspicious* normally remain player-owned unless explicitly established as factual information in the fiction through a valid action.

## Player-Built Connections

The Case Board supports simple expressive tools.

Players may:

- connect information;
- group items;
- annotate them;
- optionally label their own relationships.

Avoid formal logic notation or heavy graph administration as a default requirement.

## Optional Reasoning Tool

The Case Board is not mandatory homework.

Players may use it heavily, lightly, or minimally. A player who can mentally track the case should not be forced to externalize every inference merely to continue playing.

Formal commitment becomes necessary primarily at the Case File, where V1 uses Structured Reconstruction rather than an essay or proof packet.

## Theory History

The live Case Board should stay focused on the player's current thinking.

Nightcap may retain abandoned or evolving player-authored theories that the player actually externalized through the Case Board or another explicit interaction, invisibly for:

- Postmortem;
- telemetry;
- later reflection;
- playtest research.

Historical theories should not automatically clutter or anchor the active investigation.

## State, Not Inference

> **The game may help me remember what I know. It should not tell me what I think.**

## Validation Note

Paper Test #2 v2.2 produced mixed memory-difficulty signals, so the exact amount of memory assistance remains a testing question. The test did, however, reinforce character-legibility and recall friction strongly enough to justify the factual notebook / living-card baseline without turning that support into automated deduction.

The prior Gate 2 question now concerns **how much additional memory/retrieval support is useful before it starts doing the reasoning**, not whether Nightcap should provide any factual memory surface at all.

## TESTING

- exact Case Board UX;
- optional provenance displays;
- re-entry cues;
- search/filtering;
- friction vs. deduction impact;
- how much Case Board interaction players actually want;
- note-entry friction on phones;
- how much information belongs on a living suspect card before it becomes clutter.