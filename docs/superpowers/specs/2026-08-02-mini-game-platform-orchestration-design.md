# Mini-game Platform Orchestration Design

> Current version: v0.3
> Last updated: 2026-08-03
> Status: Founder-approved design, implementation not approved
> Canonical implementation contracts: docs/specs/0077-mini-game-registration-and-story-opportunities.md through docs/specs/0080-mini-game-onboarding-preview-and-certification.md
> Planning artifact: docs/superpowers/specs/2026-08-02-mini-game-platform-orchestration-design.md

## Purpose

Define the platform direction, developer experience, Nightcap integration
path, and work order required to make every existing mini-game game-ready
without turning Arcwright into a general-purpose game engine.

This design replaces two assumptions: that every mini-game must execute inside
Arcwright's Python runtime, and that developers should manually assemble the
platform's registration, binding, adapter, preview, and certification
machinery. Arcwright remains authoritative for narrative orchestration and
canonical story consequences. Developers experience an assisted browser-first
golden path while hosting, execution, result authority, presentation, and
distribution remain independently negotiable platform capabilities.

## Human Collaboration Contract

**Interaction profiles:** Decision interview plus Creative collaboration.

**Classification rationale:** The platform boundary, developer workflow,
story integration model, and deferred currency behavior require founder
judgment. Each Nightcap game's gameplay, tuning, art, animation, and session
fit require creative review and real-device playtesting.

**Current phase:** Approved low-cost architecture and work-order artifact.

**Locked founder direction:**

- The game registers its mini-games with Arcwright.
- Arcwright delivers an eligible mini-game at the best authored story
  opportunity.
- Selection is deterministic and constrained by the human-authored arc.
- The Grill is both Beat 3's title and the player-facing interrogation
  mini-game name, but the beat and mini-game are separate typed objects.
- The Grill runs automatically in Beat 3.
- A future player-requested Grill may occur during any beat, costs
  experience-defined game currency, and permits at most one additional run.
- The currency-funded request flow is contract-ready but feature-deferred
  until the end-to-end Nightcap session works across beats, story, mini-games,
  phone and TV connectivity, and multiplayer state.
- Implementation requires a separate explicit founder approval after the
  plans are reviewed.
- Browser games are the first supported onboarding target. The first-time
  target is 10 to 15 minutes and 20 minutes maximum; returning-user target is
  5 to 10 minutes and 15 minutes maximum.
- The onboarding clock ends when a game is integrated, story-aware, styled,
  simulated, locally testable, and ready for a controlled playtest. Production
  certification is the next explicit gate.
- Managed browser hosting is the default. Bring-your-own browser hosting is an
  advanced path over the same protocol.
- The developer and original game remain authoritative over original source
  and assets. Arcwright creates a non-destructive, versioned adaptation.
  Arcwright-powered adaptation capabilities require the licensed Arcwright
  runtime; Arcwright platform source is not exported.
- Onboarding supports destination-first and reusable-first paths, with
  destination-first recommended for the fastest useful result.
- The game designer controls placement authority. A designer may pin a game
  to an exact moment or beat, delegate a bounded window or candidate pool to
  Arcwright, allow a host or player request, or compose these modes.
- Arcwright may generate private draft code, art, animation, audio, copy, and
  configuration only after asking permission. Generated work is reviewable,
  reversible, and cannot enter production without approval.
- A one-player source game may be adapted into an approved multiplayer form.
  Arcwright recommends one strong participation model and up to two playable
  alternatives for designer review.
- Readiness states are Imported, Reusable, Playtest-ready, and
  Production-ready. Every state and next action must be easy to see and
  understand. Playtest-ready includes one-click local testing;
  Production-ready includes visual evidence and rehearsal tooling.
- Intelligent authoring and deterministic runtime execution are separate
  planes. Only approved, versioned artifacts cross into live execution.
- Hosting, execution, result authority, presentation, and distribution are
  separate negotiated capabilities. Initial browser profiles do not become a
  permanent adapter ceiling.
- The founder approved the original direction on 2026-08-02 and the expanded
  browser-first developer experience and capability architecture on
  2026-08-03.

**Next gate:** Approval of the canonical implementation specs and separate
approval to execute the selected implementation plan. Approval of this
artifact does not approve implementation.

