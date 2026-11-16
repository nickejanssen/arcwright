---
id: arcexecution.architecture.02-technology-stack
namespace: arc-execution
title: Technology Stack
owner: Nico Janssen
status: active
review_by: "2026-12-10"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

> Source: Project knowledge artifact 07-Technical-Architecture-v1.3
> Last synced: 2026-05-21
> This file is the canonical source. Edit it here through a pull request; the Notion export it was first synced from is historical.

# Technology Stack

All decisions in this section are locked (Chat 6a, May 7 2026). Rationale is summarized here; full rationale is in `docs/product/decisions-log.csv`. Alternatives considered are listed to prevent re-litigation during implementation.

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

**Safety L2: GPT-OSS-Safeguard 20B on Groq.** Pre-generation safety classification. Supports bring-your-own-policy. Groq inference: fast and cheap (~$0.075/million input tokens; output rate pending verification per `docs/product/open-questions-log.csv`). See Section 10 for full safety pipeline.

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

## 2.11 Full Target Stack And The Build-Versus-Adopt Rule (November 2026)

Added in the November 2026 reset. Sections 2.1 to 2.10 record what is locked and built. This section records the whole stack the full game and the full engine need, including layers not adopted yet, so the founder and every agent can see what is ours and what is borrowed.

**The rule (D-114, ADR-0026):** build only what makes Arcwright unique. Adopt existing technology for the rest. Replace an adopted tool only when it lacks a feature we need, it gets too expensive, or there is a strong purpose for a custom version. Free options first; up to $50 a month in total when a free option falls short. Nothing is installed, signed up for or bought without the founder's approval, and a new dependency is a hard rule in `AGENTS.md`.

**Where things plug in.** Model providers plug into the router inside the engine; it routes seven kinds of text task today and has no voice task yet. Everything a player sees or hears (voice, animation, UI, art) belongs to the game's display side, which the engine knows nothing about.

**What happens when a player taps.** The phone sends the tap to the API. The engine checks it against the rules and updates the story state. Only then does it ask a model to voice the result. It sends events back saying what to show and to whom, and the screens perform them.

In the tables below, "verified" means the licence or price was checked on 2026-11-14. Section 2.11.7 re-checks the session 1 layers on 2026-11-15. Anything not marked verified is from memory and must be checked before it is relied on.

### 2.11.1 The stack today, top to bottom

| Layer | What it does | Built with | Ours or adopted | State |
| --- | --- | --- | --- | --- |
| Players' screens | Shows the story on the TV, takes taps on phones | TypeScript | Hand-built | Old design only; two sets of code (`dashboard/`, `nightcap-web/`) |
| Connection kit (SDK) | Lets any screen talk to the engine | TypeScript, about 500 lines | Ours | Works |
| Front door (API) | Receives requests, checks who is asking | FastAPI | Adopted | Works on the founder's PC |
| **Engine, the dungeon master** | Story units, who knows what, characters, pacing, safety, mini-game rules, play records | Python, about 16,000 lines, 912 passing tests | **Ours: the unique part** | Tested, for the old design |
| AI models | Write the lines the engine asks for | LiteLLM routing to hosted models | Adopted | Works |
| Data | Saves sessions | Postgres with pgvector | Adopted | Founder's PC only |
| Sign-in | Tells players apart | Firebase | Adopted | Worked in the August rehearsal |
| Hosting | Puts it on the internet | Cloud Run, Cloud SQL, Cloudflare | Adopted | Never deployed; today it is the founder's PC and a tunnel |
| Game content | Nightcap's story files, cases and mini-games | Data files | Ours, per game | Old design; the new case is in progress |

### 2.11.2 What players see and hear (the game's side)

