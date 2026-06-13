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