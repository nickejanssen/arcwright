---
id: engineeringpractice.superpowers.plans.2026-09-27-phase-0-dev-friction
namespace: engineering-practice
title: Phase 0 Development Friction Implementation Plan
owner: Nico Janssen
status: active
review_by: "2027-03-27"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Phase 0 Development Friction Implementation Plan

> **For agentic workers:** This plan is written to be executed by **Codex** (or any agent) with no prior conversation context. Follow the repository's platform-neutral Implementer skill, `docs/skills/github-task-implementer/SKILL.md` (Codex's discovery mirror is `.agents/skills/github-task-implementer/SKILL.md`; where the two differ, `docs/skills/` is canonical). Work the tasks in order. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop the deploy workflows turning `main` red when no deploy credentials exist, record a tooling freeze as decision D-110, and document a Python 3.11 local setup that matches CI.

**Architecture:** Each deploy workflow gets a `preflight` job that checks whether its required settings are present and gates the unchanged `deploy` job on the result. The freeze is one appended row in `docs/product/decisions-log.csv`. The Python fix is a README edit. No product code (`engine/`, `api/`, `sdk/`, `dashboard/`, `config/`) changes.

**Tech Stack:** GitHub Actions YAML, bash, Python 3.11 standard library plus PyYAML (already installed transitively by `requirements.txt`), `uv`.

**Spec:** `docs/superpowers/specs/2026-09-27-phase-0-dev-friction-design.md` (approved)

**User decisions (already made):**
- "Freeze ends when the Gate 1 call is recorded" (the founder chose this over "engine phase starts" and "fixed date").
- "A. Preflight check": skip with a notice when nothing is configured, fail when partly configured, deploy when fully configured (chosen over a manual-only trigger or disabling in GitHub settings).
- The founder approved all three spec sections, including the credential-presence check that `AGENTS.md` lists as approval-gated ("Secrets or auth").
- "Codex executes this plan."

---

## Ground rules for the executor

- **Collaboration profile:** independent execution. The spec settles every decision. If you hit something the spec and this plan do not answer, stop and ask; do not guess.
- **No GitHub issue exists for this work.** Do not create one. Reference the spec in commits and the PR (`Refs docs/superpowers/specs/2026-09-27-phase-0-dev-friction-design.md`). Skip the Implementer skill's tracker-closing step (section 11).
- **Branch:** create `task/phase-0-dev-friction` from `origin/claude/arcwright-nightcap-phase-plan-a023ca`, which carries the spec and this plan. Your PR targets `main` and will include those two documents.
  ```bash
  git fetch origin
  git switch -c task/phase-0-dev-friction origin/claude/arcwright-nightcap-phase-plan-a023ca
  ```
- **Do not touch** `.claude/`, `.codex/`, `team-ai/`, `docs/agents/`, `docs/skills/`, `AGENTS.md`, or any product code. D-110 freezes tooling, and none of those files are in scope.
- **Line endings:** the repo uses `core.autocrlf=true`, so working-copy files may be CRLF. Edit in place and keep each file's existing line endings.
- **Scratch scripts:** Tasks 2 and 3 use helper scripts. Save them in a temp directory **outside the repository** (referred to below as `$SCRATCH`) and never commit them.
- **Windows:** run shell commands in Git Bash. In Python, launch bash by full path (the harness below does), because a bare `bash` can resolve to the WSL stub.
- **Commits:** conventional subject, one per task, pre-commit hooks enabled. Never use `--no-verify`.

## File map

| File | Change | Responsibility |
|---|---|---|
| `README.md` | Modify the `### Python` block under "Getting Started" (currently lines 121–129) | Local setup that yields Python 3.11 |
| `.github/workflows/deploy-api.yml` | Replace whole file | Preflight gate plus the unchanged Cloud Run deploy |
| `.github/workflows/deploy-web.yml` | Replace whole file | Preflight gate plus the unchanged Cloudflare deploy |
| `docs/product/decisions-log.csv` | Append one row | D-110 freeze record |

---

### Task 1: Python 3.11 local setup (README)

**Goal:** README setup instructions produce a Python 3.11 virtual environment that matches CI, and that environment is what later tasks use.

**Files:**
- Modify: `README.md` (the `### Python` block, lines 121–129)

