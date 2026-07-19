# AW-282 Structured Interaction Design

> Current version: v0.1
> Last updated: 2026-07-18
> Status: Approved design
> Canonical path: docs/superpowers/specs/2026-07-18-aw282-structured-interaction-design.md

**Author**: Codex, founder-directed design session

## References

- [AW-282 roadmap task](../../roadmap/tasks/AW-282-interrogation-round-loop-and-question-intents.md)
- [Nightcap Couch Race v1 parent spec](../../specs/0072-nightcap-couch-race-v1.md)
- [Nightcap Couch Race story bible](../../story-bibles/nightcap-couch-race.md)
- [Live-loop AI character dialogue](../../specs/0071-live-loop-ai-character-dialogue.md)
- [Architecture: Arc Execution](../../architecture/03-arc-execution.md)
- [Architecture: Event System](../../architecture/08-event-system.md)
- [Architecture: Knowledge Graph](../../architecture/04-knowledge-graph.md)
- [Leverage advantages and sabotages design](../../product/nightcap-leverage-advantages-sabotages.md)
- [Discovery and checkpoint record](../../product/aw282-discovery-and-checkpoints.md)

## Overview

AW-282 adds a game-agnostic Structured Interaction capability for bounded, state-aware player interactions. Nightcap configures the capability as interrogation rounds. Daily Case can configure the same capability for one player and one character.

The engine owns deterministic state, option eligibility, resource accounting, selection order, duplicate handling, and event audiences. AI character answers and contradiction detection remain the AW-283 seam. The engine never asks a model to build menus, select targets, infer relevance, or update canonical state.

## Locked product decisions

- The player-facing concept is **Questions**, with the action **Ask**. The word “intent” does not appear in player copy.
- The platform vocabulary uses `Structured Interaction` and typed interaction concepts. It does not use Nightcap-specific names in engine modules or schemas.
- A player sees five question choices at a time: three dependable choices and up to two choices unlocked by held evidence.
- Evidence-unlocked choices are deterministic. Eligible choices not shown remain eligible later in deterministic authored order.
- V1 does not accept unrestricted free-text or voice questions.
- Players choose who to interview and what to ask after the opening character is staged. The engine may stage an opening character, but never chooses a player target or question for them.
- Players lock choices privately. Resolution follows table order, with the first participant rotating each round.
- Identical public questions in the same round combine into one public answer. Each player still spends one selection. Authored private options additionally produce private feedback for the selecting player.
- Identical private responses resolve separately.
- The budget counts selections, not unique public answers.
- Target budget guidance is six to eight total selections per interrogation beat where player count permits: three each for two players, two each for three to four players, and one each for five to eight players. Every player receives at least one selection.
- Private feedback is phrased for the player as “You noticed…” and labeled “Your read.” It provides directional observations, not automatic truth or lie verdicts.
- A deterministic stall signal may trigger a narrator bridge or authored lead highlight. No model decides that players are close to solving.

## Platform vocabulary

These names describe structure, not Nightcap semantics:

| Concept | Responsibility |
|---|---|
| `InteractionDefinition` | Authored rules for one configured interaction capability. |
| `InteractionWindow` | A bounded period in which players may select and resolve interactions. |
| `InteractionOption` | One selectable action with deterministic eligibility and authored presentation data. |
| `InteractionTarget` | A selectable entity that can receive an interaction. |
| `InteractionSelection` | A private player choice of target and option. |
| `InteractionResolution` | The deterministic ordering and grouping result for locked selections. |
| `InteractionOutcome` | The structured result delivered to public or private audiences. |
| `PrivateFeedback` | Player-specific structured feedback associated with an outcome. |
| `InteractionLimit` | Authored count or budget constraint for a player or window. |
| `InteractionDirector` | Deterministic staging, pacing, grouping, and fallback coordinator. |

Nightcap maps these concepts to suspects, questions, answers, and “Your read” feedback outside the engine vocabulary.

## Round-flow artifact

### Setup

The director receives an immutable session snapshot containing:

- Session seed.
- Participant order and active participants.
- Current beat and interaction window.
- Eligible targets.
- Each participant’s held evidence identifiers.
- Authored option definitions and evidence unlock rules.
- Per-player selection limits.
- Prior interaction claims and feedback references needed for eligibility.

