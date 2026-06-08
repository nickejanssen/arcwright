---
name: github-task-implementer
description: Implement one GitHub issue, task, or story from intake through PR handoff while staying inside the ticket's documented scope. Use when an AI agent needs to read the full work item, inspect linked specs and repo docs, verify prerequisites, propose a plan before coding, implement only the approved acceptance criteria, run required checks, report each acceptance criterion explicitly, address review feedback, and perform post-merge branch cleanup.
---

# Implementer (Codex launcher)

This is a thin launcher. It carries no role logic of its own. The canonical, platform-neutral contract is `docs/skills/github-task-implementer/SKILL.md`. Read that file in full and follow it exactly.

Before changing any code, also read the always-on rules in `AGENTS.md` (engine constraints, approval gates, workflow, agent-local-file policy). Do not write implementation code until the plan is approved.