**Acceptance Criteria:**
- [ ] The `### Python` block uses `uv venv` and `uv pip install -r requirements.txt`, and states the `py -3.11 -m venv .venv` fallback and why 3.11 matters.
- [ ] Following the new block in this checkout yields `.venv` whose `python --version` prints `Python 3.11.x`.
- [ ] In that `.venv`, ruff, mypy and the engine tests pass (commands under Verify).
- [ ] No other README content changes.

**Verify:** `.venv/Scripts/python --version` (Windows) or `.venv/bin/python --version` → `Python 3.11.x`; then the three commands in Step 3 each pass.

**Steps:**

- [ ] **Step 1: Replace the Python block.** The current text is:

````markdown
### Python

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
pip install "pre-commit>=3.7.0"
pre-commit install
```
````

Replace it with exactly:

````markdown
### Python

```bash
uv venv
. .venv/Scripts/activate
uv pip install -r requirements.txt
pip install "pre-commit>=3.7.0"
pre-commit install
```

`uv venv` reads `.python-version` (3.11), which matches CI. Windows' default `python` may be newer than 3.11, and mypy then fails on numpy's type stubs. Without `uv`, create the environment with `py -3.11 -m venv .venv` instead.
````

- [ ] **Step 2: Follow the new instructions in this checkout.** `.venv/` is already gitignored. On Linux or macOS the activate path is `.venv/bin/activate`. If `uv` is missing, use the documented `py -3.11` fallback.

```bash
uv venv
. .venv/Scripts/activate
uv pip install -r requirements.txt
uv pip install ruff==0.15.14 mypy==1.13.0 pytest==8.3.4
python --version
```

Expected: `Python 3.11.x`. (The second install line pins the same tool versions CI's `verify-tasks.yml` installs.)

- [ ] **Step 3: Run the CI-equivalent checks in the new environment.**

```bash
python -m ruff check --config pyproject.toml engine api
python -m mypy --config-file pyproject.toml engine api
python -m pytest engine/tests -q -p no:warnings
```

Expected: `All checks passed!`; `Success: no issues found in 126 source files` (the count may drift slightly); `912 passed, 1 skipped` or more passed, 0 failed. The one skip is the migration test that needs `DATABASE_URL`.

- [ ] **Step 4: Commit.**

```bash
git add README.md
git commit -m "docs(readme): set up the local Python 3.11 environment with uv" -m "Refs docs/superpowers/specs/2026-09-27-phase-0-dev-friction-design.md"
```

---

### Task 2: Deploy preflight for both workflows

**Goal:** Deploy API and Deploy Web skip cleanly with a visible notice when none of their settings exist, fail naming the missing settings when partly configured, and deploy unchanged when fully configured.

**Files:**
- Modify (replace whole file): `.github/workflows/deploy-api.yml`
- Modify (replace whole file): `.github/workflows/deploy-web.yml`
- Scratch only (not committed): `$SCRATCH/check_preflight.py`

**Acceptance Criteria:**
- [ ] Both workflows keep their existing `push` trigger and add `workflow_dispatch:`.
- [ ] Both have a `preflight` job whose `ready` output feeds `deploy` via `needs: preflight` and `if: needs.preflight.outputs.ready == 'true'`.
- [ ] The `deploy` job's steps are byte-for-byte the same as before this change.
- [ ] The preflight step tests only whether values are non-empty and never prints a value.
- [ ] `check_preflight.py` reports PASS for none, some and all cases on both files, and FAIL for both files as they are on `main` before this change.

**Verify:** `python $SCRATCH/check_preflight.py .github/workflows/deploy-api.yml .github/workflows/deploy-web.yml` → six `PASS` lines, exit code 0.

**Steps:**

- [ ] **Step 1: Write the harness to `$SCRATCH/check_preflight.py`.** It extracts the real preflight script from each workflow and runs it under bash with no settings, some settings, and all settings.

```python
import os, shutil, subprocess, sys, tempfile, yaml
BASH = shutil.which("bash")  # full path: a bare "bash" on Windows can hit the WSL stub
failures = 0
for path in sys.argv[1:]:
    wf = yaml.safe_load(open(path, encoding="utf-8"))
    assert "workflow_dispatch" in wf["on"], f"{path}: no workflow_dispatch trigger"
    deploy = wf["jobs"]["deploy"]
    assert deploy["needs"] == "preflight", f"{path}: deploy does not need preflight"
    assert deploy["if"] == "needs.preflight.outputs.ready == 'true'", f"{path}: wrong deploy condition"
    step = wf["jobs"]["preflight"]["steps"][0]
    names = list(step["env"])
    cases = {"none": [], "some": names[:1], "all": names}
    expected = {"none": (0, "ready=false", "::notice title=Deploy skipped::"),
                "some": (1, "", "::error title=Deploy partially configured::"),
                "all": (0, "ready=true", "")}
    for case, present in cases.items():
        with tempfile.NamedTemporaryFile("r", delete=False, suffix=".out") as out:
            out_path = out.name
        env = {k: v for k, v in os.environ.items() if k not in names}
        env.update({n: "x" for n in present})
        env["GITHUB_OUTPUT"] = out_path
        proc = subprocess.run([BASH, "-e", "-c", step["run"]], env=env, capture_output=True, text=True)
        output = open(out_path, encoding="utf-8").read().strip()
        os.unlink(out_path)
        rc, want_out, want_msg = expected[case]
        ok = proc.returncode == rc and output == want_out and proc.stdout.startswith(want_msg)
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'} {os.path.basename(path)} [{case}] rc={proc.returncode} output={output!r}")
sys.exit(1 if failures else 0)
```

- [ ] **Step 2: Confirm the harness fails on the current files.**

Run: `python $SCRATCH/check_preflight.py .github/workflows/deploy-api.yml`
Expected: `AssertionError: .github/workflows/deploy-api.yml: no workflow_dispatch trigger` and a non-zero exit.

- [ ] **Step 3: Replace `.github/workflows/deploy-api.yml` with exactly:**

```yaml
---
name: Deploy API