## Executive Recommendation

Arcwright should be the easiest way to turn a playable mechanic into reusable,
story-aware gameplay. It is a narrative gameplay orchestrator and adaptation
platform, not a replacement for every game engine.

The platform should compile a designer-friendly onboarding conversation into
a small, versioned contract that connects:

1. a game-owned mini-game package;
2. a human-authored story opportunity;
3. a deterministic Arcwright scheduler;
4. negotiated hosting, execution, authority, and presentation profiles;
5. a typed result envelope; and
6. a declarative mapping from result semantics to canonical story
   consequences.

This creates a compelling developer proposition:

- Keep the engine, renderer, assets, and gameplay technology you already use.
- Import a browser game and let Arcwright infer the mechanical contract.
- Confirm what the mini-game can do for a story in designer language.
- Let Arcwright adapt player count, presentation, and destination fit without
  overwriting the original.
- Let Arcwright place it only where the human-authored experience allows.
- Receive runtime story context without exposing private or hidden state.
- Return a typed, authority-verified result.
- Let Arcwright apply the authored narrative consequences, persistence,
  telemetry, and downstream pacing effects.

Nightcap proves the managed browser path. Later Unity, Unreal, Godot, native,
edge, spatial, voice, and custom runtimes negotiate compatible profiles
without changing placement policy or canonical consequence contracts.

## Product Boundary

### Arcwright owns

- Arc and beat execution.
- Human-authored opportunity validation.
- Deterministic eligibility and selection.
- Invocation identity, idempotency, lifecycle, pause/resume, and replay record.
- Surface-agnostic lifecycle and consequence events.
- Canonical story state, knowledge assertions, resources, obligations, and
  other narrative consequences.
- Safety enforcement for content generated or processed by Arcwright.
- Cross-game telemetry and certification evidence.
- Import analysis, adaptation generation, managed hosting, local simulation,
  readiness visualization, and licensed adaptation runtime capabilities.

### The game developer owns

- Mini-game rules, internal simulation, controls, and moment-to-moment feel.
- Game-specific scoring and result semantics.
- Renderer implementation, assets, audio, animation, and platform integration.
- Confirmation or correction of inferred package capabilities.
- Declaring how the mini-game can contribute to that game's story.
- Experience-specific runtime configuration and theme implementation.
- Original source, original assets, and authored content supplied to
  Arcwright.

### The human arc author owns

- Story opportunities and their narrative purpose.
- Which registered packages or capability tags are eligible.
- Trigger policy, repetition policy, pacing budget, and fallback.
- Mapping allowed result semantics to authored canonical consequences.
- Whether the opportunity is authored, generative, or hybrid in content.

### Arcwright must not own

- A universal rendering framework for every engine.
- Arbitrary third-party gameplay code execution inside the Python service.
- Unconstrained AI selection of mini-games or consequences.
- Nightcap-specific beat names, currencies, visual surfaces, or scoring terms
  in platform contracts.
- A public marketplace or arbitrary plugin loader during Horizon 1.
- Placement authority the game designer did not explicitly delegate.
- Silent mutation of imported source or silent generation of presentation
  assets.

## SME Architecture Guardrails

The approved direction carries the following platform constraints into every
implementation spec and acceptance suite.

### Capability negotiation and result authority

- Hosting, execution, result authority, presentation, and distribution are
  independent versioned profiles. A profile advertises capabilities and proof
  requirements; it does not authorize arbitrary executable plugins.
- The first profiles are local browser sandbox, managed browser transcript
  validation, and authenticated external browser authority.
- Future profiles may support deterministic WebAssembly, signed replay proofs,
  certified third-party operators, confidential execution, edge coordination,
  native engines, or new surfaces without changing story placement or result
  consequence contracts.
- Every production authority profile proves producer identity, exact package
  and adaptation versions, input provenance, replay or independent
  verification, permitted consequence classes, revocation, audit, and
  rollback.

- A player token or renderer cannot submit a canonical host-authoritative
  result.
- Every accepted result is bound to its session, invocation, registration,
  package version, result schema version, status revision, and one-time result
  identity.
