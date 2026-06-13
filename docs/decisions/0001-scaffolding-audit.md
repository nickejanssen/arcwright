# 0001 — Scaffolding Audit Against Technical Architecture v1.3

**Date:** 2026-05-20
**Status:** Informational — read-only analysis, no code changes
**Architecture reference:** `docs/archive/notion-export/07-Technical-Architecture-v1 3 35db7de354a881618e59e65c8e12caf6.md` (S1-S15)
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
