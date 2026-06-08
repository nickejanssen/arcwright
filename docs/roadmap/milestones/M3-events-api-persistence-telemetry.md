# M3: Events, API, Persistence, Telemetry

**Status:** Planned  
**Build-order coverage:** #6 events, #8 API + auth, #9 persistence, #10 telemetry, #11 full harness

## Summary

This milestone exposes the platform over API boundaries, adds event delivery and resume behavior, and completes the full telemetry and simulation harness work needed for real end-to-end sessions.

## Epics

- [M3-A: Content Event System](../epics/M3-A-content-event-system.md)
- [M3-B: API, Auth, And TypeScript SDK](../epics/M3-B-api-auth-and-typescript-sdk.md)
- [M3-C: Session Persistence And Resume](../epics/M3-C-session-persistence-and-resume.md)
- [M3-D: Telemetry And Full Simulation Harness](../epics/M3-D-telemetry-and-full-simulation-harness.md)

## Exit Gate

- A full Nightcap session runs end-to-end through the API
- Event routing respects target audience boundaries
- Interrupt and resume restores to the nearest beat
- Telemetry signals log from real sessions