| Layer | Today | Adopt | Cost | When |
| --- | --- | --- | --- | --- |
| Screens | Two hand-built clients | One client on React, which the repository already uses | Free | Sessions 1 and 2 |
| Motion | None | Rive (MIT runtime, verified) | Free editor; exports carry a splash screen until $9 a seat (verified) | If it fits |
| Voices | None | Kokoro (Apache-2.0, verified, self-hosted), or the ElevenLabs or Inworld free tiers | ElevenLabs: 10,000 credits a month free with no commercial licence, $6 Starter (verified). Inworld: pay as you go, about 70 free minutes (verified) | If it fits |
| Talking-character products | None | Do not adopt whole. Convai's free tier is 100 interactions a month, $29 above that (verified). Take voices, not brains | Not planned | Not planned |
| Sound and music | None | Howler.js (MIT, verified) plus licensed tracks | Free player | Later |
| Art | A written art direction only | Image models with human finishing, rights recorded for every asset | Per use | Later |
| Richer mini-games | A small own kit | PixiJS or Phaser (MIT, verified) | Free | When a mini-game needs it |
| 3D or console games | None | Godot (MIT, verified), Unity or Unreal, through connection kits | None yet | Second game or later |

Nightcap stays in the browser with no install, as Jackbox does. Unity and Unreal matter for a different kind of game, not for a TV-and-phones party game.

### 2.11.3 The engine

| Layer | Today | Plan |
| --- | --- | --- |
| Who knows what, characters, pacing, fairness checks, rules decide outcomes | Ours | **Keep. This is the unique part.** |
| Story flow | python-statemachine, adopted | Keep |
| Story writing | Hand-edited files | Import from an adopted story tool (D-117, AW-306) |
| Viewer for the story and the live state | None | Ours, drawn with React Flow or Cytoscape.js (both MIT, verified) instead of hand-drawn graphs (AW-317) |
| Graph questions | Postgres tables | Add Apache AGE (Apache-2.0, verified) only when a real question cannot be answered without it |
| Story library search | pgvector, already installed | Keep (AW-314) |

### 2.11.4 Story-writing tools

| Tool | Style | Licence and cost |
| --- | --- | --- |
| Ink (and inkjs) | Text script, strongest logic | MIT, verified; free |
| Yarn Spinner | Text script, made for dialogue | MIT, verified; free |
| Twine | Visual map of passages | GPL-3.0, verified; free |
| Arcweave | Web-based, collaborative, editable graph | Free plan: 3 projects, 200 items, JSON export, **not for commercial projects** (vendor page, 2026-11-15). Pro $15 to $18 a member a month |
| articy:draft X FREE | Professional, heaviest, editable flow chart | Free, commercial use allowed, 700 objects per project, all exports (vendor page, 2026-11-15) |

These tools write branching scenes. None models who knows what, or fair routes to a truth. That part stays in Arcwright, so the work is an importer, not a replacement.

D-122 requires a graph view the founder can edit. Ink and Yarn Spinner are text scripts with no editable graph, so neither can be the main tool; the shortlist for AW-306 is Twine, articy:draft X FREE and Arcweave. Detail: section 4 of the [competitor comparison](../product/2026-11-15-competitor-and-prior-art.md).

### 2.11.5 AI, data and running it

| Layer | Today | Plan | When |
| --- | --- | --- | --- |
| Model routing | LiteLLM (open core) | Keep | Now |
| Voice as a routed task | None | Add when voices are adopted | With voices |
| Tracing AI calls | Own log table | Langfuse (open core) only if needed | Later |
| Play records | Engine tables | Keep, made game-agnostic (D-115, AW-304) | Sessions 1 and 2 |
| Analysis | None | Plain queries plus DuckDB (MIT, verified) | After session 1 |
| Product analytics | None | PostHog (open core) only if needed | Later |
| Player feedback | Jotform | Keep | Session 1 |
| Database and hosting | Founder's PC and a tunnel | Cloud SQL, Cloud Run, Cloudflare (built, never deployed) | Before session 3 |
| Sign-in and automated checks | Firebase, GitHub | Keep | Now |
| Real-time rooms beyond SSE | SSE plus POST | Colyseus (MIT, verified) only if a game needs it | Later |
| Payments | None | A payment provider or store | Commercial launch |

