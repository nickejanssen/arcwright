# Roadmap Tracker Alignment

**Status**: Done

**Author**: Codex | **Date**: 2026-05-29

---

# References

- Related specs: `docs/specs/0006-roadmap-organization.md`
- Related docs: `docs/roadmap/README.md`, `docs/roadmap/index.json`
- GitHub templates: `.github/ISSUE_TEMPLATE/feature.md`, `.github/pull_request_template.md`

---

# Overview

Refine the roadmap so it remains the canonical planning source in-repo while cleanly cross-referencing the live GitHub tracker for active milestone and issue work.

---

# In Scope

- Preserve `docs/roadmap/` as the canonical roadmap location
- Add guidance for how roadmap files should relate to live GitHub issues and milestones
- Add machine-readable GitHub references to the roadmap manifest where they are known
- Add a filename-compatible archival pointer for `12-Build-Roadmap-v1.1.md`

---

# Out of Scope

- Rewriting roadmap scope, sequencing, or task content
- Creating or modifying live GitHub issues, milestones, labels, or project fields
- Embedding issue numbers throughout every roadmap Markdown file

---

# Acceptance Criteria

- [x] `docs/roadmap/README.md` explains the roadmap-to-GitHub relationship
- [x] `docs/roadmap/index.json` includes tracker metadata and known live GitHub references
- [x] The roadmap keeps Markdown as canonical and uses the manifest for live GitHub cross-references
- [x] `docs/roadmap/operations/github-project-setup.md` reflects the live tracker state instead of one-time setup only
- [x] `docs/12-Build-Roadmap-v1.1.md` exists as an archival pointer to the canonical roadmap

---

# Test Plan

- Validate `docs/roadmap/index.json` as JSON
- Manually verify the known GitHub links for M1 Epic A match the live public issue pages
- Read the updated roadmap README and GitHub operations doc to confirm the ownership split is clear
