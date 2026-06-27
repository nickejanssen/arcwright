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

## Closure

M4 closes via the AW-259 parent task. The four M4 close items are:

- [AW-257: Promote Crime Scene Smash and Evidence Locker to active](../tasks/AW-257-promote-crime-scene-smash-and-evidence-locker.md)
- [AW-260: Founder Rehearsal Runbook and Blocker Log](../tasks/AW-260-founder-rehearsal-runbook-and-blocker-log.md)
- [AW-261: ADR-0003 Cloudflare vs GCP Validation Decision](../tasks/AW-261-adr-0003-cloudflare-vs-gcp-validation-decision.md)
- [AW-259: Rehearsal 1 - M4 Exit, First Real-Human Nightcap Session](../tasks/AW-259-rehearsal-1-m4-exit.md) (parent; consumes AW-254 and AW-231 as sub-issues)

AW-254 and AW-231 retain their original issue numbers (#148, #84) but their
scope is rewritten per `docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`.