- Duplicate identical delivery is idempotent. A conflicting duplicate, stale
  revision, retired registration, or cross-invocation result is rejected and
  logged without applying consequences.
- Horizon 1 proves this with an internal protocol fixture. Public credentials,
  multi-tenant package signing, and partner trust policy are deferred.
- Local sandbox results are visibly non-authoritative. They may support local
  playtests but cannot mutate production score, currency, clues, winners, or
  canonical story state.

### Recovery and package integrity

- Package definitions used by playtest or active registrations are immutable
  and identified by exact version plus integrity digest.
- Retirement blocks new invocations, not valid resume or replay of an existing
  invocation. Rollback selects a prior approved registration version for new
  work.
- Result receipt and consequence application are independently durable and
  idempotent. A crash between them retries the authored mapping without
  double-applying state.
- Each spec must define whether a host-authoritative invocation resumes,
  cancels, or falls back after host loss. It may not silently start a second
  invocation.

### Privacy, knowledge, and safety

- Runtime story context is an explicit public-safe projection. Raw knowledge
  graph state, private role information, prompts, credentials, and unrelated
  session state are never package input.
- AI-generated mini-game content is resolved only after deterministic
  selection, through the provider-agnostic router and all applicable safety
  layers.
- AI character material still requires the mandatory knowledge query. Case
  callbacks may use only authored or established facts allowed by the arc.
- External result envelopes minimize content. Opaque evidence references are
  diagnostic evidence, not trusted state mutations.

### Surface and theme agnosticism

- The engine forwards an opaque, schema-validated experience theme payload and
  surface-neutral presentation posture. It does not interpret CSS tokens,
  screen names, rendering engines, asset formats, or layout.
- A hosted renderer or external engine translates that payload into its own
  presentation. Presentation cannot affect selection, scoring, or canonical
  consequences.
- Each destination owns an experience design system containing semantic
  presentation roles, typography, art direction, motion, audio, copy voice,
  surface layouts, accessibility, intensity ranges, and immutable elements.
  Generation of incompatible replacements is permission-first and draft-only.

### Telemetry and cost

- Append-only lifecycle telemetry covers opportunity evaluation, selection,
  invocation, completion, timeout, cancellation, result rejection,
  consequence application, fallback, reconnect, duration, adapter, package,
  version, and player count.
- Cross-game telemetry uses reason codes and neutral metrics. Raw private
  content is excluded unless separately consented and enabled.
- Generative content declares cost, latency, retry, cache, and deterministic
  fallback budgets. Every model call uses routing and generation cost logs.
- Certification reports contract and operational evidence but do not replace
  production telemetry.

### Horizon 1 scope

- Build the browser golden path, managed hosting, local preview, initial trust
  profiles, a Nightcap implementation, and one synthetic non-Nightcap browser
  proof.
- Do not build Unity or Unreal SDKs, a marketplace, public package execution,
  external developer authentication, billing, or a no-code arc builder.
- Define all authoring contracts as versioned API resources usable by Studio,
  CLI, and SDK clients so a later no-code builder is a first-class client, not
  a parallel system.
- Before an H2 developer beta, validate the API and schema proposition with the
  target developers required by the PRD non-goals and open-question gates.

## What One Mini-game Per Beat Means

For Couch Race, the six authored beats should each expose at least one
mini-game opportunity. This is an opportunity coverage requirement, not a
one-package-per-beat ceiling. Each opportunity owns a pool of eligible,
certified registrations so additional games can rotate in without changing
engine code or weakening the human-authored story role.

One package may be eligible for multiple opportunities when its authored
repetition policy allows it. The Grill is the first explicit example:

- automatic invocation in the Beat 3 Grill opportunity;
- eventual optional second invocation from any beat;
- maximum two Grill runs per session;
- the optional invocation's currency transaction remains deferred.

This prevents static package IDs from becoming part of the beat model and
lets designers rebalance a session without rewriting engine code.

The initial Couch Race roles and packages are:

| Beat | Authored role | Initial package |
| --- | --- | --- |
| Pour | `social_opener` | Tell Me Something True |
| Scene | `competitive_discovery` | Crime Scene Smash and Scene Sweep rotation |
| Grill | `interrogation` | The Grill |
| Twist | `solo_recontextualization` | Evidence Locker 402 |
| Last Call | `pressure_capstone` | The Interrogation Room |
| Truth | `reveal_reconstruction` | The Unmasking |

