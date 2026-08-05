> Current version: v0.2
> Last updated: 2026-08-03
> Status: Draft
> Canonical path: docs/specs/0083-evidence-locker-402-game-ready.md

# Evidence Locker 402 Game-ready Contract

## References

- Platform contracts: `docs/specs/0077-mini-game-registration-and-story-opportunities.md` through `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`
- Package: `nightcap/mini_games/evidence-locker-402/`
- Story: `docs/story-bibles/nightcap-couch-race.md`

## Overview and gate

Evidence Locker 402 is a selected-player lock-picking challenge that becomes a
reusable package plus Nightcap adaptation. Its initial placement policy
requires Twist while remaining reusable in other approved destinations. It
supports 2-to-8-player sessions with one active participant. This Draft defines
version 0.2.0 and requires founder gameplay, spectator, visual, device, and
implementation approval.

## Human collaboration contract

**Profiles:** Creative collaboration and facilitated live operation. The founder approves selection fairness, pressure rules, spectator experience, presentation artifact, and promotion. Device and player findings are observed gates.

## Gameplay and selection

The active participant is selected by fewest prior selections in the session, then invocation-seeded hash, then stable join order. Pressure mode contains four pins, a 45-second deadline, authored order, target values from 0 through 100, tolerance 10, and a seeded red zone. A submission contains `action=release_pin`, `pin_index`, `lift_value`, and `state_revision`.

Four in-order releases inside tolerance open the lock. A wrong-order release or value in the red zone breaks the pick. Python owns participant selection, pin order, targets, tolerance, red zone, revision, success, break, timeout, and result. Result semantics grant a bounded edge on success and reduced-edge fallback on break or timeout. The normal evidence path remains available in every outcome.

`MiniGameDefinition.min_players` and `max_players` are both 1 for active participants. `session_min_players` and `session_max_players` are 2 and 8. The coordinator checks session range; the hosted adapter checks selected active count.

## Runtime configuration and story fit

Certified configuration may tune time within approved bounds, tolerance,
authored red-zone profile, presentation intensity, copy, audio, and edge
mapping. Selection fairness, private target authority, deterministic seed
behavior, and evidence-not-gated policy are fixed. The Nightcap adaptation is
a candidate in Twist's recontextualization policy; neither package nor engine
hardcodes the beat.

## Presentation and privacy

- Selected player surface: accessible lift control, private pin targets/order, revision feedback, and authoritative deadline.
- Spectator player surface: selected detective, public pin count, time, and tension copy, never target values, order, red zone, or controls.
- Shared-focus surface: selected detective, public progress, success, break, and timeout staging.
- Host surface: selection, connection state, progress, and safe cancellation/fallback controls.

The package renderer supports keyboard and touch, 44-pixel controls, visual and audio feedback, sound controls, color-independent states, ARIA status, reconnect, and reduced motion. Nightcap theme and asset interpretation stay outside generic engine code.

## Failure behavior

Stale revisions, invalid values, wrong order, red-zone release, duplicate action, selected-player disconnect, timeout, and host cancellation finalize once. Disconnect before selection excludes that participant; disconnect during play cancels into the authored reduced-edge fallback. Reconnect restores private state only to the selected authenticated player. No target or private control enters shared telemetry.

## Certification and acceptance criteria

- [ ] Version 0.2.0 is immutable at playtest and declares active range 1-to-1 plus session range 2-to-8.
- [ ] The mechanic exists as a destination-neutral reusable package and a
  non-destructive, independently versioned Nightcap adaptation.
- [ ] Selection is fair, deterministic, replayable, and least-recently-selected first.
- [ ] Pin generation, release validation, revision, break, success, timeout, disconnect, and fallback are Python-authoritative.
- [ ] Spectators remain engaged without receiving private targets or controls.
- [ ] Real-device evidence covers selected and spectator phones, shared focus, host operation, reconnect, accessibility, sound, motion, reduced motion, and 2/8-player layouts.
- [ ] Real-player rehearsal validates selection fairness, pressure, spectator attention, control clarity, success satisfaction, failure grace, Twist fit, and replay desire.
- [ ] The local lab makes selected-player, spectator, shared-focus, host,
  disconnect, reconnect, timeout, and fallback scenarios one-click testable.
- [ ] The production lab visualizes player-count, privacy, fairness,
  accessibility, performance, device, and human evidence.
- [ ] Founder signs off before active promotion and whole-session certification.

Tests cover ranges, selection history, seeded tie-break, target generation, release validation, break, success, timeout, disconnect, privacy projections, renderer payloads, and readiness gates.

## Out of scope

Multiple simultaneous active pickers, client-authoritative targets, evidence lockout, and active promotion before integrated certification are excluded.

## Founder decisions required

Approve or revise least-used selection, four pins, 45 seconds, tolerance 10, break conditions, spectator staging, and reduced-edge fallback.
