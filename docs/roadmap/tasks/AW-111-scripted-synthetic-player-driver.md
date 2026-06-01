# AW-111: Scripted synthetic player driver

**Milestone / Epic:** M1 / E  
**Size:** M  
**Implements:** Arch S2.9, S3.6, S12.2 Phase 7, S15.9 #11 (split)  
**Depends on:** AW-110

## Build

Create a declarative scenario format and synthetic player driver that converts scripted player actions into harness-runner actions with deterministic participant identities and ordering.

## Acceptance Criteria

- [ ] Synthetic player input is scriptable through a small declarative scenario schema
- [ ] A scripted scenario can drive the Nightcap scaffold from session start through reveal without UI
- [ ] Invalid or out-of-order scripted actions fail with a clear harness error
- [ ] Scenarios stay offline and do not require real provider calls

## Do NOT

- Build replay diffing or batch execution yet; that belongs to AW-112
- Depend on SSE, FastAPI routes, or browser clients

## Testing

- Scenario execution tests for the happy path
- Invalid action ordering tests

## Agent Notes

Keep the scenario DSL engine-local and small. It should target the current scaffolded runtime, not a future network API.
