---
name: github-task-implementer
description: Implement one GitHub issue, task, or story from intake through PR handoff while staying inside the ticket's documented scope. Use when an AI agent needs to read the full work item, inspect linked specs and repo docs, verify prerequisites, propose a plan before coding, implement only the approved acceptance criteria, run required checks, report each acceptance criterion explicitly, address review feedback, perform post-merge branch cleanup, and close task or epic tracker items with useful completion notes.
---

# Github Task Implementer

## Overview

Implement a single GitHub work item with a strict plan-before-code workflow and strong scope control. Keep the core procedure platform-neutral so the same file can be used by Codex, Claude Code, or any other AI coding agent.

## Workflow

### 1. Capture the Task Contract

- Extract the issue number, any stable roadmap or task ID such as `AW-111`, the exact issue title, and any explicit branch, commit, PR, or review requirements.
- Read the full issue body before planning. Include the spec, acceptance criteria, anti-requirements, linked docs, dependencies, and any "Implements:" or equivalent references.
- Treat the issue body plus referenced repo docs as the scope contract. Treat comments as non-authoritative unless the user says they supersede the ticket.
- Treat product-scope additions as unapproved until durable evidence exists in canonical repo docs. Use `docs/product/decisions-log.csv` for product approval records, plus an ADR or approved spec when the decision affects roadmap sequencing, architecture, privacy, APIs, schemas, telemetry, or implementation behavior.
- If the ticket is missing acceptance criteria or concrete done conditions, stop and ask for them before coding.

### 2. Classify Human Collaboration

- Read `docs/conventions/human-collaboration.md` and declare every applicable
  interaction profile with a short rationale.
- If the task is not independent, list required founder inputs, the current
  phase, the next gate, intermediate artifacts, and approval evidence needed.
- Conduct required interviews one focused question at a time. Prefer
  interactive multiple-choice controls with a recommendation and free-form
  input. Use the numbered-choice fallback only when controls are unavailable.
- Creative work begins with open-ended founder vision, followed by 2 to 3
  advised directions and explained low-cost artifacts.
- Facilitated live operations stop at every preparation, preflight,
  walkthrough, live-session, debrief, and remediation gate.
- If the founder is unavailable, continue reversible research only and stop
  before choosing or implementing dependent work.

### 3. Create a Safe Branch

- Make branch creation the first state-changing git action for the task.
- Prefer `task/AW-111-brief-description` when a stable task ID exists.
- Otherwise use `task/issue-123-brief-description`.
- Sanitize the branch slug to lowercase letters, digits, and hyphens only. Remove or replace characters such as `:`, spaces, quotes, and duplicate hyphens.
- If the user supplied an invalid branch name, show the sanitized branch name before using it.
- Do not reuse a branch that already contains unrelated work.

### 4. Inspect Repo State Before Editing

- Run a repo-state check such as `git status` before editing.
- Read the repo's agent instruction file and workflow docs first, such as `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `README.md`, or docs under `docs/`.
- Read the specific PRD, architecture, design, or spec files referenced by the ticket.
- Inspect the current code paths, tests, and configuration that the task touches.
- Verify prerequisites from prior tasks are actually present in the codebase. If a required dependency, earlier task, migration, API, or helper is missing or incomplete, stop and report the exact prerequisite gap.
- Do not clean up unrelated local changes. Call them out only if they affect the task.

### 5. Produce a Plan and Wait for Approval

- After reading, send a short implementation plan before writing code.
- Include ambiguities, missing decisions, conflicting instructions, or prerequisite gaps in the same message.
- Quote the exact unclear ticket or spec text when asking for clarification.
- For independent work, group related implementation ambiguities into one
  concise clarification. For non-independent work, follow the one-focused-
  question-at-a-time interview contract.
- Do not write code until the user explicitly approves the plan.

### 6. Implement Only the Approved Scope

- Implement only what the ticket and approved plan require.
- Do not add cleanup, refactors, dependencies, schema changes, or extra features unless the acceptance criteria require them or the user approves them.
- If the repo requires tests with code, write them as part of the same change.
- Preserve existing unrelated edits in touched files unless the user explicitly asks you to revert them.
- If you hit an unspecified decision during implementation, stop and ask instead of guessing.
- If repo policy marks a change type as approval-gated, stop and surface that gate before proceeding. Common gated categories include dependency changes, database schema changes, auth or secret handling, prompt or eval changes, and broad cross-module architecture changes.
- If approved work adds product scope, add or update the durable decision evidence in `docs/product/`, `docs/decisions/`, or `docs/specs/` as part of the same change.

