# Response Contracts

Use these shapes when the host platform does not prescribe a stronger format.

## Pre-Code Plan

Send this after reading the issue, linked docs, and current repo state:

```text
Plan
1. [step]
2. [step]
3. [step]

Ambiguities
- [exact unclear point]

Blockers
- [missing prerequisite, conflicting instruction, or "None"]
```

Keep the plan short. Do not start coding until the user approves it.

## Clarification Message

If clarification is required, send one message that:

- quotes the exact unclear text
- states why it blocks a safe implementation decision
- asks for the minimum decision needed to continue

Example:

```text
The issue says "use the exact issue title as the PR title," but the repo workflow requires conventional PR titles. Which rule should I follow for this ticket?
```

## Completion Report

Use this structure when reporting done:

```text
Acceptance Criteria
- [criterion]: pass | fail | blocked - [brief evidence]

Checks
- [command]: pass | fail | blocked

Pre-existing Issues
- [issue or "None"]

PR Handoff
- Branch: [name]
- Commit: [conventional commit subject]
- PR: [title or URL if available]
```

Separate failures introduced by the task from failures that were already present.

## Review Follow-Up

When the PR gets review comments:

- list each actionable comment
- state what changed or why no code change was needed
- rerun only the checks needed to prove the fix unless the repo requires a broader rerun
