# AW-108: Prompt caching and generation logging

**Milestone / Epic:** M1 / D  
**Size:** M  
**Implements:** Arch S2.7, PRD Principle 6  
**Depends on:** AW-107

## Build

Wire prompt caching for stable per-session context layers and log every generation call to `generation_logs` with token counts and cost so per-session margin is computable.

## Acceptance Criteria

- [ ] Stable context layers are marked cacheable
- [ ] Every model call writes a `generation_logs` row
- [ ] `CONTENT_LOGGING_ENABLED` controls full prompt and response population

## Do NOT

- Default runtime narrative generation to the most capable model; budget-first remains the default

## Testing

Assert cacheable layers are flagged and that a `generation_logs` row is written per call.

## Agent Notes

Document the cache invalidation rule when session state changes.
