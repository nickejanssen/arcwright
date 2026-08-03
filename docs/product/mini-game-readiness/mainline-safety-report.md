> Current version: v1.1
> Last updated: 2026-08-03
> Status: Current planning audit, implementation stopped
> Canonical path: docs/product/mini-game-readiness/mainline-safety-report.md

# Mini-game Readiness Program Mainline Safety Report

## Decision

**STOP before implementation.** The prior GO applied to planning commit
`1e65dc5` and its fixed-adapter design. The founder has since approved a
materially different browser-first package, adaptation, placement-policy,
progressive-readiness, and capability-negotiation architecture. Specs 0077
through 0080 now record that approval, and the replacement implementation
plans are written. The plans have not received the separate implementation
go-ahead required by the Human Collaboration Contract.

Current `origin/main` is
`d26d7b8dee2aafa59ef6a0fd985da5bea771dbf1` and includes PR #273 and PR #274.
The replacement planning branch was created in a new isolated worktree from
that exact commit. Five reviewed planning commits were replayed onto it, and
only approved planning revisions were migrated. The dirty main checkout and
the older dirty planning worktree were not stashed, rebased, cleaned, or
modified. Main still contains an unrelated uncommitted
`docs/product/decisions-log.csv` change being handled by another agent.

## 2026-08-03 planning refresh

| Field | Result |
| --- | --- |
| `origin_main_sha` | `d26d7b8dee2aafa59ef6a0fd985da5bea771dbf1` (`d26d7b8`) |
| `new_merged_prs` | #273 Scene Sweep backend and #274 Scene Sweep design and plan |
| `overlap` | Direct scope overlap. Scene Sweep is now an existing package and second Scene candidate. Preserve merged backend and design work. |
| `planning_worktree` | `codex/minigame-platform-browser-plans`, created from exact `origin/main`; ahead 5 by replayed planning commits, not behind, with uncommitted reviewed planning revisions |
| `main_worktree` | Up to date with origin/main; unrelated `docs/product/decisions-log.csv` modification present |
| `baseline_checks` | Focused current baseline: 91 passed, 1 skipped because `DATABASE_URL` is unset, 2 pre-existing warnings. Broader engine run: 828 passed, 1 skipped, 13 sandbox temp-permission errors, and 3 sandbox-slow timing-budget failures. |
| `decision` | STOP pending founder review of the replacement plans and explicit implementation approval. Repeat fresh-main and focused baseline checks before each executable plan. |

## 2026-08-03 replacement-plan baseline

The focused baseline was rerun from the new worktree after planning migration:

```powershell
C:\Users\nicke\OneDrive\Desktop\arcwright\.aw102-venv\Scripts\python.exe -m pytest engine/tests/test_mini_game_models.py engine/tests/test_mini_game_runtime.py engine/tests/test_mini_game_runtime_aw252.py api/tests/test_mini_games_api.py -q --basetemp .pytest-baseline-current
```

Result: `91 passed, 1 skipped, 2 warnings` in 53.15 seconds. The temporary
directory was resolved inside the worktree and removed after the run.

The broad `engine/tests` diagnostic collected 845 tests. It reached 828 passes
and one expected database skip. Thirteen tests could not create temporary
directories under the sandbox account, and three property sweeps exceeded a
15-second performance threshold under sandbox load. These are recorded as
environment-constrained baseline results, not attributed to documentation
changes and not described as a green full-suite baseline.

## Historical 2026-08-02 PreflightReport

| Field | Result |
| --- | --- |
| `origin_main_sha` | `52562723d5dd6374817e1299f8faf98ecd5dd120` (`5256272`) |
| `merged_prs` | #268 `a131259`, #269 `7aa3f92`, #271 `f442b2f`, #272 `5256272` |
| `overlapping_files` | None. `git diff --name-only 52562723d5dd6374817e1299f8faf98ecd5dd120..origin/main` was empty. |
| `worktree_clean` | PASS. `git status --short --branch` showed a clean `codex/minigame-platform-planning` worktree. |
| `baseline_checks` | See below. |
| `changed_assumptions` | None reported or observed. The branch contains the three approved planning commits `61da78d`, `2e0d858`, and `1e65dc5` above `origin/main`; these are planning inputs, not mainline changes. |

