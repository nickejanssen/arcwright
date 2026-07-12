# Phase 0 Cleanup + Phase 1 One-Command Rehearsal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Get main fully green, make the repo's roadmap record truthful, and replace the 415-line five-terminal rehearsal procedure with one command so Rehearsal 1 (first-ever real-human Nightcap session) can actually run.

**Architecture:** Phase 0 is surgical cleanup (test fixes, roadmap-record corrections, branch hygiene) with no production behavior changes except possibly one TMST reconnect fix. Phase 1 adds a Python orchestrator (`scripts/rehearsal.py`) that boots the existing local stack (Postgres via docker compose → Alembic → uvicorn API → dashboard dev server → cloudflared quick tunnel), health-checks each layer, and prints the two URLs the founder needs; plus a live-stack smoke script and a one-page quickstart. No engine logic changes; the orchestrator composes existing entry points only.

**Tech Stack:** Python 3.11+ stdlib (subprocess, urllib), docker compose, Alembic, uvicorn, Vite dev server (existing `/v1` proxy to :8000), cloudflared quick tunnel (no account), GNU make via existing `Makefile`/`make.cmd`.

**User decisions (already made):**
- Rehearsal 1 never actually ran; the record must be corrected (successor task, no AW-number reuse).
- Approach is "both, staged": one-command local rehearsal now; cloud deploy (AW-269) before Rehearsal 2/M6.
- Full cleanup sprint approved (tests, branches, statuses, AW-270 collision).
- Spec: `docs/specs/0067-development-survey-and-path-to-first-playtest.md` (Phases 0–1 only; Phases 2–4 planned after Rehearsal 1 outcomes).

---

## Context an engineer needs

