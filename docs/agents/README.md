# Arcwright Multi-Agent Operating Model

This directory defines the development roles Arcwright uses and how work flows between them. It is the human-facing companion to `AGENTS.md` (the always-on rules) and `docs/skills/` (the executable role skills).

Two kinds of role live in this operating model:

- **Thinking roles** (this directory): Product Steward, Business Steward, System Architect, Planner, Spec Author, Scribe. These run primarily in the Claude.ai Project chat, where a human and the model shape intent, plans, specs, and records. Each has a contract file here.
- **Doing roles** (`docs/skills/`): Implementer and Reviewer. These run in the coding clients (Claude Code, Codex, Copilot) through thin launchers wired up in later phases. They are full skills, not just contracts.

The Architecture SME (`docs/skills/arcwright-sme`) is consulted by every role at every gate. It is the authority on what the canonical docs say.

## The Pipeline

```
   Intent and Approval Gate
   [ Product Steward   (what and scope)   ]
   [ Business Steward  (commercial viability) ]  ->  Planner  ->  Spec Author  ->  Implementer  ->  Reviewer
   [ System Architect  (technical approach) ]        (sequence)      (spec)          (PR)            (gate)
        \________________ SME informs at every gate ________________/
        \________________ Scribe records outcomes throughout _______/
```

The intent and approval gate is a shared decision by three roles before any planning begins:

1. **Product Steward** decides what should happen and why, and whether it is in product scope. Output: an approved product intent.
2. **Business Steward** decides whether it is worth pursuing commercially (market, revenue, pricing, go-to-market, business risk). Output: a business go or no-go with constraints.
3. **System Architect** decides the technical approach and owns the design decision and any ADR. Output: an approved approach with design constraints. The SME informs this decision; the Architect makes it.

Once the gate aligns on a go:

4. **Planner** turns the approved intent into a sequenced plan and, when the work is platform-build, one or more roadmap tasks with stable AW-NNN IDs and dependencies. Output: a plan and task definitions.
5. **Spec Author** writes the `docs/specs/NNNN-*.md` spec from `docs/specs/0000-template.md`, with verifiable acceptance criteria. Output: an approved spec.
6. **Implementer** (`docs/skills/github-task-implementer`) executes one task from branch to PR, inside the spec's scope. Output: a PR with per-criterion evidence.
7. **Reviewer** (`docs/skills/arcwright-reviewer`) gates the PR against `docs/conventions/review-checklist.md` and `AGENTS.md`. Output: an evidence-backed pass or block. A human merges.

At each gate, consult the SME for authoritative answers grounded in `docs/`. The Scribe records decisions (ADRs), keeps indexes and specs in sync, and captures outcomes. Note the division of architecture labor: the **System Architect decides** the approach and owns the ADR, while the **Architecture SME informs** by reporting what the canonical docs say.

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
| Business Steward | `docs/agents/business-steward.md` | Claude.ai Project chat |
| System Architect | `docs/agents/system-architect.md` | Claude.ai Project chat |
| Planner | `docs/agents/planner.md` | Claude.ai Project chat |
| Spec Author | `docs/agents/spec-author.md` | Claude.ai Project chat |
| Scribe | `docs/agents/scribe.md` | Claude.ai Project chat and coding clients |
| Architecture SME | `docs/skills/arcwright-sme` | Any client |
| Implementer | `docs/skills/github-task-implementer` | Claude Code, Codex, Copilot |
| Reviewer | `docs/skills/arcwright-reviewer` | Claude Code, Codex, Copilot |

Note on the Implementer: the user-level `arcwright-task-runner` skill describes the same Claude Code GitHub-issue lifecycle. Its logic is fully covered by the canonical, platform-neutral `github-task-implementer`. To avoid two divergent copies, the operating model treats `github-task-implementer` as the single Implementer contract; client launchers point at it rather than re-creating task-runner.

## Relationship to the Rules

These contracts describe roles and flow. They do not restate the always-on rules. Every role is bound by `AGENTS.md` (engine constraints, approval gates, workflow, agent-local-file policy) and by `docs/conventions/`. If a role contract and `AGENTS.md` ever disagree, `AGENTS.md` wins.
