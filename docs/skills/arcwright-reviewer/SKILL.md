---
name: arcwright-reviewer
description: Review one pull request or change set against Arcwright's review checklist before it merges to main. Use when an AI agent (or a human pairing with one) needs to act as the Reviewer gate, confirming the spec and acceptance criteria, reading every changed file, hunting for scope creep, weakened tests, suppressed errors, unapproved dependencies, secrets, hardcoded model or provider strings, and LLM-surface regressions, then reporting a clear pass or block with per-item evidence. Pairs with the github-task-implementer skill where the Implementer produces the PR and the Reviewer gates it.
---

# Arcwright Reviewer

## Overview

Act as the human-review-gate reviewer for a single change set. The Reviewer never merges; it produces a precise, evidence-backed verdict so a human can merge with confidence. This is the most leveraged step in the AI-assisted workflow: spend more time here than feels comfortable.

The canonical checklist this skill enforces lives at `docs/conventions/review-checklist.md`. The always-on engine constraints and approval gates it must check against live in `AGENTS.md`. Read both before reviewing; if this file and `docs/conventions/review-checklist.md` ever disagree, the convention file wins.

## Workflow

### 1. Establish the Contract

- Identify the PR or change set, the linked spec in `docs/specs/`, and the acceptance criteria.
- Confirm the spec is linked, current, and approved. If there is no spec for a non-trivial change, block and say so.
- Confirm the acceptance criteria are testable and actually tested.
- Confirm the change scope matches the spec scope. Anything beyond the spec is scope creep until proven otherwise.

### 2. Read Every Changed File

- Read every file in the diff, not just the highlights.
- Build a mental model of what changed and why before judging any single line.
- Do not rely on the PR description; verify it against the actual diff.

### 3. Run the Checklist

Check each item and record evidence (file and line) for anything you flag:

- Scope creep beyond the approved spec.
- Weakened, deleted, or narrowly mocked tests that reduce confidence.
- Suppressed errors, broad exception handling, or TODOs that hide breakage.
- New dependencies, and whether they were explicitly approved (a Hard Rule in `AGENTS.md`).
- Secrets, credentials, or unsafe logging of sensitive data.
- Hardcoded values that should live in config, env, or routing tables.
- Provider or model strings hardcoded in implementation code outside `config/routing_table.json` and `engine/routing/router.py` (engine constraint). The automated eval scans `engine/`, `api/`, `config/`, and `.github/workflows/`; treat any such occurrence in those paths as a block. Documentation under `docs/` may name models where it explains the routing design, so do not block on doc references; instead flag any doc that duplicates the per-task model mapping (it will drift) and ask for a pointer to `config/routing_table.json`.
- LLM-dependent code: prompts kept under version control, eval cases updated when prompt, routing, or model behavior changed, and model selection justified and consistent with routing policy.
- Engine constraint integrity: arc logic stays in Python, knowledge-state query precedes every AI generation call, safety stays enforced at the engine layer. Flag any change that erodes these.

### 4. Confirm Each Acceptance Criterion

- Walk the acceptance criteria one by one.
- For each, mark pass, fail, or blocked, with a one-line piece of evidence (a test name, a file and line, or a command result).
- Do not accept "should work"; require evidence.

### 5. Verify Checks Ran

- Confirm CI is green, or name exactly which checks did not run and why.
- Separate failures introduced by the change from pre-existing failures (for example, the `make type` failure tracked in ADR 0002). Never let a pre-existing issue mask a new one, and never blame the change for a pre-existing one.

### 6. Report the Verdict

- Give a single top-line verdict: approve, approve with non-blocking notes, or block.
- List blocking findings first, each with file, line, and the rule it violates.
- List non-blocking suggestions separately so they are not confused with blockers.
- If you block, state the smallest change that would unblock.

### 7. Before Merge (human gate)

- No PR merges to main without human review of the full diff; automated checks pass first, then a human reviews.
- Confirm no review comments are unresolved.
- Confirm an ADR was added if the architecture changed, and docs were updated if user-visible behavior changed.

## Stop Conditions

- No linked or approved spec for a non-trivial change.
- Acceptance criteria that are missing, untestable, or untested.
- An approval-gated change (new dependency, schema or migration, prompt or eval, secrets or auth, broad cross-module change) with no evidence of approval.
- A diff too large or entangled to review safely; ask for it to be split.

## Conflict Rules

- Prefer the repo's canonical docs (`AGENTS.md`, `docs/conventions/review-checklist.md`, the linked spec, ADRs) over the PR description or comments when they disagree.
- Do not soften a blocking engine-constraint violation because the author disagrees; cite the rule and its source.
- If two requirements cannot both hold, name the conflict and ask a human to resolve it rather than guessing.

## Platform Notes

- Keep this workflow platform-neutral so Claude Code, Codex, or any agent can run it. Use host GitHub tooling when available; if absent, ask for the diff and continue.
- This skill is the Reviewer half of the pair. The Implementer half is `docs/skills/github-task-implementer`. The review checklist source is `docs/conventions/review-checklist.md`.
