# AW-105: Knowledge graph assertion API

**Milestone / Epic:** M1 / C  
**Size:** L  
**Implements:** Arch S4, PRD Principle 5, S15.9 #2  
**Depends on:** AW-104

## Build

Implement `assert_knowledge`, `get_character_knowledge`, and `revoke_knowledge` against the knowledge-state data model. These are deterministic functions with no AI calls.

## Acceptance Criteria

- [ ] `assert_knowledge`, `get_character_knowledge`, and `revoke_knowledge` are implemented and unit tested
- [ ] Querying a character's knowledge returns only facts that character has learned
- [ ] Revocation removes access without deleting the underlying fact
- [ ] Provenance is recorded on assertion

## Do NOT

- Make knowledge state optional or a performance trade-off
- Allow any path that returns facts outside the queried character's state

## Testing

Knowledge graph correctness is one of the locked unit-test areas. Write the full unit suite here.

## Agent Notes

This is one of the most important correctness boundaries in the platform. Over-test it.