"on":
  push:
    branches:
      - main
    paths:
      - "api/**"
      - "engine/**"
      - "config/**"
      - "Dockerfile"
  workflow_dispatch:

permissions:
  contents: read
  id-token: write

env:
  IMAGE_NAME: arcwright-api

jobs:
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

  deploy:
    name: Build and Deploy Cloud Run API
    needs: preflight
    if: needs.preflight.outputs.ready == 'true'
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: >-
            ${{ vars.GCP_WORKLOAD_IDENTITY_PROVIDER }}
          service_account: ${{ vars.GCP_SERVICE_ACCOUNT }}

      - name: Set up Google Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker for Artifact Registry
        run: >-
          gcloud auth configure-docker
          ${{ secrets.GCP_REGION }}-docker.pkg.dev --quiet

      - name: Build and push API image
        run: |
          IMAGE_URI="${{ secrets.GCP_REGION }}-docker.pkg.dev"
          IMAGE_URI="$IMAGE_URI/${{ secrets.GCP_PROJECT_ID }}"
          IMAGE_URI="$IMAGE_URI/${{ secrets.AR_REPO }}"
          IMAGE_URI="$IMAGE_URI/${{ env.IMAGE_NAME }}:${{ github.sha }}"
          docker build -t "$IMAGE_URI" .
          docker push "$IMAGE_URI"

      - name: Deploy API to Cloud Run
        run: |
          IMAGE_URI="${{ secrets.GCP_REGION }}-docker.pkg.dev"
          IMAGE_URI="$IMAGE_URI/${{ secrets.GCP_PROJECT_ID }}"
          IMAGE_URI="$IMAGE_URI/${{ secrets.AR_REPO }}"
          IMAGE_URI="$IMAGE_URI/${{ env.IMAGE_NAME }}:${{ github.sha }}"
          SECRET_BINDINGS="DATABASE_URL=DATABASE_URL:latest"
          SECRET_BINDINGS="$SECRET_BINDINGS,ARCWRIGHT_API_KEY=ARCWRIGHT_API_KEY:latest"
          SECRET_BINDINGS="$SECRET_BINDINGS,PRIMARY_LLM_API_KEY=PRIMARY_LLM_API_KEY:latest"
          SECRET_BINDINGS="$SECRET_BINDINGS,SECONDARY_LLM_API_KEY=SECONDARY_LLM_API_KEY:latest"
          SECRET_BINDINGS="$SECRET_BINDINGS,FIREBASE_SERVICE_ACCOUNT_JSON=FIREBASE_SERVICE_ACCOUNT_JSON:latest"
          gcloud \
            run deploy arcwright-api \
            --project="${{ secrets.GCP_PROJECT_ID }}" \
            --region="${{ secrets.GCP_REGION }}" \
            --image="$IMAGE_URI" \
            --allow-unauthenticated \
            --set-secrets="$SECRET_BINDINGS"
