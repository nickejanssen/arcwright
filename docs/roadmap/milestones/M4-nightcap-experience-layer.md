# M4: Nightcap Experience Layer

**Status:** Planned  
**Build-order coverage:** none (experience layer, PRD-required)

## Summary

This milestone is the Nightcap experience built on top of the platform. It covers rendering, join flow, device behavior, and the actual player-facing session experience.

The roadmap notes that the UI is built as a separate Nightcap web experience connected to Arcwright via API. M4 implementation tasks follow the AW-202 Nightcap web experience runtime contract.

## Epics

- [M4-A: Nightcap Web Experience Runtime Integration](../epics/M4-A-nightcap-external-platform-integration.md)
- [M4-B: Nightcap Host And Shared Display Experience](../epics/M4-B-nightcap-host-and-shared-display-experience.md)
- [M4-C: Nightcap Player Device Experience](../epics/M4-C-nightcap-player-device-experience.md)
- [M4-D: Real-Device Privacy And Join Validation](../epics/M4-D-real-device-privacy-and-join-validation.md)
- [M4-E: Nightcap Mini-game Interaction Layer](../epics/M4-E-nightcap-mini-game-interaction-layer.md)

## Exit Gate

- Real humans can play end-to-end on real devices
- Join flow takes under 30 seconds
- Private information never appears on the shared display
- One approved production mini-game completes on real devices through both its
  normal and delayed clue fallback paths
