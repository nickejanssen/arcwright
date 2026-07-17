# AI Agent Contribution Policy

## Tool Allocation

**Copilot (inline):** Real-time assistance and small edits (single file, under 50 lines) while the human is at the keyboard. Use for: code completion, quick fixes, simple refactors.

**Claude Code:** Synchronous multi-file work requiring context reasoning and complex debugging. Use for: implementing specs, fixing bugs across modules, refactoring, writing tests. Suitable for tasks the human is actively supervising.

**Codex (cloud):** Delegated async work with explicit specs and clear
acceptance criteria. Use for independent execution and reversible research or
preparation. If a task requires a decision interview, creative collaboration,
facilitated live operation, or owner action, Codex must stop at the applicable
phase gate and wait for founder input.

## Requirements

**Spec-first:** Any task larger than a single function requires a spec in `/docs/specs/` before implementation. Specs must define acceptance criteria. Use the template.

**Plan-then-code:** Agent writes a plan (as prose or structured outline), human approves it, then code is written. No implementation without approval.

**Human collaboration classification:** Before planning or implementation,
declare the interaction profile and follow
`docs/conventions/human-collaboration.md`. Approval evidence must identify the
named decision, artifact, version, or phase that was approved.

**Tests with code:** Tests are written in the same commit/PR as the change, not in a follow-up. Tests must validate acceptance criteria from the spec. Focus areas: knowledge graph, arc transitions, safety, routing.

**Human review gate:** No PR merges to main without human review of the full diff. Automated checks (tests, linting, type checking) pass first, then human reviews.

## LLM-Dependent Code

Prompts, model selection, routing decisions, and eval cases are product surface and require scrutiny. Changes to these components require:
- Full traceability (why this model for this task?)
- An ADR in `/docs/decisions/` if behavior shifts meaningfully
- Extra review attention; these changes affect product quality and cost

## Branch Hygiene

- One agent per feature branch at a time
- If two agents must touch overlapping files, serialize them: first agent merges, second agent pulls main and continues
- Avoid merge conflicts on shared files by coordinating with the human