Last Call's game opens the convergence sequence. Final interrogation and
Leverage use then settle, guesses lock, and The Truth begins. The Unmasking
implements D-086 by clearing innocent portraits, crediting established catches,
revealing the culprit, reconstructing the case, and handing off to score
animation, ranks, podium, superlatives, and replay. Future certified games may
rotate into either role while preserving these authored transition contracts.

## Core Contracts

### ReusableMiniGamePackage

The reusable package is the destination-neutral mechanic. Arcwright infers a
draft package from an imported browser build or source bundle, then asks the
developer to confirm only unresolved or high-impact facts. The immutable,
versioned package records:

- input and result schemas;
- participation capabilities and supported transformation patterns;
- active and session player-count ranges;
- duration and pacing ranges;
- runtime configuration schema and certified bounds;
- semantic presentation roles and required assets;
- lifecycle, reconnect, fallback, accessibility, and performance behavior;
- story affordances expressed as namespaced, extensible capabilities; and
- provenance, integrity digest, licensing, and readiness evidence.

The package describes what the mechanic can do. It never decides where it
runs or what destination-specific story state it changes.

### DestinationAdaptation

A destination adaptation is a non-destructive, versioned layer over one exact
package version. It records the approved participation model, destination
experience design system mapping, content bindings, configuration defaults,
result semantics, consequence profile, compatible execution profiles, and
certification evidence. The original package remains unchanged.

One package may have many destination adaptations. An adaptation can be
updated without forking the underlying mechanic, and a package update triggers
compatibility analysis rather than silently rewriting its adaptations.

### PlacementPolicy

Placement is a composable policy, not one trigger enum. The policy combines:

- anchors, including exact authored moments, beats, phases, story windows, or
  session-wide eligibility;
- authority grants for designer-required, engine-selected, host-triggered, or
  player-requested invocation;
- deterministic eligibility expressions over public canonical state;
- recurrence, cooldown, limit, and future game-owned cost references;
- exact package, approved pool, weighted rotation, novelty, and fallback
  selection;
- immediate or next-safe-transition timing; and
- bounded result-to-consequence mappings.

The designer may delegate any amount of placement authority, including none.
The policy is a versioned expression tree shared by Studio, CLI, SDK, and
runtime. New policy nodes require schema registration and validation; they do
not require editing every package.

### Capability profiles

The platform negotiates five independent profile families:

1. hosting;
2. execution;
3. result authority;
4. presentation; and
5. distribution.

Horizon 1 registers local browser sandbox, Arcwright-managed browser hosting,
managed deterministic transcript validation, and authenticated external
browser authority. Profile registration is closed and reviewed. Descriptors
cannot load arbitrary code or bypass the permanent trust invariants.

### MiniGameInvocation

Arcwright creates one canonical invocation containing the session, placement
policy evaluation, adaptation, exact package version and digest, selected
capability profiles, deterministic selection reason, public-safe
configuration, status, revision, lifecycle timestamps, authority proof,
result receipt, and consequence application state.

The current mini_game_runs model can evolve into this role for legacy hosted
games. A compatibility translator consumes static MiniGameBinding values
during migration, but new authoring uses packages, adaptations, and placement
policies.

### MiniGameResultEnvelope

The adapter-neutral result contains invocation identity, package and schema
version, completion status, participant or team results, declared semantic
outputs, duration, optional evidence reference, and idempotency key.

Results are facts about the mini-game. They are not direct session-state writes.

### MiniGameConsequenceMapping

The arc maps allowed result semantics to existing canonical services:

- resource and score deltas;
- knowledge assertions or clue variants;
- narrative signals and obligation progress;
- content events;
- pacing-safe follow-up context.

Mappings are declarative, versioned, validated, and bounded. Packages cannot
submit arbitrary Python, database operations, or unrestricted state patches.
Nightcap Leverage is one game-specific resource mapping. The platform contract
uses a generic resource identifier.

### Theme and Presentation Contract

