# AW-282 Discovery and Checkpoint Record

**Date**: 2026-07-18

**Status**: Approved for implementation

**Interaction profile**: Creative collaboration

## Discovery decisions

The founder-directed session established the following product and platform decisions:

1. The player-facing term is Questions with the action Ask. The term intent is not used in player copy or engine vocabulary.
2. Players choose both who to question and what to ask. The engine may stage an opening target but never chooses the player's target or question.
3. Each menu contains three dependable authored choices and up to two evidence-unlocked choices. Evidence-unlocked choices use deterministic authored order and can appear in later windows.
4. Question allowances vary by player count and are shared across rounds within a beat. The approved guidance is three selections each for two players, two each for three or four players, and one each for five through eight players.
5. Selected questions receive public answer requests. Authored private options can additionally produce private feedback for the selecting player.
6. Free-text and voice questions are deferred from v1. The possibility of an AI-answered written question remains a future design question, not an AW-282 implementation requirement.
7. Leverage advantages and sabotages are documented as a separate design artifact and remain outside AW-282 runtime scope.

## Reviewed scenarios

- [Round-flow artifact](../superpowers/specs/2026-07-18-aw282-structured-interaction-design.md#round-flow-artifact): stage target, private selection, rotating resolution, public grouping, and close-window behavior.
- [Menu scenarios](../superpowers/specs/2026-07-18-aw282-structured-interaction-design.md#menu-scenarios): dependable choices, evidence-linked choices, and deterministic later-window ordering.
- [Canonical implementation spec](../specs/0074-aw282-structured-interaction-loop.md): runtime contract, acceptance criteria, and AW-283 handoff.

The review package explained the assumptions, player-facing implications, tradeoffs, and test evidence for each scenario. The founder selected the structured menu recommendation, confirmed the vocabulary cleanup could continue during implementation, and approved the implementation plan.

## Checkpoints

| Checkpoint | Artifact | Approval evidence | Result |
|---|---|---|---|
| Discovery | This record | Founder feedback captured in the 2026-07-18 session | Approved |
| Round flow | Design record, round-flow artifact | Founder confirmed the player-led target and question flow | Approved |
| Menu behavior | Design record, menu scenarios | Founder approved baseline plus evidence-unlocked choices and deterministic ordering | Approved |
| Thin slice | Canonical spec and implementation plan | Founder replied approved before implementation | Approved |

## Scope owner actions

- Codex implements AW-282 through the pull request.
- Claude Code owns AW-283 answer generation and contradiction metadata.
- Leverage runtime behavior remains a later approved scope decision.