## Baseline checks

| Check | Result | Evidence |
| --- | --- | --- |
| `git fetch origin --prune` | `PASS` | Controller execution completed successfully with exit code 0. |
| `gh pr list --state merged --base main --limit 30 --json number,title,mergedAt,mergeCommit,headRefName,baseRefName,url` | `PASS` | Controller execution completed successfully; file inspection confirmed same-day merged PRs #268, #269, #271, and #272, including the revert. |
| `git diff --name-only 52562723d5dd6374817e1299f8faf98ecd5dd120..origin/main` | `PASS` | Empty output. |
| `git status --short --branch` | `PASS` | Clean worktree; branch is ahead of `origin/main` only by the three planning commits. |
| `git merge-base --is-ancestor origin/main HEAD` | `PASS` | Exit code 0. |

## Fix Round 1: selected-plan baseline and durable approval

The selected plan's required baseline checks were run by the controller and
are recorded here with their exact commands and outputs.

| Command | Result | Output |
| --- | --- | --- |
| `C:\Users\nicke\OneDrive\Desktop\arcwright\.aw102-venv\Scripts\python.exe -m pytest engine/tests/test_mini_game_models.py engine/tests/test_mini_game_runtime.py engine/tests/test_mini_game_runtime_aw252.py api/tests/test_mini_games_api.py -q --basetemp .superpowers\sdd\2026-08-02-mini-game-platform-readiness-program\pytest-baseline` | `PASS` | 90 passed, 1 skipped because `DATABASE_URL` was not set, 2 pre-existing warnings, exit 0. |
| `npm --prefix sdk run typecheck` | `PASS` | Exit 0. |

The earlier system Conda run was invalid because it used the old interpreter.
The first Python 3.11 attempts were `BLOCKED_ENVIRONMENT` because of the
default temporary directory. The exact Python 3.11 command above passed after
using the ignored workspace `--basetemp` path. These attempts are recorded for
traceability and are not treated as baseline failures.

Durable approval evidence for the GO decision is the founder message dated
2026-08-02: `Approved superpowers:subagent-driven-development`. It approves
execution of the artifact
`docs/superpowers/plans/2026-08-02-mini-game-platform-readiness-program.md`
at approved planning commit `1e65dc5`, conditional on the fresh-main audit.
The audit found no drift: `origin/main` remained at
`52562723d5dd6374817e1299f8faf98ecd5dd120`, the mainline diff was empty, and
the planning branch remained an ancestor-descended clean branch. This approval
identifies the artifact, its approved version commit, the decision, and its
condition.

## Selected execution-plan overlap

The selected execution plans are the ten files listed in the program map in
`docs/superpowers/plans/2026-08-02-mini-game-platform-readiness-program.md`.
Because `origin/main` has no changed files after the baseline, there are no
mainline files to overlap those plans. The planning branch's own changes are
confined to approved planning, decision, and plan artifacts and do not modify
the Task 1 report target.

## Guardrails confirmed

- No GitHub mutation was performed.
- Only the requested canonical report is a product-document change.
- No dependencies, migrations, prompts, evals, secrets, auth behavior, or
  runtime code were changed.
- The mini-game boundary remains authoritative in Python; clients render and
  submit only, and AI does not decide outcomes.
- The report records the controller-verified fetch and GitHub checks as
  passing.

## Acceptance criteria

- Fresh mainline safety audit completed against the exact baseline SHA.
- Same-day merged PR evidence recorded, including revert #272.
- Mainline overlap, worktree cleanliness, ancestry, and changed assumptions
  recorded.
- Applicable baseline checks classified as `PASS`.
- The selected plan's Python 3.11 and SDK typecheck baseline commands and
  outputs are recorded.
- Durable founder approval evidence identifies the approved plan artifact,
  planning commit `1e65dc5`, decision, date, and fresh-main condition.
- Founder go decision recorded for Task 1 execution.