### 2.11.6 Candid notes for strategy

From memory, not checked in the reset: middleware alone has rarely reached very large outcomes, and the large ones came from a hit game that became a platform. That supports the games-first order: the near-term fact everything rests on is whether a room of people has a great time with Nightcap and asks to play again. The proper comparison was done on 2026-11-15: [competitor and prior-art comparison](../product/2026-11-15-competitor-and-prior-art.md). Its main findings: Hidden Door now sells something close to a story engine for any world; "rules decide, the AI only voices" is no longer a difference by itself; nobody was found directing a group in one room on a TV with phones.

### 2.11.7 Build-versus-adopt review for session 1 (AW-309, 2026-11-15)

The rule in ADR-0026 applied to each layer the thin first version needs. Licences and prices were read on the makers' own pages on 2026-11-15 unless a row says otherwise. **Session 1 needs no paid plan and no new tool.** Everything paid in this table together stays under the $50 a month ceiling.

| Layer | Today | Recommendation | Licence and price | What it replaces | When |
| --- | --- | --- | --- | --- | --- |
| Screens | Two hand-built clients. `dashboard/` uses React 18 and Vite. `nightcap-web/` is about 5,300 lines with no libraries | **Adopt React for the one surviving client.** Which codebase survives is decided in the inventory (AW-300) | React: MIT (from memory), free, already in `dashboard/package.json` | Hand-written rendering code in `nightcap-web/` | Screens spec (AW-302) |
| Rooms: TV plus phones | Built: room code, join, event stream | **Keep.** Do not adopt Playroom Kit | Playroom Kit: free plan is non-commercial and capped at 10 daily users; $10 a month above that. It would hold session state, which the engine must own | Nothing | Now |
| Motion | None | **Wait.** For session 1 use the transitions browsers already have. Adopt Rive only if "motion on the TV" is reached in the if-it-fits list | Rive runtimes: MIT, no runtime fee. Free plan exports play a Rive splash screen. $9 a seat a month billed yearly, or $17 monthly, removes it | Nothing yet | If it fits, item 5 |
| Host voice | None. The host's 468 written lines are text | **If it fits: render the written lines to audio files once, ahead of play, with Kokoro.** No voice call during a session, so no cost per session, no delay and no provider at run time | Kokoro: Apache-2.0, free, runs on the founder's PC. Alternatives: ElevenLabs free plan has no commercial licence and needs attribution, Starter is $6 a month; Inworld is $25 per million characters on demand, $15 for its fast model | Nothing yet | If it fits, item 1 |
| Friends' voices (AW-320) | None | **Recorded files only.** No product needed | Free | Nothing | If it fits, item 9 |
| Sound | None | **Wait.** The browser's own audio player is enough for line files and a few effects. Adopt Howler.js when sounds must overlap or phones refuse to play | Howler.js: MIT, free (verified 2026-11-14, not re-read today) | Nothing yet | Later |
| Story tool | Hand-edited files | **Adopt one with an editable graph** (D-122). Shortlist in 2.11.4 | Free options exist on the shortlist | Hand-editing story files | AW-306 |
| Talking-character products | None | **Do not adopt.** Take voices, not brains (ADR-0026) | Not applicable | Nothing | Not planned |

Decisions this review raises for the founder, each recorded in `docs/product/open-questions-log.csv` and asked one at a time:

1. Whether the surviving Nightcap client may add React as a dependency. Asked with the inventory (AW-300), because it depends on which codebase survives.
2. Whether to install Kokoro on the founder's PC to render three sample host lines, so he can hear the quality before choosing a voice. Asked only when the must-have list is done.

Not verified: how Kokoro sounds for this host, and the total length of the host's lines. Both are checked when decision 2 is reached.
