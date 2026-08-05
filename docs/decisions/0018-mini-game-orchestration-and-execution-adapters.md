# 0018 - Mini-game Orchestration, Adaptation, and Trust Profiles

**Date:** 2026-08-03
**Status:** Accepted
**Decision authority:** Founder approvals recorded 2026-08-02 and 2026-08-03
**Supersedes:** docs/decisions/0009-mini-game-runtime-boundary.md
**Architecture references:** docs/architecture/03-arc-execution.md,
docs/architecture/05-session-persistence.md,
docs/architecture/08-event-system.md, docs/architecture/09-developer-api.md,
docs/architecture/10-content-safety.md, docs/architecture/11-telemetry.md,
docs/architecture/13-cost-model.md
**Design reference:**
docs/superpowers/specs/2026-08-02-mini-game-platform-orchestration-design.md
**Contract references:** docs/specs/0077-mini-game-registration-and-story-opportunities.md,
docs/specs/0078-mini-game-invocation-and-execution-adapters.md,
docs/specs/0079-mini-game-results-consequences-theme-and-telemetry.md,
docs/specs/0080-mini-game-onboarding-preview-and-certification.md

---

# Context

ADR 0009 correctly separated canonical Arcwright session state from browser
presentation, but it made Python authority over timers, scoring, submissions,
and outcomes universal for every mini-game.

That model works for existing Arcwright-hosted Nightcap web games. It does not
provide a credible path for a developer importing a browser game or using
Unity, Unreal, Godot, native code, or a custom engine. Requiring that developer
to move gameplay simulation into Python would make Arcwright a replacement
game engine instead of Layer 2 narrative runtime middleware.

The first orchestration design also exposed platform internals as developer
work: registration, binding, adapter choice, result mapping, preview fixtures,
and certification. That is architecturally explicit but commercially weak.
Arcwright must retain rigorous internal contracts while making first-time
browser onboarding Playtest-ready in 10 to 15 minutes, 20 minutes maximum.

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

Arcwright is the narrative gameplay orchestrator and adaptation platform. It
does not become a general-purpose replacement for every game engine.

Arcwright imports or scaffolds a reusable, versioned mini-game package and
creates non-destructive destination adaptations. Human-authored arcs declare
composable placement policies, eligible adaptations or capabilities,
delegated authority, recurrence, fallback, and declarative consequence
mappings. Arcwright deterministically selects an eligible adaptation only
inside the authority the designer granted and creates a canonical invocation.

An opportunity may select by authored priority or by deterministic
session-seeded rotation. Rotation persists its selected registration and
reason, applies an authored recent-candidate lookback within the session, and
never asks AI to choose story placement. Cross-session history is an optional
experience continuity input, not a platform or Nightcap v1 dependency.

Hosting, execution, result authority, presentation, and distribution are
independent, versioned capability profiles. They are negotiated for an exact
package and destination adaptation. A profile descriptor cannot load arbitrary
code, bypass safety, or grant itself canonical consequence authority.

Horizon 1 implements these browser profiles:

1. **local browser sandbox.** Arcwright launches an imported game locally for
   analysis and playtest. Its results are visibly non-authoritative and cannot
   mutate production canonical state.
2. **managed browser with transcript validation.** Arcwright hosts the browser
   bundle, records a versioned input transcript, validates it through an
   approved deterministic reducer, and computes the canonical result.
3. **external browser authority.** The developer hosts gameplay and an
   authenticated external backend submits one idempotent, versioned,
   schema-validated result envelope. A browser client is never result
   authority.
4. **legacy hosted mechanic compatibility.** Existing closed Python mechanics
   remain usable while they migrate into reusable packages and destination
   adaptations.

Future registered profiles may support deterministic WebAssembly, signed
replay proofs, certified third-party operators, confidential execution, edge
coordination, native engines, or new surfaces. They must satisfy the permanent
trust invariants without changing placement-policy or consequence contracts.