Arcwright forwards validated experience-owned presentation context, not
surface instructions: an opaque theme payload, accessibility preferences,
locale, narrative posture, urgency, attention hints, public-safe story context,
duration, and stakes copy references. The engine understands only the
surface-neutral fields needed for orchestration.

Hosted web renderers consume the experience theme contract. External host
engines translate the same semantics into their own rendering systems.
Presentation adaptation cannot alter rules, scoring, or canonical state.

## Deterministic Selection

Eligible candidates are the intersection of:

1. registrations enabled by the game;
2. candidates allowed by the authored opportunity;
3. package capabilities compatible with player count and adapter;
4. repetition, cooldown, and lifecycle constraints;
5. runtime availability and content readiness; and
6. the opportunity's time and pacing budget.

Selection is deterministic from authored policy and replayable session state.
AI may compose permitted presentation or content only after selection. AI never
chooses the package, trigger, winner, or consequence.

`authored_order` preserves explicit designer priority. For opportunities that
opt into `session_seeded_rotation`, Arcwright orders eligible candidates by a
stable hash of session, opportunity, and registration identity, then excludes
the authored number of most-recent candidates from the current session when an
alternative is eligible. The selected registration and reason are persisted.
No-repeat history across prior sessions is an optional experience continuity
input for later work, not a Nightcap v1 dependency.

If no candidate is eligible, Arcwright executes the authored fallback and
records a non-sensitive reason code.

## Developer Workflow

Retain and upgrade the existing arcwright-minigame skill, helper script,
package template, loader, fixtures, and validation commands. These remain
internal automation and expert escape hatches. They are not the first-time
developer experience.

The first screen asks where the game should be used first. A developer may
select a destination or create a reusable package without one. Destination
selection is recommended because it produces an immediate useful adaptation.

The first-time browser golden path is:

1. Import a static browser bundle or connect a hosted browser build and select
   managed hosting by default.
2. Arcwright launches the game in a private sandbox, analyzes its interaction
   and lifecycle, and generates a draft reusable package.
3. The developer confirms inferred capabilities and destination story intent
   in plain language. Arcwright exposes structured fields only when requested.
4. Arcwright detects participation mismatch and generates one recommended
   multiplayer adaptation plus up to two meaningful alternatives.
5. Arcwright asks permission before generating private draft code, art,
   animation, audio, copy, or destination styling.
6. The designer composes or confirms placement authority and result
   consequences using natural language and visual policy controls.
7. Arcwright runs a deterministic multi-surface story simulation, displays why
   the game was selected, and opens a one-click local playtest.
8. The readiness view reports Playtest-ready or explains the smallest
   concrete action needed.

First-time target is 10 to 15 minutes and 20 minutes maximum. Returning target
is 5 to 10 minutes and 15 minutes maximum. Time is saved through inference,
generated adapters, reusable destination profiles, defaults, and progressive
disclosure, never by removing quality capabilities.

CLI, SDK, and future graphical Studio call the same versioned authoring APIs
and produce the same artifacts. The no-code experience is therefore prepared
from the first contract release rather than reimplemented later.

## Progressive readiness

Every state is always visible in plain language, with current evidence, next
action, blockers, and estimated effort. Status never relies on color alone.

1. **Imported:** Arcwright can launch and analyze the original browser game.
2. **Reusable:** The destination-neutral package has configurable
   participation, presentation, inputs, outputs, and lifecycle behavior.
3. **Playtest-ready:** One destination adaptation has approved participation,
   placement, styling, story consequences, multi-surface behavior, and passing
   local preflight. This is the onboarding time target.
4. **Production-ready:** Automated and human evidence proves the adaptation is
   safe, authoritative, resilient, accessible, performant, and successful in
   its destination.

Playtest-ready includes one-click local launch, hot reload, simulated players,
phone and shared-focus previews, QR codes for local devices, deterministic
fixtures, record and replay, reset, reconnect, timeout, and failure simulation.
No cloud deployment is required.

Production-ready includes a visual gate map, multi-surface timeline, scenario
and player-count matrix, side-by-side version comparison, evidence recordings,
one-click staged rehearsal, and separate display of automated passes and human
approvals.

A destination adaptation is production-ready only when all applicable gates
pass:

