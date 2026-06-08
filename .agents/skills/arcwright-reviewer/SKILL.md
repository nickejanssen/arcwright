---
name: arcwright-reviewer
description: Review one pull request or change set against Arcwright's review checklist before it merges to main. Use when an AI agent (or a human pairing with one) needs to act as the Reviewer gate, confirming the spec and acceptance criteria, reading every changed file, hunting for scope creep, weakened tests, suppressed errors, unapproved dependencies, secrets, hardcoded model or provider strings, and LLM-surface regressions, then reporting a clear pass or block with per-item evidence. Pairs with the github-task-implementer skill where the Implementer produces the PR and the Reviewer gates it.
---

# Reviewer (Codex launcher)

This is a thin launcher. It carries no role logic of its own. The canonical contract is `docs/skills/arcwright-reviewer/SKILL.md`. Read that file in full and follow it exactly.

The review checklist source is `docs/conventions/review-checklist.md` and the always-on rules are in `AGENTS.md`. You do not merge; you produce an evidence-backed pass or block verdict for a human.
