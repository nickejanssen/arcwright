# 0018 - Mini-game Orchestration and Execution Adapters

**Date:** 2026-08-02
**Status:** Accepted
**Decision authority:** Founder approval recorded 2026-08-02
**Supersedes:** docs/decisions/0009-mini-game-runtime-boundary.md
**Architecture references:** docs/architecture/03-arc-execution.md,
docs/architecture/05-session-persistence.md,
docs/architecture/08-event-system.md, docs/architecture/09-developer-api.md,
docs/architecture/10-content-safety.md, docs/architecture/11-telemetry.md,
docs/architecture/13-cost-model.md
**Design reference:**
docs/superpowers/specs/2026-08-02-mini-game-platform-orchestration-design.md

---

# Context

ADR 0009 correctly separated canonical Arcwright session state from browser
presentation, but it made Python authority over timers, scoring, submissions,
and outcomes universal for every mini-game.

That model works for Arcwright-hosted Nightcap web games. It does not provide a
credible path for a developer whose mini-game already runs in Unity, Unreal,
Godot, native code, or a custom engine. Requiring that developer to move
gameplay simulation into Python would make Arcwright a replacement game engine
instead of Layer 2 narrative runtime middleware.

The current static beat binding also cannot naturally represent:

- a game registering multiple mini-games;
- authored story opportunities with eligible candidate pools;
- deterministic selection at runtime;
- a package eligible in more than one opportunity;
- repeatable games such as The Grill;
- external host engines returning typed results; or
- declarative mapping from game results to canonical narrative consequences.

Human arc primacy requires the author to constrain where a mini-game may run
and what its result may change. Surface agnosticism requires Arcwright to avoid
owning renderer technology. Deterministic state requires Arcwright to retain
authority over narrative consequences regardless of where gameplay executes.

# Decision

Arcwright is the narrative gameplay orchestrator. It does not become a
general-purpose mini-game engine.

Games register versioned mini-game packages with Arcwright. Human-authored arcs
declare story opportunities, eligible registrations or capabilities, trigger
and repetition policy, fallback, and declarative consequence mappings.
Arcwright deterministically selects an eligible package from the authored
intersection and creates a canonical invocation.

An opportunity may select by authored priority or by deterministic
session-seeded rotation. Rotation persists its selected registration and
reason, applies an authored recent-candidate lookback within the session, and
never asks AI to choose story placement. Cross-session history is an optional
experience continuity input, not a platform or Nightcap v1 dependency.

Mini-game execution uses one of two adapters:

1. **arcwright_hosted.** Arcwright's Python runtime owns authoritative gameplay
   lifecycle, submissions, timing, mechanic state, scoring, and result
   calculation. Browser clients render authorized state and submit actions.
2. **host_authoritative.** The developer's game engine owns internal gameplay
   state and scoring. Arcwright schedules the invocation and accepts one
   idempotent, versioned, schema-validated result envelope. Arcwright does not
   load or execute arbitrary host gameplay code.

A host-authoritative result is accepted only through a trusted host boundary,
never from a player client as canonical authority. It is bound to the session,
invocation, registration, package version, schema version, status revision,
and one-time result identity. Conflicting duplicates, stale results, and
cross-invocation submissions are rejected and recorded without applying
consequences.

Across both adapters, Arcwright owns:

- opportunity and registration validation;
- deterministic scheduling;
- invocation identity, lifecycle, persistence, and replay record;
- result-envelope validation;
- authored mapping from result semantics to canonical story state;
- knowledge, resource, score, obligation, event, and pacing consequences;
- platform safety for content generated or processed by Arcwright;
- cross-game telemetry and certification evidence.

Experience-owned theme and renderer configuration remains an opaque, validated
payload to the engine. Arcwright may emit surface-neutral presentation posture
and accessibility context, but it does not interpret CSS, screen topology,
engine assets, or renderer implementation.

Invocation state, result acceptance, and consequence application are
recoverable and exactly-once from the append-only event and persistence record.
A resumed invocation uses its immutable registered package version. A retired
version cannot receive new invocations but remains available for valid resume
and replay.

Any Arcwright-generated mini-game content uses the provider-agnostic router,
cost and latency logging, safety layers, and an explicitly allowed public-safe
context projection. It does not receive raw private knowledge state. AI never
selects a game, decides an outcome, grades a deterministic answer, or applies a
canonical consequence.

Mini-game results are facts about gameplay, not direct state patches. An arc
maps allowed result semantics to bounded canonical services. Packages may not
submit arbitrary Python, SQL, or unrestricted session-state mutations.

Current static MiniGameBinding values remain a compatibility path while
registration and opportunity contracts are introduced.

No public marketplace, arbitrary plugin loader, or public third-party platform
is added in Horizon 1. The architecture is proved with Nightcap plus a
synthetic non-Nightcap host-authoritative protocol fixture. Unity, Unreal, and
other engine-specific SDKs, public credentials, multi-tenant package trust, and
commercial developer access remain later approved work.

The Grill runs automatically in its Beat 3 opportunity. A generic request-cost
extension may be represented in contracts, but the optional currency-funded
second run, request UI, transaction behavior, price, refunds, and cross-beat
flow remain deferred per D-097.

# Consequences

## Positive consequences

- External developers keep their game engine and gameplay architecture.
- Arcwright preserves deterministic narrative authority.
- Nightcap reuses the runtime already built under ADR 0009.
- Story authors control eligibility and consequences.
- Repeatable and swappable games no longer require hardcoded beat IDs.
- One result and lifecycle contract works across hosted and external engines.
- Developer tooling can validate story fit, compatibility, and readiness before
  deployment.
- External result authority is constrained by invocation identity, trust,
  replay protection, and bounded consequence mappings.

## Negative consequences

- The platform gains adapter, registration, opportunity, invocation, result,
  and consequence contracts.
- Host-authoritative gameplay cannot be independently simulated by Arcwright
  unless a developer supplies replay evidence or a test adapter.
- Existing specs, authoring guidance, skill instructions, bindings, and
  game-specific transport types need compatibility updates.
- Certification must distinguish contract correctness from subjective gameplay
  quality.
- Package integrity, retirement, recovery, privacy, safety, telemetry, cost,
  and host trust become explicit certification responsibilities.

## Trade-offs

- We accept a broader orchestration contract to avoid owning every developer's
  gameplay runtime.
- We retain a closed hosted mechanic registry instead of loading arbitrary
  executable plugins.
- We defer a public plugin ecosystem while proving the contract internally.
- We require declarative consequence mappings rather than allowing packages to
  mutate canonical state directly.

# References

- docs/prd/01-overview.md
- docs/prd/02-requirements.md
- docs/prd/03-scope.md
- docs/architecture/01-overview.md
- docs/architecture/03-arc-execution.md
- docs/architecture/08-event-system.md
- docs/architecture/09-developer-api.md
- docs/architecture/10-content-safety.md
- docs/architecture/11-telemetry.md
- docs/architecture/13-cost-model.md
- docs/architecture/14-architecture-validation.md
- docs/decisions/0009-mini-game-runtime-boundary.md
- docs/product/decisions-log.csv D-093, D-094, D-095, and D-097
- docs/story-bibles/nightcap-couch-race.md