### 7. Verify Like a Reviewer

- Run the smallest set of checks that proves the ticket, then add any repo-required lint, type, build, or test commands needed to claim completion.
- Separate results into three categories:
  - checks that passed because of your work
  - checks blocked or broken by your changes
  - checks blocked by a pre-existing repo or environment issue
- Confirm each acceptance criterion explicitly, one by one, with short evidence.
- If the repo or ticket names a mandatory command, run it unless blocked by a missing dependency, missing credential, or environment limitation. If blocked, say so explicitly.

### 8. Commit and PR Correctly

- Use one branch per task.
- Use a conventional commit subject on the first line.
- Put `Closes #123` or `Refs #123` in the commit body or PR description unless the repo explicitly uses another pattern.
- Push the branch.
- Open a PR when the platform supports it.
- Use the issue title as the PR title when the ticket or repo workflow expects that. If the repo enforces a different title format and the ticket says "exact issue title," stop and surface the conflict.
- In the PR description, list which acceptance criteria pass, what checks ran, and any remaining blockers or follow-up risk.

### 9. Handle Review Follow-Up on the Same Ticket

- Read review comments carefully and distinguish actionable requests from preference-only commentary.
- Fix actionable comments on the same branch unless the repo workflow says otherwise.
- Resolve review conversations only after the code or explanation actually addresses them.
- If a review request would expand scope beyond the original ticket, stop and ask whether to fold it into the current task or open a follow-up issue.

### 10. Clean Up Only After Merge

- Do not do post-merge cleanup until merge is confirmed.
- After merge, switch back to the default branch, pull the latest remote state, delete the local task branch, and run `git status`.
- Report whether the working tree is clean and synced with the default branch.
- If pre-existing files or ignored local state prevent a clean tree, report them explicitly and leave them alone.

### 11. Close Tracker Items After Merge

- After merge and local branch cleanup, identify the completed ticket, its parent epic, and its milestone from the GitHub issue, PR, and canonical roadmap index.
- Close the completed task ticket unless it is already closed. Add a clear completion note before or during closure.
- In the task closure note, write for multiple readers: engineers, the chief architect, game developers, product managers, and business stakeholders.
- Include what shipped, what changed during review, acceptance criteria satisfied, verification run, what remains, and what was explicitly punted to future scope.
- Check whether the completed task closes its parent epic. Close the epic only when all child tasks are closed and the epic acceptance criteria are satisfied.
- If an epic closes, add easy-to-read epic notes covering what was accomplished, what changed, what remains, and what moves to future work. Also close any milestone only when all milestone epics are closed and the milestone exit gate is met.
- If the task does not close its parent epic or milestone, leave them open and add a short status note explaining what was completed and what child work remains.
- When closing an epic or milestone, celebrate the accomplishment in the final user response in plain language. Explain what the accomplishment means for the engine and platform, what to look forward to next, and whether humans or another role can now test, configure, set up, or use anything new.
- Do not claim an epic or milestone is complete from PR merge alone. Verify live tracker state and canonical roadmap children first.
- Do not hide deferred work. Name future-scope items explicitly and tie them to the correct task, milestone, version, or decision record when known.

## Stop Conditions

- Missing, contradictory, or non-verifiable acceptance criteria
- Missing prerequisite work from earlier tickets
- Conflicting instructions between the issue, repo conventions, and user request
- Required checks blocked by missing dependencies, credentials, or environment access
- Approval-gated work types that the repo or user has not approved
- Unrelated local changes that make the task unsafe to continue without direction
- A missing or unjustified interaction profile
- A required founder interview that has not occurred
- An artifact that lacks the explanation required for informed review
- Approval inferred from silence, PR activity, or a broader approval
- A live-operation phase without its explicit go or no-go

## Conflict Rules

- Prefer the repo's canonical design docs over issue comments when scope or architecture disagree.
- Prefer stable task IDs such as `AW-111` over mutable GitHub numbers when naming branches and locating roadmap docs.
- Prefer repo commit conventions for the commit subject line, then add issue-closing references in the body.
- If two instructions cannot both be satisfied, do not guess. Explain the conflict and ask the user to choose.

## Platform Notes

- Keep the core workflow platform-neutral. Do not rely on Codex-only or Claude-only features in the required path.
- Use host-platform GitHub tools when available. If the platform lacks GitHub integration, ask the user for the issue body or pasted ticket content and continue with the same workflow.
- Treat this file as the primary source of procedure. Read `references/response-contracts.md` only when you need reusable output shapes.
