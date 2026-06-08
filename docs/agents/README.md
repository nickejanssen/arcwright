# Arcwright Multi-Agent Operating Model

This directory defines the development roles Arcwright uses and how work flows between them. It is the human-facing companion to `AGENTS.md` (the always-on rules) and `docs/skills/` (the executable role skills).

Two kinds of role live in this operating model:

- **Thinking roles** (this directory): Product Steward, Planner, Spec Author, Scribe. These run primarily in the Claude.ai Project chat, where a human and the model shape intent, plans, specs, and records. Each has a contract file here.
- **Doing roles** (`docs/skills/`): Implementer and Reviewer. These run in the coding clients (Claude Code, Codex, Copilot) through thin launchers wired up in later phases. They are full skills, not just contracts.

The Architecture SME (`docs/skills/arcwright-sme`) is consulted by every role at every gate. It is the authority on what the canonical docs say.

## The Pipeline

```
Product Steward  ->  Planner  ->  Spec Author  ->  Implementer  ->  Reviewer
     (intent)       (sequence)      (spec)          (PR)            (gate)
        \______________ SME consulted at every gate ______________/
        \______________ Scribe records outcomes throughout _______/
```

1. **Product Steward** decides what should happen and why, and whether it is in scope. Output: an approved intent.
2. **Planner** turns approved intent into a sequenced plan and, when the work is platform-build, one or more roadmap tasks with stable AW-NNN IDs and dependencies. Output: a plan and task definitions.
3. **Spec Author** writes the `docs/specs/NNNN-*.md` spec from `docs/specs/0000-template.md`, with verifiable acceptance criteria. Output: an approved spec.
4. **Implementer** (`docs/skills/github-task-implementer`) executes one task from branch to PR, inside the spec's scope. Output: a PR with per-criterion evidence.
5. **Reviewer** (`docs/skills/arcwright-reviewer`) gates the PR against `docs/conventions/review-checklist.md` and `AGENTS.md`. Output: an evidence-backed pass or block. A human merges.

At each gate, consult the SME for authoritative answers grounded in `docs/`. The Scribe records decisions (ADRs), keeps indexes and specs in sync, and captures outcomes.

## The AW-NNN Handoff Key

The stable roadmap task ID (for example `AW-111`) is the thread that ties the pipeline together for platform-build work:

- Planner mints the AW-NNN and records it in `docs/roadmap/index.json` and `docs/roadmap/tasks/AW-NNN-*.md`.
- Spec Author references the AW-NNN in the spec.
- Implementer branches `task/AW-NNN-brief-description` and references the task in the PR.
- Reviewer and Scribe refer to the same AW-NNN.

Prefer the stable AW-NNN over a mutable GitHub issue number when naming branches and locating roadmap docs. Not all work needs an AW-NNN: meta-tooling and infra changes can ship as a numbered spec plus PRs with no roadmap ID (see `docs/specs/` precedent), in which case the spec number is the thread.

## Role-to-Surface Map

| Role | Contract or skill | Where it runs |
|---|---|---|
| Product Steward | `docs/agents/product-steward.md` | Claude.ai Project chat |
| Planner | `docs/agents/planner.md` | Claude.ai Project chat |
| Spec Author | `docs/agents/spec-author.md` | Claude.ai Project chat |
| Scribe | `docs/agents/scribe.md` | Claude.ai Project chat and coding clients |
| Architecture SME | `docs/skills/arcwright-sme` | Any client |
| Implementer | `docs/skills/github-task-implementer` | Claude Code, Codex, Copilot |
| Reviewer | `docs/skills/arcwright-reviewer` | Claude Code, Codex, Copilot |

Note on the Implementer: the user-level `arcwright-task-runner` skill describes the same Claude Code GitHub-issue lifecycle. Its logic is fully covered by the canonical, platform-neutral `github-task-implementer`. To avoid two divergent copies, the operating model treats `github-task-implementer` as the single Implementer contract; client launchers point at it rather than re-creating task-runner.

## Relationship to the Rules

These contracts describe roles and flow. They do not restate the always-on rules. Every role is bound by `AGENTS.md` (engine constraints, approval gates, workflow, agent-local-file policy) and by `docs/conventions/`. If a role contract and `AGENTS.md` ever disagree, `AGENTS.md` wins.
