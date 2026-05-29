# Pre-Commit Hook Setup

**Status**: Done

**Author**: Codex | **Date**: 2026-05-21

---

# References

- Architecture sections: `docs/architecture/15-development-guide.md`
- PRD sections: `docs/prd/01-overview.md`
- Related specs: `docs/specs/0000-template.md`
- Convention files: `docs/conventions/ai-contributions.md`

---

# Overview

Add a repo-wide pre-commit hook setup that fits Arcwright's mixed Python and TypeScript toolchain and blocks common quality and security mistakes before commit.

---

# In Scope

- Add a root `.pre-commit-config.yaml`
- Add non-destructive formatter and linter checks for Python and JS/TS
- Add a gitleaks secrets scan
- Add a check that rejects temporary debug markers
- Document local hook installation in conventions and README

---

# Out of Scope

- CI workflow changes
- Auto-fixing hooks that rewrite files during commit
- Broad refactors to existing source files

---

# Acceptance Criteria

- [x] `pre-commit` is configured at the repo root
- [x] Python files are checked with Ruff lint and Ruff format in check-only mode
- [x] JS/TS files are checked with Prettier and ESLint in check-only mode
- [x] Commits fail if gitleaks detects secrets
- [x] Commits fail if staged files contain the configured temporary-marker strings
- [x] `docs/conventions/setup.md` explains local installation and usage
- [x] `README.md` Getting Started includes the hook install command

---

# Test Plan

- Validate `.pre-commit-config.yaml` structure
- Run targeted config checks where local tooling is available
- Manually verify docs against the configured commands

---

# Risks and Unknowns

**Risks**:
- New hook tooling may surface a large number of existing style issues when first run
- Repo-local JS/TS lint configuration may need refinement as the SDK and dashboard grow

**Unknowns**:
- Whether the maintainer wants hook execution mirrored in CI in a follow-up change

---

# Open Questions

- None after approval to add the needed dev-only tooling for JS/TS checks
