# Initial Eval Harness

**Status**: Done

**Author**: Codex | **Date**: 2026-05-21

---

# References

- Architecture sections: `docs/architecture/06-model-routing.md`, `docs/architecture/15-development-guide.md`
- PRD sections: `docs/prd/02-requirements.md`, `docs/prd/04-non-goals.md`
- Related specs: `docs/specs/0000-template.md`
- Convention files: `docs/conventions/ai-contributions.md`

---

# Overview

Add a runnable eval harness for the LLM-dependent surface that exists today: routing-table behavior and provider/model routing-policy invariants.

---

# In Scope

- Add `/evals` with JSON cases, a simple pytest runner, reports scaffolding, and README guidance
- Evaluate `config/routing_table.json` coverage and machine-checkable routing assertions
- Add a non-blocking GitHub Actions workflow that reports eval results on relevant pull requests

---

# Out of Scope

- Prompt-quality scoring for prompt files that do not exist yet
- Full live model-call eval execution against external providers
- Merge-blocking on eval regressions

---

# Acceptance Criteria

- [x] `/evals/cases`, `/evals/runners`, `/evals/reports`, and `/evals/README.md` exist
- [x] At least one JSON eval case covers the current routing-table behavior
- [x] A pytest-based runner loads eval cases and checks the actual repo implementation files
- [x] Eval reports are written under `/evals/reports`, which is gitignored except for `.gitkeep`
- [x] `.github/workflows/evals.yml` runs on relevant PR changes, reports results, and does not fail the PR on eval regressions
- [x] The local eval runner is executable with the repo’s current Python test tooling

---

# Test Plan

- Run the eval runner locally with pytest
- Validate the eval workflow YAML structure
- Manually confirm the workflow uses path filters and posts a summary comment on pull requests

---

# Risks and Unknowns

**Risks**:
- The harness may feel narrow until prompt files and router implementation code exist
- GitHub comment permissions can differ between same-repo PRs and forks, so comment posting needs a safe fallback

**Unknowns**:
- Which future LLM-dependent code path will be the next one added to the harness first: prompt assembly, safety classification, or routing fallback behavior

---

# Open Questions

- None after approval of the initial routing-focused scope
