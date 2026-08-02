# Mini-game Platform Orchestration Design

> Current version: v0.2
> Last updated: 2026-08-02
> Status: Approved direction, implementation not approved
> Canonical implementation contracts: to be split into approved specs before implementation
> Planning artifact: docs/superpowers/specs/2026-08-02-mini-game-platform-orchestration-design.md

## Purpose

Define the platform direction, developer experience, Nightcap integration
path, and work order required to make every existing mini-game game-ready
without turning Arcwright into a general-purpose game engine.

This design replaces the assumption that every mini-game must execute inside
Arcwright's Python runtime. Arcwright remains authoritative for narrative
orchestration and canonical story consequences. Mini-game execution authority
varies by an explicit adapter contract.

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
- The founder approved this architecture and planning direction on 2026-08-02.

**Next gate:** Approval of the canonical implementation specs and separate
approval to execute the selected implementation plan. Approval of this
artifact does not approve implementation.

## Executive Recommendation

Arcwright should be a narrative gameplay orchestrator, not a universal
mini-game engine.

The platform should expose a small, versioned contract that connects:

1. a game-owned mini-game package;
2. a human-authored story opportunity;
3. a deterministic Arcwright scheduler;
4. an execution adapter;
5. a typed result envelope; and
6. a declarative mapping from result semantics to canonical story
   consequences.

This creates a compelling developer proposition:

- Keep the engine, renderer, assets, and gameplay technology you already use.
- Tell Arcwright what the mini-game can do for a story.
- Let Arcwright place it only where the human-authored experience allows.
- Receive runtime story context without exposing private or hidden state.
- Return a typed result.
- Let Arcwright apply the authored narrative consequences, persistence,
  telemetry, and downstream pacing effects.

Nightcap uses an Arcwright-hosted web adapter. Unity, Unreal, Godot, native,
or custom games can use a host-authoritative adapter without moving their
gameplay simulation into Python.

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

### The game developer owns

- Mini-game rules, internal simulation, controls, and moment-to-moment feel.
- Game-specific scoring and result semantics.
- Renderer implementation, assets, audio, animation, and platform integration.
- Registration of package capabilities and supported execution adapters.
- Declaring how the mini-game can contribute to that game's story.
- Experience-specific runtime configuration and theme implementation.

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

## SME Architecture Guardrails

The approved direction carries the following platform constraints into every
implementation spec and acceptance suite.

### Host trust and result authority

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

- Build internal contracts, a Nightcap implementation, and one synthetic
  non-Nightcap protocol proof.
- Do not build Unity or Unreal SDKs, a marketplace, public package execution,
  external developer authentication, billing, or a no-code arc builder.
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
| Scene | `competitive_discovery` | Crime Scene Smash |
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

### MiniGamePackageManifest

Extend the current manifest with versioned input and result schemas, supported
execution adapters, capability and story-role tags, participation and
player-count capabilities, time budget, runtime configuration schema,
presentation declarations, assets, fallback, compatibility, and certification
metadata.

The package declares capabilities. It does not decide where it runs.

### MiniGameRegistration

The experience registers a package version for use in that game. Registration
contains an experience-scoped ID, package and version, enabled adapter,
configuration defaults, allowed story roles, theme and localization bindings,
result semantic vocabulary, optional request-policy extension fields, and
compatibility constraints.

Registration is explicit and version-pinned. Installing a package does not
authorize its use in an arc.

### MiniGameOpportunity

The human-authored arc declares a story opportunity containing:

- stable opportunity ID and graph position;
- narrative role, such as opener, discovery, pressure, release, or finale;
- eligible registration IDs and/or capability tags;
- trigger mode;
- deterministic selection policy and recent-candidate lookback;
- invocation count, cooldown, and repetition policy;
- time and pacing budget;
- public-safe context fields;
- fallback behavior;
- consequence mapping profile;
- presentation posture and attention target.

The current BeatDefinition.mini_games binding list becomes a compatibility
input to this richer opportunity contract.

### MiniGameInvocation

Arcwright creates one canonical invocation containing the session,
opportunity, registration, package version, deterministic selection reason,
adapter, public-safe configuration, status, revision, lifecycle timestamps,
result receipt, and consequence application state.

The current mini_game_runs model can evolve into this role for hosted games.

### MiniGameExecutionAdapter

Two adapters are required.

#### arcwright_hosted

For Nightcap web mini-games and packages that choose Arcwright hosting:

- Python owns authoritative gameplay lifecycle, submissions, mechanic state,
  timing, and result calculation.
- Existing runtime, persistence, API, SDK, and event work is reused.
- Mechanic implementations remain closed and explicitly registered.
- Browser clients render authorized state and submit actions.

#### host_authoritative

For Unity, Unreal, Godot, native, or custom engines:

- Arcwright creates and schedules the invocation.
- The host engine launches and runs the mini-game.
- The host owns internal gameplay state and scoring.
- The host returns one idempotent, schema-validated result envelope.
- Arcwright validates identity, version, lifecycle, and result shape, then
  applies only the authored consequence mapping.
- Arcwright never loads or executes arbitrary host gameplay code.

Both adapters emit the same platform lifecycle and consequence events.

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
package template, loader, fixtures, and validation commands.

The target flow is:

