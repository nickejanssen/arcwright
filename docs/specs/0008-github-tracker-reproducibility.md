# GitHub Tracker Reproducibility

**Status**: Done

**Author**: Codex | **Date**: 2026-05-29

---

# References

- Related specs: `docs/specs/0007-roadmap-tracker-alignment.md`
- Related docs: `docs/roadmap/operations/github-project-setup.md`, `docs/roadmap/index.json`
- GitHub templates: `.github/ISSUE_TEMPLATE/feature.md`, `.github/ISSUE_TEMPLATE/bug.md`, `.github/pull_request_template.md`

---

# Overview

Capture the current live GitHub tracker setup in repo-owned configuration so labels, milestones, project fields, and seed roadmap issues can be recreated from the codebase if needed.

---

# In Scope

- Add machine-readable GitHub tracker config under `.github/`
- Document how the current live setup can be rebuilt from those files
- Clarify the role of the archival `12b` setup file now that the live setup already exists

---

# Out of Scope

- Creating or modifying live GitHub labels, milestones, project fields, or issues from this environment
- Rewriting roadmap epic or task content
- Adding a networked bootstrap script that cannot be exercised safely here

---

# Acceptance Criteria

- [x] Repo contains machine-readable tracker configuration for labels, milestones, project fields, and the M1 Epic A seed issues
- [x] Canonical GitHub operations doc explains how to rebuild the setup from repo files
- [x] `12b-GitHub-M1-Epic-A-Setup.md` is treated as an archival pointer, not the canonical operational source
- [x] Roadmap manifest points at the tracker configuration so agents can discover it quickly

---

# Test Plan

- Validate the new JSON config files as JSON
- Read the rebuilt operations doc to confirm a maintainer could recreate the tracker from repo state
- Verify roadmap manifest references the new tracker config paths