The director validates that the window is open and that every active participant has a legal selection path.

### Stage the opening character

The director selects an opening target from authored candidates using the session seed and deterministic eligibility rules. The selected target is staged as the cinematic opening, but players remain free to choose other eligible targets.

No model call occurs during staging.

### Build each player's menu

For each participant, the engine evaluates the authored option rules against that participant's held evidence and the current window state.

The menu contains:

1. Three dependable options selected from the authored baseline order.
2. Up to two eligible evidence-based options selected from deterministic evidence order.
3. No duplicate semantic options.
4. A stable fallback when fewer than five options are eligible.

If more than two evidence-based options are eligible, the unshown options remain eligible in the same deterministic order for later windows. The engine never calls a model to rank or write the menu.

### Private selection

The player privately selects a target and one option. The client submits only a typed selection identifier. The engine revalidates target eligibility, option eligibility, and remaining selection allowance before accepting the selection.

The player may revise the selection until the private selection window closes. A submitted selection is not public until resolution begins.

### Lock and resolve

At the deadline, or when all active participants lock, the director creates a deterministic resolution plan:

1. Rotate the first participant using the round index.
2. Preserve table order from that starting point.
3. Group identical public target and option pairs into one public answer request.
4. Keep private outcomes associated with each original selection.
5. Apply authored pacing metadata without changing player-selected targets or options.

The resolution plan is immutable after creation. AW-283 consumes the unique public answer requests and returns structured generated content for the engine to validate and emit.

### Emit outcomes

For every public group, emit one public outcome to all authorized session participants. For every selection whose authored option has private visibility, emit one private `PrivateFeedback` outcome only to the selecting participant.

The public outcome contains no private evidence or player-specific feedback. The private outcome contains the source interaction identifier, the player-specific observation, and any authored follow-up eligibility identifiers.

### Close the window

After every accepted selection has resolved or entered an explicit fallback state:

- Mark the window complete.
- Persist selection expenditure.
- Persist claim and feedback references needed by later windows.
- Emit the next authored arc transition or narrator bridge if configured.
- Do not silently refund a selection because a public question was duplicated.

## Option-menu artifact

The following is a Nightcap-facing content example. The engine stores typed option structure and stable identifiers. Theme copy belongs in arc content.

### Three dependable choices

| Stable role | Example player copy | Purpose |
|---|---|---|
| Location and timing | “Where were you around the time it happened?” | Establish or test an alibi window. |
| Relationship | “What was your relationship with the victim?” | Establish motive, tension, or access. |
| Observation | “What did you notice that night?” | Invite a broad observation without requiring a theory. |

### Up to two evidence-based choices

| Stable role | Example player copy | Unlock condition |
|---|---|---|
| Evidence link | “What can you tell me about the torn invitation?” | Player holds the authored evidence identifier for the invitation. |
| Detail follow-up | “Why did you leave before the lights went out?” | Player holds an evidence item whose authored unlock points to the timeline gap. |

These examples are not engine strings. A different game may use “Inspect,” “Challenge,” “Trade,” or another theme-specific action while consuming the same platform option structure.

## Selection allowance

The allowance is an `InteractionLimit` configured per window and participant group. The engine counts accepted player selections.

Example for two players:

- Alex has three selections.
- Sam has three selections.
- If both select the same public question, the room hears one answer, but six selections are still spent in total.
- If either player selects an authored private option, that player receives a private feedback outcome.

Example for five players:

- Each participant has one selection.
- The director may still group identical public questions.
- The group can hear fewer unique answers than selections without violating the budget.

Token exhaustion rejects further selections with a typed, player-safe error. It does not expose another player's remaining allowance.

## Deterministic director rules

The `InteractionDirector` may:

- Stage an authored opening target.
- Rotate resolution order.
- Group identical public selections.
- Choose an authored fallback for a stalled or invalid interaction.
- Apply authored pacing metadata that changes presentation order within the legal resolution plan.

The director may not:

- Select a target for a player.
- Select a question for a player.
- Build or rank a menu with a model.
- Infer that a player is close to solving.
- Decide whether a character lied.
- Change evidence, case truth, or canonical session state based on generated prose.

## Error and recovery behavior

