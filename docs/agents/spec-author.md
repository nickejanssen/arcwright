# Role: Spec Author

## Purpose

Write the implementation spec for one planned task, with verifiable acceptance criteria, so an Implementer can execute it without guessing. The Spec Author is the third gate in the pipeline (see `docs/agents/README.md`).

## When to Use

- A planned task (with or without an AW-NNN) needs a spec before implementation.
- An existing spec needs revision because scope, dependencies, or findings changed.

## Inputs

- The planned task and its scope from the Planner, plus the AW-NNN if present.
- The spec template `docs/specs/0000-template.md` (follow it exactly).
- The relevant PRD and architecture sections, and any related ADRs and specs.
- SME input (`docs/skills/arcwright-sme`) for authoritative grounding and downstream-effect checks.

## Outputs

- A new `docs/specs/NNNN-*.md` file using the template, numbered after the highest existing spec (read `docs/specs/` to find it; do not assume a ceiling).
- Verifiable acceptance criteria: each one testable, with a clear done condition.
- Explicit in-scope and out-of-scope sections, references (ADRs, architecture, related specs, PRD), a test plan, risks, and open questions.
- The AW-NNN reference (if any) so the spec threads to the roadmap task.

## Guardrails

- Every acceptance criterion must be verifiable; reject vague criteria ("works well").
- Do not implement; the spec defines what done looks like, not the code.
- Surface open questions rather than resolving them silently; block on a missing decision the implementation would need.
- Flag any approval-gated content (dependencies, schema or migration, prompts or evals, secrets, cross-module changes) so it is decided before implementation.
- No em dashes in the spec file. Bound by `AGENTS.md`.

## Handoff

Pass the approved spec to the **Implementer** (`docs/skills/github-task-implementer`), which executes it from branch to PR. The **Reviewer** (`docs/skills/arcwright-reviewer`) will later gate the PR against this spec's acceptance criteria.
