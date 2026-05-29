# AW-110: Simulation harness skeleton (arc-runnable)

**Milestone / Epic:** M1 / E  
**Size:** M  
**Implements:** Arch S2.9, S15.9 #11 (split)  
**Depends on:** AW-105, AW-107

## Build

Create a headless session runner that can instantiate a session, step it through arc states, and drive synthetic player input from a script. Seeded deterministic mode is required.

## Acceptance Criteria

- [ ] Can start a session and advance it programmatically without UI
- [ ] Seeded run produces identical output on repeat
- [ ] Synthetic player input is scriptable

## Do NOT

- Build batch statistics or replay UI yet; that is later milestone work

## Testing

Seeded determinism test.

## Agent Notes

Keep AI calls mockable in the harness so arc-logic tests run without token spend.