1. Intake or import a concept or prototype.
2. Scaffold a standard package.
3. Implement an Arcwright-hosted or host-authoritative adapter.
4. Register the versioned package with the experience.
5. Author a story opportunity in the arc.
6. Map result semantics to narrative consequences.
7. Bind theme, motion, asset, accessibility, and localization contracts.
8. Validate schema, privacy, safety, compatibility, and lifecycle.
9. Preview deterministic selection and surface or host payloads.
10. Rehearse headless, reconnect, multiplayer, and real-device paths.
11. Produce a machine-readable certification report.
12. Promote lifecycle metadata only after all gates pass.

This is the developer value: Arcwright handles story placement, session
orchestration, narrative consequence, persistence, safety boundaries, and
diagnostics while preserving the developer's engine and creative ownership.

## Game-ready Definition

A mini-game is game-ready only when all applicable gates pass:

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

Package existence, schema validation, or visibility in Nightcap is not
game-ready evidence by itself.

## Current Couch Race Inventory

At the verified baseline, the repository has:

- three authored packages;
- two active catalog entries;
- two bindings across six Couch Race beats;
- one implemented deterministic mechanic;
- zero production package renderers; and
- zero game-ready packages.

The repository contains three authored packages:

| Package | Current role | Known gap |
| --- | --- | --- |
| crime-scene-smash | Bound to Scene | Prototype renderer and incomplete hosted mechanic |
| evidence-locker-402 | Bound to Twist | Prototype renderer and incomplete hosted mechanic |
| tell-me-something-true | Implemented social truth/bluff path, not bound | Needs migration into generic registration, opportunity, and presentation contracts |

Additional known work:

- The Grill exists as structured Couch Race interaction infrastructure but is
  not a registered mini-game package.
- AW-289's Interrogation Room trivia has a design brief and prototype reference
  but no production package.
- D-086 defines The Unmasking reveal direction, but no production package or
  reveal-reconstruction mechanic exists.
- Pour, Grill, Last Call, and Truth have no current static package binding.

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

### Phase 0: Reconcile authority and trackers

- Accept the superseding ADR.
- Update canonical architecture references.
- Record D-097.
- Correct AW-285's partial-merge status without treating its full original
  acceptance criteria as complete.
- Reconcile AW-288 and AW-289 so no work is duplicated.
- Create or update one GitHub issue per approved implementation plan.

### Phase 1: Contract and compatibility layer

- Add registration, opportunity, invocation, adapter, result, consequence,
  and theme contracts.
- Preserve compatibility for current static bindings.
- Add contract tests with a synthetic non-Nightcap experience and a fake
  host-authoritative adapter.
- Specify trusted host result submission, package integrity, retirement,
  recovery, privacy, safety, telemetry, and generation budgets.
- Do not expose a public marketplace or third-party code loader.

### Phase 2: Orchestrator and adapters

- Implement deterministic opportunity selection.
- Implement the shared invocation lifecycle.
- Adapt the current Python runtime as arcwright_hosted.
- Add the host-authoritative protocol.
- Add result validation and declarative consequence application.

### Phase 3: Onboarding and certification

- Upgrade the existing skill, script, templates, validators, and fixtures.
- Add registration and opportunity scaffolding.
- Add preview, deterministic simulation, compatibility checks, and readiness
  reports.
- Add trust-boundary, digest, retirement, cost, telemetry, and public-safe
  context checks.
- Document the complete internal developer path.

### Phase 4: Make each package a certified playtest candidate

Recommended order:

1. Tell Me Something True as the migration canary because its deterministic
   mechanic path is the most complete.
2. Crime Scene Smash to complete the competitive real-time hosted path.
3. Evidence Locker 402 to complete the individual puzzle path.
4. The Grill to package the interrogation loop and verify story-native,
   repeatable gameplay.
5. Interrogation Room trivia after its separate creative brief and content
   approval gates.
6. The Unmasking after its reveal-reconstruction sequence and presentation
   artifact are approved.

Each game gets its own gameplay, presentation, tuning, and rehearsal plan.
Package-only certification leaves registration and whole-session gates marked
as integration pending.

### Phase 5: Nightcap foundation

- Register exact certified playtest package versions and digests.
- Author six rotating beat-opportunity pools with the roles above.
- Integrate Leverage and race-score consequences through generic services.
- Implement Nightcap's theme and presentation contract.
- Preserve the deferred request-cost extension without building it.

### Phase 6: End-to-end certification and closeout

- Run the six-opportunity Couch Race session across phones, shared display,
  multiplayer state, reconnect, pause/resume, and fallbacks.
- Run the synthetic non-Nightcap host-authoritative reference.
- Complete real-device and real-player rehearsal gates.
- Promote only fully passing package versions from playtest to active.
- Reconcile every related local and GitHub status artifact.
- Only after this phase, reopen the optional currency-funded Grill design.

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

Baseline for this artifact:

- origin/main: 52562723d5dd6374817e1299f8faf98ecd5dd120
- Includes PR #269 and PR #268.
- PR #271's inline-script tests were reverted by PR #272 and are absent.
- Issue #270 remains blocked on restored CI coverage.

## Planning Acceptance Criteria

- [x] Founder approves this architecture direction.
- [x] ADR 0018 is accepted before contract implementation.
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