- package and registration schemas validate;
- execution adapter works end to end;
- lifecycle, reconnect, timeout, cancellation, and idempotency are verified;
- result semantics and consequence mappings are deterministic;
- story opportunity fit is approved;
- private and public payload boundaries pass;
- runtime configuration works across supported player counts;
- theme, graphics, animation, audio, and accessibility meet the session bar;
- gameplay is tuned through creative review and real-player rehearsal;
- performance budgets pass;
- telemetry and replay evidence are available;
- host trust, package integrity, retirement, and crash recovery pass;
- generative content meets knowledge, safety, cost, latency, and fallback
  budgets when applicable;
- fallback preserves story progress;
- lifecycle is active;
- related specs, plans, roadmap records, GitHub issues, epics, and milestone
  gates agree.

One package may be Production-ready for one destination while another
adaptation remains Playtest-ready. Package existence, schema validation, or
visibility in Nightcap is not readiness evidence by itself.

## Current Couch Race Inventory

At the refreshed 2026-08-03 mainline baseline, the repository has:

- four authored packages, including Scene Sweep from PR #273;
- Scene Sweep backend package, mechanic, and API implementation plus its
  founder-approved design and implementation plan from PRs #273 and #274;
- two legacy bindings across six Couch Race beats;
- no reusable-package plus destination-adaptation onboarding path;
- no measured 10-to-15-minute browser golden path; and
- zero packages with complete per-adaptation Production-ready evidence.

The repository contains four authored packages:

| Package | Current role | Known gap |
| --- | --- | --- |
| crime-scene-smash | Bound to Scene | Prototype renderer and incomplete hosted mechanic |
| evidence-locker-402 | Bound to Twist | Prototype renderer and incomplete hosted mechanic |
| tell-me-something-true | Implemented social truth/bluff path, not bound | Needs migration into generic registration, opportunity, and presentation contracts |
| scene-sweep | Backend implemented, not bound | Needs renderer, reusable-package migration, Nightcap adaptation, local playtest, and certification; should rotate with Crime Scene Smash in Scene |

Additional known work:

- The Grill exists as structured Couch Race interaction infrastructure but is
  not a registered mini-game package.
- AW-289's Interrogation Room trivia has a design brief and prototype reference
  but no production package.
- D-086 defines The Unmasking reveal direction, but no production package or
  reveal-reconstruction mechanic exists.
- Pour, Grill, Last Call, and Truth have no current legacy package binding.
- Scene has two intended candidates, Crime Scene Smash and Scene Sweep, but the
  current static binding cannot express the approved rotation.

Platform-wide blockers that must land before package polish can produce an
end-to-end game:

- Arc progression never calls MiniGameRuntime.create_run or start_run.
- Production code does not drive timeout checks.
- Runtime creation does not enforce package player-count compatibility.
- The bound packages' clue fields do not match the runtime clue-array contract.
- Package discovery skips every authored package because none has
  client/renderer.ts.
- The web mini-game stage does not supply the session ID, token, and API base
  URL required by browser startup.
- Tell Me Something True's web client discards authoritative phase state on
  state fetch, blocking correct reconnect restoration.
- API responses omit the immutable definition version while the web client
  loads latest, so resumed runs can render against a different package version.
- FastAPI and SDK transport contain Tell Me Something True branches and types
  that belong behind a hosted mechanic adapter.
- Runtime finalization stores outcomes but no production path applies generic
  resource, score, or authored story consequences.
- Package discovery hardcodes Nightcap, includes fixtures in normal discovery,
  ignores lifecycle when choosing renderers, and silently skips incomplete
  active packages.

The implementation plans will attach the full audited readiness and test
matrix, including package-specific schema and lifecycle inconsistencies.

## Recommended Work Order

### Phase 0: Reconcile approved design and current mainline

- Amend ADR 0018 and specs 0077 through 0080 from fixed adapters and manual
  onboarding to the approved browser-first adaptation architecture.
- Incorporate PR #273 and PR #274 as the authoritative Scene Sweep baseline.
- Reconcile AW-285, AW-288, AW-289, AW-278, AW-275, AW-286, M5-I, and the
  artifact closeout matrix without reopening completed scope.
- Map every implementation plan to an existing issue or one approved missing
  issue before creating new GitHub work.