An externally authoritative result is accepted only through a trusted backend
boundary, never from a player client as canonical authority. The API derives an
internal, non-request principal from verified credentials and canonical
session assignment. Presentation metadata never grants authority. A caller
cannot serialize or supply the internal principal. Every accepted production
result proves producer identity, exact package and adaptation versions, input
provenance, replay or independent verification, permitted consequence classes,
and revocation and audit state. Conflicting duplicates, stale results,
cross-invocation submissions, and invalid proofs are rejected and recorded
without applying consequences.

Across all profiles, Arcwright owns:

- opportunity and registration validation;
- deterministic scheduling;
- invocation identity, lifecycle, persistence, and replay record;
- result-envelope validation;
- authored mapping from result semantics to canonical story state;
- knowledge, resource, score, obligation, event, and pacing consequences;
- platform safety for content generated or processed by Arcwright;
- cross-game telemetry and certification evidence.

Each destination owns an experience design system containing semantic
presentation roles, typography, art direction, motion, audio, copy voice,
surface layouts, accessibility, intensity ranges, and immutable elements. The
Python engine receives only the validated, surface-neutral runtime projection.
Arcwright may generate private draft presentation adaptations only after
permission and cannot promote them without designer approval.

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

No public marketplace or arbitrary plugin loader is added in Horizon 1. The
architecture is proved with the browser golden path, Nightcap, and a synthetic
non-Nightcap browser integration. Unity, Unreal, and other engine-specific
SDKs, public credentials, multi-tenant package trust, and commercial developer
access remain later approved work. Studio, CLI, and SDK must use the same
versioned authoring APIs so future no-code tooling is not a parallel system.

The Grill runs automatically in its Beat 3 opportunity. A generic request-cost
extension may be represented in contracts, but the optional currency-funded
second run, request UI, transaction behavior, price, refunds, and cross-beat
flow remain deferred per D-097.

The Grill product direction is a repeatable interrogation capability that may
eventually be player-requested from any beat. The current contract reserves
`player_request` and a game-owned request-policy reference but keeps execution
disabled until that separate policy is approved. Arcwright does not define or
interpret Nightcap currency, price, deduction, refund, or request UI.

`host_request` is likewise reserved and rejected in this horizon. Neither
request mode becomes executable until a separate approved contract defines
authenticated authority, session and opportunity eligibility, idempotency,
cooldown, denial, audit, and recovery behavior.

The existing `arcwright-minigame` skill, `minigame_tool.py`, package loader,
runtime, resolver, API, SDK, renderer kit, discovery, and stage remain the
single foundation. They are extended into assisted import, reusable-package
analysis, destination adaptation, placement-policy authoring, local preview,
and visual readiness evidence. The developer should not need to understand or
manually operate each internal mechanism during the golden path.

Exact package, adaptation, placement, invocation, authority, and result field
contracts live in specs 0077 through 0079. Profile registration remains closed
and reviewed; capability negotiation is not arbitrary plugin execution. Local
preview is exact-versioned and visibly non-authoritative. Certification never
treats automated checks as device, playtest, or founder evidence.

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
- Browser developers receive a measurable, assisted path to a locally
  Playtest-ready destination adaptation instead of a manual schema workflow.
- New hosting, execution, authority, presentation, and distribution technology
  can register compatible profiles without changing story contracts.

## Negative consequences

- The platform gains package, adaptation, placement-policy, capability-profile,
  invocation, result, and consequence contracts.
- Externally authoritative gameplay cannot be independently simulated by
  Arcwright unless a developer supplies replay evidence or a test profile.
- Existing specs, authoring guidance, skill instructions, bindings, and
  game-specific transport types need compatibility updates.
- Certification must distinguish contract correctness from subjective gameplay
  quality.
- Package integrity, adaptation provenance, retirement, recovery, privacy,
  safety, telemetry, cost, and authority proof become explicit certification
  responsibilities.

## Trade-offs

- We accept a broader internal contract while hiding routine complexity behind
  inference, generation, defaults, and progressive disclosure.
- We retain closed profile registration instead of loading arbitrary executable
  plugins.
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
