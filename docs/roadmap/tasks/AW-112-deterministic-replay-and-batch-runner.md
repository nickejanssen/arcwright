# AW-112: Deterministic replay and batch runner

**Milestone / Epic:** M1 / E  
**Size:** S  
**Implements:** Arch S2.9, S12.2 Phase 7, S15.9 #11 (split)  
**Depends on:** AW-110, AW-111

## Build

Add deterministic trace comparison and a headless batch runner that can execute the same scripted scenario repeatedly from seeds without UI or token spend.

## Acceptance Criteria

- [ ] Running the same scenario twice with the same seed produces an identical harness trace
- [ ] Batch runner can execute 10 headless sessions from scripted scenarios
- [ ] Batch output includes per-run seed and pass/fail summary for determinism checks
- [ ] Batch execution remains offline and mock-friendly

## Do NOT

- Build a replay UI, metrics dashboard, or analytics pipeline
- Introduce real provider calls into the batch path

## Testing

- Seeded determinism test
- 10-run batch smoke test

## Agent Notes

Mock at the `engine.routing.logging.generate` boundary if any generation path is exercised. Do not reintroduce provider or model string literals into harness tests.
