---
id: engineeringpractice.superpowers.specs.2026-09-27-phase-0-dev-friction-design
namespace: engineering-practice
title: Phase 0 Development Friction Design
owner: Nico Janssen
status: active
review_by: "2027-03-27"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Phase 0 Development Friction Design

> Status: Approved design, 2026-09-27 (founder approved all three sections and the preflight approach in session)
> Canonical path: docs/superpowers/specs/2026-09-27-phase-0-dev-friction-design.md

## Purpose

Phase 0 of the plan to get Arcwright and Nightcap back on track: remove the three things that make development noisier or slower before the v3.0 playtest work begins. It changes no product code in `engine/`, `api/`, `sdk/`, `dashboard/` or `config/`.

## Evidence (measured 2026-09-27)

- **Deploy API** has failed 32 of 32 runs since July. Every run stops at `google-github-actions/auth` because no workload identity provider is configured. It triggers on every push to `main` touching `api/**`, `engine/**`, `config/**` or `Dockerfile`, so main goes red on most engine work.
- **Deploy Web** has failed 8 of 8 runs. It triggers only on `nightcap-web/**` and last ran 2026-08-05.
- The repository has no Actions secrets or variables configured.
- **Local Python:** `.python-version` already pins `3.11`, but the Windows `py` launcher ignores it, so `python` resolves to 3.14. Under 3.14, `mypy` stops with `numpy/__init__.pyi: Type statement is only supported in Python 3.12 and greater`. In a `uv`-built 3.11 `.venv`: mypy reports no issues in 126 files, `pytest engine/tests` passes (912 passed, 1 skipped), and ruff passes. CI already runs mypy on 3.11 (`verify-tasks.yml`) and passes.
- **Tooling drift:** commits from 2026-09-01 to 2026-09-27 went almost entirely to agent and knowledge-base infrastructure, while Paper Test #2 v3.0 (published 2026-08-31) has had no external sessions.

## Design

### 1. Deploy preflight

Applies to `.github/workflows/deploy-api.yml` and `.github/workflows/deploy-web.yml`.

Each workflow gains a first job, `preflight`, that checks whether the settings its deploy needs are present. It tests only whether each value is non-empty and never prints a value.

| Workflow | Required settings |
|---|---|
| Deploy API | `vars.GCP_WORKLOAD_IDENTITY_PROVIDER`, `vars.GCP_SERVICE_ACCOUNT`, `secrets.GCP_REGION`, `secrets.GCP_PROJECT_ID`, `secrets.AR_REPO` |
| Deploy Web | `secrets.CLOUDFLARE_API_TOKEN`, `secrets.CLOUDFLARE_ACCOUNT_ID` |

Outcomes:

| Settings present | Preflight result | Deploy job | Run conclusion |
|---|---|---|---|
| none | `::notice` titled "Deploy skipped" that names the settings | skipped | success |
| some, not all | `::error` titled "Deploy partially configured" that names the missing settings; exit 1 | not run | failure |
| all | `ready=true` | runs as today, unchanged steps | per the deploy |

A partial configuration fails on purpose: it means someone is partway through setup and needs to know what is missing.

The existing `deploy` job gains `needs: preflight` and `if: needs.preflight.outputs.ready == 'true'`. Its steps are unchanged.

Both workflows also gain a `workflow_dispatch:` trigger, so the change can be verified right after merge (the PR touches only `.github/`, so no path filter fires) and so the Arcwright engine phase can trigger a first real deploy on demand.

GitHub does not allow the `secrets` context in a job-level `if`, which is why the check is a job with an output rather than a condition on the deploy job.

Reference preflight step (the API variant; the Web variant differs only in the `env` block and the `required` list):

