# M4: Nightcap Experience Layer

**Status:** Planned  
**Build-order coverage:** none (experience layer, PRD-required)

## Summary

This milestone is the Nightcap experience built on top of the platform. It covers rendering, join flow, device behavior, and the actual player-facing session experience.

The roadmap notes that the UI may be built on an external platform connected to Arcwright via API. M4 implementation tasks are blocked until AW-202 selects the external platform and documents the integration contract.

## Epics

- [M4-A: Nightcap External Platform Integration](../epics/M4-A-nightcap-external-platform-integration.md)
- [M4-B: Nightcap Host And Shared Display Experience](../epics/M4-B-nightcap-host-and-shared-display-experience.md)
- [M4-C: Nightcap Player Device Experience](../epics/M4-C-nightcap-player-device-experience.md)
- [M4-D: Real-Device Privacy And Join Validation](../epics/M4-D-real-device-privacy-and-join-validation.md)

## Exit Gate

- Real humans can play end-to-end on real devices
- Join flow takes under 30 seconds
- Private information never appears on the shared display
