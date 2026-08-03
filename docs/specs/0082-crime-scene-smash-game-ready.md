> Current version: v0.2
> Last updated: 2026-08-03
> Status: Draft
> Canonical path: docs/specs/0082-crime-scene-smash-game-ready.md

# Crime Scene Smash Game-ready Contract

## References

- Platform contracts: `docs/specs/0077-mini-game-registration-and-story-opportunities.md` through `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`
- Package: `nightcap/mini_games/crime-scene-smash/`
- Story: `docs/story-bibles/nightcap-couch-race.md`

## Overview and gate

Crime Scene Smash is a 2-to-8-player, 90-second competitive evidence-smash
race. It becomes a reusable package plus Nightcap adaptation and initially
rotates with Scene Sweep in Scene's approved discovery pool. This Draft defines
version 0.2.0 and requires founder rules, visual, gameplay, device, and
implementation approval.

## Human collaboration contract

**Profiles:** Creative collaboration and facilitated live operation. The founder approves the board rules, score/tie-break formula, visual artifact, fun bar, and promotion. Real-device and real-player evidence remain separate gates.

## Gameplay and authority

Each participant receives a private 8-by-8 board with six authored tile roles and no initial matches. A player submits two orthogonally adjacent coordinates and the current board revision. A valid swap must create a horizontal or vertical run of at least three. Python unions intersecting matches, removes tiles, drops columns, refills from the participant's seeded stream, and repeats until no cascade remains.

Score is `10 * removed_tile_count * cascade_depth`; each run of five or more adds a 50-point lead burst. Invalid swaps leave the board unchanged and increment the invalid-swap count. Python owns board seed, initial generation, swap validation, match union, cascade order, refill cursor, revision, score, timeout, and rank. The browser never submits score, matches, replacement tiles, or winner.

Final rank sorts by score descending, maximum cascade depth descending, earliest final accepted move, then stable participant join order. Result semantics expose ranked participant IDs and neutral performance values. The arc maps those facts to bounded rewards; loss or timeout never removes required evidence.

## Runtime configuration and story fit

Certified configuration may tune duration, authored tile-role art, sound
palette, copy, score-to-reward mapping, and presentation intensity. Board
dimensions, scoring formula, authority, tie-breaks, and privacy require a new
approved package version. Its destination adaptation is one candidate in the
Scene discovery placement policy, so Scene Sweep and future certified games
may rotate without engine or renderer changes.

## Presentation and theme

- Player surface: private board, score, revision-safe pending feedback, combo/cascade feedback, and authoritative countdown.
- Shared-focus surface: table-safe leaderboard, final-five countdown, and winner reveal, never private boards.
- Host surface: progress, latency/error state, deadline, and approved safe controls.

The package-local renderer supports touch and keyboard grids, 44-pixel targets, color-independent tile identity, ARIA status, reconnect remount, authoritative countdown, sound controls, captions or visual equivalents, and reduced-motion cascade substitution. Theme, art, animation, and audio are Nightcap configuration interpreted outside the engine.

## Failure behavior

Stale revisions, non-adjacent swaps, swaps without a match, duplicates, late input, disconnect, timeout, and renderer loss are rejected or finalized once without corrupting the board. Reconnect restores the exact private board, refill cursor, score, revision, deadline, and public rank. The authored reduced-edge fallback preserves story progression.

## Certification and acceptance criteria

- [ ] Version 0.2.0 is immutable at playtest, supports 2 through 8 players, and resolves the exact digest.
- [ ] The mechanic exists as a destination-neutral reusable package and a
  non-destructive, independently versioned Nightcap adaptation.
- [ ] Same seed and participant produce the same match-free board and refill sequence.
- [ ] All valid, invalid, cascade, special, timeout, tie, duplicate, and reconnect paths are deterministic.
- [ ] Private boards never enter another player's or a shared projection.
- [ ] Simultaneous 8-player play meets input, bundle, mount, and shared-rank legibility budgets.
- [ ] Real-device evidence covers touch accuracy, keyboard access, latency, reconnect, sound, motion, reduced motion, and privacy.
- [ ] Real-player rehearsal validates immediate comprehension, fairness, payoff, 90-second pacing, competition, story return, and replay desire.
- [ ] The local lab proves the game and Scene Sweep rotate deterministically,
  explains each selection, and supports replay and fallback without cloud
  deployment.
- [ ] Production-ready evidence is visualized separately from Playtest-ready
  and distinguishes automated checks from human approvals.
- [ ] Founder signs off before active promotion and whole-session registration certification.

Tests cover board generation, match detection, cascades, score formula, tie-breaks, revisions, timeouts, privacy, renderer payloads, exact-version loading, and readiness gates.

## Out of scope

Client-authoritative board logic, permanent clue failure, cross-session ranking, and active promotion before integrated certification are excluded.

## Founder decisions required

Approve or revise the 8-by-8 board, six tile roles, score formula, 50-point lead burst, 90-second duration, tie-break order, and audiovisual direction.