```

- [ ] **Step 4: Replace `.github/workflows/deploy-web.yml` with exactly:**

```yaml
---
name: Deploy Web

"on":
  push:
    branches:
      - main
    paths:
      - "nightcap-web/**"
  workflow_dispatch:

permissions:
  contents: read

jobs:
  preflight:
    name: Check deploy configuration
    runs-on: ubuntu-latest
    outputs:
      ready: ${{ steps.check.outputs.ready }}

    steps:
      - name: Check required deploy settings
        id: check
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
        run: |
          required=(CLOUDFLARE_API_TOKEN CLOUDFLARE_ACCOUNT_ID)
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

  deploy:
    name: Build and Deploy Nightcap Web
    needs: preflight
    if: needs.preflight.outputs.ready == 'true'
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Set up Node.js
        uses: actions/setup-node@v6
        with:
          node-version: "20"

      - name: Install root tooling dependencies
        run: npm ci

      - name: Install dependencies
        run: npm ci --prefix nightcap-web

      - name: Build web app
        run: npm run build --prefix nightcap-web

      - name: Deploy with Wrangler
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
        run: npx --yes wrangler@4.105.0 deploy --env production
        working-directory: nightcap-web
```

- [ ] **Step 5: Run the harness on the new files.**

Run: `python $SCRATCH/check_preflight.py .github/workflows/deploy-api.yml .github/workflows/deploy-web.yml`
Expected, exit code 0:
```
PASS deploy-api.yml [none] rc=0 output='ready=false'
PASS deploy-api.yml [some] rc=1 output=''
PASS deploy-api.yml [all] rc=0 output='ready=true'
PASS deploy-web.yml [none] rc=0 output='ready=false'
PASS deploy-web.yml [some] rc=1 output=''
PASS deploy-web.yml [all] rc=0 output='ready=true'
```

- [ ] **Step 6: Confirm the deploy steps are unchanged.** In `git diff .github/workflows/`, the only changes are: the added `workflow_dispatch:` line, the added `preflight` job, and the two added lines (`needs:`, `if:`) in `deploy`. Any other `+` or `-` line inside `deploy`'s steps is a mistake; fix it before committing. (If line endings make the whole file show as changed, use `git diff --ignore-cr-at-eol`.)

- [ ] **Step 7: Commit.**

```bash
git add .github/workflows/deploy-api.yml .github/workflows/deploy-web.yml
git commit -m "ci(deploy): skip deploys cleanly until deploy settings are configured" -m "Refs docs/superpowers/specs/2026-09-27-phase-0-dev-friction-design.md"
```

---

### Task 3: Record the tooling freeze (D-110)

**Goal:** `docs/product/decisions-log.csv` gains exactly one correctly quoted D-110 row recording the freeze, its scope, its break-fix exception and its end condition.

**Files:**
- Modify (append one row): `docs/product/decisions-log.csv`
- Scratch only (not committed): `$SCRATCH/append_d110.py`, `$SCRATCH/check_d110.py`

**Acceptance Criteria:**
- [ ] The last row's `Decision` starts with `D-110 `, and D-110 appears exactly once.
- [ ] The row parses with `csv.DictReader` into exactly the six columns `Decision, Date, Rationale, Section, Status, Tags`, with `Section` = `Process / Tooling` and `Status` = `Committed`.
- [ ] `git diff docs/product/decisions-log.csv` shows exactly one added line and no removed lines.
- [ ] `python scripts/checks/scope_evidence_check.py` prints `scope-evidence-check: OK`.

**Verify:** `python $SCRATCH/check_d110.py` → `D-110 OK (N rows)`; `git diff --numstat docs/product/decisions-log.csv` → `1	0	docs/product/decisions-log.csv`.

**Steps:**

- [ ] **Step 1: Write the checker to `$SCRATCH/check_d110.py`.**

```python
import csv, sys
path = sys.argv[1] if len(sys.argv) > 1 else "docs/product/decisions-log.csv"
rows = list(csv.DictReader(open(path, encoding="utf-8", newline="")))
last = rows[-1]
assert last["Decision"].startswith("D-110 "), last["Decision"][:40]
assert None not in last and len(last) == 6, f"field count {len(last)}"
assert last["Section"] == "Process / Tooling" and last["Status"] == "Committed"
assert sum(r["Decision"].startswith("D-110 ") for r in rows) == 1
print(f"D-110 OK ({len(rows)} rows)")
```

- [ ] **Step 2: Run it before appending.**

Run: `python $SCRATCH/check_d110.py`
Expected: `AssertionError` naming D-109's text (the last row is still D-109).

- [ ] **Step 3: Write the append script to `$SCRATCH/append_d110.py`.** It uses the `csv` module for quoting, matches the file's line ending, and refuses to run twice.

```python
import csv, io, sys