- **Repo layout:** `engine/` (Python engine), `api/` (FastAPI), `dashboard/` (Vite/React host+player web surface used for local rehearsal; it proxies `/v1` → `http://localhost:8000`), `nightcap-web/` (Cloudflare Workers runtime — NOT used in local rehearsal), `docs/roadmap/` (manifest `index.json` + task files), `docs/roadmap/operations/rehearsal-1-runbook.md` (the 415-line procedure being replaced).
- **Failing tests (6) on main:**
  - 5 × `api/tests/test_costs_api.py::TestGetSessionCostSummary::*` — the fixture posts `{"arc_id": "test-arc"}`; AW-256 (commit `ca5ea53`, PR #191) made `create_session` validate arc IDs via `_load_nightcap_arc_definition` and raise `SessionStateError: Unknown arc: 'test-arc'`. Working tests (`api/tests/test_sessions_api.py:97`) use `"nightcap-v1"`.
  - 1 × `api/tests/test_mini_games_api.py::TestGetActiveMiniGame::test_tmst_spotlight_phase_state_is_authorized_for_reconnect` — endpoint returns all of the player's own submissions (input + vote) in `my_submissions`; test expects vote-only during spotlight. Needs diagnosis (Task 2).
- **Conventions:** conventional commits; run `python -m ruff check engine api` and `python -m ruff format --check engine api` before claiming done; tests written with changes (`docs/conventions/testing.md`). Never touch `.claude/`, `.codex/`, `.cursor/`. Hard rule: no new dependencies without approval — every Phase 1 script below is stdlib-only on purpose.
- **Tracker convention:** GitHub Issues is the live tracker (D-049); the manifest `docs/roadmap/index.json` records canonical IDs and backfills live issue numbers. New tasks get the next free AW number — highest today is AW-272, so the new rehearsal task is **AW-273**.
- **Required `.env` variables** (read by engine/api via `os.environ`): `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`, `ARCWRIGHT_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`. A template exists at `.env.example`; local-dev Postgres values are `arcwright`/`arcwright`/`arcwright`.

---

### Task 1: Fix the five costs-API test failures

**Goal:** `api/tests/test_costs_api.py` passes by using a registered arc ID in the session-creation fixture.

**Files:**
- Modify: `api/tests/test_costs_api.py` (line 77 fixture; audit all `"test-arc"` occurrences)

**Acceptance Criteria:**
- [ ] `python -m pytest api/tests/test_costs_api.py -q` → all pass, 0 failures
- [ ] No production code changed

**Verify:** `python -m pytest api/tests/test_costs_api.py -q` → `... passed` with 0 failed

**Steps:**

- [ ] **Step 1: Confirm the failure mode is the arc registry**

Run: `python -m pytest "api/tests/test_costs_api.py::TestGetSessionCostSummary::test_known_session_returns_200" -q`
Expected: FAIL with `SessionStateError: Unknown arc: 'test-arc'` raised from `engine/session/service.py:106`.

- [ ] **Step 2: Change the session-creation fixture to a registered arc**

In `api/tests/test_costs_api.py:77`, change:

```python
    resp = client.post("/v1/sessions", json={"arc_id": "test-arc"})
```

to:

```python
    resp = client.post("/v1/sessions", json={"arc_id": "nightcap-v1"})
```

Then run `grep -n "test-arc" api/tests/test_costs_api.py`. For each remaining occurrence, apply this rule: occurrences that flow into `POST /v1/sessions` must become `"nightcap-v1"`; occurrences used only as a **query filter** (e.g. line 131 `GET /v1/usage?arc_id=test-arc`) stay `"test-arc"` **if** the test asserts filter behavior on a nonexistent arc — read each assertion before deciding. If an assertion counts usage rows for the created session, the filter value must match the arc the session was created with.

- [ ] **Step 3: Run the file's suite**

Run: `python -m pytest api/tests/test_costs_api.py -q`
Expected: PASS, 0 failed.

- [ ] **Step 4: Commit**

```bash
git add api/tests/test_costs_api.py
git commit -m "fix(tests): use registered arc id in costs API fixtures broken by AW-256 validation"
```

---

### Task 2: Diagnose and fix the TMST reconnect `my_submissions` failure

**Goal:** `test_tmst_spotlight_phase_state_is_authorized_for_reconnect` passes, with the fix applied to whichever side (endpoint or test) contradicts the TMST contract.

**Files:**
- Read first: `docs/specs/0061-aw-258-tell-me-something-true.md` (line ~406: "reconnect exposes only authorized state"), `docs/roadmap/tasks/AW-264-tmst-api-events-and-sdk.md` (line 36)
- Modify (one of): `api/routers/mini_games.py:346-378` OR `api/tests/test_mini_games_api.py:~460-525`

**Acceptance Criteria:**
- [ ] The chosen fix is justified in the commit message by citing spec 0061 / AW-264 language
- [ ] `python -m pytest api/tests/test_mini_games_api.py -q` → all pass
- [ ] Full suite green: `python -m pytest engine/tests api/tests tests -q` → 0 failed

**Verify:** `python -m pytest engine/tests api/tests tests -q` → `513 passed` (± the known `DATABASE_URL` skip), 0 failed

**Steps:**

- [ ] **Step 1: Reproduce and read both sides**

Run: `python -m pytest "api/tests/test_mini_games_api.py::TestGetActiveMiniGame::test_tmst_spotlight_phase_state_is_authorized_for_reconnect" -q`
Expected: FAIL — `my_submissions` contains `tmst-input-self` and `tmst-vote-1`; the test expects only `tmst-vote-1`.

Read `api/routers/mini_games.py:346-353`: players get `[s for s in run.submissions if s.character_id == character_id]` — all own submissions, no phase scoping.

- [ ] **Step 2: Decide which side is wrong**

Decision rule (from spec 0061 "reconnect exposes only authorized state" and AW-264 "reconnect exposes only authorized state ... privacy test covering ... reconnect"):
- A player's **own** input submission is authorized state for that player — showing it leaks nothing. If neither spec 0061 nor the AW-265 task file (`docs/roadmap/tasks/AW-265-tmst-web-rendering-four-phases.md`) requires phase-scoped filtering of `my_submissions`, the **test expectation is stale** → fix the test.
- If either doc states the reconnect payload during spotlight must contain only spotlight-phase submissions (check for words like "phase-scoped", "current phase", "vote status only"), the **endpoint** must filter → fix the endpoint.

Check git context: the test landed in `26f960f` (PR #198) and the renderer in `a42c01b` (PR #199). `git log --oneline 26f960f..HEAD -- api/routers/mini_games.py` shows whether the endpoint changed after the test was written.

- [ ] **Step 3a (if test is stale): fix the expectation**

In `api/tests/test_mini_games_api.py:515`, change the assertion to expect both own submissions in seeded order:

```python
        assert body["my_submissions"] == [
            {
                "submission_id": "tmst-input-self",
                "is_accepted": True,
                "rejection_reason": None,
            },
            {
                "submission_id": "tmst-vote-1",
                "is_accepted": True,
                "rejection_reason": None,
            },
        ]
```

- [ ] **Step 3b (if endpoint must phase-scope): filter votes during spotlight**

In `api/routers/mini_games.py`, after the existing `visible_submissions` block (lines 346–353), add phase scoping for TMST spotlight reconnects:

```python
    if (
        claims.role == "player"
        and run.game_id == _TMST_GAME_ID
        and isinstance(run.runtime_state, dict)
        and run.runtime_state.get("phase") == "spotlight"
    ):
        visible_submissions = [
            s
            for s in visible_submissions
            if s.submission_id.startswith("tmst-vote")
        ]
```

**Caution:** do not key off submission-ID prefixes if the runtime records a structured submission `kind`/`payload.type` — inspect one seeded submission in the test (`payload` field) and filter on the structured field instead. Prefix matching is the fallback only if no structured field exists.

- [ ] **Step 4: Run the full suite**

Run: `python -m pytest engine/tests api/tests tests -q`
Expected: 0 failed (1 pre-existing skip when `DATABASE_URL` unset is acceptable).

- [ ] **Step 5: Commit**

```bash
git add api/tests/test_mini_games_api.py api/routers/mini_games.py
git commit -m "fix(api): align TMST reconnect my_submissions with spec 0061 authorized-state contract"
```

(Adjust the message to name which side was fixed and why.)

---

### Task 3: Correct the Rehearsal 1 record (AW-273)

**Goal:** The repo and tracker truthfully record that Rehearsal 1 never ran, via a new task AW-273 that owns the actual execution.

**Files:**
- Create: `docs/roadmap/tasks/AW-273-rehearsal-1-execution.md`
- Modify: `docs/roadmap/index.json` (add AW-273 to `tasks`), `docs/roadmap/tasks/AW-259-rehearsal-1-m4-exit.md` (status note)

**Acceptance Criteria:**
- [ ] AW-273 task file exists with dependencies on the Phase 1 tooling and states plainly that AW-259/#176 was closed without execution
- [ ] `docs/roadmap/index.json` parses as valid JSON and contains AW-273
- [ ] GitHub issue created for AW-273 and its number backfilled into the manifest
- [ ] A comment on issue #176 links forward to the AW-273 issue

**Verify:** `python -c "import json; d=json.load(open('docs/roadmap/index.json')); print([t['id'] for t in d['tasks'] if t['id']=='AW-273'])"` → `['AW-273']`

**Steps:**

- [ ] **Step 1: Create `docs/roadmap/tasks/AW-273-rehearsal-1-execution.md`**

```markdown
# AW-273: Rehearsal 1 Execution - First Real-Human Nightcap Session

**Milestone / Epic:** M5 (M4 exit-gate debt; no epic)
**Size:** M
**Status:** Planned

## Plain-English Summary

Run the first real-human Nightcap session. AW-259 (#176) defined this work
but was closed on 2026-06-27 without the session being executed; the M4 exit
gate ("real humans playing end-to-end on real devices") has not actually been
passed. This task owns the actual execution using the one-command rehearsal
stack (`make rehearsal`) and the quickstart runbook.

## Definition of Done

- Founder solo smoke test completed (founder plus two phone browser tabs).
- Real-human session: founder plus at least three invitees on real devices,
  through join, host setup, shared display, private player events, both
  production mini-games (Crime Scene Smash, Evidence Locker), accusation,
  and killer reveal.
- Blocker log filled from
  `docs/roadmap/operations/blocker-log-template.md` and committed under
  `docs/roadmap/operations/`.
- Outcomes recorded on this task's GitHub issue before it is closed.

## Dependencies

- `make rehearsal` orchestrator and smoke script (this plan, Tasks 6-7)
- Quickstart runbook (this plan, Task 8)

## References

- Supersedes-for-execution: AW-259 (#176), AW-231 (#84), AW-254 (#148)
- Spec: docs/specs/0067-development-survey-and-path-to-first-playtest.md
```

- [ ] **Step 2: Add an execution-status note to `docs/roadmap/tasks/AW-259-rehearsal-1-m4-exit.md`**

Directly under the `**Status:** Planned` line, add:

```markdown
> **Execution note (2026-07-11):** Issue #176 was closed on 2026-06-27
> without the rehearsal being run. The real-human execution is tracked by
> AW-273 (docs/roadmap/tasks/AW-273-rehearsal-1-execution.md).
```

- [ ] **Step 3: Register AW-273 in the manifest**

In `docs/roadmap/index.json`, append to the `tasks` array (after the AW-272 entry, before the closing `]`):

```json
    {
      "id": "AW-273",
      "title": "Rehearsal 1 Execution - First Real-Human Nightcap Session",
      "milestone": "M5",
      "epic": null,
      "size": "M",
      "depends_on": [],
      "path": "docs/roadmap/tasks/AW-273-rehearsal-1-execution.md",
      "epic_id": null
    }
```

Validate: `python -c "import json; json.load(open('docs/roadmap/index.json'))"` → no output, exit 0.

- [ ] **Step 4: Create the GitHub issue and backfill**

```bash
gh issue create --title "AW-273: Rehearsal 1 Execution — First Real-Human Nightcap Session" \
  --milestone "M5: Hardening + Proof Prerequisites" --label task,size:M,M5 \
  --body-file docs/roadmap/tasks/AW-273-rehearsal-1-execution.md
```

Take the returned issue number `N` and add to the AW-273 manifest entry:

```json
      "github": {
        "issue_number": N,
        "url": "https://github.com/nickejanssen/arcwright/issues/N"
      },
```

Then comment on the old issue:

```bash
gh issue comment 176 --body "Correction: this issue was closed on 2026-06-27 without the rehearsal being executed. The real-human execution is now tracked in AW-273 (#N)."
```

- [ ] **Step 5: Commit**

```bash
git add docs/roadmap/tasks/AW-273-rehearsal-1-execution.md docs/roadmap/tasks/AW-259-rehearsal-1-m4-exit.md docs/roadmap/index.json
git commit -m "docs(roadmap): file AW-273 rehearsal execution task; record that AW-259 closed unexecuted"
```

---

### Task 4: Sync roadmap status metadata and resolve the AW-270 ID collision

**Goal:** Manifest and task-file statuses match GitHub reality; AW-270 unambiguously means "Authorial Intent Block".

**Files:**
- Modify: `docs/roadmap/index.json`, task files under `docs/roadmap/tasks/` whose GitHub issues are closed, `docs/roadmap/README.md` (collision note)

**Acceptance Criteria:**
- [ ] Manifest `milestones[].status`: M1–M4 `"complete"`, M5 `"active"`, M6 `"planned"`, M0 unchanged (`"overridden"`)
- [ ] Manifest `epics[].status`: epics whose GitHub epic issues are closed → `"complete"`; M5-E `"complete"`; M5-F `"active"`; remaining M5/M6 epics `"planned"` or `"active"` per open issue state
- [ ] Task files for closed issues carry `**Status:** Complete`; AW-259's status reads `Closed unexecuted (see AW-273)`
- [ ] A note in `docs/roadmap/README.md` records that closed issue #190 used the label "AW-270" for the rehearsal lobby before AW-270 was assigned to Authorial Intent Block (#202), and that AW numbers are never reused
- [ ] `python -c "import json; json.load(open('docs/roadmap/index.json'))"` exits 0

**Verify:** `python - <<'EOF'` script below prints `OK`

```python
import json
d = json.load(open("docs/roadmap/index.json"))
ms = {m["id"]: m["status"] for m in d["milestones"]}
assert ms["M1"] == ms["M2"] == ms["M3"] == ms["M4"] == "complete", ms
assert ms["M5"] == "active", ms
print("OK")
```

**Steps:**

- [ ] **Step 1: Pull ground truth from GitHub**

```bash
gh issue list --state all --limit 250 --json number,title,state \
  --template '{{range .}}{{.number}}	{{.state}}	{{.title}}{{"\n"}}{{end}}' > /tmp/issue-truth.tsv
```

(Windows: write to the session scratchpad instead of `/tmp`.) Every status edit below must agree with this file; where the file and this plan disagree, the file wins.

- [ ] **Step 2: Update manifest statuses**

In `docs/roadmap/index.json`: set `status` to `"complete"` on milestones M1–M4 and on every epic whose epic issue is CLOSED in the truth file (M1-A…E, M2-A…E, M3-A…D, M4-A…E, M5-E). Set M5 milestone and M5-F to `"active"`. Leave open epics as `"planned"`.

- [ ] **Step 3: Update task-file status headers**

For each task file in `docs/roadmap/tasks/` whose issue is CLOSED in the truth file, change `**Status:** Planned` (or similar) to `**Status:** Complete`. For AW-259 use `**Status:** Closed unexecuted (see AW-273)`. Batch carefully — statuses live on the line starting `**Status:**`. Do not touch any other content.

- [ ] **Step 4: Record the AW-270 collision**

In `docs/roadmap/README.md`, add under a `## Task ID hygiene` heading (create it if absent):

```markdown
## Task ID hygiene

AW numbers are never reused. Historical exception: closed issue #190
("Nightcap Rehearsal Lobby", June 2026) was mistakenly labeled AW-270 before
AW-270 was permanently assigned to "Authorial Intent Block" (#202, ADR-0012).
Any reference to AW-270 dated before 2026-07-11 may mean the lobby work;
verify against the issue number, not the AW label.
```

Also comment on the closed issue:

```bash
gh issue comment 190 --body "Task-ID correction: this issue's 'AW-270' label predates the permanent assignment of AW-270 to Authorial Intent Block (#202). Treat this issue as unlabeled lobby work. See docs/roadmap/README.md → Task ID hygiene."
```

- [ ] **Step 5: Validate and commit**

Run the Verify script above → `OK`.

```bash
git add docs/roadmap/index.json docs/roadmap/tasks docs/roadmap/README.md
git commit -m "docs(roadmap): sync statuses with tracker truth; record AW-270 id collision"
```

---

### Task 5: Branch hygiene

**Goal:** Local branches reduced to `main` plus intentional work; the parked cloud-deploy runbook work is in a PR, not stranded.

**Files:** none (git refs only), PR for `docs/cloud-deploy-runbook-expansion`

**Acceptance Criteria:**
- [ ] Every deleted branch was verified squash-merged (its diff vs main is empty or its PR is merged) BEFORE deletion
- [ ] `docs/cloud-deploy-runbook-expansion` has an open PR
- [ ] `git branch` afterwards lists only `main` (plus any branch that failed verification, called out to the founder rather than deleted)

**Verify:** `git branch --list` → `* main` only (or main + explicitly-reported keepers)

**Steps:**

- [ ] **Step 1: Verify each candidate is truly merged**

For each of: `claude/quirky-poincare-da6f1c`, `claude/hungry-pare-0ca5a7`, `claude/thirsty-edison-7eada6`, `pr-151`, `pr-205`, `chore/dashboard-build-artifacts`, `docs/aw-254-gate-aw-257-precursor`, `docs/m1-epic-e-spec-refinements`, `task/AW-105-knowledge-graph-api`, `task/AW-6-full-alembic-migration`:

```bash
git diff main...BRANCH --stat
```

Empty diff → squash-merged or obsolete → safe. Non-empty diff → check whether a merged PR contains the same changes (`gh pr list --state merged --search "BRANCH"`). Known-good from the survey: `pr-205` → merged PR #205; `claude/hungry-pare-0ca5a7` → merged PR #194; `claude/thirsty-edison-7eada6` → merged PR #191. If any branch has real unmerged content other than `docs/cloud-deploy-runbook-expansion`, DO NOT delete it — list it in the final report for the founder.

- [ ] **Step 2: PR the parked runbook branch**

```bash
git push -u origin docs/cloud-deploy-runbook-expansion
gh pr create --head docs/cloud-deploy-runbook-expansion \
  --title "docs(operations): expand cloud deploy runbook with full GCP, Cloudflare, and Firebase setup steps" \
  --body "Parked during the ADR-0012 rollout (see a5e8f95). Un-parks the cloud-deploy runbook expansion ahead of Phase 3 (AW-269).

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```

- [ ] **Step 3: Delete verified branches**

```bash
git branch -D claude/quirky-poincare-da6f1c claude/hungry-pare-0ca5a7 claude/thirsty-edison-7eada6 pr-151 pr-205 chore/dashboard-build-artifacts docs/aw-254-gate-aw-257-precursor docs/m1-epic-e-spec-refinements task/AW-105-knowledge-graph-api task/AW-6-full-alembic-migration
```

(Remove from this list any branch Step 1 flagged as unmerged.)

- [ ] **Step 4: Report**

No commit (refs only). Post the kept/deleted table in the task completion report.

---

### Task 6: `make rehearsal` orchestrator

**Goal:** One command boots the full local rehearsal stack with per-layer health checks and prints the host URL and player join URL.

**Files:**
- Create: `scripts/rehearsal.py`
- Modify: `Makefile` (add `rehearsal`, `rehearsal-stop` targets)

**Acceptance Criteria:**
- [ ] `make rehearsal` from a cold machine (Docker running, `.env` present) reaches "READY" and prints tunnel URL + local host URL
- [ ] Missing/incomplete `.env` fails with the exact variable names and the fix, before anything boots
- [ ] Each layer failure names the layer and the remediation (the script never exits with a bare stack trace for an expected failure)
- [ ] Ctrl+C tears down all child processes; `make rehearsal-stop` stops the Docker database
- [ ] Stdlib-only (no new dependencies)

**Verify:** `make rehearsal` → output ends with a block containing `PLAYER JOIN URL: https://<random>.trycloudflare.com` and `HOST URL (this machine): http://localhost:5173`; Ctrl+C exits cleanly; `docker compose ps` afterwards shows postgres still up until `make rehearsal-stop`.

**Steps:**

- [ ] **Step 1: Write `scripts/rehearsal.py`**

```python
"""One-command local rehearsal stack.

Boots: Postgres (docker compose) -> Alembic -> API (uvicorn) ->
dashboard (Vite dev server) -> cloudflared quick tunnel.
Prints the host URL and the player join URL, then supervises children
until Ctrl+C. Stdlib only.
"""

from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env"
ENV_EXAMPLE = REPO_ROOT / ".env.example"
API_PORT = 8000
WEB_PORT = 5173
REQUIRED_KEYS = ("ANTHROPIC_API_KEY", "GROQ_API_KEY")
TUNNEL_URL_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")

children: list[subprocess.Popen] = []


def fail(layer: str, problem: str, fix: str) -> None:
    print(f"\n[FAIL] {layer}: {problem}\n  Fix: {fix}", file=sys.stderr)
    teardown()
    sys.exit(1)


def teardown() -> None:
    for proc in reversed(children):
        if proc.poll() is None:
            proc.terminate()
    deadline = time.monotonic() + 10
    for proc in reversed(children):
        try:
            proc.wait(timeout=max(0.1, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            proc.kill()


def read_env() -> dict[str, str]:
    if not ENV_FILE.exists():
        if ENV_EXAMPLE.exists():
            shutil.copy(ENV_EXAMPLE, ENV_FILE)
            print(f"[setup] Created {ENV_FILE.name} from {ENV_EXAMPLE.name}.")
        else:
            fail(".env", "no .env or .env.example found",
                 "create .env at the repo root (see rehearsal quickstart)")
    env: dict[str, str] = {}
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    missing = [k for k in REQUIRED_KEYS if not env.get(k)]
    if missing:
        fail(".env", f"blank required keys: {', '.join(missing)}",
             "open .env and paste your keys (Anthropic: console.anthropic.com,"
             " Groq: console.groq.com)")
    return env


def wait_http(name: str, url: str, timeout_s: int, fix: str) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                if resp.status < 500:
                    print(f"[ok] {name} is up ({url})")
                    return
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(1.5)
    fail(name, f"not reachable at {url} after {timeout_s}s", fix)


def run_step(name: str, cmd: list[str], fix: str) -> None:
    print(f"[step] {name}: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=REPO_ROOT)
    if result.returncode != 0:
        fail(name, f"exit code {result.returncode}", fix)


def spawn(name: str, cmd: list[str], cwd: Path, env: dict[str, str],
          fix: str) -> subprocess.Popen:
    print(f"[start] {name}: {' '.join(cmd)}")
    try:
        proc = subprocess.Popen(
            cmd, cwd=cwd, env={**os.environ, **env},
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
    except FileNotFoundError:
        fail(name, f"command not found: {cmd[0]}", fix)
    children.append(proc)
    return proc


def main() -> None:
    env = read_env()

    if shutil.which("docker") is None:
        fail("Docker", "docker CLI not found",
             "install/start Docker Desktop, wait for the tray icon to go solid")
    if shutil.which("cloudflared") is None:
        fail("cloudflared", "cloudflared not found on PATH",
             "winget install Cloudflare.cloudflared (then reopen the terminal)")

    run_step("Postgres", ["docker", "compose", "up", "-d", "--wait"],
             "open Docker Desktop; then re-run make rehearsal")
    run_step("Migrations",
             [sys.executable, "-m", "alembic", "upgrade", "head"],
             "check POSTGRES_* values in .env match docker-compose.yml")

    spawn("API", [sys.executable, "-m", "uvicorn", "api.main:app",
                  "--host", "0.0.0.0", "--port", str(API_PORT),
                  "--env-file", ".env"],
          REPO_ROOT, env, "check the API log above for the first traceback")
    wait_http("API", f"http://localhost:{API_PORT}/health", 60,
              "read the uvicorn output above; usually a bad .env value")

    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if npm is None:
        fail("Dashboard", "npm not found", "install Node.js LTS from nodejs.org")
    spawn("Dashboard", [npm, "run", "dev"], REPO_ROOT / "dashboard", env,
          "run: cd dashboard && npm install")
    wait_http("Dashboard", f"http://localhost:{WEB_PORT}", 90,
              "run: cd dashboard && npm install, then re-run make rehearsal")

    tunnel = spawn("Tunnel",
                   ["cloudflared", "tunnel", "--url",
                    f"http://localhost:{WEB_PORT}"],
                   REPO_ROOT, env, "check your internet connection")
    join_url = None
    deadline = time.monotonic() + 45
    assert tunnel.stdout is not None
    while time.monotonic() < deadline and join_url is None:
        line = tunnel.stdout.readline()
        if not line:
            time.sleep(0.5)
            continue
        match = TUNNEL_URL_RE.search(line)
        if match:
            join_url = match.group(0)
    if join_url is None:
        fail("Tunnel", "no trycloudflare URL after 45s",
             "check internet; retry make rehearsal")

    print("\n" + "=" * 62)
    print("READY - Nightcap rehearsal stack is up")
    print(f"HOST URL (this machine):  http://localhost:{WEB_PORT}")
    print(f"PLAYER JOIN URL (phones): {join_url}")
    print("Leave this window open. Ctrl+C stops everything.")
    print("=" * 62 + "\n")

    try:
        while True:
            for proc in children:
                if proc.poll() is not None:
                    fail("Supervisor",
                         f"a child process exited (code {proc.returncode})",
                         "scroll up for its last log lines; re-run make rehearsal")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[stop] shutting down (database stays up; make rehearsal-stop stops it)")
        teardown()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    main()
```

Note for the implementer: the tunnel-URL scrape reads cloudflared's **stdout+stderr combined** (stderr is redirected to stdout in `spawn`). cloudflared prints the URL banner to stderr — the redirect is what makes the regex see it. Do not "simplify" the redirect away.

- [ ] **Step 2: Add Make targets**

Append to `Makefile`:

```makefile
.PHONY: rehearsal rehearsal-stop rehearsal-smoke

rehearsal:
	$(PYTHON) scripts/rehearsal.py

rehearsal-stop:
	docker compose down
```

(`rehearsal-smoke` is added in Task 7 but declared `.PHONY` here once.)

- [ ] **Step 3: Failure-path tests**

Manual verification matrix (run each, confirm the named layer + fix appear, no stack trace):
1. Rename `.env` → run `make rehearsal` → auto-creates from `.env.example`, then fails on blank `ANTHROPIC_API_KEY` with the console URLs. Restore `.env`.
2. Stop Docker Desktop → `[FAIL] Postgres` with the Docker Desktop fix.
3. With everything healthy → READY block prints both URLs; open `http://localhost:5173` and confirm the join screen loads.
4. Ctrl+C → children exit; `docker compose ps` still shows postgres; `make rehearsal-stop` stops it.

- [ ] **Step 4: Lint and commit**

```bash
python -m ruff check scripts/rehearsal.py && python -m ruff format scripts/rehearsal.py
git add scripts/rehearsal.py Makefile
git commit -m "feat(ops): one-command local rehearsal stack (make rehearsal)"
```

---

### Task 7: Live-stack smoke script

**Goal:** A scripted end-to-end pass against the *running* rehearsal stack proves the exact stack humans will touch: create session → host token works → two players join → session starts → events flow.

**Files:**
- Create: `scripts/rehearsal_smoke.py`
- Modify: `Makefile` (add `rehearsal-smoke` target body)

**Acceptance Criteria:**
- [ ] With `make rehearsal` running, `make rehearsal-smoke` exits 0 and prints `SMOKE PASS` after exercising: `POST /v1/sessions`, join-code lookup, ≥2 player joins, session start, and reading ≥1 event
- [ ] Any failed step prints the step name, HTTP status, and response body, and exits 1
- [ ] Stdlib-only

**Verify:** (stack up) `make rehearsal-smoke` → last line `SMOKE PASS`; (stack down) exits 1 with `[FAIL] api-health`.

**Steps:**

- [ ] **Step 1: Discover the exact endpoint shapes**

Before writing code, read `api/routers/` (sessions router) and `api/tests/test_sessions_api.py` for: create-session request/response fields (`arc_id`, `join_code`, host token header/claim shape), the player join endpoint (path + body from `api/tests/` join-flow tests, per AW-228), the start/lifecycle transition endpoint, and the events read path (SSE endpoint or REST events listing — AW-216). Mirror the calls the passing tests make; the smoke script is those same calls pointed at `http://localhost:8000` instead of TestClient.

- [ ] **Step 2: Write `scripts/rehearsal_smoke.py`**

Skeleton (fill endpoint paths/fields from Step 1 — the shapes below mirror `test_sessions_api.py` and must be corrected against it, not guessed):

```python
"""Smoke test against the LIVE local rehearsal stack (not TestClient).

Usage: make rehearsal-smoke   (requires `make rehearsal` running)
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = "http://localhost:8000"


def call(step: str, method: str, path: str, body: dict | None = None,
         token: str | None = None) -> dict:
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read() or b"{}")
            print(f"[ok] {step} -> {resp.status}")
            return payload
    except urllib.error.HTTPError as err:
        print(f"[FAIL] {step}: HTTP {err.code}\n{err.read().decode()}",
              file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as err:
        print(f"[FAIL] {step}: {err.reason} — is `make rehearsal` running?",
              file=sys.stderr)
        sys.exit(1)


def main() -> None:
    call("api-health", "GET", "/health")
    session = call("create-session", "POST", "/v1/sessions",
                   {"arc_id": "nightcap-v1"})
    session_id = session["session_id"]
    # Steps below: join two players via the join-code flow, start the
    # session, read events — exact paths/bodies mirrored from
    # api/tests/test_sessions_api.py in Step 1.
    ...
    print("SMOKE PASS")


if __name__ == "__main__":
    main()
```

The `...` MUST be replaced with the real join/start/events calls found in Step 1 — shipping the skeleton with `...` is a task failure.

- [ ] **Step 3: Prove it both ways**

Run with the stack down: expect `[FAIL] api-health` and exit 1.
Run `make rehearsal` in another terminal, then `make rehearsal-smoke`: expect `SMOKE PASS`, exit 0.

- [ ] **Step 4: Add the Make target, lint, commit**

```makefile
rehearsal-smoke:
	$(PYTHON) scripts/rehearsal_smoke.py
```

```bash
python -m ruff check scripts/rehearsal_smoke.py
git add scripts/rehearsal_smoke.py Makefile
git commit -m "feat(ops): live-stack rehearsal smoke script (make rehearsal-smoke)"
```

---

### Task 8: One-page rehearsal quickstart

**Goal:** A founder-executable one-page runbook replaces the 415-line procedure as the canonical way to run a rehearsal.

**Files:**
- Create: `docs/roadmap/operations/rehearsal-quickstart.md`
- Modify: `docs/roadmap/operations/rehearsal-1-runbook.md` (deprecation banner)

**Acceptance Criteria:**
- [ ] Quickstart fits on roughly one page: prerequisites (4 bullets max), the two commands (`make rehearsal`, `make rehearsal-smoke`), what to do during the session, wrap-up/blocker-log capture
- [ ] Old runbook keeps its content (troubleshooting value) but opens with a banner pointing to the quickstart
- [ ] Quickstart references AW-273 as the task it serves

**Verify:** `wc -l docs/roadmap/operations/rehearsal-quickstart.md` → under ~90 lines

**Steps:**

- [ ] **Step 1: Write `docs/roadmap/operations/rehearsal-quickstart.md`**

```markdown
# Rehearsal Quickstart

> Current version: v1.0
> Last updated: 2026-07-11
> Status: Current
> Canonical path: docs/roadmap/operations/rehearsal-quickstart.md
> Serves: AW-273 (Rehearsal 1 execution) and later rehearsals

## One-time prerequisites

- Docker Desktop installed and running (tray icon solid).
- Python env active (`conda activate base`) and Node.js LTS installed.
- `cloudflared` installed: `winget install Cloudflare.cloudflared`.
- `.env` at the repo root with real `ANTHROPIC_API_KEY` and `GROQ_API_KEY`
  values (run `make rehearsal` once — it creates `.env` from the template
  and tells you exactly which keys are blank).

## Start the stack

```powershell
make rehearsal
```

Wait for the READY block. It prints two URLs:
- **HOST URL** — open on the shared display (laptop/TV everyone can see).
- **PLAYER JOIN URL** — send to players' phones (changes every restart;
  do not restart mid-session).

Optional but recommended before players arrive:

```powershell
make rehearsal-smoke
```

Expected: `SMOKE PASS`. If it fails, the failing step and response are
printed — see the troubleshooting sections of
[rehearsal-1-runbook.md](rehearsal-1-runbook.md) and
[rehearsal-1-failure-cheat-sheet.md](rehearsal-1-failure-cheat-sheet.md).

## During the session

1. On the shared display, create the session and read the join code aloud.
2. Players open the join URL on their phones and enter the code
   (target: everyone in under 30 seconds each).
3. Play end-to-end: arrival, private events, both mini-games
   (Crime Scene Smash, Evidence Locker), accusation, killer reveal.
4. When something breaks or feels wrong, say "logging it" out loud and jot
   one line — timestamp, who, what. Keep playing if the session survives.

## Wrap-up (do this the same evening)

1. Copy `blocker-log-template.md` to
   `rehearsal-1-blocker-log.md` in this directory and fill it from your
   notes.
2. Commit it, and paste the highlights into the AW-273 GitHub issue.
3. Stop the stack: Ctrl+C in the rehearsal window, then
   `make rehearsal-stop`.
```

- [ ] **Step 2: Add the deprecation banner**

At the top of `docs/roadmap/operations/rehearsal-1-runbook.md`, directly under the H1, insert:

```markdown
> **Superseded for day-of use (2026-07-11):** start with
> [rehearsal-quickstart.md](rehearsal-quickstart.md) — the stack is now one
> command (`make rehearsal`). This document remains as the deep
> troubleshooting reference; its five-terminal manual procedure is obsolete.
```

- [ ] **Step 3: Commit**

```bash
git add docs/roadmap/operations/rehearsal-quickstart.md docs/roadmap/operations/rehearsal-1-runbook.md
git commit -m "docs(operations): one-page rehearsal quickstart; deprecate five-terminal procedure"
```

---

### Task 9: Verified end-to-end dry run (exit gate)

**Goal:** Prove the exact stack humans will touch works, before anyone invites humans: full `make rehearsal` boot plus `SMOKE PASS`, with output captured.

**USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Files:** none created (evidence pasted into the task/PR record)

**Acceptance Criteria:**
- [ ] Fresh terminal: `make rehearsal` reaches the READY block; the printed PLAYER JOIN URL is opened (curl or browser) and returns the join screen HTML (HTTP 200)
- [ ] `make rehearsal-smoke` exits 0 with final line `SMOKE PASS` while that stack is running
- [ ] Full test suite green on the final tree: `python -m pytest engine/tests api/tests tests -q` → 0 failed
- [ ] All captured output (READY block, SMOKE PASS line, pytest tail) pasted into the task completion report

**Verify:** `make rehearsal` → READY block; `make rehearsal-smoke` → `SMOKE PASS`; `curl -s -o /dev/null -w "%{http_code}" <join-url>` → `200`; `python -m pytest engine/tests api/tests tests -q` → `0 failed`

**Steps:**

- [ ] **Step 1: Cold boot** — new terminal, `make rehearsal`, capture the READY block verbatim.
- [ ] **Step 2: External reachability** — `curl -s -o /dev/null -w "%{http_code}" <PLAYER JOIN URL>` → `200` (the tunnel serves the app to the outside).
- [ ] **Step 3: Smoke** — `make rehearsal-smoke` → capture `SMOKE PASS`.
- [ ] **Step 4: Suite** — `python -m pytest engine/tests api/tests tests -q` → capture the summary line.
- [ ] **Step 5: Teardown** — Ctrl+C, `make rehearsal-stop`; paste all evidence into the completion report. No commit (evidence-only task).

---

## Not in this plan (deliberately)

- Phases 2–4 of the spec (player-drop AI takeover #138, `"arrival"` fallback #137, cloud deploy AW-269, Rehearsal 2 AW-266, M6 chain) — planned after Rehearsal 1's blocker log exists.
- Deprecation-warning cleanup (spec Phase 0 item 7, optional) — skipped as noise reduction with no functional payoff right now; revisit if warnings mask real failures.
- Any change to `engine/` behavior, schemas, prompts, or dependencies (Hard Rules).
