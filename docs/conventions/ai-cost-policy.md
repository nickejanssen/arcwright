# AI Cost Policy

Use the lightest agent surface that matches the work.

## Agent Order

**First reach: Copilot in VS Code**

Use when the human is at the keyboard and the change is incremental.

**Second reach: Claude Code**

Use for synchronous multi-file work or complex debugging. Reserve it for cases where collaborative depth is needed.

**Third reach: Codex (cloud)**

Use for well-specified async tasks that can run while the human is unavailable. The spec must be complete before delegation.

**Avoid: Claude.ai Project chat for code generation**

Use that surface for strategy, planning, and spec writing.

## Workflow Rule

- One agent per feature branch.
- If a task is unclear, escalate to spec writing in Project chat before spending agent credits on implementation attempts.
- In the PR description, note which agents were used and roughly how much effort each contributed: `minimal`, `moderate`, or `primary`.
