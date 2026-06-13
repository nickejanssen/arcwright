# Docs Organization

**Status**: Done

**Author**: Codex | **Date**: 2026-06-13

---

# References

- Related ADRs: [docs/decisions/0001-scaffolding-audit.md](../decisions/0001-scaffolding-audit.md)
- Architecture sections: [docs/architecture/01-overview.md](../architecture/01-overview.md), [docs/architecture/15-development-guide.md](../architecture/15-development-guide.md)
- Related specs: [docs/specs/0006-roadmap-organization.md](0006-roadmap-organization.md), [docs/specs/0007-roadmap-tracker-alignment.md](0007-roadmap-tracker-alignment.md)
- PRD sections: [docs/prd/01-overview.md](../prd/01-overview.md)

---

# Overview

This spec defines the repository documentation layout so active canonical docs are separated from raw Notion exports and historical artifacts without losing context.

---

# In Scope

- Add a top-level documentation README with canonical reading order and editing rules
- Add stable homes for product logs, story bibles, and archived Notion exports
- Move loose root-level docs into the appropriate folder
- Preserve all source context from the previous `docs/` root
- Update canonical references that point to moved files

---

# Out of Scope

- Product-content edits to the PRD, story bibles, decisions log, or open questions log
- Deleting historical artifacts
- Changing implementation specs, roadmap scope, or architecture decisions beyond path references
- Rewriting old Notion export links inside archived files

---

# Acceptance Criteria

- [x] `docs/README.md` explains canonical folders, archive folders, reading order, and editing rules
- [x] Root-level Notion export artifacts are moved out of `docs/` root
- [x] Active story bibles live under `docs/story-bibles/`
- [x] Product decision and open-question logs live under `docs/product/`
- [x] Raw source exports remain available under `docs/archive/notion-export/`
- [x] Canonical docs and skills reference the new folder structure
- [x] No `.claude/`, `.codex/`, `.cursor/`, `.vscode/`, or similar agent-local files are modified or staged
- [x] Active documentation uses stable filenames with in-file version metadata instead of one active file per version
- [x] AI-cost guidance directs agents to canonical targeted reads before archived source recovery

---

# Test Plan

- Inspect `docs/` root for only canonical folders and top-level navigation files
- Run `rg` for references to old moved root paths from canonical folders
- Run `git status --short` and verify only intended documentation changes appear

---

# Risks and Unknowns

**Risks**:
- Some historical archived links may point to files by their old root-relative location
- External links or personal bookmarks to old root-level files may need updating

**Unknowns**:
- Whether Notion will continue to sync raw exports into `docs/` root or can be configured to sync into `docs/archive/notion-export/`

---

# Open Questions

- Should future Notion syncs write directly to `docs/archive/notion-export/`?
- Should full monolithic PRD and architecture exports be regenerated periodically, or should the split canonical docs become the only maintained form?