### Phase 1: Prove the browser golden path as a vertical slice

- Use Tell Me Something True as the canary because its deterministic mechanic
  is the most complete.
- Import it through the same browser onboarding path an external developer
  will use.
- Generate a reusable package and Nightcap destination adaptation.
- Provide managed local hosting, one-click multi-surface preview, simulated
  players, deterministic fixtures, placement-policy preview, and a visible
  Playtest-ready result.
- Instrument first-time and returning onboarding duration. Do not declare the
  golden path complete without observed 10-to-15-minute and 5-to-10-minute
  usability evidence.

This phase intentionally produces working value before a broad horizontal
platform build. The contract is then hardened from a real integration rather
than designed only from abstractions.

### Phase 2: Generalize the platform from the canary

- Implement reusable package, destination adaptation, placement-policy, result,
  consequence, experience-design-system, and readiness resources.
- Implement capability negotiation for hosting, execution, result authority,
  presentation, and distribution.
- Register local sandbox, managed browser transcript validation, and
  authenticated external browser authority profiles.
- Preserve legacy MiniGameBinding and hosted Python mechanics through explicit
  compatibility translators.
- Add a synthetic non-Nightcap browser game and an independent first-time
  developer walkthrough before claiming platform usability.

### Phase 3: Build the creator and assurance experience

- Extend the existing skill, script, templates, loaders, fixtures, and
  validators rather than duplicating them.
- Add permission-first adaptation generation, multiplayer alternatives,
  destination experience design systems, story simulation, and selection
  explanations.
- Add the always-visible Imported, Reusable, Playtest-ready, and
  Production-ready journey.
- Add the local playtest lab and visual production-readiness lab.
- Expose the same authoring APIs to CLI and SDK so a future graphical Studio
  uses the same resources.

### Phase 4: Make existing packages Playtest-ready

Recommended order after the Tell Me Something True canary:

1. Crime Scene Smash and Scene Sweep as one Scene rotation milestone. Preserve
   the merged Scene Sweep backend and add only its missing renderer,
   adaptation, placement, and readiness work.
2. Evidence Locker 402 to prove selected-player and spectator adaptation.
3. The Grill to package the existing interrogation capability and prove exact
   beat placement plus future repeat and request policy seams.

Each package receives a reusable contract and a Nightcap adaptation. Gameplay,
presentation, tuning, device, and rehearsal evidence remain package-specific.

### Phase 5: Create the missing Last Call and Truth games

1. Complete AW-289's Interrogation Room creative gates and build it as Last
   Call's pressure capstone with simultaneous guesses, reveal handoff, scoring,
   ranks, and podium transition.
2. Reconcile AW-278 with spec 0085 and build The Unmasking as Truth's
   pressure-release and case-reconstruction game.

Neither game is reduced to a static beat binding. Both become reusable
packages with approved Nightcap adaptations and placement policies.

### Phase 6: Integrate and certify Nightcap

- Author six placement policies and candidate pools. Scene initially rotates
  Crime Scene Smash and Scene Sweep.
- Integrate score, knowledge, evidence, Leverage-compatible resources, and
  pacing consequences through generic services.
- Run the complete Couch Race session across phones, shared focus, multiplayer
  state, reconnect, pause/resume, fallbacks, and exact-version replay.
- Complete real-device, real-player, creative, and founder gates per
  adaptation before Production-ready promotion.

### Phase 7: Close the program and validate the platform promise

- Repeat the synthetic non-Nightcap onboarding with a first-time external
  developer and record time, confusion, intervention, and outcome.
- Verify every live result uses an approved authority profile and every
  production consequence is replayable or independently verifiable.
- Reconcile specs, plans, roadmap tasks, GitHub issues, epics, milestones,
  readiness reports, and PR evidence.
- Only after sign-off, reopen the optional currency-funded Grill design.

## Artifact Reconciliation

### Supersede or amend

- docs/decisions/0009-mini-game-runtime-boundary.md: supersede with the
  adapter-aware ADR while retaining hosted runtime rules.
- docs/conventions/mini-game-authoring.md: make adapter-aware.
- docs/skills/arcwright-minigame/SKILL.md and launcher: remove stale build
  claims and add registration, opportunity, adapter, preview, and certification.