path = sys.argv[1] if len(sys.argv) > 1 else "docs/product/decisions-log.csv"
row = [
    "D-110 Agent and knowledge-base tooling frozen to break-fixes until the Gate 1 call is recorded",
    "September 27, 2026",
    "Founder decision (2026-09-27) while planning the return to Nightcap validation. "
    "Between 2026-09-01 and 2026-09-27 nearly every commit went to agent and knowledge-base "
    "infrastructure while Paper Test #2 v3.0, published 2026-08-31, had no external sessions. "
    "Frozen: new capability in team-ai/, .claude/agents/, .claude/commands/, docs/agents/, "
    "docs/skills/, the session hooks registered in .claude/settings.json, and the knowledge-base "
    "scripts. Allowed: break-fixes, meaning changes that restore behavior that previously worked, "
    "such as a broken hook or a failing CI check; no new tooling capability. The freeze ends when "
    "the Gate 1 decision on v3.0 evidence (pass, narrow v3.x successor, or larger design "
    "correction, per docs/gdd/nightcap/02-validation/98-validation-state-and-remaining-plan.md "
    "step 5) is recorded. AGENTS.md is intentionally unchanged: a temporary rule does not belong "
    "in the permanent always-on file. Spec: "
    "docs/superpowers/specs/2026-09-27-phase-0-dev-friction-design.md.",
    "Process / Tooling",
    "Committed",
    "process; tooling; knowledge-base; nightcap",
]

raw = open(path, "rb").read()
if b"D-110 " in raw:
    sys.exit("D-110 already present; not appending")
newline = "\r\n" if raw.endswith(b"\r\n") or (not raw.endswith(b"\n") and b"\r\n" in raw) else "\n"
buf = io.StringIO()
csv.writer(buf, lineterminator=newline).writerow(row)
with open(path, "ab") as f:
    if not raw.endswith(b"\n"):
        f.write(newline.encode())
    f.write(buf.getvalue().encode("utf-8"))
