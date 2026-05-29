# CI and CodeQL Workflows

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

Add GitHub Actions workflows for CI and CodeQL so Arcwright runs consistent automated checks on pushes to `main` and on pull requests.

---

# In Scope

- Add `.github/workflows/ci.yml`
- Add `.github/workflows/codeql.yml`
- Configure dependency caching and concurrency cancellation
- Run lint, type check, tests, build, and gitleaks checks that match the current repo toolchain

---

# Out of Scope

- New application code
- New package manager lockfiles
- Expanded CI coverage beyond the currently configured Python and TypeScript tooling

---

# Acceptance Criteria

- [x] `ci.yml` runs on `pull_request` and `push` to `main`
- [x] `ci.yml` uses one inferred Python version and one inferred Node version without a version matrix
- [x] `ci.yml` installs dependencies with caching, then runs lint, type check, tests, applicable builds, and gitleaks
- [x] `ci.yml` cancels superseded runs for the same branch or pull request
- [x] `codeql.yml` uses GitHub CodeQL for the detected `python` and `javascript-typescript` languages
- [x] Both workflow files are valid YAML

---

# Test Plan

- Validate workflow YAML structure locally
- Manually verify workflow triggers, steps, and concurrency configuration
- Confirm the CI commands match the scripts and files that exist in the repo today

---

# Risks and Unknowns

**Risks**:
- The repo currently has no `.nvmrc`, `.python-version`, or lockfiles, so CI must infer sensible runtime defaults from existing project files
- The TypeScript packages currently rely on `npm install` rather than `npm ci`, which may be slower and less reproducible until lockfiles exist

**Unknowns**:
- Whether future repo growth will justify splitting CI into multiple jobs or adding path filters

---

# Open Questions

- None after approval of the inferred runtime assumptions
