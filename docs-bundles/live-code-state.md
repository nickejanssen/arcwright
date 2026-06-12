# Live Code State — Snapshot (generated 2026-06-12)

This file summarizes the repository's engineering state relevant to M1 (Deterministic Platform Core).

1) Build / Type status
- Commands executed:
  - `cmd /c make.cmd type`
  - `c:\Users\nicke\OneDrive\Desktop\arcwright\.aw102-venv\Scripts\python.exe -m mypy --config-file pyproject.toml engine api`
- Result:
  - `cmd /c make.cmd type` failed because it invoked `C:\Users\nicke\miniconda3\python.exe`, which did not have `mypy` installed.
  - direct `.aw102-venv` command successfully ran mypy and exposed source type errors.

Quoted outputs:
```
# make.cmd path mismatch / missing mypy in Miniconda Python
C:\Users\nicke\miniconda3\python.exe: No module named mypy

# direct venv mypy run
engine\arc\arc_state.py:129: error: Function is missing a return type annotation  [no-untyped-def]
engine\safety\l1.py:206: error: Name "parts" already defined on line 201  [no-redef]
engine\routing\logging.py:92: error: Returning Any from function declared to return "RouteResult"  [no-any-return]
Found 3 errors in 3 files (checked 31 source files)
```

- Context: `Makefile`/`make.cmd` use `$(PYTHON) -m mypy --config-file pyproject.toml engine api`. The project contains a `.aw102-venv`, but `cmd /c make.cmd` is not currently using that venv and instead falls back to a Miniconda interpreter. The direct venv command above is the first successful type-check run in this session.

Known M1 blocker: CI/workflow and roadmap treat type-check failures as exit blockers. The current actual source issues are:
  1. `engine/arc/arc_state.py:129` — missing return type annotation.
  2. `engine/safety/l1.py:206` — redefinition of `parts`.
  3. `engine/routing/logging.py:92` — returning `Any` from a function declared to return `RouteResult`.

2) Schema snapshot (compact)
- Location (migrations): `migrations/versions/0001_enable_vector_extension.py`, `migrations/versions/0002_create_platform_tables.py` — these two files represent the first full migration.
- Summary of main entities (from `0002_create_platform_tables.py` and supplemental schema docs):
  - `accounts` — account_id (UUID PK), `firebase_uid` (unique), `email`, `display_name`, `created_at`, `last_seen_at`.
  - `characters` — `character_id` (UUID PK), `behavior_profile` (JSONB), `embedding` VECTOR(1536) NULL.
  - `sessions` — `session_id` (UUID PK), `arc_id`, `status`, `host_account_id` (FK → accounts), `created_at`, `started_at`, `completed_at`, `current_beat_id`, `quality_tier`, `player_count`.
  - `arc_beat_states` — statemachine snapshot store: `state_id`, `session_id` (FK), `beat_id`, `statemachine_config` JSONB, `transition_history` JSONB, `snapshot_at`, `is_current`.
  - `consent_records` — consent tracking with `consent_id`, `account_id?`, `session_id?`, `consent_type`, `granted`, `granted_at`, `revoked_at`, `consent_version`.
  - `events` — append-only events table with `event_id`, `session_id`, `actor_char_id?`, `event_type`, `payload` JSONB, `content_text`, `embedding` VECTOR(1536) NULL; indexes on (`event_type`,`timestamp`) and (`session_id`,`timestamp`).
  - `facts`, `knowledge_states` — fact store and per-character knowledge state with provenance chain and `superseded_by` self-FK.
  - `generation_logs` — generation telemetry: `log_id`, `session_id`, `task_type`, `quality_tier`, `model_used`, `latency_ms`, `input_tokens`, `output_tokens`, `cost_usd`, embeddings for prompt/output.
  - `relationships`, `locations`, `objects`, `session_participants`, `decisions`, `decision_logs` — ancillary platform tables for relationships, world model, participants, and decision/audit logs.

3) Instruction-surface conflict (concise)
- Files examined: `AGENTS.md` (authoritative), `CLAUDE.md`, `.github/copilot-instructions.md` (mirror). No `.cursorrules` file found in workspace.
- Observations:
  - `AGENTS.md` is the canonical agent instruction; `CLAUDE.md` intentionally imports it (@AGENTS.md) and contains no conflicting rules.
  - `.github/copilot-instructions.md` is a mirrored copy of `AGENTS.md` (explicit header says "GENERATED MIRROR, DO NOT EDIT BY HAND"). Its content matches `AGENTS.md`.
- Conflicting lines: I did not find substantive divergences between these three files. No `.cursorrules` was present to compare; therefore no explicit instruction-surface conflict detected in these sources.

4) M1 progress (roadmap-derived)
- Source: `docs/roadmap/milestones/M1-deterministic-platform-core.md` and the M1 epic/task files in `docs/roadmap/epics` and `docs/roadmap/tasks`.
- Completed / present in repo:
  - Alembic migrations for enabling `vector` and creating platform tables exist (`migrations/versions/0001_*.py`, `0002_*.py`). This satisfies much of AW-104's artifact (migration authored).
  - SQLAlchemy ORM models and target metadata exist under `engine/db/orm.py` (implements AW-103 intent). The migration includes `VECTOR(1536)` guard code per spec.
  - Router implementation and routing table are present: `engine/routing/router.py` and `config/routing_table.json` (AW-107 scaffold implemented).
  - Knowledge-graph core functions implemented: `engine/knowledge/graph.py` with `assert_knowledge`, `get_character_knowledge`, and `revoke_knowledge` (AW-105 implemented code-wise).
- Open / planned items (from roadmap files):
  - Tests and CI verification: M1 exit criteria require AW-104 migration to upgrade/downgrade cleanly and AW-105 knowledge graph to pass full unit suite. The repo contains tests under `engine/tests/`; local typecheck now reports a direct venv mypy run with 3 errors, so CI-level green status remains unverified until both type checks and tests are completed.
  - Model routing and generation logging: router exists but AW-108 (prompt caching & generation logging) may need test coverage and config verification; `generation_logs` table and `engine/routing/logging.py` exist, but CI tests must validate logging behavior.
- M1 Exit criteria remaining (per M1 milestone):
  - AW-104: `alembic upgrade head` and `alembic downgrade base` verified cleanly in CI/local (not verified here).
  - AW-105: knowledge graph unit tests pass (local tests present but not executed here).
  - AW-107/108: routing swaps and generation logging wired and tested (partial implementation present; tests needed).

Open blockers
- Local environment tooling: `mypy` missing produced a hard stop when running `make type`. Install pinned dev tools (`pip install -r requirements.txt` or at minimum `pip install mypy==1.13.0`) and re-run `make type`.
- Migration verification: run `alembic upgrade head` against a Postgres 15 + pgvector dev instance to confirm AW-104 acceptance criteria.
- Tests and CI check: run unit tests (`pytest engine/tests/`) and TypeScript typechecks (`npm run typecheck` in `sdk` and `dashboard`) to surface any remaining failures.

Path: docs-bundles/live-code-state.md
