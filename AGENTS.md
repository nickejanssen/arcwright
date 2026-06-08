> This is the single authoritative, always-on instruction file for every AI coding agent working in this repository, including Claude Code, Codex, and GitHub Copilot. `CLAUDE.md` imports this file so Claude Code loads it. `.github/copilot-instructions.md` is a synchronized mirror of this file, kept because Copilot code review reads that path but not `AGENTS.md`. Role-specific contracts live in `docs/agents/` and `docs/skills/`.

# Agent Operating Guide

## Project Overview

Arcwright is Layer 2 narrative runtime middleware that automates session facilitation without removing human authorship. It takes a human-authored arc definition and a group of real players, and produces a coherent, unrepeatable session experience at runtime. The platform powers Nightcap (murder mystery party game) at MVP and will support Monster RPG, enterprise team-building, and third-party developer experiences. Python engine, TypeScript SDK, GCP infrastructure, LiteLLM routing to Anthropic/Groq models.

## Architecture Principles (Non-Negotiable)

All work in this repository must comply with the Arcwright PRD and technical architecture. If a proposed implementation conflicts with one of the platform architecture principles below, the principle wins unless the founder explicitly overrides it with documented rationale.

1. Surface agnosticism
- The engine has no opinion about what displays its output.
- Never write rendering logic, UI assumptions, or surface-specific presentation code in `engine/`.
- The platform emits structured content events with context; surfaces decide whether to render them on phones, shared displays, browsers, voice, or future interfaces.

2. Human arc primacy
- AI is the runtime personalization layer, not the creative author.
- Every experience must have a human-designed arc that defines the structure, constraints, required moments, and allowed variation.
- AI generation is called only after the arc execution layer has resolved the current session state deterministically.
- LLMs compose narrative from resolved, structured state data; they do not manage, infer, or update canonical session state.
- State transitions must always be deterministic. Any feature that asks the AI to decide what happened in the session is an architecture violation and must be redesigned.

3. Configurable composition
- Arc elements may be either authored or generative, per element.
- Preserve the authored-versus-generative dial in schemas and implementation choices.
- Do not collapse an arc into all-authored or all-generative assumptions unless the spec for that arc explicitly says so.

4. Unified character model
- Human-controlled and AI-driven characters are the same platform object type.
- Character identity, personality profile, goals, knowledge state, and relationship graph belong in one shared model.
- Behavior source may differ, but the data model must stay unified.

5. Knowledge graph as first-class infrastructure
- Every session maintains a structured knowledge graph recording who knows what, when they learned it, and from whom.
- AI character responses must be constrained by character knowledge state.
- Knowledge state is mandatory platform infrastructure, not an optional add-on.

6. Cost-aware architecture from day one
- Model routing is task-type plus quality-tier based.
- Classification and safety tasks route to small, fast, low-cost models; generation tasks route to models appropriate for the required quality tier.
- Routing is budget-first by default. Do not default to the best available frontier model when a cheaper model meets the quality bar.
- Prompt caching is a named architectural requirement. Reused session context layers must be cached wherever the provider supports it.

7. Progressive proprietary infrastructure
- Launch on managed third-party AI services first.
- Replace components with proprietary or self-hosted infrastructure only when session volume, data quality, and economics justify the transition.
- Do not introduce foundation-model training or owned compute infrastructure into MVP scope.

8. Provider-agnostic model routing
- No platform operation may hardcode a dependency on any specific AI provider, model name, or model version.
- Every model call must route through the internal abstraction layer that maps task type and quality tier to the active model.
- No provider name or model string may appear anywhere outside `config/routing_table.json` and `engine/routing/router.py`. Treat any violation as a bug.

## Implementation Guardrails

- Python owns arc execution, knowledge graph, character behavior, model routing, content safety, session state, migrations, and API logic.
- TypeScript owns the web SDK, dashboard rendering, event subscription, and player input submission logic.
- No arc execution logic crosses into TypeScript.
- FastAPI route handlers must stay thin: validate input, call engine functions, return responses. No arc logic in route handlers.
- Prefer scaffolding, interfaces, and configuration over speculative business logic unless the current task explicitly requires implementation.

## Key Engine Constraints

These five constraints are non-negotiable and may not be bypassed by arc configuration or by any client-specific instruction.

