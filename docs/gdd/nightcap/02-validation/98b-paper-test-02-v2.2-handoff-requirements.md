# Nightcap — Paper Test #2 v2.2 Handoff Requirements

**Status:** TESTING / external-test specification — not game canon  
**Purpose:** Compact source of truth for the already-built external test harness.

## Infrastructure state

The external testing infrastructure already exists:

- GitHub Pages paper-test harness,
- Jotform post-play survey,
- harness/telemetry integration.

This GDD checkpoint does not own or redesign that infrastructure.

## Gate

**Gate 1 — Representative Time-to-Fun / Cohesion** remains ACTIVE.

Memory Support A/B remains blocked until this baseline passes.

## v2.2 selected direction

The v2.2 test should be a **fuller representative slice** so the post-play survey follows a meaningful play experience rather than a thin prototype.

Selected test-specific direction:

- fresh purpose-built microcase,
- working fixture title: **The Last Toast**,
- simple crime with layered proof,
- 4 meaningful suspects,
- 1 real solo tester + 1 visible authored rival with bounded deterministic reactions,
- scene-first observation as the investigation entry,
- 5 major investigation decisions,
- no explicit theory checkpoints during play,
- one short story-wrapped minigame that contests **first access to a newly exposed lead**,
- one minimal-but-real Leverage / information-warfare decision,
- strong story reactivity and fast re-entry,
- short Case File-style commitment before the existing survey,
- target roughly 15–20 minutes of meaningful play for a normal first-time tester, without optimizing to a timer at the expense of completeness.

## Critical experience requirement

Do not repeat the earlier pattern:

**choose option → receive clue card → choose another option**

The test should more closely support:

**observe → choose → discover → wonder → act → consequence → new question**

Not every discovery needs a dramatic world reaction. Relevant information itself can be satisfying when the player chose to pursue it and owns the inference.

## Test-only rival boundary

Authored rival behavior creates competitive pressure for Gate 1 only.

It is **not multiplayer evidence** and must never be used to claim that real two-player or larger-group social play has been validated.

## Do not add yet

- Memory Support A/B,
- Heat / full Counterintel,
- Group Rescue,
- full Case Board UX,
- full production Structured Reconstruction resolution/UX beyond the short representative commitment needed for this test,
- 2-vs-4 balancing,
- full Postmortem generation,
- production AI systems.