- docs/superpowers/plans/2026-08-01-couch-race-tv-and-phone-rendering.md:
  mark Task 8 moved into this work.

### Update status and compatibility notes

- Specs 0046 through 0050: retain as hosted-adapter foundations.
- AW-249 through AW-254 and M4-E: reconcile implementation with stale Markdown.
- AW-262 through AW-265 and M5-F: preserve completed implementation and move
  migration gaps into new plans.
- AW-266 and issue #183: resolve the conflict between D-079's integrated
  rehearsal direction and later text preserving a separate TMST rehearsal.
  Recommended outcome is supersession by integrated Couch Race evidence, but
  no closure occurs without founder confirmation.
- AW-268, AW-275, and M5-G: apply semantic theme and motion completion evidence
  to every active mini-game.
- AW-285 and issue #239: record that PR #269 delivered only the structural
  shared-display slice.
- AW-286 and M5-I: depend on game-ready opportunity coverage and end-to-end
  certification, not static bindings alone.
- AW-288: remove D-095-moved scope and redefine or supersede it.
- AW-289 and issue #258: preserve its creative brief and align its production
  package with the new contracts.
- M5, M6, and qualifying-session gates: update only with real exit evidence.

### Create after approval

- One canonical spec per implementation subsystem.
- One implementation plan per independently executable subsystem.
- GitHub issues only for missing approved work.
- A machine-readable readiness report for each package.

### Close only with evidence

- A game issue closes only when its game-ready gates pass.
- An epic closes only when all children and exit criteria pass.
- A milestone closes only when its canonical exit gate passes.
- A merged partial PR does not close unfinished acceptance criteria.

## Pre-execution Mainline Safety Gate

Immediately before any implementation plan begins:

1. fetch and prune GitHub refs;
2. list all PRs merged since the plan baseline;
3. inspect changed files for overlap;
4. verify the branch or worktree starts from current origin/main;
5. rebase or recreate it if main advanced;
6. confirm a clean worktree and preserve unrelated local changes;
7. run the plan's baseline tests;
8. report changed assumptions or conflicts;
9. obtain separate explicit founder implementation approval.

Refreshed planning baseline for this artifact:

- origin/main: d26d7b8dee2aafa59ef6a0fd985da5bea771dbf1
- Includes PR #273 and PR #274 for Scene Sweep, plus PR #269 and PR #268.
- PR #271's inline-script tests were reverted by PR #272 and are absent.
- Issue #270 remains blocked on restored CI coverage.
- The planning worktree is intentionally not rebased while its approved draft
  amendments are uncommitted. Every implementation worktree must be created
  from the then-current origin/main after a fresh merged-PR audit.

## Planning Acceptance Criteria

- [x] Founder approves this architecture direction.
- [x] ADR 0018 is accepted before contract implementation.
- [x] Browser-first golden path, adaptation ownership, progressive readiness,
  placement-policy composition, and capability-negotiated trust are approved.
- [ ] Every implementation plan references one canonical approved spec.
- [ ] Every plan includes the mainline safety gate.
- [ ] Every plan includes a separate founder implementation-approval gate.
- [ ] Every plan includes final local and GitHub status reconciliation.
- [ ] No plan duplicates completed AW-249 through AW-265 work.
- [ ] A synthetic non-Nightcap validation exists before platform-agnostic
  claims.
- [ ] All existing Nightcap mini-games have individual game-ready plans.
- [ ] Currency-funded player-requested Grill remains deferred per D-097.

## Known Risks

- Static beat bindings cannot express repeatable or player-requested runs.
- ADR 0009 overstates universal Python ownership of internal simulation.
- The closed Python mechanic registry cannot serve external game engines
  without an adapter.
- Prototypes may appear playable while bypassing production runtime paths.
- Game-specific API and SDK types can leak Nightcap mechanics into platform
  contracts.
- Reverted PR #271 leaves a known inline-script integration risk.
- Visual quality and tuning require creative collaboration and real humans.

## Remaining Decision Gates

The architecture and work order are approved. Canonical specs, Nightcap
placement, each game's creative artifact, the AW-266 disposition, and the
selected implementation plan still require their named approvals. No
implementation begins from this planning approval.
