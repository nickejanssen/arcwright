# Arcwright

Arcwright is Layer 2 narrative runtime middleware: a platform for running human-authored interactive arcs with AI-powered runtime personalization.

The core idea is simple:

- Humans author the arc structure, constraints, and intended experience.
- The engine resolves session state deterministically.
- LLMs generate narrative only from that resolved state.
- Surfaces render events however they want.

Nightcap, the multiplayer murder mystery party game in this repo, is the reference implementation used to stress-test the platform.

## What This Repository Is

This repository is the early Arcwright platform scaffold. It is being shaped around the PRD and technical architecture before the business logic is filled in.

Today, this repo contains:

- Python-first platform structure for the engine and API
- TypeScript scaffolding for the SDK and dashboard
- Routing and environment configuration
- Source architecture and product documents in `docs/`

This repo does not yet contain the core runtime implementation.

## What Arcwright Is Not

Arcwright is not:

- a rendering engine
- a Nightcap-only codebase
- an AI improvisation sandbox where the model decides what happened
- a public third-party developer platform yet

Per the PRD, the platform MVP is the internal engine that runs Nightcap cleanly enough that a technical co-founder could understand the architecture without a guided tour.

## Architecture Rules That Matter Most

These are the non-negotiables for work in this repo:

1. Surface agnosticism: the engine emits structured events; it does not render UI.
2. Human arc primacy: state transitions are deterministic; LLMs express resolved state, they do not manage it.
3. Configurable composition: arc elements can be authored or generative per element.
4. Unified character model: human and AI participants share the same platform character model.
5. Knowledge graph first: knowledge state is core infrastructure, not an add-on.
6. Cost-aware by default: routing is budget-first and prompt caching is required.
7. Progressive proprietary infrastructure: start managed, replace components only when economics justify it.
8. Provider-agnostic routing: no provider or model hardcoding outside `config/routing_table.json` and `engine/routing/router.py`.

See `.cursorrules` for the repo-level AI implementation guardrails derived from the PRD.

## Repository Layout

```text
arcwright/
  engine/       Python core platform library
  api/          FastAPI thin wrapper over engine
  sdk/          TypeScript web SDK
  dashboard/    TypeScript React dashboard
  migrations/   Alembic migrations
  nightcap/     Nightcap arc definition files
  config/       Environment config and routing table
  scripts/      Setup and utility scripts
  docs/         Product, architecture, decision, and design docs
```

Planned platform internals inside `engine/`:

- `arc/` for deterministic arc execution
- `characters/` for the unified character model and behavior engine
- `knowledge/` for knowledge graph logic
- `routing/` for AI model routing abstraction
- `safety/` for content safety rails
- `events/` for the content event system
- `session/` for session state and persistence
- `telemetry/` for structured telemetry and logging
- `tests/` for unit and simulation harnesses

## Read These First

If you are new to the repo, read these in order:

1. `docs/06-PRD-v1 3 358b7de354a8814292c3d0e67cb73f3c.md`
2. `docs/07-Technical-Architecture-v1 3 35db7de354a881618e59e65c8e12caf6.md`
3. `.cursorrules`

Helpful supporting docs:

- `docs/roadmap/README.md`
- `docs/07-Story-Bible-Murder-Mystery-v1 361b7de354a8817a99ece1b701763f06.md`
- `docs/09-Story-Bible-Monster-RPG-v1 0 365b7de354a881e08dd5d43e2ab2edb5.md`
- `docs/02-Decisions-Log 03d3b381bfe34918b6100a73897893da.csv`
- `docs/03-Open-Questions-Log 7f57c928827f482aa62a258bed894ce6_all.csv`

## Current Technical Defaults

Current scaffolded defaults come directly from the technical architecture doc:

- Python for engine and API
- TypeScript for SDK and dashboard
- FastAPI for the HTTP layer
- PostgreSQL plus `asyncpg` plus SQLAlchemy async
- Alembic for migrations
- LiteLLM in-process at MVP
- Firebase for dashboard/auth integration
- `config/routing_table.json` as the single source of truth for model routing

The MVP routing table currently defines task categories for:

- `character_dialogue`
- `pacing_decision`
- `safety_classification`
- `knowledge_inference`
- `narrative_generation`

## Getting Started

This repository is still scaffold-stage, so setup is intentionally light.

### Python

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
pip install pre-commit
pre-commit install
```

### Repo Tooling

```bash
npm install
```

### Environment

Create a local `.env` from `.env.example` and fill in:

- `DATABASE_URL`
- `FIREBASE_PROJECT_ID`
- `ANTHROPIC_API_KEY`
- `GROQ_API_KEY`

Do not commit secrets.

### TypeScript Packages

SDK:

```bash
cd sdk
npm install
```

Dashboard:

```bash
cd dashboard
npm install
```

## Implementation Priorities

The technical architecture document explicitly calls out the first implementation file:

- `engine/session/models.py`

That file should define the foundational session models before broader engine work expands around it.

The MVP critical path is:

- arc execution engine
- session management
- knowledge graph
- Nightcap integration
- safety rails
- basic cost tracking
- structured telemetry

The dashboard and developer-facing authoring surfaces are intentionally lower priority during H1.

## Contribution Guidance

When adding code here:

- Keep FastAPI routes thin. Validate input, call engine code, return responses.
- Do not place arc execution logic in TypeScript.
- Do not place rendering logic in the engine.
- Do not hardcode model names or providers outside the routing layer.
- Do not let AI output decide canonical session state.
- Prefer platform-clean abstractions over Nightcap-specific shortcuts unless the requirement is explicitly Nightcap-only.

If a change seems to violate the PRD or architecture docs, stop and resolve the design question before implementing it.

## Status

Current status: scaffolded repository aligned to PRD v1.3 and Technical Architecture v1.3, with core implementation still to come.
