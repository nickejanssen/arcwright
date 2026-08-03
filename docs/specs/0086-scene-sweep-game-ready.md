> Current version: v0.1
> Last updated: 2026-08-03
> Status: Draft
> Canonical path: docs/specs/0086-scene-sweep-game-ready.md

# Scene Sweep Game-ready Contract

## References

- Platform contracts: `docs/specs/0077-mini-game-registration-and-story-opportunities.md` through `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`
- Founder-approved design: `docs/superpowers/specs/2026-08-02-nightcap-scene-sweep-mini-game-design.md`
- Merged backend plan: `docs/superpowers/plans/2026-08-02-scene-sweep-engine-and-api.md`
- Merged implementation: PR #273 and PR #274
- Story: `docs/story-bibles/nightcap-couch-race.md`

## Overview and gate

Scene Sweep is the hidden-object evidence-search race implemented on main by PR
#273. This spec does not redesign or rebuild that merged backend. It defines the
remaining work to turn the implementation into a reusable package and a
Playtest-ready, then Production-ready, Nightcap adaptation that rotates with
Crime Scene Smash during Scene.

## Human collaboration contract

**Profiles:** Creative collaboration and facilitated live operation.

The existing mechanic direction is founder-approved. The founder must approve
the 2-to-3-player participation adaptation, destination presentation artifact,
gameplay calibration, real-device evidence, real-player evidence, and
production promotion.

## Preserved merged behavior

The package preserves race-to-claim, one hidden real object, end-of-round truth
reveal, no early ending when the real object is claimed, deterministic claim
arbitration, authored delayed-clue fallback, player-count-scaled object count,
and the three-layer background, object, and flavor art strategy.

Merged backend code and tests are the baseline. Follow-on work may refactor
mechanic-specific API projections behind the generic invocation boundary only
after characterization tests prove behavior is unchanged.

## Reusable package and Nightcap adaptation

The reusable package declares evidence-search, individual-race,
shared-spectacle, staged-reveal, and deterministic-fallback affordances without
Nightcap beat or clue names.

The Nightcap adaptation provides:

- one approved 2-to-3-player participation model generated and reviewed under
  spec 0080, while preserving the approved 4-to-8-player race;
- the Nightcap experience design system mapping for backgrounds, archetype
  objects, claims, countdown, reveal, sound, captions, and reduced motion;
- typed results for finder, claims, decoys, completion, timeout, and fallback;
- bounded evidence, score, and Leverage-compatible consequence mappings;
- a local multi-surface renderer for player, shared-focus, and host roles; and
- exact-version Playtest-ready and Production-ready reports.

The imported and merged package remains unchanged. Destination-specific work
is recorded as a versioned adaptation.

## Placement policy

Scene Sweep and Crime Scene Smash are the initial candidates in Couch Race's
Scene discovery pool. The policy delegates deterministic selection within that
approved pool, uses session lookback to avoid immediate repetition when an
alternative is eligible, and preserves an authored fallback. Neither package
is hardcoded into arc execution or TypeScript.

## Local and production testing

Playtest-ready must launch from the local lab with simulated players, phone and
shared-focus previews, real-device QR join, concurrent claim arbitration,
success, timeout, fallback, reconnect, reset, and deterministic replay.

Production-ready must visualize player-count coverage, viewport performance,
asset budgets, privacy, authoritative claim ordering, selection rotation,
fallback, accessibility, motion, audio, and real-player evidence. The visual
lab must show which checks are automated and which require human approval.

## Acceptance criteria

- [ ] PR #273 behavior remains characterized and no merged backend work is
  duplicated.
- [ ] Scene Sweep exists as a destination-neutral reusable package and an
  independently versioned Nightcap adaptation.
- [ ] An approved participation model supports Couch Race sessions from 2
  through 8 players.
- [ ] Phone, shared-focus, and host renderers pass privacy, accessibility,
  performance, reconnect, audio, and reduced-motion checks.
- [ ] Local Playtest-ready testing requires no cloud deployment.
- [ ] Scene rotates Crime Scene Smash and Scene Sweep deterministically without
  engine or renderer changes.
- [ ] A browser or player result cannot claim canonical finder, score, or clue
  authority.
- [ ] Real-device and real-player evidence validates search clarity, race
  fairness, shared spectacle, reveal satisfaction, story return, and replay
  desire.
- [ ] Founder approves the adaptation before Production-ready promotion.

## Tests

Tests preserve the merged plugin and API behavior, then cover reusable-package
validation, 2-to-8-player adaptation, generic transport, exact-version loading,
private and shared projections, concurrent claims, success and fallback,
renderer behavior, local lab fixtures, Scene rotation, readiness evidence, and
rollback.

## Founder decisions required

Approve one generated 2-to-3-player participation adaptation, destination
presentation artifact, tuning evidence, and production promotion. The merged
4-to-8-player mechanic direction is not reopened by this spec.
