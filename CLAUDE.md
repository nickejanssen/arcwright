# Claude Code Initialization Guide

## Project Overview

Arcwright is Layer 2 narrative runtime middleware that automates session facilitation without removing human authorship. It takes a human-authored arc definition and a group of real players, and produces a coherent, unrepeatable session experience at runtime. The platform powers Nightcap (murder mystery party game) at MVP and will support Monster RPG, enterprise team-building, and third-party developer experiences. Python engine, TypeScript SDK, GCP infrastructure, LiteLLM routing to Anthropic/Groq models.

## Documentation Structure

- `/docs/prd/` — Product requirements (01-overview, 02-requirements, 03-scope, 04-non-goals)
- `/docs/architecture/` — Technical architecture sections (01-overview through 15-development-guide)
- `/docs/decisions/` — Architecture Decision Records (ADR template, locked decisions from Chat 6a)
- `/docs/specs/` — Implementation specifications (template provided; specs created per feature)
- `/docs/conventions/` — Coding standards, testing, AI contribution, cost policy

## Before Starting Any Task

1. Read the relevant **PRD section** from `/docs/prd/` for product context
2. Read the relevant **architecture section** from `/docs/architecture/` for design details
3. Read or create a **spec file** in `/docs/specs/` using the template; spec must define acceptance criteria

## Coding Conventions

See `/docs/conventions/` for:
- `coding-style.md` — Python/TypeScript style, no fluff comments
- `testing.md` — Unit tests written with changes, focused on knowledge graph, arc transitions, safety, routing
- `ai-contributions.md` — Guidelines for agent work
- `ai-cost-policy.md` — Cost awareness principles

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
3. **Write tests as part of changes**, not after. Tests must validate acceptance criteria from spec.
4. **Run all checks locally** before claiming done: tests pass, types check, linting passes.

## Hard Rules (Requires Explicit Approval)

- **Cross-module changes** — Changes affecting multiple engine/ submodules need design review
- **New dependencies** — Any package.json or requirements.txt changes
- **Schema or migration changes** — Database changes require migration and review
- **Prompt or eval suite changes** — Safety, routing, or telemetry signal changes
- **Secrets or auth** — Anything touching Firebase, API keys, or credential handling

## Logging Architecture Decisions

When a decision affects multiple components or represents a significant trade-off:

1. Create `/docs/decisions/NNNN-decision-name.md` using the template (Status, Context, Decision, Consequences, References)
2. Surface the decision to the human with a short summary and link to the decision file
3. Reference the ADR in relevant spec or architecture files
4. Update `/docs/decisions/README.md` index if adding a new numbered decision

## Agent-Local Files — Do Not Commit

Directories like `.claude/`, `.codex/`, `.cursor/`, and similar tool metadata dirs contain a mix of:
- **Project-level config** (e.g., `.codex/environments/`, `.cursorrules`) — may be intentionally tracked
- **Local-only state** (session files, per-user settings, generated indexes) — must never be committed

Rules for every agent working in this repo:
- Do not create, modify, stage, commit, or delete files inside `.claude/`, `.codex/`, `.cursor/`, or any similar tool-local directory unless explicitly asked.
- Treat those directories as local workspace state, not product code.
- Before every commit, run `git status` and verify that no agent-local files appear in the staged list.
- If `git status` shows untracked or modified files in these directories, leave them untracked and call them out to the human — do not clean them up automatically.
- Do not include agent-local files in commits or PRs.
- Leave pre-existing local files that are unrelated to the current task alone; call them out rather than cleaning them up.

## Key Constraints

- Python 3.11+, no earlier
- Arc execution logic stays in Python engine; no arc logic in TypeScript
- Knowledge state queries are mandatory before every AI character generation (non-negotiable)
- All provider/model names stay in `routing_table.json` and `router.py` only
- Safety constraints enforced at engine layer; cannot be bypassed by arc configuration