```yaml
  preflight:
    name: Check deploy configuration
    runs-on: ubuntu-latest
    outputs:
      ready: ${{ steps.check.outputs.ready }}
    steps:
      - name: Check required deploy settings
        id: check
        env:
          GCP_WORKLOAD_IDENTITY_PROVIDER: ${{ vars.GCP_WORKLOAD_IDENTITY_PROVIDER }}
          GCP_SERVICE_ACCOUNT: ${{ vars.GCP_SERVICE_ACCOUNT }}
          GCP_REGION: ${{ secrets.GCP_REGION }}
          GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
          AR_REPO: ${{ secrets.AR_REPO }}
        run: |
          required=(GCP_WORKLOAD_IDENTITY_PROVIDER GCP_SERVICE_ACCOUNT GCP_REGION GCP_PROJECT_ID AR_REPO)
          missing=()
          for name in "${required[@]}"; do
            [ -n "${!name}" ] || missing+=("$name")
          done
          if [ "${#missing[@]}" -eq 0 ]; then
            echo "ready=true" >> "$GITHUB_OUTPUT"
          elif [ "${#missing[@]}" -eq "${#required[@]}" ]; then
            echo "::notice title=Deploy skipped::No deploy settings configured (${required[*]}). Configure them to enable deploys (AW-269)."
            echo "ready=false" >> "$GITHUB_OUTPUT"
          else
            echo "::error title=Deploy partially configured::Missing: ${missing[*]}"
            exit 1
          fi
```

**Out of scope:** the Cloud Run runtime secrets bound by `--set-secrets` (`DATABASE_URL`, `ARCWRIGHT_API_KEY`, the LLM keys, `FIREBASE_SERVICE_ACCOUNT_JSON`) live in GCP Secret Manager, which GitHub cannot inspect. Configuring them and every other part of a working deploy remains Arcwright engine-phase work under AW-269 (#188).

**Approval note:** `AGENTS.md` lists anything touching credential handling as needing explicit approval. This change checks only whether settings are present; the founder approved it with this design.

### 2. Tooling freeze record (D-110)

Append one row to `docs/product/decisions-log.csv`:

- **Decision:** `D-110 Agent and knowledge-base tooling frozen to break-fixes until the Gate 1 call is recorded`
- **Date:** `September 27, 2026`
- **Section:** `Process / Tooling`
- **Status:** `Committed`
- **Tags:** `process; tooling; knowledge-base; nightcap`
- **Rationale** (content to carry):
  - Founder decision.
  - Between 2026-09-01 and 2026-09-27 nearly every commit went to agent and knowledge-base infrastructure while Paper Test #2 v3.0, published 2026-08-31, had no external sessions.
  - Frozen scope: new capability in `team-ai/`, `.claude/agents/`, `.claude/commands/`, `docs/agents/`, `docs/skills/`, the session hooks registered in `.claude/settings.json`, and the knowledge-base scripts.
  - Allowed: break-fixes, meaning changes that restore behavior that previously worked, such as a broken hook or a failing CI check. No new tooling capability.
  - The freeze ends when the Gate 1 decision on v3.0 evidence (pass, narrow v3.x successor, or larger design correction, per `docs/gdd/nightcap/02-validation/98-validation-state-and-remaining-plan.md` step 5) is recorded.
  - `AGENTS.md` is intentionally not changed: a temporary rule does not belong in the permanent always-on file.

### 3. Python 3.11 local setup

Change the `### Python` block under README "Getting Started" to:

```bash
uv venv
. .venv/Scripts/activate
uv pip install -r requirements.txt
pip install "pre-commit>=3.7.0"
pre-commit install
```

Add, directly under it:

- one sentence: `uv venv` reads `.python-version` (3.11), which matches CI. Windows' default `python` may be newer, and mypy then fails on numpy's type stubs.
- the fallback when `uv` is unavailable: `py -3.11 -m venv .venv`.

Nothing else in the README changes.

## Verification

| Item | Before merge | After merge |
|---|---|---|
| Deploy preflight | Both workflow files parse as YAML. The preflight script, run locally in bash, gives the right outcome for none, some, and all settings present. | `gh workflow run deploy-api.yml` and `gh workflow run deploy-web.yml` each finish green, with `deploy` skipped and the "Deploy skipped" notice visible. |
| D-110 | `docs/product/decisions-log.csv` parses with `csv.DictReader`, the new row has exactly six fields, and `scripts/checks/scope_evidence_check.py` passes. | none |
| README | The documented commands, run in a fresh worktree, produce a 3.11 `.venv` in which `python -m ruff check --config pyproject.toml engine api`, `python -m mypy --config-file pyproject.toml engine api` and `python -m pytest engine/tests` pass (the commands behind the Makefile's `lint` and `type` targets; `make` is not installed on the founder's Windows machine). (This exact sequence was run on 2026-09-27.) | none |

## Not in Phase 0

- Configuring GCP or Cloudflare credentials, or making any deploy succeed (Arcwright engine phase, AW-269).
- Enforcing the freeze with hooks or CI checks.
- Other README corrections.
- The malformed Section value in an existing `decisions-log.csv` row.