print(f"appended D-110 to {path}")
```

- [ ] **Step 4: Append, then check.**

```bash
python $SCRATCH/append_d110.py
python $SCRATCH/check_d110.py
git diff --numstat docs/product/decisions-log.csv
python scripts/checks/scope_evidence_check.py
```

Expected: `appended D-110 to docs/product/decisions-log.csv`; `D-110 OK (193 rows)` (the count may differ if rows were added upstream); `1	0	docs/product/decisions-log.csv`; `scope-evidence-check: OK`.

- [ ] **Step 5: Commit.**

```bash
git add docs/product/decisions-log.csv
git commit -m "docs(decisions): D-110 freeze tooling to break-fixes until the Gate 1 call" -m "Refs docs/superpowers/specs/2026-09-27-phase-0-dev-friction-design.md"
```

---

### Task 4: Full verification and pull request

**Goal:** All repository checks pass on the branch, and a PR to `main` reports every acceptance criterion with evidence.

**Files:** none changed (verification and PR only)

**Acceptance Criteria:**
- [ ] `git status` shows a clean tree, with nothing staged or committed under `.claude/`, `.codex/`, `.venv/` or `team-ai/`.
- [ ] The branch contains exactly these changed paths relative to `origin/main`: `README.md`, `.github/workflows/deploy-api.yml`, `.github/workflows/deploy-web.yml`, `docs/product/decisions-log.csv`, `docs/superpowers/specs/2026-09-27-phase-0-dev-friction-design.md`, `docs/superpowers/plans/2026-09-27-phase-0-dev-friction.md`, `docs/superpowers/plans/2026-09-27-phase-0-dev-friction.md.tasks.json`.
- [ ] The local checks in Step 2 pass.
- [ ] The PR is open against `main`, and its CI checks (CI, CodeQL, Verify Roadmap Tasks, team-ai) pass.

**Verify:** `git diff --name-only origin/main...HEAD` → exactly the seven paths above; `gh pr checks` → all passing.

**Steps:**

- [ ] **Step 1: Check the changed paths.**

```bash
git status
git diff --name-only origin/main...HEAD
```

- [ ] **Step 2: Run the local checks in the 3.11 `.venv`.**

```bash
python -m ruff check --config pyproject.toml engine api
python -m ruff format --check engine api
python -m mypy --config-file pyproject.toml engine api
python -m pytest engine/tests -q -p no:warnings
python $SCRATCH/check_preflight.py .github/workflows/deploy-api.yml .github/workflows/deploy-web.yml
python $SCRATCH/check_d110.py
python scripts/checks/scope_evidence_check.py
```

- [ ] **Step 3: Push and open the PR.** Title: `chore: Phase 0 — quiet unconfigured deploys, freeze tooling (D-110), Python 3.11 setup`. The body must list:
  - one line per change;
  - each acceptance criterion from Tasks 1–3 with its evidence (paste the six `PASS` lines and `D-110 OK`);
  - a note that the deploy behavior can only be confirmed after merge (Task 5);
  - `Refs docs/superpowers/specs/2026-09-27-phase-0-dev-friction-design.md`.

```bash
git push -u origin task/phase-0-dev-friction
gh pr create --base main --title "chore: Phase 0 — quiet unconfigured deploys, freeze tooling (D-110), Python 3.11 setup" --body-file "$SCRATCH/pr-body.md"
```

- [ ] **Step 4: Wait for CI, then report the results to the founder.** Do not merge; the founder merges.

---

### Task 5: Post-merge confirmation of the deploy skip

**Goal:** After the founder merges the PR, confirm on GitHub that each deploy workflow run on `main` ends green with `deploy` skipped and the "Deploy skipped" notice shown.

**Files:** none

**Acceptance Criteria:**
- [ ] A manually dispatched Deploy API run on `main` concludes `success`, with job `Check deploy configuration` succeeded, job `Build and Deploy Cloud Run API` skipped, and a `Deploy skipped` annotation.
- [ ] The same holds for Deploy Web, with job `Build and Deploy Nightcap Web` skipped.

**Verify:** `gh run view <run-id> --json conclusion,jobs --jq '{conclusion, jobs: [.jobs[] | {name, conclusion}]}'` → `conclusion: "success"`, preflight `success`, deploy `skipped`.

**Steps:**

- [ ] **Step 1: Only after the founder confirms the merge,** dispatch both workflows:

```bash
gh workflow run deploy-api.yml --ref main
gh workflow run deploy-web.yml --ref main
```

- [ ] **Step 2: Find each new run and inspect it once it completes.** Run each `gh run view` command separately with the numeric ID the list command prints.

```bash
gh run list --workflow deploy-api.yml --limit 1 --json databaseId,status,conclusion
gh run list --workflow deploy-web.yml --limit 1 --json databaseId,status,conclusion
gh run view <run-id> --json conclusion,jobs --jq '{conclusion, jobs: [.jobs[] | {name, conclusion}]}'
gh run view <run-id>
```

Expected: in the JSON, `"conclusion": "success"`, the preflight job `success`, the deploy job `skipped`. The plain `gh run view` output shows a `Deploy skipped` notice under ANNOTATIONS.

- [ ] **Step 3: Report the two run URLs to the founder.** If `gh` cannot dispatch runs in your environment, ask the founder to click **Run workflow** on each workflow's Actions page, then inspect those runs.

---

## Spec coverage

| Spec requirement | Task |
|---|---|
| Deploy preflight: required settings, three outcomes, `needs` plus `if`, deploy steps unchanged | 2 |
| `workflow_dispatch` on both workflows | 2 |
| Presence-only check, no values printed | 2 (script content, AC) |
| Cloud Run runtime secrets out of scope | Not implemented, by design |
| D-110 row: wording, Section, Status, Tags, end condition | 3 |
| `AGENTS.md` unchanged | Ground rules; Task 4 path check |
| README `uv venv` block, fallback, one-sentence reason, nothing else changed | 1 |
| Verification: YAML parse plus three cases before merge | 2 |
| Verification: dispatch after merge, green with skip | 5 |
| Verification: CSV parse, one added line, scope-evidence check | 3 |
| Verification: README commands produce a passing 3.11 env | 1 |
