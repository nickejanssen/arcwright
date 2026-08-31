# Nightcap — Story Reactivity & Re-entry

**Status:** Foundational direction DECIDED; implementation details TESTING  
**Type:** GDD system one-pager

## Purpose

Story Reactivity connects Nightcap's investigation, deduction, competition, and narrative into one living murder mystery.

`REACT` is not a separate mode or screen. It is the response layer through which meaningful actions change characters, information, opportunities, social dynamics, or competitive state before returning players to play.

## Core Experience

Nightcap reactions are **naturalistic but legible**.

The game should generally avoid explicit system messages explaining causality. Timing, staging, character behavior, presentation, and context should make it understandable that something changed because of what happened.

The player perceives the consequence without the game interpreting its meaning for them.

## Tactical Consequences

Player actions may genuinely make investigation harder.

Reactions may:

- temporarily close opportunities,
- cause opportunities to be lost,
- make a suspect more guarded,
- expose information,
- alter access or priority,
- advantage another player,
- create new competitive or investigative problems.

Nightcap does not protect players from every bad tactical decision.

However, an individual consequence must not unfairly destroy case solvability. **Essential truths retain fair alternate routes.**

## Shared vs. Private Reactions

Nightcap uses a **hybrid model**.

Some reactions are shared room-level events. Others are private or selectively visible. A shared event may create unequal information, interpretation, follow-up opportunities, or tactical consequences for different players.

This preserves both cinematic party theater and private information warfare.

## Murder Relevance

A major reaction should change something players can subsequently investigate, reconsider, prove, conceal, expose, exploit, or act upon.

Flavor reactions are allowed, but should not consume the pacing budget of meaningful reactions.

## Mystery Ownership

REACT may make **state** legible.

It may not perform **inference**.

The game may show what visibly changed, legitimately acquired information, current opportunities, new opportunities, and changed competitive/social state.

It may not:

- identify the important relationship between facts,
- tell players which opportunity matters most,
- rank suspects,
- identify an undiscovered contradiction,
- recommend the correct investigation,
- confirm a theory,
- manufacture proof to rescue a struggling player.

## Re-entry

After cinematics, minigames, espionage, social confrontations, or other interruptions, players should be able to resume the murder without reconstructing the entire session.

Re-entry surfaces **state, not inference**.

Exact provenance UI, search, filtering, history, and other memory-support implementations remain TESTING.

## System Handoffs

- **Investigation → REACT:** investigation may provoke character, story, opportunity, information, or competitive consequences.
- **THINK → REACT:** reasoning becomes reactive when a player acts on it through a challenge, accusation, social move, or commitment.
- **PLAY → REACT:** competition creates finite consequences that reconnect to the murder-facing game.
- **Espionage → REACT:** information warfare may alter knowledge, exposure, access, protection, social behavior, or opportunity.
- **REACT → HUNT / THINK / PLAY:** changed state creates meaningful possibilities rather than a recommended correct move.

## Pacing

Not every action deserves a reaction beat.

Avoid cinematic interruption after routine actions, repeated recaps, dialogue that changes nothing, serial interruptions before the player can act, and long transitions back to investigation.

A meaningful reaction can be extremely small.

## Player Count

The architecture must work with two players without requiring a crowd to create meaningful consequences. At higher counts, reaction cadence must avoid excessive room-wide interruption.

Exact scaling remains TESTING.

## Design Check

> **What caused this? What changed? What can the player do differently now?**

Then ask:

> **Did the game expose state, or did it accidentally explain the mystery?**
