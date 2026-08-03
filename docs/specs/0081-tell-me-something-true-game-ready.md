> Current version: v0.2
> Last updated: 2026-08-03
> Status: Draft
> Canonical path: docs/specs/0081-tell-me-something-true-game-ready.md

# Tell Me Something True Game-ready Contract

## References

- Platform contracts: `docs/specs/0077-mini-game-registration-and-story-opportunities.md` through `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`
- Prior spec: `docs/specs/0061-aw-258-tell-me-something-true.md`
- Package: `nightcap/mini_games/tell-me-something-true/`
- Story: `docs/story-bibles/nightcap-couch-race.md`

## Overview and gate

Tell Me Something True is a 2-to-8-player competitive social opener and the
browser golden-path canary. It must become a reusable package and a Nightcap
destination adaptation for Pour without special onboarding or transport code.
This Draft freezes package version 0.2.0 behavior for founder gameplay, visual,
device, and implementation approval. It never gates required evidence.

## Human collaboration contract

**Profiles:** Creative collaboration and facilitated live operation. The founder approves the 2-player voter rule, scoring, social comfort, presentation artifact, and package promotion. Device and real-player gates require observed evidence, not automated inference.

## Gameplay contract

The authoritative phases remain `input`, `spotlight`, `reveal`, and `scoreboard`. Every connected participant submits a truth and lie during a 45-second input window. Spotlight order is deterministic and stable. Every other connected player votes during a 15-second window, with one eligible voter at two players, two at three players, and all other connected players at four through eight. Self-votes are rejected.

Correct vote awards one point to the voter. Each fooled voter awards one point to the spotlighted player. Final order is score descending, correct votes descending, then stable spotlight order. AFK input uses the authored truth fallback; disconnected players are skipped deterministically. Reconnect restores the current authorized phase, deadline, local submission state, eligible voters, and public spotlight.

Package result semantics are `winner-count`, `participation-rate`, `all-truth-round`, and `all-lie-round`. The arc may map these to bounded social competition or resource rewards, never required clues or canonical truth.

## Architecture and runtime configuration

`SocialTruthBluffPlugin` remains Python authority for phases, deadlines, vote
eligibility, duplicate rejection, reveal, scoring, tie-breaks, fallback, and
results through the legacy hosted-mechanic compatibility profile. Its
`project_state` returns only authorized state. TMST-specific projections and
validation move behind the mechanic; generic API and SDK carry opaque
`runtime_state` without TMST unions or route branches.

Arcwright imports the existing browser presentation through the same assisted
flow used by an external developer, generates the reusable package, and creates
a non-destructive Nightcap adaptation. Existing source remains unchanged until
an approved derivative change set is promoted.

Runtime configuration may tune prompt set, phase durations within certified
bounds, copy, safe timeout treatment, and presentation intensity. It cannot
change the no-self-vote rule, deterministic authority, private-data boundary,
or evidence-not-gated policy. The placement policy initially requires Pour and
may later delegate rotation within an approved social-opener pool.

## Presentation and theme

- Player surface: private truth/lie input, eligible vote, submission acknowledgement, private result.
- Shared-focus surface: spotlight, table-safe choices, vote progress, reveal, and standings, with no private prompt or unrevealed statement leakage.
- Host surface: phase progress, deadlines, disconnect state, and approved safe completion controls.

The package-local renderer uses `defineRenderer`, `MiniGameContext`, `SurfaceLifecycle`, countdown and submission guards, semantic theme tokens, package-scoped styles, 44-pixel targets, keyboard operation, ARIA live regions, captions where audio carries meaning, sound controls, and reduced-motion alternatives. The Nightcap game interprets its midnight/circus styling; Arcwright receives only opaque theme data and surface-neutral posture.

## Failure and fallback

Timeout, invalid or duplicate vote, disconnect, renderer remount, and generation failure resolve deterministically. Missing human input uses authored safe content or skip rules. No failure blocks the arc or removes evidence. Private statements and votes never enter public telemetry.

## Certification and acceptance criteria

- [ ] Version 0.2.0 is immutable at playtest and supports 2 through 8 players.
- [ ] The existing game completes the destination-first browser golden path as
  a reusable package plus Nightcap adaptation without engine edits.
- [ ] An observed first-time run reaches Playtest-ready within 20 minutes and a
  returning run within 15 minutes; target timing remains 10-to-15 and 5-to-10.
- [ ] All four phases, scoring, low-player voter rules, tie-break, timeout, disconnect, and reconnect are deterministic.
- [ ] Generic API and SDK contain no TMST-specific branch or public type.
- [ ] Phone, shared-focus, and host renderers pass privacy, accessibility, performance, audio, motion, and reduced-motion checks.
- [ ] Local Playtest-ready evidence includes simulated players, multi-surface
  preview, QR device join, timeout, fallback, reconnect, replay, and reset.
- [ ] Production-ready is displayed through the visual lab with automated and
  human evidence separated.
- [ ] Real-device and real-player evidence covers 2-player and 8-player behavior, comprehension, social comfort, dead air, spectacle, story transition, and replay desire.
- [ ] Founder approves gameplay, visuals, and package readiness before active promotion.

Automated tests cover phase progression, vote eligibility, no self-vote, scoring, deterministic ordering, AFK fallback, disconnect, reconnect projection, renderer privacy, exact version, and readiness report behavior.

## Out of scope

Required-clue gating, cross-session behavioral influence, direct killer-assignment signals, a TMST-specific public API, and active promotion before whole-session certification are excluded.

## Founder decisions required

Approve or revise the low-player voting rules, score/tie-break contract, phase timing, audiovisual direction, and social-comfort bar.