- Python 3.11+, no earlier.
- Arc execution logic stays in the Python engine; no arc logic in TypeScript.
- Knowledge state queries are mandatory before every AI character generation (non-negotiable).
- All provider and model names stay in `config/routing_table.json` and `engine/routing/router.py` only.
- Safety constraints are enforced at the engine layer; they cannot be bypassed by arc configuration.

## Documentation Structure

- `/docs/prd/`: product requirements (01-overview, 02-requirements, 03-scope, 04-non-goals)
- `/docs/architecture/`: technical architecture sections (01-overview through 15-development-guide)
- `/docs/decisions/`: Architecture Decision Records (ADR template, locked decisions from Chat 6a)
- `/docs/specs/`: implementation specifications (template provided; specs created per feature)
- `/docs/conventions/`: coding standards, testing, AI contribution, cost policy
- `/docs/agents/`: development-role contracts (Product Steward, Planner, Spec Author, Scribe, and the operating-model README)
- `/docs/skills/`: reusable, platform-neutral role skills (Implementer, Reviewer, Architecture SME)

## Before Starting Any Task

1. Read the relevant **PRD section** from `/docs/prd/` for product context.
2. Read the relevant **architecture section** from `/docs/architecture/` for design details.
3. Read or create a **spec file** in `/docs/specs/` using the template; the spec must define acceptance criteria.

## Coding Conventions

See `/docs/conventions/` for:
- `coding-style.md`: Python/TypeScript style, no fluff comments
- `testing.md`: unit tests written with changes, focused on knowledge graph, arc transitions, safety, routing
- `ai-contributions.md`: guidelines for agent work
- `ai-cost-policy.md`: cost awareness principles

## Commands

**Python (engine + API):**
```bash
pip install -r requirements.txt
pytest engine/tests/                    # Run unit tests
pytest evals/runners/test_routing_evals.py -q
python -m ruff check engine api
python -m ruff format --check engine api
```

**TypeScript (SDK + Dashboard):**
```bash
cd sdk && npm install && npm run typecheck && npm run build
cd dashboard && npm install && npm run typecheck && npm run build
```

**Database:**
```bash
alembic upgrade head                    # Apply migrations
alembic revision --autogenerate -m "description"  # Create migration
```

## Workflow Expectations

1. **Write a plan** before implementing. Use planning tools or create a plan file in your workspace.
2. **Get plan approved** before implementation. Do not implement without approval.
3. **Write tests as part of changes**, not after. Tests must validate acceptance criteria from the spec.
4. **Run all checks locally** before claiming done: tests pass, types check, linting passes.

## Hard Rules (Requires Explicit Approval)

- **Cross-module changes**: changes affecting multiple engine/ submodules need design review.
- **New dependencies**: any package.json or requirements.txt changes.
- **Schema or migration changes**: database changes require migration and review.
- **Prompt or eval suite changes**: safety, routing, or telemetry signal changes.
- **Secrets or auth**: anything touching Firebase, API keys, or credential handling.

## Logging Architecture Decisions

When a decision affects multiple components or represents a significant trade-off:

1. Create `/docs/decisions/NNNN-decision-name.md` using the template (Status, Context, Decision, Consequences, References).
2. Surface the decision to the human with a short summary and link to the decision file.
3. Reference the ADR in relevant spec or architecture files.
4. Update `/docs/decisions/README.md` index if adding a new numbered decision.

## Agent-Local Files: Do Not Commit

Directories like `.claude/`, `.codex/`, `.cursor/`, and similar tool metadata dirs contain a mix of:
- **Project-level config** (for example, `.codex/environments/`): may be intentionally tracked.
- **Local-only state** (session files, per-user settings, generated indexes): must never be committed.

Rules for every agent working in this repo:
- Do not create, modify, stage, commit, or delete files inside `.claude/`, `.codex/`, `.cursor/`, or any similar tool-local directory unless explicitly asked.
- Treat those directories as local workspace state, not product code.
- Before every commit, run `git status` and verify that no agent-local files appear in the staged list.
- If `git status` shows untracked or modified files in these directories, leave them untracked and call them out to the human; do not clean them up automatically.
- Do not include agent-local files in commits or PRs.
- Leave pre-existing local files that are unrelated to the current task alone; call them out rather than cleaning them up.
