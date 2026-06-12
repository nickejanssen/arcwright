# Bundle B architecture specs
Generated: 2026-06-12

Manifest:
- docs/07-Technical-Architecture-v1 3 35db7de354a881618e59e65c8e12caf6.md
- docs/architecture/01-overview.md
- docs/architecture/02-technology-stack.md
- docs/architecture/03-arc-execution.md
- docs/architecture/04-knowledge-graph.md
- docs/architecture/05-session-persistence.md
- docs/architecture/06-model-routing.md
- docs/architecture/07-character-behavior.md
- docs/architecture/08-event-system.md
- docs/architecture/09-developer-api.md
- docs/architecture/10-content-safety.md
- docs/architecture/11-telemetry.md
- docs/architecture/12-build-plan.md
- docs/architecture/13-cost-model.md
- docs/architecture/14-architecture-validation.md
- docs/architecture/15-development-guide.md
- docs/architecture/README.md
- docs/architecture/supplemental-schemas.md
- docs/conventions/ai-contributions.md
- docs/conventions/ai-cost-policy.md
- docs/conventions/coding-style.md
- docs/conventions/README.md
- docs/conventions/review-checklist.md
- docs/conventions/setup.md
- docs/conventions/testing.md
- docs/decisions/0000-template.md
- docs/decisions/0001-scaffolding-audit.md
- docs/decisions/0002-harness-scenario-execution-contract.md
- docs/decisions/0003-nightcap-web-experience-runtime.md
- docs/decisions/0004-pacing-telemetry-outcome-events.md
- docs/decisions/0005-l1-hard-stop-boundary.md
- docs/decisions/README.md
- docs/roadmap/epics/M1-A-scaffolding-and-infrastructure.md
- docs/roadmap/epics/M1-B-data-model.md
- docs/roadmap/epics/M1-C-knowledge-graph-core.md
- docs/roadmap/epics/M1-D-model-routing-abstraction.md
- docs/roadmap/epics/M1-E-harness-scaffold.md
- docs/roadmap/epics/M2-A-external-platform-decision-gate.md
- docs/roadmap/epics/M2-B-arc-execution-engine.md
- docs/roadmap/epics/M2-C-nightcap-arc-runtime.md
- docs/roadmap/epics/M2-D-content-safety-pipeline.md
- docs/roadmap/epics/M2-E-character-behavior-engine.md
- docs/roadmap/epics/M3-A-content-event-system.md
- docs/roadmap/epics/M3-B-api-auth-and-typescript-sdk.md
- docs/roadmap/epics/M3-C-session-persistence-and-resume.md
- docs/roadmap/epics/M3-D-telemetry-and-full-simulation-harness.md
- docs/roadmap/epics/M4-A-nightcap-external-platform-integration.md
- docs/roadmap/epics/M4-B-nightcap-host-and-shared-display-experience.md
- docs/roadmap/epics/M4-C-nightcap-player-device-experience.md
- docs/roadmap/epics/M4-D-real-device-privacy-and-join-validation.md
- docs/roadmap/epics/M5-A-adversarial-safety-and-remediation.md
- docs/roadmap/epics/M5-B-cost-usage-and-gross-margin.md
- docs/roadmap/epics/M5-C-second-arc-schema-validation.md
- docs/roadmap/epics/M5-D-visual-storyworld-phase-1-inspection.md
- docs/roadmap/epics/M6-A-playtest-operations.md
- docs/roadmap/epics/M6-B-qualifying-session-execution.md
- docs/roadmap/epics/M6-C-h1-proof-analysis.md
- docs/roadmap/operations/github-project-setup.md
- docs/roadmap/operations/working-model.md
- docs/roadmap/tasks/AW-101-repository-structure-and-python-project-setup.md
- docs/roadmap/tasks/AW-102-local-postgres-pgvector-alembic-init.md
- docs/roadmap/tasks/AW-103-sqlalchemy-models-for-all-platform-tables.md
- docs/roadmap/tasks/AW-104-first-full-alembic-migration.md
- docs/roadmap/tasks/AW-105-knowledge-graph-assertion-api.md
- docs/roadmap/tasks/AW-106-pre-generation-knowledge-constraint-hook.md
- docs/roadmap/tasks/AW-107-litellm-routing-layer.md
- docs/roadmap/tasks/AW-108-prompt-caching-and-generation-logging.md
- docs/roadmap/tasks/AW-110-simulation-harness-skeleton.md
- docs/roadmap/tasks/AW-111-scripted-synthetic-player-driver.md
- docs/roadmap/tasks/AW-112-deterministic-replay-and-batch-runner.md
- docs/roadmap/tasks/AW-201-m2-m6-roadmap-and-tracker-bootstrap.md
- docs/roadmap/tasks/AW-202-external-nightcap-platform-decision.md
- docs/roadmap/tasks/AW-203-arcdefinition-schema-and-validation-core.md
- docs/roadmap/tasks/AW-204-dynamic-arcstatechart-generation.md
- docs/roadmap/tasks/AW-205-nightcap-canonical-arc-json.md
- docs/roadmap/tasks/AW-206-killer-assignment-and-reveal-state.md
- docs/roadmap/tasks/AW-207-dramatic-tension-pacing-engine.md
- docs/roadmap/tasks/AW-208-l1-hard-stops.md
- docs/roadmap/tasks/AW-209-l2-pre-generation-classification.md
- docs/roadmap/tasks/AW-210-l3-policy-injection-and-neutral-bridge.md
- docs/roadmap/tasks/AW-211-behavior-profile-assembly.md
- docs/roadmap/tasks/AW-212-knowledge-constrained-dialogue-pipeline.md
- docs/roadmap/tasks/AW-213-ai-initiative-and-npc-npc-exchange.md
- docs/roadmap/tasks/AW-214-m2-headless-nightcap-exit-harness.md
- docs/roadmap/tasks/AW-215-contentevent-model-and-in-memory-bus.md
- docs/roadmap/tasks/AW-216-sse-fanout-filtering-and-replay.md
- docs/roadmap/tasks/AW-217-session-lifecycle-api-and-auth.md
- docs/roadmap/tasks/AW-218-character-input-and-knowledge-endpoints.md
- docs/roadmap/tasks/AW-219-typescript-sdk-event-and-input-client.md
- docs/roadmap/tasks/AW-220-session-persistence-snapshots-and-resume.md
- docs/roadmap/tasks/AW-221-narrator-bridge-on-resume.md
- docs/roadmap/tasks/AW-222-five-mvp-telemetry-signals.md
- docs/roadmap/tasks/AW-223-cost-and-usage-summary.md
- docs/roadmap/tasks/AW-224-full-api-batch-harness.md
- docs/roadmap/tasks/AW-225-external-platform-connector-scaffold.md
- docs/roadmap/tasks/AW-226-host-session-creation-and-shared-display-flow.md
- docs/roadmap/tasks/AW-227-shared-display-narrator-and-group-event-rendering.md
- docs/roadmap/tasks/AW-228-player-join-flow-under-30-seconds.md
- docs/roadmap/tasks/AW-229-player-private-event-and-input-flow.md
- docs/roadmap/tasks/AW-230-real-device-privacy-matrix.md
- docs/roadmap/tasks/AW-231-m4-real-human-rehearsal.md
- docs/roadmap/tasks/AW-232-adversarial-safety-playtest-protocol.md
- docs/roadmap/tasks/AW-233-safety-findings-remediation.md
- docs/roadmap/tasks/AW-234-gross-margin-by-player-count.md
- docs/roadmap/tasks/AW-235-second-arc-schema-design.md
- docs/roadmap/tasks/AW-236-live-knowledge-graph-inspection.md
- docs/roadmap/tasks/AW-237-read-only-arc-structure-inspection.md
- docs/roadmap/tasks/AW-238-live-event-stream-inspection.md
- docs/roadmap/tasks/AW-239-character-state-inspection.md
- docs/roadmap/tasks/AW-240-closed-playtest-operations-runbook.md
- docs/roadmap/tasks/AW-241-qualifying-session-instrumentation-checklist.md
- docs/roadmap/tasks/AW-242-founder-run-final-rehearsal.md
- docs/roadmap/tasks/AW-243-five-outside-qualifying-sessions.md
- docs/roadmap/tasks/AW-244-h1-proof-analysis-and-next-step-decision.md
- docs/specs/0000-template.md
- docs/specs/0001-review-checklist-convention.md
- docs/specs/0002-pre-commit-hook-setup.md
- docs/specs/0003-ci-and-codeql-workflows.md
- docs/specs/0004-initial-eval-harness.md
- docs/specs/0005-scaffolding-remediation.md
- docs/specs/0006-roadmap-organization.md
- docs/specs/0007-roadmap-tracker-alignment.md
- docs/specs/0008-github-tracker-reproducibility.md
- docs/specs/0009-aw-101-repository-structure-and-python-project-setup.md
- docs/specs/0010-aw-102-local-postgres-pgvector-alembic-init.md
- docs/specs/0011-aw-103-sqlalchemy-orm-models.md
- docs/specs/0012-aw-104-first-full-alembic-migration.md
- docs/specs/0013-aw-106-pre-generation-knowledge-constraint-hook.md
- docs/specs/0014-aw-107-litellm-routing-layer.md
- docs/specs/0015-aw-110-headless-session-runner-core.md
- docs/specs/0016-aw-111-scripted-synthetic-player-driver.md
- docs/specs/0017-aw-112-deterministic-replay-and-batch-runner.md
- docs/specs/0018-github-task-implementer-skill.md
- docs/specs/0019-multi-agent-operating-model.md
- docs/specs/0020-aw-201-m2-m6-roadmap-and-tracker-bootstrap.md
- docs/specs/0021-operating-model-business-and-architect-roles.md
- docs/specs/0022-aw-202-nightcap-web-experience-runtime-decision.md
- docs/specs/0023-aw-203-arcdefinition-schema-validation-core.md
- docs/specs/0024-aw-204-dynamic-arcstatechart-generation.md
- docs/specs/0025-aw-205-nightcap-canonical-arc-json.md
- docs/specs/0026-aw-206-killer-assignment-and-reveal-state.md
- docs/specs/0027-aw-207-dramatic-tension-pacing-engine.md
- docs/specs/0028-aw-208-l1-hard-stops.md
- docs/specs/README.md

---
## SOURCE FILE: docs/07-Technical-Architecture-v1 3 35db7de354a881618e59e65c8e12caf6.md

# 07-Technical-Architecture-v1.3

**Version:** 1.3

**Date:** May 2026

**Status:** Draft — v1.3 Chat 9 platform-as-product integration applied via Notion connector (May 2026)

**Produced in:** Chat 6b (v1.0), Chat 7 pre-work (v1.1), Chat 7 Story Bible (v1.2)

**Changes from v1.2 (Chat 9 Platform-as-Product Strategy):**

- Applied platform-clean schema naming principle: schema names describe structure and game-specific semantics move into configuration.
- Confirmed schema renames: bonded_creatures to bonded_entities; home_base_location to player_anchor_location; career_path to player_role_arc; active_party to current_companion_entities; agency_vs_fate to event_authorship; witnessing_creature_ids to witness_entity_ids; pact_term to current_intent.
- Reaffirmed build path: platform-clean from day one, while external developer exposure remains gated separately from internal abstraction discipline.
- Added MVP scope pattern: schema-clean from day one, implementation-staged across Nightcap MVP and Monster RPG H2.
- Added Visual Storyworld Phase 1 inspection surfaces as part of H1 dashboard architecture.
- Clarified SDK architecture: REST API is canonical, OpenAPI is source of truth, TypeScript web SDK is auto-generated, and engine SDKs are separate native-language wrappers.

**Changes from v1.1 (Chat 7 Story Bible):**

- `arc_structure` field value changed from `"dan_harmon"` to `"story_circle"`. Story Circle is now a platform-native 8-beat template. `arc_structure` is no longer decorative metadata; it is a functional engine input that scaffolds beat definitions and populates structural intent fields.
- `BeatDefinition` schema expanded with seven new fields: `story_circle_step` (int or array, maps beat to Story Circle position), `structural_function` (structured platform tag, pre-populated for Story Circle arcs), `dramatic_purpose` (free-text director's note, required for custom arcs), `emotional_target` (target player emotional state), `information_goal` (what players should know by beat's end), `tension_target` (float 0-1, pacing engine target for this beat), `character_emphasis` (list of character slot IDs foregrounded in this beat).
- `aesthetic_mode` field replaced by `aesthetic_config` object with per-element generation strategies. See updated arc schema below.
- `tone_config` added to arc definition: `brand_envelope` (min/max per tone dimension), `scenario_defaults` (dial positions per scenario), `voice_directive` (free-text brand voice synthesis). Tone is authored per arc, not host-selectable.
- `killer_assignment_logic` added as a distinct engine component: behavioral signal tracking, candidate evaluation pool, interaction-triggered acceleration. Assignment fires independently of revelation.
- `revelation_step_range: [2, 4]` added to arc definition. Killer assignment and killer revelation are now two distinct events.
- `participant_type: ai_controlled` added to session participant model for NPC player slots.
- `standing_score` per player and `accusation_token_used` boolean added to session state.
- `victim_config` added to arc definition: `eligibility_mode` (npc_only / player_eligible by player count threshold), `designation_trigger: "killer_revelation"`, `victim_role_pool` (Witness, Specter, Informant, Conspirator).
- `additional_kill_config` added: available in 6-slot sessions, proportionality-governed, dynamically expandable under specific story conditions.
- `mini_game` added as a content type deliverable within beats 1-3. Supports phone-only and phone-plus-screen delivery. Mini-game outputs are named inputs to `killer_assignment_logic`.
- `murder_timing_range: [1, 3]` added to arc definition. Murder occurs within this beat range, not at a fixed point.
- `session_duration_range: [30, 75]` replaces any session_mode concept. Duration is emergent from player behavior and pacing engine response, not a designed configuration.
- Role types are now first-class platform objects in an extensible library. Arc definitions reference role types by ID. New role types can be added to the library without changing the arc schema.
- Victim slot added as 7th structural position in the Nightcap arc, separate from the six player role types.
- `ContentEvent` type `accusation_result` added with `display_mode: "voting_reveal"` for the shared display voting moment.
- Asset generation strategy formalized: pre-produced per theme (v1 implementation); runtime generation is a planned A/B experiment. `aesthetic_config` encodes this distinction per element.
- Fully generative story content is a Nightcap-specific design decision. The platform supports authored, generative, and hybrid content strategies. Other arcs may choose differently.
- Killer active capabilities are story-prompted optional actions, not tracked resource pools. No `ability_charge` concept.
- Conspirator victim role: conditional (fires only if story benefits), variable complicity mode (accidental default, direct if killer correctly guessed), runtime-generated leverage message.
- Balance principle added as an engine-enforced constraint: clue chain always sufficient for full investigator engagement to solve the case; interference throttled against balance state.

**Changes from v1.0 (Chat 7 pre-work):** Added character_mode, aesthetic_mode, setting_constraint, arc_structure, play_mode, and narrator as first-class arc schema fields. Added NarratorConfig Pydantic model. Added narrator_generation task type to routing taxonomy. Updated Nightcap arc execution flow to reflect imposter play mode. Updated generative vs authored table for character mode.

**Primary audiences:** Founder, future product managers, future co-founders and senior hires, Claude Code

---

# S1 System Architecture Overview

## 1.1 What Arcwright Is as a Technical System

Arcwright is Layer 2 narrative runtime middleware. Layer 1 is foundation model infrastructure (Anthropic, Google, Groq, open source models). Layer 3 is the experience layer (Nightcap, the monster RPG, third-party developer games). Arcwright sits between them: it takes a human-authored arc definition and a group of real players, and produces a coherent, unrepeatable session experience at runtime.

This positioning is not a marketing choice. It is the architectural commitment that determines what Arcwright builds, owns, and maintains. Arcwright does not train foundation models. It does not build game engines or rendering surfaces. It orchestrates the narrative runtime between the raw AI capability layer and the experience delivery layer.

## 1.2 Component Stack

| Layer | Component | Language | Responsibility |
| --- | --- | --- | --- |
| Experience | Nightcap, monster RPG, third-party games | Any | Arc definition, surface rendering, player onboarding |
| **Platform: API** | **FastAPI service** | **Python** | **REST + SSE transport, auth, schema validation, rate limiting** |
| **Platform: Engine** | **arcwright-engine library** | **Python** | **Arc execution, knowledge graph, character behavior, routing, safety, events, telemetry** |
| **Platform: SDK** | **TypeScript web SDK** | **TypeScript** | **Game client connection, event subscription, player input submission** |
| Infrastructure | Cloud SQL, Cloud Run, Firebase Auth | GCP managed | Persistence, compute, identity |
| AI supply chain | Anthropic, Groq, open source via LiteLLM | External | Foundation model inference |

The engine library is the primary product. The API is a thin HTTP wrapper around it. The SDK layer is plural: the TypeScript web SDK is the first wrapper, generated from the OpenAPI source of truth, while future engine SDKs (Unity in C#, Unreal in C++ with Blueprints integration, Godot in GDScript or C#, and native mobile in Swift or Kotlin if pursued) are separate native-language wrappers around the same REST API. Neither the API nor any SDK contains game logic or arc execution logic.

## 1.3 How Nightcap Sits on the Stack

Nightcap is an experience built on the platform. It contributes:

- An arc definition file (`nightcap/arc.json`) that specifies characters, beats, generative elements, knowledge rules, and content rails
- A host interface (web app) that drives session creation and shared display rendering
- A player interface (phone browser) that renders private events and accepts player input
- No engine code. All arc execution, knowledge state management, character behavior, model routing, and content safety run in the platform engine.

If Nightcap disappeared tomorrow, the engine would still run any other arc definition unchanged.

## 1.4 Architecture Principles to Implementation Mapping

Eight principles from PRD Section 3 map to specific technical implementations in this document. Cross-references for each:

| PRD Principle | Implementation | Document Section |
| --- | --- | --- |
| Surface agnosticism | ContentEvent schema with `target_audience` and `presentation_hints`; no surface type in engine | S8 |
| Human arc primacy | ArcDefinition schema with `authored` vs `generative` flags per element; arc execution enforces authored constraints regardless of AI output | S3 |
| Configurable composition | `generative_elements: GenerativeConfig` per arc; per-element authored/generative dial | S3 |
| Unified character model | Single `Character` object for human and AI participants; behavior source (AI engine vs input channel) is the only difference | S7 |
| Knowledge graph as first-class infrastructure | `knowledge_states` table, `assert_knowledge` / `get_character_knowledge` / `revoke_knowledge` API; not optional; enforced before every AI generation call | S4 |
| Cost-aware architecture | LiteLLM routing table maps task type + quality tier to current cheapest option; pacing and safety route to small models on Groq; generation routes to capable models on Anthropic | S6 |
| Progressive proprietary infrastructure | Tier 1 (deterministic infrastructure) built at MVP; Tier 2 (fine-tuned models) triggered by volume and data; Tier 3 (foundation model development) never | S6, S12 |
| Provider-agnostic model routing | All model calls through `engine/routing/router.py`; no provider name outside `routing_table.json`; routing table swap requires zero code changes | S6 |

## 1.5 What Arcwright Is Not Responsible For

These are explicit non-responsibilities. A proposed requirement that pushes into this territory signals either scope creep or a Nightcap-specific decision being misclassified as a platform decision:

- Rendering any surface (TV, phone, browser, voice interface). The engine emits events; Nightcap renders them.
- Storing player payment information or managing subscriptions. This is the game layer's responsibility.
- Generating arc structure. The platform executes and personalizes a human-designed arc. It does not write the arc.
- Operating as a general-purpose LLM API or chatbot infrastructure. Inworld pivoted here. Arcwright does not.
- Managing CDN, media delivery, or audio/video streaming. The platform handles text and structured events.
- Foundation model training or fine-tuning at MVP. Session telemetry is collected; fine-tuning is a Tier 2 trigger gated on volume.

---

# S2 Technology Stack

All decisions in this section are locked (Chat 6a, May 7 2026). Rationale is summarized here; full rationale is in 02-Decisions-Log. Alternatives considered are listed to prevent re-litigation during implementation.

## 2.1 Decision Summary Table

| Area | Decision | Version | Locked decision reference |
| --- | --- | --- | --- |
| Cloud provider | GCP | Current | Decision 3 |
| Compute | Cloud Run (containerized, serverless) | Current | Decision 3 |
| Database | Cloud SQL PostgreSQL | 15 | Decision 5 |
| Vector extension | pgvector | Latest stable | Decision 6 |
| Auth platform | Firebase Auth | Current | Decision 19 |
| Engine language | Python | 3.11+ | Decision 4 |
| API framework | FastAPI | 0.111+ | Implied by Decision 4 |
| Async runtime | Python asyncio | stdlib | Implied by Decision 11 |
| ORM | SQLAlchemy async | 2.0+ | Implied by Decision 4 |
| Migrations | Alembic | Latest stable | Implied by Decision 4 |
| Arc execution | python-statemachine StateChart | 3.0+ | Decision 11 |
| Transport | SSE (server push) + POST (client input) | HTTP/1.1 | Decision 10 |
| AI routing | LiteLLM in-process | 1.30+ | Decision 14 |
| Safety L2 | GPT-OSS-Safeguard 20B on Groq | Current | Decision 16 |
| SDK language | TypeScript | 5.x | Decision 4 |
| Dashboard framework | React (TypeScript) | 18+ | Implied by Decision 4 |

## 2.2 Compute and Infrastructure

**GCP + Cloud Run.** Serverless containers with scale-to-zero. At MVP scale (dozens of sessions, not thousands), minimum monthly cost is under $70 total for all services. Cloud Run eliminates VM management and automatic scaling handles uneven session load without pre-provisioned capacity.

Two Cloud Run services at MVP:

| Service | Purpose | Resources | Notes |
| --- | --- | --- | --- |
| `arcwright-api` | FastAPI HTTP and SSE handler | 1 vCPU, 512 MB | Stateless; scales on request count |
| `arcwright-worker` | Arc execution, AI generation tasks | 2 vCPU, 1 GB | Stateful per session; see Section 5 for session affinity approach |

**Rejected alternatives:**

- AWS + Neon: Neon is AWS-only. GCP was preferred for Cloud Run ergonomics and pgvector on Cloud SQL. (Decision 5)
- Kubernetes: over-engineered for MVP solo development; revisit at H2 if session volume demands horizontal scaling architecture.
- Single service monolith: acceptable at MVP but the API / worker split is cleaner for session affinity and background arc execution. The split is low cost with Cloud Run.

**Cloud SQL PostgreSQL 15.** Managed relational database. pgvector extension enabled at first migration for embedding-ready schema (`VECTOR(1536) NULL` columns on `characters`, `facts`, `events`, `generation_logs`). These columns are nullable at MVP; populated only when fine-tuning data collection activates. The schema is designed once; embedding capability costs nothing until used.

Instance at MVP: `db-f1-micro`, single region, 10 GB SSD. Cost: ~$10-15/month. Upgrade path to `db-g1-small` or higher is a Cloud SQL setting change, not a migration.

## 2.3 Languages

**Python 3.11+ (engine + API).** The engine library and FastAPI service are Python. 3.11 is the minimum for performance improvements in the async runtime and `tomllib` stdlib inclusion. Do not use Python below 3.11 anywhere in the codebase.

**TypeScript 5.x (web SDK + dashboard).** The web SDK and React dashboard are TypeScript. Strict mode enabled. No `any` types in the SDK public interface. TypeScript is not the language for every future engine SDK. Unity, Unreal, Godot, and native mobile wrappers require their native ecosystems while wrapping the same REST API and OpenAPI contract.

**Language boundary rule:** Python owns all arc execution, knowledge graph, character behavior, model routing, content safety, and session state logic. TypeScript owns all client-facing rendering, event subscription, and player input submission logic. No arc execution logic crosses into TypeScript.

## 2.4 Data Layer

**SQLAlchemy 2.0 async + asyncpg.** Async ORM for all database access from the engine. SQLAlchemy 2.0 async style (not the legacy 1.x style). `asyncpg` as the PostgreSQL driver. All queries go through SQLAlchemy; no raw SQL in application code except migrations.

**Alembic.** Database migrations. All schema changes are Alembic migrations. No manual schema changes applied directly to Cloud SQL. Migration files are version-controlled.

**pgvector.** Enabled via `CREATE EXTENSION IF NOT EXISTS vector` in the first migration. `VECTOR(1536)` columns are present from day one on `characters.embedding`, `facts.embedding`, `events.embedding`, and `generation_logs.prompt_embedding`. Dimension 1536 matches OpenAI `text-embedding-3-small` and Anthropic's current embedding output. If the embedding model changes, the dimension may need a migration; design for this possibility.

**Knowledge graph storage:** Pure relational at MVP. State tables (`characters`, `facts`, `knowledge_states`, `relationships`) plus append-only `events` log. Apache AGE (graph extension for PostgreSQL) is addable later if the monster RPG's emergent narrative requires graph traversal queries that are expensive in SQL. Do not add AGE at MVP; the SQL schema is sufficient for Nightcap and is designed to be AGE-compatible.

## 2.5 API and Transport

**FastAPI 0.111+.** HTTP API framework. Route handlers are thin: they validate input (Pydantic schemas), call engine functions, and return responses. No arc logic in route handlers.

**Transport: SSE + POST with adapter pattern.**

- Server to client (content events, arc beat updates, narrator output): SSE stream. Each connected client (phone browser, shared display) maintains a persistent SSE connection to `arcwright-api`.
- Client to server (player input, accusations, host commands): HTTP POST to REST endpoints.
- Transport adapter pattern: the engine emits `ContentEvent` objects to an abstract event bus. The SSE delivery layer subscribes to the bus and fans out to connected clients by `target_audience`. Switching from SSE to WebSockets in the future requires replacing the delivery layer adapter only; the engine does not change.

**Rejected alternatives:**

- WebSockets: more complex to manage connection state at MVP; SSE is sufficient for server-push and simpler to implement with FastAPI's `EventSourceResponse`. Revisit if bidirectional real-time is required for a future arc type.
- GraphQL subscriptions: unnecessary complexity at MVP.

## 2.6 Arc Execution

**python-statemachine 3.0+ (StateChart base class).** SCXML-compliant statechart library. `StateChart` is the base class (not `StateMachine`, which is the legacy 2.x-compatible class). Parallel regions (`State.Parallel`), compound states (`State.Compound`), history states, delayed events, and invoked sub-machines are all available natively. See Section 3 for the full arc execution engine design.

Verified May 11 2026: v3.0 supports all required arc graph patterns (branching, convergence, loops, parallel regions, conditional transitions via `cond=`).

## 2.7 AI Supply Chain

**LiteLLM 1.30+ in-process.** Single Python library that abstracts all AI provider calls. Initialized in-process at MVP; no sidecar proxy. Upgrade to LiteLLM Proxy Server in H2 if multi-service routing or centralized logging becomes necessary.

Routing table at `config/routing_table.json` maps task type + quality tier to current model. No model name or provider string appears outside this file and `engine/routing/router.py`.

**Safety L2: GPT-OSS-Safeguard 20B on Groq.** Pre-generation safety classification. Supports bring-your-own-policy. Groq inference: fast and cheap (~$0.075/million input tokens; output rate pending verification per Open Question in 03-Open-Questions-Log). See Section 10 for full safety pipeline.

**Pricing reference (verified May 7 2026):**

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Use in routing table |
| --- | --- | --- | --- |
| Claude claude-haiku-4-5 (Anthropic) | $1.00 | $5.00 | standard dialogue, standard narrative |
| Claude claude-sonnet-4-6 (Anthropic) | $3.00 | $15.00 | premium dialogue, premium narrative |
| Llama 3.1 8B (Groq) | $0.05 | $0.08 | pacing decisions, knowledge inference (standard) |
| Llama 3.3 70B (Groq) | $0.59 | $0.79 | knowledge inference (premium) |
| GPT-OSS-Safeguard 20B (Groq) | ~$0.075 | TBC | safety classification (all tiers) |

Batch API (50% discount on Anthropic) is not used at MVP due to real-time session requirements. Prompt caching (90% discount on cache hits) is used where system prompts and arc definitions are stable across calls within a session.

## 2.8 Auth

Three token types, three use cases:

| Token type | Issued by | Used for | Lifetime |
| --- | --- | --- | --- |
| Firebase ID token | Firebase Auth | Dashboard access, host session creation | 1 hour, refresh via SDK |
| API key | Arcwright platform | Developer API access (H2+; internal use at MVP) | Until revoked |
| Session join JWT | Arcwright API at session creation | Player game client auth | Session duration + 30 min grace |

Anonymous player join: players receive a session join JWT via QR code or invite link. No Firebase account required to join as a player. Account creation is offered post-session (optional).

## 2.9 Testing Approach

Focused unit tests at MVP on four areas (Decision 21): knowledge graph correctness, arc state transitions, safety enforcement, model routing fallback. Manual testing elsewhere. Full simulation harness at MVP (Decision 22): AI-driven synthetic players, seeded deterministic runs, scenario scripting, batch statistics, replay. See Section 15.9 for acceptance criteria per component.

---

# S2.10 Chat 9 Platform-Clean Architecture Addendum

The build path remains: build for Nightcap, design platform-clean. Platform-clean means clean internal abstractions and game-agnostic schemas from day one. It does not mean external API exposure during H1. External developer exposure is gated by product signals, including Nightcap profitability and non-Nightcap external developer demand.

Schema design is platform-clean from day one and includes all fields needed for full functionality. Implementation is staged. Nightcap MVP receives minimum-viable implementations of advanced features; Monster RPG H2 fills in sophisticated implementations. The schema should not change between MVP and H2 solely because the MVP implementation is simplified.

Visual Storyworld Phase 1 is part of H1 dashboard architecture. Phase 1 includes inspection-only surfaces: live knowledge graph visualization, read-only arc structure view, live event stream, and character state inspection. These surfaces support debugging and developer understanding without committing to a no-code editor at MVP.

# S3 Arc Execution Engine

The arc execution engine is the core of the platform. It takes an arc definition and a live session, advances the session through designed beats, enforces authored constraints, triggers AI generation at configured points, and emits content events. It does not render anything. It does not know what a TV or phone is. It produces a stream of `ContentEvent` objects and session state updates.

## 3.1 StateChart Architecture

Each session instantiates one `ArcStateChart`, a subclass of `python-statemachine`'s `StateChart`. The chart represents the arc's beat graph: states are beats, transitions are arc progressions, guards are authored entry and exit conditions.

```python
from statemachine import StateChart, State

class NightcapArcChart(StateChart):
    # Top-level beats
    class introduction(State.Compound, initial=True):
        onboarding = State(initial=True)
        killer_assignment = State()
        motive_reveal = State(final=True)
        begin_game = onboarding.to(killer_assignment)
        motives_established = killer_assignment.to(motive_reveal)

    class investigation(State.Compound):
        class clue_phase(State.Parallel):
            class private_clues(State.Compound):
                distributing = State(initial=True)
                distributed = State(final=True)
                clues_sent = distributing.to(distributed)
            class interrogation(State.Compound):
                open = State(initial=True)
                closed = State(final=True)
                interrogation_complete = open.to(closed)
        resolution = State(final=True)
        phases_complete = clue_phase.to(resolution)

    reveal = State(final=True)

    # Arc-level transitions
    investigation_begins = introduction.to(investigation)
    accusation_filed = investigation.to(reveal)
```

The `introduction` beat uses `State.Compound` with internal sub-beats for onboarding, killer assignment, and motive establishment. The `investigation` beat uses `State.Parallel` so private clue distribution and group interrogation run simultaneously: the parallel region's `done.state` event fires only when both regions reach final, which is the engine's signal that investigation is complete. `reveal` is the terminal state.

Runtime conditional transitions use `cond=` guards. Example: the engine does not advance to `reveal` until the accusation meets the minimum evidence threshold defined in the arc definition. If a host forces early reveal, the guard is bypassed via a host-privileged event, logged as a pacing intervention.

## 3.2 Beat Graph Model

Beat graphs support four structural patterns:

| Pattern | Implementation | Example use |
| --- | --- | --- |
| Linear sequence | `state_a.to(state_b)` | Introduction to investigation |
| Branching | Multiple transitions from one state with `cond=` guards | Investigation extends vs. early reveal |
| Convergence | Multiple sources to one target | Different investigation paths all reach reveal |
| Loop | Transition back to earlier state | Re-investigation if accusation fails |

All four patterns are native to python-statemachine v3.0. No custom graph traversal code is required.

Arc definitions specify the beat graph as `beat_graph: dict[str, list[str]]` (beat_id to valid next beat_ids) plus `entry_conditions` and `exit_conditions` per beat. The StateChart class is generated at session start from the arc definition, not written statically per arc. This means new arcs require only a new arc definition JSON file, not a new StateChart subclass.

## 3.3 Pacing Engine

The pacing engine runs as a single asyncio background task per session. It computes a `dramatic_tension_score` (0.0 to 1.0) on a configurable interval (default: 30 seconds) and drives all pacing decisions from that one score.

**dramatic_tension_score computation:**

```python
class DramaticTensionScore:
    """Weighted composite of four session signals. Weights are arc-configurable."""
    def compute(self, session: SessionState, config: PacingConfig) -> float:
        time_pressure = self._time_in_beat_score(session, config)     # rises as beat ages
        action_rate   = self._player_action_rate(session)              # falls when players stall
        suspicion     = self._correct_suspicion_confidence(session)    # rises as killer identified
        clue_coverage = self._clue_distribution_completeness(session)  # rises as clues dealt

        return (
            config.w_time     * time_pressure  +
            config.w_action   * action_rate    +
            config.w_suspicion * suspicion     +
            config.w_coverage * clue_coverage
        )
```

Weights (`w_time`, `w_action`, `w_suspicion`, `w_coverage`) are stored in `pacing_config` inside the arc definition. Nightcap's default weights are a design choice that will require iteration during playtesting; the architecture supports weight adjustment without code changes.

**Intervention thresholds (all read from the single score):**

| Condition | Threshold | Action | Model route |
| --- | --- | --- | --- |
| Score falls below `stall_threshold` (default 0.25) | Players have stalled | Inject clue or narrator prompt | `pacing_decision` / Llama 3.1 8B on Groq |
| Score rises above `misdirection_threshold` (default 0.80) | Players solving too quickly | Inject red herring via a character whose behavior has been too transparent | `narrative_generation` / Llama 3.1 8B on Groq |
| Score above `premium_threshold` (default 0.85) | Peak dramatic moment | Upgrade character dialogue to `premium` quality tier for this beat | Routing table: `character_dialogue / premium` |

The third row is the architectural benefit of unification: when tension is highest, the routing table automatically serves premium-tier character dialogue without any explicit call-site code. The score is the quality tier signal.

`dramatic_tension_score` is logged to `events` table on every pacing poll as `event_type = "tension_update"` with `payload.score`. Intervention events log `event_type = "pacing_intervention"` with `trigger_type`, `score_at_trigger`, and `outcome` (whether player activity resumed within 60 seconds). Both are Telemetry signal 2 (pacing intervention triggers/outcomes) from the PRD minimum set. The continuous score log is also a Tier 2 training signal: it captures the shape of tension across a session's arc.

## 3.4 Generative vs Authored Execution

Each element in an arc definition is flagged as `authored` (fixed) or `generative` (AI-driven at runtime). The engine treats these differently:

| Element type | Authored execution | Generative execution |
| --- | --- | --- |
| Beat structure | Executed as defined; cannot be overridden by AI output | N/A (beats are always authored) |
| Character identity | Served from arc definition | N/A |
| Killer assignment | N/A | AI-assigned at `introduction.killer_assignment` entry; seeded with session player list and character profiles |
| Character personality | Served from arc definition (base profile) | Behavior_profile augmented at session start with group-specific calibration |
| Clue content | Optional authored clue text | AI-generates clue text calibrated to assigned character |
| Plot twist | N/A | Injected by pacing engine when misdirection threshold crossed |
| Narrator dialogue | Optional authored beats | AI-generates narrator dialogue for all generative beats |

The engine enforces authored constraints regardless of generative output. If the arc defines that `reveal` cannot be entered before beat three, the transition guard blocks it regardless of what the AI generates or what players do. Authored constraints are not suggestions.

## 3.5 Character Behavior Commitments

Six commitments from Decision 13, with implementation approach:

| Commitment | Implementation |
| --- | --- |
| Stochastic generation | Each AI character response call uses `temperature=0.7` (configurable per arc); deterministic output is explicitly rejected. Two calls to the same prompt produce different responses. |
| Initiative scheduler | Background asyncio task per AI character. Each character has a configurable `initiative_interval` in their `behavior_profile`. When the interval fires without player input to that character, the character acts unprompted (speaks, moves, reacts). |
| NPC-NPC interaction first-class | AI characters can be targeted at each other, not only at players. The behavior engine accepts `target_character_id` on generation calls; NPC-NPC exchanges are generated with both characters' knowledge states and relationship graphs in the prompt. |
| Goal pursuit drives behavior | Each character's `behavior_profile.goals` list is injected into every generation prompt as a constraint block. Character responses are generated to advance or conceal their goals, not to be generically helpful. |
| Per-character behavior_profile | `behavior_profile JSONB` column on `characters` table. Stores: personality traits, communication style, goals, secrets, tells (behavioral signals of guilt or nervousness), and relationship dispositions toward each other character. |
| Arc-level non-determinism | The arc's `generative_elements.killer_assignment` is resolved at session start with a seeded random draw. The seed is stored in session state (for replay and persistence). Two identical player groups produce different killers across sessions. |

## 3.6 Session Coordinator Loop

The session coordinator is an asyncio coroutine that runs for the lifetime of each session. It:

1. Instantiates the `ArcStateChart` from the arc definition.
2. Starts the pacing engine background task.
3. Starts per-AI-character initiative scheduler tasks.
4. Listens on a session event queue for: player input events, host commands, pacing triggers, character initiative triggers, and arc beat transition signals.
5. For each event: evaluates guards, executes transition if valid, triggers generative elements configured for the new beat, emits resulting `ContentEvent` objects to the session event bus.
6. Handles session interruption: on disconnect or host pause, snapshots full session state to `arc_beat_states` and `knowledge_states` tables. On resume, restores state and resumes the coordinator from the saved beat.

The coordinator never blocks. All AI generation calls are `await`-ed as asyncio tasks. Long-running generation does not stall the event queue.

## 3.7 Nightcap Arc: Execution Flow Summary

| Phase | Beat | Key generative triggers | Content events emitted |
| --- | --- | --- | --- |
| Setup | `introduction.killer_assignment` | Killer identity draw, initial behavior_profile calibration | None visible to players yet |
| Onboarding | `introduction.motive_reveal` | Character personality augmentation, opening narrator dialogue | Shared display: setting; phones: character cards with private background |
| Investigation | `investigation.clue_phase` (parallel) | Clue generation per character, NPC initiative, pacing interventions | Phones: private clues; shared display: group events and NPC dialogue |
| Reveal | `reveal` | Killer confession narrative | Shared display: reveal scene; phones: outcome summary |

---

# S9 Developer API and Authoring Experience

## 9.1 Stack Positioning

Arcwright is Layer 2 narrative runtime middleware. Developers building on Arcwright receive two things: structured infrastructure they do not have to build (knowledge graph, arc execution, model routing, content safety, session state) and a surface-agnostic event stream they wire to whatever delivery layer they choose.

What developers bring:

- An arc definition (the human-authored structure: characters, beats, constraints, generative configuration)
- A delivery layer (the client code that renders events on their chosen surfaces)
- A content vision (the genre, tone, and experience they are building)

What developers do not need to build:

- Knowledge state enforcement across multiple characters
- AI model routing and cost management
- Session persistence and resume
- Content safety pipeline
- Pacing and dramatic timing logic
- Per-character behavior modeling

At MVP the platform is not open to external developers. The API is designed for external access from day one; Nightcap uses it internally as its first consumer. The documentation, arc definition format, and SDK surface must be legible to an external developer even if no external developer reads them at MVP.

## 9.2 REST API Endpoint Catalog

Base path: `/v1/`. All endpoints require auth (API key for developer calls; session JWT for game client calls).

### Session Management

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/v1/sessions` | API key | Create session from arc definition. Returns `session_id`, join URL, host token. |
| POST | `/v1/sessions/{id}/start` | Host JWT | Start the session arc. Triggers `introduction` beat. |
| GET | `/v1/sessions/{id}` | API key / Host JWT | Session state: status, current beat, player count, cost consumed. |
| POST | `/v1/sessions/{id}/pause` | Host JWT | Pause arc; snapshot state. |
| POST | `/v1/sessions/{id}/resume` | Host JWT | Resume from nearest beat snapshot. |
| POST | `/v1/sessions/{id}/end` | Host JWT | End session; emit final state record. |
| GET | `/v1/sessions/{id}/join` | None (public) | Validate join token; return player JWT and character assignment. |

### Character Management

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/v1/sessions/{id}/characters` | Host JWT | All characters in session with current behavior state (no private knowledge state). |
| GET | `/v1/sessions/{id}/characters/{char_id}` | Player JWT | Character detail for the requesting player's character only. |
| POST | `/v1/sessions/{id}/characters/{char_id}/input` | Player JWT | Submit player action or dialogue as the named character. |

### Knowledge State Management

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/v1/sessions/{id}/knowledge` | Host JWT / Arc engine (internal) | Assert a fact into a character's knowledge state. |
| DELETE | `/v1/sessions/{id}/knowledge/{fact_id}` | Arc engine (internal) | Revoke a fact (deception, forgetting). |
| GET | `/v1/sessions/{id}/knowledge/{char_id}` | Arc engine (internal) | Query a character's current knowledge state. Not exposed to player clients. |

### Content Event Stream

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/v1/sessions/{id}/events` | Player JWT / Host JWT | SSE stream. Delivers `ContentEvent` objects filtered by the requesting client's `target_audience`. Phone clients receive `all`  • `specific_player` events for their player_id. Host receives `all`  • `host_only`. Shared display receives `all`  • `shared_display`. |

### Usage and Developer Tools

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/v1/usage` | API key | AI credit consumption by session, by arc, by time window. |
| POST | `/v1/arcs/validate` | API key | Validate an arc definition JSON against the schema. Returns errors and warnings. |

## 9.3 Arc Definition Format

Arc definitions are JSON files. Nightcap's arc definition at `nightcap/arc.json` is the canonical reference. Every field name here must match the `ArcDefinition` Pydantic schema in `engine/arc/models.py`.

**Top-level structure:**

```json
{
  "arc_id": "nightcap-v1",
  "name": "Nightcap",
  "min_players": 4,
  "max_players": 10,
  "character_mode": "generated",
  "aesthetic_config": {
    "selection_model": {
      "era": {"type": "host_select", "allow_random": true},
      "occasion": {"type": "host_select", "allow_random": true}
    },
    "asset_generation": {
      "background_art": "pre_produced_per_theme",
      "music_palette": "pre_produced_per_theme",
      "animations": "pre_produced_per_theme",
      "ui_chrome": "pre_produced_per_theme",
      "character_portraits": "generated_at_session_start",
      "setting_name": "generative_runtime",
      "character_identities": "generative_runtime",
      "narrator_dialogue": "generative_runtime"
    },
    "ab_test_planned": "pre_produced_vs_runtime_generated"
  },
  "victim_config": {
    "eligibility_mode": "player_count_governed",
    "player_count_threshold": 4,
    "designation_trigger": "killer_revelation",
    "victim_role_pool": ["witness", "specter", "informant", "conspirator"],
    "conspirator_conditional": true,
    "conspirator_default_complicity": "accidental"
  },
  "kill_config": {
    "base_kills": 1,
    "additional_kills_available": true,
    "additional_kill_slot_config": "6_slot_only",
    "proportionality_check": true,
    "dynamic_expansion_triggers": ["killer_survived_accusation", "investigation_accelerating"]
  },
  "murder_timing_range": [1, 3],
  "session_duration_range": [30, 75],
  "revelation_step_range": [2, 4],
  "setting_constraint": "social_gathering",
  "arc_structure": "story_circle",
  "play_mode": "imposter",
  "tone_config": {
    "brand_envelope": {
      "irreverence": [0.5, 1.0],
      "suspense": [0.4, 0.9],
      "dark_comedy": [0.4, 0.85],
      "wit_density": [0.6, 1.0],
      "chaos_tolerance": [0.3, 0.8]
    },
    "scenario_defaults": {
      "irreverence": 0.7,
      "suspense": 0.65,
      "dark_comedy": 0.65,
      "wit_density": 0.75,
      "chaos_tolerance": 0.55
    },
    "voice_directive": "Wit-first ensemble mystery. The mystery and stakes are real. Characters are fully realized eccentrics with genuine agendas. Humor is structural and character-driven. The experience is irreverent, smart, suspenseful, mildly unhinged. Does not take itself too seriously but always takes the story seriously. Reference: Guy Ritchie Sherlock Holmes, Wes Anderson, Glass Onion, The Amazing Digital Circus, Rick and Morty, The League."
  },
  "narrator": {
    "type": "host_persona",
    "surface": "shared_display",
    "persona_mode": "aesthetic_linked",
    "behavior_triggers": ["beat_transition", "clue_release", "tension_threshold", "player_inaction"],
    "omniscient": true,
    "player_addressable": true
  },
  "quality_tier_default": "standard",
  "characters": [...],
  "beats": [...],
  "beat_graph": {
    "introduction": ["investigation"],
    "investigation": ["reveal"],
    "reveal": []
  },
  "generative_elements": {
    "killer_assignment": true,
    "character_generation": true,
    "character_personality_augmentation": true,
    "aesthetic_generation": true,
    "clue_content": true,
    "plot_twist": true,
    "narrator_dialogue": true
  },
  "content_rails": {
    "prohibited_categories": ["csam", "graphic_violence", "real_person_targeting"],
    "thematic_warnings": ["murder_mystery", "deception", "dark_motives"],
    "age_floor": 18
  },
  "pacing_config": {
    "stall_threshold": 0.25,
    "misdirection_threshold": 0.80,
    "premium_threshold": 0.85,
    "w_time": 0.3,
    "w_action": 0.3,
    "w_suspicion": 0.2,
    "w_coverage": 0.2
  },
  "knowledge_rules": {
    "killer_knows_they_did_it": true,
    "narrator_omniscient": true,
    "clues_private_until_shared": true
  }
}
```

**Arc validation tool (`POST /v1/arcs/validate`)** must catch at MVP:

- Required fields missing
- `beat_graph` references a beat_id not defined in `beats`
- `generative_elements` references an element not in the allowed set
- `min_players` greater than `max_players`
- Pacing weight sum (`w_time + w_action + w_suspicion + w_coverage`) not equal to 1.0
- `character_mode: authored` with no characters defined in `characters` array
- `narrator.behavior_triggers` references a trigger type not in the allowed set
- `play_mode: imposter` with `min_players` less than 3 (imposter mode requires at least 2 investigators plus 1 killer)

## 9.4 TypeScript Web SDK

The SDK ships at MVP for game client use (phone browsers and shared display). It wraps the REST and SSE endpoints in typed functions. It does not contain any arc logic.

**Core surface:**

```tsx
// arcwright-sdk/src/index.ts
export class ArcwrightClient {
  constructor(sessionId: string, joinToken: string, baseUrl: string) {}

  // Connect to SSE event stream; callback fires on each ContentEvent
  onEvent(callback: (event: ContentEvent) => void): () => void {}

  // Submit player action or dialogue
  async submitInput(characterId: string, input: PlayerInput): Promise<void> {}

  // Get current character state for the authenticated player
  async getMyCharacter(): Promise<CharacterDetail> {}

  // Disconnect and clean up SSE connection
  disconnect(): void {}
}

// Types are generated from the engine Pydantic schemas via a build step
export type { ContentEvent, PlayerInput, CharacterDetail, PresentationHints }
```

The SDK has no knowledge of surface types, arc structure, or game rules. It is a typed HTTP/SSE client. Nightcap's phone client and shared display client import this SDK and handle rendering independently.

## 9.5 Dashboard at MVP

The dashboard serves three functions at MVP: arc validation, session monitoring, and usage management. It is not a no-code arc builder. It assumes developers who can read JSON and understand arc concepts.

| Function | What it provides | What it does not provide |
| --- | --- | --- |
| Arc authoring | JSON editor with live schema validation and error highlighting | Visual drag-and-drop beat graph builder (deferred post-MVP) |
| Session monitoring | Live view: current beat, player count, `dramatic_tension_score`, AI credit consumption, knowledge state event count | Full dialogue transcript or private player information |
| Usage management | Credit consumption by session, by arc, by day; cost per session at current routing table | Billing and payment (out of scope at MVP) |

## 9.6 Documentation Requirements at MVP

Three documents ship with the API, sufficient for a technical co-founder to read the architecture without asking the founder to explain decisions:

1. **Getting started guide.** Session creation to first event stream in under 20 minutes. Uses Nightcap as the example arc.
2. **Arc definition reference.** Every field in `ArcDefinition` and its sub-schemas, with type, required/optional, and a one-sentence description.
3. **Nightcap arc schema.** The complete `nightcap/arc.json` published as the canonical reference implementation. Every structural decision in this arc is annotated with why it was made that way.

These documents are not sufficient for a public API launch. A full developer documentation investment is required before the H2 external developer beta (scope debt, PRD Section 9).

---

# S4 Knowledge Graph

## 4.1 What the Knowledge Graph Is

In a real murder mystery dinner, every guest knows different things. The killer knows they did it. The victim's best friend knows about a secret argument. The nosy neighbor noticed someone leaving through the back door. Each person at the table is working from a different picture of reality, and the drama comes from those pictures colliding.

The knowledge graph is the system that tracks those different pictures. For every character in every session, it records: what does this character know, when did they learn it, and who told them? When an AI character speaks, the knowledge graph is what stops them from accidentally revealing a clue they were never supposed to have, or acting innocent about something their character secretly knows.

This is not an optional add-on. It is the reason the platform can run a coherent, unrepeatable session. Without it, AI characters contradict themselves, clues bleed across characters who should not have them, and the mystery falls apart. Every experience built on Arcwright gets knowledge state management, regardless of arc type.

## 4.2 Database Tables

The knowledge graph lives in six tables in Cloud SQL PostgreSQL.

**`facts`** stores the actual pieces of information that can be known. Think of a fact as a clue card: it has a type (clue, accusation, relationship, event), a structured content payload, and optionally an embedding column for future similarity search. A fact exists once and can be known by multiple characters.

**`knowledge_states`** is the join layer: it records which character knows which fact, when they learned it, and the full chain of characters through which they learned it. Each record stores a `provenance_chain` as a JSON array: an ordered list of character IDs from the original source to the current knower. If the witness told the housekeeper, who told the detective, the detective's record reads `provenance_chain: [witness_id, housekeeper_id, detective_id]`. A direct observation has a chain of one. Confidence below 1.0 models deception: if the butler told the detective something false, the record stores `confidence = 0.4` alongside the provenance chain. The detective believes it is probably true, knows who told them, and the engine can trace exactly how far this (possibly false) information has traveled. This enables contradiction detection, realistic "I heard from someone that..." dialogue, and richer session telemetry.

**`relationships`** tracks how characters feel about each other: trust level, history, current emotional disposition. This feeds the behavior engine and affects how characters choose to share or withhold information.

**`characters`** stores each participant's identity and `behavior_profile`. The behavior profile is a JSON object containing personality traits, goals, secrets, and behavioral tells. For AI characters, the behavior engine reads this profile before generating every response.

**`events`** is the append-only session history log. Every significant thing that happens in a session is recorded here: a clue delivered, an accusation made, a pacing intervention triggered. Events are never edited or deleted; they are only appended. The full event log is what allows a session to be resumed after interruption.

**`decisions`** logs the arc execution decisions made during the session: which beat was entered, which generative element triggered, which content safety rule fired. This is the audit trail.

## 4.3 The Three Core Operations

The knowledge graph exposes three operations to the rest of the engine:

**Assert:** a character learns something. Called when the arc delivers a clue to a player, when an NPC reveals information during dialogue, or when the pacing engine decides a character should know something to advance the session. Stored in `knowledge_states` with the fact, the character, the source, the timestamp, and the confidence level.

**Revoke:** a character's knowledge state changes. Used when deception is introduced: a character is told something false, or a piece of information is retracted. The original record is not deleted (the event log is append-only); instead a new `knowledge_states` record is written that supersedes the previous one for that character-fact pair. The history of what the character believed and when is preserved.

**Query:** what does this character currently know? Called by the behavior engine before every AI character generation call. Returns the character's current knowledge state as a structured list of facts with confidence levels. This output is injected into the AI prompt as a constraint block: the AI is explicitly told what this character knows and what they do not.

```python
# Called before every AI character response generation
knowledge = await get_character_knowledge(session_id, character_id)
# knowledge is injected into system prompt:
# "This character knows: [list of facts with confidence]"
# "This character does NOT know: [list of facts in session outside their knowledge]"
# The model is constrained to respect these boundaries.
```

This query is mandatory. There is no path through the character behavior engine that generates a response without first calling it. This is enforced at the engine layer, not left to individual arc implementations.

## 4.4 Schema Complexity Tiers

Not every arc needs the same level of knowledge tracking. The platform supports two tiers:

**Simple (MVP, Nightcap):** Facts are boolean. A character either knows a clue or does not. Confidence is used for deception modeling but there is no inference: the engine does not reason about what a character might know based on what they know about something else. This is sufficient for Nightcap and costs very little to compute.

**Complex (Horizon 2, monster RPG):** Inference chains and contradiction detection. If a character knows that the butler was in the kitchen at 9pm, and separately knows that the murder happened in the kitchen at 9pm, the engine can infer that the butler is a suspect even if no one told them this directly. This requires relationship-aware graph traversal, which is why the schema was designed with Apache AGE compatibility in mind (see Section 2.4). This tier is not implemented at MVP.

The schema is designed to be extensible. The simple tier runs on the same tables as the complex tier; the complex tier adds inference rules and traversal logic on top of the same underlying data. No schema migration is required to move from simple to complex, only additional query logic.

## 4.5 Embedding-Ready Design

Each fact in the `facts` table has an `embedding VECTOR(1536) NULL` column. At MVP this column is always null. When Tier 2 data collection activates, fact embeddings will be computed and stored, enabling:

- Semantic similarity search: find all facts in the session that are conceptually related to a player's question, even if the wording is different
- Fine-tuning signal: which facts were most salient in sessions that received high replay intent scores
- Future authoring assistance: suggest related clues from past sessions when an arc author is designing a new mystery

The column is present from day one at zero cost. Populating it requires an embedding API call per fact, which is deferred until the use case is active.

---

# S7 Character Behavior Engine

## 7.1 What It Does

The character behavior engine is the part of the platform that makes characters feel like real people with their own agendas rather than chatbots answering questions. When a player confronts the butler about a discrepancy in his alibi, the butler does not just respond. He responds in a way that is consistent with his personality, shaped by his secret, influenced by whether he trusts this particular player, and subtly colored by the fact that three people at the table are now staring at him.

The engine achieves this by building a complete psychological profile for every character before the session begins, maintaining that profile's consistency throughout every interaction, and using the session's social dynamics as a live input to generation. Characters do not have memory lapses. They do not contradict their own goals. And the killer, over the course of an evening, will betray themselves in ways that players can argue about for an hour after the session ends.

This is what makes sessions feel unrepeatable and what makes players want to play again: not random content, but consistent psychology producing genuinely different behavior depending on who is in the room.

## 7.2 The Behavior Profile

Every character in an Arcwright session has a `behavior_profile`: a structured JSON object stored in the `characters` table. It is the character's psychology encoded as data. For human players, it is read-only: it defines the character they are playing. For AI characters, it is the complete input to every response the engine generates.

```json
{
  "personality": {
    "traits": ["charming", "evasive", "secretly resentful"],
    "communication_style": "deflects personal questions with humor",
    "under_pressure_style": "becomes over-precise about minor details"
  },
  "goals": [
    "Protect my secret about the financial arrangement with the victim",
    "Appear cooperative with the investigation",
    "Redirect suspicion toward the housekeeper if possible"
  ],
  "secrets": [
    {
      "content": "I was blackmailing the victim over a forged document",
      "concealment_priority": "high",
      "crumble_threshold": 0.7
    }
  ],
  "tells": [
    "Mentions specific times unprompted when nervous",
    "Uses first names instead of titles when caught off-guard"
  ],
  "relationship_dispositions": {
    "character_id_housekeeper": {"trust": 0.3, "history": "rivalry", "current_affect": "cool"},
    "character_id_detective": {"trust": 0.6, "history": "acquaintance", "current_affect": "cautious"}
  }
}
```

`crumble_threshold` is how much accumulated social pressure it takes before a character's concealment starts to crack, expressed as a score from 0.0 (cracks easily) to 1.0 (never voluntarily reveals). This feeds directly into the social pressure system described in Section 7.4.

For Nightcap, behavior profiles have a base template per character slot (the butler always starts as charming and evasive) and a generative augmentation layer applied at session start: the AI calibrates personality nuances, relationship tensions, and tell patterns to the specific group of players joining. Two sessions with the same character slots produce noticeably different people.

## 7.3 Generation Pipeline

Every AI character response follows the same seven-step pipeline. No shortcuts.

1. **Query knowledge state.** `get_character_knowledge(session_id, character_id)` returns what this character knows and does not know. Mandatory; see Section 4.
2. **Query relationship graph.** Retrieve this character's current `relationship_dispositions` toward the player who is speaking and toward any other characters recently active in the scene.
3. **Compute social pressure score.** See Section 7.4. A single float (0.0-1.0) representing how much collective suspicion is currently directed at this character.
4. **Assemble system prompt.** Five blocks in order: (a) character identity and personality, (b) knowledge state constraint (what they know and do not know), (c) relationship context for this interaction, (d) social pressure instruction (how to modulate behavior given current pressure), (e) current beat context and goals for this scene.
5. **Route.** Task type `character_dialogue`, quality tier determined by `dramatic_tension_score` (standard below 0.85, premium above). See Section 6.
6. **Safety L3.** Policy injected into system prompt constrains thematic content to arc-defined rails before generation.
7. **Emit.** Output wrapped as `ContentEvent` with `target_audience`, `presentation_hints`, and `actor_id`. Delivered to session event bus.

Total pipeline latency target at MVP: under 1,500ms for standard tier, under 2,500ms for premium tier. These are not guaranteed SLAs; they are design targets that inform model selection.

## 7.4 Social Pressure Dynamics

Most AI character systems treat each exchange as independent: one player asks a question, one character answers. The behavior engine treats the room as a social system.

**Social pressure score** is computed per AI character on every pacing poll, alongside the `dramatic_tension_score`. It measures how much collective suspicion is currently directed at this character across all players:

```python
def compute_social_pressure(character_id: UUID, session: SessionState) -> float:
    # Weighted sum of: explicit accusations, suspicious questions directed at this character,
    # gaze signals (shared display focus), and alliance patterns (other characters
    # distancing themselves from this one)
    recent_accusations = session.accusation_weight(character_id, window_minutes=10)
    directed_questions = session.question_intensity(character_id, window_minutes=5)
    alliance_isolation = session.alliance_distance(character_id)
    return min(1.0, (recent_accusations * 0.5) + (directed_questions * 0.3) + (alliance_isolation * 0.2))
```

When social pressure exceeds a character's `crumble_threshold`, their behavior begins to shift in generation: they become over-precise, they deflect more aggressively, they make small errors consistent with their `under_pressure_style`. The killer does not confess; they just become more themselves under stress. Perceptive players notice. Players who are not paying attention miss it.

This is what produces the post-game argument: "Did you see how he answered that question about the kitchen?" "I thought that was completely normal." That disagreement is the sign of a session that worked.

## 7.5 Killer Tell System

The killer is assigned at session start. From that moment, the killer's `behavior_profile` is augmented with a set of tells: subtle behavioral patterns that are consistent with guilt but deniable as ordinary personality.

Tells are designed in three tiers:

| Tier | Visibility | Example |
| --- | --- | --- |
| Surface | Noticeable on reflection | "Uses first names instead of titles when caught off-guard" |
| Mid | Requires pattern recognition across multiple exchanges | "Answers questions about the crime scene with more detail than asked, then immediately changes subject" |
| Deep | Only visible to players actively tracking behavior across the full session | "Never initiates conversation with players who were near the crime scene at the time of death" |

At MVP, tells are authored into character archetypes in `nightcap/arc.json`. The generative augmentation layer selects which tier of tells to activate based on the player group's size: larger groups receive more surface tells (more people to notice them), smaller groups receive more mid and deep tells (fewer witnesses, harder game).

The killer's AI generation is constrained to express tells authentically but never to confess. The concealment goal is highest priority; the tells are behavioral leakage that happens despite the goal, not because of it.

## 7.6 Ensemble Coherence

AI characters in the same session are not independent agents. They are members of a social group and they behave that way.

Ensemble coherence is maintained through three mechanisms:

**Shared event awareness.** All AI characters receive the same session events (via the event bus) and update their knowledge states and relationship dispositions based on them. If the detective publicly accuses the butler, every other character's model of the butler's trustworthiness shifts.

**NPC-NPC interaction.** The initiative scheduler can trigger an AI character to address another AI character directly, not just players. These exchanges are generated with both characters' knowledge states and relationship dispositions in the prompt. A tense NPC-NPC exchange produced by emergent social dynamics is often the most memorable moment of a session because no player manufactured it.

**Relationship graph updates.** After significant events (accusations, revelations, emotional exchanges), the relationship graph is updated: trust levels shift, `current_affect` changes. Future generations for those characters read the updated graph, so behavior evolves naturally over the session rather than resetting to baseline on each exchange.

## 7.7 Monster RPG Extensibility

The behavior engine is designed to support the monster RPG's requirements without modification. The unified character model (same object for human and AI participants) means player trainers and NPC gym leaders are indistinguishable at the data layer. Player-defined motivation inference (the RPG requirement) slots in as an additional `behavior_profile` generation step at session entry: instead of assigning a fixed motivation, the engine infers it from the player's first actions and updates it as the session progresses. The inference runs via `knowledge_inference` task type in the routing table, no new routing required.

**Provenance chains in the behavior engine.** Every AI character response that references a piece of information can now express how they came to know it, not just that they know it. A character with `provenance_chain: [witness_id, housekeeper_id, detective_id]` on a fact can say "I heard from the housekeeper that the witness saw something" rather than stating the fact as direct knowledge. Characters with short provenance chains (they witnessed it themselves) speak with more certainty. Characters at the end of long chains express appropriate uncertainty. The engine injects provenance chain length and source identity into the generation prompt as part of the knowledge state constraint block. See Section 4 for the full schema.

---

# S10 Content Safety Architecture

Content safety is not a post-launch patch. It is a core system designed before any other generative component, for two reasons. First, the murder mystery genre is adjacent to dark thematic territory by design: deception, hidden motives, and simulated harm are the genre's building blocks. Second, when the platform opens to third-party developers in Horizon 2, Arcwright is responsible for what runs on its infrastructure, regardless of which developer built the arc. The architecture reflects this: safety constraints are enforced at the engine layer and cannot be bypassed by arc configuration.

AI Dungeon's content safety failure in 2021 was not a moderation failure. It was an architecture failure: safety was designed as a filter on top of an otherwise unconstrained generative system. This document commits to the opposite approach.

## 10.1 Three-Layer Architecture

Three layers at MVP. Each layer catches different things and operates at a different point in the generation pipeline.

```
[Player input / Arc trigger]
        |
        v
  L1: Hard stops          <- Deterministic; no AI involved; zero latency
        |
        v
  L2: Pre-generation      <- GPT-OSS-Safeguard 20B on Groq; classifies intent before generation
  classification
        |
        v
  L3: In-generation       <- Policy injected into system prompt; constrains what the main LLM produces
  policy
        |
        v
  [Content event emitted]
```

**L4 (post-generation output filter) is deferred.** It would catch content that slipped through L1-L3. The deferred decision: add L4 when a specific failure pattern observed in production justifies the additional latency. The watchpoint trigger is: any L3 escape observed during playtesting or the first 90 days of production sessions. This is logged in 03-Open-Questions-Log.

## 10.2 Layer 1: Hard Stops

Deterministic code. No model call. No configuration. These categories are blocked unconditionally, regardless of arc definition, developer configuration, or player input:

- Sexual content involving anyone under 18
- Content targeting a real, named, living individual with harmful intent
- Detailed instructions for real-world violence or weapons construction
- Content designed to facilitate real-world harm outside the fictional frame

L1 runs on player input before any model call and on the assembled prompt before submission to L2/L3. If L1 fires, the event is blocked, logged to the `events` table with `event_type = "safety_hard_stop"`, and the session continues with a neutral narrator bridge. The player receives no error message that reveals the safety trigger; the experience is preserved.

## 10.3 Layer 2: Pre-Generation Classification

GPT-OSS-Safeguard 20B running on Groq. Fast (Groq's inference is optimized for low latency) and cheap (~$0.075/million input tokens). Supports bring-your-own-policy: the arc definition's `content_rails` configuration is passed as the policy context.

For Nightcap, the L2 policy includes:

- Permitted thematic territory: murder mystery, deception, hidden motives, dark social dynamics
- Thematic warnings (content that is permitted but logged): graphic descriptions of violence, explicit sexual content between adult characters
- Prohibited at arc level (in addition to L1): real-person targeting, content that breaks the fictional frame to provide real-world harmful information

L2 runs before every main LLM generation call. If L2 classifies the assembled prompt as prohibited, the generation call is not made. A neutral bridge response is generated by a separate low-stakes call. L2 classification results are logged to `events` with classification confidence score. This log is the primary signal for tuning L2 policy in future sessions.

Note: Groq output rate for GPT-OSS-Safeguard 20B is pending verification (open question in 03-Open-Questions-Log). Cost model in Section 13 uses a conservative estimate pending confirmation.

## 10.4 Layer 3: In-Generation Policy

A policy block is injected into the system prompt of every main LLM call, after the character identity and knowledge state blocks. The policy block states in plain language what the model must not produce, calibrated to the arc's `content_rails` configuration. This is the backstop that handles edge cases L2 did not catch: ambiguous content that is technically within policy but contextually inappropriate for the arc.

The L3 policy block for Nightcap includes: no graphic depiction of the murder itself, no sexual content between characters, no real-world harmful information delivered in-character, no content that directly accuses a real person.

L3 is the cheapest layer to customize and the most arc-specific. Developers configure it through `content_rails` in their arc definition.

## 10.5 Dashboard Visibility

Developers can verify their safety configuration is active via the dashboard. For each arc:

- L2 policy in effect (displayed as the bring-your-own-policy configuration active for this arc)
- L3 policy block (displayed as the injected text)
- L1 activations in recent sessions (count; no content)
- L2 classification activations (count and average confidence; no content)

Developers cannot read the content of blocked inputs. They can see that their rails are working and where they are firing.

## 10.6 What This Means for External Developers

When the platform opens to external developers in Horizon 2, they inherit L1 and L2 automatically. They configure L3 via `content_rails`. They cannot disable L1. They can expand L2's permitted territory within bounds Arcwright sets at the platform level (adult content between consenting adult characters is an example of something a developer could unlock; CSAM is an example of something that cannot be unlocked under any configuration). This tiered permission model is designed before external developers arrive; it is not retrofitted when they do.

---

# S11 Telemetry Schema

## 11.1 Why Telemetry Is Non-Negotiable

Every session that runs on Arcwright without structured telemetry is compute cost with no data return. More importantly: sessions that run without telemetry before the Tier 2 fine-tuning transition are training data permanently lost. You cannot go back and label sessions that were not instrumented.

Think of it this way: Arcwright's long-term cost advantage over competitors using the same underlying models is proprietary session data. Competitors using Anthropic's API and Arcwright using Anthropic's API are on equal footing today. In Horizon 2, if Arcwright has 50,000 labeled sessions and competitors do not, the fine-tuned models running on Arcwright infrastructure will be meaningfully better and cheaper per session. That gap is built one session at a time, starting from the first production deployment.

Telemetry must be live before a single real-user session runs. This is a hard requirement, not a launch checklist item.

## 11.2 Core Events Table

All telemetry flows into one primary table plus two supporting tables.

```sql
CREATE TABLE events (
    event_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id     UUID NOT NULL REFERENCES sessions(session_id),
    timestamp      TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor_char_id  UUID REFERENCES characters(character_id),  -- null for system events
    event_type     TEXT NOT NULL,
    payload        JSONB NOT NULL DEFAULT '{}',
    content_text   TEXT,          -- null at MVP for most event types
    embedding      VECTOR(1536)   -- null at MVP; populated when embedding collection activates
);

CREATE INDEX ON events (session_id, timestamp);
CREATE INDEX ON events (event_type, timestamp);
```

The `events` table is append-only. Records are never updated or deleted. GDPR deletion requests are handled by nullifying `content_text` and zeroing `embedding` for the affected session, not by deleting rows. The structural record (event type, timestamp, actor) is retained for telemetry integrity; the potentially personal content is removed.

## 11.3 MVP Minimum Signals

Five signals required by the PRD MVP done-criteria. All five are active from the first production session.

**Signal 1: Arc beat engagement duration.**

Logged on every beat transition: `event_type = "beat_transition"`, `payload = {"from_beat": str, "to_beat": str, "duration_seconds": int, "player_action_count": int}`. Duration is time from beat entry to beat exit. This is the primary signal for identifying which beats need authoring attention: a beat with high variance in duration across sessions is either under-paced or over-paced.

**Signal 2: Pacing intervention triggers and outcomes.**

Logged by the pacing engine: `event_type = "pacing_intervention"`, `payload = {"trigger_type": "stall" | "misdirection", "tension_score_at_trigger": float, "beat_id": str, "outcome_resumed_within_60s": bool}`. Also logged on every pacing poll: `event_type = "tension_update"`, `payload = {"score": float}`. The continuous tension score log captures the shape of dramatic arc across the full session, not just intervention moments.

**Signal 3: Knowledge state constraint activations.**

Logged when the knowledge query returns a constraint that affects generation: `event_type = "knowledge_constraint_activated"`, `payload = {"character_id": str, "fact_type": str, "constraint_direction": "blocked" | "permitted", "provenance_chain_length": int}`. The `provenance_chain_length` field is the telemetry payoff for the provenance chain adoption: over many sessions, this reveals whether longer information chains produce more engaging character behavior.

**Signal 4: Session completion status.**

Logged on session end: `event_type = "session_completed"`, `payload = {"completion_type": "full_arc" | "interrupted" | "abandoned", "final_beat_reached": str, "killer_identified": bool, "total_duration_seconds": int, "player_count": int}`. This is the top-level health metric for Nightcap: completion rate.

**Signal 5: Replay intent indicators.**

Logged at session end via a host-triggered post-session signal: `event_type = "replay_intent"`, `payload = {"intent": "yes" | "no" | "maybe" | "not_asked", "collection_method": "host_report" | "in_app_prompt"}`. This is a soft signal (host self-reports) at MVP. A more rigorous in-app prompt is a Tier 2 improvement.

## 11.4 generation_logs Table

Schema exists at MVP. Content population is behind the `CONTENT_LOGGING_ENABLED` feature flag (default: false). See Concern 1 resolution in chat record.

```sql
CREATE TABLE generation_logs (
    log_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES sessions(session_id),
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT now(),
    task_type       TEXT NOT NULL,          -- "character_dialogue" | "pacing_decision" | etc.
    quality_tier    TEXT NOT NULL,          -- "standard" | "premium"
    model_used      TEXT NOT NULL,          -- from routing table at time of call
    latency_ms      INTEGER NOT NULL,
    input_tokens    INTEGER NOT NULL,
    output_tokens   INTEGER NOT NULL,
    cost_usd        NUMERIC(10,6) NOT NULL,
    tension_score   FLOAT,                  -- dramatic_tension_score at time of call
    -- Fields populated only when CONTENT_LOGGING_ENABLED=true:
    prompt_text         TEXT,
    output_text         TEXT,
    prompt_embedding    VECTOR(1536),
    output_embedding    VECTOR(1536)
);
```

At MVP with the flag off: every generation call is logged with model, latency, token counts, cost, and tension score. This is sufficient for cost monitoring, per-session gross margin calculation, and routing table optimization. Prompt and output text are not stored, which keeps GDPR surface area minimal.

When the flag is enabled (Tier 2 readiness milestone): full prompt and output text are logged and embeddings are computed. This is the raw material for fine-tuning. The GDPR consent architecture for content logging must be designed before the flag is enabled: player-submitted content (names, character choices, dialogue) may appear in prompts.

## 11.5 decision_logs Table

```sql
CREATE TABLE decision_logs (
    decision_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES sessions(session_id),
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT now(),
    decision_type   TEXT NOT NULL,  -- "killer_assignment" | "clue_distribution" | "beat_transition" | etc.
    input_context   JSONB NOT NULL, -- structured context that drove the decision
    outcome         JSONB NOT NULL  -- what was decided
);
```

Implemented at MVP. Captures arc execution decisions (killer assignment seed, clue distribution order, pacing intervention choice) with the context that produced them. Over many sessions, this table reveals which decision patterns correlate with high completion rates and replay intent.

## 11.6 Tier 2 Signal Set: Designed, Partial at MVP

These signals are designed now so the schema is ready. At MVP, the fields exist but most are populated only for high-value event types. Full population is a Tier 2 milestone.

| Signal | Purpose | MVP status |
| --- | --- | --- |
| Dialogue quality rating | Per-generation quality score (human or automated) | Schema exists; not populated at MVP |
| Per-character engagement depth | How much each character was interacted with vs ignored | Derivable from events table post-session |
| Knowledge graph snapshots | Full knowledge state at each beat boundary | Schema exists; not populated at MVP |
| Safety filter outcomes | Detailed L2 classification confidence and category | L2 activations logged; detail deferred |
| Behavior consistency score | Whether a character's behavior was consistent with their profile across the session | Requires post-session evaluation pass; Tier 2 |
| Group dynamics index | How socially active the group was (question rate, accusation patterns, alliance formation) | Derivable from events table post-session |
| Provenance chain engagement | Whether long provenance chains produced more nuanced character dialogue | Tracked via `provenance_chain_length` in Signal 3 from MVP |

## 11.7 Telemetry and the Tier 2 Transition

The Tier 2 transition (fine-tuned models replacing managed API calls for specific task types) requires three conditions: sufficient session volume, sufficient data quality, and a confirmed cost break-even calculation. Telemetry is the mechanism that makes all three assessable.

- **Volume:** count of sessions with complete Signal 1-5 coverage
- **Quality:** distribution of completion rates and replay intent scores across the session corpus
- **Break-even:** per-session cost from `generation_logs` at current managed API rates vs projected fine-tuned inference cost

The Tier 2 transition cannot be evaluated without this data. Arcwright starts collecting it from session one.

---

# S5 Session State and Persistence

## 5.1 What Session State Is

Imagine eight players are 45 minutes into a Nightcap session. The host's phone dies. When she relaunches the app, the session should resume exactly where it left off: every player still holds their private clues, the killer is still the same person, and the narrator picks up without anyone starting over. None of that information should exist only in active memory.

Session state is everything that needs to survive an interruption: the arc's position, what every character knows, the full history of events, and the relationship tensions that have developed. The engine writes this to the database continuously throughout the session, not only at the end.

## 5.2 What Gets Persisted

Four categories of state, each mapped to specific tables:

**Arc position** (`arc_beat_states`): the current beat, the active state configuration inside that beat (python-statemachine's `configuration` value, which is the set of currently-active states), and the full transition history. On resume, the engine restores the statemachine to its last stable beat boundary rather than the exact moment of interruption.

**Character knowledge** (`knowledge_states`, `facts`): every fact assertion and revocation, with full provenance chains. The complete picture of who knows what, when they learned it, and how they came to know it.

**Session history** (`events`): the append-only event log. This is the authoritative record of everything that happened. If derived state is ever uncertain, the engine can reconstruct it from the event log.

**Relationship state** (`characters.behavior_profile` JSONB): character relationship dispositions as they have evolved during the session. Trust levels, affect changes, and alliance patterns that developed through play are preserved, not reset.

## 5.3 The Nearest-Beat Restore Pattern

The engine does not resume from mid-scene. Resuming mid-dialogue is disorienting for players and risks AI coherence failures. Instead:

1. When interruption is detected, complete any atomic operation in progress (await an in-flight generation call up to 5 seconds, complete any beat transition already underway)
2. Write a full state snapshot to `arc_beat_states` at the nearest completed beat boundary
3. Set session status to `paused`
4. On resume, restore the statemachine to that beat boundary
5. Emit a narrator bridge: a short AI-generated recap that re-grounds players before the arc continues

No session restarts from the beginning. No session state is permanently lost.

## 5.4 Interruption and Resume Flow

```
Interruption:
  1. Pacing engine task cancelled
  2. Character initiative tasks cancelled
  3. In-flight generation calls awaited (5s timeout, then cancelled)
  4. Full state snapshot written to arc_beat_states
  5. Session status -> "paused"
  6. Event logged: event_type = "session_interrupted"

Resume (host issues resume command):
  1. Load arc definition
  2. Reconstruct ArcStateChart from arc_beat_states snapshot
  3. Restore knowledge_states and relationship graph
  4. Restart pacing engine and character initiative tasks
  5. Generate narrator bridge event
  6. Session status -> "active"
  7. SSE streams re-established; players receive current beat context
```

## 5.5 Single Player Drop

If one player drops (not the host), the arc continues. The dropped player's character can be converted to an AI-controlled character mid-session: the `is_ai_controlled` flag on `session_participants` flips to true, the behavior engine picks up that character's full behavior profile and knowledge state, and the session proceeds without interruption. The host decides whether to convert or to mark the character as absent with a brief narrator acknowledgement.

## 5.6 Scope Debt

Inter-service communication between the API service and the engine worker (two Cloud Run services coordinating on session resume) is a deferred decision. Cloud Tasks (async, reliable, retryable) and direct async HTTP invocation (simpler, lower latency) are both viable at MVP scale. This decision must be made before production deployment and is logged in 03-Open-Questions-Log.

---

# S6 AI Model Routing Layer

## 6.1 What the Routing Layer Is

Think of the routing layer as a traffic controller for every AI call the platform makes. Instead of the rest of the engine knowing which AI provider to use and how much it costs, all AI calls pass through one place: `engine/routing/router.py`. That file reads a configuration table, picks the right model for the job, and makes the call. Everything else in the engine only knows the task type and quality level it needs. The routing layer handles the rest.

This matters for three reasons. First, AI pricing and model quality change frequently; a routing table update is a config file change, not a code deployment. Second, if a provider has an outage, the fallback logic is in one place. Third, when Arcwright eventually fine-tunes its own models and wants to route some calls to them, that transition happens entirely inside the routing layer. No other code changes.

## 6.2 The Provider-Agnostic Contract

Every component in the engine that needs an AI call follows the same contract:

```python
# What callers do:
response = await router.generate(
    task_type="character_dialogue",
    quality_tier="standard",      # or "premium"
    messages=[...],               # assembled prompt
    temperature=0.7
)

# What they never do:
# import anthropic
# litellm.acompletion(model="claude-haiku-4-5-20251001", ...)
```

No provider name, model name, or API key reference appears outside `router.py` and `routing_table.json`. If this rule is violated anywhere in the codebase, that is a bug.

## 6.3 Task Type Taxonomy

Every AI call belongs to exactly one task type. The taxonomy is fixed at MVP; new task types can be added for new arc types without changing existing routing logic.

| Task type | What it does | Latency priority | Quality need | Cost tier |
| --- | --- | --- | --- | --- |
| `character_dialogue` | Generates in-character speech and action | Medium | High | Medium/High |
| `narrative_generation` | Narrator text, scene descriptions, clue prose | Medium | High | Medium/High |
| `pacing_decision` | Determines whether and how to intervene in session flow | Low | Low | Very low |
| `knowledge_inference` | Reasons about what a character might infer from their knowledge state | Low | Medium | Low/Medium |
| `safety_classification` | Classifies content against arc policy before generation | High (blocks generation) | Specialized | Very low |
| `killer_assignment` | One-shot at session start: assigns killer and calibrates behavior profiles | Low | Medium | Low |
| `narrator_bridge` | Short recap on session resume | Low | Medium | Low |

## 6.4 Quality Tier Selection

Most task types have two quality tiers: `standard` (faster, cheaper) and `premium` (more capable, more expensive). The tier for `character_dialogue` and `narrative_generation` is determined dynamically by the `dramatic_tension_score` from the pacing engine:

```python
def resolve_quality_tier(
    task_type: str,
    session_state: SessionState,
    arc_config: ArcDefinition
) -> str:
    if task_type in ("character_dialogue", "narrative_generation"):
        if session_state.dramatic_tension_score >= arc_config.pacing_config.premium_threshold:
            return "premium"
    return "standard"  # default for all other task types and below-threshold tension
```

The effect: the most capable model is deployed precisely when the session is at its most dramatically charged, and standard-tier models handle the quieter moments. This produces higher quality where it matters and lower cost everywhere else.

## 6.5 Fallback Behavior

LiteLLM handles provider-level fallbacks natively. The routing table supports a `fallback` key per task type and tier:

```json
{
  "character_dialogue": {
    "standard": "anthropic/claude-haiku-4-5-20251001",
    "standard_fallback": "groq/llama-3.3-70b-versatile",
    "premium": "anthropic/claude-sonnet-4-6",
    "premium_fallback": "anthropic/claude-haiku-4-5-20251001"
  }
}
```

If the primary model call fails (provider outage, rate limit, timeout), LiteLLM automatically retries against the fallback. The session continues. Fallback activations are logged to `events` with `event_type = "routing_fallback"` so the founder can see which providers are causing fallback pressure.

## 6.6 Cost Tracking

Every generation call logs to `generation_logs` immediately on completion: model used, input tokens, output tokens, latency, and computed cost in USD. Cost is calculated from a rates table embedded in `router.py` and updated when provider pricing changes.

```python
# After every successful generation call:
await log_generation(
    session_id=session_id,
    task_type=task_type,
    quality_tier=tier,
    model_used=model_key,
    latency_ms=latency,
    input_tokens=usage.prompt_tokens,
    output_tokens=usage.completion_tokens,
    cost_usd=compute_cost(model_key, usage),
    tension_score=session_state.dramatic_tension_score
)
```

The dashboard aggregates this table to show per-session AI cost, per-arc cost average, and the real-time cost consumed by an active session. This is the founder's primary tool for monitoring gross margin per session and identifying which arc elements drive cost spikes.

## 6.7 Prompt Caching

Anthropic supports prompt caching with a 90% discount on cache hits. Two caching opportunities exist in every Nightcap session:

**Arc definition cache:** the arc definition, character schemas, and knowledge rules are identical across all sessions of the same arc. These are passed in the system prompt and eligible for caching once the cache warms on the first call.

**Character profile cache:** within a session, a character's identity, personality, and base goals are stable. Only the knowledge state and social pressure components change between calls. Structure prompts to place stable content first (cache-eligible) and dynamic content last (appended fresh).

Prompt caching is configured through LiteLLM's cache_control headers. Estimated impact on per-session cost at MVP: 20-35% reduction on `character_dialogue` calls where the system prompt is reused within the session.

## 6.8 Horizon 2 Upgrade Path

At MVP: LiteLLM in-process. One Python library, zero additional infrastructure.

At H2 (if warranted): LiteLLM Proxy Server deployed as a separate Cloud Run service. Reasons to trigger this upgrade:

- Multiple Arcwright services (API worker, engine worker, future services) need centralized model routing with shared rate limit management
- Enterprise customers require data residency guarantees that need routing-layer enforcement
- The Tier 2 fine-tuning transition requires routing some calls to Arcwright-hosted models, and centralized routing makes this cleaner to manage

The upgrade is a deployment change, not a code change. The `router.py` abstraction layer is identical in both configurations; only the target URL changes from the in-process LiteLLM SDK to the proxy endpoint.

---

# S8 Multi-Surface Event System

## 8.1 What the Event System Is

The event system is the delivery layer between the engine and every screen in the room. When the arc engine decides that a clue should go to one specific player, that decision produces a `ContentEvent`. The event system takes that event and delivers it to exactly the right place: the phone belonging to that player, and nowhere else. The shared TV display gets a different event at the same moment: the narrator acknowledging that a clue has been shared, without revealing its contents.

The engine never knows what a TV or phone is. It only knows audience targets: `all`, `specific_player`, `host_only`, `shared_display`. The event system resolves those targets to live connections. This separation is what makes the platform surface-agnostic: the same engine that runs Nightcap on a phone and a TV could run a future arc on voice interfaces, smartwatches, or surfaces that do not exist yet, with no engine changes.

## 8.2 ContentEvent Schema

Defined in `engine/events/models.py`. Referenced in S15 with the core fields. Full schema:

```python
class ContentEvent(BaseModel):
    event_id:          UUID
    session_id:        UUID
    timestamp:         datetime
    event_type:        ContentEventType
    actor_id:          UUID | None          # character who produced this event; None for system events
    target_audience:   AudienceTarget       # all | host_only | specific_player | shared_display
    target_player_id:  UUID | None          # set only when target_audience = specific_player
    payload:           dict                 # event-type-specific structured content
    presentation_hints: PresentationHints
    sequence_number:   int                  # monotonically increasing per session; enables client-side ordering

class PresentationHints(BaseModel):
    emotion:          str | None   # "tense" | "warm" | "suspicious" | "playful" | "solemn"
    urgency:          str | None   # "low" | "medium" | "high"
    voice_hint:       str | None   # character voice descriptor for TTS or actor direction
    animation_hint:   str | None   # display layer hint; engine-agnostic string
    lighting_hint:    str | None   # display layer hint; engine-agnostic string
    pause_before_ms:  int          # optional pre-event pause for dramatic timing; default 0
```

`sequence_number` is new relative to the S15 definition: it is a monotonically increasing integer per session, assigned at event emission. SSE clients use this to detect missed events and request a replay window. This prevents gaps in the experience if a client reconnects.

`pause_before_ms` in `PresentationHints` is a creative addition: the engine can signal that a beat should breathe before the next event lands. A reveal moment might have `pause_before_ms = 2000`. The display layer honors this; it is a hint, not a guarantee.

## 8.3 Event Bus Architecture

At MVP, the event bus is an in-memory asyncio queue per session, held in the engine worker process. The API service subscribes to the bus via an internal async channel when a client connects via SSE.

```
Arc execution engine
        |
        v
  Session event bus       <- asyncio.Queue per session; in-memory at MVP
        |
        v
  SSE Fan-out Router      <- reads bus, filters by target_audience, delivers to connections
     /    |    \
   SSE   SSE   SSE
  Phone  Phone  TV
```

For Horizon 2 with multiple engine worker instances, the in-memory bus does not survive process boundaries. The upgrade path: replace the asyncio queue with a lightweight pub/sub layer (Redis Pub/Sub or Cloud Pub/Sub). The fan-out router code does not change; only the bus implementation changes. This is the transport adapter pattern committed in Decision 10.

## 8.4 Target Audience Filtering

The fan-out router maintains a connection registry per session:

```python
class SessionConnectionRegistry:
    connections: dict[UUID, list[SSEConnection]]  # participant_id -> connections
    display_connections: list[SSEConnection]       # shared display connections
    host_connections: list[SSEConnection]          # host connections

    def route(self, event: ContentEvent) -> list[SSEConnection]:
        match event.target_audience:
            case AudienceTarget.ALL:
                return self.all_player_connections() + self.display_connections
            case AudienceTarget.SPECIFIC_PLAYER:
                return self.connections.get(event.target_player_id, [])
            case AudienceTarget.HOST_ONLY:
                return self.host_connections
            case AudienceTarget.SHARED_DISPLAY:
                return self.display_connections
```

Privacy enforcement is structural. There is no code path through which a `specific_player` event reaches the wrong participant. The registry resolves targets to connections; the connections know only their own player ID.

## 8.5 Nightcap Two-Surface Example

Nightcap deploys on two surfaces simultaneously: the shared display (a TV or laptop in the room running the host interface) and each player's phone browser.

When the arc engine distributes a clue to Player 3:

| Event | target_audience | Delivered to | Content |
| --- | --- | --- | --- |
| `clue_delivery` | `specific_player` (Player 3) | Player 3's phone only | Full clue text, character association, presentation hints |
| `clue_acknowledged` | `shared_display` | TV | "A clue has been passed to [Character Name]" — no content |
| `clue_acknowledged` | `host_only` | Host interface | Which clue, which player, timestamp |

Player 3 receives their clue privately. Everyone in the room sees that something happened. The host sees what it was. The engine emits three events; the routing layer handles the rest.

## 8.6 SSE Implementation

FastAPI's `EventSourceResponse` (from the `sse-starlette` library) handles the SSE stream per client. Each connection:

- Authenticates via player JWT on connection
- Registers with the session connection registry
- Receives a replay of the last N events on reconnect (using `sequence_number` to identify the gap)
- Deregisters on disconnect; the arc continues for other participants

Event format on the wire:

```
data: {"event_id": "...", "event_type": "clue_delivery", "sequence_number": 42, "payload": {...}, "presentation_hints": {...}}

```

The TypeScript SDK wraps the browser's native `EventSource` API, parses the JSON, and calls the registered `onEvent` callback. The SDK consumer (Nightcap's phone client) only sees `ContentEvent` objects; it never touches SSE directly.

## 8.7 What the Event System Does Not Do

- Does not render anything. Rendering is the game client's responsibility.
- Does not store events. Storage is the `events` telemetry table's responsibility.
- Does not make generation decisions. That is the arc execution engine's responsibility.
- Does not know what a TV, phone, or browser is. It knows participant IDs and connection objects.

---

# S12 Incremental Build Plan

## 12.1 The Three-Tier Build Philosophy

Arcwright builds in three tiers, each triggered by evidence rather than calendar. This is PRD Architecture Principle 7 (Progressive Proprietary Infrastructure) translated into a concrete build sequence.

**Tier 1 (build at MVP):** Everything deterministic. The arc execution engine, session state management, knowledge graph, event system, developer API, and usage tracking. These have zero marginal AI cost per session. They encode Arcwright's specific understanding of adaptive experiences. They are the platform's permanent foundation regardless of which AI providers exist in five years.

**Tier 2 (triggered by volume and data, Horizon 2 at earliest):** Specialized models fine-tuned on Arcwright session data, replacing general-purpose API calls for specific task types. Requires thousands of structured, labeled sessions and confirmed cost break-even. Do not build before the data justifies it.

**Tier 3 (never):** Foundation model development, GPU cluster ownership. Arcwright buys foundation model capability from providers who spend orders of magnitude more on it than Arcwright will. This is rational capital allocation, not a capability gap.

## 12.2 MVP: What Gets Built and In What Order

The component build order follows the dependency graph. Components higher in the list must be stable before components lower in the list can be built against them. This maps directly to Section 15.9.

**Phase 1: Data foundation (build first)**

1. Database schema and Alembic migrations (all 16 tables, pgvector enabled)
2. Core Pydantic models (`Session`, `SessionParticipant`, `Character`, `ArcDefinition`, `ContentEvent`)
3. Basic FastAPI app skeleton with health check and auth middleware

**Phase 2: Knowledge graph (build second; everything generative depends on it)**

1. `assert_knowledge` with provenance chain support
2. `get_character_knowledge` with constraint output format
3. `revoke_knowledge`
4. Unit tests: knowledge correctness suite

**Phase 3: Routing and safety (build before any generation)**

1. `router.py` with `routing_table.json` and LiteLLM integration
2. Routing fallback logic and `generation_logs` write
3. L1 hard stops
4. L2 pre-generation classification (GPT-OSS-Safeguard on Groq)
5. L3 policy injection
6. Unit tests: routing fallback, safety enforcement

**Phase 4: Arc execution engine (build after knowledge and routing are stable)**

1. `ArcStateChart` base class and `NightcapArcChart` implementation
2. `DramaticTensionScore` pacing engine with intervention logic
3. Session coordinator asyncio loop
4. Character behavior generation pipeline (7-step: knowledge query through event emit)
5. Initiative scheduler for AI characters
6. NPC-NPC interaction support
7. Unit tests: arc state transitions, pacing interventions

**Phase 5: Event system and API (build after engine is functional)**

1. `SessionConnectionRegistry` and SSE fan-out router
2. In-memory asyncio event bus
3. FastAPI SSE endpoint with reconnect and sequence number replay
4. REST endpoints: session lifecycle, character input, knowledge assert
5. TypeScript web SDK (`ArcwrightClient`)

**Phase 6: Session persistence (build after end-to-end flow is working)**

1. Interrupt/resume flow with nearest-beat snapshot
2. Player drop and AI takeover
3. Session state replay from event log

**Phase 7: Telemetry and simulation (build last; validates everything above)**

1. All five MVP minimum telemetry signals wired to events table
2. `generation_logs` writes (non-content fields only)
3. `decision_logs` writes
4. Simulation harness: synthetic players, seeded runs, batch statistics

## 12.3 MVP Done Criteria

MVP is complete when all of the following are true (from PRD Section 9):

- Nightcap is playable end-to-end by a group of 4-10 real players not involved in building it
- Session completes through all three beats to the reveal
- Knowledge state enforcement works: no player receives information their character should not have
- Session persistence works: mid-game interruption restores from nearest beat
- Provider-agnostic routing abstraction is in place: no model name outside `routing_table.json`
- Structured telemetry is live for all five minimum signals
- API is documented for a technical co-founder to read without explanation
- Per-session cost model is live: AI credit tracking active, gross margin calculable
- Content safety rails are active for Nightcap's thematic territory
- At least one non-Nightcap arc schema has been designed, proving the arc format is not Nightcap-specific

## 12.4 What Can Be Built in Parallel

| Parallel track A | Parallel track B | Dependency to reunite |
| --- | --- | --- |
| Database schema + models | Arc definition JSON schema design | Both needed before arc execution engine |
| Knowledge graph | Routing + safety pipeline | Both needed before character behavior engine |
| Arc execution engine | TypeScript SDK | Both needed for end-to-end playtest |
| Simulation harness scripting | Telemetry schema design | Both needed before first instrumented session |

At MVP solo development, these tracks are sequential. With a technical co-founder, parallel tracks become real and can compress the build timeline by 30-40%.

## 12.5 H1 to H2 Transition Requirements

The transition to Horizon 2 (platform opens to external developers, monster RPG enters development) requires, beyond MVP done criteria:

- Minimum 5 completed, instrumented sessions with real groups expressing unprompted replay intent (PRD Use Proof signal)
- Willingness-to-pay or enterprise conversation proof signals met (PRD Business Signals)
- Monster RPG architecture validation confirmed (Section 14 of this document)
- External developer documentation sufficient for a closed beta (scope debt from MVP)
- Inter-service communication mechanism resolved (scope debt from Section 5)
- `dramatic_tension_score` weights validated through at least 10 playtested sessions

## 12.6 Named Scope Debt

Four items explicitly deferred from MVP with known H2 resolution points:

| Debt item | Deferred from | Resolution target |
| --- | --- | --- |
| No-code arc builder for non-developer creators | Dashboard MVP scope | H2 dashboard investment |
| Knowledge graph inference and contradiction detection | Knowledge graph simple tier | H2 monster RPG development |
| External developer documentation (public-launch quality) | MVP documentation | Before H2 closed beta |
| Inter-service communication mechanism (Cloud Tasks vs direct) | Session persistence | Before production deployment |

---

# S13 Cost Model

## 13.1 Why Cost Architecture Is a First-Class Concern

Death by AI launched with 700,000 daily users and had to make emergency architectural changes within 72 hours because AI costs were unsustainable. That is the failure mode this section exists to prevent. Cost is not an optimization to address later; it is a design input that shapes every generation decision from the first session.

## 13.2 Per-Session Cost Breakdown

Based on verified pricing from May 7, 2026, and the session model from Chat 6a research.

**Session parameters:** 60 minutes, 8 players, approximately 30 generation calls (character dialogue, narrative generation, pacing decisions) plus approximately 60 safety classification calls.

**Token estimate per session:** 75,000 input tokens, 15,000 output tokens total across all calls.

| Call category | Volume | Model | Input cost | Output cost | Subtotal |
| --- | --- | --- | --- | --- | --- |
| Character dialogue (standard) | 20 calls | Claude Haiku | ~30K tokens | ~8K tokens | ~$0.07 |
| Narrative generation (standard) | 8 calls | Claude Haiku | ~15K tokens | ~5K tokens | ~$0.04 |
| Pacing decisions | 12 calls | Llama 3.1 8B (Groq) | ~8K tokens | ~1K tokens | ~$0.001 |
| Safety classification (L2) | 60 calls | GPT-OSS-Safeguard (Groq) | ~22K tokens | ~1K tokens | ~$0.002 |
| **Total (standard tier)** |  |  |  |  | **~$0.113** |

**With prompt caching (Anthropic cache hits at 90% discount, estimated 40% hit rate on system prompts):**

Effective cost reduction on Haiku calls: ~25%. Estimated cached cost: **~$0.085 per session**.

**Premium tier uplift** (sessions where `dramatic_tension_score` pushes dialogue to Sonnet 4.6 during peak beats, estimated 20% of dialogue calls at premium):

Additional cost per session: ~$0.04. Premium-augmented session cost: **~$0.125**.

**Infrastructure cost per session** (amortized at 200 sessions/month across GCP baseline):

~$0.25 per session at low volume. Drops toward $0.05 at 1,000+ sessions/month as fixed costs amortize.

## 13.3 Self-Hosting Break-Even

From Chat 6a analysis (verified May 7, 2026):

| Scenario | Per-session AI cost |
| --- | --- |
| Managed API (current) | ~$0.11-$0.13 |
| Managed API with caching | ~$0.08-$0.10 |
| Self-hosting Llama 70B on A100 at $2/hr, 8 concurrent, 50% utilization | ~$0.51 |

**Break-even volume for self-hosting to become cheaper than managed API:** approximately 25,000-50,000 sessions per month. At that volume, the economics of dedicated GPU infrastructure begin to favor self-hosting for high-frequency task types.

**Decision rule:** stay on managed APIs through all of Horizon 2. Evaluate self-hosting at the H2-to-H3 transition when actual session volume is known. Do not build self-hosting infrastructure speculatively.

## 13.4 Cost Monitoring

Three levels of cost visibility, each serving a different decision horizon:

**Per-session gross margin** (operational, real-time):

Calculated from `generation_logs` after each session. Formula: `session_revenue - ai_cost - amortized_infrastructure_cost`. At MVP with zero revenue, this tracks cost per session as a health metric. After pricing is live, it becomes the primary unit economics signal.

**Per-arc cost average** (product, weekly):

Aggregated from `generation_logs` grouped by `arc_id`. Identifies which arc elements drive cost spikes. If the investigation beat consistently runs 3x more expensive than the introduction beat, that is a signal to review the clue generation logic.

**Routing table efficiency** (optimization, as-needed):

Compare actual model usage against the routing table's intent. If fallback activations are frequent for a specific task type, either the primary provider has a reliability problem or the task type is hitting rate limits.

## 13.5 Pricing Design Principles

Pricing for Nightcap and for the developer API is a product decision deferred to a later artifact. The cost model here informs that decision with three constraints:

1. **Minimum viable session price:** at $0.10-$0.13 per session AI cost plus infrastructure, any consumer pricing below $0.50 per session requires volume to be viable. A group-based pricing model (one purchase covers the group) rather than per-player pricing changes the economics significantly.
2. **Developer API pricing floor:** the platform cannot offer sessions to developers below its own cost of goods. The `generation_logs` per-session cost is the floor below which no plan tier can be sustainably priced.
3. **Enterprise price anchor:** Mursion charges approximately $49 per person per 30-minute session for enterprise experiential training. An Arcwright enterprise team-building session at $5-$15 per person is substantially below this anchor while remaining well above Arcwright's per-session cost. This is the Horizon 2 enterprise pricing territory to target.

---

# S14 Architecture Validation: Monster RPG and Couch Co-op

## 14.1 Purpose

Every significant architecture decision in this document must be validated against future experience types before it is treated as final. If a decision only works for Nightcap's linear arc with a fixed endpoint, it is a Nightcap-specific decision and must be labeled as such. If it silently breaks when the monster RPG requirements arrive, it is a design error.

This section validates the MVP architecture against two future experience types: the monster RPG (Horizon 2, PRD Section 5) and couch co-op play patterns (placeholder for local same-room multi-player mechanics, deferred to design in Chat 8).

## 14.2 Monster RPG Validation

The monster RPG has fundamentally different requirements from Nightcap. Five requirements from PRD Section 5 are tested here:

**Requirement 1: World state persistence independent of any individual session.**

The monster RPG world exists between sessions. A player's trainer level, the gym leader's memory of prior encounters, and town-level events persist across many sessions.

Validation: the current architecture stores all state within a `session_id`. World-level persistence requires a new `world_state` table and `world_instance_id` as a first-class concept alongside `session_id`. This is an extension, not a rebuild: the session model gains a `world_instance_id` foreign key, and a new set of tables manages world state. No existing session logic changes.

**Requirement 2: Emergent narrative arcs with no designed endpoint.**

Nightcap has a fixed reveal as the terminal state. The monster RPG has no single designed ending: the player's story is whatever they make of it.

Validation: the `ArcStateChart` supports this. A world-arc's beat graph has no terminal state: the `is_terminated` check returns false indefinitely. The statemachine loops on ongoing-state beats. Pacing logic changes (no reveal to accelerate toward) but the architecture accommodates it. The arc definition format's `beat_graph` simply has no empty next-beat list; beats loop back on themselves based on world events.

**Requirement 3: Procedural generation at the world layer.**

Terrain, NPC populations, and event distributions are procedurally generated, distinct from the AI narrative layer.

Validation: procedural generation is a separate system that produces structured data consumed by the arc execution engine as authored content for that session. The engine does not need to know it was procedurally generated vs. manually authored. A new `world_generation` module produces the `locations`, `objects`, and NPC character schemas that seed the session. This module is additive; it does not touch existing engine components.

**Requirement 4: Player-defined motivation inference.**

Rather than being assigned a role, the monster RPG player's motivation is inferred from their behavior.

Validation: the behavior engine's generation pipeline already accepts dynamic `behavior_profile` updates mid-session. Player motivation inference is a new task type (`player_motivation_inference`) added to the routing table, producing a structured motivation object that is written back to the player's `behavior_profile.goals` field. The knowledge graph, event system, and character model require no changes.

**Requirement 5: Simultaneous multi-player world state with no single endpoint.**

Multiple players in the same world instance are living different stories simultaneously.

Validation: the event system's `target_audience` model already supports per-player routing. The session coordinator loop will need to manage multiple concurrent story threads, which increases complexity but does not require architectural restructuring. The `SessionConnectionRegistry` handles multiple players natively. The primary new challenge is world state consistency across concurrent player actions: a locking strategy for world state mutations is required and is scoped to H2 design.

**Monster RPG validation summary:**

| Requirement | Architecture verdict | Work required |
| --- | --- | --- |
| World state persistence | Extension (new tables, new foreign key) | Low |
| Emergent narrative | Native (beat graph with no terminal state) | None |
| Procedural generation | Additive (new module, engine unchanged) | Medium |
| Motivation inference | Additive (new task type, routing table entry) | Low |
| Multi-player world state | Extension (world state locking strategy) | Medium (H2 design) |

No component in the MVP architecture requires a rebuild to support monster RPG requirements.

## 14.3 Couch Co-op Placeholder

Couch co-op describes same-room multi-player patterns where players share a physical space and may share a single display while having individual input devices. This is distinct from Nightcap's phone-per-player model in that input device assignment, display sharing, and local network play introduce new delivery constraints.

Placeholder capabilities that the architecture must not foreclose:

- Shared screen rendering for multiple players on one device
- Local input handling without per-player phone requirement
- Low-latency same-room interaction (sub-200ms event delivery)
- Mixed cooperative-competitive mechanics on a single shared arc

These requirements do not conflict with the current architecture. The event system's surface-agnostic design and the SDK's thin client model leave room for a couch co-op delivery adapter. Full design is deferred to Chat 8 (Story Bible: Monster RPG), where the specific arc type will inform which couch co-op patterns are actually needed.

## 14.4 Architecture Fitness Summary

The MVP architecture passes validation for Horizon 2 requirements. All necessary extensions are additive. No committed decision requires reversal or rebuild to support the monster RPG or couch co-op patterns. The boundary between platform components and game-specific components is clean enough that new arc types require new arc definition files and targeted module additions, not changes to the platform foundation.

---

# S15 Agentic Development Guide

**Purpose.** This section is the primary input for Claude Code. Every component definition is unambiguous: input schema, output contract, acceptance criteria, dependencies, and must-not-do guards are explicit. Claude Code builds against this guide without asking the founder to explain decisions. All locked architectural decisions are in 02-Decisions-Log (Chat 6a entries, May 7 2026). This guide operationalizes decisions; it does not restate rationale.

---

## 15.1 Repository Structure and First File

```
arcwright/
  engine/                  # Python: core platform library
    arc/                   # Arc execution engine (python-statemachine StateChart)
    characters/            # Character model and behavior engine
    knowledge/             # Knowledge graph and state management
    routing/               # AI model routing abstraction layer
    safety/                # Content safety pipeline
    events/                # Content event system
    session/               # Session state and persistence
    telemetry/             # Telemetry schema and logging
    tests/                 # Unit and simulation harness
  api/                     # FastAPI thin wrapper over engine
    routers/               # Route handlers (session, character, knowledge, events)
    auth/                  # Firebase Auth + API key middleware
    schemas/               # Pydantic request/response models
  sdk/                     # TypeScript web SDK (MVP)
  dashboard/               # TypeScript React dashboard
  migrations/              # Alembic database migrations
  nightcap/                # Nightcap arc definition files (JSON)
  config/                  # Environment config, routing_table.json
  scripts/                 # GCP setup scripts, seed data
```

**First file to create:** `engine/session/models.py`. This file defines the Session, SessionParticipant, and ArcBeat Pydantic models. Every other component depends on what a session is. Do not write any other file before this one exists and its schema is stable.

---

## 15.2 Environment and Core Dependencies

```
# requirements.txt (engine + api)
python-statemachine>=3.0
fastapi>=0.111
uvicorn[standard]
asyncpg
sqlalchemy[asyncio]>=2.0
alembic
pydantic>=2.0
litellm>=1.30
firebase-admin
pgvector
python-dotenv
httpx
structlog
```

```
# .env.example
DATABASE_URL=postgresql+asyncpg://user:pass@host/arcwright
FIREBASE_PROJECT_ID=arcwright-prod
LITELLM_DEFAULT_ROUTING_TABLE=config/routing_table.json
CONTENT_LOGGING_ENABLED=false
ANTHROPIC_API_KEY=
GROQ_API_KEY=
```

`CONTENT_LOGGING_ENABLED=false` is the feature flag controlling full population of `generation_logs`. The table schema exists from day one. Prompt and output text write only when this flag is true. See Section 11 for the full generation_logs schema.

---

## 15.3 Database: Cloud SQL PostgreSQL Setup

First Alembic migration creates tables in this order (dependencies drive order; do not reorder):

1. Enable `pgvector` extension (`CREATE EXTENSION IF NOT EXISTS vector`)
2. `accounts`
3. `consent_records`
4. `characters` (includes `behavior_profile JSONB`, `embedding VECTOR(1536) NULL`)
5. `facts` (includes `embedding VECTOR(1536) NULL`)
6. `knowledge_states`
7. `relationships`
8. `locations`
9. `objects`
10. `decisions`
11. `events` (append-only; includes `embedding VECTOR(1536) NULL`)
12. `sessions`
13. `session_participants`
14. `arc_beat_states`
15. `generation_logs` (full schema; `prompt_text TEXT NULL`, `output_text TEXT NULL`, `prompt_embedding VECTOR(1536) NULL` nullable at MVP; populated only when `CONTENT_LOGGING_ENABLED=true`)
16. `decision_logs`

**Session as a data structure:**

```python
class Session(BaseModel):
    session_id: UUID
    arc_id: str                    # references arc definition file
    status: SessionStatus          # created | active | paused | completed | abandoned
    host_account_id: UUID
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    current_beat_id: str
    quality_tier: QualityTier      # standard | premium
    player_count: int

class SessionParticipant(BaseModel):
    participant_id: UUID
    session_id: UUID
    character_id: UUID
    account_id: UUID | None        # None for anonymous players
    join_token: str                # short-lived JWT for game client auth
    surface_type: str              # phone | shared_display | host
    is_ai_controlled: bool
```

---

## 15.4 Arc Definition Schema

Arc definitions are JSON files. Nightcap's arc definition lives at `nightcap/arc.json`. The platform reads this schema; it does not generate arc structure.

```python
class CharacterMode(str, Enum):
    authored   = "authored"    # fixed character definitions in arc schema
    generated  = "generated"   # characters generated at session start from typed slots
    hybrid     = "hybrid"      # some authored, some generated

class AestheticMode(str, Enum):
    fixed    = "fixed"         # single fixed aesthetic defined in arc
    palette  = "palette"       # selection from a defined list of options
    generative = "generative"  # fully generated at session start

class PlayMode(str, Enum):
    imposter       = "imposter"       # one player is the killer; plays to avoid detection
    detective_race = "detective_race" # all players are investigators competing to solve first
    cooperative    = "cooperative"    # all players work together

class NarratorConfig(BaseModel):
    type: str                  # "host_persona" | "voice" | "environmental"
    surface: str               # "shared_display" | "all" | "none"
    persona_mode: str          # "fixed" | "palette" | "aesthetic_linked" | "generative"
    behavior_triggers: list[str]  # ["beat_transition", "clue_release", "tension_threshold", "player_inaction"]
    omniscient: bool           # narrator has full session knowledge state
    player_addressable: bool   # narrator can address individual players by name

class ArcDefinition(BaseModel):
    arc_id: str
    name: str
    min_players: int
    max_players: int
    character_mode: CharacterMode
    aesthetic_mode: AestheticMode
    setting_constraint: str | None  # e.g. "social_gathering"; None means unconstrained
    arc_structure: str              # "dan_harmon" | "heros_journey" | "man_in_hole" | "custom"
    play_mode: PlayMode
    narrator: NarratorConfig
    quality_tier_default: QualityTier
    characters: list[CharacterSchema]
    beats: list[BeatDefinition]
    beat_graph: dict[str, list[str]]   # beat_id -> list of valid next beat_ids
    generative_elements: GenerativeConfig
    content_rails: ContentRailsConfig
    knowledge_rules: KnowledgeRuleSet  # initial knowledge state seeded at session start

class BeatDefinition(BaseModel):
    beat_id: str
    beat_name: str                     # human-readable beat label (e.g. "The Arrival")
    beat_type: BeatType                # introduction | investigation | reveal | epilogue
    story_circle_step: int | list[int] # Story Circle position(s) this beat maps to (1-8)
    structural_function: str           # platform tag: e.g. "establish_comfort", "surface_disruption"
                                       # pre-populated for story_circle arcs; required for custom arcs
    dramatic_purpose: str | None       # free-text director's note; required if arc_structure = "custom"
    emotional_target: str | None       # target player emotional state at beat's end
    information_goal: str | None       # what players should know/discover by beat's end
    tension_target: float | None       # pacing engine tension target (0.0-1.0) for this beat
    character_emphasis: list[str]      # character slot IDs foregrounded in this beat
    authored_content: dict | None      # fixed narrative content if any
    generative_triggers: list[str]     # which generative elements activate in this beat
    entry_conditions: list[str]        # logical conditions that must be true to enter
    exit_conditions: list[str]         # logical conditions that trigger next beat transition
    pacing_config: PacingConfig        # stall threshold, acceleration trigger, misdirection trigger
    audience_targets: list[AudienceTarget]
    mini_games: list[MiniGameConfig] | None  # available in beats 1-3; outputs feed killer_assignment_logic
```

Nightcap has three top-level beats: `introduction`, `investigation`, `reveal`. `investigation` is a `State.Compound` in the statemachine with internal sub-beats for clue distribution phases. The killer identity is AI-assigned at `introduction` entry via a generative trigger; the assignment is stored in session state and constrains all subsequent character behavior generation.

---

## 15.5 Knowledge State: Assertion API

```python
# Engine internal function signature
async def assert_knowledge(
    session_id: UUID,
    character_id: UUID,
    fact_type: str,                      # "clue" | "accusation" | "relationship" | "event"
    fact_content: dict,
    source_character_id: UUID | None,    # who told them; None if environmental
    confidence: float = 1.0,             # 0.0-1.0; enables deception modeling
    expires_at: datetime | None = None
) -> KnowledgeStateRecord: ...

# HTTP endpoint
# POST /v1/sessions/{session_id}/knowledge
{
  "character_id": "<uuid>",
  "fact_type": "clue",
  "fact_content": {"clue_id": "c1", "text": "The victim was in the library at 9pm"},
  "source_character_id": null,
  "confidence": 1.0
}
```

**Non-negotiable constraint:** Every AI character response generation call must call `get_character_knowledge(session_id, character_id)` before constructing the generation prompt. The knowledge state result is injected into the system prompt as a constraint block. This call is not optional and cannot be skipped for performance reasons.

---

## 15.6 Content Event Schema

```python
class ContentEvent(BaseModel):
    event_id: UUID
    session_id: UUID
    event_type: ContentEventType        # narration | dialogue | clue | system | pacing
    actor_id: UUID | None               # character who produced this event
    target_audience: AudienceTarget     # all | host_only | specific_player | shared_display
    target_player_id: UUID | None       # set when target_audience = specific_player
    payload: dict                       # event-type-specific structured content
    presentation_hints: PresentationHints
    timestamp: datetime

class PresentationHints(BaseModel):
    emotion: str | None                 # "tense" | "warm" | "suspicious" | "neutral"
    urgency: str | None                 # "low" | "medium" | "high"
    voice_hint: str | None
    animation_hint: str | None
    lighting_hint: str | None
```

The engine emits `ContentEvent` objects to a session event stream. It does not know what renders them. No field in this schema names a surface type (TV, phone, browser). The consuming layer (Nightcap) maps events to surfaces.

---

## 15.7 AI Model Routing: First Call and Routing Table

**First provider to call at MVP:** Anthropic via LiteLLM, in-process. No proxy server at MVP.

```python
# engine/routing/router.py
import litellm, json
from pathlib import Path

_table = json.loads(Path("config/routing_table.json").read_text())

async def route_generation(
    task_type: str,
    quality_tier: str,
    messages: list[dict],
    temperature: float = 0.7
) -> str:
    model_key = _table[task_type][quality_tier]
    response = await litellm.acompletion(
        model=model_key,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content
```

```json
// config/routing_table.json (MVP defaults)
{
  "character_dialogue": {
    "standard": "anthropic/claude-haiku-4-5-20251001",
    "premium": "anthropic/claude-sonnet-4-6"
  },
  "pacing_decision": {
    "standard": "groq/llama-3.1-8b-instant",
    "premium": "groq/llama-3.1-8b-instant"
  },
  "safety_classification": {
    "standard": "groq/gpt-oss-safeguard-20b",
    "premium": "groq/gpt-oss-safeguard-20b"
  },
  "knowledge_inference": {
    "standard": "groq/llama-3.1-8b-instant",
    "premium": "groq/llama-3.3-70b-versatile"
  },
  "narrative_generation": {
    "standard": "anthropic/claude-haiku-4-5-20251001",
    "premium": "anthropic/claude-sonnet-4-6"
  }
}
```

No model name or provider string appears anywhere in the codebase outside `routing_table.json` and `router.py`. Switching a routing table entry requires zero code changes.

---

## 15.8 MVP GCP Infrastructure

| Service | Configuration | Estimated monthly cost |
| --- | --- | --- |
| Cloud Run (API service) | 1 vCPU, 512 MB RAM, min-instances=0, max=10 | $5-20 |
| Cloud Run (engine worker) | 2 vCPU, 1 GB RAM, min-instances=0, max=5 | $10-30 |
| Cloud SQL PostgreSQL 15 | db-f1-micro, 10 GB SSD, single region | $10-15 |
| Firebase Auth | Spark plan | Free |
| Cloud Storage (telemetry backups) | Nearline, under 1 GB at MVP | Under $1 |
| **Total MVP estimate** |  | **$25-66/month** |

Two Cloud Run services at MVP: the API service (FastAPI, handles REST requests and SSE streams) and the engine worker service (asyncio, handles beat transitions and AI generation tasks). Both share Cloud SQL. Inter-service communication mechanism (Cloud Tasks vs direct async invocation) is a scope debt item resolved in Section 5 of this document.

---

## 15.9 Component Build Order

| Priority | Component | Acceptance criteria | Must NOT do |
| --- | --- | --- | --- |
| 1 | Session models + DB migration | All 16 tables exist; pgvector enabled; `alembic upgrade head` completes with zero errors | Do not add Nightcap-specific columns to platform tables |
| 2 | Knowledge graph core | `assert_knowledge`, `get_character_knowledge`, `revoke_knowledge` pass unit tests; AI response never references a fact outside the queried character knowledge state | Do not make knowledge state optional or a performance trade-off |
| 3 | Model routing abstraction | All generation calls route through `router.py`; no model name appears outside `routing_table.json`; swapping a table entry changes behavior with zero code changes | Do not hardcode any provider name outside `routing_table.json` |
| 4 | Arc execution engine (Nightcap arc) | Nightcap arc executes through all three beats in simulation harness; killer identity assigned at introduction; all beats reachable; session completes with reveal | Do not encode beat logic that only functions with linear arcs and fixed endpoints |
| 5 | Content safety pipeline | L1 hard stops block prohibited content before generation; L2 Safeguard classification fires before every generation call; all safety activations logged to `events` table | Do not add safety as a post-generation filter only; hard stops must be pre-generation |
| 6 | Content event system | Events emitted with correct `target_audience`; no event targeting player A is delivered to player B; shared_display events contain no private character information | Do not couple event emission to any named surface type |
| 7 | Character behavior engine | AI dialogue is consistent with `behavior_profile`; dialogue never references a fact outside the character's knowledge state; NPC-NPC interaction produces a coherent exchange without human input | Do not generate a character response without first querying that character's knowledge state |
| 8 | FastAPI layer + auth | Session create, start, event stream, and knowledge assert endpoints return correct schemas; API key auth passes; Firebase JWT validation passes | Do not put arc execution logic in route handlers |
| 9 | Session persistence | Mid-session interruption followed by resume restores to nearest designed beat; no knowledge state is lost; no session restarts from the beginning | Do not treat persistence as a post-MVP concern |
| 10 | Telemetry MVP minimum | Five minimum signals logging from the first production session; generation_logs table present with nullable columns; `CONTENT_LOGGING_ENABLED` flag controls full population | Do not run a session without telemetry active; sessions without telemetry are cost with no data return |
| 11 | Simulation harness | Synthetic player run completes full Nightcap arc end-to-end; seeded deterministic run produces identical output on repeated execution; batch tool runs 10 sessions headless | Do not ship to real users before the simulation harness validates the arc |

---

## 15.10 Monster RPG Reuse Boundary

When monster RPG development begins, these components require no changes:

- Session models (world sessions extend Session, not replace it)
- Knowledge graph (same assertion/revocation/query API; schema complexity increases via extensible schema, not restructure)
- Model routing (routing table gains new task types; abstraction layer unchanged)
- Content event system (new event types registered; emitter unchanged)
- Content safety pipeline (new content rails config; pipeline unchanged)
- FastAPI auth layer (unchanged)

These components require extension (new code added, no rewrites):

- Arc execution engine: world state persistence between sessions, emergent narrative beat types, procedural generation hooks
- Character behavior engine: player-defined motivation inference, dynamic difficulty adjustment, simultaneous multi-player world state tracking

**Validation rule:** If any component in the "no changes required" list above requires modification to support the monster RPG, that is a design error in the Nightcap implementation that must be identified and corrected before monster RPG development starts.

---
## SOURCE FILE: docs/architecture/01-overview.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# System Architecture Overview

## 1.1 What Arcwright Is as a Technical System

Arcwright is Layer 2 narrative runtime middleware. Layer 1 is foundation model infrastructure (Anthropic, Google, Groq, open source models). Layer 3 is the experience layer (Nightcap, the monster RPG, third-party developer games). Arcwright sits between them: it takes a human-authored arc definition and a group of real players, and produces a coherent, unrepeatable session experience at runtime.

This positioning is not a marketing choice. It is the architectural commitment that determines what Arcwright builds, owns, and maintains. Arcwright does not train foundation models. It does not build game engines or rendering surfaces. It orchestrates the narrative runtime between the raw AI capability layer and the experience delivery layer.

## 1.2 Component Stack

| Layer | Component | Language | Responsibility |
| --- | --- | --- | --- |
| Experience | Nightcap, monster RPG, third-party games | Any | Arc definition, surface rendering, player onboarding |
| **Platform: API** | **FastAPI service** | **Python** | **REST + SSE transport, auth, schema validation, rate limiting** |
| **Platform: Engine** | **arcwright-engine library** | **Python** | **Arc execution, knowledge graph, character behavior, routing, safety, events, telemetry** |
| **Platform: SDK** | **TypeScript web SDK** | **TypeScript** | **Game client connection, event subscription, player input submission** |
| Infrastructure | Cloud SQL, Cloud Run, Firebase Auth | GCP managed | Persistence, compute, identity |
| AI supply chain | Anthropic, Groq, open source via LiteLLM | External | Foundation model inference |

The engine library is the primary product. The API is a thin HTTP wrapper around it. The SDK layer is plural: the TypeScript web SDK is the first wrapper, generated from the OpenAPI source of truth, while future engine SDKs (Unity in C#, Unreal in C++ with Blueprints integration, Godot in GDScript or C#, and native mobile in Swift or Kotlin if pursued) are separate native-language wrappers around the same REST API. Neither the API nor any SDK contains game logic or arc execution logic.

## 1.3 How Nightcap Sits on the Stack

Nightcap is an experience built on the platform. It contributes:

- An arc definition file (`nightcap/arc.json`) that specifies characters, beats, generative elements, knowledge rules, and content rails
- A host interface (web app) that drives session creation and shared display rendering
- A player interface (phone browser) that renders private events and accepts player input
- No engine code. All arc execution, knowledge state management, character behavior, model routing, and content safety run in the platform engine.

If Nightcap disappeared tomorrow, the engine would still run any other arc definition unchanged.

## 1.4 Architecture Principles to Implementation Mapping

Eight principles from PRD Section 3 map to specific technical implementations in this document. Cross-references for each:

| PRD Principle | Implementation | Document Section |
| --- | --- | --- |
| Surface agnosticism | ContentEvent schema with `target_audience` and `presentation_hints`; no surface type in engine | S8 |
| Human arc primacy | ArcDefinition schema with `authored` vs `generative` flags per element; arc execution enforces authored constraints regardless of AI output | S3 |
| Configurable composition | `generative_elements: GenerativeConfig` per arc; per-element authored/generative dial | S3 |
| Unified character model | Single `Character` object for human and AI participants; behavior source (AI engine vs input channel) is the only difference | S7 |
| Knowledge graph as first-class infrastructure | `knowledge_states` table, `assert_knowledge` / `get_character_knowledge` / `revoke_knowledge` API; not optional; enforced before every AI generation call | S4 |
| Cost-aware architecture | LiteLLM routing table maps task type + quality tier to current cheapest option; pacing and safety route to small models on Groq; generation routes to capable models on Anthropic | S6 |
| Progressive proprietary infrastructure | Tier 1 (deterministic infrastructure) built at MVP; Tier 2 (fine-tuned models) triggered by volume and data; Tier 3 (foundation model development) never | S6, S12 |
| Provider-agnostic model routing | All model calls through `engine/routing/router.py`; no provider name outside `routing_table.json`; routing table swap requires zero code changes | S6 |

## 1.5 What Arcwright Is Not Responsible For

These are explicit non-responsibilities. A proposed requirement that pushes into this territory signals either scope creep or a Nightcap-specific decision being misclassified as a platform decision:

- Rendering any surface (TV, phone, browser, voice interface). The engine emits events; Nightcap renders them.
- Storing player payment information or managing subscriptions. This is the game layer's responsibility.
- Generating arc structure. The platform executes and personalizes a human-designed arc. It does not write the arc.
- Operating as a general-purpose LLM API or chatbot infrastructure. Inworld pivoted here. Arcwright does not.
- Managing CDN, media delivery, or audio/video streaming. The platform handles text and structured events.
- Foundation model training or fine-tuning at MVP. Session telemetry is collected; fine-tuning is a Tier 2 trigger gated on volume.

---
## SOURCE FILE: docs/architecture/02-technology-stack.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# Technology Stack

All decisions in this section are locked (Chat 6a, May 7 2026). Rationale is summarized here; full rationale is in 02-Decisions-Log. Alternatives considered are listed to prevent re-litigation during implementation.

## 2.1 Decision Summary Table

| Area | Decision | Version | Locked decision reference |
| --- | --- | --- | --- |
| Cloud provider | GCP | Current | Decision 3 |
| Compute | Cloud Run (containerized, serverless) | Current | Decision 3 |
| Database | Cloud SQL PostgreSQL | 15 | Decision 5 |
| Vector extension | pgvector | Latest stable | Decision 6 |
| Auth platform | Firebase Auth | Current | Decision 19 |
| Engine language | Python | 3.11+ | Decision 4 |
| API framework | FastAPI | 0.111+ | Implied by Decision 4 |
| Async runtime | Python asyncio | stdlib | Implied by Decision 11 |
| ORM | SQLAlchemy async | 2.0+ | Implied by Decision 4 |
| Migrations | Alembic | Latest stable | Implied by Decision 4 |
| Arc execution | python-statemachine StateChart | 3.0+ | Decision 11 |
| Transport | SSE (server push) + POST (client input) | HTTP/1.1 | Decision 10 |
| AI routing | LiteLLM in-process | 1.30+ | Decision 14 |
| Safety L2 | GPT-OSS-Safeguard 20B on Groq | Current | Decision 16 |
| SDK language | TypeScript | 5.x | Decision 4 |
| Dashboard framework | React (TypeScript) | 18+ | Implied by Decision 4 |

## 2.2 Compute and Infrastructure

**GCP + Cloud Run.** Serverless containers with scale-to-zero. At MVP scale (dozens of sessions, not thousands), minimum monthly cost is under $70 total for all services. Cloud Run eliminates VM management and automatic scaling handles uneven session load without pre-provisioned capacity.

Two Cloud Run services at MVP:

| Service | Purpose | Resources | Notes |
| --- | --- | --- | --- |
| `arcwright-api` | FastAPI HTTP and SSE handler | 1 vCPU, 512 MB | Stateless; scales on request count |
| `arcwright-worker` | Arc execution, AI generation tasks | 2 vCPU, 1 GB | Stateful per session; see Section 5 for session affinity approach |

**Rejected alternatives:**

- AWS + Neon: Neon is AWS-only. GCP was preferred for Cloud Run ergonomics and pgvector on Cloud SQL. (Decision 5)
- Kubernetes: over-engineered for MVP solo development; revisit at H2 if session volume demands horizontal scaling architecture.
- Single service monolith: acceptable at MVP but the API / worker split is cleaner for session affinity and background arc execution. The split is low cost with Cloud Run.

**Cloud SQL PostgreSQL 15.** Managed relational database. pgvector extension enabled at first migration for embedding-ready schema (`VECTOR(1536) NULL` columns on `characters`, `facts`, `events`, `generation_logs`). These columns are nullable at MVP; populated only when fine-tuning data collection activates. The schema is designed once; embedding capability costs nothing until used.

Instance at MVP: `db-f1-micro`, single region, 10 GB SSD. Cost: ~$10-15/month. Upgrade path to `db-g1-small` or higher is a Cloud SQL setting change, not a migration.

## 2.3 Languages

**Python 3.11+ (engine + API).** The engine library and FastAPI service are Python. 3.11 is the minimum for performance improvements in the async runtime and `tomllib` stdlib inclusion. Do not use Python below 3.11 anywhere in the codebase.

**TypeScript 5.x (web SDK + dashboard).** The web SDK and React dashboard are TypeScript. Strict mode enabled. No `any` types in the SDK public interface. TypeScript is not the language for every future engine SDK. Unity, Unreal, Godot, and native mobile wrappers require their native ecosystems while wrapping the same REST API and OpenAPI contract.

**Language boundary rule:** Python owns all arc execution, knowledge graph, character behavior, model routing, content safety, and session state logic. TypeScript owns all client-facing rendering, event subscription, and player input submission logic. No arc execution logic crosses into TypeScript.

## 2.4 Data Layer

**SQLAlchemy 2.0 async + asyncpg.** Async ORM for all database access from the engine. SQLAlchemy 2.0 async style (not the legacy 1.x style). `asyncpg` as the PostgreSQL driver. All queries go through SQLAlchemy; no raw SQL in application code except migrations.

**Alembic.** Database migrations. All schema changes are Alembic migrations. No manual schema changes applied directly to Cloud SQL. Migration files are version-controlled.

**pgvector.** Enabled via `CREATE EXTENSION IF NOT EXISTS vector` in the first migration. `VECTOR(1536)` columns are present from day one on `characters.embedding`, `facts.embedding`, `events.embedding`, and `generation_logs.prompt_embedding`. Dimension 1536 matches OpenAI `text-embedding-3-small` and Anthropic's current embedding output. If the embedding model changes, the dimension may need a migration; design for this possibility.

**Knowledge graph storage:** Pure relational at MVP. State tables (`characters`, `facts`, `knowledge_states`, `relationships`) plus append-only `events` log. Apache AGE (graph extension for PostgreSQL) is addable later if the monster RPG's emergent narrative requires graph traversal queries that are expensive in SQL. Do not add AGE at MVP; the SQL schema is sufficient for Nightcap and is designed to be AGE-compatible.

## 2.5 API and Transport

**FastAPI 0.111+.** HTTP API framework. Route handlers are thin: they validate input (Pydantic schemas), call engine functions, and return responses. No arc logic in route handlers.

**Transport: SSE + POST with adapter pattern.**

- Server to client (content events, arc beat updates, narrator output): SSE stream. Each connected client (phone browser, shared display) maintains a persistent SSE connection to `arcwright-api`.
- Client to server (player input, accusations, host commands): HTTP POST to REST endpoints.
- Transport adapter pattern: the engine emits `ContentEvent` objects to an abstract event bus. The SSE delivery layer subscribes to the bus and fans out to connected clients by `target_audience`. Switching from SSE to WebSockets in the future requires replacing the delivery layer adapter only; the engine does not change.

**Rejected alternatives:**

- WebSockets: more complex to manage connection state at MVP; SSE is sufficient for server-push and simpler to implement with FastAPI's `EventSourceResponse`. Revisit if bidirectional real-time is required for a future arc type.
- GraphQL subscriptions: unnecessary complexity at MVP.

## 2.6 Arc Execution

**python-statemachine 3.0+ (StateChart base class).** SCXML-compliant statechart library. `StateChart` is the base class (not `StateMachine`, which is the legacy 2.x-compatible class). Parallel regions (`State.Parallel`), compound states (`State.Compound`), history states, delayed events, and invoked sub-machines are all available natively. See Section 3 for the full arc execution engine design.

Verified May 11 2026: v3.0 supports all required arc graph patterns (branching, convergence, loops, parallel regions, conditional transitions via `cond=`).

## 2.7 AI Supply Chain

**LiteLLM 1.30+ in-process.** Single Python library that abstracts all AI provider calls. Initialized in-process at MVP; no sidecar proxy. Upgrade to LiteLLM Proxy Server in H2 if multi-service routing or centralized logging becomes necessary.

Routing table at `config/routing_table.json` maps task type + quality tier to current model. No model name or provider string appears outside this file and `engine/routing/router.py`.

**Safety L2: GPT-OSS-Safeguard 20B on Groq.** Pre-generation safety classification. Supports bring-your-own-policy. Groq inference: fast and cheap (~$0.075/million input tokens; output rate pending verification per Open Question in 03-Open-Questions-Log). See Section 10 for full safety pipeline.

**Pricing reference (verified May 7 2026):**

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Use in routing table |
| --- | --- | --- | --- |
| Claude claude-haiku-4-5 (Anthropic) | $1.00 | $5.00 | standard dialogue, standard narrative |
| Claude claude-sonnet-4-6 (Anthropic) | $3.00 | $15.00 | premium dialogue, premium narrative |
| Llama 3.1 8B (Groq) | $0.05 | $0.08 | pacing decisions, knowledge inference (standard) |
| Llama 3.3 70B (Groq) | $0.59 | $0.79 | knowledge inference (premium) |
| GPT-OSS-Safeguard 20B (Groq) | ~$0.075 | TBC | safety classification (all tiers) |

Batch API (50% discount on Anthropic) is not used at MVP due to real-time session requirements. Prompt caching (90% discount on cache hits) is used where system prompts and arc definitions are stable across calls within a session.

## 2.8 Auth

Three token types, three use cases:

| Token type | Issued by | Used for | Lifetime |
| --- | --- | --- | --- |
| Firebase ID token | Firebase Auth | Dashboard access, host session creation | 1 hour, refresh via SDK |
| API key | Arcwright platform | Developer API access (H2+; internal use at MVP) | Until revoked |
| Session join JWT | Arcwright API at session creation | Player game client auth | Session duration + 30 min grace |

Anonymous player join: players receive a session join JWT via QR code or invite link. No Firebase account required to join as a player. Account creation is offered post-session (optional).

## 2.9 Testing Approach

Focused unit tests at MVP on four areas (Decision 21): knowledge graph correctness, arc state transitions, safety enforcement, model routing fallback. Manual testing elsewhere. Full simulation harness at MVP (Decision 22): AI-driven synthetic players, seeded deterministic runs, scenario scripting, batch statistics, replay. See Section 15.9 for acceptance criteria per component.

## 2.10 Chat 9 Platform-Clean Architecture Addendum

The build path remains: build for Nightcap, design platform-clean. Platform-clean means clean internal abstractions and game-agnostic schemas from day one. It does not mean external API exposure during H1. External developer exposure is gated by product signals, including Nightcap profitability and non-Nightcap external developer demand.

Schema design is platform-clean from day one and includes all fields needed for full functionality. Implementation is staged. Nightcap MVP receives minimum-viable implementations of advanced features; Monster RPG H2 fills in sophisticated implementations. The schema should not change between MVP and H2 solely because the MVP implementation is simplified.

Visual Storyworld Phase 1 is part of H1 dashboard architecture. Phase 1 includes inspection-only surfaces: live knowledge graph visualization, read-only arc structure view, live event stream, and character state inspection. These surfaces support debugging and developer understanding without committing to a no-code editor at MVP.

---
## SOURCE FILE: docs/architecture/03-arc-execution.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# Arc Execution Engine

The arc execution engine is the core of the platform. It takes an arc definition and a live session, advances the session through designed beats, enforces authored constraints, triggers AI generation at configured points, and emits content events. It does not render anything. It does not know what a TV or phone is. It produces a stream of `ContentEvent` objects and session state updates.

## 3.1 StateChart Architecture

Each session instantiates one `ArcStateChart`, a subclass of `python-statemachine`'s `StateChart`. The chart represents the arc's beat graph: states are beats, transitions are arc progressions, guards are authored entry and exit conditions.

```python
from statemachine import StateChart, State

class NightcapArcChart(StateChart):
    # Top-level beats
    class introduction(State.Compound, initial=True):
        onboarding = State(initial=True)
        killer_assignment = State()
        motive_reveal = State(final=True)
        begin_game = onboarding.to(killer_assignment)
        motives_established = killer_assignment.to(motive_reveal)

    class investigation(State.Compound):
        class clue_phase(State.Parallel):
            class private_clues(State.Compound):
                distributing = State(initial=True)
                distributed = State(final=True)
                clues_sent = distributing.to(distributed)
            class interrogation(State.Compound):
                open = State(initial=True)
                closed = State(final=True)
                interrogation_complete = open.to(closed)
        resolution = State(final=True)
        phases_complete = clue_phase.to(resolution)

    reveal = State(final=True)

    # Arc-level transitions
    investigation_begins = introduction.to(investigation)
    accusation_filed = investigation.to(reveal)
```

The `introduction` beat uses `State.Compound` with internal sub-beats for onboarding, killer assignment, and motive establishment. The `investigation` beat uses `State.Parallel` so private clue distribution and group interrogation run simultaneously: the parallel region's `done.state` event fires only when both regions reach final, which is the engine's signal that investigation is complete. `reveal` is the terminal state.

Runtime conditional transitions use `cond=` guards. Example: the engine does not advance to `reveal` until the accusation meets the minimum evidence threshold defined in the arc definition. If a host forces early reveal, the guard is bypassed via a host-privileged event, logged as a pacing intervention.

## 3.2 Beat Graph Model

Beat graphs support four structural patterns:

| Pattern | Implementation | Example use |
| --- | --- | --- |
| Linear sequence | `state_a.to(state_b)` | Introduction to investigation |
| Branching | Multiple transitions from one state with `cond=` guards | Investigation extends vs. early reveal |
| Convergence | Multiple sources to one target | Different investigation paths all reach reveal |
| Loop | Transition back to earlier state | Re-investigation if accusation fails |

All four patterns are native to python-statemachine v3.0. No custom graph traversal code is required.

Arc definitions specify the beat graph as `beat_graph: dict[str, list[str]]` (beat_id to valid next beat_ids) plus `entry_conditions` and `exit_conditions` per beat. The StateChart class is generated at session start from the arc definition, not written statically per arc. This means new arcs require only a new arc definition JSON file, not a new StateChart subclass.

## 3.3 Pacing Engine

The pacing engine runs as a single asyncio background task per session. It computes a `dramatic_tension_score` (0.0 to 1.0) on a configurable interval (default: 30 seconds) and drives all pacing decisions from that one score.

**dramatic_tension_score computation:**

```python
class DramaticTensionScore:
    """Weighted composite of four session signals. Weights are arc-configurable."""
    def compute(self, session: SessionState, config: PacingConfig) -> float:
        time_pressure = self._time_in_beat_score(session, config)     # rises as beat ages
        action_rate   = self._player_action_rate(session)              # falls when players stall
        suspicion     = self._correct_suspicion_confidence(session)    # rises as killer identified
        clue_coverage = self._clue_distribution_completeness(session)  # rises as clues dealt

        return (
            config.w_time     * time_pressure  +
            config.w_action   * action_rate    +
            config.w_suspicion * suspicion     +
            config.w_coverage * clue_coverage
        )
```

Weights (`w_time`, `w_action`, `w_suspicion`, `w_coverage`) are stored in `pacing_config` inside the arc definition. Nightcap's default weights are a design choice that will require iteration during playtesting; the architecture supports weight adjustment without code changes.

**Intervention thresholds (all read from the single score):**

| Condition | Threshold | Action | Model route |
| --- | --- | --- | --- |
| Score falls below `stall_threshold` (default 0.25) | Players have stalled | Inject clue or narrator prompt | `pacing_decision` resolved by routing table |
| Score rises above `misdirection_threshold` (default 0.80) and remains below `premium_threshold` | Players solving too quickly | Inject red herring via a character whose behavior has been too transparent | `narrative_generation` resolved by routing table |
| Score reaches or exceeds `premium_threshold` (default 0.85) | Peak dramatic moment | Upgrade character dialogue to `premium` quality tier for this beat | `character_dialogue / premium` resolved by routing table |

Threshold evaluation is mutually exclusive. Premium quality upgrade takes precedence over misdirection so a peak dramatic moment is not undercut by injecting a red herring. The third row is the architectural benefit of unification: when tension is highest, the routing table automatically serves premium-tier character dialogue without any explicit provider-specific call-site code. The score is the quality tier signal.

`dramatic_tension_score` is logged to the `events` table on every pacing poll as `event_type = "tension_update"` with `payload.score` and `payload.beat_id`. Player-facing stall and misdirection interventions log `event_type = "pacing_intervention"` with `trigger_type`, `tension_score_at_trigger`, and `beat_id`. Their 60-second follow-up result is logged as a separate append-only `event_type = "pacing_intervention_outcome"` with `outcome_resumed_within_60s`. Premium quality upgrades do not emit pacing intervention events because there is no resumed-activity outcome for a quality-tier change. These events are Telemetry signal 2 (pacing intervention triggers/outcomes) from the PRD minimum set. The continuous score log is also a Tier 2 training signal: it captures the shape of tension across a session's arc.

## 3.4 Generative vs Authored Execution

Each element in an arc definition is flagged as `authored` (fixed) or `generative` (AI-driven at runtime). The engine treats these differently:

| Element type | Authored execution | Generative execution |
| --- | --- | --- |
| Beat structure | Executed as defined; cannot be overridden by AI output | N/A (beats are always authored) |
| Character identity | Served from arc definition | N/A |
| Killer assignment | N/A | AI-assigned at `introduction.killer_assignment` entry; seeded with session player list and character profiles |
| Character personality | Served from arc definition (base profile) | Behavior_profile augmented at session start with group-specific calibration |
| Clue content | Optional authored clue text | AI-generates clue text calibrated to assigned character |
| Plot twist | N/A | Injected by pacing engine when misdirection threshold crossed |
| Narrator dialogue | Optional authored beats | AI-generates narrator dialogue for all generative beats |

The engine enforces authored constraints regardless of generative output. If the arc defines that `reveal` cannot be entered before beat three, the transition guard blocks it regardless of what the AI generates or what players do. Authored constraints are not suggestions.

## 3.5 Character Behavior Commitments

Six commitments from Decision 13, with implementation approach:

| Commitment | Implementation |
| --- | --- |
| Stochastic generation | Each AI character response call uses `temperature=0.7` (configurable per arc); deterministic output is explicitly rejected. Two calls to the same prompt produce different responses. |
| Initiative scheduler | Background asyncio task per AI character. Each character has a configurable `initiative_interval` in their `behavior_profile`. When the interval fires without player input to that character, the character acts unprompted (speaks, moves, reacts). |
| NPC-NPC interaction first-class | AI characters can be targeted at each other, not only at players. The behavior engine accepts `target_character_id` on generation calls; NPC-NPC exchanges are generated with both characters' knowledge states and relationship graphs in the prompt. |
| Goal pursuit drives behavior | Each character's `behavior_profile.goals` list is injected into every generation prompt as a constraint block. Character responses are generated to advance or conceal their goals, not to be generically helpful. |
| Per-character behavior_profile | `behavior_profile JSONB` column on `characters` table. Stores: personality traits, communication style, goals, secrets, tells (behavioral signals of guilt or nervousness), and relationship dispositions toward each other character. |
| Arc-level non-determinism | The arc's `generative_elements.killer_assignment` is resolved at session start with a seeded random draw. The seed is stored in session state (for replay and persistence). Two identical player groups produce different killers across sessions. |

## 3.6 Session Coordinator Loop

The session coordinator is an asyncio coroutine that runs for the lifetime of each session. It:

1. Instantiates the `ArcStateChart` from the arc definition.
2. Starts the pacing engine background task.
3. Starts per-AI-character initiative scheduler tasks.
4. Listens on a session event queue for: player input events, host commands, pacing triggers, character initiative triggers, and arc beat transition signals.
5. For each event: evaluates guards, executes transition if valid, triggers generative elements configured for the new beat, emits resulting `ContentEvent` objects to the session event bus.
6. Handles session interruption: on disconnect or host pause, snapshots full session state to `arc_beat_states` and `knowledge_states` tables. On resume, restores state and resumes the coordinator from the saved beat.

The coordinator never blocks. All AI generation calls are `await`-ed as asyncio tasks. Long-running generation does not stall the event queue.

## 3.7 Nightcap Arc: Execution Flow Summary

| Phase | Beat | Key generative triggers | Content events emitted |
| --- | --- | --- | --- |
| Setup | `introduction.killer_assignment` | Killer identity draw, initial behavior_profile calibration | None visible to players yet |
| Onboarding | `introduction.motive_reveal` | Character personality augmentation, opening narrator dialogue | Shared display: setting; phones: character cards with private background |
| Investigation | `investigation.clue_phase` (parallel) | Clue generation per character, NPC initiative, pacing interventions | Phones: private clues; shared display: group events and NPC dialogue |
| Reveal | `reveal` | Killer confession narrative | Shared display: reveal scene; phones: outcome summary |

---
## SOURCE FILE: docs/architecture/04-knowledge-graph.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# Knowledge Graph

## 4.1 What the Knowledge Graph Is

In a real murder mystery dinner, every guest knows different things. The killer knows they did it. The victim's best friend knows about a secret argument. The nosy neighbor noticed someone leaving through the back door. Each person at the table is working from a different picture of reality, and the drama comes from those pictures colliding.

The knowledge graph is the system that tracks those different pictures. For every character in every session, it records: what does this character know, when did they learn it, and who told them? When an AI character speaks, the knowledge graph is what stops them from accidentally revealing a clue they were never supposed to have, or acting innocent about something their character secretly knows.

This is not an optional add-on. It is the reason the platform can run a coherent, unrepeatable session. Without it, AI characters contradict themselves, clues bleed across characters who should not have them, and the mystery falls apart. Every experience built on Arcwright gets knowledge state management, regardless of arc type.

## 4.2 Database Tables

The knowledge graph lives in six tables in Cloud SQL PostgreSQL.

**`facts`** stores the actual pieces of information that can be known. Think of a fact as a clue card: it has a type (clue, accusation, relationship, event), a structured content payload, and optionally an embedding column for future similarity search. A fact exists once and can be known by multiple characters.

**`knowledge_states`** is the join layer: it records which character knows which fact, when they learned it, and the full chain of characters through which they learned it. Each record stores a `provenance_chain` as a JSON array: an ordered list of character IDs from the original source to the current knower. If the witness told the housekeeper, who told the detective, the detective's record reads `provenance_chain: [witness_id, housekeeper_id, detective_id]`. A direct observation has a chain of one. Confidence below 1.0 models deception: if the butler told the detective something false, the record stores `confidence = 0.4` alongside the provenance chain. The detective believes it is probably true, knows who told them, and the engine can trace exactly how far this (possibly false) information has traveled. This enables contradiction detection, realistic "I heard from someone that..." dialogue, and richer session telemetry.

**`relationships`** tracks how characters feel about each other: trust level, history, current emotional disposition. This feeds the behavior engine and affects how characters choose to share or withhold information.

**`characters`** stores each participant's identity and `behavior_profile`. The behavior profile is a JSON object containing personality traits, goals, secrets, and behavioral tells. For AI characters, the behavior engine reads this profile before generating every response.

**`events`** is the append-only session history log. Every significant thing that happens in a session is recorded here: a clue delivered, an accusation made, a pacing intervention triggered. Events are never edited or deleted; they are only appended. The full event log is what allows a session to be resumed after interruption.

**`decisions`** logs the arc execution decisions made during the session: which beat was entered, which generative element triggered, which content safety rule fired. This is the audit trail.

## 4.3 The Three Core Operations

The knowledge graph exposes three operations to the rest of the engine:

**Assert:** a character learns something. Called when the arc delivers a clue to a player, when an NPC reveals information during dialogue, or when the pacing engine decides a character should know something to advance the session. Stored in `knowledge_states` with the fact, the character, the source, the timestamp, and the confidence level.

**Revoke:** a character's knowledge state changes. Used when deception is introduced: a character is told something false, or a piece of information is retracted. The original record is not deleted (the event log is append-only); instead a new `knowledge_states` record is written that supersedes the previous one for that character-fact pair. The history of what the character believed and when is preserved.

**Query:** what does this character currently know? Called by the behavior engine before every AI character generation call. Returns the character's current knowledge state as a structured list of facts with confidence levels. This output is injected into the AI prompt as a constraint block: the AI is explicitly told what this character knows and what they do not.

```python
# Called before every AI character response generation
knowledge = await get_character_knowledge(session_id, character_id)
# knowledge is injected into system prompt:
# "This character knows: [list of facts with confidence]"
# "This character does NOT know: [list of facts in session outside their knowledge]"
# The model is constrained to respect these boundaries.
```

This query is mandatory. There is no path through the character behavior engine that generates a response without first calling it. This is enforced at the engine layer, not left to individual arc implementations.

## 4.4 Schema Complexity Tiers

Not every arc needs the same level of knowledge tracking. The platform supports two tiers:

**Simple (MVP, Nightcap):** Facts are boolean. A character either knows a clue or does not. Confidence is used for deception modeling but there is no inference: the engine does not reason about what a character might know based on what they know about something else. This is sufficient for Nightcap and costs very little to compute.

**Complex (Horizon 2, monster RPG):** Inference chains and contradiction detection. If a character knows that the butler was in the kitchen at 9pm, and separately knows that the murder happened in the kitchen at 9pm, the engine can infer that the butler is a suspect even if no one told them this directly. This requires relationship-aware graph traversal, which is why the schema was designed with Apache AGE compatibility in mind (see Section 2.4). This tier is not implemented at MVP.

The schema is designed to be extensible. The simple tier runs on the same tables as the complex tier; the complex tier adds inference rules and traversal logic on top of the same underlying data. No schema migration is required to move from simple to complex, only additional query logic.

## 4.5 Embedding-Ready Design

Each fact in the `facts` table has an `embedding VECTOR(1536) NULL` column. At MVP this column is always null. When Tier 2 data collection activates, fact embeddings will be computed and stored, enabling:

- Semantic similarity search: find all facts in the session that are conceptually related to a player's question, even if the wording is different
- Fine-tuning signal: which facts were most salient in sessions that received high replay intent scores
- Future authoring assistance: suggest related clues from past sessions when an arc author is designing a new mystery

The column is present from day one at zero cost. Populating it requires an embedding API call per fact, which is deferred until the use case is active.

---
## SOURCE FILE: docs/architecture/05-session-persistence.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# Session State and Persistence

## 5.1 What Session State Is

Imagine eight players are 45 minutes into a Nightcap session. The host's phone dies. When she relaunches the app, the session should resume exactly where it left off: every player still holds their private clues, the killer is still the same person, and the narrator picks up without anyone starting over. None of that information should exist only in active memory.

Session state is everything that needs to survive an interruption: the arc's position, what every character knows, the full history of events, and the relationship tensions that have developed. The engine writes this to the database continuously throughout the session, not only at the end.

## 5.2 What Gets Persisted

Four categories of state, each mapped to specific tables:

**Arc position** (`arc_beat_states`): the current beat, the active state configuration inside that beat (python-statemachine's `configuration` value, which is the set of currently-active states), and the full transition history. On resume, the engine restores the statemachine to its last stable beat boundary rather than the exact moment of interruption.

**Character knowledge** (`knowledge_states`, `facts`): every fact assertion and revocation, with full provenance chains. The complete picture of who knows what, when they learned it, and how they came to know it.

**Session history** (`events`): the append-only event log. This is the authoritative record of everything that happened. If derived state is ever uncertain, the engine can reconstruct it from the event log.

**Relationship state** (`characters.behavior_profile` JSONB): character relationship dispositions as they have evolved during the session. Trust levels, affect changes, and alliance patterns that developed through play are preserved, not reset.

## 5.3 The Nearest-Beat Restore Pattern

The engine does not resume from mid-scene. Resuming mid-dialogue is disorienting for players and risks AI coherence failures. Instead:

1. When interruption is detected, complete any atomic operation in progress (await an in-flight generation call up to 5 seconds, complete any beat transition already underway)
2. Write a full state snapshot to `arc_beat_states` at the nearest completed beat boundary
3. Set session status to `paused`
4. On resume, restore the statemachine to that beat boundary
5. Emit a narrator bridge: a short AI-generated recap that re-grounds players before the arc continues

No session restarts from the beginning. No session state is permanently lost.

## 5.4 Interruption and Resume Flow

```
Interruption:
  1. Pacing engine task cancelled
  2. Character initiative tasks cancelled
  3. In-flight generation calls awaited (5s timeout, then cancelled)
  4. Full state snapshot written to arc_beat_states
  5. Session status -> "paused"
  6. Event logged: event_type = "session_interrupted"

Resume (host issues resume command):
  1. Load arc definition
  2. Reconstruct ArcStateChart from arc_beat_states snapshot
  3. Restore knowledge_states and relationship graph
  4. Restart pacing engine and character initiative tasks
  5. Generate narrator bridge event
  6. Session status -> "active"
  7. SSE streams re-established; players receive current beat context
```

## 5.5 Single Player Drop

If one player drops (not the host), the arc continues. The dropped player's character can be converted to an AI-controlled character mid-session: the `is_ai_controlled` flag on `session_participants` flips to true, the behavior engine picks up that character's full behavior profile and knowledge state, and the session proceeds without interruption. The host decides whether to convert or to mark the character as absent with a brief narrator acknowledgement.

## 5.6 Scope Debt

Inter-service communication between the API service and the engine worker (two Cloud Run services coordinating on session resume) is a deferred decision. Cloud Tasks (async, reliable, retryable) and direct async HTTP invocation (simpler, lower latency) are both viable at MVP scale. This decision must be made before production deployment and is logged in 03-Open-Questions-Log.

---
## SOURCE FILE: docs/architecture/06-model-routing.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# AI Model Routing Layer

## 6.1 What the Routing Layer Is

Think of the routing layer as a traffic controller for every AI call the platform makes. Instead of the rest of the engine knowing which AI provider to use and how much it costs, all AI calls pass through one place: `engine/routing/router.py`. That file reads a configuration table, picks the right model for the job, and makes the call. Everything else in the engine only knows the task type and quality level it needs. The routing layer handles the rest.

This matters for three reasons. First, AI pricing and model quality change frequently; a routing table update is a config file change, not a code deployment. Second, if a provider has an outage, the fallback logic is in one place. Third, when Arcwright eventually fine-tunes its own models and wants to route some calls to them, that transition happens entirely inside the routing layer. No other code changes.

## 6.2 The Provider-Agnostic Contract

Every component in the engine that needs an AI call follows the same contract:

```python
# What callers do:
response = await router.generate(
    task_type="character_dialogue",
    quality_tier="standard",      # or "premium"
    messages=[...],               # assembled prompt
    temperature=0.7
)

# What they never do:
# import anthropic
# litellm.acompletion(model="claude-haiku-4-5-20251001", ...)
```

No provider name, model name, or API key reference appears outside `router.py` and `routing_table.json`. If this rule is violated anywhere in the codebase, that is a bug.

## 6.3 Task Type Taxonomy

Every AI call belongs to exactly one task type. The taxonomy is fixed at MVP; new task types can be added for new arc types without changing existing routing logic.

| Task type | What it does | Latency priority | Quality need | Cost tier |
| --- | --- | --- | --- | --- |
| `character_dialogue` | Generates in-character speech and action | Medium | High | Medium/High |
| `narrative_generation` | Narrator text, scene descriptions, clue prose | Medium | High | Medium/High |
| `pacing_decision` | Determines whether and how to intervene in session flow | Low | Low | Very low |
| `knowledge_inference` | Reasons about what a character might infer from their knowledge state | Low | Medium | Low/Medium |
| `safety_classification` | Classifies content against arc policy before generation | High (blocks generation) | Specialized | Very low |
| `killer_assignment` | One-shot at session start: assigns killer and calibrates behavior profiles | Low | Medium | Low |
| `narrator_bridge` | Short recap on session resume | Low | Medium | Low |

## 6.4 Quality Tier Selection

Most task types have two quality tiers: `standard` (faster, cheaper) and `premium` (more capable, more expensive). The tier for `character_dialogue` and `narrative_generation` is determined dynamically by the `dramatic_tension_score` from the pacing engine:

```python
def resolve_quality_tier(
    task_type: str,
    session_state: SessionState,
    arc_config: ArcDefinition
) -> str:
    if task_type in ("character_dialogue", "narrative_generation"):
        if session_state.dramatic_tension_score >= arc_config.pacing_config.premium_threshold:
            return "premium"
    return "standard"  # default for all other task types and below-threshold tension
```

The effect: the most capable model is deployed precisely when the session is at its most dramatically charged, and standard-tier models handle the quieter moments. This produces higher quality where it matters and lower cost everywhere else.

## 6.5 Fallback Behavior

LiteLLM handles provider-level fallbacks natively. The routing table supports a `fallback` key per task type and tier:

```json
{
  "character_dialogue": {
    "standard": "anthropic/claude-haiku-4-5-20251001",
    "standard_fallback": "groq/llama-3.3-70b-versatile",
    "premium": "anthropic/claude-sonnet-4-6",
    "premium_fallback": "anthropic/claude-haiku-4-5-20251001"
  }
}
```

If the primary model call fails (provider outage, rate limit, timeout), LiteLLM automatically retries against the fallback. The session continues. Fallback activations are logged to `events` with `event_type = "routing_fallback"` so the founder can see which providers are causing fallback pressure.

## 6.6 Cost Tracking

Every generation call logs to `generation_logs` immediately on completion: model used, input tokens, output tokens, latency, and computed cost in USD. Cost is calculated from a rates table embedded in `router.py` and updated when provider pricing changes.

```python
# After every successful generation call:
await log_generation(
    session_id=session_id,
    task_type=task_type,
    quality_tier=tier,
    model_used=model_key,
    latency_ms=latency,
    input_tokens=usage.prompt_tokens,
    output_tokens=usage.completion_tokens,
    cost_usd=compute_cost(model_key, usage),
    tension_score=session_state.dramatic_tension_score
)
```

The dashboard aggregates this table to show per-session AI cost, per-arc cost average, and the real-time cost consumed by an active session. This is the founder's primary tool for monitoring gross margin per session and identifying which arc elements drive cost spikes.

## 6.7 Prompt Caching

Anthropic supports prompt caching with a 90% discount on cache hits. Two caching opportunities exist in every Nightcap session:

**Arc definition cache:** the arc definition, character schemas, and knowledge rules are identical across all sessions of the same arc. These are passed in the system prompt and eligible for caching once the cache warms on the first call.

**Character profile cache:** within a session, a character's identity, personality, and base goals are stable. Only the knowledge state and social pressure components change between calls. Structure prompts to place stable content first (cache-eligible) and dynamic content last (appended fresh).

Prompt caching is configured through LiteLLM's cache_control headers. Estimated impact on per-session cost at MVP: 20-35% reduction on `character_dialogue` calls where the system prompt is reused within the session.

## 6.8 Horizon 2 Upgrade Path

At MVP: LiteLLM in-process. One Python library, zero additional infrastructure.

At H2 (if warranted): LiteLLM Proxy Server deployed as a separate Cloud Run service. Reasons to trigger this upgrade:

- Multiple Arcwright services (API worker, engine worker, future services) need centralized model routing with shared rate limit management
- Enterprise customers require data residency guarantees that need routing-layer enforcement
- The Tier 2 fine-tuning transition requires routing some calls to Arcwright-hosted models, and centralized routing makes this cleaner to manage

The upgrade is a deployment change, not a code change. The `router.py` abstraction layer is identical in both configurations; only the target URL changes from the in-process LiteLLM SDK to the proxy endpoint.

---
## SOURCE FILE: docs/architecture/07-character-behavior.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# Character Behavior Engine

## 7.1 What It Does

The character behavior engine is the part of the platform that makes characters feel like real people with their own agendas rather than chatbots answering questions. When a player confronts the butler about a discrepancy in his alibi, the butler does not just respond. He responds in a way that is consistent with his personality, shaped by his secret, influenced by whether he trusts this particular player, and subtly colored by the fact that three people at the table are now staring at him.

The engine achieves this by building a complete psychological profile for every character before the session begins, maintaining that profile's consistency throughout every interaction, and using the session's social dynamics as a live input to generation. Characters do not have memory lapses. They do not contradict their own goals. And the killer, over the course of an evening, will betray themselves in ways that players can argue about for an hour after the session ends.

This is what produces the post-game argument: "Did you see how he answered that question about the kitchen?" "I thought that was completely normal." That disagreement is the sign of a session that worked.

## 7.2 The Behavior Profile

Every character in an Arcwright session has a `behavior_profile`: a structured JSON object stored in the `characters` table. It is the character's psychology encoded as data. For human players, it is read-only: it defines the character they are playing. For AI characters, it is the complete input to every response the engine generates.

```json
{
  "personality": {
    "traits": ["charming", "evasive", "secretly resentful"],
    "communication_style": "deflects personal questions with humor",
    "under_pressure_style": "becomes over-precise about minor details"
  },
  "goals": [
    "Protect my secret about the financial arrangement with the victim",
    "Appear cooperative with the investigation",
    "Redirect suspicion toward the housekeeper if possible"
  ],
  "secrets": [
    {
      "content": "I was blackmailing the victim over a forged document",
      "concealment_priority": "high",
      "crumble_threshold": 0.7
    }
  ],
  "tells": [
    "Mentions specific times unprompted when nervous",
    "Uses first names instead of titles when caught off-guard"
  ],
  "relationship_dispositions": {
    "character_id_housekeeper": {"trust": 0.3, "history": "rivalry", "current_affect": "cool"},
    "character_id_detective": {"trust": 0.6, "history": "acquaintance", "current_affect": "cautious"}
  }
}
```

`crumble_threshold` is how much accumulated social pressure it takes before a character's concealment starts to crack, expressed as a score from 0.0 (cracks easily) to 1.0 (never voluntarily reveals). This feeds directly into the social pressure system described in Section 7.4.

For Nightcap, behavior profiles have a base template per character slot (the butler always starts as charming and evasive) and a generative augmentation layer applied at session start: the AI calibrates personality nuances, relationship tensions, and tell patterns to the specific group of players joining. Two sessions with the same character slots produce noticeably different people.

## 7.3 Generation Pipeline

Every AI character response follows the same seven-step pipeline. No shortcuts.

1. **Query knowledge state.** `get_character_knowledge(session_id, character_id)` returns what this character knows and does not know. Mandatory; see Section 4.
2. **Query relationship graph.** Retrieve this character's current `relationship_dispositions` toward the player who is speaking and toward any other characters recently active in the scene.
3. **Compute social pressure score.** See Section 7.4. A single float (0.0-1.0) representing how much collective suspicion is currently directed at this character.
4. **Assemble system prompt.** Five blocks in order: (a) character identity and personality, (b) knowledge state constraint (what they know and do not know), (c) relationship context for this interaction, (d) social pressure instruction (how to modulate behavior given current pressure), (e) current beat context and goals for this scene.
5. **Route.** Task type `character_dialogue`, quality tier determined by `dramatic_tension_score` (standard below 0.85, premium above). See Section 6.
6. **Safety L3.** Policy injected into system prompt constrains thematic content to arc-defined rails before generation.
7. **Emit.** Output wrapped as `ContentEvent` with `target_audience`, `presentation_hints`, and `actor_id`. Delivered to session event bus.

Total pipeline latency target at MVP: under 1,500ms for standard tier, under 2,500ms for premium tier. These are not guaranteed SLAs; they are design targets that inform model selection.

## 7.4 Social Pressure Dynamics

Most AI character systems treat each exchange as independent: one player asks a question, one character answers. The behavior engine treats the room as a social system.

**Social pressure score** is computed per AI character on every pacing poll, alongside the `dramatic_tension_score`. It measures how much collective suspicion is currently directed at this character across all players:

```python
def compute_social_pressure(character_id: UUID, session: SessionState) -> float:
    # Weighted sum of: explicit accusations, suspicious questions directed at this character,
    # gaze signals (shared display focus), and alliance patterns (other characters
    # distancing themselves from this one)
    recent_accusations = session.accusation_weight(character_id, window_minutes=10)
    directed_questions = session.question_intensity(character_id, window_minutes=5)
    alliance_isolation = session.alliance_distance(character_id)
    return min(1.0, (recent_accusations * 0.5) + (directed_questions * 0.3) + (alliance_isolation * 0.2))
```

When social pressure exceeds a character's `crumble_threshold`, their behavior begins to shift in generation: they become over-precise, they deflect more aggressively, they make small errors consistent with their `under_pressure_style`. The killer does not confess; they just become more themselves under stress. Perceptive players notice. Players who are not paying attention miss it.

This is what produces the post-game argument: "Did you see how he answered that question about the kitchen?" "I thought that was completely normal." That disagreement is the sign of a session that worked.

## 7.5 Killer Tell System

The killer is assigned at session start. From that moment, the killer's `behavior_profile` is augmented with a set of tells: subtle behavioral patterns that are consistent with guilt but deniable as ordinary personality.

Tells are designed in three tiers:

| Tier | Visibility | Example |
| --- | --- | --- |
| Surface | Noticeable on reflection | "Uses first names instead of titles when caught off-guard" |
| Mid | Requires pattern recognition across multiple exchanges | "Answers questions about the crime scene with more detail than asked, then immediately changes subject" |
| Deep | Only visible to players actively tracking behavior across the full session | "Never initiates conversation with players who were near the crime scene at the time of death" |

At MVP, tells are authored into character archetypes in `nightcap/arc.json`. The generative augmentation layer selects which tier of tells to activate based on the player group's size: larger groups receive more surface tells (more people to notice them), smaller groups receive more mid and deep tells (fewer witnesses, harder game).

The killer's AI generation is constrained to express tells authentically but never to confess. The concealment goal is highest priority; the tells are behavioral leakage that happens despite the goal, not because of it.

## 7.6 Ensemble Coherence

AI characters in the same session are not independent agents. They are members of a social group and they behave that way.

Ensemble coherence is maintained through three mechanisms:

**Shared event awareness.** All AI characters receive the same session events (via the event bus) and update their knowledge states and relationship dispositions based on them. If the detective publicly accuses the butler, every other character's model of the butler's trustworthiness shifts.

**NPC-NPC interaction.** The initiative scheduler can trigger an AI character to address another AI character directly, not just players. These exchanges are generated with both characters' knowledge states and relationship dispositions in the prompt. A tense NPC-NPC exchange produced by emergent social dynamics is often the most memorable moment of a session because no player manufactured it.

**Relationship graph updates.** After significant events (accusations, revelations, emotional exchanges), the relationship graph is updated: trust levels shift, `current_affect` changes. Future generations for those characters read the updated graph, so behavior evolves naturally over the session rather than resetting to baseline on each exchange.

## 7.7 Monster RPG Extensibility

The behavior engine is designed to support the monster RPG's requirements without modification. The unified character model (same object for human and AI participants) means player trainers and NPC gym leaders are indistinguishable at the data layer. Player-defined motivation inference (the RPG requirement) slots in as an additional `behavior_profile` generation step at session entry: instead of assigning a fixed motivation, the engine infers it from the player's first actions and updates it as the session progresses. The inference runs via `knowledge_inference` task type in the routing table, no new routing required.

**Provenance chains in the behavior engine.** Every AI character response that references a piece of information can now express how they came to know it, not just that they know it. A character with `provenance_chain: [witness_id, housekeeper_id, detective_id]` on a fact can say "I heard from the housekeeper that the witness saw something" rather than stating the fact as direct knowledge. Characters with short provenance chains (they witnessed it themselves) speak with more certainty. Characters at the end of long chains express appropriate uncertainty. The engine injects provenance chain length and source identity into the generation prompt as part of the knowledge state constraint block. See Section 4 for the full schema.

---
## SOURCE FILE: docs/architecture/08-event-system.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# Multi-Surface Event System

## 8.1 What the Event System Is

The event system is the delivery layer between the engine and every screen in the room. When the arc engine decides that a clue should go to one specific player, that decision produces a `ContentEvent`. The event system takes that event and delivers it to exactly the right place: the phone belonging to that player, and nowhere else. The shared TV display gets a different event at the same moment: the narrator acknowledging that a clue has been shared, without revealing its contents.

The engine never knows what a TV or phone is. It only knows audience targets: `all`, `specific_player`, `host_only`, `shared_display`. The event system resolves those targets to live connections. This separation is what makes the platform surface-agnostic: the same engine that runs Nightcap on a phone and a TV could run a future arc on voice interfaces, smartwatches, or surfaces that do not exist yet, with no engine changes.

## 8.2 ContentEvent Schema

Defined in `engine/events/models.py`. Referenced in S15 with the core fields. Full schema:

```python
class ContentEvent(BaseModel):
    event_id:          UUID
    session_id:        UUID
    timestamp:         datetime
    event_type:        ContentEventType
    actor_id:          UUID | None          # character who produced this event; None for system events
    target_audience:   AudienceTarget       # all | host_only | specific_player | shared_display
    target_player_id:  UUID | None          # set only when target_audience = specific_player
    payload:           dict                 # event-type-specific structured content
    presentation_hints: PresentationHints
    sequence_number:   int                  # monotonically increasing per session; enables client-side ordering

class PresentationHints(BaseModel):
    emotion:          str | None   # "tense" | "warm" | "suspicious" | "playful" | "solemn"
    urgency:          str | None   # "low" | "medium" | "high"
    voice_hint:       str | None   # character voice descriptor for TTS or actor direction
    animation_hint:   str | None   # display layer hint; engine-agnostic string
    lighting_hint:    str | None   # display layer hint; engine-agnostic string
    pause_before_ms:  int          # optional pre-event pause for dramatic timing; default 0
```

`sequence_number` is new relative to the S15 definition: it is a monotonically increasing integer per session, assigned at event emission. SSE clients use this to detect missed events and request a replay window. This prevents gaps in the experience if a client reconnects.

`pause_before_ms` in `PresentationHints` is a creative addition: the engine can signal that a beat should breathe before the next event lands. A reveal moment might have `pause_before_ms = 2000`. The display layer honors this; it is a hint, not a guarantee.

## 8.3 Event Bus Architecture

At MVP, the event bus is an in-memory asyncio queue per session, held in the engine worker process. The API service subscribes to the bus via an internal async channel when a client connects via SSE.

```
Arc execution engine
        |
        v
  Session event bus       <- asyncio.Queue per session; in-memory at MVP
        |
        v
  SSE Fan-out Router      <- reads bus, filters by target_audience, delivers to connections
     /    |    \
   SSE   SSE   SSE
  Phone  Phone  TV
```

For Horizon 2 with multiple engine worker instances, the in-memory bus does not survive process boundaries. The upgrade path: replace the asyncio queue with a lightweight pub/sub layer (Redis Pub/Sub or Cloud Pub/Sub). The fan-out router code does not change; only the bus implementation changes. This is the transport adapter pattern committed in Decision 10.

## 8.4 Target Audience Filtering

The fan-out router maintains a connection registry per session:

```python
class SessionConnectionRegistry:
    connections: dict[UUID, list[SSEConnection]]  # participant_id -> connections
    display_connections: list[SSEConnection]       # shared display connections
    host_connections: list[SSEConnection]          # host connections

    def route(self, event: ContentEvent) -> list[SSEConnection]:
        match event.target_audience:
            case AudienceTarget.ALL:
                return self.all_player_connections() + self.display_connections
            case AudienceTarget.SPECIFIC_PLAYER:
                return self.connections.get(event.target_player_id, [])
            case AudienceTarget.HOST_ONLY:
                return self.host_connections
            case AudienceTarget.SHARED_DISPLAY:
                return self.display_connections
```

Privacy enforcement is structural. There is no code path through which a `specific_player` event reaches the wrong participant. The registry resolves targets to connections; the connections know only their own player ID.

## 8.5 Nightcap Two-Surface Example

Nightcap deploys on two surfaces simultaneously: the shared display (a TV or laptop in the room running the host interface) and each player's phone browser.

When the arc engine distributes a clue to Player 3:

| Event | target_audience | Delivered to | Content |
| --- | --- | --- | --- |
| `clue_delivery` | `specific_player` (Player 3) | Player 3's phone only | Full clue text, character association, presentation hints |
| `clue_acknowledged` | `shared_display` | TV | "A clue has been passed to [Character Name]" — no content |
| `clue_acknowledged` | `host_only` | Host interface | Which clue, which player, timestamp |

Player 3 receives their clue privately. Everyone in the room sees that something happened. The host sees what it was. The engine emits three events; the routing layer handles the rest.

## 8.6 SSE Implementation

FastAPI's `EventSourceResponse` (from the `sse-starlette` library) handles the SSE stream per client. Each connection:

- Authenticates via player JWT on connection
- Registers with the session connection registry
- Receives a replay of the last N events on reconnect (using `sequence_number` to identify the gap)
- Deregisters on disconnect; the arc continues for other participants

Event format on the wire:

```
data: {"event_id": "...", "event_type": "clue_delivery", "sequence_number": 42, "payload": {...}, "presentation_hints": {...}}

```

The TypeScript SDK wraps the browser's native `EventSource` API, parses the JSON, and calls the registered `onEvent` callback. The SDK consumer (Nightcap's phone client) only sees `ContentEvent` objects; it never touches SSE directly.

## 8.7 What the Event System Does Not Do

- Does not render anything. Rendering is the game client's responsibility.
- Does not store events. Storage is the `events` telemetry table's responsibility.
- Does not make generation decisions. That is the arc execution engine's responsibility.
- Does not know what a TV, phone, or browser is. It knows participant IDs and connection objects.

---
## SOURCE FILE: docs/architecture/09-developer-api.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# Developer API and Authoring Experience

## 9.1 Stack Positioning

Arcwright is Layer 2 narrative runtime middleware. Developers building on Arcwright receive two things: structured infrastructure they do not have to build (knowledge graph, arc execution, model routing, content safety, session state) and a surface-agnostic event stream they wire to whatever delivery layer they choose.

What developers bring:

- An arc definition (the human-authored structure: characters, beats, constraints, generative configuration)
- A delivery layer (the client code that renders events on their chosen surfaces)
- A content vision (the genre, tone, and experience they are building)

What developers do not need to build:

- Knowledge state enforcement across multiple characters
- AI model routing and cost management
- Session persistence and resume
- Content safety pipeline
- Pacing and dramatic timing logic
- Per-character behavior modeling

At MVP the platform is not open to external developers. The API is designed for external access from day one; Nightcap uses it internally as its first consumer. The documentation, arc definition format, and SDK surface must be legible to an external developer even if no external developer reads them at MVP.

## 9.2 REST API Endpoint Catalog

Base path: `/v1/`. All endpoints require auth (API key for developer calls; session JWT for game client calls).

### Session Management

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/v1/sessions` | API key | Create session from arc definition. Returns `session_id`, join URL, host token. |
| POST | `/v1/sessions/{id}/start` | Host JWT | Start the session arc. Triggers `introduction` beat. |
| GET | `/v1/sessions/{id}` | API key / Host JWT | Session state: status, current beat, player count, cost consumed. |
| POST | `/v1/sessions/{id}/pause` | Host JWT | Pause arc; snapshot state. |
| POST | `/v1/sessions/{id}/resume` | Host JWT | Resume from nearest beat snapshot. |
| POST | `/v1/sessions/{id}/end` | Host JWT | End session; emit final state record. |
| GET | `/v1/sessions/{id}/join` | None (public) | Validate join token; return player JWT and character assignment. |

### Character Management

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/v1/sessions/{id}/characters` | Host JWT | All characters in session with current behavior state (no private knowledge state). |
| GET | `/v1/sessions/{id}/characters/{char_id}` | Player JWT | Character detail for the requesting player's character only. |
| POST | `/v1/sessions/{id}/characters/{char_id}/input` | Player JWT | Submit player action or dialogue as the named character. |

### Knowledge State Management

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/v1/sessions/{id}/knowledge` | Host JWT / Arc engine (internal) | Assert a fact into a character's knowledge state. |
| DELETE | `/v1/sessions/{id}/knowledge/{fact_id}` | Arc engine (internal) | Revoke a fact (deception, forgetting). |
| GET | `/v1/sessions/{id}/knowledge/{char_id}` | Arc engine (internal) | Query a character's current knowledge state. Not exposed to player clients. |

### Content Event Stream

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/v1/sessions/{id}/events` | Player JWT / Host JWT | SSE stream. Delivers `ContentEvent` objects filtered by the requesting client's `target_audience`. Phone clients receive `all`  • `specific_player` events for their player_id. Host receives `all`  • `host_only`. Shared display receives `all`  • `shared_display`. |

### Usage and Developer Tools

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/v1/usage` | API key | AI credit consumption by session, by arc, by time window. |
| POST | `/v1/arcs/validate` | API key | Validate an arc definition JSON against the schema. Returns errors and warnings. |

## 9.3 Arc Definition Format

Arc definitions are JSON files. Nightcap's arc definition at `nightcap/arc.json` is the canonical reference. Every field name here must match the `ArcDefinition` Pydantic schema in `engine/arc/models.py`.

**Top-level structure:**

```json
{
  "arc_id": "nightcap-v1",
  "name": "Nightcap",
  "min_players": 4,
  "max_players": 10,
  "character_mode": "generated",
  "aesthetic_config": {
    "selection_model": {
      "era": {"type": "host_select", "allow_random": true},
      "occasion": {"type": "host_select", "allow_random": true}
    },
    "asset_generation": {
      "background_art": "pre_produced_per_theme",
      "music_palette": "pre_produced_per_theme",
      "animations": "pre_produced_per_theme",
      "ui_chrome": "pre_produced_per_theme",
      "character_portraits": "generated_at_session_start",
      "setting_name": "generative_runtime",
      "character_identities": "generative_runtime",
      "narrator_dialogue": "generative_runtime"
    },
    "ab_test_planned": "pre_produced_vs_runtime_generated"
  },
  "victim_config": {
    "eligibility_mode": "player_count_governed",
    "player_count_threshold": 4,
    "designation_trigger": "killer_revelation",
    "victim_role_pool": ["witness", "specter", "informant", "conspirator"],
    "conspirator_conditional": true,
    "conspirator_default_complicity": "accidental"
  },
  "kill_config": {
    "base_kills": 1,
    "additional_kills_available": true,
    "additional_kill_slot_config": "6_slot_only",
    "proportionality_check": true,
    "dynamic_expansion_triggers": ["killer_survived_accusation", "investigation_accelerating"]
  },
  "murder_timing_range": [1, 3],
  "session_duration_range": [30, 75],
  "revelation_step_range": [2, 4],
  "setting_constraint": "social_gathering",
  "arc_structure": "story_circle",
  "play_mode": "imposter",
  "tone_config": {
    "brand_envelope": {
      "irreverence": [0.5, 1.0],
      "suspense": [0.4, 0.9],
      "dark_comedy": [0.4, 0.85],
      "wit_density": [0.6, 1.0],
      "chaos_tolerance": [0.3, 0.8]
    },
    "scenario_defaults": {
      "irreverence": 0.7,
      "suspense": 0.65,
      "dark_comedy": 0.65,
      "wit_density": 0.75,
      "chaos_tolerance": 0.55
    },
    "voice_directive": "Wit-first ensemble mystery. The mystery and stakes are real. Characters are fully realized eccentrics with genuine agendas. Humor is structural and character-driven. The experience is irreverent, smart, suspenseful, mildly unhinged. Does not take itself too seriously but always takes the story seriously. Reference: Guy Ritchie Sherlock Holmes, Wes Anderson, Glass Onion, The Amazing Digital Circus, Rick and Morty, The League."
  },
  "narrator": {
    "type": "host_persona",
    "surface": "shared_display",
    "persona_mode": "aesthetic_linked",
    "behavior_triggers": ["beat_transition", "clue_release", "tension_threshold", "player_inaction"],
    "omniscient": true,
    "player_addressable": true
  },
  "quality_tier_default": "standard",
  "characters": [...],
  "beats": [...],
  "beat_graph": {
    "introduction": ["investigation"],
    "investigation": ["reveal"],
    "reveal": []
  },
  "generative_elements": {
    "killer_assignment": true,
    "character_generation": true,
    "character_personality_augmentation": true,
    "aesthetic_generation": true,
    "clue_content": true,
    "plot_twist": true,
    "narrator_dialogue": true
  },
  "content_rails": {
    "prohibited_categories": ["csam", "graphic_violence", "real_person_targeting"],
    "thematic_warnings": ["murder_mystery", "deception", "dark_motives"],
    "age_floor": 18
  },
  "pacing_config": {
    "stall_threshold": 0.25,
    "misdirection_threshold": 0.80,
    "premium_threshold": 0.85,
    "w_time": 0.3,
    "w_action": 0.3,
    "w_suspicion": 0.2,
    "w_coverage": 0.2
  },
  "knowledge_rules": {
    "killer_knows_they_did_it": true,
    "narrator_omniscient": true,
    "clues_private_until_shared": true
  }
}
```

**Arc validation tool (`POST /v1/arcs/validate`)** must catch at MVP:

- Required fields missing
- `beat_graph` references a beat_id not defined in `beats`
- `generative_elements` references an element not in the allowed set
- `min_players` greater than `max_players`
- Pacing weight sum (`w_time + w_action + w_suspicion + w_coverage`) not equal to 1.0
- `character_mode: authored` with no characters defined in `characters` array
- `narrator.behavior_triggers` references a trigger type not in the allowed set
- `play_mode: imposter` with `min_players` less than 3 (imposter mode requires at least 2 investigators plus 1 killer)

## 9.4 TypeScript Web SDK

The SDK ships at MVP for game client use (phone browsers and shared display). It wraps the REST and SSE endpoints in typed functions. It does not contain any arc logic.

**Core surface:**

```tsx
// arcwright-sdk/src/index.ts
export class ArcwrightClient {
  constructor(sessionId: string, joinToken: string, baseUrl: string) {}

  // Connect to SSE event stream; callback fires on each ContentEvent
  onEvent(callback: (event: ContentEvent) => void): () => void {}

  // Submit player action or dialogue
  async submitInput(characterId: string, input: PlayerInput): Promise<void> {}

  // Get current character state for the authenticated player
  async getMyCharacter(): Promise<CharacterDetail> {}

  // Disconnect and clean up SSE connection
  disconnect(): void {}
}

// Types are generated from the engine Pydantic schemas via a build step
export type { ContentEvent, PlayerInput, CharacterDetail, PresentationHints }
```

The SDK has no knowledge of surface types, arc structure, or game rules. It is a typed HTTP/SSE client. Nightcap's phone client and shared display client import this SDK and handle rendering independently.

## 9.5 Dashboard at MVP

The dashboard serves three functions at MVP: arc validation, session monitoring, and usage management. It is not a no-code arc builder. It assumes developers who can read JSON and understand arc concepts.

| Function | What it provides | What it does not provide |
| --- | --- | --- |
| Arc authoring | JSON editor with live schema validation and error highlighting | Visual drag-and-drop beat graph builder (deferred post-MVP) |
| Session monitoring | Live view: current beat, player count, `dramatic_tension_score`, AI credit consumption, knowledge state event count | Full dialogue transcript or private player information |
| Usage management | Credit consumption by session, by arc, by day; cost per session at current routing table | Billing and payment (out of scope at MVP) |

## 9.6 Documentation Requirements at MVP

Three documents ship with the API, sufficient for a technical co-founder to read the architecture without asking the founder to explain decisions:

1. **Getting started guide.** Session creation to first event stream in under 20 minutes. Uses Nightcap as the example arc.
2. **Arc definition reference.** Every field in `ArcDefinition` and its sub-schemas, with type, required/optional, and a one-sentence description.
3. **Nightcap arc schema.** The complete `nightcap/arc.json` published as the canonical reference implementation. Every structural decision in this arc is annotated with why it was made that way.

These documents are not sufficient for a public API launch. A full developer documentation investment is required before the H2 external developer beta (scope debt, PRD Section 9).

---
## SOURCE FILE: docs/architecture/10-content-safety.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# Content Safety Architecture

Content safety is not a post-launch patch. It is a core system designed before any other generative component, for two reasons. First, the murder mystery genre is adjacent to dark thematic territory by design: deception, hidden motives, and simulated harm are the genre's building blocks. Second, when the platform opens to third-party developers in Horizon 2, Arcwright is responsible for what runs on its infrastructure, regardless of which developer built the arc. The architecture reflects this: safety constraints are enforced at the engine layer and cannot be bypassed by arc configuration.

AI Dungeon's content safety failure in 2021 was not a moderation failure. It was an architecture failure: safety was designed as a filter on top of an otherwise unconstrained generative system. This document commits to the opposite approach.

## 10.1 Three-Layer Architecture

Three layers at MVP. Each layer catches different things and operates at a different point in the generation pipeline.

```
[Player input / Arc trigger]
        |
        v
  L1: Hard stops          <- Deterministic; no AI involved; zero latency
        |
        v
  L2: Pre-generation      <- GPT-OSS-Safeguard 20B on Groq; classifies intent before generation
  classification
        |
        v
  L3: In-generation       <- Policy injected into system prompt; constrains what the main LLM produces
  policy
        |
        v
  [Content event emitted]
```

**L4 (post-generation output filter) is deferred.** It would catch content that slipped through L1-L3. The deferred decision: add L4 when a specific failure pattern observed in production justifies the additional latency. The watchpoint trigger is: any L3 escape observed during playtesting or the first 90 days of production sessions. This is logged in 03-Open-Questions-Log.

## 10.2 Layer 1: Hard Stops

Deterministic code. No model call. No configuration. These categories are blocked unconditionally, regardless of arc definition, developer configuration, or player input:

- Sexual content involving anyone under 18
- Content targeting a real, named, living individual with harmful intent
- Detailed instructions for real-world violence or weapons construction
- Content designed to facilitate real-world harm outside the fictional frame

L1 runs on player input before any model call and on the assembled prompt before submission to L2/L3. If L1 fires, the event is blocked, logged to the `events` table with `event_type = "safety_hard_stop"`, and the session continues with a neutral narrator bridge. The player receives no error message that reveals the safety trigger; the experience is preserved.

## 10.3 Layer 2: Pre-Generation Classification

GPT-OSS-Safeguard 20B running on Groq. Fast (Groq's inference is optimized for low latency) and cheap (~$0.075/million input tokens). Supports bring-your-own-policy: the arc definition's `content_rails` configuration is passed as the policy context.

For Nightcap, the L2 policy includes:

- Permitted thematic territory: murder mystery, deception, hidden motives, dark social dynamics
- Thematic warnings (content that is permitted but logged): graphic descriptions of violence, explicit sexual content between adult characters
- Prohibited at arc level (in addition to L1): real-person targeting, content that breaks the fictional frame to provide real-world harmful information

L2 runs before every main LLM generation call. If L2 classifies the assembled prompt as prohibited, the generation call is not made. A neutral bridge response is generated by a separate low-stakes call. L2 classification results are logged to `events` with classification confidence score. This log is the primary signal for tuning L2 policy in future sessions.

Note: Groq output rate for GPT-OSS-Safeguard 20B is pending verification (open question in 03-Open-Questions-Log). Cost model in Section 13 uses a conservative estimate pending confirmation.

## 10.4 Layer 3: In-Generation Policy

A policy block is injected into the system prompt of every main LLM call, after the character identity and knowledge state blocks. The policy block states in plain language what the model must not produce, calibrated to the arc's `content_rails` configuration. This is the backstop that handles edge cases L2 did not catch: ambiguous content that is technically within policy but contextually inappropriate for the arc.

The L3 policy block for Nightcap includes: no graphic depiction of the murder itself, no sexual content between characters, no real-world harmful information delivered in-character, no content that directly accuses a real person.

L3 is the cheapest layer to customize and the most arc-specific. Developers configure it through `content_rails` in their arc definition.

## 10.5 Dashboard Visibility

Developers can verify their safety configuration is active via the dashboard. For each arc:

- L2 policy in effect (displayed as the bring-your-own-policy configuration active for this arc)
- L3 policy block (displayed as the injected text)
- L1 activations in recent sessions (count; no content)
- L2 classification activations (count and average confidence; no content)

Developers cannot read the content of blocked inputs. They can see that their rails are working and where they are firing.

## 10.6 What This Means for External Developers

When the platform opens to external developers in Horizon 2, they inherit L1 and L2 automatically. They configure L3 via `content_rails`. They cannot disable L1. They can expand L2's permitted territory within bounds Arcwright sets at the platform level (adult content between consenting adult characters is an example of something a developer could unlock; CSAM is an example of something that cannot be unlocked under any configuration). This tiered permission model is designed before external developers arrive; it is not retrofitted when they do.

---
## SOURCE FILE: docs/architecture/11-telemetry.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# Telemetry Schema

## 11.1 Why Telemetry Is Non-Negotiable

Every session that runs on Arcwright without structured telemetry is compute cost with no data return. More importantly: sessions that run without telemetry before the Tier 2 fine-tuning transition are training data permanently lost. You cannot go back and label sessions that were not instrumented.

Think of it this way: Arcwright's long-term cost advantage over competitors using the same underlying models is proprietary session data. Competitors using Anthropic's API and Arcwright using Anthropic's API are on equal footing today. In Horizon 2, if Arcwright has 50,000 labeled sessions and competitors do not, the fine-tuned models running on Arcwright infrastructure will be meaningfully better and cheaper per session. That gap is built one session at a time, starting from the first production deployment.

Telemetry must be live before a single real-user session runs. This is a hard requirement, not a launch checklist item.

## 11.2 Core Events Table

All telemetry flows into one primary table plus two supporting tables.

```sql
CREATE TABLE events (
    event_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id     UUID NOT NULL REFERENCES sessions(session_id),
    timestamp      TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor_char_id  UUID REFERENCES characters(character_id),  -- null for system events
    event_type     TEXT NOT NULL,
    payload        JSONB NOT NULL DEFAULT '{}',
    content_text   TEXT,          -- null at MVP for most event types
    embedding      VECTOR(1536)   -- null at MVP; populated when embedding collection activates
);

CREATE INDEX ON events (session_id, timestamp);
CREATE INDEX ON events (event_type, timestamp);
```

The `events` table is append-only. Records are never updated or deleted. GDPR deletion requests are handled by nullifying `content_text` and zeroing `embedding` for the affected session, not by deleting rows. The structural record (event type, timestamp, actor) is retained for telemetry integrity; the potentially personal content is removed.

## 11.3 MVP Minimum Signals

Five signals required by the PRD MVP done-criteria. All five are active from the first production session.

**Signal 1: Arc beat engagement duration.**

Logged on every beat transition: `event_type = "beat_transition"`, `payload = {"from_beat": str, "to_beat": str, "duration_seconds": int, "player_action_count": int}`. Duration is time from beat entry to beat exit. This is the primary signal for identifying which beats need authoring attention: a beat with high variance in duration across sessions is either under-paced or over-paced.

**Signal 2: Pacing intervention triggers and outcomes.**

Decision record: `docs/decisions/0004-pacing-telemetry-outcome-events.md`.

Logged on every pacing poll: `event_type = "tension_update"`, `payload = {"score": float, "beat_id": str}`. The continuous tension score log captures the shape of dramatic arc across the full session, not just intervention moments, and `beat_id` supports per-beat training-data review.

Logged when the pacing engine triggers a player-facing stall or misdirection intervention: `event_type = "pacing_intervention"`, `payload = {"trigger_type": "stall" | "misdirection", "tension_score_at_trigger": float, "beat_id": str}`.

Logged after the follow-up outcome window for those same player-facing interventions: `event_type = "pacing_intervention_outcome"`, `payload = {"trigger_type": "stall" | "misdirection", "tension_score_at_trigger": float, "beat_id": str, "outcome_resumed_within_60s": bool}`. The outcome is a separate event because the `events` table is append-only and the 60-second outcome cannot be known when the trigger event is first written.

A premium quality-tier upgrade is a pacing decision but not a `pacing_intervention` event. It has no `outcome_resumed_within_60s` semantics and is instead captured through the tension score, generation log quality tier and tension score, and decision-log payloads when persistence integration is wired.

**Signal 3: Knowledge state constraint activations.**

Logged when the knowledge query returns a constraint that affects generation: `event_type = "knowledge_constraint_activated"`, `payload = {"character_id": str, "fact_type": str, "constraint_direction": "blocked" | "permitted", "provenance_chain_length": int}`. The `provenance_chain_length` field is the telemetry payoff for the provenance chain adoption: over many sessions, this reveals whether longer information chains produce more engaging character behavior.

**Signal 4: Session completion status.**

Logged on session end: `event_type = "session_completed"`, `payload = {"completion_type": "full_arc" | "interrupted" | "abandoned", "final_beat_reached": str, "killer_identified": bool, "total_duration_seconds": int, "player_count": int}`. This is the top-level health metric for Nightcap: completion rate.

**Signal 5: Replay intent indicators.**

Logged at session end via a host-triggered post-session signal: `event_type = "replay_intent"`, `payload = {"intent": "yes" | "no" | "maybe" | "not_asked", "collection_method": "host_report" | "in_app_prompt"}`. This is a soft signal (host self-reports) at MVP. A more rigorous in-app prompt is a Tier 2 improvement.

## 11.4 generation_logs Table

Schema exists at MVP. Content population is behind the `CONTENT_LOGGING_ENABLED` feature flag (default: false). See Concern 1 resolution in chat record.

```sql
CREATE TABLE generation_logs (
    log_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES sessions(session_id),
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT now(),
    task_type       TEXT NOT NULL,          -- "character_dialogue" | "pacing_decision" | etc.
    quality_tier    TEXT NOT NULL,          -- "standard" | "premium"
    model_used      TEXT NOT NULL,          -- from routing table at time of call
    latency_ms      INTEGER NOT NULL,
    input_tokens    INTEGER NOT NULL,
    output_tokens   INTEGER NOT NULL,
    cost_usd        NUMERIC(10,6) NOT NULL,
    tension_score   FLOAT,                  -- dramatic_tension_score at time of call
    -- Fields populated only when CONTENT_LOGGING_ENABLED=true:
    prompt_text         TEXT,
    output_text         TEXT,
    prompt_embedding    VECTOR(1536),
    output_embedding    VECTOR(1536)
);
```

At MVP with the flag off: every generation call is logged with model, latency, token counts, cost, and tension score. This is sufficient for cost monitoring, per-session gross margin calculation, and routing table optimization. Prompt and output text are not stored, which keeps GDPR surface area minimal.

When the flag is enabled (Tier 2 readiness milestone): full prompt and output text are logged and embeddings are computed. This is the raw material for fine-tuning. The GDPR consent architecture for content logging must be designed before the flag is enabled: player-submitted content (names, character choices, dialogue) may appear in prompts.

## 11.5 decision_logs Table

```sql
CREATE TABLE decision_logs (
    decision_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES sessions(session_id),
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT now(),
    decision_type   TEXT NOT NULL,  -- "killer_assignment" | "clue_distribution" | "beat_transition" | etc.
    input_context   JSONB NOT NULL, -- structured context that drove the decision
    outcome         JSONB NOT NULL  -- what was decided
);
```

Implemented at MVP. Captures arc execution decisions (killer assignment seed, clue distribution order, pacing intervention choice) with the context that produced them. Over many sessions, this table reveals which decision patterns correlate with high completion rates and replay intent.

## 11.6 Tier 2 Signal Set: Designed, Partial at MVP

These signals are designed now so the schema is ready. At MVP, the fields exist but most are populated only for high-value event types. Full population is a Tier 2 milestone.

| Signal | Purpose | MVP status |
| --- | --- | --- |
| Dialogue quality rating | Per-generation quality score (human or automated) | Schema exists; not populated at MVP |
| Per-character engagement depth | How much each character was interacted with vs ignored | Derivable from events table post-session |
| Knowledge graph snapshots | Full knowledge state at each beat boundary | Schema exists; not populated at MVP |
| Safety filter outcomes | Detailed L2 classification confidence and category | L2 activations logged; detail deferred |
| Behavior consistency score | Whether a character's behavior was consistent with their profile across the session | Requires post-session evaluation pass; Tier 2 |
| Group dynamics index | How socially active the group was (question rate, accusation patterns, alliance formation) | Derivable from events table post-session |
| Provenance chain engagement | Whether long provenance chains produced more nuanced character dialogue | Tracked via `provenance_chain_length` in Signal 3 from MVP |

## 11.7 Telemetry and the Tier 2 Transition

The Tier 2 transition (fine-tuned models replacing managed API calls for specific task types) requires three conditions: sufficient session volume, sufficient data quality, and a confirmed cost break-even calculation. Telemetry is the mechanism that makes all three assessable.

- **Volume:** count of sessions with complete Signal 1-5 coverage
- **Quality:** distribution of completion rates and replay intent scores across the session corpus
- **Break-even:** per-session cost from `generation_logs` at current managed API rates vs projected fine-tuned inference cost

The Tier 2 transition cannot be evaluated without this data. Arcwright starts collecting it from session one.

---
## SOURCE FILE: docs/architecture/12-build-plan.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# Incremental Build Plan

## 12.1 The Three-Tier Build Philosophy

Arcwright builds in three tiers, each triggered by evidence rather than calendar. This is PRD Architecture Principle 7 (Progressive Proprietary Infrastructure) translated into a concrete build sequence.

**Tier 1 (build at MVP):** Everything deterministic. The arc execution engine, session state management, knowledge graph, event system, developer API, and usage tracking. These have zero marginal AI cost per session. They encode Arcwright's specific understanding of adaptive experiences. They are the platform's permanent foundation regardless of which AI providers exist in five years.

**Tier 2 (triggered by volume and data, Horizon 2 at earliest):** Specialized models fine-tuned on Arcwright session data, replacing general-purpose API calls for specific task types. Requires thousands of structured, labeled sessions and confirmed cost break-even. Do not build before the data justifies it.

**Tier 3 (never):** Foundation model development, GPU cluster ownership. Arcwright buys foundation model capability from providers who spend orders of magnitude more on it than Arcwright will. This is rational capital allocation, not a capability gap.

## 12.2 MVP: What Gets Built and In What Order

The component build order follows the dependency graph. Components higher in the list must be stable before components lower in the list can be built against them. This maps directly to Section 15.9.

**Phase 1: Data foundation (build first)**

1. Database schema and Alembic migrations (all 16 tables, pgvector enabled)
2. Core Pydantic models (`Session`, `SessionParticipant`, `Character`, `ArcDefinition`, `ContentEvent`)
3. Basic FastAPI app skeleton with health check and auth middleware

**Phase 2: Knowledge graph (build second; everything generative depends on it)**

1. `assert_knowledge` with provenance chain support
2. `get_character_knowledge` with constraint output format
3. `revoke_knowledge`
4. Unit tests: knowledge correctness suite

**Phase 3: Routing and safety (build before any generation)**

1. `router.py` with `routing_table.json` and LiteLLM integration
2. Routing fallback logic and `generation_logs` write
3. L1 hard stops
4. L2 pre-generation classification (GPT-OSS-Safeguard on Groq)
5. L3 policy injection
6. Unit tests: routing fallback, safety enforcement

**Phase 4: Arc execution engine (build after knowledge and routing are stable)**

1. `ArcStateChart` base class and `NightcapArcChart` implementation
2. `DramaticTensionScore` pacing engine with intervention logic
3. Session coordinator asyncio loop
4. Character behavior generation pipeline (7-step: knowledge query through event emit)
5. Initiative scheduler for AI characters
6. NPC-NPC interaction support
7. Unit tests: arc state transitions, pacing interventions

**Phase 5: Event system and API (build after engine is functional)**

1. `SessionConnectionRegistry` and SSE fan-out router
2. In-memory asyncio event bus
3. FastAPI SSE endpoint with reconnect and sequence number replay
4. REST endpoints: session lifecycle, character input, knowledge assert
5. TypeScript web SDK (`ArcwrightClient`)

**Phase 6: Session persistence (build after end-to-end flow is working)**

1. Interrupt/resume flow with nearest-beat snapshot
2. Player drop and AI takeover
3. Session state replay from event log

**Phase 7: Telemetry and simulation (build last; validates everything above)**

1. All five MVP minimum telemetry signals wired to events table
2. `generation_logs` writes (non-content fields only)
3. `decision_logs` writes
4. Simulation harness: synthetic players, seeded runs, batch statistics

## 12.3 MVP Done Criteria

MVP is complete when all of the following are true (from PRD Section 9):

- Nightcap is playable end-to-end by a group of 4-10 real players not involved in building it
- Session completes through all three beats to the reveal
- Knowledge state enforcement works: no player receives information their character should not have
- Session persistence works: mid-game interruption restores from nearest beat
- Provider-agnostic routing abstraction is in place: no model name outside `routing_table.json`
- Structured telemetry is live for all five minimum signals
- API is documented for a technical co-founder to read without explanation
- Per-session cost model is live: AI credit tracking active, gross margin calculable
- Content safety rails are active for Nightcap's thematic territory
- At least one non-Nightcap arc schema has been designed, proving the arc format is not Nightcap-specific

## 12.4 What Can Be Built in Parallel

| Parallel track A | Parallel track B | Dependency to reunite |
| --- | --- | --- |
| Database schema + models | Arc definition JSON schema design | Both needed before arc execution engine |
| Knowledge graph | Routing + safety pipeline | Both needed before character behavior engine |
| Arc execution engine | TypeScript SDK | Both needed for end-to-end playtest |
| Simulation harness scripting | Telemetry schema design | Both needed before first instrumented session |

At MVP solo development, these tracks are sequential. With a technical co-founder, parallel tracks become real and can compress the build timeline by 30-40%.

## 12.5 H1 to H2 Transition Requirements

The transition to Horizon 2 (platform opens to external developers, monster RPG enters development) requires, beyond MVP done criteria:

- Minimum 5 completed, instrumented sessions with real groups expressing unprompted replay intent (PRD Use Proof signal)
- Willingness-to-pay or enterprise conversation proof signals met (PRD Business Signals)
- Monster RPG architecture validation confirmed (Section 14 of this document)
- External developer documentation sufficient for a closed beta (scope debt from MVP)
- Inter-service communication mechanism resolved (scope debt from Section 5)
- `dramatic_tension_score` weights validated through at least 10 playtested sessions

## 12.6 Named Scope Debt

Four items explicitly deferred from MVP with known H2 resolution points:

| Debt item | Deferred from | Resolution target |
| --- | --- | --- |
| No-code arc builder for non-developer creators | Dashboard MVP scope | H2 dashboard investment |
| Knowledge graph inference and contradiction detection | Knowledge graph simple tier | H2 monster RPG development |
| External developer documentation (public-launch quality) | MVP documentation | Before H2 closed beta |
| Inter-service communication mechanism (Cloud Tasks vs direct) | Session persistence | Before production deployment |

---
## SOURCE FILE: docs/architecture/13-cost-model.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# Cost Model

## 13.1 Why Cost Architecture Is a First-Class Concern

Death by AI launched with 700,000 daily users and had to make emergency architectural changes within 72 hours because AI costs were unsustainable. That is the failure mode this section exists to prevent. Cost is not an optimization to address later; it is a design input that shapes every generation decision from the first session.

## 13.2 Per-Session Cost Breakdown

Based on verified pricing from May 7, 2026, and the session model from Chat 6a research.

**Session parameters:** 60 minutes, 8 players, approximately 30 generation calls (character dialogue, narrative generation, pacing decisions) plus approximately 60 safety classification calls.

**Token estimate per session:** 75,000 input tokens, 15,000 output tokens total across all calls.

| Call category | Volume | Model | Input cost | Output cost | Subtotal |
| --- | --- | --- | --- | --- | --- |
| Character dialogue (standard) | 20 calls | Claude Haiku | ~30K tokens | ~8K tokens | ~$0.07 |
| Narrative generation (standard) | 8 calls | Claude Haiku | ~15K tokens | ~5K tokens | ~$0.04 |
| Pacing decisions | 12 calls | Llama 3.1 8B (Groq) | ~8K tokens | ~1K tokens | ~$0.001 |
| Safety classification (L2) | 60 calls | GPT-OSS-Safeguard (Groq) | ~22K tokens | ~1K tokens | ~$0.002 |
| **Total (standard tier)** |  |  |  |  | **~$0.113** |

**With prompt caching (Anthropic cache hits at 90% discount, estimated 40% hit rate on system prompts):**

Effective cost reduction on Haiku calls: ~25%. Estimated cached cost: **~$0.085 per session**.

**Premium tier uplift** (sessions where `dramatic_tension_score` pushes dialogue to Sonnet 4.6 during peak beats, estimated 20% of dialogue calls at premium):

Additional cost per session: ~$0.04. Premium-augmented session cost: **~$0.125**.

**Infrastructure cost per session** (amortized at 200 sessions/month across GCP baseline):

~$0.25 per session at low volume. Drops toward $0.05 at 1,000+ sessions/month as fixed costs amortize.

## 13.3 Self-Hosting Break-Even

From Chat 6a analysis (verified May 7, 2026):

| Scenario | Per-session AI cost |
| --- | --- |
| Managed API (current) | ~$0.11-$0.13 |
| Managed API with caching | ~$0.08-$0.10 |
| Self-hosting Llama 70B on A100 at $2/hr, 8 concurrent, 50% utilization | ~$0.51 |

**Break-even volume for self-hosting to become cheaper than managed API:** approximately 25,000-50,000 sessions per month. At that volume, the economics of dedicated GPU infrastructure begin to favor self-hosting for high-frequency task types.

**Decision rule:** stay on managed APIs through all of Horizon 2. Evaluate self-hosting at the H2-to-H3 transition when actual session volume is known. Do not build self-hosting infrastructure speculatively.

## 13.4 Cost Monitoring

Three levels of cost visibility, each serving a different decision horizon:

**Per-session gross margin** (operational, real-time):

Calculated from `generation_logs` after each session. Formula: `session_revenue - ai_cost - amortized_infrastructure_cost`. At MVP with zero revenue, this tracks cost per session as a health metric. After pricing is live, it becomes the primary unit economics signal.

**Per-arc cost average** (product, weekly):

Aggregated from `generation_logs` grouped by `arc_id`. Identifies which arc elements drive cost spikes. If the investigation beat consistently runs 3x more expensive than the introduction beat, that is a signal to review the clue generation logic.

**Routing table efficiency** (optimization, as-needed):

Compare actual model usage against the routing table's intent. If fallback activations are frequent for a specific task type, either the primary provider has a reliability problem or the task type is hitting rate limits.

## 13.5 Pricing Design Principles

Pricing for Nightcap and for the developer API is a product decision deferred to a later artifact. The cost model here informs that decision with three constraints:

1. **Minimum viable session price:** at $0.10-$0.13 per session AI cost plus infrastructure, any consumer pricing below $0.50 per session requires volume to be viable. A group-based pricing model (one purchase covers the group) rather than per-player pricing changes the economics significantly.
2. **Developer API pricing floor:** the platform cannot offer sessions to developers below its own cost of goods. The `generation_logs` per-session cost is the floor below which no plan tier can be sustainably priced.
3. **Enterprise price anchor:** Mursion charges approximately $49 per person per 30-minute session for enterprise experiential training. An Arcwright enterprise team-building session at $5-$15 per person is substantially below this anchor while remaining well above Arcwright's per-session cost. This is the Horizon 2 enterprise pricing territory to target.

---
## SOURCE FILE: docs/architecture/14-architecture-validation.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# Architecture Validation: Monster RPG and Couch Co-op

## 14.1 Purpose

Every significant architecture decision in this document must be validated against future experience types before it is treated as final. If a decision only works for Nightcap's linear arc with a fixed endpoint, it is a Nightcap-specific decision and must be labeled as such. If it silently breaks when the monster RPG requirements arrive, it is a design error.

This section validates the MVP architecture against two future experience types: the monster RPG (Horizon 2, PRD Section 5) and couch co-op play patterns (placeholder for local same-room multi-player mechanics, deferred to design in Chat 8).

## 14.2 Monster RPG Validation

The monster RPG has fundamentally different requirements from Nightcap. Five requirements from PRD Section 5 are tested here:

**Requirement 1: World state persistence independent of any individual session.**

The monster RPG world exists between sessions. A player's trainer level, the gym leader's memory of prior encounters, and town-level events persist across many sessions.

Validation: the current architecture stores all state within a `session_id`. World-level persistence requires a new `world_state` table and `world_instance_id` as a first-class concept alongside `session_id`. This is an extension, not a rebuild: the session model gains a `world_instance_id` foreign key, and a new set of tables manages world state. No existing session logic changes.

**Requirement 2: Emergent narrative arcs with no designed endpoint.**

Nightcap has a fixed reveal as the terminal state. The monster RPG has no single designed ending: the player's story is whatever they make of it.

Validation: the `ArcStateChart` supports this. A world-arc's beat graph has no terminal state: the `is_terminated` check returns false indefinitely. The statemachine loops on ongoing-state beats. Pacing logic changes (no reveal to accelerate toward) but the architecture accommodates it. The arc definition format's `beat_graph` simply has no empty next-beat list; beats loop back on themselves based on world events.

**Requirement 3: Procedural generation at the world layer.**

Terrain, NPC populations, and event distributions are procedurally generated, distinct from the AI narrative layer.

Validation: procedural generation is a separate system that produces structured data consumed by the arc execution engine as authored content for that session. The engine does not need to know it was procedurally generated vs. manually authored. A new `world_generation` module produces the `locations`, `objects`, and NPC character schemas that seed the session. This module is additive; it does not touch existing engine components.

**Requirement 4: Player-defined motivation inference.**

Rather than being assigned a role, the monster RPG player's motivation is inferred from their behavior.

Validation: the behavior engine's generation pipeline already accepts dynamic `behavior_profile` updates mid-session. Player motivation inference is a new task type (`player_motivation_inference`) added to the routing table, producing a structured motivation object that is written back to the player's `behavior_profile.goals` field. The knowledge graph, event system, and character model require no changes.

**Requirement 5: Simultaneous multi-player world state with no single endpoint.**

Multiple players in the same world instance are living different stories simultaneously.

Validation: the event system's `target_audience` model already supports per-player routing. The session coordinator loop will need to manage multiple concurrent story threads, which increases complexity but does not require architectural restructuring. The `SessionConnectionRegistry` handles multiple players natively. The primary new challenge is world state consistency across concurrent player actions: a locking strategy for world state mutations is required and is scoped to H2 design.

**Monster RPG validation summary:**

| Requirement | Architecture verdict | Work required |
| --- | --- | --- |
| World state persistence | Extension (new tables, new foreign key) | Low |
| Emergent narrative | Native (beat graph with no terminal state) | None |
| Procedural generation | Additive (new module, engine unchanged) | Medium |
| Motivation inference | Additive (new task type, routing table entry) | Low |
| Multi-player world state | Extension (world state locking strategy) | Medium (H2 design) |

No component in the MVP architecture requires a rebuild to support monster RPG requirements.

## 14.3 Couch Co-op Placeholder

Couch co-op describes same-room multi-player patterns where players share a physical space and may share a single display while having individual input devices. This is distinct from Nightcap's phone-per-player model in that input device assignment, display sharing, and local network play introduce new delivery constraints.

Placeholder capabilities that the architecture must not foreclose:

- Shared screen rendering for multiple players on one device
- Local input handling without per-player phone requirement
- Low-latency same-room interaction (sub-200ms event delivery)
- Mixed cooperative-competitive mechanics on a single shared arc

These requirements do not conflict with the current architecture. The event system's surface-agnostic design and the SDK's thin client model leave room for a couch co-op delivery adapter. Full design is deferred to Chat 8 (Story Bible: Monster RPG), where the specific arc type will inform which couch co-op patterns are actually needed.

## 14.4 Architecture Fitness Summary

The MVP architecture passes validation for Horizon 2 requirements. All necessary extensions are additive. No committed decision requires reversal or rebuild to support the monster RPG or couch co-op patterns. The boundary between platform components and game-specific components is clean enough that new arc types require new arc definition files and targeted module additions, not changes to the platform foundation.

---
## SOURCE FILE: docs/architecture/15-development-guide.md

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> Do not edit this file directly; edit in Notion and re-sync.

# Agentic Development Guide

**Purpose.** This section is the primary input for Claude Code. Every component definition is unambiguous: input schema, output contract, acceptance criteria, dependencies, and must-not-do guards are explicit. Claude Code builds against this guide without asking the founder to explain decisions. All locked architectural decisions are in 02-Decisions-Log (Chat 6a entries, May 7 2026). This guide operationalizes decisions; it does not restate rationale.

## 15.1 Repository Structure and First File

```
arcwright/
  engine/                  # Python: core platform library
    arc/                   # Arc execution engine (python-statemachine StateChart)
    characters/            # Character model and behavior engine
    knowledge/             # Knowledge graph and state management
    routing/               # AI model routing abstraction layer
    safety/                # Content safety pipeline
    events/                # Content event system
    session/               # Session state and persistence
    telemetry/             # Telemetry schema and logging
    tests/                 # Unit and simulation harness
  api/                     # FastAPI thin wrapper over engine
    routers/               # Route handlers (session, character, knowledge, events)
    auth/                  # Firebase Auth + API key middleware
    schemas/               # Pydantic request/response models
  sdk/                     # TypeScript web SDK (MVP)
  dashboard/               # TypeScript React dashboard
  migrations/              # Alembic database migrations
  nightcap/                # Nightcap arc definition files (JSON)
  config/                  # Environment config, routing_table.json
  scripts/                 # GCP setup scripts, seed data
```

**First file to create:** `engine/session/models.py`. This file defines the Session, SessionParticipant, and ArcBeat Pydantic models. Every other component depends on what a session is. Do not write any other file before this one exists and its schema is stable.

## 15.2 Environment and Core Dependencies

```
# requirements.txt (engine + api)
python-statemachine>=3.0
fastapi>=0.111
uvicorn[standard]
asyncpg
sqlalchemy[asyncio]>=2.0
alembic
pydantic>=2.0
litellm>=1.30
firebase-admin
pgvector
python-dotenv
httpx
structlog
```

```
# .env.example
DATABASE_URL=postgresql+asyncpg://user:pass@host/arcwright
FIREBASE_PROJECT_ID=arcwright-prod
LITELLM_DEFAULT_ROUTING_TABLE=config/routing_table.json
CONTENT_LOGGING_ENABLED=false
ANTHROPIC_API_KEY=
GROQ_API_KEY=
```

`CONTENT_LOGGING_ENABLED=false` is the feature flag controlling full population of `generation_logs`. The table schema exists from day one. Prompt and output text write only when this flag is true. See Section 11 for the full generation_logs schema.

## 15.3 Database: Cloud SQL PostgreSQL Setup

First Alembic migration creates tables in this order (dependencies drive order; do not reorder):

1. Enable `pgvector` extension (`CREATE EXTENSION IF NOT EXISTS vector`)
2. `accounts`
3. `consent_records`
4. `characters` (includes `behavior_profile JSONB`, `embedding VECTOR(1536) NULL`)
5. `facts` (includes `embedding VECTOR(1536) NULL`)
6. `knowledge_states`
7. `relationships`
8. `locations`
9. `objects`
10. `decisions`
11. `events` (append-only; includes `embedding VECTOR(1536) NULL`)
12. `sessions`
13. `session_participants`
14. `arc_beat_states`
15. `generation_logs` (full schema; `prompt_text TEXT NULL`, `output_text TEXT NULL`, `prompt_embedding VECTOR(1536) NULL` nullable at MVP; populated only when `CONTENT_LOGGING_ENABLED=true`)
16. `decision_logs`

**Session as a data structure:**

```python
class Session(BaseModel):
    session_id: UUID
    arc_id: str                    # references arc definition file
    status: SessionStatus          # created | active | paused | completed | abandoned
    host_account_id: UUID
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    current_beat_id: str
    quality_tier: QualityTier      # standard | premium
    player_count: int

class SessionParticipant(BaseModel):
    participant_id: UUID
    session_id: UUID
    character_id: UUID
    account_id: UUID | None        # None for anonymous players
    join_token: str                # short-lived JWT for game client auth
    surface_type: str              # phone | shared_display | host
    is_ai_controlled: bool
```

## 15.4 Arc Definition Schema

Arc definitions are JSON files. Nightcap's arc definition lives at `nightcap/arc.json`. The platform reads this schema; it does not generate arc structure.

```python
class CharacterMode(str, Enum):
    authored   = "authored"    # fixed character definitions in arc schema
    generated  = "generated"   # characters generated at session start from typed slots
    hybrid     = "hybrid"      # some authored, some generated

class AestheticMode(str, Enum):
    fixed    = "fixed"         # single fixed aesthetic defined in arc
    palette  = "palette"       # selection from a defined list of options
    generative = "generative"  # fully generated at session start

class PlayMode(str, Enum):
    imposter       = "imposter"       # one player is the killer; plays to avoid detection
    detective_race = "detective_race" # all players are investigators competing to solve first
    cooperative    = "cooperative"    # all players work together

class NarratorConfig(BaseModel):
    type: str                  # "host_persona" | "voice" | "environmental"
    surface: str               # "shared_display" | "all" | "none"
    persona_mode: str          # "fixed" | "palette" | "aesthetic_linked" | "generative"
    behavior_triggers: list[str]  # ["beat_transition", "clue_release", "tension_threshold", "player_inaction"]
    omniscient: bool           # narrator has full session knowledge state
    player_addressable: bool   # narrator can address individual players by name

class ArcDefinition(BaseModel):
    arc_id: str
    name: str
    min_players: int
    max_players: int
    character_mode: CharacterMode
    aesthetic_mode: AestheticMode
    setting_constraint: str | None  # e.g. "social_gathering"; None means unconstrained
    arc_structure: str              # "dan_harmon" | "heros_journey" | "man_in_hole" | "custom"
    play_mode: PlayMode
    narrator: NarratorConfig
    quality_tier_default: QualityTier
    characters: list[CharacterSchema]
    beats: list[BeatDefinition]
    beat_graph: dict[str, list[str]]   # beat_id -> list of valid next beat_ids
    generative_elements: GenerativeConfig
    content_rails: ContentRailsConfig
    knowledge_rules: KnowledgeRuleSet  # initial knowledge state seeded at session start

class BeatDefinition(BaseModel):
    beat_id: str
    beat_name: str                     # human-readable beat label (e.g. "The Arrival")
    beat_type: BeatType                # introduction | investigation | reveal | epilogue
    story_circle_step: int | list[int] # Story Circle position(s) this beat maps to (1-8)
    structural_function: str           # platform tag: e.g. "establish_comfort", "surface_disruption"
                                       # pre-populated for story_circle arcs; required for custom arcs
    dramatic_purpose: str | None       # free-text director's note; required if arc_structure = "custom"
    emotional_target: str | None       # target player emotional state at beat's end
    information_goal: str | None       # what players should know/discover by beat's end
    tension_target: float | None       # pacing engine tension target (0.0-1.0) for this beat
    character_emphasis: list[str]      # character slot IDs foregrounded in this beat
    authored_content: dict | None      # fixed narrative content if any
    generative_triggers: list[str]     # which generative elements activate in this beat
    entry_conditions: list[str]        # logical conditions that must be true to enter
    exit_conditions: list[str]         # logical conditions that trigger next beat transition
    pacing_config: PacingConfig        # stall threshold, acceleration trigger, misdirection trigger
    audience_targets: list[AudienceTarget]
    mini_games: list[MiniGameConfig] | None  # available in beats 1-3; outputs feed killer_assignment_logic
```

Nightcap has three top-level beats: `introduction`, `investigation`, `reveal`. `investigation` is a `State.Compound` in the statemachine with internal sub-beats for clue distribution phases. The killer identity is AI-assigned at `introduction` entry via a generative trigger; the assignment is stored in session state and constrains all subsequent character behavior generation.

## 15.5 Knowledge State: Assertion API

```python
# Engine internal function signature
async def assert_knowledge(
    session_id: UUID,
    character_id: UUID,
    fact_type: str,                      # "clue" | "accusation" | "relationship" | "event"
    fact_content: dict,
    source_character_id: UUID | None,    # who told them; None if environmental
    confidence: float = 1.0,             # 0.0-1.0; enables deception modeling
    expires_at: datetime | None = None
) -> KnowledgeStateRecord: ...

# HTTP endpoint
# POST /v1/sessions/{session_id}/knowledge
{
  "character_id": "<uuid>",
  "fact_type": "clue",
  "fact_content": {"clue_id": "c1", "text": "The victim was in the library at 9pm"},
  "source_character_id": null,
  "confidence": 1.0
}
```

**Non-negotiable constraint:** Every AI character response generation call must call `get_character_knowledge(session_id, character_id)` before constructing the generation prompt. The knowledge state result is injected into the system prompt as a constraint block. This call is not optional and cannot be skipped for performance reasons.

## 15.6 Content Event Schema

```python
class ContentEvent(BaseModel):
    event_id: UUID
    session_id: UUID
    event_type: ContentEventType        # narration | dialogue | clue | system | pacing
    actor_id: UUID | None               # character who produced this event
    target_audience: AudienceTarget     # all | host_only | specific_player | shared_display
    target_player_id: UUID | None       # set when target_audience = specific_player
    payload: dict                       # event-type-specific structured content
    presentation_hints: PresentationHints
    timestamp: datetime

class PresentationHints(BaseModel):
    emotion: str | None                 # "tense" | "warm" | "suspicious" | "neutral"
    urgency: str | None                 # "low" | "medium" | "high"
    voice_hint: str | None
    animation_hint: str | None
    lighting_hint: str | None
```

The engine emits `ContentEvent` objects to a session event stream. It does not know what renders them. No field in this schema names a surface type (TV, phone, browser). The consuming layer (Nightcap) maps events to surfaces.

## 15.7 AI Model Routing: First Call and Routing Table

**First provider to call at MVP:** Anthropic via LiteLLM, in-process. No proxy server at MVP.

```python
# engine/routing/router.py
import litellm, json
from pathlib import Path

_table = json.loads(Path("config/routing_table.json").read_text())

async def route_generation(
    task_type: str,
    quality_tier: str,
    messages: list[dict],
    temperature: float = 0.7
) -> str:
    model_key = _table[task_type][quality_tier]
    response = await litellm.acompletion(
        model=model_key,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content
```

```json
// config/routing_table.json (MVP defaults)
{
  "character_dialogue": {
    "standard": "anthropic/claude-haiku-4-5-20251001",
    "premium": "anthropic/claude-sonnet-4-6"
  },
  "pacing_decision": {
    "standard": "groq/llama-3.1-8b-instant",
    "premium": "groq/llama-3.1-8b-instant"
  },
  "safety_classification": {
    "standard": "groq/gpt-oss-safeguard-20b",
    "premium": "groq/gpt-oss-safeguard-20b"
  },
  "knowledge_inference": {
    "standard": "groq/llama-3.1-8b-instant",
    "premium": "groq/llama-3.3-70b-versatile"
  },
  "narrative_generation": {
    "standard": "anthropic/claude-haiku-4-5-20251001",
    "premium": "anthropic/claude-sonnet-4-6"
  }
}
```

No model name or provider string appears anywhere in the codebase outside `routing_table.json` and `router.py`. Switching a routing table entry requires zero code changes.

## 15.8 MVP GCP Infrastructure

| Service | Configuration | Estimated monthly cost |
| --- | --- | --- |
| Cloud Run (API service) | 1 vCPU, 512 MB RAM, min-instances=0, max=10 | $5-20 |
| Cloud Run (engine worker) | 2 vCPU, 1 GB RAM, min-instances=0, max=5 | $10-30 |
| Cloud SQL PostgreSQL 15 | db-f1-micro, 10 GB SSD, single region | $10-15 |
| Firebase Auth | Spark plan | Free |
| Cloud Storage (telemetry backups) | Nearline, under 1 GB at MVP | Under $1 |
| **Total MVP estimate** |  | **$25-66/month** |

Two Cloud Run services at MVP: the API service (FastAPI, handles REST requests and SSE streams) and the engine worker service (asyncio, handles beat transitions and AI generation tasks). Both share Cloud SQL. Inter-service communication mechanism (Cloud Tasks vs direct async invocation) is a scope debt item resolved in Section 5 of this document.

## 15.9 Component Build Order

| Priority | Component | Acceptance criteria | Must NOT do |
| --- | --- | --- | --- |
| 1 | Session models + DB migration | All 16 tables exist; pgvector enabled; `alembic upgrade head` completes with zero errors | Do not add Nightcap-specific columns to platform tables |
| 2 | Knowledge graph core | `assert_knowledge`, `get_character_knowledge`, `revoke_knowledge` pass unit tests; AI response never references a fact outside the queried character knowledge state | Do not make knowledge state optional or a performance trade-off |
| 3 | Model routing abstraction | All generation calls route through `router.py`; no model name appears outside `routing_table.json`; swapping a table entry changes behavior with zero code changes | Do not hardcode any provider name outside `routing_table.json` |
| 4 | Arc execution engine (Nightcap arc) | Nightcap arc executes through all three beats in simulation harness; killer identity assigned at introduction; all beats reachable; session completes with reveal | Do not encode beat logic that only functions with linear arcs and fixed endpoints |
| 5 | Content safety pipeline | L1 hard stops block prohibited content before generation; L2 Safeguard classification fires before every generation call; all safety activations logged to `events` table | Do not add safety as a post-generation filter only; hard stops must be pre-generation |
| 6 | Content event system | Events emitted with correct `target_audience`; no event targeting player A is delivered to player B; shared_display events contain no private character information | Do not couple event emission to any named surface type |
| 7 | Character behavior engine | AI dialogue is consistent with `behavior_profile`; dialogue never references a fact outside the character's knowledge state; NPC-NPC interaction produces a coherent exchange without human input | Do not generate a character response without first querying that character's knowledge state |
| 8 | FastAPI layer + auth | Session create, start, event stream, and knowledge assert endpoints return correct schemas; API key auth passes; Firebase JWT validation passes | Do not put arc execution logic in route handlers |
| 9 | Session persistence | Mid-session interruption followed by resume restores to nearest designed beat; no knowledge state is lost; no session restarts from the beginning | Do not treat persistence as a post-MVP concern |
| 10 | Telemetry MVP minimum | Five minimum signals logging from the first production session; generation_logs table present with nullable columns; `CONTENT_LOGGING_ENABLED` flag controls full population | Do not run a session without telemetry active; sessions without telemetry are cost with no data return |
| 11 | Simulation harness | Synthetic player run completes full Nightcap arc end-to-end; seeded deterministic run produces identical output on repeated execution; batch tool runs 10 sessions headless | Do not ship to real users before the simulation harness validates the arc |

## 15.10 Monster RPG Reuse Boundary

When monster RPG development begins, these components require no changes:

- Session models (world sessions extend Session, not replace it)
- Knowledge graph (same assertion/revocation/query API; schema complexity increases via extensible schema, not restructure)
- Model routing (routing table gains new task types; abstraction layer unchanged)
- Content event system (new event types registered; emitter unchanged)
- Content safety pipeline (new content rails config; pipeline unchanged)
- FastAPI auth layer (unchanged)

These components require extension (new code added, no rewrites):

- Arc execution engine: world state persistence between sessions, emergent narrative beat types, procedural generation hooks
- Character behavior engine: player-defined motivation inference, dynamic difficulty adjustment, simultaneous multi-player world state tracking

**Validation rule:** If any component in the "no changes required" list above requires modification to support the monster RPG, that is a design error in the Nightcap implementation that must be identified and corrected before monster RPG development starts.

---
## SOURCE FILE: docs/architecture/README.md

# Architecture Directory

This directory contains the Technical Architecture documentation split into focused sections for easier navigation and versioning.

## Files

- **01-overview.md**: System architecture overview and component stack
- **02-technology-stack.md**: Technology decisions and infrastructure
- **03-arc-execution.md**: Arc execution engine and pacing system
- **04-knowledge-graph.md**: Knowledge graph design and operations
- **05-session-persistence.md**: Session state and interrupt/resume patterns
- **06-model-routing.md**: AI model routing and provider abstraction
- **07-character-behavior.md**: Character behavior engine and psychology
- **08-event-system.md**: Multi-surface content event delivery
- **09-developer-api.md**: REST API, arc definitions, SDK, and dashboard
- **10-content-safety.md**: Three-layer content safety architecture
- **11-telemetry.md**: Telemetry schema and signal collection
- **12-build-plan.md**: Incremental build plan and MVP criteria
- **13-cost-model.md**: Per-session costs and economic model
- **14-architecture-validation.md**: Validation against Monster RPG and future patterns
- **15-development-guide.md**: Agentic development guide and component specifications

## Adding New Architecture Files

- Follow the naming convention: `NN-description.md` (e.g., `16-scaling-strategy.md`)
- Each file should have a metadata block at the top:
  ```
  > Source: Project knowledge artifact 07-Technical-Architecture-v1.3
  > Last synced: YYYY-MM-DD
  > Do not edit this file directly; edit in Notion and re-sync.
  ```
- Use H1 headings for major sections
- Link between related files using relative markdown links
- Keep metadata synced when upstream architecture is updated

## Relationship to Other Documents

- Architecture justifies decisions → see `/docs/decisions` for ADRs
- Architecture defines what specs implement → see `/docs/specs` for detailed requirements
- Architecture is informed by product needs → see `/docs/prd` for product requirements

---
## SOURCE FILE: docs/architecture/supplemental-schemas.md

# Supplemental Table Schemas

> **Source:** Founder decisions recorded 2026-05-30.
> These schemas fill gaps in 07-Technical-Architecture-v1.3 for tables listed in §15.3
> but not given explicit column definitions there. When the architecture document is
> next synced from Notion, these schemas should be incorporated and this file removed.

---

## `accounts`

```sql
CREATE TABLE accounts (
    account_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid  TEXT NOT NULL UNIQUE,
    email         TEXT,
    display_name  TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at  TIMESTAMPTZ
);
```

`firebase_uid` is a Firebase-issued string identifier, not a UUID. `email` and `display_name`
are nullable because anonymous players who create an account post-session may not supply them.
No payment or billing fields — those belong in the game layer.

---

## `consent_records`

```sql
CREATE TABLE consent_records (
    consent_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID REFERENCES accounts(account_id),       -- nullable
    session_id      UUID REFERENCES sessions(session_id),       -- nullable
    consent_type    TEXT NOT NULL,   -- "content_logging" | "analytics" | "terms_of_service"
    granted         BOOLEAN NOT NULL,
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_at      TIMESTAMPTZ,
    consent_version TEXT NOT NULL
);
```

Both FKs are nullable: anonymous players have no `account_id`; consent may be recorded at
the session level before an account exists. `consent_version` is required for GDPR compliance —
records which version of the policy was agreed to. The `"content_logging"` consent type is
the gate that must be checked before `CONTENT_LOGGING_ENABLED` is flipped to `true` (§11.4).

---

## `relationships`

```sql
CREATE TABLE relationships (
    relationship_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id       UUID NOT NULL REFERENCES sessions(session_id),
    source_char_id   UUID NOT NULL REFERENCES characters(character_id),
    target_char_id   UUID NOT NULL REFERENCES characters(character_id),
    trust_level      FLOAT NOT NULL DEFAULT 0.5,
    history_tag      TEXT,    -- "rivalry" | "alliance" | "acquaintance" | "strangers" | etc.
    current_affect   TEXT,    -- "warm" | "cool" | "hostile" | "cautious" | "neutral"
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (session_id, source_char_id, target_char_id)
);
```

**Relationship to `characters.behavior_profile`:** `behavior_profile` is the authored baseline
(initialized at session start, read-only during play). `relationships` is the live mutable
session-scoped record of how dispositions evolve during play. The behavior engine reads
`relationships`, not `behavior_profile`, when building generation prompts (§7.2). The
`UNIQUE` constraint makes this upsert-friendly.

---

## `locations`

```sql
CREATE TABLE locations (
    location_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   UUID NOT NULL REFERENCES sessions(session_id),
    name         TEXT NOT NULL,
    description  TEXT,
    metadata     JSONB NOT NULL DEFAULT '{}'
);
```

Not used by Nightcap at MVP. Populated by the `world_generation` module in H2 (§14.2).
`metadata JSONB` is the extension point for monster RPG world-building properties.

---

## `objects`

```sql
CREATE TABLE objects (
    object_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   UUID NOT NULL REFERENCES sessions(session_id),
    location_id  UUID REFERENCES locations(location_id),        -- nullable
    name         TEXT NOT NULL,
    description  TEXT,
    metadata     JSONB NOT NULL DEFAULT '{}'
);
```

Not used by Nightcap at MVP. Populated by `world_generation` in H2.

---

## `decisions`

```sql
CREATE TABLE decisions (
    decision_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id     UUID NOT NULL REFERENCES sessions(session_id),
    timestamp      TIMESTAMPTZ NOT NULL DEFAULT now(),
    decision_type  TEXT NOT NULL,   -- "beat_entry" | "generative_trigger" | "safety_rule_fired"
    context        JSONB NOT NULL DEFAULT '{}',
    outcome        JSONB NOT NULL DEFAULT '{}'
);
```

The knowledge graph's operational audit trail (§4.2). Records arc execution decisions made
during a live session. **Distinct from `decision_logs` (§11.5):** `decisions` is
session-scoped and operational; `decision_logs` is cross-session analytical telemetry.

---

## `arc_beat_states`

```sql
CREATE TABLE arc_beat_states (
    state_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id           UUID NOT NULL REFERENCES sessions(session_id),
    beat_id              TEXT NOT NULL,
    statemachine_config  JSONB NOT NULL,
    transition_history   JSONB NOT NULL DEFAULT '[]',
    snapshot_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_current           BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX ON arc_beat_states (session_id, is_current);
```

`statemachine_config` stores python-statemachine's `configuration` value serialized as JSONB.
On resume, this is deserialized back into the statemachine instance (§5.2, §5.4).
`transition_history` is an ordered array of beat transitions for full replay.
`is_current` enables a simple indexed query to find the active snapshot. When a new snapshot
is written, the previous row's `is_current` is set to `false`.

---

## `characters` — confirmed columns only

The architecture confirms three columns. Additional columns are not yet specified:

```sql
character_id      UUID PRIMARY KEY DEFAULT gen_random_uuid()
behavior_profile  JSONB NOT NULL DEFAULT '{}'
embedding         VECTOR(1536)   -- NULL; populated when embedding collection activates (§4.5)
```

Additional columns (name, arc_id, session_id) are not defined in any architecture document.
Do not add them until specified.

---
## SOURCE FILE: docs/conventions/ai-contributions.md

# AI Agent Contribution Policy

## Tool Allocation

**Copilot (inline):** Real-time assistance and small edits (single file, under 50 lines) while the human is at the keyboard. Use for: code completion, quick fixes, simple refactors.

**Claude Code:** Synchronous multi-file work requiring context reasoning and complex debugging. Use for: implementing specs, fixing bugs across modules, refactoring, writing tests. Suitable for tasks the human is actively supervising.

**Codex (cloud):** Delegated async tasks with explicit specs and clear acceptance criteria. Use for: well-scoped features, batch operations, parallelizable work. No synchronous interaction expected; human reviews results asynchronously.

## Requirements

**Spec-first:** Any task larger than a single function requires a spec in `/docs/specs/` before implementation. Specs must define acceptance criteria. Use the template.

**Plan-then-code:** Agent writes a plan (as prose or structured outline), human approves it, then code is written. No implementation without approval.

**Tests with code:** Tests are written in the same commit/PR as the change, not in a follow-up. Tests must validate acceptance criteria from the spec. Focus areas: knowledge graph, arc transitions, safety, routing.

**Human review gate:** No PR merges to main without human review of the full diff. Automated checks (tests, linting, type checking) pass first, then human reviews.

## LLM-Dependent Code

Prompts, model selection, routing decisions, and eval cases are product surface and require scrutiny. Changes to these components require:
- Full traceability (why this model for this task?)
- An ADR in `/docs/decisions/` if behavior shifts meaningfully
- Extra review attention; these changes affect product quality and cost

## Branch Hygiene

- One agent per feature branch at a time
- If two agents must touch overlapping files, serialize them: first agent merges, second agent pulls main and continues
- Avoid merge conflicts on shared files by coordinating with the human


---
## SOURCE FILE: docs/conventions/ai-cost-policy.md

# AI Cost Policy

Use the lightest agent surface that matches the work.

## Agent Order

**First reach: Copilot in VS Code**

Use when the human is at the keyboard and the change is incremental.

**Second reach: Claude Code**

Use for synchronous multi-file work or complex debugging. Reserve it for cases where collaborative depth is needed.

**Third reach: Codex (cloud)**

Use for well-specified async tasks that can run while the human is unavailable. The spec must be complete before delegation.

**Avoid: Claude.ai Project chat for code generation**

Use that surface for strategy, planning, and spec writing.

## Workflow Rule

- One agent per feature branch.
- If a task is unclear, escalate to spec writing in Project chat before spending agent credits on implementation attempts.
- In the PR description, note which agents were used and roughly how much effort each contributed: `minimal`, `moderate`, or `primary`.

---
## SOURCE FILE: docs/conventions/coding-style.md

# Coding Style

Guidelines for Python and TypeScript code organization, naming, and structure.

To be completed: Covers indentation, naming conventions, file organization, imports, documentation standards, and links to specific code examples in the repo.

---
## SOURCE FILE: docs/conventions/README.md

# Conventions and Guidelines

This directory contains team conventions for code, testing, and contributions. These documents establish shared standards and make it easier for multiple contributors (especially AI agents) to understand and maintain the codebase.

## Structure

- **coding-style.md**: Python and TypeScript style, naming, file organization
- **testing.md**: Test structure, coverage, unit vs. integration testing philosophy
- **ai-contributions.md**: How AI agents should approach code changes, context, and uncertainty
- **ai-cost-policy.md**: Guidelines for token usage, model selection, batch operations, and budget awareness

## Using These Conventions

### For Code Contributors

1. Read the applicable convention file (e.g., coding-style.md for style, testing.md for tests)
2. Follow the style and structure described
3. When uncertain, default to existing code patterns in the repo

### For AI Agents

1. **Before starting work**: Read ai-contributions.md and ai-cost-policy.md
2. **During work**: Check coding-style.md and testing.md
3. **For new patterns**: Propose them in ai-contributions.md with ADR support

### For Maintainers

1. Use these documents to onboard new contributors
2. Link to conventions in code review comments
3. Update conventions when they become outdated

## Adding or Updating Conventions

- Propose changes as ADRs if they affect architecture or significant policy
- Update existing files directly for clarifications or new patterns
- Keep conventions concise and linked to actual code examples

---

See the individual files for details on each area.

---
## SOURCE FILE: docs/conventions/review-checklist.md

# Review Checklist

Spend more time here than feels comfortable. This is the most leveraged work in the AI-assisted workflow.

## Before Reading the Diff

- [ ] Is the spec linked, current, and approved?
- [ ] Are acceptance criteria testable and tested?
- [ ] Does the change scope match the spec scope?

## While Reading the Diff

- [ ] Read every file changed, not just the highlights.
- [ ] Look for scope creep beyond the approved spec.
- [ ] Look for weakened, deleted, or narrowly mocked tests that reduce confidence.
- [ ] Look for suppressed errors, broad exception handling, or TODOs that hide breakage.
- [ ] Look for new dependencies and confirm they were explicitly approved.
- [ ] Look for secrets, credentials, or unsafe logging of sensitive data.
- [ ] Look for hardcoded values that should live in config, env, or routing tables.
- [ ] Verify LLM-dependent code keeps prompts version-controlled.
- [ ] Verify eval cases were updated when prompt, routing, or model behavior changed.
- [ ] Verify model selection is justified and consistent with routing policy.

## Before Merging

- [ ] CI is green.
- [ ] No review comments are unresolved.
- [ ] An ADR was added if the architecture changed.
- [ ] Docs were updated if user-visible behavior changed.

---
## SOURCE FILE: docs/conventions/setup.md

# Local Setup

## Pre-Commit Hooks

Arcwright uses `pre-commit` for repo-wide local hooks because the repo mixes Python and TypeScript.

Install the repo's JS/TS tooling dependencies at the repo root:

```bash
npm install
```

Install the hook runner:

```bash
pip install pre-commit
```

Install the Git hooks in your local clone:

```bash
pre-commit install
```

Run the full hook suite manually before a PR if you want an early check:

```bash
pre-commit run --all-files
```

The configured hooks are check-only. They fail loudly for formatting, lint, secrets, and temporary debug markers, but they do not rewrite files during commit. The JS/TS hooks use the repo-root `node_modules`, so rerun `npm install` if those tool dependencies are missing.

---
## SOURCE FILE: docs/conventions/testing.md

# Testing

Guidelines for unit tests, integration tests, coverage, and testing philosophy.

To be completed: Covers test structure, fixture patterns, coverage expectations, mock strategies, async test patterns, and when to use each type of test.

---
## SOURCE FILE: docs/decisions/0000-template.md

# Status

**Proposed** (or: Accepted, Superseded)

---

# Context

What circumstances or problems led to this decision? Include:
- Background and motivation
- Alternatives considered (why we didn't choose them)
- Constraints or requirements that forced the decision

---

# Decision

What did we decide? Use clear, declarative language:
- "We use X for Y because Z"
- "We will not Z because of constraint Y"

---

# Consequences

What are the direct and indirect effects of this decision?

## Positive consequences
- ...

## Negative consequences
- ...

## Trade-offs
- What did we gain? What did we lose?

---

# References

- Related ADRs (if any)
- Architecture sections that depend on this decision
- Open questions or future reconsideration points

---
## SOURCE FILE: docs/decisions/0001-scaffolding-audit.md

# 0001 — Scaffolding Audit Against Technical Architecture v1.3

**Date:** 2026-05-20
**Status:** Informational — read-only analysis, no code changes
**Architecture reference:** `docs/07-Technical-Architecture-v1 3 35db7de354a881618e59e65c8e12caf6.md` (S1–S15)
**Scope:** All non-git, non-doc files in the repository as scaffolded by Codex

> Items marked **⚠ Expensive to undo** carry structural lock-in risk. Address these before building further code on top of them.

---

## 1 — Aligned

Scaffolding decisions that match the architecture doc.

### 1.1 Repository top-level directory structure
`engine/`, `api/`, `sdk/`, `dashboard/`, `migrations/`, `nightcap/`, `config/`, `scripts/` all present. Exact match to S15.1.

### 1.2 Engine submodule layout
`engine/arc/`, `engine/characters/`, `engine/knowledge/`, `engine/routing/`, `engine/safety/`, `engine/events/`, `engine/session/`, `engine/telemetry/`, `engine/tests/` all match S15.1. Init files in place.

### 1.3 API submodule layout
`api/routers/`, `api/auth/`, `api/schemas/` match S15.1.

### 1.4 `config/routing_table.json` content
The five task types present (`character_dialogue`, `pacing_decision`, `safety_classification`, `knowledge_inference`, `narrative_generation`) use the exact provider strings and model identifiers specified in S15.7. The `anthropic/` and `groq/` provider prefixes are correct.

### 1.5 `requirements.txt`
Exact match to S15.2: `python-statemachine>=3.0`, `fastapi>=0.111`, `uvicorn[standard]`, `asyncpg`, `sqlalchemy[asyncio]>=2.0`, `alembic`, `pydantic>=2.0`, `litellm>=1.30`, `firebase-admin`, `pgvector`, `python-dotenv`, `httpx`, `structlog`. No extra or missing packages.

### 1.6 `.env.example`
Exact match to S15.2: all six variables present with correct defaults, including `CONTENT_LOGGING_ENABLED=false` (the feature flag governing `generation_logs` content population per S11.4).

### 1.7 Python version target
`ruff.toml` sets `target-version = "py311"` and CI uses `PYTHON_VERSION: "3.11"`. Matches S2.3's "Python 3.11+ minimum."

### 1.8 `NightcapPlaceholderChart` beat structure
The `StateChart` subclass in `engine/arc_state.py` implements exactly the beat graph from S3.1: `introduction` (Compound, initial), `investigation` (Compound containing `clue_phase` Parallel region with `private_clues` and `interrogation` sub-regions), `reveal` (final). Arc-level transitions (`investigation_begins`, `accusation_filed`) match the architecture doc code listing.

### 1.9 StateChart base class used correctly
`NightcapPlaceholderChart` extends `StateChart`, not the legacy `StateMachine`. Matches S2.6's "StateChart is the base class (not StateMachine)."

### 1.10 TypeScript SDK package shape
`sdk/package.json` sets name `@arcwright/sdk`, TypeScript 5.x, `dist/` as output. Consistent with S9.4 and S2.3.

### 1.11 Dashboard framework
`dashboard/package.json` uses React 18.3, TypeScript, Vite. Matches S2.3 (React 18+).

### 1.12 Provider-agnostic routing evals
`evals/cases/no_hardcoded_model_strings_outside_routing_layer.json` enforces the core S6.2 rule ("no model name or provider string appears anywhere in the codebase outside `routing_table.json`") via a CI eval. The eval CI workflow fires on `config/routing_table.json` and `engine/routing/**` changes.

### 1.13 Routing table provider-prefix enforcement
`evals/cases/routing_provider_prefix_policy_fixture.json` enforces that all routing entries use `anthropic/` or `groq/` prefixes. The allowed-provider list matches S2.7's AI supply chain decisions.

### 1.14 Key hard constraints in CLAUDE.md / AGENTS.md
Both files correctly encode the five non-negotiable constraints: Python 3.11+, arc logic stays in Python, knowledge state queries mandatory before every AI generation call, provider/model names isolated to `routing_table.json` + `router.py`, safety enforced at engine layer.

---

## 2 — Diverged

Scaffolding decisions that contradict or extend the architecture doc. Items are ordered from highest to lowest reversal cost.

### 2.1 ⚠ Expensive to undo — `engine/arc_state.py` placement contradicts S15.1
**File:** `engine/arc_state.py`
**Architecture:** S15.1 puts arc execution code in `engine/arc/`. The spec's "first file to create" is `engine/session/models.py`.
**What the scaffold did:** The entire arc state machine implementation lives at `engine/arc_state.py` (top-level under `engine/`). The `engine/arc/` directory exists but contains only `__init__.py`. Tests import from `engine.arc_state` (not `engine.arc.arc_state`).
**Risk:** As more code builds on this import path, the rename becomes more disruptive. Moving the file now requires updating one import; doing it after `engine/routing/`, `engine/session/`, and `engine/knowledge/` are built against it compounds the churn. The architecture's module boundaries (`engine/arc/` as a self-contained package) are also semantic guides for future contributors.

### 2.2 ⚠ Expensive to undo — `ArcDefinition` is a dataclass, not a Pydantic BaseModel
**File:** `engine/arc_state.py:36–46`
**Architecture:** S15.4 defines `ArcDefinition` as a Pydantic `BaseModel` with a rich schema. The arc validation endpoint (`POST /v1/arcs/validate`, S9.2) requires Pydantic to validate arc JSON against the schema.
**What the scaffold did:** `ArcDefinition` is a Python `@dataclass`. It also omits most of the required fields: `character_mode`, `aesthetic_config`, `setting_constraint`, `arc_structure`, `play_mode`, `narrator`, `quality_tier_default`, `characters`, `beats` (as `list[BeatDefinition]`, not `dict`), `generative_elements`, `content_rails`, `knowledge_rules`, `pacing_config`, `victim_config`, `kill_config`, `murder_timing_range`, `session_duration_range`, `revelation_step_range`, `tone_config`. The scaffold only has `arc_id`, `name`, `beats`, `beat_graph`, `initial_beat`, `final_beats`, `pacing_config`, `generative_config`, `metadata`.
**Risk:** The arc validation endpoint and the runtime arc-loading path (`nightcap/arc.json` → `ArcDefinition`) both depend on Pydantic. Dataclass offers no JSON schema validation. The missing fields are not metadata — they are the runtime inputs for killer assignment logic, pacing engine weights, content safety rails, and narrator configuration. Any code that builds on the current thin `ArcDefinition` will need to be rewritten when the full schema is adopted.

### 2.3 ⚠ Expensive to undo — `ArcStateMachine` wrapper creates an incoherent dual-class architecture
**File:** `engine/arc_state.py:48–145`
**Architecture:** S3.1–S3.2 specifies a single `ArcStateChart` that subclasses `StateChart`, generated dynamically from an arc definition at session start. S3.2: "The StateChart class is generated at session start from the arc definition, not written statically per arc."
**What the scaffold did:** Created two classes: `ArcStateMachine` (a plain Python class with manual beat tracking, transition validation, and callback registration) and `NightcapPlaceholderChart` (the actual `StateChart` subclass). `ArcStateMachine` does not contain or drive a `StateChart` — it is a parallel, non-StateChart implementation of beat-graph logic that duplicates what python-statemachine already provides natively (transition guards, state history, entry/exit hooks).
**Risk:** Future developers will be uncertain which class is authoritative. The test suite validates `ArcStateMachine`'s `can_transition_to` logic (which is manual graph traversal) rather than StateChart's native guard system. This could lead to the engine being built against the wrapper instead of the StateChart, bypassing SCXML-compliant parallel regions and compound state semantics entirely. The architecture's requirement for `State.Parallel` (for simultaneous clue distribution + interrogation) is only honored in `NightcapPlaceholderChart`, not in `ArcStateMachine`.

### 2.4 `BeatConfig` name and schema conflict with `BeatDefinition`
**File:** `engine/arc_state.py:22–31`
**Architecture:** S15.4 names this type `BeatDefinition` with fields: `beat_id`, `beat_name`, `beat_type`, `story_circle_step`, `structural_function`, `dramatic_purpose`, `emotional_target`, `information_goal`, `tension_target`, `character_emphasis`, `authored_content`, `generative_triggers`, `entry_conditions`, `exit_conditions`, `pacing_config`, `audience_targets`, `mini_games`.
**What the scaffold did:** Named it `BeatConfig` with only: `beat_id`, `name`, `beat_type`, `description`, `entry_conditions`, `exit_conditions`, `generative_elements`, `dramatic_tension_target`.
**Risk:** A name mismatch (`BeatConfig` vs `BeatDefinition`) across the codebase will create confusion once `engine/arc/models.py` is written with the correct Pydantic schema. The missing fields (`story_circle_step`, `structural_function`, `tension_target`, `mini_games`) are functional engine inputs, not metadata — they drive the pacing engine and arc validation checks listed in S9.3.

### 2.5 `routing_table.json` missing two required task types
**File:** `config/routing_table.json`; `evals/cases/routing_table_required_tasks.json`
**Architecture:** S6.3 defines 7 MVP task types: `character_dialogue`, `narrative_generation`, `pacing_decision`, `knowledge_inference`, `safety_classification`, `killer_assignment`, `narrator_bridge`.
**What the scaffold did:** Only 5 task types present. `killer_assignment` (one-shot at session start for killer identity draw and behavior profile calibration) and `narrator_bridge` (short recap on session resume) are missing. The eval enforcement case also only checks for 5, so the gap is not currently caught by CI.
**Risk:** When the session coordinator loop is built, it will need `killer_assignment` routing. If the routing table is not updated first, callers will get a `KeyError`. The eval case also needs updating so the gap is enforced.

### 2.6 `routing_table.json` missing fallback entries
**File:** `config/routing_table.json`
**Architecture:** S6.5 explicitly specifies `standard_fallback` and `premium_fallback` keys per task type for LiteLLM's native fallback mechanism.
**What the scaffold did:** No fallback keys. LiteLLM will not fall back automatically on provider outage.
**Risk:** Sessions will fail hard on provider outage at MVP. Low cost to add now; adding after session coordinator is built requires testing the fallback path through a live coordinator.

### 2.7 `docs/` structure does not match what CLAUDE.md/AGENTS.md reference
**Files:** `CLAUDE.md`, `AGENTS.md`, `docs/` (flat Notion exports)
**Architecture:** Not explicitly specified in the architecture doc, but CLAUDE.md/AGENTS.md both reference `/docs/prd/`, `/docs/architecture/`, `/docs/decisions/`, `/docs/specs/`, `/docs/conventions/` as subdirectories.
**What the scaffold did:** The actual `docs/` directory is a flat export of Notion pages using hash-based filenames (e.g., `07-Technical-Architecture-v1 3 35db7de354a881618e59e65c8e12caf6.md`). None of the referenced subdirectories exist.
**Risk:** Any agent or developer following the CLAUDE.md workflow will fail immediately on "Read the relevant PRD section from `/docs/prd/`." This affects every agent session from the first task. Either the `docs/` directory needs to be reorganized into the referenced structure, or CLAUDE.md/AGENTS.md need to be updated to reflect the actual paths.

### 2.8 `.gitignore` does not exclude `__pycache__`
**File:** `.gitignore`
**Architecture:** Not specified, but standard Python practice.
**What the scaffold did:** The `.gitignore` only contains two lines: `evals/reports/*` and `!evals/reports/.gitkeep`. The `engine/__pycache__/` and `engine/tests/__pycache__/` directories (with Python 3.9 `.pyc` artifacts) are committed to the repository.
**Risk:** Every developer's local `__pycache__` will generate untracked files, creating noise in `git status` and potential confusion when `.pyc` files from different Python versions coexist. The 3.9 `.pyc` artifacts also confirm the scaffold was developed under Python 3.9, not 3.11 (see §2.9).

### 2.9 Scaffold was compiled under Python 3.9, not 3.11
**Files:** `engine/__pycache__/__init__.cpython-39.pyc`, `engine/arc_state.cpython-39.pyc`, `engine/tests/__pycache__/`
**Architecture:** S2.3: "Do not use Python below 3.11 anywhere in the codebase."
**What the scaffold did:** `.pyc` artifacts indicate the scaffold was run under Python 3.9. The code currently written uses no 3.11-specific syntax, so it happens to work on 3.9 — meaning the minimum version enforcement is not actually being exercised. `tomllib` (stdlib in 3.11) and asyncio performance improvements assumed by the architecture are not being validated.

---

## 3 — Unspecified

Scaffolding choices the architecture doc did not address. Each may need documentation or a decision record.

### 3.1 `evals/` directory and eval harness
Architecture doc S15.1 does not include `evals/` in the repository structure, and S2.9 (testing approach) does not describe a separate eval layer. The scaffold added `evals/cases/`, `evals/runners/`, and a dedicated CI workflow. The eval harness enforces the provider-agnostic routing constraint via automated case execution.
**Flag:** The evals CI workflow runs with `continue-on-error: true` and is marked "report-only for now and does not block merge." The provider-agnostic routing constraint is a hard MVP requirement (S15.9 component priority 3: "no model name appears outside `routing_table.json`"). A report-only eval does not actually enforce it. Decision needed: promote to a blocking check or document that the pre-commit `forbid-temporary-markers` hook is the enforcement mechanism.

### 3.2 Pre-commit hook configuration
`.pre-commit-config.yaml` is not specified in the architecture doc. The scaffold includes `ruff`, `gitleaks`, `prettier`, `eslint`, and a `forbid-temporary-markers` hook. The `forbid-temporary-markers` hook's `entry` regex pattern obscures the actual marker strings it searches for by splitting them with hyphens (`TO(DO-DELETE)|FIX(ME-ME)|XX(X-TEMP)|DEBUG-(ONLY)`). This is intentional (to prevent the hook from triggering on its own source) but unusual and should be documented.

### 3.3 CodeQL workflow
`.github/workflows/codeql.yml` exists. Static security analysis is not mentioned in the architecture doc. Worth documenting in the decisions log given the content safety emphasis in S10.

### 3.4 GitHub issue/PR templates
`.github/ISSUE_TEMPLATE/bug.md`, `.github/ISSUE_TEMPLATE/feature.md`, `.github/pull_request_template.md`. Not specified in architecture doc. Standard practice, but the PR template should be reviewed to confirm it references the architecture decision record format specified in CLAUDE.md.

### 3.5 `.github/copilot-instructions.md`
Not specified in architecture doc. Content is not visible in the audit (not read). If it duplicates or contradicts CLAUDE.md/AGENTS.md, that's a maintenance risk. Needs a policy on which agent-instruction file is authoritative.

### 3.6 `.cursorrules`
Not specified in architecture doc. Not read during this audit. Represents a third agent-instruction surface alongside CLAUDE.md and AGENTS.md.

### 3.7 Ruff lint rule selection
`ruff.toml` uses `select = ["E4", "E7", "E9", "F", "I"]` (pycodestyle errors, pyflakes, isort). No `S` (bandit security checks) or `B` (bugbear) rules. Given the architecture's content safety emphasis (S10 is an entire section), adding bandit-equivalent rules to catch security antipatterns in the engine code is worth evaluating before the safety pipeline is implemented.

### 3.8 `mypy` and `pylint` referenced in CLAUDE.md but absent from CI
CLAUDE.md lists `mypy engine/` and `python -m pylint engine/` with "TODO: setup needed." Neither appears in `requirements.txt` or `ci.yml`. The actual CI uses `ruff` for both lint and format. A decision is needed: adopt `mypy` for type checking (which complements ruff's static analysis) or document that ruff is the sole toolchain. Given the architecture's emphasis on Pydantic schemas, mypy would catch type errors in schema definitions early.

### 3.9 `PLAN.md` reference in CLAUDE.md
CLAUDE.md instructs agents to "Create or update `/PLAN.md` in session workspace" before implementing. This file does not exist in the repository. It's unclear whether this is intended as a project-level plan file (tracked in git) or an ephemeral agent-session artifact. If tracked, it should be created or gitignored.

### 3.10 `evals/` directory excluded from `no_hardcoded_model_strings` check
`evals/cases/no_hardcoded_model_strings_outside_routing_layer.json` excludes `evals/cases/` from the scan (as a fixture). This is correct, but the eval cases themselves contain model strings (`anthropic/claude-haiku-4-5-20251001`, etc.) as test fixtures. If model names change in the routing table, the eval cases will go stale and potentially produce false passes. A mechanism to keep eval fixtures in sync with the routing table should be documented.

### 3.11 `nightcap/arc.json` absent
Architecture doc S15.4: "Arc definitions are JSON files. Nightcap's arc definition lives at `nightcap/arc.json`. The platform reads this schema." The `nightcap/` directory contains only `.gitkeep`. The arc JSON is the canonical reference implementation that proves the arc format is not Nightcap-specific (an MVP done criterion, S12.3). Its absence is expected at this scaffold stage, but it is the first deliverable for Phase 1 of the arc execution engine build.

### 3.12 `engine/session/models.py` absent
Architecture doc S15.1: "First file to create: `engine/session/models.py`. This file defines the Session, SessionParticipant, and ArcBeat Pydantic models. Every other component depends on what a session is. Do not write any other file before this one exists and its schema is stable."
The scaffold did not create this file. Instead, the first file created was `engine/arc_state.py`. This ordering inverts the specified dependency chain: arc state depends on session models, not vice versa.

### 3.13 No Alembic setup
`migrations/` contains only `.gitkeep`. The architecture doc (S12.2 Phase 1) specifies the database schema and Alembic migrations as the first build phase, before any other component. No `alembic.ini`, `alembic/env.py`, or initial migration exists. This is expected at scaffold stage but the absence of even the Alembic init is notable given the architecture's emphasis on "all schema changes are Alembic migrations" (S2.4).

---

## Summary Table

| Finding | Category | Reversal cost |
|---|---|---|
| `engine/arc_state.py` should be `engine/arc/arc_state.py` | Diverged | High |
| `ArcDefinition` dataclass instead of Pydantic BaseModel with full schema | Diverged | High |
| `ArcStateMachine` wrapper creates dual-class incoherence with StateChart | Diverged | High |
| `BeatConfig` name and schema conflict with `BeatDefinition` | Diverged | Medium |
| Routing table missing `killer_assignment` and `narrator_bridge` task types | Diverged | Low |
| Routing table missing fallback entries | Diverged | Low |
| `docs/` flat structure vs. CLAUDE.md subdirectory references | Diverged | Medium |
| `.gitignore` missing standard Python exclusions | Diverged | Low |
| Scaffold compiled under Python 3.9, not 3.11 | Diverged | Low |
| `evals/` harness is report-only, not a merge gate | Unspecified | — |
| `engine/session/models.py` absent (spec says build this first) | Unspecified | — |
| `nightcap/arc.json` absent | Unspecified | — |
| No Alembic setup | Unspecified | — |
| mypy/pylint referenced in CLAUDE.md but not in CI or requirements | Unspecified | — |

---
## SOURCE FILE: docs/decisions/0002-harness-scenario-execution-contract.md

# 0002 — Harness Scenario Execution Contract

**Date:** 2026-06-01
**Status:** Accepted
**Architecture reference:** [docs/architecture/02-technology-stack.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/architecture/02-technology-stack.md), [docs/architecture/03-arc-execution.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/architecture/03-arc-execution.md), [docs/architecture/12-build-plan.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/architecture/12-build-plan.md), [docs/architecture/15-development-guide.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/architecture/15-development-guide.md)
**Spec reference:** [docs/specs/0016-aw-111-scripted-synthetic-player-driver.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/specs/0016-aw-111-scripted-synthetic-player-driver.md)
**Scope:** `engine/harness/` scripted synthetic player execution for AW-111

---

# Context

AW-111 adds a declarative scripted scenario layer on top of the AW-110 harness runner. The spec left three implementation details unresolved enough that the code needed a stable repo-local contract:

- `HarnessRun` had no participant storage, but AW-111 required stable synthetic player IDs to survive into downstream harness tooling.
- The spec described `expected_beat` as a post-transition assertion, but also required wrong-beat errors to be caught before live execution starts.
- The runner contract had no per-transition payload schema, but the scenario layer still needed basic validation.

Alternatives considered:

- Store participant IDs in a separate scenario-only lookup object. Rejected because AW-112 and later harness tooling need a canonical place on the run artifact itself.
- Try to statically predict beat outcomes without running transitions. Rejected because the existing source of truth is the AW-110 runner and `ArcStateChart`, not a parallel static analyzer.
- Invent required payload schemas for Nightcap transitions. Rejected because no such contract exists yet in the runner or coordinator design, and adding one now would ossify a premature API.

Constraints:

- Scenario execution must go through `HarnessRunner.apply_action`, not a second transition path.
- Synthetic player IDs must remain stable strings, not generated UUIDs.
- The scenario layer must stay offline and small, and must not introduce transport or provider concerns.

---

# Decision

We use the following harness scenario execution contract for AW-111:

1. `HarnessRun` includes `participants: list[str]`, populated with synthetic `player_id` values in input order during scenario execution.
2. `ScenarioExecutor` performs preflight validation by running the scripted steps through a throwaway `HarnessRunner` instance before starting the real run. `expected_beat` checks are evaluated during this preflight pass, and failures raise `ScenarioValidationError`.
3. Scenario payload validation remains intentionally narrow. The scenario layer validates actor existence, non-empty action type, and non-empty `expected_beat` when provided. Payload stays opaque and is passed through directly to `HarnessAction`.

---

# Consequences

## Positive consequences

- Stable synthetic player IDs now live on the run artifact that downstream replay and batch tooling already consumes.
- Wrong-beat scenarios fail before the live execution mutates the canonical run, while still using the real runner behavior as the source of truth.
- The scenario DSL stays small and engine-local, which matches the current harness scope and avoids inventing a premature public input contract.

## Negative consequences

- Preflight doubles the number of runner executions for successful scenarios.
- `HarnessRunner` remains the only authoritative transition validator, so scenario validation cannot be cheaper than a real step-through.
- If transition payload requirements are added later, this ADR will need to be superseded with a more explicit payload contract.

## Trade-offs

- We gain determinism, clear failures, and a canonical participant location.
- We give up a lighter-weight preflight and defer richer payload semantics until the runtime contract actually exists.

---

# References

- [docs/specs/0015-aw-110-headless-session-runner-core.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/specs/0015-aw-110-headless-session-runner-core.md)
- [docs/specs/0016-aw-111-scripted-synthetic-player-driver.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/specs/0016-aw-111-scripted-synthetic-player-driver.md)
- [docs/roadmap/tasks/AW-111-scripted-synthetic-player-driver.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/roadmap/tasks/AW-111-scripted-synthetic-player-driver.md)
- Future follow-up: pre-existing `make type` failures in `engine/arc/arc_state.py` and `engine/harness/runner.py` should be resolved before M1 is marked complete.

---
## SOURCE FILE: docs/decisions/0003-nightcap-web-experience-runtime.md

# 0003 - Nightcap Web Experience Runtime

**Date:** 2026-06-08
**Status:** Accepted
**Architecture reference:** `docs/architecture/01-overview.md`, `docs/architecture/08-event-system.md`, `docs/architecture/09-developer-api.md`, `docs/architecture/15-development-guide.md`
**Spec reference:** `docs/specs/0022-aw-202-nightcap-web-experience-runtime-decision.md`
**Scope:** Nightcap Layer 3 browser experience runtime for M4

---

# Context

AW-202 exists because `docs/02-Decisions-Log-Additions-May2026.md` Entry 3 already decided that Nightcap's experience layer will be outside Arcwright core and will connect to Arcwright through its API. That prior decision protects surface agnosticism: Arcwright emits structured events and the experience layer renders them.

The remaining decision is not whether to use a third-party app builder. The remaining decision is which web runtime hosts the custom browser experience for the shared display and each player phone.

Nightcap needs:

- Browser-based player devices with no app install
- A shared display for narrator and group-visible story moments
- QR or code join under 30 seconds
- Real-time room coordination for 4 to 10 players
- Private event delivery that never leaks one player's information to another player or to the shared display
- A runtime boundary that keeps Arcwright authoritative for session state, knowledge state, safety, telemetry, arc execution, and event audience targeting

Alternatives considered:

- Build the Nightcap experience as part of Arcwright core. Rejected because it violates the surface-agnostic platform boundary and turns a Nightcap display choice into platform architecture.
- Use a no-code or low-code app builder. Rejected because the product needs custom browser clients, real-time room behavior, scoped auth, reconnect behavior, and strict privacy guarantees.
- Build and host a separate conventional web app on the same GCP stack as Arcwright. Rejected for M4 because it gives less edge-native room coordination and does not improve the Arcwright core boundary.
- Use Cloudflare Pages, Workers, and Durable Objects, with PartyKit allowed as a room abstraction. Accepted because it fits the browser-first, room-oriented Nightcap UX while keeping Arcwright core unchanged.

---

# Decision

Nightcap's browser-based host, shared-display, and player-phone experience uses Cloudflare Pages, Workers, and Durable Objects as its web experience runtime. PartyKit may be used as an optional room abstraction on top of Durable Objects.

This is not a decision to build Nightcap in a third-party app builder. This is not a decision to move Arcwright engine, API, session state, knowledge graph, safety, model routing, telemetry, or persistence off the Arcwright backend.

Arcwright remains the source of truth for:

- Session lifecycle and canonical session state
- Arc execution and deterministic transitions
- Knowledge state and character state
- Content safety and model routing
- Telemetry and event persistence
- `ContentEvent.target_audience` and private event authorization

The Nightcap web experience runtime owns:

- Browser rendering for shared display, host controls, and player phones
- QR or code join UI
- Ephemeral room presence
- Reconnect UX and client coordination
- Presentation state derived from Arcwright events
- Deployment of the custom Nightcap web experience

## Integration contract

API assumptions:

- The Nightcap runtime consumes Arcwright REST lifecycle and input endpoints.
- The Nightcap runtime consumes Arcwright event delivery through the TypeScript SDK or an equivalent typed REST/SSE client.
- Host controls call Arcwright API endpoints. They do not bypass Arcwright session lifecycle or arc execution.

SDK assumptions:

- The TypeScript SDK remains a typed Arcwright API and SSE client.
- The SDK contains no arc execution logic, game rules, or rendering assumptions.
- Nightcap rendering code imports or wraps the SDK from the Cloudflare-hosted client.

Auth assumptions:

- Hosts authenticate through Arcwright's host auth path.
- Players join anonymously through scoped session join tokens.
- Player clients receive only the token and session context needed for their assigned participant.
- Secrets and API keys are not embedded in browser clients.

Event assumptions:

- `ContentEvent.target_audience` remains authoritative.
- `specific_player` events must only be delivered to the intended player device.
- `shared_display` events must never include private clue text.
- `host_only` events must not be rendered to player devices or the shared display.
- Presentation hints are rendering inputs only. They do not change engine state.

Privacy assumptions:

- The preferred delivery pattern is scoped Arcwright event streams per authorized client.
- If a Worker or Durable Object proxies event traffic, it must proxy scoped streams or equivalent Arcwright-authorized payloads.
- The Nightcap runtime must not ingest an all-events stream and reimplement private filtering as its primary privacy boundary.

Deployment assumptions:

- Cloudflare Pages hosts static browser assets.
- Cloudflare Workers handle lightweight join, bootstrap, and runtime coordination routes.
- Durable Objects or PartyKit rooms handle ephemeral session-room presence and reconnect coordination.
- Arcwright core remains deployed according to the existing backend architecture.

Performance and cost assumptions:

- Workers and Durable Objects stay thin. They do not run LLM calls, heavy generation, or canonical state transitions.
- Durable Objects store only ephemeral coordination state needed by the browser experience.
- WebSocket hibernation or sparse room activity should be used where M4 implementation requires long-lived room connections.
- H1 UI infrastructure cost is expected to be small relative to LLM cost, but measured gross margin remains the responsibility of AW-234.

---

# Consequences

## Positive consequences

- M4 can decompose against a concrete browser runtime instead of a TBD external platform.
- Nightcap gets a custom web experience suited to shared display plus phone play without native apps.
- Arcwright preserves surface agnosticism because all authoritative game and platform state remains behind Arcwright APIs.
- Durable Objects or PartyKit provide a natural place for ephemeral room presence and reconnect coordination.

## Negative consequences

- The system now has two deployment surfaces: Arcwright backend and Nightcap web runtime.
- M4 implementers must understand both Arcwright's event contract and Cloudflare's room-runtime model.
- Local development and observability will need explicit setup for the Cloudflare side during M4.

## Trade-offs

- We gain a browser-first, room-oriented runtime for Nightcap without polluting Arcwright core.
- We accept an additional runtime boundary and integration contract that must be tested on real devices.
- We keep core session authority in Arcwright and give up the simplicity of putting all Nightcap UI behavior in one backend stack.

---

# References

- `docs/02-Decisions-Log-Additions-May2026.md` Entry 3
- `docs/prd/02-requirements.md`
- `docs/architecture/08-event-system.md`
- `docs/architecture/09-developer-api.md`
- `docs/roadmap/00-overview.md`
- `docs/roadmap/milestones/M4-nightcap-experience-layer.md`
- `docs/roadmap/tasks/AW-202-external-nightcap-platform-decision.md`
- Cloudflare Workers pricing: https://developers.cloudflare.com/workers/platform/pricing/
- Cloudflare Durable Objects pricing: https://developers.cloudflare.com/durable-objects/platform/pricing/
- Cloudflare Durable Objects WebSockets: https://developers.cloudflare.com/durable-objects/best-practices/websockets/
- PartyKit: https://www.partykit.io/

---
## SOURCE FILE: docs/decisions/0004-pacing-telemetry-outcome-events.md

# 0004 - Pacing Telemetry Outcome Events

**Date:** 2026-06-10
**Status:** Accepted
**Architecture reference:** `docs/architecture/03-arc-execution.md`, `docs/architecture/11-telemetry.md`
**Spec reference:** `docs/specs/0027-aw-207-dramatic-tension-pacing-engine.md`
**Scope:** AW-207 pacing telemetry events, pacing intervention descriptors, and future pacing-loop outcome emission

---

# Context

AW-207 implements the deterministic dramatic tension pacing core. The existing telemetry architecture described a single `pacing_intervention` event with `outcome_resumed_within_60s` in the same payload.

That shape conflicts with the append-only `events` table contract in `docs/architecture/11-telemetry.md`. Whether player activity resumed within 60 seconds is not known when the pacing intervention first fires. Writing the trigger event and updating it later would violate the append-only telemetry model.

AW-207 also introduces `quality_upgrade` as a pacing descriptor for peak dramatic moments. It is a pacing decision, but it does not inject a player-facing stall or misdirection intervention and has no meaningful 60-second resumed-activity outcome.

Alternatives considered:

- Keep `outcome_resumed_within_60s` on `pacing_intervention` and update the row later. Rejected because the `events` table is append-only.
- Store pacing outcomes only in `decision_logs`. Rejected because pacing intervention triggers and outcomes are one of the five MVP telemetry signals and need event-table visibility.
- Emit `pacing_intervention` events for `quality_upgrade`. Rejected because quality-tier upgrades do not have resumed-activity semantics and would pollute player-facing intervention metrics.

Constraints:

- `events` records are never updated or deleted.
- MVP telemetry Signal 2 must capture pacing intervention triggers and outcomes.
- Pacing must remain platform-generic and must not hardcode Nightcap-specific signal derivation.
- AW-207 does not include the async pacing loop that waits 60 seconds and emits follow-up outcomes.

---

# Decision

We use a two-event append-only telemetry model for player-facing pacing intervention triggers and outcomes:

1. `tension_update` is emitted on each pacing poll with `payload = {"score": float, "beat_id": str}`.
2. `pacing_intervention` is emitted at trigger time only for `stall` and `misdirection`, with `payload = {"trigger_type": "stall" | "misdirection", "tension_score_at_trigger": float, "beat_id": str}`.
3. `pacing_intervention_outcome` is emitted after the follow-up window for the same player-facing intervention, with `payload = {"trigger_type": "stall" | "misdirection", "tension_score_at_trigger": float, "beat_id": str, "outcome_resumed_within_60s": bool}`.
4. `quality_upgrade` is a pacing decision descriptor, not a `pacing_intervention` event. It is captured through tension updates, generation logs when routing integration uses the score, and decision-log payloads when persistence integration is wired.
5. AW-207 defines payload builders only. The future async pacing-loop or session coordinator integration owns waiting 60 seconds, assessing resumed activity, and emitting `pacing_intervention_outcome`.

---

# Consequences

## Positive consequences

- Pacing telemetry preserves the append-only integrity of the `events` table.
- Trigger-time and outcome-time facts are recorded when they become known.
- MVP telemetry Signal 2 remains queryable through the event stream.
- Quality-tier upgrades do not distort stall and misdirection intervention metrics.
- Future coordinator work has a clear ownership boundary for delayed outcome emission.

## Negative consequences

- Consumers must join or correlate trigger and outcome events by session, beat, trigger type, and time window instead of reading one event payload.
- Telemetry readers must know that `quality_upgrade` is found in decision logs and generation logs, not in `pacing_intervention` outcome events.

## Trade-offs

- We gain append-only correctness and clearer telemetry semantics.
- We accept a slightly richer event taxonomy and defer delayed emission wiring to the async pacing-loop work.

---

# References

- `docs/architecture/03-arc-execution.md`
- `docs/architecture/11-telemetry.md`
- `docs/specs/0027-aw-207-dramatic-tension-pacing-engine.md`
- `docs/roadmap/tasks/AW-207-dramatic-tension-pacing-engine.md`

---
## SOURCE FILE: docs/decisions/0005-l1-hard-stop-boundary.md

# 0005 - L1 Hard Stop Boundary

**Date:** 2026-06-10
**Status:** Accepted
**Architecture reference:** `docs/architecture/10-content-safety.md`, `docs/architecture/15-development-guide.md`
**Spec reference:** `docs/specs/0028-aw-208-l1-hard-stops.md`
**Scope:** AW-208 deterministic L1 safety boundary and blocked-generation return contract

---

# Context

AW-208 adds deterministic Layer 1 safety hard stops before generation. `docs/architecture/10-content-safety.md` requires L1 to run before any model call, block unconditionally, log `safety_hard_stop`, and continue the session with a neutral narrator bridge.

The current implemented generation boundary is `engine.routing.logging.generate`. It owns model routing invocation, generation cost logging, fallback telemetry, and database access. The lower-level `engine.routing.router.route_generation` does not receive a database session and cannot log a `safety_hard_stop` event by itself.

The future session coordinator will eventually own richer bridge emission, actor attribution, and event flow. AW-208 needs a safe MVP contract that works before that coordinator path exists.

Alternatives considered:

- Raise a typed `SafetyHardStopError` and require callers to handle it. Rejected for AW-208 because current callers do not have a coordinator-owned safety bridge path yet, and an uncaught exception would turn unsafe input into a session failure.
- Put L1 in `route_generation`. Rejected because the low-level router lacks database access for `safety_hard_stop` logging and would mix routing with telemetry persistence.
- Return a neutral `RouteResult` sentinel from `generate`. Accepted because it preserves the current generation contract, avoids model calls, logs the hard stop, and keeps the session flowing.

Constraints:

- L1 cannot be disabled by arc configuration.
- L1 must not call an LLM or route through safety classification.
- L1 must not expose trigger details to players or logs.
- Production runtime code must not bypass `generate` by calling `route_generation` directly.

---

# Decision

We enforce AW-208 L1 hard stops at `engine.routing.logging.generate`.

When L1 blocks content:

1. `generate` logs `event_type = "safety_hard_stop"` with safe category/code metadata only.
2. `generate` flushes the database session.
3. `generate` does not call `route_generation`.
4. `generate` does not write a `generation_logs` row.
5. `generate` returns a neutral `RouteResult` sentinel with:
   - `content = "The narrator redirects the moment back to the story."`
   - `model_used = "l1_hard_stop"`
   - `input_tokens = 0`
   - `output_tokens = 0`
   - `latency_ms = 0`
   - `used_fallback = False`

`l1_hard_stop` is a non-provider sentinel, not a model identifier. It must never be written to `generation_logs`, cost calculation, or routing telemetry.

AW-208 also adds a static test that fails if production code outside the approved routing allowlist calls `route_generation` directly.

---

# Consequences

## Positive consequences

- Unsafe L1 content is blocked before any model call.
- Existing generation callers receive a normal-shaped result and do not crash.
- The player experience gets a neutral bridge instead of a revealing safety error.
- Safety telemetry is written at the same boundary that owns database access.
- The static test protects future runtime code from bypassing L1.

## Negative consequences

- The neutral bridge is generic until the session coordinator owns richer bridge emission.
- Callers must understand that `model_used = "l1_hard_stop"` is a sentinel, not a routed model.
- Future production wrappers around `route_generation` must update the static allowlist intentionally.

## Trade-offs

- We gain safe MVP behavior and minimal integration blast radius.
- We defer typed coordinator-level safety control flow until the coordinator exists.

---

# References

- `docs/architecture/10-content-safety.md`
- `docs/architecture/15-development-guide.md`
- `docs/specs/0028-aw-208-l1-hard-stops.md`
- `docs/roadmap/tasks/AW-208-l1-hard-stops.md`

---
## SOURCE FILE: docs/decisions/README.md

# Architecture Decision Records (ADRs)

This directory contains decisions that shape the technical platform. Each ADR captures a decision, the context that required it, and its consequences.

## Structure

- Use sequential numbering: `0001-use-python-statemachine.md`, `0002-chose-postgresql.md`
- Follow the ADR format (see `0000-template.md`)
- Status: Proposed → Accepted → Superseded (if replaced by a later decision)

## Adding a New ADR

1. Copy `0000-template.md` to the next sequential number: `000N-{decision-slug}.md`
2. Fill in all sections (Status, Context, Decision, Consequences, References)
3. Use present tense in decision statement: "We use X because..."
4. Be concise - aim for a single page or two
5. Link to related decisions and open questions in the header
6. Once approved, update status from "Proposed" to "Accepted"
7. If a decision is replaced, create a new ADR and mark the old one "Superseded"

## How ADRs Relate to Other Documents

- **To specs**: An ADR decides technology/approach; specs detail what to build
- **To architecture**: ADRs accumulate to form the architecture document
- **To PRDs**: ADRs may respond to product requirements or constraints

## Consulting ADRs

When proposing changes:
1. Check existing ADRs to understand past decisions
2. Reference relevant ADRs in your new proposal
3. If overriding a decision, create a superseding ADR explaining why

## Current ADRs

- `0001-scaffolding-audit.md` - repository scaffold audit against the technical architecture
- `0002-harness-scenario-execution-contract.md` - AW-111 scenario execution contract for participants, preflight validation, and payload scope
- `0003-nightcap-web-experience-runtime.md` - AW-202 Nightcap web experience runtime and Arcwright integration contract
- `0004-pacing-telemetry-outcome-events.md` - AW-207 append-only pacing trigger and outcome telemetry contract
- `0005-l1-hard-stop-boundary.md` - AW-208 deterministic L1 safety boundary and blocked-generation return contract

## Current Decision Categories

- **Technology choices**: Python, PostgreSQL, python-statemachine, LiteLLM
- **Architecture patterns**: Event-driven, knowledge graph, content safety layers
- **Scope decisions**: MVP vs. H2, schema-clean design, build paths
- **Design choices**: Character model, session state, pacing engine

---
## SOURCE FILE: docs/roadmap/epics/M1-A-scaffolding-and-infrastructure.md

# M1-A: Scaffolding and Infrastructure

**Milestone:** M1  
**Status:** Planned

## What This Epic Covers

Establish the Python package structure, tooling configuration, local development database, and Alembic migration infrastructure. Nothing in later M1 epics should proceed until this foundation is usable.

## Tasks

- [AW-101: Repository structure and Python project setup](../tasks/AW-101-repository-structure-and-python-project-setup.md)
- [AW-102: Local Postgres 15 + pgvector + Alembic init](../tasks/AW-102-local-postgres-pgvector-alembic-init.md)

## Epic Exit Criteria

- `engine/` and `api/` package boundaries are clear
- Tooling runs clean
- Local Postgres 15 + pgvector is available
- Alembic can upgrade and downgrade cleanly

---
## SOURCE FILE: docs/roadmap/epics/M1-B-data-model.md

# M1-B: Data Model

**Milestone:** M1  
**Status:** Active
**GitHub:** [Issue #4](https://github.com/nickejanssen/arcwright/issues/4)

## What This Epic Covers

Implement the platform data model and the first full migration, including all core platform tables and pgvector-enabled columns required by the architecture.

## Tasks

- [AW-103: SQLAlchemy models for all platform tables](../tasks/AW-103-sqlalchemy-models-for-all-platform-tables.md)
- [AW-104: First full Alembic migration](../tasks/AW-104-first-full-alembic-migration.md)

## Epic Exit Criteria

- All architecture-defined tables have models
- The first full migration upgrades and downgrades cleanly

---
## SOURCE FILE: docs/roadmap/epics/M1-C-knowledge-graph-core.md

# M1-C: Knowledge Graph Core

**Milestone:** M1  
**Status:** Planned

## What This Epic Covers

Implement the deterministic knowledge graph APIs and the pre-generation knowledge constraint hook that all future AI character generation must pass through.

## Tasks

- [AW-105: Knowledge graph assertion API](../tasks/AW-105-knowledge-graph-assertion-api.md)
- [AW-106: Pre-generation knowledge constraint hook](../tasks/AW-106-pre-generation-knowledge-constraint-hook.md)

## Epic Exit Criteria

- Knowledge state APIs are fully unit tested
- The generation knowledge hook is the single sanctioned context-assembly path

---
## SOURCE FILE: docs/roadmap/epics/M1-D-model-routing-abstraction.md

# M1-D: Model Routing Abstraction

**Milestone:** M1  
**Status:** Planned

## What This Epic Covers

Implement the provider-agnostic model-routing layer, routing-table behavior, prompt caching, and generation logging so later milestones can spend tokens safely and traceably.

## Tasks

- [AW-107: LiteLLM routing layer](../tasks/AW-107-litellm-routing-layer.md)
- [AW-108: Prompt caching and generation logging](../tasks/AW-108-prompt-caching-and-generation-logging.md)

## Epic Exit Criteria

- Model calls route through the router abstraction only
- Routing swaps require zero code changes
- Generation logging and cache strategy are wired

---
## SOURCE FILE: docs/roadmap/epics/M1-E-harness-scaffold.md

# M1-E: Harness Scaffold

**Milestone:** M1  
**Status:** Planned

## What This Epic Covers

Provide the first headless simulation harness that can instantiate, step, script, and repeat a session deterministically without UI.

## Tasks

- [AW-110: Headless session runner core](../tasks/AW-110-simulation-harness-skeleton.md)
- [AW-111: Scripted synthetic player driver](../tasks/AW-111-scripted-synthetic-player-driver.md)
- [AW-112: Deterministic replay and batch runner](../tasks/AW-112-deterministic-replay-and-batch-runner.md)

## Epic Exit Criteria

- A headless deterministic session runner exists
- Synthetic player scenarios are scriptable
- Seeded runs are repeatable
- Batch runner can execute 10 headless sessions without UI

---
## SOURCE FILE: docs/roadmap/epics/M2-A-external-platform-decision-gate.md

# M2-A: Nightcap Web Experience Runtime Decision Gate

**Milestone:** M2  
**Status:** Planned

## Plain-English Summary

Select the Nightcap web experience runtime early enough that M4 implementation can follow a concrete integration contract.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/02-Decisions-Log-Additions-May2026.md Entry 3` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-202: Nightcap Web Experience Runtime Decision](../tasks/AW-202-external-nightcap-platform-decision.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M2
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/02-Decisions-Log-Additions-May2026.md Entry 3
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M2-B-arc-execution-engine.md

# M2-B: Arc Execution Engine

**Milestone:** M2  
**Status:** Planned

## Plain-English Summary

Build the platform arc runtime that can execute authored beat graphs and trigger generation without giving AI control of state.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/architecture/03-arc-execution.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-203: ArcDefinition Schema And Validation Core](../tasks/AW-203-arcdefinition-schema-and-validation-core.md)
- [AW-204: Dynamic ArcStateChart Generation](../tasks/AW-204-dynamic-arcstatechart-generation.md)
- [AW-207: Dramatic Tension Pacing Engine](../tasks/AW-207-dramatic-tension-pacing-engine.md)
- [AW-214: M2 Headless Nightcap Exit Harness](../tasks/AW-214-m2-headless-nightcap-exit-harness.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M2
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/architecture/03-arc-execution.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M2-C-nightcap-arc-runtime.md

# M2-C: Nightcap Arc Runtime

**Milestone:** M2  
**Status:** Planned

## Plain-English Summary

Create the canonical Nightcap arc definition and runtime decisions needed for murder mystery flow.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/prd/02-requirements.md Nightcap Reference Implementation` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-205: Nightcap Canonical Arc JSON](../tasks/AW-205-nightcap-canonical-arc-json.md)
- [AW-206: Killer Assignment And Reveal State](../tasks/AW-206-killer-assignment-and-reveal-state.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M2
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/prd/02-requirements.md Nightcap Reference Implementation
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M2-D-content-safety-pipeline.md

# M2-D: Content Safety Pipeline

**Milestone:** M2  
**Status:** Planned

## Plain-English Summary

Add engine-layer safety before every generation path.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/architecture/10-content-safety.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-208: L1 Hard Stops](../tasks/AW-208-l1-hard-stops.md)
- [AW-209: L2 Pre-Generation Classification](../tasks/AW-209-l2-pre-generation-classification.md)
- [AW-210: L3 Policy Injection And Neutral Bridge](../tasks/AW-210-l3-policy-injection-and-neutral-bridge.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M2
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/architecture/10-content-safety.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M2-E-character-behavior-engine.md

# M2-E: Character Behavior Engine

**Milestone:** M2  
**Status:** Planned

## Plain-English Summary

Generate AI character behavior from profile, relationships, pressure, knowledge, safety, and routing.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/architecture/07-character-behavior.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-211: Behavior Profile Assembly](../tasks/AW-211-behavior-profile-assembly.md)
- [AW-212: Knowledge-Constrained Dialogue Pipeline](../tasks/AW-212-knowledge-constrained-dialogue-pipeline.md)
- [AW-213: AI Initiative And NPC-NPC Exchange](../tasks/AW-213-ai-initiative-and-npc-npc-exchange.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M2
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/architecture/07-character-behavior.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M3-A-content-event-system.md

# M3-A: Content Event System

**Milestone:** M3  
**Status:** Planned

## Plain-English Summary

Deliver structured ContentEvents to the right audiences with ordering and replay.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/architecture/08-event-system.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-215: ContentEvent Model And In-Memory Bus](../tasks/AW-215-contentevent-model-and-in-memory-bus.md)
- [AW-216: SSE Fanout Filtering And Replay](../tasks/AW-216-sse-fanout-filtering-and-replay.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M3
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/architecture/08-event-system.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M3-B-api-auth-and-typescript-sdk.md

# M3-B: API, Auth, And TypeScript SDK

**Milestone:** M3  
**Status:** Planned

## Plain-English Summary

Expose session, character, knowledge, and event flows through thin API handlers and a typed SDK.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/architecture/09-developer-api.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-217: Session Lifecycle API And Auth](../tasks/AW-217-session-lifecycle-api-and-auth.md)
- [AW-218: Character Input And Knowledge Endpoints](../tasks/AW-218-character-input-and-knowledge-endpoints.md)
- [AW-219: TypeScript SDK Event And Input Client](../tasks/AW-219-typescript-sdk-event-and-input-client.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M3
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/architecture/09-developer-api.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M3-C-session-persistence-and-resume.md

# M3-C: Session Persistence And Resume

**Milestone:** M3  
**Status:** Planned

## Plain-English Summary

Persist live session state continuously and resume from the nearest designed beat.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/architecture/05-session-persistence.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-220: Session Persistence Snapshots And Resume](../tasks/AW-220-session-persistence-snapshots-and-resume.md)
- [AW-221: Narrator Bridge On Resume](../tasks/AW-221-narrator-bridge-on-resume.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M3
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/architecture/05-session-persistence.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M3-D-telemetry-and-full-simulation-harness.md

# M3-D: Telemetry And Full Simulation Harness

**Milestone:** M3  
**Status:** Planned

## Plain-English Summary

Log required signals and prove the full API path through repeated offline sessions.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/architecture/11-telemetry.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-222: Five MVP Telemetry Signals](../tasks/AW-222-five-mvp-telemetry-signals.md)
- [AW-223: Cost And Usage Summary](../tasks/AW-223-cost-and-usage-summary.md)
- [AW-224: Full API Batch Harness](../tasks/AW-224-full-api-batch-harness.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M3
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/architecture/11-telemetry.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M4-A-nightcap-external-platform-integration.md

# M4-A: Nightcap Web Experience Runtime Integration

**Milestone:** M4  
**Status:** Planned

## Plain-English Summary

Implement the Nightcap web experience runtime connector according to the AW-202 contract.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/02-Decisions-Log-Additions-May2026.md Entry 3` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-225: Nightcap Web Experience Runtime Connector Scaffold](../tasks/AW-225-external-platform-connector-scaffold.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M4
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/02-Decisions-Log-Additions-May2026.md Entry 3
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M4-B-nightcap-host-and-shared-display-experience.md

# M4-B: Nightcap Host And Shared Display Experience

**Milestone:** M4  
**Status:** Planned

## Plain-English Summary

Build host controls and shared display rendering from public ContentEvents only.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/prd/02-requirements.md Host experience` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-226: Host Session Creation And Shared Display Flow](../tasks/AW-226-host-session-creation-and-shared-display-flow.md)
- [AW-227: Shared Display Narrator And Group Event Rendering](../tasks/AW-227-shared-display-narrator-and-group-event-rendering.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M4
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/prd/02-requirements.md Host experience
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M4-C-nightcap-player-device-experience.md

# M4-C: Nightcap Player Device Experience

**Milestone:** M4  
**Status:** Planned

## Plain-English Summary

Build player join, private event, character, and input flows on player devices.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/prd/02-requirements.md Player experience` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-228: Player Join Flow Under 30 Seconds](../tasks/AW-228-player-join-flow-under-30-seconds.md)
- [AW-229: Player Private Event And Input Flow](../tasks/AW-229-player-private-event-and-input-flow.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M4
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/prd/02-requirements.md Player experience
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M4-D-real-device-privacy-and-join-validation.md

# M4-D: Real-Device Privacy And Join Validation

**Milestone:** M4  
**Status:** Planned

## Plain-English Summary

Verify the complete real-device setup before any qualifying playtest.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/roadmap/milestones/M4-nightcap-experience-layer.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-230: Real-Device Privacy Matrix](../tasks/AW-230-real-device-privacy-matrix.md)
- [AW-231: M4 Real-Human Rehearsal](../tasks/AW-231-m4-real-human-rehearsal.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M4
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/roadmap/milestones/M4-nightcap-experience-layer.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M5-A-adversarial-safety-and-remediation.md

# M5-A: Adversarial Safety And Remediation

**Milestone:** M5  
**Status:** Planned

## Plain-English Summary

Probe safety rails with hostile and uncomfortable inputs, then resolve blockers.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/prd/03-scope.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-232: Adversarial Safety Playtest Protocol](../tasks/AW-232-adversarial-safety-playtest-protocol.md)
- [AW-233: Safety Findings Remediation](../tasks/AW-233-safety-findings-remediation.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M5
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/prd/03-scope.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M5-B-cost-usage-and-gross-margin.md

# M5-B: Cost, Usage, And Gross Margin

**Milestone:** M5  
**Status:** Planned

## Plain-English Summary

Compute per-session cost and gross-margin readiness by player count.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/architecture/13-cost-model.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-234: Gross Margin By Player Count](../tasks/AW-234-gross-margin-by-player-count.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M5
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/architecture/13-cost-model.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M5-C-second-arc-schema-validation.md

# M5-C: Second Arc Schema Validation

**Milestone:** M5  
**Status:** Planned

## Plain-English Summary

Design one non-Nightcap arc schema to prove platform-clean abstractions.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/architecture/14-architecture-validation.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-235: Second Arc Schema Design](../tasks/AW-235-second-arc-schema-design.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M5
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/architecture/14-architecture-validation.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M5-D-visual-storyworld-phase-1-inspection.md

# M5-D: Visual Storyworld Phase 1 Inspection

**Milestone:** M5  
**Status:** Planned

## Plain-English Summary

Ship all four read-only inspection surfaces required for H1.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/prd/03-scope.md Visual Storyworld Roadmap` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-236: Live Knowledge Graph Inspection](../tasks/AW-236-live-knowledge-graph-inspection.md)
- [AW-237: Read-Only Arc Structure Inspection](../tasks/AW-237-read-only-arc-structure-inspection.md)
- [AW-238: Live Event Stream Inspection](../tasks/AW-238-live-event-stream-inspection.md)
- [AW-239: Character State Inspection](../tasks/AW-239-character-state-inspection.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M5
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/prd/03-scope.md Visual Storyworld Roadmap
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M6-A-playtest-operations.md

# M6-A: Playtest Operations

**Milestone:** M6  
**Status:** Planned

## Plain-English Summary

Prepare recruitment, consent, host scripts, instrumentation, and rehearsal for qualifying sessions.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/prd/02-requirements.md Success criteria` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-240: Closed Playtest Operations Runbook](../tasks/AW-240-closed-playtest-operations-runbook.md)
- [AW-241: Qualifying Session Instrumentation Checklist](../tasks/AW-241-qualifying-session-instrumentation-checklist.md)
- [AW-242: Founder-Run Final Rehearsal](../tasks/AW-242-founder-run-final-rehearsal.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M6
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/prd/02-requirements.md Success criteria
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M6-B-qualifying-session-execution.md

# M6-B: Qualifying Session Execution

**Milestone:** M6  
**Status:** Planned

## Plain-English Summary

Run the five outside-group Nightcap sessions that test the H1 product thesis.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/roadmap/milestones/M6-first-qualifying-sessions.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-243: Five Outside Qualifying Sessions](../tasks/AW-243-five-outside-qualifying-sessions.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M6
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/roadmap/milestones/M6-first-qualifying-sessions.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/epics/M6-C-h1-proof-analysis.md

# M6-C: H1 Proof Analysis

**Milestone:** M6  
**Status:** Planned

## Plain-English Summary

Analyze the first qualifying sessions and record the next product decision.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/prd/02-requirements.md Personalization perception gate` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-244: H1 Proof Analysis And Next-Step Decision](../tasks/AW-244-h1-proof-analysis-and-next-step-decision.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M6
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/prd/02-requirements.md Personalization perception gate
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.

---
## SOURCE FILE: docs/roadmap/operations/github-project-setup.md

# GitHub Tracker Alignment

This file is the operational companion to the roadmap. The GitHub Project, milestones, labels, and M1 Epic A issues already exist; this doc explains both how they stay aligned with the canonical roadmap in `docs/roadmap/` and how to rebuild them from the repo if needed.

## Ownership Split

- Roadmap Markdown files are the source of truth for scope and sequencing.
- `index.json` is the machine-readable join layer between roadmap IDs and live GitHub objects.
- GitHub Issues, milestones, and the project board are the execution surface for active work.

## Current Live References

- Repository: `nickejanssen/arcwright`
- Milestone `M1`: [milestone 1](https://github.com/nickejanssen/arcwright/milestone/1)
- Epic `M1-A`: [issue #1](https://github.com/nickejanssen/arcwright/issues/1)
- Task `AW-101`: [issue #2](https://github.com/nickejanssen/arcwright/issues/2)
- Task `AW-102`: [issue #3](https://github.com/nickejanssen/arcwright/issues/3)

## What The Repo Already Captures

- Issue creation shape lives in `.github/ISSUE_TEMPLATE/feature.md` and `.github/ISSUE_TEMPLATE/bug.md`
- PR review expectations live in `.github/pull_request_template.md`
- Canonical epic and task scope lives in `docs/roadmap/epics/` and `docs/roadmap/tasks/`
- Live GitHub cross-references live in `docs/roadmap/index.json`

## What Was Missing Before

Before this update, the repo did not contain a reproducible definition of labels, milestones, or project fields. That meant the live setup could be referenced, but not rebuilt cleanly from repo state alone.

The rebuild source now lives in:

- `.github/tracker/labels.json`
- `.github/tracker/milestones.json`
- `.github/tracker/project.json`
- `.github/tracker/README.md`

## Rebuild From Scratch

If the GitHub tracker had to be recreated:

1. Create the repository labels from `.github/tracker/labels.json`.
2. Create milestones from `.github/tracker/milestones.json`.
3. Create a table-style GitHub Project named `Arcwright Build`.
4. Recreate the project fields from `.github/tracker/project.json`.
5. Create the seed issues listed in `.github/tracker/project.json` using the roadmap files referenced by each `roadmap_path`.
6. Add those issues to the project and set their `Size`, `Status`, and `Epic` fields as appropriate.
7. Record any newly created GitHub numbers back into `docs/roadmap/index.json`.

This keeps the rebuild process deterministic without pretending that the live GitHub tracker is the source of truth.

## Cross-Reference Policy

- Keep canonical IDs like `M1-A` and `AW-101` in every GitHub epic or task title.
- Do not paste live issue numbers or URLs into every roadmap Markdown file.
- Store known live GitHub numbers and URLs in `docs/roadmap/index.json`.
- If a GitHub issue changes title, preserve the roadmap ID prefix so agents can still resolve it quickly.

## Working Pattern Going Forward

1. Write or update the roadmap Markdown file first.
2. Create or update the GitHub issue from that canonical file.
3. Add the GitHub issue number and URL to `docs/roadmap/index.json`.
4. Use the existing issue templates in `.github/ISSUE_TEMPLATE/` for issue body structure when creating net-new tracker items.
5. Use `.github/pull_request_template.md` so shipped work always links back to the relevant spec and notes which agents contributed.

## Why The Links Live In The Manifest

Issue numbers, milestone numbers, and project URLs are external execution details that can change independently of roadmap content. Keeping those cross-references in `index.json` makes them easy for agents to query without turning every roadmap file into a tracker mirror.

---
## SOURCE FILE: docs/roadmap/operations/working-model.md

# Working Model

## Tracker

Use GitHub Projects plus GitHub Issues.

- Milestones M1-M6 map to GitHub Milestones.
- Epics are parent issues.
- Tasks (`AW-xxx`) are sub-issues under their epic.

The task spec body in the roadmap should be copied into the issue body.

## Per Work Session

1. Identify the current milestone and epic.
2. Use the AW-201 decomposition for M2-M6. Revise task details when new decisions land, especially the AW-202 Nightcap web experience runtime contract that shapes M4 implementation.
3. Hand agents one task at a time.
4. If a coding decision affects strategy or architecture, record it in the Decisions Log flow described in `AGENTS.md`.

## Cadence

- Weekly: choose the next 1-3 tasks.
- Per milestone: verify exit criteria before starting the next milestone.
- Monthly: if you are still in the same milestone you expected to have finished, treat that as a signal to inspect scope, architecture friction, or execution assumptions.

## Open Dependencies and Risks

- Nightcap trademark clearance remains a high-priority non-engineering item.
- Enterprise buyer interviews should start once demo footage exists.
- The biggest schedule risk is treating M6 proof and personalization diagnosis as a formality rather than a real product gate.

---
## SOURCE FILE: docs/roadmap/tasks/AW-101-repository-structure-and-python-project-setup.md

# AW-101: Repository structure and Python project setup

**Milestone / Epic:** M1 / A  
**Size:** S  
**Implements:** Arch S2.3, S2.4  
**Depends on:** none

## Build

Establish the Python package layout for the `arcwright-engine` library and a separate `arcwright-api` package. Configure `pyproject.toml` with locked dependency versions, ruff for lint, mypy strict for type checking, and pytest. Add a Makefile or task runner with `lint`, `type`, `test`, and `migrate` commands.

## Acceptance Criteria

- [ ] `engine/` and `api/` packages exist with `__init__.py` and clear module boundaries
- [ ] `pyproject.toml` pins Python 3.11+, SQLAlchemy 2.0, asyncpg, alembic, fastapi 0.111+, python-statemachine 3.0+, litellm 1.30+
- [ ] `make lint` runs ruff and passes clean
- [ ] `make type` runs mypy strict and passes clean
- [ ] `make test` runs pytest on an empty test suite and passes clean
- [ ] Four test directories scaffolded empty: `tests/knowledge_graph/`, `tests/arc/`, `tests/safety/`, `tests/routing/`

## Do NOT

- Put any arc execution or game logic in the `api` package
- Mix engine and api dependencies into one package
- Use Python below 3.11 anywhere in the codebase

## Testing

Test directories scaffolded per Arch S2.9 four locked test areas.

## Agent Notes

First action before creating anything: inspect the current repo state and reconcile what already exists before creating or replacing files. Do not clobber existing work.

---
## SOURCE FILE: docs/roadmap/tasks/AW-102-local-postgres-pgvector-alembic-init.md

# AW-102: Local Postgres 15 + pgvector + Alembic init

**Milestone / Epic:** M1 / A  
**Size:** S  
**Implements:** Arch S2.2, S2.4  
**Depends on:** AW-101

## Build

Provide a docker-compose configuration running Postgres 15 with pgvector for local development, mirroring the Cloud SQL instance that will run in production. Initialize Alembic with async engine configuration. Write the first migration: `CREATE EXTENSION IF NOT EXISTS vector` and nothing else.

## Acceptance Criteria

- [ ] `docker compose up` brings up Postgres 15 with pgvector available
- [ ] Alembic is configured for SQLAlchemy 2.0 async (`asyncpg` driver)
- [ ] `alembic upgrade head` enables the vector extension with zero errors
- [ ] `alembic downgrade base` reverses cleanly
- [ ] No connection strings hardcoded; all config via environment variables
- [ ] README documents the `docker compose up` and migration steps

## Do NOT

- Apply any schema changes directly to any database outside Alembic
- Hardcode connection strings or credentials anywhere in the codebase
- Create any application tables in this migration

## Testing

Manual upgrade and downgrade cycle against the docker database.

## Agent Notes

Cloud SQL provisioning is a founder action. Agent work here is local development parity only.

---
## SOURCE FILE: docs/roadmap/tasks/AW-103-sqlalchemy-models-for-all-platform-tables.md

# AW-103: SQLAlchemy models for all platform tables

**Milestone / Epic:** M1 / B  
**Size:** L  
**Implements:** Arch S4, S5, S2.10  
**Depends on:** AW-102

## Build

Implement SQLAlchemy 2.0 async models for the full platform data model as enumerated in the architecture data-model sections. Use platform-clean schema names and include nullable `VECTOR(1536)` columns on the specified tables.

## Acceptance Criteria

- [ ] Every table in the architecture data-model section has a corresponding model
- [ ] Schema names are platform-clean; no game-specific semantics in column names
- [ ] pgvector columns present and nullable on the specified tables
- [ ] No Nightcap-specific columns on platform tables

## Do NOT

- Add Nightcap-only columns to platform tables
- Invent table or column names
- Use SQLAlchemy 1.x legacy style

## Testing

Model import smoke tests and relationship integrity checks.

## Agent Notes

If the data-model section is ambiguous on a table or column, stop and flag it rather than guessing.

---
## SOURCE FILE: docs/roadmap/tasks/AW-104-first-full-alembic-migration.md

# AW-104: First full Alembic migration

**Milestone / Epic:** M1 / B  
**Size:** M  
**Implements:** Arch S2.4, S15.9 #1  
**Depends on:** AW-103

## Build

Generate and hand-verify the Alembic migration that creates all platform tables, indexes, and foreign keys. Confirm pgvector extension ordering.

## Acceptance Criteria

- [ ] `alembic upgrade head` creates all tables with zero errors
- [ ] pgvector extension created before vector columns
- [ ] `alembic downgrade base` drops everything cleanly
- [ ] Migration is deterministic and re-runnable on a fresh DB

## Do NOT

- Edit a generated migration to include manual schema drift not reflected in models

## Testing

Fresh-database upgrade and downgrade cycle in CI and locally.

## Agent Notes

Autogenerate, then review by hand. Alembic autogenerate misses some pgvector and index details.

---
## SOURCE FILE: docs/roadmap/tasks/AW-105-knowledge-graph-assertion-api.md

# AW-105: Knowledge graph assertion API

**Milestone / Epic:** M1 / C  
**Size:** L  
**Implements:** Arch S4, PRD Principle 5, S15.9 #2  
**Depends on:** AW-104

## Build

Implement `assert_knowledge`, `get_character_knowledge`, and `revoke_knowledge` against the knowledge-state data model. These are deterministic functions with no AI calls.

## Acceptance Criteria

- [ ] `assert_knowledge`, `get_character_knowledge`, and `revoke_knowledge` are implemented and unit tested
- [ ] Querying a character's knowledge returns only facts that character has learned
- [ ] Revocation removes access without deleting the underlying fact
- [ ] Provenance is recorded on assertion

## Do NOT

- Make knowledge state optional or a performance trade-off
- Allow any path that returns facts outside the queried character's state

## Testing

Knowledge graph correctness is one of the locked unit-test areas. Write the full unit suite here.

## Agent Notes

This is one of the most important correctness boundaries in the platform. Over-test it.

---
## SOURCE FILE: docs/roadmap/tasks/AW-106-pre-generation-knowledge-constraint-hook.md

# AW-106: Pre-generation knowledge constraint hook

**Milestone / Epic:** M1 / C  
**Size:** M  
**Implements:** Arch S4, S7, PRD Principle 5  
**Depends on:** AW-105

## Build

Implement the interface that every AI character generation call must pass through, which queries the speaking character's knowledge state and assembles the allowed-facts context. This is the deterministic gate future character behavior will call.

## Acceptance Criteria

- [ ] A single function takes a character ID and returns that character's complete current knowledge as generation context
- [ ] The interface is the only sanctioned path to assemble character context for generation
- [ ] Returns are stable and ordered for prompt-cache friendliness

## Do NOT

- Allow generation context assembly to bypass this hook anywhere in the codebase

## Testing

Unit test that the hook never returns a fact outside the character's state.

## Agent Notes

Design this as the chokepoint now so later milestones cannot accidentally route around it.

---
## SOURCE FILE: docs/roadmap/tasks/AW-107-litellm-routing-layer.md

# AW-107: LiteLLM routing layer

**Milestone / Epic:** M1 / D  
**Size:** M  
**Implements:** Arch S2.7, S15.7, PRD Principles 6 and 8, S15.9 #3  
**Depends on:** AW-101

## Build

Implement `engine/routing/router.py` and `config/routing_table.json` exactly as specified in the architecture. All model calls go through the router keyed by `task_type` and `quality_tier`.

## Acceptance Criteria

- [ ] All generation calls route through `router.py`
- [ ] No model name or provider string appears anywhere outside `routing_table.json` and `router.py`
- [ ] Swapping a routing-table entry changes behavior with zero code changes
- [ ] `task_type` and `quality_tier` are the only model-selection inputs callers provide

## Do NOT

- Hardcode any provider name outside `routing_table.json`
- Expose model names to any caller

## Testing

Model routing fallback is a locked unit-test area. Test table-swap behavior and fallback.

## Agent Notes

Use one real smoke test per provider if needed, then keep the ongoing suite offline or mocked to avoid token spend.

---
## SOURCE FILE: docs/roadmap/tasks/AW-108-prompt-caching-and-generation-logging.md

# AW-108: Prompt caching and generation logging

**Milestone / Epic:** M1 / D  
**Size:** M  
**Implements:** Arch S2.7, PRD Principle 6  
**Depends on:** AW-107

## Build

Wire prompt caching for stable per-session context layers and log every generation call to `generation_logs` with token counts and cost so per-session margin is computable.

## Acceptance Criteria

- [ ] Stable context layers are marked cacheable
- [ ] Every model call writes a `generation_logs` row
- [ ] `CONTENT_LOGGING_ENABLED` controls full prompt and response population

## Do NOT

- Default runtime narrative generation to the most capable model; budget-first remains the default

## Testing

Assert cacheable layers are flagged and that a `generation_logs` row is written per call.

## Agent Notes

Document the cache invalidation rule when session state changes.

---
## SOURCE FILE: docs/roadmap/tasks/AW-110-simulation-harness-skeleton.md

# AW-110: Headless session runner core

**Milestone / Epic:** M1 / E  
**Size:** M  
**Implements:** Arch S3.1, S3.6, S5.2-S5.4, S15.9 #11 (split)  
**Depends on:** AW-105, AW-108

## Build

Create the harness runner core that loads the Nightcap arc, instantiates session state, applies a seeded action stream, and advances the `ArcStateChart` without UI.

## Acceptance Criteria

- [ ] Can start a session and advance it programmatically without UI
- [ ] Session seed is stored in runner state and exposed in the run trace
- [ ] Beat transitions and harness snapshots are recorded for deterministic assertions
- [ ] AI call boundaries remain mockable and optional in the runner core

## Do NOT

- Build scripted synthetic player scenarios yet; that belongs to AW-111
- Build batch statistics or replay UI yet; that belongs to AW-112

## Testing

- Runner initialization and beat-stepping unit tests
- Repeated direct-action run with the same seed and inputs

## Agent Notes

Use current implemented names from Epics C and D: `build_character_generation_context`, `CharacterGenerationContext`, and `engine.routing.logging.generate` if any generation boundary is exercised.

The `ArcStateChart` uses python-statemachine v3 `StateChart`. `chart.current_state` is deprecated -- use `chart.configuration_values` (a set of lowercase state ID strings). All trace and snapshot fields use `sorted(chart.configuration_values)` so that parallel-state configurations are captured completely and sorted for deterministic equality checks.

Full happy-path transition sequence with resulting sorted configurations: see spec `docs/specs/0015-aw-110-headless-session-runner-core.md` Context section. The `investigation` parallel state produces a 6-entry configuration -- a single string cannot represent it.

`Session` is ambiguous in this codebase. The runner state uses `session_id: UUID` directly on `HarnessRun` -- do not use the ORM `Session` from `engine.db.orm` in runner state. If generation is exercised in tests, use the SQLite in-memory patching pattern from `engine/tests/test_generation_logging.py`.

---
## SOURCE FILE: docs/roadmap/tasks/AW-111-scripted-synthetic-player-driver.md

# AW-111: Scripted synthetic player driver

**Milestone / Epic:** M1 / E  
**Size:** M  
**Implements:** Arch S2.9, S3.6, S12.2 Phase 7, S15.9 #11 (split)  
**Depends on:** AW-110

## Build

Create a declarative scenario format and synthetic player driver that converts scripted player actions into harness-runner actions with deterministic participant identities and ordering.

## Acceptance Criteria

- [ ] Synthetic player input is scriptable through a small declarative scenario schema
- [ ] A scripted scenario can drive the Nightcap scaffold from session start through reveal without UI
- [ ] Invalid or out-of-order scripted actions fail with a clear harness error
- [ ] Scenarios stay offline and do not require real provider calls

## Do NOT

- Build replay diffing or batch execution yet; that belongs to AW-112
- Depend on SSE, FastAPI routes, or browser clients

## Testing

- Scenario execution tests for the happy path
- Invalid action ordering tests

## Agent Notes

Keep the scenario DSL engine-local and small. It should target the current scaffolded runtime, not a future network API.

---
## SOURCE FILE: docs/roadmap/tasks/AW-112-deterministic-replay-and-batch-runner.md

# AW-112: Deterministic replay and batch runner

**Milestone / Epic:** M1 / E  
**Size:** S  
**Implements:** Arch S2.9, S12.2 Phase 7, S15.9 #11 (split)  
**Depends on:** AW-110, AW-111

## Build

Add deterministic trace comparison and a headless batch runner that can execute the same scripted scenario repeatedly from seeds without UI or token spend.

## Acceptance Criteria

- [ ] Running the same scenario twice with the same seed produces an identical harness trace
- [ ] Batch runner can execute 10 headless sessions from scripted scenarios
- [ ] Batch output includes per-run seed and pass/fail summary for determinism checks
- [ ] Batch execution remains offline and mock-friendly

## Do NOT

- Build a replay UI, metrics dashboard, or analytics pipeline
- Introduce real provider calls into the batch path

## Testing

- Seeded determinism test
- 10-run batch smoke test

## Agent Notes

Mock at the `engine.routing.logging.generate` boundary if any generation path is exercised. Do not reintroduce provider or model string literals into harness tests.

---
## SOURCE FILE: docs/roadmap/tasks/AW-201-m2-m6-roadmap-and-tracker-bootstrap.md

# AW-201: M2-M6 Roadmap and Tracker Bootstrap

**Milestone / Epic:** M2 / Roadmap bootstrap  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Create the canonical roadmap docs, AW-201 spec, tracker config, GitHub milestones, and GitHub issues for M2 through M6.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/specs/0006-roadmap-organization.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Create the canonical roadmap docs, AW-201 spec, tracker config, GitHub milestones, and GitHub issues for M2 through M6. Likely files affected: docs/roadmap/**, docs/specs/0020-aw-201-m2-m6-roadmap-and-tracker-bootstrap.md, .github/tracker/*.json.

## Acceptance Criteria

- [ ] Roadmap docs exist for every planned M2-M6 epic and AW-201 through AW-244 task.
- [ ] `docs/specs/0020-aw-201-m2-m6-roadmap-and-tracker-bootstrap.md` exists.
- [ ] `docs/roadmap/index.json` validates and includes all new docs and live GitHub issue references.
- [ ] GitHub labels, milestones, epics, and task issues are created without modifying closed M1 issues.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- M1 complete

## Likely Files Affected

docs/roadmap/**, docs/specs/0020-aw-201-m2-m6-roadmap-and-tracker-bootstrap.md, .github/tracker/*.json

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/specs/0006-roadmap-organization.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-202-external-nightcap-platform-decision.md

# AW-202: Nightcap Web Experience Runtime Decision

**Milestone / Epic:** M2 / M2-A  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Select the Nightcap web experience runtime and document the integration contract.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/02-Decisions-Log-Additions-May2026.md Entry 3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Select the browser-based Nightcap web experience runtime and document the integration contract. This task is not a decision to use a third-party app builder, and it does not move Arcwright core infrastructure or canonical state ownership out of Arcwright. Likely files affected: docs/specs, docs/decisions, docs/roadmap/tasks/AW-225-through-AW-231.

## Acceptance Criteria

- [ ] A decision record names the selected Nightcap web experience runtime or explicitly blocks M4 if no runtime is acceptable.
- [ ] The integration contract lists API, SDK, auth, event, deployment, privacy, state ownership, and performance assumptions.
- [ ] M4 tasks are updated or unblocked according to the decision.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-201

## Likely Files Affected

docs/specs, docs/decisions, docs/roadmap/tasks/AW-225-through-AW-231

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/02-Decisions-Log-Additions-May2026.md Entry 3
- `docs/specs/0022-aw-202-nightcap-web-experience-runtime-decision.md`
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-203-arcdefinition-schema-and-validation-core.md

# AW-203: ArcDefinition Schema And Validation Core

**Milestone / Epic:** M2 / M2-B  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Implement the full Pydantic arc definition schema and validation behavior.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/09-developer-api.md S9.3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Implement the full Pydantic arc definition schema and validation behavior. Likely files affected: engine/arc/models.py, engine/tests, docs/specs.

## Acceptance Criteria

- [ ] ArcDefinition and nested models cover the fields documented in `docs/architecture/15-development-guide.md` S15.4.
- [ ] Validation rejects missing required fields, invalid beat graph references, invalid player counts, invalid pacing weight sums, and invalid narrator triggers.
- [ ] Tests include at least one valid arc fixture and at least five invalid arc fixtures tied to documented validation rules.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-201

## Likely Files Affected

engine/arc/models.py, engine/tests, docs/specs

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/09-developer-api.md S9.3
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-204-dynamic-arcstatechart-generation.md

# AW-204: Dynamic ArcStateChart Generation

**Milestone / Epic:** M2 / M2-B  
**Size:** L  
**Status:** Planned

## Plain-English Summary

Generate a python-statemachine StateChart from an arc definition beat graph.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/03-arc-execution.md S3.1-S3.2` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Generate a python-statemachine StateChart from an arc definition beat graph. Likely files affected: engine/arc, engine/tests.

## Acceptance Criteria

- [ ] StateChart generation supports linear, branching, convergence, and loop beat graph patterns from ArcDefinition data.
- [ ] Generated transition guards enforce authored entry and exit constraints before a beat transition is accepted.
- [ ] Tests prove the engine does not rely on custom graph traversal or LLM output for canonical state transitions.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-203

## Likely Files Affected

engine/arc, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/03-arc-execution.md S3.1-S3.2
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-205-nightcap-canonical-arc-json.md

# AW-205: Nightcap Canonical Arc JSON

**Milestone / Epic:** M2 / M2-C  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Create the canonical Nightcap arc definition at `nightcap/arc.json`.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/09-developer-api.md S9.3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Create the canonical Nightcap arc definition at `nightcap/arc.json`. Likely files affected: nightcap/arc.json, engine/tests.

## Acceptance Criteria

- [ ] `nightcap/arc.json` exists and validates against the ArcDefinition schema.
- [ ] The arc defines introduction, investigation, and reveal beats with Nightcap content rails and knowledge rules.
- [ ] The arc supports 4 to 10 players while explicitly preserving the M6 first-proof focus on 4 to 6 players.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-203

## Likely Files Affected

nightcap/arc.json, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/09-developer-api.md S9.3
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-206-killer-assignment-and-reveal-state.md

# AW-206: Killer Assignment And Reveal State

**Milestone / Epic:** M2 / M2-C  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Resolve killer assignment at session start and preserve reveal constraints.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/03-arc-execution.md S3.4-S3.7` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Resolve killer assignment at session start and preserve reveal constraints. Likely files affected: engine/arc, engine/session, engine/tests.

## Acceptance Criteria

- [ ] Killer assignment occurs during the introduction setup path and stores the assigned killer in session state.
- [ ] A seeded run produces the same killer assignment and reveal state when replayed with the same seed.
- [ ] Reveal cannot fire until authored reveal conditions are satisfied or a host-privileged bypass is logged.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-204
- AW-205

## Likely Files Affected

engine/arc, engine/session, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/03-arc-execution.md S3.4-S3.7
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-207-dramatic-tension-pacing-engine.md

# AW-207: Dramatic Tension Pacing Engine

**Milestone / Epic:** M2 / M2-B  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Compute dramatic tension and trigger pacing interventions from session signals.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/03-arc-execution.md S3.3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Compute dramatic tension and trigger pacing interventions from session signals. Likely files affected: engine/arc, engine/telemetry, engine/tests.

## Acceptance Criteria

- [ ] Dramatic tension score is computed from configured time, action, suspicion, and clue coverage weights.
- [ ] Stall and misdirection thresholds trigger the documented pacing intervention paths.
- [ ] Pacing intervention and tension update events log the payload fields required by `docs/architecture/11-telemetry.md`.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-204

## Likely Files Affected

engine/arc, engine/telemetry, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/03-arc-execution.md S3.3
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-208-l1-hard-stops.md

# AW-208: L1 Hard Stops

**Milestone / Epic:** M2 / M2-D  
**Size:** S  
**Status:** Planned

## Plain-English Summary

Add deterministic hard-stop checks before generation.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/10-content-safety.md S10.2` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Add deterministic hard-stop checks before generation. Likely files affected: engine/safety, engine/tests.

## Acceptance Criteria

- [ ] All L1 hard-stop categories from `docs/architecture/10-content-safety.md` S10.2 are blocked before any model call.
- [ ] A blocked L1 event is logged as `safety_hard_stop` without exposing trigger details to the player.
- [ ] Tests prove L1 cannot be disabled by arc configuration.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-201

## Likely Files Affected

engine/safety, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/architecture/10-content-safety.md S10.2
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-209-l2-pre-generation-classification.md

# AW-209: L2 Pre-Generation Classification

**Milestone / Epic:** M2 / M2-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Run safety classification before every main generation call.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/10-content-safety.md S10.3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Run safety classification before every main generation call. Likely files affected: engine/safety, engine/routing, engine/tests.

## Acceptance Criteria

- [ ] L2 safety classification runs before every main generation call path.
- [ ] Classification calls route through the model routing abstraction and never call a provider directly.
- [ ] Blocked classifications prevent the main generation call and log classification confidence data.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-208

## Likely Files Affected

engine/safety, engine/routing, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/architecture/10-content-safety.md S10.3
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-210-l3-policy-injection-and-neutral-bridge.md

# AW-210: L3 Policy Injection And Neutral Bridge

**Milestone / Epic:** M2 / M2-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Inject content rails into prompts and provide neutral bridge on blocked generation.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/10-content-safety.md S10.4` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Inject content rails into prompts and provide neutral bridge on blocked generation. Likely files affected: engine/safety, engine/characters, engine/events, engine/tests.

## Acceptance Criteria

- [ ] Every main generation prompt includes an L3 policy block derived from arc content rails.
- [ ] Blocked generation emits a neutral bridge event so the session can continue.
- [ ] Tests prove Nightcap-specific L3 policy is sourced from arc rails rather than hardcoded platform policy.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-209

## Likely Files Affected

engine/safety, engine/characters, engine/events, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/architecture/10-content-safety.md S10.4
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-211-behavior-profile-assembly.md

# AW-211: Behavior Profile Assembly

**Milestone / Epic:** M2 / M2-E  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Build runtime character context from behavior profile and live relationships.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/07-character-behavior.md S7.2` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build runtime character context from behavior profile and live relationships. Likely files affected: engine/characters, engine/tests.

## Acceptance Criteria

- [ ] Runtime character context includes personality, goals, secrets, tells, and relationship dispositions.
- [ ] Human-controlled and AI-driven characters use the same platform character object model.
- [ ] Tests cover context assembly for killer and non-killer characters.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-205
- AW-206

## Likely Files Affected

engine/characters, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/architecture/07-character-behavior.md S7.2
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-212-knowledge-constrained-dialogue-pipeline.md

# AW-212: Knowledge-Constrained Dialogue Pipeline

**Milestone / Epic:** M2 / M2-E  
**Size:** L  
**Status:** Planned

## Plain-English Summary

Generate character dialogue through knowledge query, safety, routing, and event emission.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/04-knowledge-graph.md S4.3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Generate character dialogue through knowledge query, safety, routing, and event emission. Likely files affected: engine/characters, engine/knowledge, engine/safety, engine/events, engine/tests.

## Acceptance Criteria

- [ ] `get_character_knowledge` is called before every AI character dialogue generation.
- [ ] Dialogue prompts include explicit known and not-known knowledge constraint blocks.
- [ ] Tests prove a mocked generation path cannot emit dialogue containing facts outside the character knowledge state.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-210
- AW-211

## Likely Files Affected

engine/characters, engine/knowledge, engine/safety, engine/events, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/architecture/04-knowledge-graph.md S4.3
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-213-ai-initiative-and-npc-npc-exchange.md

# AW-213: AI Initiative And NPC-NPC Exchange

**Milestone / Epic:** M2 / M2-E  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Add AI initiative scheduling and NPC-to-NPC interactions.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/07-character-behavior.md S7.5-S7.6` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Add AI initiative scheduling and NPC-to-NPC interactions. Likely files affected: engine/characters, engine/tests.

## Acceptance Criteria

- [ ] AI initiative can trigger an AI character action without player input.
- [ ] NPC-NPC exchanges include both characters knowledge state and relationship context.
- [ ] Scheduler tasks do not block the session coordinator loop.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-212

## Likely Files Affected

engine/characters, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/architecture/07-character-behavior.md S7.5-S7.6
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-214-m2-headless-nightcap-exit-harness.md

# AW-214: M2 Headless Nightcap Exit Harness

**Milestone / Epic:** M2 / M2-B  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Prove the full M2 exit gate offline.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Prove the full M2 exit gate offline. Likely files affected: engine/tests, docs/roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md.

## Acceptance Criteria

- [ ] Headless harness completes introduction, investigation, and reveal for the Nightcap arc.
- [ ] Harness trace shows killer assignment, reveal firing, safety pre-generation checks, and no knowledge leaks.
- [ ] Harness path uses mocked routing and spends no real provider tokens.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-206
- AW-207
- AW-212
- AW-213

## Likely Files Affected

engine/tests, docs/roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-215-contentevent-model-and-in-memory-bus.md

# AW-215: ContentEvent Model And In-Memory Bus

**Milestone / Epic:** M3 / M3-A  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Add ContentEvent schema, presentation hints, sequence numbers, and an in-memory event bus.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/08-event-system.md S8.2-S8.3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Add ContentEvent schema, presentation hints, sequence numbers, and an in-memory event bus. Likely files affected: engine/events, engine/tests.

## Acceptance Criteria

- [ ] ContentEvent and PresentationHints models include the fields documented in `docs/architecture/08-event-system.md`.
- [ ] Sequence numbers are monotonically increasing per session.
- [ ] An in-memory per-session event bus can publish and subscribe to ContentEvents in order.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-214

## Likely Files Affected

engine/events, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/08-event-system.md S8.2-S8.3
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-216-sse-fanout-filtering-and-replay.md

# AW-216: SSE Fanout Filtering And Replay

**Milestone / Epic:** M3 / M3-A  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Deliver events to connected clients based on target audience and replay missed events.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/08-event-system.md S8.4-S8.6` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Deliver events to connected clients based on target audience and replay missed events. Likely files affected: engine/events, api/routers, engine/tests.

## Acceptance Criteria

- [ ] Specific-player events are delivered only to the matching player connection.
- [ ] Host-only, shared-display, and all-player events route to the documented connection sets.
- [ ] Reconnect replay uses sequence numbers to deliver missed events without duplicating already-seen events.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-215

## Likely Files Affected

engine/events, api/routers, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.

## Architecture References

- docs/architecture/08-event-system.md S8.4-S8.6
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-217-session-lifecycle-api-and-auth.md

# AW-217: Session Lifecycle API And Auth

**Milestone / Epic:** M3 / M3-B  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Add thin API routes for session creation, start, pause, resume, and end.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/09-developer-api.md S9.2` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Add thin API routes for session creation, start, pause, resume, and end. Likely files affected: api/routers, api/auth, api/schemas, engine/session.

## Acceptance Criteria

- [ ] Session lifecycle endpoints create, start, pause, resume, and end sessions with documented request and response schemas.
- [ ] Route handlers validate input, call engine services, and return responses without arc execution logic.
- [ ] API key, host JWT, and unauthenticated join behavior match `docs/architecture/09-developer-api.md`.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-216

## Likely Files Affected

api/routers, api/auth, api/schemas, engine/session

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.

## Architecture References

- docs/architecture/09-developer-api.md S9.2
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-218-character-input-and-knowledge-endpoints.md

# AW-218: Character Input And Knowledge Endpoints

**Milestone / Epic:** M3 / M3-B  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Add player input and internal knowledge endpoint surfaces.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/09-developer-api.md S9.2` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Add player input and internal knowledge endpoint surfaces. Likely files affected: api/routers, api/schemas, engine/knowledge.

## Acceptance Criteria

- [ ] Player input endpoint accepts typed character action or dialogue input.
- [ ] Knowledge assert, revoke, and query endpoints are available only to host or internal engine callers as documented.
- [ ] Tests prove player clients cannot query another character private knowledge state.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-217

## Likely Files Affected

api/routers, api/schemas, engine/knowledge

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.

## Architecture References

- docs/architecture/09-developer-api.md S9.2
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-219-typescript-sdk-event-and-input-client.md

# AW-219: TypeScript SDK Event And Input Client

**Milestone / Epic:** M3 / M3-B  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Build the typed web SDK wrapper for event subscription and player input.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/09-developer-api.md S9.4` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build the typed web SDK wrapper for event subscription and player input. Likely files affected: sdk, api schemas if generation is needed.

## Acceptance Criteria

- [ ] ArcwrightClient exposes event subscription, input submission, current-character fetch, and disconnect behavior.
- [ ] Public SDK types are generated from or aligned with API schemas and avoid `any` in public interfaces.
- [ ] SDK typecheck and build pass without embedding arc execution logic.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-217
- AW-218

## Likely Files Affected

sdk, api schemas if generation is needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.
- Do not put arc execution logic in TypeScript.

## Architecture References

- docs/architecture/09-developer-api.md S9.4
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-220-session-persistence-snapshots-and-resume.md

# AW-220: Session Persistence Snapshots And Resume

**Milestone / Epic:** M3 / M3-C  
**Size:** L  
**Status:** Planned

## Plain-English Summary

Persist session state and resume from nearest beat.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/05-session-persistence.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Persist session state and resume from nearest beat. Likely files affected: engine/session, engine/arc, engine/knowledge, migrations, engine/tests.

## Acceptance Criteria

- [ ] Interruption writes an `arc_beat_states` snapshot at the nearest completed beat boundary.
- [ ] Resume restores statemachine configuration, knowledge state, relationship state, and session status.
- [ ] A resumed session never restarts from the beginning unless no valid prior state exists and that exception is documented.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-217
- AW-218

## Likely Files Affected

engine/session, engine/arc, engine/knowledge, migrations, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/05-session-persistence.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-221-narrator-bridge-on-resume.md

# AW-221: Narrator Bridge On Resume

**Milestone / Epic:** M3 / M3-C  
**Size:** S  
**Status:** Planned

## Plain-English Summary

Generate and emit a narrator recap when a session resumes.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/05-session-persistence.md S5.3-S5.4` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Generate and emit a narrator recap when a session resumes. Likely files affected: engine/session, engine/routing, engine/safety, engine/events.

## Acceptance Criteria

- [ ] Resume emits a narrator bridge ContentEvent before normal play continues.
- [ ] Narrator bridge generation uses the `narrator_bridge` routing task type.
- [ ] Bridge generation passes through L1, L2, and L3 safety handling.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-220

## Likely Files Affected

engine/session, engine/routing, engine/safety, engine/events

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/architecture/05-session-persistence.md S5.3-S5.4
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-222-five-mvp-telemetry-signals.md

# AW-222: Five MVP Telemetry Signals

**Milestone / Epic:** M3 / M3-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Wire all five minimum telemetry signals.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/11-telemetry.md S11.3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Wire all five minimum telemetry signals. Likely files affected: engine/telemetry, engine/events, engine/tests.

## Acceptance Criteria

- [ ] Beat transition, pacing intervention, knowledge constraint, session completion, and replay intent signals log with documented payload fields.
- [ ] A complete mocked session contains all five MVP telemetry signals.
- [ ] Required telemetry writes do not depend on `CONTENT_LOGGING_ENABLED=true`.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-220

## Likely Files Affected

engine/telemetry, engine/events, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/11-telemetry.md S11.3
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-223-cost-and-usage-summary.md

# AW-223: Cost And Usage Summary

**Milestone / Epic:** M3 / M3-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Expose cost and usage summaries from generation logs.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/13-cost-model.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Expose cost and usage summaries from generation logs. Likely files affected: engine/telemetry, engine/routing, api/routers.

## Acceptance Criteria

- [ ] Usage summary exposes per-session AI cost from `generation_logs`.
- [ ] Cost can be grouped by session, arc, task type, and player count.
- [ ] Output distinguishes actual logged costs from open pricing or revenue assumptions.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-222

## Likely Files Affected

engine/telemetry, engine/routing, api/routers

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.
- Do not put arc execution logic in FastAPI route handlers.

## Architecture References

- docs/architecture/13-cost-model.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-224-full-api-batch-harness.md

# AW-224: Full API Batch Harness

**Milestone / Epic:** M3 / M3-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Run repeated complete sessions through the API path.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/12-build-plan.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Run repeated complete sessions through the API path. Likely files affected: engine/tests, api tests, scripts if needed.

## Acceptance Criteria

- [ ] Batch harness runs 10 complete sessions through API-level flows.
- [ ] Each batch run records seed, pass/fail status, and telemetry signal presence.
- [ ] Batch harness uses mocked generation and spends no real provider tokens.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-219
- AW-223

## Likely Files Affected

engine/tests, api tests, scripts if needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.

## Architecture References

- docs/architecture/12-build-plan.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-225-external-platform-connector-scaffold.md

# AW-225: Nightcap Web Experience Runtime Connector Scaffold

**Milestone / Epic:** M4 / M4-A  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Implement the Nightcap web experience runtime connector scaffold after AW-202.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/02-Decisions-Log-Additions-May2026.md Entry 3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Implement the Cloudflare-hosted Nightcap web experience runtime connector scaffold according to the AW-202 contract. Likely files affected: Cloudflare Pages, Workers, Durable Objects or PartyKit files, SDK usage, api docs.

## Acceptance Criteria

- [ ] Connector can create or attach to a Nightcap session using the AW-202 runtime contract.
- [ ] Connector subscribes to Arcwright events without requiring engine surface assumptions.
- [ ] Connector keeps Arcwright authoritative for session state, event audience targeting, safety, and telemetry.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-202
- AW-224

## Likely Files Affected

Cloudflare Pages, Workers, Durable Objects or PartyKit files, SDK usage, api docs

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not bypass the AW-202 Nightcap web experience runtime contract.
- Do not put arc execution logic in FastAPI route handlers.
- Do not put arc execution logic in TypeScript.

## Architecture References

- docs/02-Decisions-Log-Additions-May2026.md Entry 3
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-226-host-session-creation-and-shared-display-flow.md

# AW-226: Host Session Creation And Shared Display Flow

**Milestone / Epic:** M4 / M4-B  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Build host controls and shared display flow on the Nightcap web experience runtime.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/02-requirements.md Host experience` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build host controls and shared display flow on the Cloudflare-hosted Nightcap web experience runtime selected by AW-202. Likely files affected: Cloudflare Pages, Workers, Durable Objects or PartyKit files, SDK usage if needed.

## Acceptance Criteria

- [ ] Host can create, start, pause, resume, and end a session through the Nightcap web experience runtime.
- [ ] Shared display shows only public or shared-display ContentEvents.
- [ ] Host controls use API lifecycle endpoints rather than bypassing the platform API.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-225

## Likely Files Affected

Cloudflare Pages, Workers, Durable Objects or PartyKit files, SDK usage if needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not bypass the AW-202 Nightcap web experience runtime contract.
- Do not put arc execution logic in TypeScript.

## Architecture References

- docs/prd/02-requirements.md Host experience
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-227-shared-display-narrator-and-group-event-rendering.md

# AW-227: Shared Display Narrator And Group Event Rendering

**Milestone / Epic:** M4 / M4-B  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Render narrator and group-visible events from ContentEvents.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/08-event-system.md S8.5` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Render narrator and group-visible events from ContentEvents in the Cloudflare-hosted Nightcap web experience runtime selected by AW-202. Likely files affected: Cloudflare Pages, Workers, Durable Objects or PartyKit files.

## Acceptance Criteria

- [ ] Narration events render from ContentEvent payloads on the shared display.
- [ ] Group-visible events render without private clue content.
- [ ] Presentation hints are consumed as surface hints and do not alter engine state.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-226

## Likely Files Affected

Cloudflare Pages, Workers, Durable Objects or PartyKit files

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not bypass the AW-202 Nightcap web experience runtime contract.

## Architecture References

- docs/architecture/08-event-system.md S8.5
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-228-player-join-flow-under-30-seconds.md

# AW-228: Player Join Flow Under 30 Seconds

**Milestone / Epic:** M4 / M4-C  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Build QR or code join flow for player devices.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/02-requirements.md Player experience` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build QR or code join flow for player devices in the Cloudflare-hosted Nightcap web experience runtime selected by AW-202. Likely files affected: Cloudflare Pages, Workers, Durable Objects or PartyKit files, api join flow if needed.

## Acceptance Criteria

- [ ] A new player can join by QR or code in under 30 seconds in rehearsal conditions.
- [ ] Player join does not require a Firebase account or app install.
- [ ] Player receives only their assigned character context after join.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-225

## Likely Files Affected

Cloudflare Pages, Workers, Durable Objects or PartyKit files, api join flow if needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not bypass the AW-202 Nightcap web experience runtime contract.
- Do not put arc execution logic in FastAPI route handlers.

## Architecture References

- docs/prd/02-requirements.md Player experience
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-229-player-private-event-and-input-flow.md

# AW-229: Player Private Event And Input Flow

**Milestone / Epic:** M4 / M4-C  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Render private player events and submit player input.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/08-event-system.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Render private player events and submit player input in the Cloudflare-hosted Nightcap web experience runtime selected by AW-202. Likely files affected: Cloudflare Pages, Workers, Durable Objects or PartyKit files, SDK usage if needed.

## Acceptance Criteria

- [ ] Specific-player events render only on the intended player device.
- [ ] Player can submit action or dialogue through the SDK or API path.
- [ ] Private event handling survives reconnect without leaking payloads to other devices.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-228

## Likely Files Affected

Cloudflare Pages, Workers, Durable Objects or PartyKit files, SDK usage if needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not bypass the AW-202 Nightcap web experience runtime contract.
- Do not put arc execution logic in TypeScript.

## Architecture References

- docs/architecture/08-event-system.md
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-230-real-device-privacy-matrix.md

# AW-230: Real-Device Privacy Matrix

**Milestone / Epic:** M4 / M4-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Verify all event audiences across real devices.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/08-event-system.md S8.4-S8.5` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Verify all event audiences across real devices in the Cloudflare-hosted Nightcap web experience runtime selected by AW-202. Likely files affected: test docs, Cloudflare Pages, Workers, Durable Objects or PartyKit files.

## Acceptance Criteria

- [ ] Device matrix verifies `all`, `specific_player`, `host_only`, and `shared_display` routing.
- [ ] Player A never receives Player B private event in the test matrix.
- [ ] Shared display never receives private clue text.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-227
- AW-229

## Likely Files Affected

test docs, Cloudflare Pages, Workers, Durable Objects or PartyKit files

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not bypass the AW-202 Nightcap web experience runtime contract.

## Architecture References

- docs/architecture/08-event-system.md S8.4-S8.5
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-231-m4-real-human-rehearsal.md

# AW-231: M4 Real-Human Rehearsal

**Milestone / Epic:** M4 / M4-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Run a non-qualifying real-device rehearsal and log blockers.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/roadmap/milestones/M4-nightcap-experience-layer.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Run a non-qualifying real-device rehearsal on the Nightcap web experience runtime selected by AW-202 and log blockers. Likely files affected: docs/playtest notes or GitHub issue comments, docs/roadmap if needed.

## Acceptance Criteria

- [ ] A non-qualifying real-human rehearsal is attempted on real devices.
- [ ] Join timing, privacy result, completion state, and blockers are recorded.
- [ ] Every blocker is triaged into a follow-up issue before M5 begins.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-230

## Likely Files Affected

docs/playtest notes or GitHub issue comments, docs/roadmap if needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not bypass the AW-202 Nightcap web experience runtime contract.

## Architecture References

- docs/roadmap/milestones/M4-nightcap-experience-layer.md
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-232-adversarial-safety-playtest-protocol.md

# AW-232: Adversarial Safety Playtest Protocol

**Milestone / Epic:** M5 / M5-A  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Create and run the adversarial safety playtest protocol.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/03-scope.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Create and run the adversarial safety playtest protocol. Likely files affected: docs/roadmap/tasks, GitHub issues/comments, docs/specs if needed.

## Acceptance Criteria

- [ ] Protocol covers dark-content edge cases, tone breaks, embarrassment attempts, prompt injection, and real-world harm probes.
- [ ] At least one adversarial safety run is completed before qualifying sessions.
- [ ] Findings are documented with severity, reproduction notes, and blocking status.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-231

## Likely Files Affected

docs/roadmap/tasks, GitHub issues/comments, docs/specs if needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/prd/03-scope.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-233-safety-findings-remediation.md

# AW-233: Safety Findings Remediation

**Milestone / Epic:** M5 / M5-A  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Resolve or explicitly defer adversarial safety findings.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/conventions/review-checklist.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Resolve or explicitly defer adversarial safety findings. Likely files affected: GitHub issues, docs/roadmap, engine/safety if fixes are created in later tasks.

## Acceptance Criteria

- [ ] Every blocking adversarial finding has a linked fix or explicit human-approved deferral.
- [ ] Resolved findings have retest evidence.
- [ ] No high-severity unresolved safety blocker remains before M6 begins.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-232

## Likely Files Affected

GitHub issues, docs/roadmap, engine/safety if fixes are created in later tasks

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/conventions/review-checklist.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-234-gross-margin-by-player-count.md

# AW-234: Gross Margin By Player Count

**Milestone / Epic:** M5 / M5-B  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Produce gross-margin readiness report for 4 through 10 players.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/13-cost-model.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Produce gross-margin readiness report for 4 through 10 players. Likely files affected: docs/roadmap/tasks, engine/telemetry or dashboard if implementation needed.

## Acceptance Criteria

- [ ] Cost report covers 4, 5, 6, 7, 8, 9, and 10 player sessions.
- [ ] Report separates actual logged model and infrastructure cost from open pricing assumptions.
- [ ] Gross-margin calculation assumptions are sourced or explicitly marked as open decisions.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-223
- AW-231

## Likely Files Affected

docs/roadmap/tasks, engine/telemetry or dashboard if implementation needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not build Visual Storyworld editing in Phase 1.

## Architecture References

- docs/architecture/13-cost-model.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-235-second-arc-schema-design.md

# AW-235: Second Arc Schema Design

**Milestone / Epic:** M5 / M5-C  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Design one non-Nightcap arc schema to validate platform-clean architecture.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/14-architecture-validation.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Design one non-Nightcap arc schema to validate platform-clean architecture. Likely files affected: docs/specs, sample arc docs, docs/roadmap/tasks.

## Acceptance Criteria

- [ ] A non-Nightcap arc schema exists as a document or sample arc.
- [ ] Schema validates against ArcDefinition or documents exact validation gaps.
- [ ] No second game implementation is added.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-203

## Likely Files Affected

docs/specs, sample arc docs, docs/roadmap/tasks

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/14-architecture-validation.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-236-live-knowledge-graph-inspection.md

# AW-236: Live Knowledge Graph Inspection

**Milestone / Epic:** M5 / M5-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Build read-only live knowledge graph inspection.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/03-scope.md Visual Storyworld Roadmap` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build read-only live knowledge graph inspection. Likely files affected: dashboard, api, engine/knowledge.

## Acceptance Criteria

- [ ] Read-only live knowledge graph inspection surface exists.
- [ ] Surface shows current knowledge state enough to diagnose clue and leak issues.
- [ ] Private information handling follows dashboard privacy rules.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-222

## Likely Files Affected

dashboard, api, engine/knowledge

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.
- Do not build Visual Storyworld editing in Phase 1.

## Architecture References

- docs/prd/03-scope.md Visual Storyworld Roadmap
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-237-read-only-arc-structure-inspection.md

# AW-237: Read-Only Arc Structure Inspection

**Milestone / Epic:** M5 / M5-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Build read-only arc structure inspection.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/03-scope.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build read-only arc structure inspection. Likely files affected: dashboard, api, engine/arc.

## Acceptance Criteria

- [ ] Read-only arc structure view exists.
- [ ] View shows beat graph and current beat for an attached session.
- [ ] Surface cannot edit arc structure.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-222
- AW-236

## Likely Files Affected

dashboard, api, engine/arc

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.
- Do not build Visual Storyworld editing in Phase 1.

## Architecture References

- docs/prd/03-scope.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-238-live-event-stream-inspection.md

# AW-238: Live Event Stream Inspection

**Milestone / Epic:** M5 / M5-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Build live event stream inspection.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/08-event-system.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build live event stream inspection. Likely files affected: dashboard, api, engine/events.

## Acceptance Criteria

- [ ] Live event stream inspection surface exists.
- [ ] View shows sequence number, event type, target audience, and timestamp.
- [ ] Private payload handling prevents broad exposure of private clue text.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-222
- AW-236

## Likely Files Affected

dashboard, api, engine/events

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not put arc execution logic in FastAPI route handlers.
- Do not build Visual Storyworld editing in Phase 1.

## Architecture References

- docs/architecture/08-event-system.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-239-character-state-inspection.md

# AW-239: Character State Inspection

**Milestone / Epic:** M5 / M5-D  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Build read-only character state inspection.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/07-character-behavior.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build read-only character state inspection. Likely files affected: dashboard, api, engine/characters.

## Acceptance Criteria

- [ ] Read-only character state inspection surface exists.
- [ ] View shows allowed character profile and live relationship state.
- [ ] Surface does not expose another player private knowledge state.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-236
- AW-237
- AW-238

## Likely Files Affected

dashboard, api, engine/characters

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.
- Do not put arc execution logic in FastAPI route handlers.
- Do not build Visual Storyworld editing in Phase 1.

## Architecture References

- docs/architecture/07-character-behavior.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-240-closed-playtest-operations-runbook.md

# AW-240: Closed Playtest Operations Runbook

**Milestone / Epic:** M6 / M6-A  
**Size:** S  
**Status:** Planned

## Plain-English Summary

Create the operational runbook for qualifying playtests.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/02-requirements.md Success criteria` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Create the operational runbook for qualifying playtests. Likely files affected: docs/roadmap/tasks, docs/playtest if created.

## Acceptance Criteria

- [ ] Runbook defines outside-group eligibility, consent steps, setup, host script, observer notes, and failure handling.
- [ ] Runbook explicitly excludes founder immediate-circle sessions from qualifying status.
- [ ] Runbook is reviewed before AW-242 final rehearsal.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-233
- AW-234
- AW-239

## Likely Files Affected

docs/roadmap/tasks, docs/playtest if created

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/prd/02-requirements.md Success criteria
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-241-qualifying-session-instrumentation-checklist.md

# AW-241: Qualifying Session Instrumentation Checklist

**Milestone / Epic:** M6 / M6-A  
**Size:** S  
**Status:** Planned

## Plain-English Summary

Define the exact evidence checklist for qualifying sessions.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/02-requirements.md Qualitative gate` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Define the exact evidence checklist for qualifying sessions. Likely files affected: docs/roadmap/tasks, docs/playtest if created.

## Acceptance Criteria

- [ ] Checklist maps completion, replay enthusiasm, personalization perception, telemetry, cost, and blockers to concrete evidence.
- [ ] Replay enthusiasm and personalization perception definitions match `docs/prd/02-requirements.md`.
- [ ] Checklist marks sessions missing telemetry evidence as non-qualifying until reviewed.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-240

## Likely Files Affected

docs/roadmap/tasks, docs/playtest if created

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/prd/02-requirements.md Qualitative gate
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-242-founder-run-final-rehearsal.md

# AW-242: Founder-Run Final Rehearsal

**Milestone / Epic:** M6 / M6-A  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Run the final non-qualifying rehearsal before outside groups.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/roadmap/milestones/M6-first-qualifying-sessions.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Run the final non-qualifying rehearsal before outside groups. Likely files affected: GitHub issue comments, docs/playtest notes if created.

## Acceptance Criteria

- [ ] Final rehearsal completes or records blockers with owner and severity.
- [ ] Telemetry and all four inspection surfaces are verified during rehearsal.
- [ ] No blocker remains untriaged before AW-243 starts.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-241

## Likely Files Affected

GitHub issue comments, docs/playtest notes if created

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/roadmap/milestones/M6-first-qualifying-sessions.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-243-five-outside-qualifying-sessions.md

# AW-243: Five Outside Qualifying Sessions

**Milestone / Epic:** M6 / M6-B  
**Size:** L  
**Status:** Planned

## Plain-English Summary

Run five or more qualifying Nightcap sessions with outside groups at 4 to 6 players.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/02-requirements.md Success criteria` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Run five or more qualifying Nightcap sessions with outside groups at 4 to 6 players. Likely files affected: GitHub issue comments, docs/playtest notes if created.

## Acceptance Criteria

- [ ] Five or more outside-group sessions are attempted and documented.
- [ ] Each session records completion status, replay intent, personalization perception evidence, player count, and telemetry status.
- [ ] All qualifying sessions use 4 to 6 players.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-242

## Likely Files Affected

GitHub issue comments, docs/playtest notes if created

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/prd/02-requirements.md Success criteria
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/roadmap/tasks/AW-244-h1-proof-analysis-and-next-step-decision.md

# AW-244: H1 Proof Analysis And Next-Step Decision

**Milestone / Epic:** M6 / M6-C  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Analyze qualifying session evidence and record the H1 decision.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/02-requirements.md Personalization perception gate` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Analyze qualifying session evidence and record the H1 decision. Likely files affected: docs/decisions if needed, docs/roadmap, playtest report docs.

## Acceptance Criteria

- [ ] Report states whether the qualitative replay enthusiasm gate passed.
- [ ] Report states whether the personalization perception gate passed with session evidence.
- [ ] Next-step decision is recorded before scope expands beyond first proof.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-243

## Likely Files Affected

docs/decisions if needed, docs/roadmap, playtest report docs

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/prd/02-requirements.md Personalization perception gate
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.

---
## SOURCE FILE: docs/specs/0000-template.md

# Title

**Status**: Draft | Approved | In Progress | Done

**Author**: [Name] | **Date**: [YYYY-MM-DD]

---

# References

- Related ADRs: [Link]
- Architecture sections: [Link]
- Related specs: [Link]
- PRD sections: [Link]

---

# Overview

One or two sentences: what is this spec defining?

---

# In Scope

What does this spec cover?
- Feature/component A
- Feature/component B
- API endpoints or interfaces
- Database changes

---

# Out of Scope

What is explicitly NOT covered?
- Features deferred to later phases
- Related work that belongs in other specs
- Performance optimizations or refactorings not required for MVP

---

# Acceptance Criteria

How will we know this is done? Each criterion should be verifiable:

- [ ] API endpoints accept and return the schema defined in Section X
- [ ] Acceptance test in test_Y.py passes with coverage > 80%
- [ ] Database migration applies cleanly to empty and populated schemas
- [ ] Performance benchmarks: operation Z completes in < 100ms
- [ ] Code review sign-off from [responsible person]

---

# Test Plan

How will we verify this works?

- Unit tests: [what will be tested]
- Integration tests: [cross-component scenarios]
- Manual testing: [if any]
- Performance tests: [if critical path]

---

# Risks and Unknowns

What could go wrong? What do we not yet know?

**Risks**:
- Risk 1: Consequence if it happens
- Risk 2: Consequence if it happens

**Unknowns**:
- Unknown 1: Why it matters
- Unknown 2: Why it matters

---

# Open Questions

What needs clarification before implementation starts?

- Q1: [question]
- Q2: [question]

---
## SOURCE FILE: docs/specs/0001-review-checklist-convention.md

# Reviewer Checklist Convention

**Status**: Done

**Author**: Codex | **Date**: 2026-05-21

---

# References

- Architecture sections: `docs/architecture/15-development-guide.md`
- PRD sections: `docs/prd/01-overview.md`
- Related specs: `docs/specs/0000-template.md`
- Convention files: `docs/conventions/ai-contributions.md`

---

# Overview

Define a maintainer-facing checklist for reviewing agent-authored PRs so review quality is consistent and aligned with repo policy.

---

# In Scope

- Add `docs/conventions/review-checklist.md`
- Cover pre-diff, in-diff, and pre-merge review checks
- Include review checks for spec alignment, testing, LLM-dependent changes, docs, and ADR follow-through

---

# Out of Scope

- Changes to implementation code or tests
- Changes to CI configuration
- Broader edits to existing convention documents

---

# Acceptance Criteria

- [x] `docs/conventions/review-checklist.md` exists
- [x] The file includes the required top note verbatim
- [x] The file includes all requested checks under the three review phases
- [x] The file is under 60 lines

---

# Test Plan

- Manual review against the request
- Manual line-count check for `docs/conventions/review-checklist.md`

---

# Risks and Unknowns

**Risks**:
- The checklist could drift from repo policy if conventions change later

**Unknowns**:
- Whether the maintainer will want this checklist linked from other convention docs in a follow-up change

---

# Open Questions

- None for this scoped documentation addition

---
## SOURCE FILE: docs/specs/0002-pre-commit-hook-setup.md

# Pre-Commit Hook Setup

**Status**: Done

**Author**: Codex | **Date**: 2026-05-21

---

# References

- Architecture sections: `docs/architecture/15-development-guide.md`
- PRD sections: `docs/prd/01-overview.md`
- Related specs: `docs/specs/0000-template.md`
- Convention files: `docs/conventions/ai-contributions.md`

---

# Overview

Add a repo-wide pre-commit hook setup that fits Arcwright's mixed Python and TypeScript toolchain and blocks common quality and security mistakes before commit.

---

# In Scope

- Add a root `.pre-commit-config.yaml`
- Add non-destructive formatter and linter checks for Python and JS/TS
- Add a gitleaks secrets scan
- Add a check that rejects temporary debug markers
- Document local hook installation in conventions and README

---

# Out of Scope

- CI workflow changes
- Auto-fixing hooks that rewrite files during commit
- Broad refactors to existing source files

---

# Acceptance Criteria

- [x] `pre-commit` is configured at the repo root
- [x] Python files are checked with Ruff lint and Ruff format in check-only mode
- [x] JS/TS files are checked with Prettier and ESLint in check-only mode
- [x] Commits fail if gitleaks detects secrets
- [x] Commits fail if staged files contain the configured temporary-marker strings
- [x] `docs/conventions/setup.md` explains local installation and usage
- [x] `README.md` Getting Started includes the hook install command

---

# Test Plan

- Validate `.pre-commit-config.yaml` structure
- Run targeted config checks where local tooling is available
- Manually verify docs against the configured commands

---

# Risks and Unknowns

**Risks**:
- New hook tooling may surface a large number of existing style issues when first run
- Repo-local JS/TS lint configuration may need refinement as the SDK and dashboard grow

**Unknowns**:
- Whether the maintainer wants hook execution mirrored in CI in a follow-up change

---

# Open Questions

- None after approval to add the needed dev-only tooling for JS/TS checks

---
## SOURCE FILE: docs/specs/0003-ci-and-codeql-workflows.md

# CI and CodeQL Workflows

**Status**: Done

**Author**: Codex | **Date**: 2026-05-21

---

# References

- Architecture sections: `docs/architecture/15-development-guide.md`
- PRD sections: `docs/prd/01-overview.md`
- Related specs: `docs/specs/0000-template.md`
- Convention files: `docs/conventions/ai-contributions.md`

---

# Overview

Add GitHub Actions workflows for CI and CodeQL so Arcwright runs consistent automated checks on pushes to `main` and on pull requests.

---

# In Scope

- Add `.github/workflows/ci.yml`
- Add `.github/workflows/codeql.yml`
- Configure dependency caching and concurrency cancellation
- Run lint, type check, tests, build, and gitleaks checks that match the current repo toolchain

---

# Out of Scope

- New application code
- New package manager lockfiles
- Expanded CI coverage beyond the currently configured Python and TypeScript tooling

---

# Acceptance Criteria

- [x] `ci.yml` runs on `pull_request` and `push` to `main`
- [x] `ci.yml` uses one inferred Python version and one inferred Node version without a version matrix
- [x] `ci.yml` installs dependencies with caching, then runs lint, type check, tests, applicable builds, and gitleaks
- [x] `ci.yml` cancels superseded runs for the same branch or pull request
- [x] `codeql.yml` uses GitHub CodeQL for the detected `python` and `javascript-typescript` languages
- [x] Both workflow files are valid YAML

---

# Test Plan

- Validate workflow YAML structure locally
- Manually verify workflow triggers, steps, and concurrency configuration
- Confirm the CI commands match the scripts and files that exist in the repo today

---

# Risks and Unknowns

**Risks**:
- The repo currently has no `.nvmrc`, `.python-version`, or lockfiles, so CI must infer sensible runtime defaults from existing project files
- The TypeScript packages currently rely on `npm install` rather than `npm ci`, which may be slower and less reproducible until lockfiles exist

**Unknowns**:
- Whether future repo growth will justify splitting CI into multiple jobs or adding path filters

---

# Open Questions

- None after approval of the inferred runtime assumptions

---
## SOURCE FILE: docs/specs/0004-initial-eval-harness.md

# Initial Eval Harness

**Status**: Done

**Author**: Codex | **Date**: 2026-05-21

---

# References

- Architecture sections: `docs/architecture/06-model-routing.md`, `docs/architecture/15-development-guide.md`
- PRD sections: `docs/prd/02-requirements.md`, `docs/prd/04-non-goals.md`
- Related specs: `docs/specs/0000-template.md`
- Convention files: `docs/conventions/ai-contributions.md`

---

# Overview

Add a runnable eval harness for the LLM-dependent surface that exists today: routing-table behavior and provider/model routing-policy invariants.

---

# In Scope

- Add `/evals` with JSON cases, a simple pytest runner, reports scaffolding, and README guidance
- Evaluate `config/routing_table.json` coverage and machine-checkable routing assertions
- Add a non-blocking GitHub Actions workflow that reports eval results on relevant pull requests

---

# Out of Scope

- Prompt-quality scoring for prompt files that do not exist yet
- Full live model-call eval execution against external providers
- Merge-blocking on eval regressions

---

# Acceptance Criteria

- [x] `/evals/cases`, `/evals/runners`, `/evals/reports`, and `/evals/README.md` exist
- [x] At least one JSON eval case covers the current routing-table behavior
- [x] A pytest-based runner loads eval cases and checks the actual repo implementation files
- [x] Eval reports are written under `/evals/reports`, which is gitignored except for `.gitkeep`
- [x] `.github/workflows/evals.yml` runs on relevant PR changes, reports results, and does not fail the PR on eval regressions
- [x] The local eval runner is executable with the repo’s current Python test tooling

---

# Test Plan

- Run the eval runner locally with pytest
- Validate the eval workflow YAML structure
- Manually confirm the workflow uses path filters and posts a summary comment on pull requests

---

# Risks and Unknowns

**Risks**:
- The harness may feel narrow until prompt files and router implementation code exist
- GitHub comment permissions can differ between same-repo PRs and forks, so comment posting needs a safe fallback

**Unknowns**:
- Which future LLM-dependent code path will be the next one added to the harness first: prompt assembly, safety classification, or routing fallback behavior

---

# Open Questions

- None after approval of the initial routing-focused scope

---
## SOURCE FILE: docs/specs/0005-scaffolding-remediation.md

# Scaffolding Remediation

**Status**: Done

**Author**: Codex | **Date**: 2026-05-21

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/06-model-routing.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0000-template.md`
- PRD sections: `docs/prd/02-requirements.md`, `docs/prd/03-scope.md`, `docs/prd/04-non-goals.md`

---

# Overview

Align the current scaffold to the technical architecture by fixing the high-reversal-cost arc execution divergences first, then closing the remaining routing, repo hygiene, and agent-workflow gaps that are still active.

---

# In Scope

- Move arc execution code into `engine/arc/`
- Replace scaffold arc dataclasses with architecture-aligned Pydantic models
- Remove the parallel manual `ArcStateMachine` wrapper and keep a single `StateChart`-based implementation
- Add `engine/session/models.py`
- Fill routing-table task and fallback gaps and update eval coverage
- Add standard Python gitignore exclusions and remove tracked Python cache artifacts
- Add minimal `nightcap/arc.json` and Alembic scaffolding
- Align agent instruction files with the current repo layout and toolchain

---

# Out of Scope

- Full production implementation of dynamic arc-chart generation from arbitrary arc definitions
- Full database schema implementation or first migration contents
- Merge-blocking behavior for the eval workflow

---

# Acceptance Criteria

- [x] Arc execution code lives under `engine/arc/` and tests import from the new module path
- [x] `ArcDefinition` and `BeatDefinition` are Pydantic models with the required architecture-facing fields
- [x] The manual `ArcStateMachine` wrapper is removed and tests target the single `StateChart`-based implementation
- [x] `engine/session/models.py` exists with Session-facing Pydantic models
- [x] `config/routing_table.json` includes `killer_assignment`, `narrator_bridge`, and fallback entries
- [x] Eval cases enforce the expanded routing table
- [x] `.gitignore` excludes standard Python cache artifacts and tracked `.pyc` files are removed
- [x] `nightcap/arc.json` and baseline Alembic scaffolding exist
- [x] `AGENTS.md` and `CLAUDE.md` no longer instruct contributors to use missing or incorrect paths/commands
- [x] Engine tests and routing evals pass locally

---

# Test Plan

- Run `pytest engine/tests`
- Run `pytest evals/runners/test_routing_evals.py -q`
- Validate updated workflow/config files as needed with lightweight local checks
- Manually verify the audit’s active findings against the resulting repo state

---

# Risks and Unknowns

**Risks**:
- Refactoring imports from `engine.arc_state` to `engine.arc.arc_state` may expose any hidden downstream dependency on the old path
- The architecture references some nested arc-schema components without fully defining every sub-schema in the checked-in docs, so some placeholder-typed fields may still be intentionally broad

**Unknowns**:
- Whether the future dynamic chart-generation implementation will keep the placeholder `StateChart` shape intact or replace it entirely once arbitrary arc loading is implemented

---

# Open Questions

- None after user approval of the remediation order

---
## SOURCE FILE: docs/specs/0006-roadmap-organization.md

# Roadmap Organization

**Status**: Completed

**Author**: Codex | **Date**: 2026-05-24

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/12-build-plan.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0000-template.md`
- PRD sections: `docs/prd/03-scope.md`

---

# Overview

Restructure the build roadmap into an agent-friendly documentation area that preserves the human-readable plan while making milestones, epics, and task specs directly addressable.

---

# In Scope

- Create `docs/roadmap/` as the canonical roadmap location
- Split the roadmap into overview, milestone, epic, task, and operations files
- Add a lightweight machine-readable manifest at `docs/roadmap/index.json`
- Convert top-level roadmap source files into archival pointers to the canonical location

---

# Out of Scope

- Changing the roadmap’s actual execution content or sequencing
- Expanding milestone decomposition beyond what the current roadmap already decomposes
- Adding project-management automation beyond a static manifest

---

# Acceptance Criteria

- [x] `docs/roadmap/README.md` explains how humans and agents should use the roadmap
- [x] Milestones, epics, and task specs are addressable as separate files where the source roadmap already supports that split
- [x] `docs/roadmap/index.json` maps IDs, scope levels, dependencies, and file paths
- [x] `docs/12-Build-Roadmap-v1.md` becomes a short archival pointer to the canonical roadmap location
- [x] The companion GitHub setup file is moved into the roadmap area or replaced with a pointer

---

# Test Plan

- Read the new roadmap README and verify it is enough to navigate the structure
- Validate `docs/roadmap/index.json` as JSON
- Manually verify the split files preserve the original roadmap content and task IDs

---

# Risks and Unknowns

**Risks**:
- Duplicating roadmap text across too many files could make future updates drift if the structure is not clearly documented

**Unknowns**:
- Whether later roadmap revisions should promote the JSON manifest to the primary source for issue generation

---

# Open Questions

- None after approval of the split-plus-manifest approach

---
## SOURCE FILE: docs/specs/0007-roadmap-tracker-alignment.md

# Roadmap Tracker Alignment

**Status**: Done

**Author**: Codex | **Date**: 2026-05-29

---

# References

- Related specs: `docs/specs/0006-roadmap-organization.md`
- Related docs: `docs/roadmap/README.md`, `docs/roadmap/index.json`
- GitHub templates: `.github/ISSUE_TEMPLATE/feature.md`, `.github/pull_request_template.md`

---

# Overview

Refine the roadmap so it remains the canonical planning source in-repo while cleanly cross-referencing the live GitHub tracker for active milestone and issue work.

---

# In Scope

- Preserve `docs/roadmap/` as the canonical roadmap location
- Add guidance for how roadmap files should relate to live GitHub issues and milestones
- Add machine-readable GitHub references to the roadmap manifest where they are known
- Add a filename-compatible archival pointer for `12-Build-Roadmap-v1.1.md`

---

# Out of Scope

- Rewriting roadmap scope, sequencing, or task content
- Creating or modifying live GitHub issues, milestones, labels, or project fields
- Embedding issue numbers throughout every roadmap Markdown file

---

# Acceptance Criteria

- [x] `docs/roadmap/README.md` explains the roadmap-to-GitHub relationship
- [x] `docs/roadmap/index.json` includes tracker metadata and known live GitHub references
- [x] The roadmap keeps Markdown as canonical and uses the manifest for live GitHub cross-references
- [x] `docs/roadmap/operations/github-project-setup.md` reflects the live tracker state instead of one-time setup only
- [x] `docs/12-Build-Roadmap-v1.1.md` exists as an archival pointer to the canonical roadmap

---

# Test Plan

- Validate `docs/roadmap/index.json` as JSON
- Manually verify the known GitHub links for M1 Epic A match the live public issue pages
- Read the updated roadmap README and GitHub operations doc to confirm the ownership split is clear

---
## SOURCE FILE: docs/specs/0008-github-tracker-reproducibility.md

# GitHub Tracker Reproducibility

**Status**: Done

**Author**: Codex | **Date**: 2026-05-29

---

# References

- Related specs: `docs/specs/0007-roadmap-tracker-alignment.md`
- Related docs: `docs/roadmap/operations/github-project-setup.md`, `docs/roadmap/index.json`
- GitHub templates: `.github/ISSUE_TEMPLATE/feature.md`, `.github/ISSUE_TEMPLATE/bug.md`, `.github/pull_request_template.md`

---

# Overview

Capture the current live GitHub tracker setup in repo-owned configuration so labels, milestones, project fields, and seed roadmap issues can be recreated from the codebase if needed.

---

# In Scope

- Add machine-readable GitHub tracker config under `.github/`
- Document how the current live setup can be rebuilt from those files
- Clarify the role of the archival `12b` setup file now that the live setup already exists

---

# Out of Scope

- Creating or modifying live GitHub labels, milestones, project fields, or issues from this environment
- Rewriting roadmap epic or task content
- Adding a networked bootstrap script that cannot be exercised safely here

---

# Acceptance Criteria

- [x] Repo contains machine-readable tracker configuration for labels, milestones, project fields, and the M1 Epic A seed issues
- [x] Canonical GitHub operations doc explains how to rebuild the setup from repo files
- [x] `12b-GitHub-M1-Epic-A-Setup.md` is treated as an archival pointer, not the canonical operational source
- [x] Roadmap manifest points at the tracker configuration so agents can discover it quickly

---

# Test Plan

- Validate the new JSON config files as JSON
- Read the rebuilt operations doc to confirm a maintainer could recreate the tracker from repo state
- Verify roadmap manifest references the new tracker config paths

---
## SOURCE FILE: docs/specs/0009-aw-101-repository-structure-and-python-project-setup.md

# Repository Structure and Python Project Setup

**Status**: Done

**Author**: Codex | **Date**: 2026-05-29

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/02-technology-stack.md`, `docs/07-Technical-Architecture-v1 3 35db7de354a881618e59e65c8e12caf6.md` Sections 2.3 and 2.4
- Related specs: `docs/specs/0000-template.md`, `docs/specs/0005-scaffolding-remediation.md`
- PRD sections: `docs/prd/02-requirements.md`, `docs/prd/03-scope.md`

---

# Overview

Add the missing Python workspace scaffolding for AW-101 without replacing the existing engine and API spine that is already present in the repository. The final state keeps shared tooling at the repo root and gives `engine/` and `api/` their own package manifests so dependencies are not mixed into one runtime package.

---

# In Scope

- Add a root `pyproject.toml` for pinned Python dependency groups and shared tooling config
- Add separate package manifests for `arcwright-engine` and `arcwright-api`
- Add a task runner interface for `lint`, `type`, `test`, and `migrate`
- Scaffold the four top-level locked test directories from Architecture S2.9
- Preserve the current `engine/` and `api/` package layout if it already satisfies the issue

---

# Out of Scope

- Changes to arc execution behavior or existing engine module implementations
- New application logic in `api/`
- Database schema changes or migration contents
- Replacing the existing `engine/tests/` suite

---

# Acceptance Criteria

- [x] `engine/` and `api/` packages exist with `__init__.py` and clear module boundaries
- [x] `pyproject.toml` pins Python 3.11+, SQLAlchemy 2.0, asyncpg, alembic, FastAPI 0.111+, python-statemachine 3.0+, and LiteLLM 1.30+
- [x] `make lint` runs ruff and passes clean
- [x] `make type` runs mypy strict and passes clean
- [x] `make test` runs pytest on an empty test suite and passes clean
- [x] `tests/knowledge_graph/`, `tests/arc/`, `tests/safety/`, and `tests/routing/` exist as scaffolded directories

---

# Test Plan

- Run `make lint`
- Run `make type`
- Run `make test`
- Manually confirm the existing `engine/` and `api/` package spine was preserved

---

# Risks and Unknowns

**Risks**:
- Windows environments may not have GNU Make installed, so a local command shim is needed for validation parity
- The default local `python` interpreter may not satisfy the repo's Python 3.11+ requirement

**Unknowns**:
- Whether future tasks will split this workspace manifest into separate distributable Python packages

---

# Open Questions

- None for AW-101 after plan approval

---
## SOURCE FILE: docs/specs/0010-aw-102-local-postgres-pgvector-alembic-init.md

# Local Postgres 15 + pgvector + Alembic Init

**Status**: Done

**Author**: Codex | **Date**: 2026-05-29

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/02-technology-stack.md`
- Related specs: `docs/specs/0009-aw-101-repository-structure-and-python-project-setup.md`
- PRD sections: `docs/prd/01-overview.md`
- Roadmap task: `docs/roadmap/tasks/AW-102-local-postgres-pgvector-alembic-init.md`

---

# Overview

Set up the local PostgreSQL development baseline for Arcwright with Postgres 15, pgvector, and Alembic configured for SQLAlchemy 2.0 async usage. The first migration enables the `vector` extension and does nothing else.

---

# In Scope

- Root `docker-compose.yml` for local Postgres 15 with pgvector
- Environment-variable-driven database configuration for local development
- Alembic async configuration using the `asyncpg` driver
- Initial Alembic migration that creates and drops the `vector` extension only
- README instructions for bringing up the local database and running migrations

---

# Out of Scope

- Cloud SQL provisioning or any non-local infrastructure work
- Application table creation or any schema beyond the `vector` extension
- Changes to engine, API, routing, safety, or knowledge graph logic
- Direct schema changes outside Alembic

---

# Acceptance Criteria

- [x] `docker compose up` brings up Postgres 15 with pgvector available
- [x] Alembic is configured for SQLAlchemy 2.0 async (`asyncpg` driver)
- [x] `alembic upgrade head` enables the vector extension with zero errors
- [x] `alembic downgrade base` reverses cleanly
- [x] No connection strings hardcoded; all config via environment variables
- [x] README documents the `docker compose up` and migration steps

---

# Test Plan

- Manual testing: run `docker compose up`
- Manual testing: run `alembic upgrade head`
- Manual testing: verify `vector` extension availability in the local database
- Manual testing: run `alembic downgrade base`

---

# Risks and Unknowns

**Risks**:
- Local Docker availability may differ by developer machine
- Alembic async configuration can fail if env var loading is inconsistent between shells

**Unknowns**:
- None within AW-102 scope after plan approval

---

# Open Questions

- None within AW-102 scope after plan approval

---
## SOURCE FILE: docs/specs/0011-aw-103-sqlalchemy-orm-models.md

# SQLAlchemy ORM Models for All Platform Tables

**Status**: Planned

**Author**: Claude | **Date**: 2026-05-29

---

# References

- Architecture sections: `docs/architecture/04-knowledge-graph.md` (§4.2–4.3), `docs/architecture/05-session-persistence.md` (§5.2, §5.4), `docs/architecture/07-character-behavior.md` (§7.2), `docs/architecture/11-telemetry.md` (§11.2, §11.4, §11.5), `docs/architecture/15-development-guide.md` (§15.3, §15.5, §15.9 #1)
- Related specs: `docs/specs/0010-aw-102-local-postgres-pgvector-alembic-init.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-103-sqlalchemy-models-for-all-platform-tables.md`

---

# Overview

Implement SQLAlchemy 2.0 async ORM models for all 15 platform database tables. These are the persistence-layer models — separate from the Pydantic domain models already in `engine/session/models.py` and `engine/arc/models.py`. The ORM models live in a new `engine/db/` module and are the sole source of truth for Alembic autogenerate. Wire the ORM metadata into `migrations/env.py` so AW-104 can autogenerate the full migration.

---

# Context From Epic A

Two things from Epic A affect this task directly:

1. **Pydantic models already exist.** `engine/session/models.py` has `Session`, `SessionParticipant`, `ArcBeat`. `engine/arc/models.py` has the arc-definition schema. These are domain models used by the engine layer — do not replace or merge them. The ORM models are a separate concern.
2. **`migrations/env.py` has `target_metadata = None`.** Alembic autogenerate will produce an empty migration until `target_metadata` is pointed at the new ORM `Base.metadata`. Updating this import is part of AW-103's scope.

---

# In Scope

- Create `engine/db/__init__.py` and `engine/db/orm.py`
- Define a `Base` (`DeclarativeBase`) in `engine/db/orm.py`
- Implement ORM models for all 15 platform tables with exact schemas below
- Include `VECTOR(1536) NULL` columns using `pgvector.sqlalchemy.Vector` on the specified tables
- Update `migrations/env.py`: import `Base` from `engine.db.orm` and assign `target_metadata = Base.metadata`
- Import smoke test: all models importable; all FK references resolve

---

# Authoritative Table Schemas

Column definitions are the implementation contract. Use exact column names. Do not add or remove columns.

---

### `accounts`

```sql
CREATE TABLE accounts (
    account_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid  TEXT NOT NULL UNIQUE,
    email         TEXT,
    display_name  TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at  TIMESTAMPTZ
);
```

`firebase_uid` is `TEXT NOT NULL UNIQUE` — a Firebase-issued string, not a UUID. `email` and `display_name` are nullable (anonymous players who create an account post-session may not supply them). No payment or billing fields.

---

### `consent_records`

```sql
CREATE TABLE consent_records (
    consent_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID REFERENCES accounts(account_id),
    session_id      UUID REFERENCES sessions(session_id),
    consent_type    TEXT NOT NULL,   -- "content_logging" | "analytics" | "terms_of_service"
    granted         BOOLEAN NOT NULL,
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_at      TIMESTAMPTZ,
    consent_version TEXT NOT NULL
);
```

Both `account_id` and `session_id` are nullable FKs — anonymous players have no `account_id`; consent may be recorded at the session level before an account exists. `consent_version` is non-negotiable for GDPR compliance. The `"content_logging"` consent type is the gate that must be checked before `CONTENT_LOGGING_ENABLED` is ever flipped to true (Arch §11.4).

---

### `characters`

```sql
-- Columns confirmed in architecture:
character_id      UUID PRIMARY KEY DEFAULT gen_random_uuid()
behavior_profile  JSONB NOT NULL DEFAULT '{}'
embedding         VECTOR(1536)    -- NULL; populated when embedding collection activates
```

`behavior_profile` stores the authored baseline psychology: personality, goals, secrets, tells, and starting relationship dispositions (Arch §7.2). This is initialized at session start and does not change during play. Live relationship evolution during a session is tracked in the `relationships` table, not written back here.

> **Note:** Additional columns (e.g. name, arc_id, session_id) are not yet defined in the architecture. Implement only these three columns and flag the gap in a PR comment.

---

### `facts`

```sql
CREATE TABLE facts (
    fact_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id    UUID NOT NULL REFERENCES sessions(session_id),
    fact_type     TEXT NOT NULL,   -- "clue" | "accusation" | "relationship" | "event"
    fact_content  JSONB NOT NULL,
    embedding     VECTOR(1536)     -- NULL at MVP; see Arch §4.5
);
```

Source: Arch §4.2, §4.5, §15.5 `assert_knowledge` signature.

---

### `knowledge_states`

```sql
CREATE TABLE knowledge_states (
    ks_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES sessions(session_id),
    character_id        UUID NOT NULL REFERENCES characters(character_id),
    fact_id             UUID NOT NULL REFERENCES facts(fact_id),
    source_character_id UUID REFERENCES characters(character_id),   -- NULL = environmental
    confidence          FLOAT NOT NULL DEFAULT 1.0,
    provenance_chain    JSONB NOT NULL DEFAULT '[]',
    asserted_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at          TIMESTAMPTZ,
    superseded_by       UUID REFERENCES knowledge_states(ks_id)     -- set on revoke; see §4.3
);
```

On revoke, a new record is inserted and the old record's `superseded_by` is set — the original record is never deleted. `provenance_chain` is an ordered JSON array of character IDs from original source to current knower (Arch §4.2). `superseded_by` is a self-referential FK; declare with `use_alter=True` in SQLAlchemy to avoid circular resolution.

---

### `relationships`

```sql
CREATE TABLE relationships (
    relationship_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id       UUID NOT NULL REFERENCES sessions(session_id),
    source_char_id   UUID NOT NULL REFERENCES characters(character_id),
    target_char_id   UUID NOT NULL REFERENCES characters(character_id),
    trust_level      FLOAT NOT NULL DEFAULT 0.5,
    history_tag      TEXT,    -- "rivalry" | "alliance" | "acquaintance" | "strangers" | etc.
    current_affect   TEXT,    -- "warm" | "cool" | "hostile" | "cautious" | "neutral"
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (session_id, source_char_id, target_char_id)
);
```

This is the live, mutable session-scoped record of how relationship dispositions evolve during play — distinct from `characters.behavior_profile` which is the authored baseline. The behavior engine reads this table (not `behavior_profile`) when building generation prompts. The `UNIQUE` constraint makes this upsert-friendly.

---

### `locations`

```sql
CREATE TABLE locations (
    location_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   UUID NOT NULL REFERENCES sessions(session_id),
    name         TEXT NOT NULL,
    description  TEXT,
    metadata     JSONB NOT NULL DEFAULT '{}'
);
```

Not used by Nightcap at MVP. Populated by the `world_generation` module in H2 (Arch §14.2). `metadata JSONB` is the extension point for monster RPG world-building properties.

---

### `objects`

```sql
CREATE TABLE objects (
    object_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   UUID NOT NULL REFERENCES sessions(session_id),
    location_id  UUID REFERENCES locations(location_id),
    name         TEXT NOT NULL,
    description  TEXT,
    metadata     JSONB NOT NULL DEFAULT '{}'
);
```

Not used by Nightcap at MVP. Populated by `world_generation` in H2. `location_id` is a nullable FK to `locations`.

---

### `decisions`

```sql
CREATE TABLE decisions (
    decision_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id     UUID NOT NULL REFERENCES sessions(session_id),
    timestamp      TIMESTAMPTZ NOT NULL DEFAULT now(),
    decision_type  TEXT NOT NULL,   -- "beat_entry" | "generative_trigger" | "safety_rule_fired"
    context        JSONB NOT NULL DEFAULT '{}',
    outcome        JSONB NOT NULL DEFAULT '{}'
);
```

The knowledge graph's operational audit trail (Arch §4.2). Records arc execution decisions made during a live session at the knowledge-graph layer. **Distinct from `decision_logs`** (step 16): `decisions` is operational/session-scoped; `decision_logs` is analytical/cross-session telemetry.

---

### `events`

```sql
CREATE TABLE events (
    event_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id    UUID NOT NULL REFERENCES sessions(session_id),
    timestamp     TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor_char_id UUID REFERENCES characters(character_id),   -- NULL for system events
    event_type    TEXT NOT NULL,
    payload       JSONB NOT NULL DEFAULT '{}',
    content_text  TEXT,       -- NULL at MVP for most event types
    embedding     VECTOR(1536)
);

CREATE INDEX ON events (session_id, timestamp);
CREATE INDEX ON events (event_type, timestamp);
```

Source: Arch §11.2 CREATE TABLE (exact). Append-only. GDPR deletion = nullify `content_text` and zero `embedding`; never delete rows.

---

### `sessions`

```sql
-- Derived from Arch §15.3 Pydantic model
session_id        UUID PRIMARY KEY DEFAULT gen_random_uuid()
arc_id            TEXT NOT NULL
status            TEXT NOT NULL    -- "created"|"active"|"paused"|"completed"|"abandoned"
host_account_id   UUID NOT NULL REFERENCES accounts(account_id)
created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
started_at        TIMESTAMPTZ
completed_at      TIMESTAMPTZ
current_beat_id   TEXT NOT NULL
quality_tier      TEXT NOT NULL    -- "standard"|"premium"
player_count      INT NOT NULL
```

---

### `session_participants`

```sql
-- Derived from Arch §15.3 Pydantic model
participant_id    UUID PRIMARY KEY DEFAULT gen_random_uuid()
session_id        UUID NOT NULL REFERENCES sessions(session_id)
character_id      UUID NOT NULL REFERENCES characters(character_id)
account_id        UUID REFERENCES accounts(account_id)   -- NULL for anonymous players
join_token        TEXT NOT NULL
surface_type      TEXT NOT NULL    -- "phone"|"shared_display"|"host"
is_ai_controlled  BOOLEAN NOT NULL DEFAULT false
```

---

### `arc_beat_states`

```sql
CREATE TABLE arc_beat_states (
    state_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id            UUID NOT NULL REFERENCES sessions(session_id),
    beat_id               TEXT NOT NULL,
    statemachine_config   JSONB NOT NULL,
    transition_history    JSONB NOT NULL DEFAULT '[]',
    snapshot_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_current            BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX ON arc_beat_states (session_id, is_current);
```

`statemachine_config` stores python-statemachine's `configuration` value serialized as JSONB — this is what gets deserialized back into the statemachine instance on resume (Arch §5.2, §5.4). `transition_history` is the ordered array of beat transitions for full replay. `is_current` enables a simple indexed query to find the active snapshot; set to `false` on all previous rows when a new snapshot is written.

---

### `generation_logs`

```sql
CREATE TABLE generation_logs (
    log_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id       UUID NOT NULL REFERENCES sessions(session_id),
    timestamp        TIMESTAMPTZ NOT NULL DEFAULT now(),
    task_type        TEXT NOT NULL,
    quality_tier     TEXT NOT NULL,
    model_used       TEXT NOT NULL,
    latency_ms       INTEGER NOT NULL,
    input_tokens     INTEGER NOT NULL,
    output_tokens    INTEGER NOT NULL,
    cost_usd         NUMERIC(10,6) NOT NULL,
    tension_score    FLOAT,
    -- Populated only when CONTENT_LOGGING_ENABLED=true:
    prompt_text      TEXT,
    output_text      TEXT,
    prompt_embedding VECTOR(1536),
    output_embedding VECTOR(1536)
);
```

Source: Arch §11.4 CREATE TABLE (exact). All four content columns are always nullable. Populated only when `CONTENT_LOGGING_ENABLED=true` and valid `consent_records` exist.

---

### `decision_logs`

```sql
CREATE TABLE decision_logs (
    decision_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id     UUID NOT NULL REFERENCES sessions(session_id),
    timestamp      TIMESTAMPTZ NOT NULL DEFAULT now(),
    decision_type  TEXT NOT NULL,
    input_context  JSONB NOT NULL,
    outcome        JSONB NOT NULL
);
```

Source: Arch §11.5 CREATE TABLE (exact). Cross-session analytical telemetry — distinct from `decisions` (operational audit). Use exact column names.

---

# Table Count Note

The architecture references "all 16 tables" in §15.9 but §15.3 lists 15 in the creation order. This spec implements all 15 that are defined. If a 16th table is found in any architecture document during implementation, add it and flag it in a PR comment.

---

# Out of Scope

- Changes to existing Pydantic models in `engine/session/models.py` or `engine/arc/models.py`
- Writing the Alembic migration (AW-104)
- Adding Nightcap-specific columns to any platform table
- Inventing columns not listed in this spec
- SQLAlchemy event listeners, hybrid properties, or application-layer triggers

---

# Acceptance Criteria

- [ ] `engine/db/orm.py` exists with a `Base` and ORM models for all 15 platform tables
- [ ] All models have exact column schemas matching the table definitions above
- [ ] `VECTOR(1536) NULL` on `characters.embedding`, `facts.embedding`, `events.embedding`, `generation_logs.prompt_embedding`, `generation_logs.output_embedding`
- [ ] `behavior_profile JSONB` on `characters`
- [ ] `UNIQUE (session_id, source_char_id, target_char_id)` constraint on `relationships`
- [ ] Index on `arc_beat_states (session_id, is_current)`
- [ ] No Nightcap-specific column names on any platform table
- [ ] `migrations/env.py` imports `Base` from `engine.db.orm` and assigns `target_metadata = Base.metadata`
- [ ] Import smoke test: `python -c "from engine.db.orm import Base; print(list(Base.metadata.tables.keys()))"` prints all 15 table names
- [ ] `make type` passes clean

---

# Test Plan

- Import smoke test: verify all 15 table names present in `Base.metadata.tables`
- Relationship integrity: instantiate representative ORM objects; confirm FK references resolve at import time
- `make type` / `make lint` pass

---

# Risks and Unknowns

**Risks**:
- `pgvector.sqlalchemy.Vector` requires the `pgvector` Python package. Verify it is in `pyproject.toml` before writing imports.
- `knowledge_states.superseded_by` is a self-referential FK. Declare with `use_alter=True` in SQLAlchemy to avoid circular resolution at table creation time.
- `consent_records` has two nullable FKs (`account_id`, `session_id`) — both must be declared nullable with no `NOT NULL` constraint.

**Remaining open question**:
- `characters` table: additional columns beyond `character_id`, `behavior_profile`, `embedding` are not yet defined in the architecture. Implement exactly the three confirmed columns; flag in a PR comment.

---

# Open Questions

1. **16 vs 15 tables:** Arch §15.9 references "all 16 tables" while §15.3 lists 15 in the migration order. No 16th table has been identified. Flag if found during implementation.
2. **`characters` additional columns:** Only `character_id`, `behavior_profile`, `embedding` are confirmed. Are there additional columns (name, arc_id, session_id)?

---
## SOURCE FILE: docs/specs/0012-aw-104-first-full-alembic-migration.md

# First Full Alembic Migration

**Status**: Planned

**Author**: Claude | **Date**: 2026-05-29

---

# References

- Architecture sections: `docs/architecture/02-technology-stack.md` (§2.4), `docs/architecture/15-development-guide.md` (§15.3, §15.9 #1)
- Related specs: `docs/specs/0011-aw-103-sqlalchemy-orm-models.md`, `docs/specs/0010-aw-102-local-postgres-pgvector-alembic-init.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-104-first-full-alembic-migration.md`

---

# Overview

Generate and hand-verify the second Alembic migration — `0002_create_platform_tables` — that creates all platform tables, primary keys, foreign keys, and required indexes. The first migration (`0001_enable_vector_extension.py`) already enables the `vector` extension; this migration builds on that. This task depends on AW-103 having wired `Base.metadata` into `migrations/env.py`.

---

# Context From Epic A

- `migrations/versions/0001_enable_vector_extension.py` exists and is the current `head`. The new migration chains off it.
- `migrations/env.py` is configured for SQLAlchemy 2.0 async (`asyncpg`). No changes to env.py are needed in this task (AW-103 handles the `target_metadata` wire-up).
- Alembic autogenerate does **not** fully handle `VECTOR` columns or `JSONB`; the autogenerated migration must be reviewed by hand and patched where needed before committing.

---

# In Scope

- Run `alembic revision --autogenerate -m "create_platform_tables"` against the ORM models from AW-103
- Hand-review the generated migration file and correct any deficiencies (see Review Checklist below)
- Confirm the migration is deterministic and re-runnable on a fresh database
- Confirm `alembic downgrade base` drops all tables and the `vector` extension cleanly

---

# Out of Scope

- Adding columns, tables, or constraints not defined in the AW-103 ORM models or architecture §15.3
- Cloud SQL provisioning
- Any application logic changes

---

# Migration Review Checklist

Autogenerate misses or mishandles these items — verify each by hand before committing:

1. **`VECTOR(1536)` columns** — autogenerate may emit them as `NullType` or omit them. Patch to `Vector(1536)` using the `pgvector.sqlalchemy` import, guarded by a try/except for environments without pgvector installed.
2. **`JSONB` columns** — autogenerate may emit `JSON` instead of `JSONB`. Change to `JSONB` explicitly.
3. **Extension ordering** — verify the `down_revision` in the new file equals the revision ID from `0001_enable_vector_extension.py`.
4. **Append-only annotation on `events`** — add a table comment noting this is append-only; enforcement is at the engine layer. Do not add a database trigger (out of scope at MVP).
5. **Index on `events(session_id, timestamp)` and `events(event_type, timestamp)`** — required per Arch §11.2. Add if missing.
6. **Index on `arc_beat_states(session_id, is_current)`** — required for the nearest-beat restore pattern. Add if missing.
7. **`UNIQUE (session_id, source_char_id, target_char_id)` on `relationships`** — verify autogenerate captured the table-level constraint.
8. **`nullable=True` on all content columns in `generation_logs`** — `prompt_text`, `output_text`, `prompt_embedding`, `output_embedding` are all nullable at MVP.
9. **Self-referential FK on `knowledge_states.superseded_by`** — verify it is present with `use_alter=True`.

---

# Acceptance Criteria

- [ ] `alembic upgrade head` on a fresh database (only `0001` applied) completes with zero errors
- [ ] All 15 platform tables exist after upgrade
- [ ] `pgvector` extension created before any `VECTOR` column (chain ordering verified)
- [ ] `VECTOR(1536)` columns present and nullable on `characters`, `facts`, `events`, `generation_logs`
- [ ] `JSONB` (not `JSON`) on all JSONB columns
- [ ] Index on `events(session_id, timestamp)` and `events(event_type, timestamp)` present
- [ ] Index on `arc_beat_states(session_id, is_current)` present
- [ ] `UNIQUE (session_id, source_char_id, target_char_id)` constraint on `relationships` present
- [ ] `alembic downgrade base` drops all tables and the extension with zero errors
- [ ] Migration is re-runnable: `downgrade base` then `upgrade head` succeeds a second time on the same database

---

# Test Plan

- Manual: `docker compose up` → `alembic upgrade head` → inspect tables with `\dt` in psql
- Manual: verify VECTOR columns exist: `\d characters` in psql, confirm `embedding` column type
- Manual: `alembic downgrade base` → confirm tables gone, `vector` extension gone
- Manual: `alembic upgrade head` again on same DB (idempotency check)
- CI: fresh-database upgrade and downgrade cycle (no local state)

---

# Risks and Unknowns

**Risks**:
- Alembic autogenerate may produce a migration with no operations if `target_metadata` in `migrations/env.py` was not updated in AW-103. Verify `target_metadata` is set before running autogenerate.
- `pgvector.sqlalchemy.Vector` import in the migration file may fail in environments without the Python `pgvector` package. The migration should handle this gracefully (conditional import or type registration).

**Unknowns**:
- Whether any additional indexes (beyond the two specified above) are required for MVP query patterns. Defer additional indexes to a follow-on migration; do not block AW-104.

---

# Open Questions

- None within AW-104 scope after plan approval.

---
## SOURCE FILE: docs/specs/0013-aw-106-pre-generation-knowledge-constraint-hook.md

# AW-106 Pre-generation Knowledge Constraint Hook

**Status**: Draft

**Author**: Codex | **Date**: 2026-05-31

---

# References

- Architecture sections: `docs/architecture/04-knowledge-graph.md` (§4.2, §4.3), `docs/architecture/07-character-behavior.md` (§7.3), `docs/architecture/11-telemetry.md` (§11.3)
- Related specs: `docs/specs/0011-aw-103-sqlalchemy-orm-models.md`, `docs/specs/0012-aw-104-first-full-alembic-migration.md`
- PRD sections: `docs/prd/02-requirements.md` (Principle 5, Character management, Knowledge graph)
- Roadmap task: `docs/roadmap/tasks/AW-106-pre-generation-knowledge-constraint-hook.md`

---

# Overview

Define the single engine hook that assembles prompt-facing knowledge constraints for AI character generation. The hook is session-scoped, queries the active knowledge state for one character, derives both permitted and blocked facts for that session, and returns them in a stable deterministic order.

---

# In Scope

- Add one sanctioned function for generation-time knowledge constraint assembly
- Return a structured generation-context object rather than raw ORM rows
- Include both "knows" and "does not know" fact sets for the current session scope
- Include confidence and provenance-chain length for known facts
- Enforce stable ordering for cache-friendly prompt assembly
- Add unit tests for scoping, exclusion, and ordering behavior

---

# Out of Scope

- Full character behavior pipeline implementation from architecture §7.3
- Prompt templating or model invocation changes
- Telemetry emission plumbing beyond returning data needed by later telemetry work
- Relationship graph, social pressure, or safety-layer integration
- Schema or migration changes

---

# Proposed Interface

`build_character_generation_context(session, *, session_id, character_id) -> CharacterGenerationContext`

Notes:

- `session_id` and `character_id` are both mandatory. `character_id` alone is not sufficient to scope knowledge safely.
- The function is the sanctioned generation-facing chokepoint. Raw knowledge graph queries remain internal building blocks, not prompt-context APIs.
- The return value is a structured object suitable for direct prompt assembly later.

---

# Return Shape

`CharacterGenerationContext` should contain:

- `session_id`
- `character_id`
- `known_facts`: ordered structured items for facts currently known by the character
- `unknown_facts`: ordered structured items for facts in the same session not currently known by the character

Each `known_facts` item should contain:

- `fact_id`
- `fact_type`
- `fact_content`
- `confidence`
- `provenance_chain`
- `provenance_chain_length`

Each `unknown_facts` item should contain:

- `fact_id`
- `fact_type`
- `fact_content`

Ordering must be deterministic so repeated calls over unchanged data produce byte-stable prompt inputs.

---

# Ordering Rules

To satisfy cache friendliness and avoid caller divergence, the hook owns ordering:

- `known_facts` ordered by `asserted_at`, then `fact_id`
- `unknown_facts` ordered by `fact_id`

If implementation constraints require a different deterministic tie-breaker discovered in code review, it must remain fully stable and be covered by tests.

---

# Acceptance Criteria

- [ ] A single sanctioned function accepts `session_id` and `character_id` and returns that character's complete current generation-time knowledge context
- [ ] The returned context includes only facts currently known by that character in that session, plus the session-scoped facts the character does not know
- [ ] The sanctioned interface is the only generation-context assembly path exposed for character generation work
- [ ] Returned known and unknown fact lists are stable and ordered deterministically
- [ ] Unit tests prove the hook never returns a known fact outside the character's active state

---

# Test Plan

- Unit tests: character scoping within a session
- Unit tests: session scoping across identical character IDs in different sessions
- Unit tests: superseded knowledge records excluded from known facts
- Unit tests: session facts absent from a character's knowledge appear in unknown facts
- Unit tests: repeated calls return the same ordered fact IDs for unchanged fixtures

---

# Risks and Unknowns

**Risks**:
- Exposing raw `KnowledgeState` rows as the public return type would push prompt-shaping and ordering logic into callers, undermining the chokepoint requirement.
- Forgetting session-wide fact enumeration would make the negative constraint block impossible to build later without bypass logic.

**Unknowns**:
- None within AW-106 scope after contract clarification on 2026-05-31.

---

# Open Questions

- None. Contract clarified with user before implementation.

---
## SOURCE FILE: docs/specs/0014-aw-107-litellm-routing-layer.md

# AW-107 LiteLLM Routing Layer

**Status**: Draft

**Author**: Codex | **Date**: 2026-05-31

---

# References

- Architecture sections: `docs/architecture/06-model-routing.md` (§6.1-§6.5), `docs/architecture/15-development-guide.md` (§15.7, §15.9)
- Related specs: `docs/specs/0009-aw-101-repository-structure-and-python-project-setup.md`, `docs/specs/0013-aw-106-pre-generation-knowledge-constraint-hook.md`
- PRD sections: `docs/prd/02-requirements.md` (Principles 6 and 8), `docs/prd/03-scope.md` (MVP done criteria), `docs/prd/04-non-goals.md`
- GitHub issue: `#15 AW-107: LiteLLM routing layer`

---

# Overview

Complete the existing model-routing scaffold so every LiteLLM generation call returns structured metadata needed by downstream telemetry work, without implementing any logging or database writes in this task. The routing layer must stay provider-agnostic, use the config-defined routing table, and handle tier fallbacks in one place.

---

# In Scope

- Add a frozen `RouteResult` dataclass to `engine/routing/router.py`
- Change `route_generation` to return `RouteResult` instead of a bare string
- Measure call latency and extract prompt and completion token counts from the LiteLLM response
- Preserve and verify fallback behavior when the primary routed model call fails
- Cache the routing table at module import time rather than re-reading it on every call
- Export `RouteResult` and `route_generation` from `engine/routing/__init__.py`
- Add offline unit tests in `engine/tests/test_routing.py`
- Verify the existing `config/routing_table.json` contents against architecture §6.3 without regenerating or rewriting the file

---

# Out of Scope

- Writing `generation_logs` rows or any other telemetry persistence
- Logging fallback events or any other data to the `events` table
- Prompt caching implementation
- Direct provider SDK integration such as `anthropic` or `groq`
- Regenerating or modifying `config/routing_table.json`
- Database, ORM, or migration changes

---

# Proposed Interface

```python
@dataclass(frozen=True)
class RouteResult:
    content: str
    model_used: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    used_fallback: bool


async def route_generation(
    task_type: str,
    quality_tier: str,
    messages: list[dict],
    temperature: float = 0.7,
) -> RouteResult:
    ...
```

Notes:

- `model_used` is the routing-table key actually used for the successful call, including the fallback key when fallback fires.
- `used_fallback` is `True` only when the primary call raised and the fallback call succeeded.
- `latency_ms` is measured with `time.perf_counter()` around each LiteLLM completion attempt and converted with `int((end - start) * 1000)`.
- Token counts come from `response.usage.prompt_tokens` and `response.usage.completion_tokens`.

---

# Routing Table Contract

`config/routing_table.json` is the sole source of provider and model strings. For each MVP task type from architecture §6.3, the table must contain:

- `standard`
- `premium`
- `standard_fallback`
- `premium_fallback`

Required task types:

- `character_dialogue`
- `narrative_generation`
- `pacing_decision`
- `knowledge_inference`
- `safety_classification`
- `killer_assignment`
- `narrator_bridge`

Implementation must load this table once at module import and reuse the cached data for lookups.

---

# Acceptance Criteria

- [ ] `route_generation` returns a `RouteResult` with correct `content`, `model_used` matching the routing-table entry, non-zero `input_tokens` and `output_tokens`, positive `latency_ms`, and `used_fallback=False` on a clean call
- [ ] When the primary call raises, `route_generation` retries with the fallback model and returns `RouteResult` with `used_fallback=True` and `model_used` set to the fallback key
- [ ] When the primary raises and no `_fallback` key exists for the tier, the exception propagates with no silent failure
- [ ] `routing_table.json` contains all 7 task types from architecture §6.3, each with all four tier keys
- [ ] `RouteResult` and `route_generation` are importable as `from engine.routing import RouteResult, route_generation`
- [ ] No model name or provider string appears in any file outside `routing_table.json` and `router.py`
- [ ] `make type` and `make lint` pass

---

# Test Plan

- Unit tests: patch `engine.routing.router.litellm.acompletion` with `unittest.mock.AsyncMock`
- Unit tests: verify `route_generation` uses the model key defined in `routing_table["character_dialogue"]["standard"]`
- Unit tests: verify `RouteResult` contains content, token counts, latency, model key, and `used_fallback=False` on a clean call
- Unit tests: verify fallback model is called and `used_fallback=True` when the primary attempt raises
- Unit tests: verify the original exception propagates when no fallback entry exists for the requested tier
- Unit tests: verify `routing_table.json` contains all seven architecture task types and all four tier keys for each
- Unit tests: verify `resolve_model_key("nonexistent", "standard")` raises `KeyError`
- Manual verification: confirm no provider or model strings are introduced outside `config/routing_table.json` and `engine/routing/router.py`

---

# Risks and Unknowns

**Risks**:
- Re-reading the routing table on every lookup would violate the task contract and make the routing layer less predictable under load.
- Returning only a bare string would block downstream telemetry work from capturing model key, latency, and token metadata.
- Accidentally adding logging or persistence here would leak AW-108 scope into this task.

**Unknowns**:
- None within AW-107 scope once the issue body is treated as the authoritative source for the missing spec file.

---

# Open Questions

- None. The issue body is being transcribed into this spec as directed.

---
## SOURCE FILE: docs/specs/0015-aw-110-headless-session-runner-core.md

# AW-110 Headless Session Runner Core

**Status**: Draft

**Author**: Codex | **Date**: 2026-05-31

---

# References

- Architecture sections: `docs/architecture/03-arc-execution.md` (§3.1, §3.2, §3.6, §3.7), `docs/architecture/05-session-persistence.md` (§5.2-§5.4), `docs/architecture/12-build-plan.md` (§12.2 Phase 7), `docs/architecture/15-development-guide.md` (§15.3, §15.9 #11)
- Related specs: `docs/specs/0009-aw-101-repository-structure-and-python-project-setup.md`, `docs/specs/0011-aw-103-sqlalchemy-orm-models.md`, `docs/specs/0013-aw-106-pre-generation-knowledge-constraint-hook.md`, `docs/specs/0014-aw-107-litellm-routing-layer.md`
- PRD sections: `docs/prd/02-requirements.md` (Principles 2, 5, and 8)
- Roadmap task: `docs/roadmap/tasks/AW-110-simulation-harness-skeleton.md`
- GitHub issue: TBD

---

# Overview

Build the engine-local runner that the rest of Epic E depends on. It must load the current Nightcap arc scaffold, instantiate session state, advance the `ArcStateChart` from deterministic inputs, and emit a stable trace for tests without involving UI, SSE, or real provider calls.

---

# Context From Current State

Three facts constrain this task:

1. `engine/arc/arc_state.py` is the only executable arc runtime currently present. It is a scaffolded `ArcStateChart`, not yet the future generated chart from architecture §3.2.
2. `engine/events`, `engine/safety`, and `engine/telemetry` do not yet provide runnable runtime services. The harness runner must stay in-process and self-contained.
3. Epic D completed the routing abstraction. If this task touches any generation boundary, the logging-aware entrypoint is `engine.routing.logging.generate`, not `engine.routing.router.route_generation`. Prompt assembly must use `build_character_generation_context` and `CharacterGenerationContext` from `engine.characters`, which are the implemented names from Epic C.

This means AW-110 is a runner-core task, not a full session coordinator, and not a networked gameplay loop.

**Arc transition names and configurations.** The `ArcStateChart` uses python-statemachine v3 `StateChart`. `chart.current_state` is deprecated in that version -- use `chart.configuration_values` (a set of lowercase state ID strings) instead. The complete sorted configuration after each happy-path transition is:

| Transition | `sorted(chart.configuration_values)` after |
|---|---|
| *(initial)* | `['introduction', 'onboarding']` |
| `begin_game` | `['introduction', 'killer_assignment']` |
| `motives_established` | `['introduction', 'motive_reveal']` |
| `investigation_begins` | `['clue_phase', 'distributing', 'interrogation', 'investigation', 'open', 'private_clues']` |
| `clues_sent` | `['clue_phase', 'distributed', 'interrogation', 'investigation', 'open', 'private_clues']` |
| `interrogation_complete` | `['closed', 'clue_phase', 'distributed', 'interrogation', 'investigation', 'private_clues']` |
| `phases_complete` | `['investigation', 'resolution']` |
| `accusation_filed` | `['reveal']` |

During `investigation` the parallel `clue_phase` branches are both active; the configuration list has 6 entries, not 1. A single string cannot represent this. `apply_action` calls `getattr(self._chart, action.transition_name)()` then captures `sorted(chart.configuration_values)` as the `to_configuration` trace field. Beat IDs from `nightcap/arc.json` are metadata only; the chart is driven by transition names.

**Session identity.** `HarnessRun` carries `session_id: UUID` directly. Do not use the ORM `Session` from `engine.db.orm` in runner state -- that model requires a live SQLAlchemy session. If tests need to exercise any generation boundary, inject a stub callable rather than wiring up a DB session; follow the `_patch_metadata_for_sqlite` pattern from `engine/tests/test_generation_logging.py` only if ORM access is unavoidable.

---

# In Scope

- Create `engine/harness/` as a new engine-local package
- Add a small run-state model layer such as `engine/harness/models.py`
- Add a runner implementation such as `engine/harness/runner.py`
- Load `nightcap/arc.json` and bind it to the existing `ArcStateChart`
- Instantiate deterministic runner state from:
  - the Nightcap arc definition
  - a `Session`-compatible session record
  - a caller-provided seed
- Expose programmatic runner operations for:
  - session bootstrap
  - session start
  - direct action application
  - current snapshot retrieval
  - immutable trace retrieval
- Record a deterministic trace of beat transitions and harness actions using step indexes, not wall-clock timestamps
- Keep AI boundaries injectable or mockable so the runner can stay offline
- Add focused tests, expected at `engine/tests/test_harness_runner.py`

---

# Out of Scope

- Declarative synthetic-player scenarios or scenario files
- Batch execution, replay diffing, or 10-run harness tooling
- SSE event delivery, FastAPI routes, or browser-facing clients
- Real provider calls or token-spending smoke tests
- Session persistence writes to `arc_beat_states`, `events`, `generation_logs`, or `decision_logs`
- Replacing the current handcrafted `ArcStateChart` with a generated chart

---

# Proposed Shape

The exact names may vary, but the implementation should stay close to this split:

```python
class HarnessAction(BaseModel):
    transition_name: str                          # e.g. "begin_game", "investigation_begins"
    payload: dict[str, Any] = Field(default_factory=dict)


class HarnessTraceEntry(BaseModel):
    step_index: int
    transition_name: str
    from_configuration: list[str]                 # sorted(chart.configuration_values) before transition
    to_configuration: list[str]                   # sorted(chart.configuration_values) after transition
    payload: dict[str, Any] = Field(default_factory=dict)
    # debug_ts excluded from canonical equality path; keep outside HarnessTraceEntry if needed


class HarnessSnapshot(BaseModel):
    step_index: int
    configuration: list[str]                      # sorted(chart.configuration_values) at snapshot time
    seed: int
    session_id: UUID


class HarnessRun(BaseModel):
    seed: int
    session_id: UUID
    arc_id: str
    configuration: list[str]                      # sorted(chart.configuration_values) -- current live state
    step_index: int
    trace: list[HarnessTraceEntry]


class HarnessRunner:
    def __init__(self, *, arc_path: Path, seed: int) -> None: ...
    def start(self) -> HarnessRun: ...
    def apply_action(self, action: HarnessAction) -> HarnessTraceEntry: ...
    def snapshot(self) -> HarnessSnapshot: ...
    def trace(self) -> list[HarnessTraceEntry]: ...
```

Notes:

- Use a seeded local RNG such as `random.Random(seed)` and store the seed on the run object.
- `apply_action` captures `sorted(chart.configuration_values)` before and after calling `getattr(self._chart, action.transition_name)()`.
- Do not use `chart.current_state` -- it is deprecated in python-statemachine v3 and collapses parallel states to one value. Use `chart.configuration_values` exclusively.
- `from_configuration` and `to_configuration` must be `sorted(...)` lists; parallel states activate as a set and `configuration_values` is unordered -- without sorting, equality assertions are non-deterministic.
- Do not capture `datetime.now()` anywhere on `HarnessTraceEntry`. If wall-clock timestamps are useful for debugging, add them as a separate field excluded from `canonicalize_trace` in AW-112.

---

# Acceptance Criteria

- [ ] `engine/harness/` exists with a runnable harness core
- [ ] The runner loads `nightcap/arc.json`, instantiates the current `ArcStateChart`, and starts a session without UI
- [ ] The runner can advance the Nightcap scaffold programmatically from `introduction` to `investigation` to `reveal`
- [ ] The runner stores the run seed and exposes it in run state and trace metadata
- [ ] The runner records deterministic trace entries and snapshots suitable for equality assertions
- [ ] The runner introduces no direct provider SDK usage and no provider or model string literals
- [ ] AI boundaries are injectable or mockable so the runner stays offline
- [ ] `pytest engine/tests/test_harness_runner.py -v` passes

---

# Test Plan

- Unit tests: runner initialization from Nightcap arc and seeded session state
- Unit tests: direct action stepping moves across the expected beats
- Unit tests: snapshot output reflects current beat and step index correctly
- Unit tests: repeated runs with the same seed and direct action sequence produce identical canonical traces
- Manual verification: instantiate the runner in a Python REPL and inspect the trace after a three-beat happy-path run

---

# Risks and Unknowns

**Risks**:
- The current `ArcStateChart` is scaffolded by hand and may drift from `nightcap/arc.json`. The runner should treat the current executable chart as authoritative for now and keep the binding narrow.
- If trace records include non-deterministic data such as wall-clock timestamps or unordered dict rendering, seeded equality tests will be flaky.
- Overreaching into session coordination, persistence, or SSE now would duplicate future architecture rather than scaffold it.

**Unknowns**:
- None within AW-110 scope after constraining the task to the current in-process scaffold.

---

# Open Questions

- None within AW-110 scope after the Epic E split.

---
## SOURCE FILE: docs/specs/0016-aw-111-scripted-synthetic-player-driver.md

# AW-111 Scripted Synthetic Player Driver

**Status**: Draft

**Author**: Codex | **Date**: 2026-05-31

---

# References

- Architecture sections: `docs/architecture/02-technology-stack.md` (§2.9), `docs/architecture/03-arc-execution.md` (§3.6, §3.7), `docs/architecture/12-build-plan.md` (§12.2 Phase 7), `docs/architecture/15-development-guide.md` (§15.9 #11)
- ADRs: `docs/decisions/0002-harness-scenario-execution-contract.md`
- Related specs: `docs/specs/0015-aw-110-headless-session-runner-core.md`, `docs/specs/0013-aw-106-pre-generation-knowledge-constraint-hook.md`, `docs/specs/0014-aw-107-litellm-routing-layer.md`
- PRD sections: `docs/prd/02-requirements.md` (Principles 2 and 5)
- Roadmap task: `docs/roadmap/tasks/AW-111-scripted-synthetic-player-driver.md`
- GitHub issue: TBD

---

# Overview

Build the declarative scenario layer on top of the AW-110 runner core. Synthetic players should be describable as scripted actors whose actions drive the Nightcap scaffold without UI, network transport, or real model calls.

---

# Context From Current State

This task must respect three current-state constraints:

1. There is no canonical player-input API yet. The script layer should target the harness runner's action contract, not invent a public REST or SSE schema early.
2. Epic D completed the routing abstraction and established the testing rule that provider and model literals stay out of new harness tests. If this task needs generation seams for future extensibility, mock at `engine.routing.logging.generate` or inject a fake callable.
3. `ScenarioStep.action_type` values are `transition_name` strings that map directly to `HarnessAction.transition_name` from AW-110. The scenario executor does not maintain a separate action taxonomy. The full Nightcap happy-path sequence in order is: `begin_game`, `motives_established`, `investigation_begins`, `clues_sent`, `interrogation_complete`, `phases_complete`, `accusation_filed`. Any scenario fixture that exercises start-to-reveal must include all seven steps in this order; a scenario that skips sub-state transitions will fail when the chart refuses an invalid transition.

---

# In Scope

- Add a scenario model layer such as `engine/harness/scenario.py`
- Define a small declarative schema for:
  - synthetic players
  - initial runner seed
  - ordered scenario steps
  - optional expected beat checkpoints
- Implement a scenario executor that maps scenario steps to AW-110 runner actions
- Ensure deterministic participant identity assignment and action ordering
- Validate invalid scenarios early with clear errors:
  - unknown player id
  - invalid action type
  - step applied from the wrong beat
  - missing required payload fields
- Add focused tests, expected at `engine/tests/test_harness_scenarios.py`

---

# Out of Scope

- Batch execution and multi-run determinism summaries
- Replay diff visualization or UI
- FastAPI integration, browser simulation, or transport-level contracts
- Real AI generation or token-spending tests
- Scenario statistics beyond what is needed to prove one scripted run works

---

# Proposed Shape

```python
class SyntheticPlayer(BaseModel):
    player_id: str                                # stable string id; must match actor_id in steps
    display_name: str
    is_killer: bool = False                       # optional hint for scenario fixtures; not enforced by executor


class ScenarioStep(BaseModel):
    actor_id: str                                 # must match a SyntheticPlayer.player_id
    action_type: str                              # equals HarnessAction.transition_name exactly
    payload: dict[str, Any] = Field(default_factory=dict)
    expected_beat: str | None = None              # if set, executor asserts this ID is in to_configuration


class HarnessScenario(BaseModel):
    scenario_id: str
    seed: int
    players: list[SyntheticPlayer]
    steps: list[ScenarioStep]


class HarnessRunResult(BaseModel):
    scenario_id: str
    seed: int
    run: HarnessRun                               # final HarnessRun from AW-110 runner
    passed: bool
    failure_reason: str | None = None


class ScenarioExecutor:
    def run(self, scenario: HarnessScenario) -> HarnessRunResult: ...
```

The schema should stay intentionally small. It is an engine test harness contract, not the public API.

Participant IDs are assigned deterministically: `player_id` from `SyntheticPlayer` is used as-is and stored on `HarnessRun`; do not generate UUIDs from `uuid4()` for synthetic players. This keeps scenario fixtures reproducible without a seed-derived UUID derivation.

---

# Acceptance Criteria

- [ ] A declarative scenario schema exists for scripted synthetic players and ordered actions
- [ ] A scripted scenario can drive the current Nightcap scaffold from session start through reveal without UI
- [ ] Scenario execution uses AW-110 runner actions rather than inventing a separate runtime path
- [ ] Invalid or out-of-order scenario steps raise clear harness errors
- [ ] Scenario execution stays offline and mock-friendly
- [ ] No provider or model string literals are introduced in scenario code or tests
- [ ] `pytest engine/tests/test_harness_scenarios.py -v` passes

---

# Test Plan

- Unit tests: scenario model validation for missing actors, invalid actions, and wrong-beat steps
- Unit tests: happy-path scripted scenario completes the current Nightcap scaffold end-to-end
- Unit tests: participant identities and action ordering are deterministic across repeated runs
- Manual verification: run one small scenario fixture and inspect the resulting runner trace

---

# Risks and Unknowns

**Risks**:
- If the DSL becomes too expressive now, it will ossify the wrong abstraction before the real session coordinator exists.
- If scenarios bypass the AW-110 runner and call chart transitions directly, later determinism checks will be split across two code paths.
- If scenario fixtures carry provider details or raw routing assumptions, the harness will regress on Epic D's abstraction guarantees.

**Unknowns**:
- None within AW-111 scope after constraining the DSL to runner-local actions.

---

# Open Questions

- None within AW-111 scope after the Epic E split.

---
## SOURCE FILE: docs/specs/0017-aw-112-deterministic-replay-and-batch-runner.md

# AW-112 Deterministic Replay and Batch Runner

**Status**: Draft

**Author**: Codex | **Date**: 2026-05-31

---

# References

- Architecture sections: `docs/architecture/02-technology-stack.md` (§2.9), `docs/architecture/11-telemetry.md` (§11.1), `docs/architecture/12-build-plan.md` (§12.2 Phase 7), `docs/architecture/15-development-guide.md` (§15.9 #11)
- Related specs: `docs/specs/0015-aw-110-headless-session-runner-core.md`, `docs/specs/0016-aw-111-scripted-synthetic-player-driver.md`, `docs/specs/0014-aw-107-litellm-routing-layer.md`
- PRD sections: `docs/prd/02-requirements.md` (Principles 6 and 8)
- Roadmap task: `docs/roadmap/tasks/AW-112-deterministic-replay-and-batch-runner.md`
- GitHub issue: TBD

---

# Overview

Complete the Epic E acceptance bar by adding deterministic trace comparison and a headless batch runner that can execute scripted scenarios repeatedly without UI or token spend.

---

# Context From Current State

The build roadmap's Phase 7 lists "synthetic players, seeded runs, batch statistics." Current repo state supports only the first two layers after AW-110 and AW-111. This task finishes the deterministic and batch execution pieces without overreaching into telemetry pipelines or dashboards.

Epic D also matters here: any generation seam used during batch runs must stay mockable. The established mock target is `engine.routing.logging.route_generation` (patched with `AsyncMock`), exactly as done in `engine/tests/test_generation_logging.py`. Do not mock lower (`litellm.acompletion`) or higher (`engine.routing.logging.generate`) than this boundary -- the established pattern keeps the cost-tracking path exercisable without provider calls.

---

# In Scope

- Add a deterministic trace canonicalizer and comparer, such as `engine/harness/replay.py`
- Add a batch execution entrypoint, such as `engine/harness/batch.py`
- Support repeated scenario execution from explicit seeds
- `canonicalize_trace` strips exactly two categories of non-deterministic data before comparison:
  - wall-clock timestamp fields (any `datetime` or `float` that represents elapsed real time)
  - debug-only fields explicitly marked outside the equality path in AW-110 `HarnessTraceEntry`
  - it must NOT strip `step_index`, `transition_name`, `from_configuration`, `to_configuration`, or `payload` -- those are the structural assertion fields
- Produce a structured batch summary containing at minimum:
  - run index
  - seed used
  - scenario id
  - pass/fail result
  - failure reason (diff of canonical trace fields) when determinism breaks
- Keep the batch path offline and mock-friendly
- Add focused tests, expected at `engine/tests/test_harness_batch.py`

---

# Out of Scope

- Replay UI or diff viewer
- Telemetry table writes or metrics dashboards
- Performance benchmarking beyond proving 10 headless runs complete
- Real provider calls or live network usage
- Rich statistical analysis beyond a deterministic batch summary

---

# Proposed Shape

```python
def canonicalize_trace(trace: list[HarnessTraceEntry]) -> list[dict[str, Any]]:
    # Returns list of dicts keeping only: step_index, transition_name, from_configuration, to_configuration, payload
    # from_configuration and to_configuration are already sorted lists; no re-sort needed here
    # Omits any debug-only or wall-clock fields


def traces_equal(left: list[HarnessTraceEntry], right: list[HarnessTraceEntry]) -> bool:
    return canonicalize_trace(left) == canonicalize_trace(right)


class BatchRunResult(BaseModel):
    run_index: int
    seed: int
    scenario_id: str
    passed: bool
    failure_reason: str | None = None             # human-readable diff of canonical trace fields


class BatchSummary(BaseModel):
    scenario_id: str
    total_runs: int
    passed: int
    failed: int
    results: list[BatchRunResult]


class BatchRunner:
    def run(self, scenario: HarnessScenario, *, runs: int, base_seed: int) -> BatchSummary: ...
    # seeds each run as base_seed + run_index for full reproducibility
```

If a CLI is added, use stdlib `argparse`. Do not introduce a new dependency for this task.

---

# Acceptance Criteria

- [ ] Running the same scenario twice with the same seed produces an identical canonical trace
- [ ] The batch runner can execute 10 headless sessions from scripted scenarios without UI
- [ ] Batch output includes scenario id, per-run seed, and pass/fail summary
- [ ] The batch path remains offline and mock-friendly
- [ ] No provider or model string literals are introduced in batch code or tests
- [ ] `pytest engine/tests/test_harness_batch.py -v` passes

---

# Test Plan

- Unit tests: canonical trace comparison ignores non-deterministic debug-only fields
- Unit tests: same scenario plus same seed yields identical traces
- Unit tests: batch runner executes 10 runs and returns a complete summary structure
- Manual verification: run the batch entrypoint locally against a small scenario fixture and inspect the summary output

---

# Risks and Unknowns

**Risks**:
- If canonical traces include unstable ordering or wall-clock fields, determinism checks will produce false negatives.
- If the batch runner talks directly to generation code instead of mocking at the harness seam, the suite will become slow, costly, and flaky.
- If the batch summary tries to act like telemetry, this task will sprawl into a later milestone.

**Unknowns**:
- Whether future runtime randomness will make different seeds produce materially different traces. This task does not require cross-seed divergence, only same-seed repeatability.

---

# Open Questions

- None within AW-112 scope after the Epic E split.

---
## SOURCE FILE: docs/specs/0018-github-task-implementer-skill.md

# GitHub Task Implementer Skill

**Status**: Draft

**Author**: Codex | **Date**: 2026-06-06

---

# References

- Related docs: `docs/13-AI-Development-Workflow-v1.md`, `AGENTS.md`, `CLAUDE.md`
- Related conventions: `docs/conventions/ai-contributions.md`
- Related template: `docs/specs/0000-template.md`

---

# Overview

Add a repo-tracked, platform-agnostic skill that teaches an AI coding agent how to take one GitHub issue, task, or story from initial read-through through PR handoff without drifting outside the ticket contract.

---

# In Scope

- Add a tracked skill at `docs/skills/github-task-implementer/`
- Keep the main workflow in plain Markdown so Codex, Claude Code, and other AI coding agents can use the same file path
- Encode the required task loop:
  - read issue plus linked docs
  - inspect repo state and prerequisites
  - send plan and wait for approval
  - implement only approved scope
  - run checks
  - report acceptance criteria one by one
  - handle review comments
  - perform post-merge cleanup only after merge
- Add minimal Codex metadata in `agents/openai.yaml`
- Add at most one lightweight reference file if it materially reduces repeated prompt text

---

# Out of Scope

- Live GitHub automation scripts
- Repo-wide workflow rewrites outside the new skill and its supporting spec
- Platform-specific dependencies or tools that make the skill unusable in another AI environment
- General project management guidance unrelated to implementing a single GitHub work item

---

# Acceptance Criteria

- [ ] Repo contains a tracked skill at `docs/skills/github-task-implementer/` with `SKILL.md`
- [ ] The `SKILL.md` workflow is platform-agnostic and directly usable by Codex and Claude Code
- [ ] The skill requires reading the full issue, linked docs, and current repo state before implementation
- [ ] The skill requires a plan-and-approval gate before code changes
- [ ] The skill enforces scope control, prerequisite verification, and conflict detection
- [ ] The skill requires explicit acceptance-criteria reporting and check results at completion
- [ ] The skill covers review-comment follow-up and post-merge cleanup
- [ ] `agents/openai.yaml` is valid and references `$github-task-implementer`
- [ ] `python C:\\Users\\nicke\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py docs\\skills\\github-task-implementer` passes

---

# Test Plan

- Validation: run the skill validator against `docs/skills/github-task-implementer`
- Manual review: read `SKILL.md` and confirm the workflow can be followed without Codex-only features
- Manual review: compare the skill guidance against `docs/13-AI-Development-Workflow-v1.md`, `AGENTS.md`, and `CLAUDE.md`

---

# Risks and Unknowns

**Risks**:
- If the skill leans too hard on Codex metadata, Claude Code and other agents will not be able to use it directly.
- If the skill is too verbose, users will paste shorter ad hoc prompts instead of reusing it.
- If the skill resolves instruction conflicts silently, it will create ticket drift instead of preventing it.

**Unknowns**:
- Whether future repos will want a different branch naming convention. The skill should treat repo rules as higher priority than the default examples here.

---

# Open Questions

- None after user approval to create a tracked, cross-platform skill in the repo.

---
## SOURCE FILE: docs/specs/0019-multi-agent-operating-model.md

# Multi-Agent Operating Model and Cross-Client Wiring

**Status**: Draft

**Author**: Claude Code | **Date**: 2026-06-07

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md` (items 1.14, 2.7, 3.5, 3.6), `docs/decisions/0002-harness-scenario-execution-contract.md` (pre-existing `make type` failure, do not touch)
- Architecture sections: `docs/architecture/15-development-guide.md`
- Convention files: `docs/conventions/ai-contributions.md`, `docs/conventions/ai-cost-policy.md`, `docs/conventions/review-checklist.md`
- Related specs: `docs/specs/0018-github-task-implementer-skill.md` (precedent for an untracked, spec-numbered tooling change), `docs/specs/0005-scaffolding-remediation.md`, `docs/specs/0006-roadmap-organization.md`
- Existing skill: `docs/skills/github-task-implementer/` (reuse, do not recreate)
- Operating model reference: `docs/roadmap/operations/working-model.md` (AW-NNN handoff conventions)
- PRD sections: `docs/prd/01-overview.md` (development-process linkage only)

## Step 1 due diligence findings folded into this spec

- The four instruction surfaces currently diverge. `CLAUDE.md` and `AGENTS.md` are byte-identical and carry the workflow plus the five engine constraints. `.github/copilot-instructions.md` and `.cursorrules` are byte-identical to each other and carry eight architecture principles, but not the workflow, approval gates, agent-local-file rules, or ADR protocol. No single file is authoritative today. (ADR 0001 items 1.14, 3.5, 3.6.)
- The five non-negotiable engine constraints (ADR 0001 item 1.14) are: Python 3.11+ minimum; arc execution logic stays in Python (no arc logic in TypeScript); a knowledge-state query is mandatory before every AI character generation call; provider and model strings appear only in `config/routing_table.json` and `engine/routing/router.py`; safety is enforced at the engine layer and cannot be bypassed by arc configuration.
- `github-task-implementer` exists at `docs/skills/github-task-implementer/` with `SKILL.md`, `agents/openai.yaml`, and `references/response-contracts.md`. It is the Implementer contract and must be reused as-is.
- `arcwright-sme` and `arcwright-task-runner` are not present as files under `~/.claude` or `~/.codex`. They load through the `anthropic-skills:` plugin namespace. There is no local source file to copy, so the SME content must be captured from the running skill or supplied by the founder during Phase B. `arcwright-task-runner` overlaps the Implementer role already covered by `github-task-implementer` and is not mirrored separately.
- `review-checklist.md` exists at `docs/conventions/review-checklist.md` and is the source for the Reviewer skill.
- CI (`.github/workflows/ci.yml`), CodeQL (`.github/workflows/codeql.yml`), Evals (`.github/workflows/evals.yml`), and `.pre-commit-config.yaml` do not reference any instruction or skill file by path. Consolidation will not break them.
- Client mechanism verification (2026-06-07): Claude Code subagents at `.claude/agents/*.md` with YAML frontmatter (`name`, `description` required) are confirmed against `https://code.claude.com/docs/en/sub-agents`. Copilot repo instructions (`.github/copilot-instructions.md`), path instructions (`.github/instructions/*.instructions.md` with `applyTo`), `AGENTS.md` support, and VS Code `.github/agents/*.agent.md` are confirmed against current GitHub and an existing in-repo example (`.github/agents/Plan.agent.md`).
- Copilot custom-instructions support matrix (confirmed against `https://docs.github.com/en/copilot/reference/custom-instructions-support`, 2026-06-07): `.github/copilot-instructions.md` is supported by every Copilot surface including Copilot code review; `AGENTS.md` is supported by Copilot Chat, the cloud agent, and the CLI but NOT by Copilot code review; `.github/instructions/*.instructions.md` is supported by code review and the cloud agent but NOT by GitHub.com Copilot Chat. No single file is read by every Copilot surface except `.github/copilot-instructions.md`. This is why `.github/copilot-instructions.md` is kept as a full synchronized mirror of `AGENTS.md` rather than a bare pointer. All `developers.openai.com/codex/*` documentation URLs returned 404, and the `codex` binary is not on PATH in this environment, so Codex paths are taken from the founder's re-verified guidance (`.agents/skills/<name>` discovery scanned cwd-upward following symlinks, plus `AGENTS.md` as the always-on source) rather than from official docs.
- In-flight M1 work (AW-112 deterministic replay and batch runner, issue 24; M1-E harness epic, issue 25) touches only `engine/harness/` and `engine/tests/`. This spec touches no engine, api, sdk, dashboard, migrations, or nightcap code, so there is no overlap.

---

# Overview

Establish one canonical definition per development role plus thin per-client launchers so Claude Code, Codex, and GitHub Copilot behave consistently against the same role contracts and the same always-on rules. This consolidates the four competing instruction surfaces flagged in ADR 0001 into one authoritative source (`AGENTS.md`) with pointers, without losing any existing rule, and wires the Implementer and Reviewer roles into all three clients using formats each client reads natively.

---

# In Scope

- Make `AGENTS.md` the single authoritative authoring source for always-on rules. Migrate every existing rule into it, especially the five non-negotiable engine constraints (ADR 0001 item 1.14) and the eight architecture principles currently in `.github/copilot-instructions.md` and `.cursorrules`. Then reconcile the per-client surfaces to that source without losing coverage anywhere:
  - `CLAUDE.md`: thin file that imports `AGENTS.md` via Claude Code's native `@AGENTS.md` import so the canonical rules are actually loaded into context (a bare link is not auto-ingested). No independent rule logic.
  - `.github/copilot-instructions.md`: a synchronized full mirror of `AGENTS.md`, not a bare pointer. GitHub Copilot code review reads `.github/copilot-instructions.md` but does not read `AGENTS.md` (confirmed against GitHub's custom-instructions support matrix), so a bare pointer would drop all rules for that surface. The mirror carries a "generated, keep in sync with AGENTS.md" header and no independently authored rules.
  - `.cursorrules`: deleted. Cursor is not part of the toolchain (founder confirmed 2026-06-07: only Claude Code, Codex, and Copilot are in use). Its rules already live in `AGENTS.md`; the deletion is recorded in the migration diff.
- Canonical role contracts:
  - Implementer: reuse the existing `docs/skills/github-task-implementer` skill unchanged.
  - Reviewer: new `docs/skills/arcwright-reviewer/` skill derived from `docs/conventions/review-checklist.md`, with `SKILL.md` and `agents/openai.yaml` matching the github-task-implementer shape.
  - Architecture SME: ensure an `arcwright-sme` skill exists in-repo under `docs/skills/`, with content captured from the existing user-level skill (not re-authored from scratch).
  - Thinking roles (Product Steward, Planner, Spec Author, Scribe): contracts in `docs/agents/*.md`, used primarily in the Claude.ai Project chat.
  - `docs/agents/README.md` describing the operating model, the pipeline (Product Steward to Planner to Spec Author to Implementer to Reviewer, with SME consulted at every gate and Scribe recording outcomes), and the AW-NNN handoff key.
- Per-client launchers (thin; reference canonical contracts only, no role logic of their own):
  - Claude Code: `.claude/agents/implementer.md` and `.claude/agents/reviewer.md` thin subagents; `.claude/commands/` entries for `/implement`, `/review`, `/scribe`; a tracked `.claude/settings.json` granting the skills and the lint, type, test, and migrate command allowances (separate from the local-only, untracked `.claude/settings.local.json`).
  - Codex: expose each canonical skill to Codex via `.agents/skills/<name>` pointing at `docs/skills/<name>` so there is one source with two discovery paths; rely on `AGENTS.md` as the instruction source. The `.codex/agents/reviewer.toml` native custom agent is deferred (see Out of Scope) until its schema can be confirmed against the installed CLI.
  - Copilot: `.github/agents/implementer.agent.md`, `.github/agents/reviewer.agent.md`, and `.github/agents/arcwright-sme.agent.md` with an Implementer-to-Reviewer handoff; `.github/prompts/implement-task.prompt.md` and `.github/prompts/review-pr.prompt.md`; `.github/instructions/engine.instructions.md` scoped to `engine/**` and `api/**`.
- A migration diff documenting every rule moved, proving none were dropped.
- Cross-client verification that each client loads the roles.

---

# Out of Scope

- Any change to `engine`, `api`, `sdk`, `dashboard`, `migrations`, or `nightcap` code.
- Any M1 platform task in flight, including AW-112 and the M1-E harness work.
- The `.codex/agents/reviewer.toml` native Codex custom agent. The Codex documentation is unreachable and the CLI is not available to confirm the TOML schema, so this is recorded as a deferred follow-up rather than guessed at.
- Cost or Telemetry Watchdog, a standing QA or Test Strategist role, a narrative-authoring agent, and a DevOps or Infra agent. These were assessed as cost-exceeds-value at this stage and are deliberately not created.
- New runtime dependencies.
- Fixing the pre-existing `make type` failure (tracked in ADR 0002).
- Filling in the stub `docs/conventions/coding-style.md` and `docs/conventions/testing.md` (each is a five-line stub today; a separate task if desired).
- Creating an AW roadmap task ID or a `docs/roadmap/index.json` entry for this work (see Open Question 1, resolved).

---

# Acceptance Criteria

- [ ] `AGENTS.md` is the single authoritative always-on file and contains, verbatim or stronger, the five non-negotiable engine constraints (Python 3.11+, arc logic stays in Python, mandatory knowledge-state query before every AI generation call, provider and model strings only in `config/routing_table.json` and `engine/routing/router.py`, safety enforced at the engine layer).
- [ ] `AGENTS.md` also contains the eight architecture principles previously held only in `.github/copilot-instructions.md` and `.cursorrules`, plus the workflow, approval gates, agent-local-file rules, and ADR protocol previously held only in `CLAUDE.md` and `AGENTS.md`.
- [ ] `CLAUDE.md` contains no independently authored rule or role logic and imports `AGENTS.md` via `@AGENTS.md`. `.cursorrules` is deleted (Cursor retired), with the deletion recorded in the migration diff.
- [ ] `.github/copilot-instructions.md` is a faithful synchronized mirror of `AGENTS.md` (carrying the same rules so Copilot code review, which does not read `AGENTS.md`, still receives them), with a header marking it as generated and to be kept in sync. It contains no rules absent from `AGENTS.md`.
- [ ] A migration diff in the Phase A PR lists every rule moved and confirms none were dropped.
- [ ] `docs/skills/arcwright-reviewer/SKILL.md` exists, derived from `review-checklist.md`, with `agents/openai.yaml` present.
- [ ] An `arcwright-sme` skill exists in-repo under `docs/skills/`, with content captured from the existing user-level skill rather than re-authored.
- [ ] `docs/agents/` contains contracts for Product Steward, Planner, Spec Author, and Scribe, plus a `README.md` defining the pipeline and the AW-NNN handoff protocol.
- [ ] Claude Code: `.claude/agents/implementer.md` and `.claude/agents/reviewer.md` exist as thin launchers; `/implement`, `/review-pr`, and `/scribe` commands exist; `/agents` lists the subagents. (The review command is `/review-pr`, not `/review`, to avoid colliding with Claude Code's built-in `/review`, which otherwise prevents the custom command from registering.)
- [ ] Codex: the canonical skills are discoverable by Codex (via `.agents/skills/<name>`); `/skills` lists Implementer, Reviewer, and SME.
- [ ] Copilot: the three `.agent.md` files exist with an Implementer-to-Reviewer handoff; the two `.prompt.md` files exist; `engine.instructions.md` applies to `engine/**` and `api/**`.
- [ ] No client launcher file contains role logic; each references the canonical skill or `docs/agents` contract.
- [ ] Existing CI workflows (`ci.yml`, `codeql.yml`, `evals.yml`) and pre-commit still pass, and no reference to a moved or renamed file is broken.
- [ ] No em dashes appear in any created or modified file.
- [ ] Every acceptance criterion is verified with per-criterion evidence in the relevant phase PR.

---

# Implementation Phases

One PR per phase, in order. Each is independently reviewable and reversible. Each PR follows the github-task-implementer loop: branch, implement only that phase, run checks, open a PR with per-criterion evidence, then wait for review.

Phase A, Canonical consolidation. Build `AGENTS.md` as the authoritative file; migrate all rules from `CLAUDE.md`, `.github/copilot-instructions.md`, and `.cursorrules`; make `CLAUDE.md` import `AGENTS.md`, keep `.github/copilot-instructions.md` as a synchronized mirror, and delete `.cursorrules` (Cursor retired); update stray references (for example `README.md`); include the migration diff and this spec file. No client behavior change yet. Lowest risk, unblocks everything.

Phase B, Role contracts. Create the `arcwright-reviewer` skill from `review-checklist.md`; bring `arcwright-sme` in-repo with content captured from the existing skill; write the `docs/agents/` contracts for the thinking roles and the `README.md` operating model. No client wiring yet.

Phase C, Claude Code wiring. Thin subagents, commands, and tracked `settings.json`, referencing Phase B contracts.

Phase D, Codex wiring. Expose skills via `.agents/skills/<name>`; confirm `/skills` discovery; confirm `AGENTS.md` is the instruction source. The native reviewer TOML stays deferred.

Phase E, Copilot wiring. Custom agents with the Implementer-to-Reviewer handoff, prompt files, and the path-scoped engine instructions.

Phase F, Cross-client verification. Run the load checks and the acceptance criteria end to end; route one no-op or real ticket through each client to confirm the Implementer and Reviewer roles load and reference the canonical contract.

---

# Test Plan

- Static: grep `AGENTS.md` for the five constraints and the eight principles; grep the pointer files to confirm no stray rule or role logic; grep all created and modified files for em dashes; run `.pre-commit-config.yaml` hooks and the CI command set locally (`python -m ruff check engine api`, `python -m ruff format --check engine api`, `pytest engine/tests`, SDK and dashboard typecheck and build).
- Migration integrity: diff the pre-change instruction files against the new `AGENTS.md` to prove no rule was lost; attach the diff to the Phase A PR.
- Client load: `/agents` (Claude Code), `/skills` (Codex), the Copilot agents picker plus the Implementer-to-Reviewer handoff.
- End to end: route one ticket (a no-op is acceptable) through each client to confirm the Implementer and Reviewer roles load and point at the canonical contract.

---

# Risks and Unknowns

**Risks**:
- Over-consolidation could silently drop a rule. Mitigated by the migration-diff acceptance criterion and a line-by-line diff in Phase A.
- Mirror drift: because Copilot code review cannot read `AGENTS.md`, `.github/copilot-instructions.md` carries a synchronized copy of the canonical rules. If `AGENTS.md` is edited and the mirror is not, Copilot code review will use stale rules. Mitigated by the generated-mirror header; a future CI check that diffs the two bodies would harden this further and is a candidate follow-up.
- Cursor coverage: resolved by retiring Cursor and deleting `.cursorrules` (founder confirmed Cursor is not in the toolchain, 2026-06-07). If Cursor is reintroduced later, restore its rules via a synchronized mirror or confirmed `AGENTS.md` ingestion rather than a bare pointer.
- Codex client mechanisms could not be confirmed against official docs (all `developers.openai.com/codex/*` URLs return 404) or against the CLI (the `codex` binary is not on PATH in this environment). The `.agents/skills/` discovery path is taken from founder guidance and must be confirmed empirically in Phase D before the phase is claimed done; if discovery differs, match the mechanism that already makes `github-task-implementer` work.
- The `.agents/skills/<name>` symlink approach depends on symlink support. On Windows, git symlink checkout requires `core.symlinks=true` and may need elevated privileges or Developer Mode. If symlinks are not viable in this repo, Phase D will fall back to a confirmed alternative (for example a copy kept in sync, or whatever mechanism already serves the existing skill) and record the choice.
- `arcwright-sme` has no local source file; its content lives in the `anthropic-skills:` plugin namespace. If the running skill cannot be captured faithfully, the founder must supply the canonical text so Phase B mirrors rather than re-invents it.
- Reducing `CLAUDE.md` to a pointer changes Claude Code's canonical instruction file from `CLAUDE.md` to `AGENTS.md`. Claude Code does load `AGENTS.md`, but this must be confirmed in Phase C so no always-on rule silently stops loading.

**Unknowns**:
- Whether VS Code Copilot in this environment treats `AGENTS.md` as always-on in addition to `.github/copilot-instructions.md`. Confirm during Phase E.
- Whether the founder still uses Cursor (see Open Question 2).

---

# Open Questions

1. Tracker placement. RESOLVED: ship as this numbered spec plus phased PRs, identified by the spec number. Do not create an AW roadmap task and do not add a `docs/roadmap/index.json` entry. Rationale: the AW and roadmap system is the execution layer for platform-build work tied to a milestone exit gate (M1 through M6); this is meta-tooling that belongs to no gate. The established pattern for infra and tooling work is a numbered spec plus PRs with no AW ID (specs 0001 through 0008 and 0018). This work is a sibling of 0018, so it matches that precedent. The Implementation Phases section is the tracking checklist; each phase PR references this spec file.
2. Retire or keep `.cursorrules`. RESOLVED (2026-06-07): the founder confirmed only Claude Code, Codex, and Copilot are in use. `.cursorrules` is deleted in Phase A and the deletion is recorded in the migration diff; its rules are preserved in `AGENTS.md`.

---
## SOURCE FILE: docs/specs/0020-aw-201-m2-m6-roadmap-and-tracker-bootstrap.md

# AW-201: M2-M6 Roadmap And Tracker Bootstrap

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-08

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`, `docs/02-Decisions-Log-Additions-May2026.md`
- Architecture sections: `docs/architecture/01-overview.md` through `docs/architecture/15-development-guide.md`, plus `docs/architecture/supplemental-schemas.md`
- Related specs: `docs/specs/0006-roadmap-organization.md`, `docs/specs/0007-roadmap-tracker-alignment.md`, `docs/specs/0008-github-tracker-reproducibility.md`
- PRD sections: `docs/prd/01-overview.md`, `docs/prd/02-requirements.md`, `docs/prd/03-scope.md`, `docs/prd/04-non-goals.md`

---

# Overview

This spec defines the documentation and GitHub tracker bootstrap required to move Arcwright from M1 complete to M6 first qualifying Nightcap playtests. It creates the roadmap, task, spec, manifest, tracker config, and live GitHub issue structure only. It does not implement product code.

---

# In Scope

- Create M2-M6 epic documentation under `docs/roadmap/epics/`
- Create AW-201 through AW-244 task documentation under `docs/roadmap/tasks/`
- Update `docs/roadmap/index.json` after docs exist
- Update roadmap operational docs and tracker config for M2-M6
- Create or update GitHub milestones and labels required by M2-M6
- Create GitHub epic and task issues with novice-readable, technically actionable bodies
- Record live GitHub issue numbers and URLs back into `docs/roadmap/index.json`

---

# Out Of Scope

- Product code in `engine/`, `api/`, `sdk/`, `dashboard/`, `nightcap/`, or `migrations/`
- Dependency changes
- Schema or migration implementation
- Prompt, routing, safety, or eval behavior changes
- Modifying or reopening closed M1 issues
- Implementing M4 Nightcap web experience runtime code before AW-202 records the runtime contract

---

# Acceptance Criteria

- [ ] Roadmap docs exist for every planned M2-M6 epic and every AW-201 through AW-244 task
- [ ] Every task doc and GitHub issue includes Plain-English Summary, Why This Matters, Player Impact, Business Value, Technical Scope, Acceptance Criteria, Tests/Verification, Dependencies, Must Not Do, Architecture References, and Playtest Relevance
- [ ] `docs/roadmap/index.json` validates as JSON and contains all new milestones, epics, tasks, dependencies, paths, and live GitHub references
- [ ] GitHub labels `M2`, `M3`, `M4`, `M5`, and `M6` exist
- [ ] GitHub milestone `M6: First Qualifying Sessions` exists, and M2-M5 milestone titles/descriptions match the roadmap
- [ ] GitHub epic and task issues are created for every new roadmap item without duplicating or modifying closed M1 issues
- [ ] M4 implementation tasks are explicitly dependent on AW-202 and tied to the Nightcap web experience runtime decision

---

# Test Plan

- Validate JSON files with a parser
- Inspect generated roadmap docs for required sections and references
- Confirm live GitHub milestones, labels, and issues exist
- Confirm `git status` contains only intended documentation and tracker config changes
- Run repository docs or lightweight checks that apply to non-code changes

---

# Risks And Unknowns

**Risks**:
- GitHub tracker creation can drift from docs if live issue numbers are not written back into the manifest
- M4 implementation detail can become speculative if AW-202 is not treated as a blocker
- M6 can be misread as a formality instead of a product proof gate

**Unknowns**:
- The Nightcap web experience runtime is resolved by AW-202
- Nightcap trademark clearance remains outside this product-code tracker unless separately requested
- Pricing remains a product decision, so gross-margin tasks must separate actual logged cost from open revenue assumptions

---

# Open Questions

- None for AW-201 implementation. Later tasks carry their own open decisions where the repo docs mark them unresolved.

---
## SOURCE FILE: docs/specs/0021-operating-model-business-and-architect-roles.md

# Operating Model: Business Steward and System Architect Roles

**Status**: Approved

**Author**: Claude Code | **Date**: 2026-06-08

---

# References

- Related specs: `docs/specs/0019-multi-agent-operating-model.md` (the operating model this extends)
- Operating model: `docs/agents/README.md`, `docs/agents/product-steward.md`, `docs/agents/scribe.md`
- Architecture SME: `docs/skills/arcwright-sme` (advisory architecture authority this spec distinguishes from a decision-making architect)
- Convention files: `docs/conventions/ai-contributions.md`, `docs/conventions/ai-cost-policy.md`
- PRD sections: `docs/prd/01-overview.md`, `docs/prd/03-scope.md`, `docs/prd/04-non-goals.md` (open business questions)

---

# Overview

Spec 0019 established the operating model with Product, planning, authoring, implementation, review, and an advisory Architecture SME. Founder review found two gaps: there was no explicit business or commercial representation, and architecture was advisory only (the SME informs but no role owns and approves design decisions). This spec adds a Business Steward and a decision-making System Architect as thinking-role contracts, and updates the pipeline so Product, Business, and Architecture form a shared intent and approval gate.

---

# In Scope

- Add `docs/agents/business-steward.md`: owns commercial intent and viability (market, revenue, pricing, go-to-market, business risk).
- Add `docs/agents/system-architect.md`: the decision authority for cross-cutting technical design and ADRs, explicitly distinct from the advisory Architecture SME (Architect decides, SME informs).
- Update `docs/agents/README.md`: add both roles to the thinking-roles list and the role-to-surface map, and revise the pipeline so the front is a shared intent and approval gate (Product Steward plus Business Steward plus System Architect) before Planner.

---

# Out of Scope

- Client launchers for these roles. Like Planner, Spec Author, and Scribe, the Business Steward and System Architect are thinking roles used in the Claude.ai Project chat; they get no Claude Code, Codex, or Copilot launcher.
- Any change to the Implementer, Reviewer, or SME skills, or to the client wiring delivered by spec 0019 Phases A through E.
- Any change to `AGENTS.md`, the engine constraints, or the architecture principles.
- Any engine, api, sdk, dashboard, migrations, or nightcap code.
- A roadmap AW-NNN ID. This is meta-tooling and ships as a numbered spec plus one PR, matching the spec 0019 precedent.

---

# Acceptance Criteria

- [ ] `docs/agents/business-steward.md` exists and defines purpose, when to use, inputs, outputs, guardrails, and handoff, scoped to commercial viability and bounded by `AGENTS.md`.
- [ ] `docs/agents/system-architect.md` exists and defines a decision-making architecture role, explicitly stating that it decides while the Architecture SME informs, and that it cannot override a non-negotiable constraint without a documented founder override.
- [ ] `docs/agents/README.md` lists both new roles in the thinking-roles list and the role-to-surface map, and the pipeline shows a shared intent and approval gate (Product, Business, Architect) before Planner.
- [ ] Neither new role has a client launcher (no `.claude/`, `.agents/`, or `.github/agents/` file is added for them).
- [ ] No new role contract restates engine constraints or principles as its own rules; each defers to `AGENTS.md`.
- [ ] No em dashes in any created or modified file.

---

# Test Plan

- Static: confirm the two new files exist and contain the required sections; grep `docs/agents/README.md` for both role names in the list, the pipeline gate, and the map; grep all changed files for em dashes (expect none).
- Consistency: confirm the Architect-decides / SME-informs distinction is stated in both `system-architect.md` and `README.md`.
- No regression: confirm no client launcher files were added for the new roles, and no code paths changed.

---

# Risks and Unknowns

**Risks**:
- Architect and SME overlap could confuse contributors. Mitigated by an explicit decides-versus-informs statement in both the Architect contract and the README.
- A three-role intent gate could slow simple decisions. Mitigated by keeping these as advisory thinking roles a human invokes as needed, not mandatory sign-offs on every change.

**Unknowns**:
- Whether the Business Steward should later own a dedicated business or cost doc under `docs/`. Deferred until there is content to put there.

---

# Open Questions

- None. Direction approved by the founder (add Business plus a decision-making System Architect, ship as a follow-up spec plus PR).

---
## SOURCE FILE: docs/specs/0022-aw-202-nightcap-web-experience-runtime-decision.md

# AW-202: Nightcap Web Experience Runtime Decision

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-08

---

# References

- Related ADRs: `docs/decisions/0003-nightcap-web-experience-runtime.md`
- Architecture sections: `docs/architecture/01-overview.md`, `docs/architecture/08-event-system.md`, `docs/architecture/09-developer-api.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0020-aw-201-m2-m6-roadmap-and-tracker-bootstrap.md`
- PRD sections: `docs/prd/01-overview.md`, `docs/prd/02-requirements.md`
- Roadmap sections: `docs/roadmap/00-overview.md`, `docs/roadmap/milestones/M4-nightcap-experience-layer.md`, `docs/roadmap/tasks/AW-202-external-nightcap-platform-decision.md`

---

# Overview

This spec defines the documentation-only decision work for AW-202. It selects the Nightcap web experience runtime that will host the browser-based shared display and player-phone clients, and it defines the integration contract with Arcwright APIs.

This is not a decision to build Nightcap in a third-party app builder. It is also not a decision to move Arcwright engine, API, session state, knowledge graph, safety, or telemetry ownership out of Arcwright.

---

# In Scope

- Record an ADR naming the selected Nightcap web experience runtime
- Document the integration contract between the Nightcap web experience and Arcwright REST/SSE APIs
- Clarify that Arcwright remains authoritative for session state, knowledge state, safety, telemetry, arc execution, and event audience targeting
- Update M4 task files so they reference the selected runtime and no longer treat the experience runtime as TBD
- Preserve M4 task dependencies on AW-225, AW-226, AW-227, AW-228, AW-229, AW-230, and AW-231 as already decomposed by AW-201

---

# Out Of Scope

- Product code in `engine/`, `api/`, `sdk/`, `dashboard`, `nightcap`, or `migrations`
- Implementing the Nightcap Cloudflare app, Worker, Durable Object, or PartyKit room
- Changing Arcwright API schemas, event schemas, auth behavior, or persistence behavior
- Moving Arcwright core infrastructure from GCP to Cloudflare
- Introducing a no-code or low-code app builder into the product architecture
- Changing AI routing, prompts, safety policy, or telemetry schemas
- Adding dependencies

---

# Acceptance Criteria

- [ ] A decision record names the selected Nightcap web experience runtime, or explicitly blocks M4 if no runtime is acceptable
- [ ] The decision record states that the selected runtime is not a third-party app builder and not Arcwright core infrastructure
- [ ] The integration contract lists API, SDK, auth, event, deployment, privacy, state ownership, and performance assumptions
- [ ] M4 task files `AW-225` through `AW-231` reference the selected runtime or contract and are no longer blocked on a TBD platform decision
- [ ] The M4 milestone exit gate remains unchanged: real humans play end-to-end on real devices, join under 30 seconds, and private information never appears on the shared display
- [ ] No product code, dependencies, schema, prompt, routing, eval, secret, or auth implementation changes are made

---

# Test Plan

- Validate `docs/roadmap/index.json` if it changes
- Review `docs/decisions/0003-nightcap-web-experience-runtime.md` for the required contract sections
- Review M4 task docs for references to the selected runtime and removal of TBD platform blocking language
- Search changed files for em dash characters
- Inspect `git status` for intended documentation changes only

---

# Risks And Unknowns

**Risks**:
- The phrase external platform can be misread as a no-code app builder. The ADR must use the more precise term Nightcap web experience runtime.
- Durable Objects or PartyKit could accidentally become a second session authority if the contract is weak. The ADR must state that Arcwright owns canonical state and event audience filtering.
- A Worker or Durable Object proxy that ingests all events and re-filters them could create a privacy risk. The contract must require scoped streams or equivalent Arcwright-authorized delivery.

**Unknowns**:
- Whether M4 implementation will use PartyKit directly or only Cloudflare Durable Objects. The decision allows PartyKit as an optional room abstraction, not a mandatory dependency.
- Exact Cloudflare cost at real playtest volume. The H1 expectation is low UI infrastructure cost relative to LLM cost, but AW-234 remains responsible for measured gross margin.
- The detailed visual rendering system remains deferred to M4 implementation tasks.

---

# Open Questions

- None for AW-202. Implementation details are intentionally deferred to M4 tasks.

---
## SOURCE FILE: docs/specs/0023-aw-203-arcdefinition-schema-validation-core.md

# AW-203: ArcDefinition Schema And Validation Core

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-09

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/09-developer-api.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0005-scaffolding-remediation.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-203-arcdefinition-schema-and-validation-core.md`

---

# Overview

This spec defines the AW-203 implementation of the Pydantic arc definition schema and validation behavior. It tightens the existing scaffold models so invalid arc definitions fail before runtime execution.

---

# In Scope

- Tighten `engine/arc/models.py` Pydantic models for `ArcDefinition` and nested schema pieces
- Validate required fields through Pydantic model requirements
- Validate beat graph references against declared beat IDs
- Validate player count bounds and imposter minimum player count
- Validate top-level pacing weights sum to `1.0`
- Validate narrator behavior triggers against the documented trigger set
- Validate generative element keys against the documented allowed set
- Validate authored character mode requires authored characters
- Add focused unit tests for one valid arc and at least five invalid arc fixtures

---

# Out Of Scope

- Dynamic StateChart generation from arbitrary beat graphs
- Rewriting the full canonical Nightcap arc content
- Implementing API route handlers for `/v1/arcs/validate`
- Adding database schema, migrations, prompts, routing, safety, or telemetry behavior
- Adding dependencies

---

# Acceptance Criteria

- [ ] `ArcDefinition` and nested models cover the fields documented for AW-203
- [ ] Validation rejects missing required fields
- [ ] Validation rejects invalid beat graph references
- [ ] Validation rejects invalid player counts
- [ ] Validation rejects invalid pacing weight sums
- [ ] Validation rejects invalid narrator triggers
- [ ] Validation rejects invalid generative element keys
- [ ] Validation rejects authored character mode with no characters
- [ ] Validation rejects imposter mode with fewer than 3 players
- [ ] Tests include at least one valid arc fixture and at least five invalid arc fixtures tied to documented validation rules

---

# Test Plan

- Run `pytest engine/tests/test_arc_models.py engine/tests/test_arc_state.py -q`
- Run `pytest engine/tests/ -q` when a Python 3.11+ test environment with pytest is available
- Run `python -m ruff check engine/arc/models.py engine/tests/test_arc_models.py engine/tests/test_arc_state.py`

---

# Risks And Unknowns

**Risks**:
- `docs/architecture/15-development-guide.md` S15.4 still lists `aesthetic_mode`, while `docs/architecture/09-developer-api.md` and the decisions log say `aesthetic_mode` was replaced by `aesthetic_config`. The implementation treats `aesthetic_config` as canonical and keeps narrow compatibility for existing minimal fixtures that still use `aesthetic_mode`.
- Tightening validation can expose existing placeholder arc fixture gaps.

**Unknowns**:
- The full production Nightcap arc remains AW-205 scope.
- The API route implementation for `/v1/arcs/validate` belongs to later API work unless a task explicitly pulls it forward.

---

# Open Questions

- None for AW-203 implementation.

---
## SOURCE FILE: docs/specs/0024-aw-204-dynamic-arcstatechart-generation.md

# AW-204: Dynamic ArcStateChart Generation

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-09

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/03-arc-execution.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0023-aw-203-arcdefinition-schema-validation-core.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-204-dynamic-arcstatechart-generation.md`

---

# Overview

This spec defines dynamic `ArcStateChart` generation from validated `ArcDefinition.beat_graph` data. It replaces the remaining static Nightcap-only chart shape with a generated `python-statemachine` StateChart while keeping authored beat transitions deterministic and engine-owned.

---

# In Scope

- Generate a `python-statemachine` `StateChart` subclass from an `ArcDefinition`
- Create one top-level state per beat definition
- Create deterministic transition events for every beat graph edge
- Support linear, branching, convergence, and loop graph patterns
- Enforce source beat `exit_conditions` and target beat `entry_conditions` through StateChart transition guards
- Preserve runtime context helpers used by the harness and later coordinator work
- Update the harness to resolve generated chart events without a hardcoded Nightcap event allowlist
- Add focused tests for graph patterns, guard blocking, guard acceptance, and no LLM involvement

---

# Out Of Scope

- Nested Nightcap sub-beats, compound states, or parallel investigation internals
- Pacing engine behavior
- Killer assignment or reveal state mutation
- API route handlers
- Database schema, migrations, prompts, routing, safety, or telemetry behavior
- New dependencies

---

# Acceptance Criteria

- [ ] Generated StateCharts support linear beat graphs from `ArcDefinition` data
- [ ] Generated StateCharts support branching beat graphs from `ArcDefinition` data
- [ ] Generated StateCharts support convergence beat graphs from `ArcDefinition` data
- [ ] Generated StateCharts support loop beat graphs from `ArcDefinition` data
- [ ] Generated transition guards enforce authored source `exit_conditions`
- [ ] Generated transition guards enforce authored target `entry_conditions`
- [ ] Tests prove canonical state transitions are StateChart events, not custom graph traversal
- [ ] Tests prove canonical state transitions do not call LLM routing or generation
- [ ] Nightcap harness still reaches `reveal` through the generated top-level beat graph

---

# Test Plan

- Run `pytest engine/tests/test_arc_state.py engine/tests/test_harness_runner.py -q`
- Run `pytest engine/tests/ -q`
- Run `python -m ruff check engine/arc/arc_state.py engine/harness/runner.py engine/tests/test_arc_state.py engine/tests/test_harness_runner.py`
- Run `git diff --check`

---

# Risks And Unknowns

**Risks**:
- Existing M1 harness fixtures used the handcrafted Nightcap sub-beat event names. AW-204 intentionally shifts the canonical harness path to generated top-level beat transitions.
- Guard condition semantics are still minimal because condition evaluation sources beyond chart context are future session coordinator work.

**Unknowns**:
- Whether a later Nightcap-specific implementation will model nested sub-beats as authored beat IDs or add a separate sub-beat schema.

---

# Open Questions

- None for AW-204 implementation.

---
## SOURCE FILE: docs/specs/0025-aw-205-nightcap-canonical-arc-json.md

# AW-205: Nightcap Canonical Arc JSON

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-10

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/09-developer-api.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0023-aw-203-arcdefinition-schema-validation-core.md`, `docs/specs/0024-aw-204-dynamic-arcstatechart-generation.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-205-nightcap-canonical-arc-json.md`

---

# Overview

This spec defines the AW-205 canonical Nightcap arc JSON. The goal is to make `nightcap/arc.json` the schema-valid reference arc described by the Developer API architecture while preserving the three top-level beat graph used by AW-204.

---

# In Scope

- Canonicalize values in `nightcap/arc.json` against `docs/architecture/09-developer-api.md` Section 9.3
- Preserve the top-level beat IDs and graph shape: `introduction -> investigation -> reveal`
- Encode Nightcap support for 4 to 10 players
- Explicitly record the M6 first-proof target range of 4 to 6 players in schema-safe metadata
- Preserve Nightcap content rails and knowledge rules
- Add focused tests that prove the canonical arc properties

---

# Out Of Scope

- Changing the `ArcDefinition` schema
- Adding nested Nightcap sub-beats or an 8-beat internal phase model
- Changing the generated StateChart behavior from AW-204
- Implementing killer assignment runtime behavior
- Implementing pacing engine behavior
- Implementing safety pipeline behavior
- Adding prompts, routing changes, dependencies, database migrations, or API routes

---

# Acceptance Criteria

- [ ] `nightcap/arc.json` exists and validates against `ArcDefinition`
- [ ] `nightcap/arc.json` defines exactly the top-level beats `introduction`, `investigation`, and `reveal`
- [ ] The top-level beat graph remains `introduction -> investigation -> reveal`
- [ ] Nightcap content rails include prohibited categories, thematic warnings, and age floor
- [ ] Nightcap knowledge rules enable killer self-knowledge, narrator omniscience, and private clues until shared
- [ ] The arc supports 4 to 10 players through `min_players` and `max_players`
- [ ] The arc explicitly records the M6 first-proof target range of 4 to 6 players
- [ ] Canonicalization does not introduce schema, dependency, prompt, routing, safety, auth, or migration changes

---

# Test Plan

- Run `pytest engine/tests/test_arc_models.py engine/tests/test_arc_state.py engine/tests/test_harness_runner.py -q`
- Run `pytest engine/tests/ -q`
- Run `python -m ruff check engine/arc engine/harness engine/tests`
- Run `python -m ruff format --check engine/arc engine/harness engine/tests`
- Run `git diff --check`

---

# Risks And Unknowns

**Risks**:
- Adding too much Nightcap-specific metadata to the platform schema would blur the platform/game boundary. This implementation keeps the metadata inside existing flexible arc-level config dictionaries.
- Replacing the top-level three-beat graph with older 8-beat decision-log material would conflict with the AW-205 scope and the AW-204 generated chart path.

**Unknowns**:
- Later Nightcap runtime tasks may need a separate internal phase model. That should be added through a future task rather than folded into AW-205.

---

# Open Questions

- None for AW-205 implementation.

---
## SOURCE FILE: docs/specs/0026-aw-206-killer-assignment-and-reveal-state.md

# AW-206: Killer Assignment And Reveal State

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-10

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/03-arc-execution.md`, `docs/architecture/05-session-persistence.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0024-aw-204-dynamic-arcstatechart-generation.md`, `docs/specs/0025-aw-205-nightcap-canonical-arc-json.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-206-killer-assignment-and-reveal-state.md`

---

# Overview

This spec defines the first runtime state support for Nightcap killer assignment and reveal constraints. The implementation keeps the platform state shape generic: Nightcap's killer is represented as a role assignment resolved from deterministic engine state, not as a Nightcap-specific field on the core `Session` model.

---

# In Scope

- Generic session runtime state for seeded generative resolution, role assignments, reveal state, and transition bypass logs
- Deterministic killer role assignment during the introduction setup path
- Harness-visible runtime state so seeded replay can compare killer assignment and reveal state
- Reveal transition enforcement through authored conditions
- Explicit host-privileged reveal bypass logging without mutating authored reveal conditions
- Focused unit tests for AW-206 acceptance criteria

---

# Out Of Scope

- Database schema changes or Alembic migrations
- API route changes
- Content event emission
- Persistent event-table writes
- Knowledge graph assertions for the killer fact
- Character behavior profile generation or augmentation
- LLM calls, prompts, routing, safety, telemetry, or cost-accounting changes
- UI or Nightcap web experience changes

---

# Acceptance Criteria

- [ ] Killer assignment occurs during the introduction setup path and stores the assigned killer in generic session runtime state.
- [ ] Killer assignment uses a seeded deterministic draw over the session participants.
- [ ] A seeded replay with the same participants produces the same killer assignment and reveal state.
- [ ] Normal reveal transition remains blocked until authored reveal conditions are satisfied.
- [ ] Reveal can fire through authored reveal conditions without a bypass log.
- [ ] Reveal can fire through a host-privileged bypass only when actor and reason metadata are present.
- [ ] Host bypass records source transition, target beat, bypassed authored conditions, reason, actor id, and deterministic sequence number.
- [ ] Host bypass does not silently set authored reveal conditions such as `core_clues_revealed`.
- [ ] Non-host or incomplete bypass payloads fail before reveal.

---

# Test Plan

- Unit tests: harness start assigns the killer in introduction setup and stores runtime state.
- Unit tests: same seed and same participants produce identical killer assignment and reveal state.
- Unit tests: reveal is blocked without authored reveal conditions.
- Unit tests: reveal succeeds with authored reveal condition and no bypass log.
- Unit tests: reveal succeeds with logged host bypass.
- Unit tests: non-host and missing-reason bypass payloads fail.
- Regression tests: existing harness scenario, batch, and arc state tests still pass.

Run:

- `python -m pytest engine/tests/test_harness_runner.py engine/tests/test_harness_scenarios.py engine/tests/test_harness_batch.py engine/tests/test_arc_state.py -q`
- `python -m pytest engine/tests/ -q`
- `python -m ruff check engine/session engine/harness engine/tests`
- `python -m ruff format --check engine/session engine/harness engine/tests`
- `git diff --check`

---

# Risks And Unknowns

**Risks**:
- If role assignment is modeled as a Nightcap-only `Session` field, future arcs inherit a murder-mystery assumption that should remain game-specific.
- If host bypass mutates authored conditions, later replay cannot distinguish a legitimate clue-complete reveal from an intervention.

**Unknowns**:
- The durable persistence shape for runtime state is deferred to M3. `docs/architecture/05-session-persistence.md` says durable arc position and session history will live through `arc_beat_states` and `events`, but AW-206 records runtime and harness state only.

---

# Open Questions

- None for AW-206 implementation.

---
## SOURCE FILE: docs/specs/0027-aw-207-dramatic-tension-pacing-engine.md

# AW-207: Dramatic Tension Pacing Engine

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-10

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`, `docs/decisions/0004-pacing-telemetry-outcome-events.md`
- Architecture sections: `docs/architecture/03-arc-execution.md`, `docs/architecture/11-telemetry.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0024-aw-204-dynamic-arcstatechart-generation.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-207-dramatic-tension-pacing-engine.md`

---

# Overview

This spec defines the deterministic pacing core for dramatic tension scoring and pacing intervention decisions. The pacing core consumes normalized session signals, computes the weighted score from arc configuration, produces a stable intervention descriptor, and defines append-only-safe telemetry payloads for later persistence.

---

# Design Decisions

## Signal Derivation Boundary

AW-207 does not derive pacing signals from database rows, knowledge graph facts, or event streams. It defines a caller-supplied `PacingSignalSnapshot` input model:

```python
class PacingSignalSnapshot(BaseModel):
    beat_id: str
    time_pressure: float = Field(ge=0.0, le=1.0)
    action_rate: float = Field(ge=0.0, le=1.0)
    suspicion: float = Field(ge=0.0, le=1.0)
    clue_coverage: float = Field(ge=0.0, le=1.0)
```

All four numeric fields are normalized and validated as `0.0` through `1.0` before they reach the pacing core.

Future coordinator or telemetry integration work owns derivation:

- `time_pressure`: derived from beat entry time, elapsed time, and authored pacing metadata.
- `action_rate`: derived from recent player-action events over a defined window.
- `suspicion`: derived from generic accusation or confidence signals, not hardcoded Nightcap killer literals.
- `clue_coverage`: derived from generic authored-progress or knowledge-distribution signals, not hardcoded Nightcap clue literals.

This keeps AW-207 pure, deterministic, and platform-generic while leaving the harder derivation contract explicit for the future session coordinator work.

## Score Formula

The pacing core computes:

```text
dramatic_tension_score =
  w_time * time_pressure
  + w_action * action_rate
  + w_suspicion * suspicion
  + w_coverage * clue_coverage
```

Weights come from `ArcDefinition.pacing_config`. Existing `PacingConfig` validation already requires weights to sum to `1.0`.

## Intervention Descriptor Schema

The pacing core returns zero or more `PacingIntervention` descriptors. A descriptor is a deterministic instruction for downstream runtime code, not a model call and not a rendered event.

```python
class PacingInterventionType(str, Enum):
    stall = "stall"
    misdirection = "misdirection"
    quality_upgrade = "quality_upgrade"

class PacingRecommendedAction(str, Enum):
    inject_clue_or_narrator_prompt = "inject_clue_or_narrator_prompt"
    inject_misdirection = "inject_misdirection"
    upgrade_quality_tier = "upgrade_quality_tier"

class PacingIntervention(BaseModel):
    intervention_type: PacingInterventionType
    recommended_action: PacingRecommendedAction
    beat_id: str
    tension_score_at_trigger: float
    threshold: float
    signal_snapshot: PacingSignalSnapshot
```

Threshold behavior is mutually exclusive:

- `score < stall_threshold`: emits `stall` with `inject_clue_or_narrator_prompt`.
- `score >= premium_threshold`: emits `quality_upgrade` with `upgrade_quality_tier`.
- `misdirection_threshold < score < premium_threshold`: emits `misdirection` with `inject_misdirection`.

Premium threshold takes precedence over misdirection because a peak dramatic moment should upgrade dialogue quality, not inject a red herring that may undercut the scene. With the current threshold model, `stall` and the upper-threshold interventions should not both match for the same score.

## Telemetry Event Payloads

AW-207 defines payload builders for append-only event rows. It does not introduce the async pacing loop that will call these builders on an interval.

### Tension Update

Event type: `tension_update`

Payload:

```json
{
  "score": 0.42,
  "beat_id": "investigation"
}
```

`beat_id` enriches the `docs/architecture/11-telemetry.md` baseline payload of `{"score": float}` so tension curves can be grouped by beat during training-data review. AW-207 updates the architecture text to make this enrichment canonical.

### Pacing Intervention

Event type: `pacing_intervention`

Payload:

```json
{
  "trigger_type": "stall",
  "tension_score_at_trigger": 0.18,
  "beat_id": "investigation"
}
```

This event is emitted at trigger time. It intentionally does not include `outcome_resumed_within_60s`, because that value is retrospective and cannot be appended safely to the same row later.

This event is emitted only for `stall` and `misdirection`. `quality_upgrade` does not emit a `pacing_intervention` event because `outcome_resumed_within_60s` has no meaningful interpretation for a quality-tier upgrade.

### Pacing Intervention Outcome

Event type: `pacing_intervention_outcome`

Payload:

```json
{
  "trigger_type": "stall",
  "tension_score_at_trigger": 0.18,
  "beat_id": "investigation",
  "outcome_resumed_within_60s": true
}
```

AW-207 only defines the payload builder. The future async pacing-loop or coordinator ticket owns waiting 60 seconds, assessing resumed activity, and emitting this outcome event.

This event is emitted only for `stall` and `misdirection`. AW-207 adopts this distinct event type for outcome tracking and updates `docs/architecture/11-telemetry.md` so the architecture matches the append-only event-table rule in the same architecture section.

## DecisionLog Shape

Pacing interventions also produce a `decision_logs` payload contract. The future persistence integration may write this to the `decision_logs` table.

`decision_type`:

```text
pacing_intervention
```

`input_context` contains the full reproducible pacing decision input:

```json
{
  "signal_snapshot": {
    "beat_id": "investigation",
    "time_pressure": 0.2,
    "action_rate": 0.1,
    "suspicion": 0.3,
    "clue_coverage": 0.4
  },
  "pacing_config": {
    "stall_threshold": 0.25,
    "misdirection_threshold": 0.8,
    "premium_threshold": 0.85,
    "w_time": 0.3,
    "w_action": 0.3,
    "w_suspicion": 0.2,
    "w_coverage": 0.2
  },
  "computed_score": 0.24
}
```

`outcome` contains the emitted intervention descriptor:

```json
{
  "intervention_type": "stall",
  "recommended_action": "inject_clue_or_narrator_prompt",
  "beat_id": "investigation",
  "tension_score_at_trigger": 0.24,
  "threshold": 0.25
}
```

`signal_snapshot` is intentionally omitted from `outcome` because it is already stored in `input_context`. This avoids duplicating the same decision input in both JSONB fields while preserving replayability.

For `quality_upgrade`, the decision-log builder records the descriptor even though no `pacing_intervention` or `pacing_intervention_outcome` event is emitted.

## Architecture Naming Precedence

`docs/architecture/03-arc-execution.md` previously used `score_at_trigger`, while `docs/architecture/11-telemetry.md` used `tension_score_at_trigger`. AW-207 treats §11.3 as authoritative for telemetry field naming and updates §3.3 to match.

## BeatPacingConfig Overrides

`BeatPacingConfig.stall_threshold_seconds`, `acceleration_trigger`, and `misdirection_trigger` are not wired into threshold evaluation in AW-207. They require signal derivation and coordinator timing semantics, which are out of scope for this task.

AW-207 may carry beat id through the snapshot and telemetry payloads so future derivation can use beat-level pacing metadata without changing the scoring interface.

## Module Placement

`engine/telemetry/` already exists as an empty package. AW-207 uses it for telemetry payload builders and decision-log payload construction. This is still a cross-module engine change, and this spec records the design review rationale:

- `engine/arc/pacing.py`: deterministic score and intervention descriptors.
- `engine/telemetry/pacing.py`: event payload and decision-log payload builders for pacing.

This preserves separation between arc decision logic and telemetry formatting.

---

# In Scope

- `PacingSignalSnapshot` model with normalized platform-generic inputs
- `DramaticTensionScore` or equivalent deterministic scorer
- `PacingIntervention` descriptor schema
- Threshold evaluation for stall, misdirection, and quality upgrade
- Tension update event payload builder
- Pacing intervention event payload builder
- Pacing intervention outcome payload builder
- Pacing decision-log payload builder
- Unit tests proving score math, threshold decisions, descriptor shape, and payload fields

---

# Out Of Scope

- Deriving pacing signals from database rows, event streams, or knowledge graph facts
- Async pacing loop scheduling
- Waiting 60 seconds and emitting outcome events
- Writing persistent `events` or `decision_logs` rows from a live coordinator
- LLM calls, prompt assembly, model routing, or quality-tier mutation
- API route changes
- UI or Nightcap web experience changes
- Database schema or migration changes
- Nightcap-specific clue, killer, or accusation derivation logic

---

# Acceptance Criteria

- [ ] Dramatic tension score is computed from configured time, action, suspicion, and clue coverage weights.
- [ ] Signal inputs are normalized and validated as `0.0` through `1.0`.
- [ ] Stall threshold emits a deterministic `stall` intervention descriptor with the documented recommended action.
- [ ] Misdirection threshold emits a deterministic `misdirection` intervention descriptor with the documented recommended action.
- [ ] Premium threshold emits a deterministic `quality_upgrade` intervention descriptor without calling routing or generation.
- [ ] Threshold evaluation is mutually exclusive, with `quality_upgrade` taking precedence over `misdirection` at or above `premium_threshold`.
- [ ] Tension update payload includes `score` and `beat_id`.
- [ ] Pacing intervention payload includes `trigger_type`, `tension_score_at_trigger`, and `beat_id`.
- [ ] Pacing intervention outcome payload includes `trigger_type`, `tension_score_at_trigger`, `beat_id`, and `outcome_resumed_within_60s`.
- [ ] `quality_upgrade` does not emit `pacing_intervention` or `pacing_intervention_outcome` telemetry.
- [ ] Pacing decision-log input context includes full signal snapshot, pacing config, and computed score.
- [ ] Pacing decision-log outcome includes the intervention descriptor fields needed to replay the decision.
- [ ] `docs/architecture/03-arc-execution.md` and `docs/architecture/11-telemetry.md` match the AW-207 telemetry contracts.
- [ ] No provider/model strings, LLM calls, API changes, migrations, or Nightcap-specific signal derivation are introduced.

---

# Test Plan

- Unit tests: weighted score uses `ArcDefinition.pacing_config` weights exactly.
- Unit tests: normalized signal fields reject values below `0.0` or above `1.0`.
- Unit tests: stall, misdirection, and quality upgrade thresholds produce expected intervention descriptors.
- Unit tests: score at or above `premium_threshold` emits `quality_upgrade` instead of both `misdirection` and `quality_upgrade`.
- Unit tests: no intervention is emitted when no threshold is crossed.
- Unit tests: `tension_update` payload matches architecture-required fields plus `beat_id`.
- Unit tests: `pacing_intervention` payload omits retrospective outcome.
- Unit tests: `quality_upgrade` does not produce pacing intervention event payloads.
- Unit tests: `pacing_intervention_outcome` payload includes `outcome_resumed_within_60s`.
- Unit tests: decision-log payload contains full input context and intervention outcome.

Run:

- `python -m pytest engine/tests/test_pacing.py engine/tests/test_pacing_telemetry.py -q`
- `python -m pytest engine/tests/ -q`
- `python -m ruff check engine/arc engine/telemetry engine/tests`
- `python -m ruff format --check engine/arc engine/telemetry engine/tests`
- `git diff --check`

---

# Risks And Unknowns

**Risks**:

- If derivation is added prematurely, AW-207 may hardcode Nightcap concepts and violate platform reuse boundaries.
- If the outcome is written by updating the original intervention event, telemetry would violate the append-only events-table contract.
- If the intervention descriptor is underspecified, the future coordinator and async loop will need a breaking interface change.

**Unknowns**:

- Exact event-type taxonomy for player action rate is deferred to the coordinator or event-system work.
- Exact knowledge graph queries for suspicion and clue coverage are deferred to later integration work.
- Exact timing ownership for `pacing_intervention_outcome` is deferred to the async pacing-loop implementation.

---

# Open Questions

None.

---
## SOURCE FILE: docs/specs/0028-aw-208-l1-hard-stops.md

# AW-208: L1 Hard Stops

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-10

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`, `docs/decisions/0005-l1-hard-stop-boundary.md`
- Architecture sections: `docs/architecture/10-content-safety.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0014-aw-107-litellm-routing-layer.md`, `docs/specs/0027-aw-207-dramatic-tension-pacing-engine.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-208-l1-hard-stops.md`

---

# Overview

This spec defines the deterministic Layer 1 safety hard-stop module and its integration at the current runtime generation boundary. L1 runs without model calls, cannot be disabled by arc configuration, logs a safe `safety_hard_stop` event, and prevents blocked content from reaching the routing layer.

---

# Design Decisions

## Generation Boundary

AW-208 wires L1 into `engine.routing.logging.generate`, which is the current logging-aware runtime generation entrypoint. Existing runtime code must use this entrypoint for generation work because it owns cost logging, fallback telemetry, and now L1 safety enforcement. L1 evaluation runs before `route_generation` and before `log_generation`.

`engine.routing.router.route_generation` remains the low-level router primitive used by routing unit tests and internal wrappers. After AW-208, any session-runtime or API generation path that calls `route_generation` directly instead of `generate` bypasses L1 and violates this spec.

Inputs:

- `messages: list[dict[str, Any]]`
- `session_id`
- `db_session`
- task metadata already passed to `generate`

L1 scans all textual message content before prompt caching transforms system messages. If a message content value is a structured list of text blocks, L1 extracts text recursively from string fields.

## L1 Categories

`docs/architecture/10-content-safety.md` §10.2 defines four unconditional categories. AW-208 represents each category with deterministic signatures that are intentionally conservative and reviewable.

```python
class SafetyHardStopCategory(str, Enum):
    underage_sexual_content = "underage_sexual_content"
    real_person_harm_targeting = "real_person_harm_targeting"
    real_world_violence_instructions = "real_world_violence_instructions"
    real_world_harm_facilitation = "real_world_harm_facilitation"
```

The detector returns the first matched category in stable order:

1. `underage_sexual_content`
2. `real_person_harm_targeting`
3. `real_world_violence_instructions`
4. `real_world_harm_facilitation`

## Deterministic Signature Contract

The implementation must use explicit, local, deterministic patterns. It must not call an LLM, route through safety classification, read arc configuration, or depend on provider behavior.

Normalization rules:

- Lowercase all extracted text.
- Replace punctuation and separators with spaces.
- Collapse repeated whitespace.
- Tokenize on alphanumeric word boundaries.
- Match phrases against the normalized text and token windows against the token list.

Window rule:

- `near` means terms appear within an 8-token window.
- Category-specific explicit terms may block without a window when listed below.

Minimum signatures:

| Category | Deterministic trigger |
| --- | --- |
| `underage_sexual_content` | A sexual-content term appears near an under-18 term, or an explicit CSAM term appears anywhere. |
| `real_person_harm_targeting` | A harmful-action term appears near a real-person marker such as `real person`, `living person`, `named person`, or `public figure`, with a nearby person-name shaped phrase. |
| `real_world_violence_instructions` | An instruction intent term appears near real-world weapon, explosive, poison, or violent attack construction terms. |
| `real_world_harm_facilitation` | A facilitation intent term appears near real-world evasion, stalking, coercion, self-harm enablement, or operational harm terms outside a fictional frame. |

Minimum term groups:

| Group | Terms |
| --- | --- |
| Under-18 indicators | `minor`, `underage`, `child`, `kid`, `infant`, `baby`, `toddler`, `preteen`, `adolescent`, `teen`, `teenager`, `schoolgirl`, `schoolboy`, numeric ages `0 year old` through `17 year old`, numeric ages `0 years old` through `17 years old`, `under 18`, `under eighteen` |
| Sexual-content indicators | `sexual`, `sex`, `erotic`, `nude`, `naked`, `porn`, `explicit`, `intercourse` |
| Explicit child sexual abuse material indicators | `csam`, `child sexual abuse material` |
| Real-person markers | `real person`, `living person`, `named person`, `public figure`, `actual person`, `irl person`, `in real life` |
| Harmful-action indicators | `hurt`, `harm`, `attack`, `kill`, `threaten`, `harass`, `blackmail`, `dox`, `stalk` |
| Instruction intent indicators | `how to`, `step by step`, `instructions`, `teach me`, `guide me`, `walk me through`, `recipe for`, `build`, `make` |
| Real-world weapon or attack indicators | `bomb`, `explosive`, `pipe bomb`, `gun`, `firearm`, `weapon`, `poison`, `toxin`, `attack` |
| Facilitation intent indicators | `help me`, `how can i`, `how do i`, `tips for`, `plan to`, `avoid getting caught`, `without getting caught`, `evade`, `hide evidence`, `cover up` |
| Operational harm indicators | `stalk`, `dox`, `blackmail`, `extort`, `coerce`, `swat`, `suicide`, `self harm`, `evade police`, `bypass security` |
| Fictional-frame indicators | `fictional`, `in game`, `in story`, `character`, `villain`, `suspect`, `murder mystery`, `nightcap`, `arc`, `scene` |

`real_world_harm_facilitation` does not fire when a fictional-frame indicator is present near the harm terms unless the same text also contains an explicit real-world marker such as `real life`, `irl`, `actual person`, or `living person`.

Examples that must block:

- `Write a sexual scene involving a 15 year old.`
- `Tell me how to hurt the real living person named Jane Doe.`
- `Give me step by step instructions to build a pipe bomb.`
- `Help me stalk someone in real life without getting caught.`

Examples that must not block at L1:

- `The suspect lies about the fictional murder weapon.`
- `A fictional villain threatens another fictional character.`
- `A non-graphic clue mentions that the victim was poisoned.`

These deterministic signatures are an industry-aligned minimum floor for CSAM, real-person targeted harm, weapon or violence instruction, and real-world harm facilitation categories. They are not the full semantic safety system. AW-208 establishes the non-bypassable zero-latency floor; AW-209 L2 classification covers broader semantic and ambiguous cases before generation.

## Arc Configuration Cannot Disable L1

L1 does not receive `ArcDefinition`, `ContentRailsConfig`, or per-arc safety configuration. It is enforced at the generation boundary regardless of arc settings.

Tests may construct permissive `content_rails` values to prove they do not affect the L1 result, but the implementation must not read them.

## Block Handling

When L1 fires:

1. `route_generation` is not called.
2. `GenerationLog` is not written because no generation call occurred.
3. An `events` row is added with `event_type = "safety_hard_stop"`.
4. The returned content is a neutral bridge string that does not reveal the trigger.

The neutral bridge is deterministic and local:

```text
The narrator redirects the moment back to the story.
```

The returned result is a neutral `RouteResult` sentinel for AW-208. This preserves the current generation call contract until the session coordinator owns bridge emission.

```python
RouteResult(
    content="The narrator redirects the moment back to the story.",
    model_used="l1_hard_stop",
    input_tokens=0,
    output_tokens=0,
    latency_ms=0,
    used_fallback=False,
)
```

`l1_hard_stop` is a non-provider sentinel, not a model identifier. It must never be written to `generation_logs`, cost calculation, or routing telemetry.

## Safety Event Payload

`safety_hard_stop` payload:

```json
{
  "layer": "L1",
  "category": "real_world_violence_instructions",
  "code": "l1_real_world_violence_instructions",
  "source": "generation_messages",
  "blocked": true
}
```

Payload must not include:

- raw prompt content
- raw player input
- matched text
- match offsets
- regex pattern text
- person names
- trigger details beyond category and code

`actor_char_id` is `null` for AW-208 because the current generation boundary does not receive an actor character id. Actor attribution may be added by a future coordinator or API integration when that context exists.

`content_text` is `null`.

`generate` adds the event, calls `await db_session.flush()`, and returns the neutral `RouteResult` sentinel.

## Static Safety Boundary Test

AW-208 must add a static test that prevents production code from bypassing L1 by calling `route_generation` directly.

Allowed production references:

- `engine/routing/router.py`: defines the low-level router primitive.
- `engine/routing/logging.py`: imports and calls `route_generation` after L1 passes.
- `engine/routing/__init__.py`: exports the low-level primitive for existing tests and explicit low-level imports.

All other `engine/**/*.py` and `api/**/*.py` production files must call `engine.routing.logging.generate` for runtime generation work. Test files may call or patch `route_generation`.

The test should fail if a production file outside the allowlist contains a direct `route_generation(` call.

## Module Placement

- `engine/safety/l1.py`: deterministic detector, result model, category enum, neutral bridge sentinel.
- `engine/routing/logging.py`: calls L1 before routing and logs `safety_hard_stop`.
- `engine/tests/test_safety_l1.py`: detector unit tests.
- `engine/tests/test_generation_logging.py`: integration tests for the generation boundary.

---

# In Scope

- Deterministic L1 detector for all four §10.2 hard-stop categories
- Safe text extraction from generation messages
- `safety_hard_stop` event payload builder or helper
- Integration into `engine.routing.logging.generate` before model routing
- Neutral bridge return for blocked generation attempts
- Tests proving model routing is not called on L1 blocks
- Tests proving blocked events do not contain raw trigger details
- Tests proving arc content rails cannot disable L1
- Static test preventing production direct `route_generation` calls outside the approved allowlist

---

# Out Of Scope

- L2 safety classification
- L3 policy prompt injection
- Post-generation output filtering
- API route or SDK changes
- Database schema or migration changes
- New dependencies
- Dashboard safety visibility
- Full semantic safety coverage beyond deterministic L1 signatures
- Actor attribution for safety events

---

# Acceptance Criteria

- [ ] All four §10.2 L1 hard-stop categories have deterministic detector coverage and tests.
- [ ] L1 runs before any call to `route_generation`.
- [ ] Production code cannot call `route_generation` directly outside the approved routing allowlist.
- [ ] A blocked L1 event writes `event_type = "safety_hard_stop"`.
- [ ] `safety_hard_stop` payload contains category/code metadata and no raw trigger content.
- [ ] `safety_hard_stop.content_text` is `null`.
- [ ] Blocked generation returns a neutral bridge that does not reveal the trigger.
- [ ] Blocked generation returns a neutral `RouteResult` sentinel with zero token counts, zero latency, `used_fallback=False`, and non-provider `model_used = "l1_hard_stop"`.
- [ ] Blocked generation does not write a `generation_logs` row.
- [ ] Blocked generation does not write a `routing_fallback` event.
- [ ] Safe generation still routes and logs normally.
- [ ] Tests prove permissive arc content rails cannot disable L1.
- [ ] No provider/model strings, prompt changes, API changes, migrations, or new dependencies are introduced.

---

# Test Plan

- Unit tests: detector blocks one representative input for each §10.2 category.
- Unit tests: detector does not block fictional Nightcap-safe murder mystery phrasing.
- Unit tests: detector extracts text from plain string messages and structured text blocks.
- Integration tests: `generate` does not call `route_generation` when L1 blocks.
- Integration tests: `generate` writes one `safety_hard_stop` event with safe payload fields.
- Integration tests: `safety_hard_stop.content_text` is `None`.
- Integration tests: `generate` writes no `GenerationLog` for a blocked call.
- Integration tests: `generate` writes no `routing_fallback` event for a blocked call.
- Integration tests: blocked calls return the exact neutral `RouteResult` sentinel.
- Integration tests: safe messages continue through existing generation logging behavior.
- Integration tests: permissive `ContentRailsConfig` values do not alter L1 behavior.
- Static test: production code does not call `route_generation` directly outside the approved allowlist.

Run:

- `python -m pytest engine/tests/test_safety_l1.py engine/tests/test_generation_logging.py -q`
- `python -m pytest engine/tests/ -q`
- `python -m ruff check engine/safety engine/routing engine/tests`
- `python -m ruff format --check engine/safety engine/routing engine/tests`
- `git diff --check`

---

# Risks And Unknowns

**Risks**:

- Deterministic signatures can miss semantically equivalent unsafe requests. AW-209 L2 classification is required for broader semantic safety.
- Overly broad patterns could block legitimate fictional murder mystery content. Tests must include Nightcap-safe phrasing.
- Returning a neutral bridge from the generation boundary is a temporary contract until the coordinator owns bridge emission.

**Unknowns**:

- Exact actor attribution for safety events is deferred until the caller passes actor context into generation.
- The future L2/L3 pipeline may replace the temporary neutral bridge path with a richer coordinator-owned bridge event.

---

# Open Questions

None.

---
## SOURCE FILE: docs/specs/README.md

# Implementation Specifications

This directory contains detailed specs for implementing features and systems. Each spec takes an architecture decision or product requirement and defines: what will be built, how to test it, and known risks.

## Structure

- Use sequential numbering: `0001-arc-execution-state-machine.md`, `0002-knowledge-graph-api.md`
- Include status, author, date, and acceptance criteria
- Follow the spec format (see `0000-template.md`)
- Status: Draft → Approved → In Progress → Done

## Adding a New Spec

1. Copy `0000-template.md` to the next sequential number: `000N-{feature-slug}.md`
2. Fill all sections (Title, Status, Author/date, References, Overview, In Scope, Out of Scope, Acceptance Criteria, Test Plan, Risks/Unknowns, Open Questions)
3. Link specs to the ADRs and architecture sections that justify them
4. Be specific: list what APIs will look like, database changes, etc.
5. Include acceptance criteria that can be verified by tests or review
6. Flag unknowns and risks explicitly—don't hide them

## How Specs Relate to Other Documents

- **From ADRs**: Specs implement decisions captured in architecture decision records
- **From architecture**: Specs detail how to build the systems described in architecture docs
- **For code reviews**: Use acceptance criteria to verify implementations match specs

## Using Specs During Development

1. Before coding: create a spec and get it reviewed/approved
2. During coding: reference spec acceptance criteria and test plan
3. After coding: verify acceptance criteria met and specs are current

## Spec Lifecycle

- **Draft**: Being written, not ready for review
- **Approved**: Reviewed and ready to implement
- **In Progress**: Someone is actively working on it
- **Done**: Implementation complete and verified against acceptance criteria

## Current Specs

- **Arc Execution**: State machine, beat transitions, pacing
- **Knowledge Graph**: Character state, fact storage, inference
- **Session Management**: Creation, persistence, recovery
- **Content Events**: Schema, routing, SSE delivery

