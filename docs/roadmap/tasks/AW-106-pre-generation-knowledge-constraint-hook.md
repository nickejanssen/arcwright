# AW-106: Pre-generation knowledge constraint hook

**Milestone / Epic:** M1 / C  
**Size:** M  
**Implements:** Arch S4, S7, PRD Principle 5  
**Depends on:** AW-105

## Build

Implement the interface that every AI character generation call must pass through, which queries the speaking character's knowledge state and assembles the allowed-facts context. This is the deterministic gate future character behavior will call.

## Acceptance Criteria

- [ ] A single function takes a character ID and returns that character's complete current knowledge as generation context
- [ ] The interface is the only sanctioned path to assemble character context for generation
- [ ] Returns are stable and ordered for prompt-cache friendliness

## Do NOT

- Allow generation context assembly to bypass this hook anywhere in the codebase

## Testing

Unit test that the hook never returns a fact outside the character's state.

## Agent Notes

Design this as the chokepoint now so later milestones cannot accidentally route around it.