| Condition | Deterministic behavior |
|---|---|
| Selection window closed | Reject submission with a closed-window error. |
| Player has no allowance | Reject submission with an exhausted-limit error. |
| Target no longer eligible | Reject submission and return the refreshed legal target set. |
| Option no longer eligible | Reject submission and return the refreshed legal option set. |
| Fewer than five legal options | Show all legal options in stable order. |
| Duplicate public selection | Group public answer generation and preserve per-player private outcomes. |
| Player disconnects before lock | Use the authored timeout fallback; never invent a free selection. |
| Player disconnects after lock | Resolve the accepted selection normally. |
| Answer generation unavailable | Emit an authored delayed or deterministic fallback outcome and preserve state. |
| All players stall | Trigger the authored narrator or lead fallback without revealing a solution. |

## AW-283 seam

AW-282 produces a validated resolution request containing:

- Window and round identifiers.
- Unique public groups.
- Original participant selections.
- Target identifiers.
- Option identifiers.
- Authorized character knowledge context reference.
- Claim and evidence references needed by the answer generator.

AW-283 returns structured answer content and contradiction metadata through its own contract. AW-282 remains responsible for audience filtering, deterministic state transitions, and selection accounting.

## Leverage seam

The approved Leverage catalog is a follow-on capability. AW-282 may expose a typed extension point for a future interaction modifier, but it does not implement Leverage grants, spends, advantages, sabotages, or mini-game rewards.

The future modifier must be able to target a legal interaction and resolve deterministically before answer generation. It cannot cancel a question, delete evidence, change case truth, or create an unfalsifiable clue.

## Testing strategy

### Unit tests

- Baseline menu contains three dependable options in authored order.
- Evidence unlocks add at most two options.
- Eligible but unshown evidence options remain deterministic for later windows.
- Duplicate semantic options are removed.
- Selection allowance counts accepted selections, not unique public groups.
- Exhausted allowance rejects further selection.
- Round order rotates by participant and round index.
- Identical public selections group into one public request.
- Identical private selections remain separate outcomes.
- Private feedback is associated with only the selecting participant.
- Staging is deterministic under a fixed seed.
- No model call is required to build a menu or resolution plan.

### Integration tests

- Public answer events reach all session participants.
- Private feedback events reach only the asker.
- Reconnect does not reveal another player's private feedback or allowance.
- AW-283-shaped answer requests preserve all knowledge and evidence references.
- A two-player and eight-player synthetic session complete a full interaction window.

### Determinism tests

- Replaying the same seed and session snapshot produces identical menus, selected option identifiers, staging target, resolution order, public grouping, and allowance expenditure.

## Acceptance criteria

- [ ] A synthetic session runs interrogation windows with options resolving deterministically from evidence state.
- [ ] Public answers reach all authorized session participants.
- [ ] Private feedback reaches only the selecting participant.
- [ ] Token exhaustion blocks further questions and is arc configurable.
- [ ] Duplicate public selections generate one public request. Authored private selections generate separate private outcomes.
- [ ] Daily Case can configure one participant and one target using the same capability.
- [ ] No unrestricted free-text input is accepted in v1.
- [ ] Menus and resolution plans require no model calls.
- [ ] A fixed seed reproduces staging, menus, resolution order, and expenditure.
- [ ] The capability contains no Nightcap-specific engine vocabulary.

## Out of scope

- AW-283 suspect answer generation and contradiction detection.
- AW-284 scoring, accusations, and Last Call.
- AW-285 TV and phone rendering.
- AW-286 rehearsal operations.
- Full Leverage economy and player-targeted advantages or sabotage.
- Free-text or voice questioning.
- Teams or cooperative competition rules.

## Risks and open questions

**Risks**:

- Five choices may still feel restrictive if evidence unlocks are weak.
- Too many evidence options can make the deterministic order feel arbitrary.
- Duplicate public questions may reduce the visible answer count even though the selection budget is correct.
- Follow-up effects increase generation cost and need explicit caps.

**Open questions before implementation**:

- Exact names and serialized shapes for the Python models.
- Whether a target is selected as part of the same option menu or as a separate interaction step.
- Exact timeout fallback behavior for a disconnected player.
- Exact event type names for public outcomes and private feedback.
- Whether Leverage receives a modifier hook in AW-282 or in its follow-on task.
