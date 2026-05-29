# M3: Events, API, Persistence, Telemetry

**Status:** Planned  
**Build-order coverage:** #6 events, #8 API + auth, #9 persistence, #10 telemetry, #11 full harness

## Summary

This milestone exposes the platform over API boundaries, adds event delivery and resume behavior, and completes the full telemetry and simulation harness work needed for real end-to-end sessions.

## Epics

- Content event system
- FastAPI layer and auth
- Session persistence
- Telemetry MVP minimum
- Full simulation harness

## Exit Gate

- A full Nightcap session runs end-to-end through the API
- Event routing respects target audience boundaries
- Interrupt and resume restores to the nearest beat
- Telemetry signals log from real sessions
