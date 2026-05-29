# Roadmap Organization

**Status**: Completed

**Author**: Codex | **Date**: 2026-05-24

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/12-build-plan.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0000-template.md`
- PRD sections: `docs/prd/03-scope.md`

---

# Overview

Restructure the build roadmap into an agent-friendly documentation area that preserves the human-readable plan while making milestones, epics, and task specs directly addressable.

---

# In Scope

- Create `docs/roadmap/` as the canonical roadmap location
- Split the roadmap into overview, milestone, epic, task, and operations files
- Add a lightweight machine-readable manifest at `docs/roadmap/index.json`
- Convert top-level roadmap source files into archival pointers to the canonical location

---

# Out of Scope

- Changing the roadmap’s actual execution content or sequencing
- Expanding milestone decomposition beyond what the current roadmap already decomposes
- Adding project-management automation beyond a static manifest

---

# Acceptance Criteria

- [x] `docs/roadmap/README.md` explains how humans and agents should use the roadmap
- [x] Milestones, epics, and task specs are addressable as separate files where the source roadmap already supports that split
- [x] `docs/roadmap/index.json` maps IDs, scope levels, dependencies, and file paths
- [x] `docs/12-Build-Roadmap-v1.md` becomes a short archival pointer to the canonical roadmap location
- [x] The companion GitHub setup file is moved into the roadmap area or replaced with a pointer

---

# Test Plan

- Read the new roadmap README and verify it is enough to navigate the structure
- Validate `docs/roadmap/index.json` as JSON
- Manually verify the split files preserve the original roadmap content and task IDs

---

# Risks and Unknowns

**Risks**:
- Duplicating roadmap text across too many files could make future updates drift if the structure is not clearly documented

**Unknowns**:
- Whether later roadmap revisions should promote the JSON manifest to the primary source for issue generation

---

# Open Questions

- None after approval of the split-plus-manifest approach
