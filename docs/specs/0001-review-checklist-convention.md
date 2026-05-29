# Reviewer Checklist Convention

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

Define a maintainer-facing checklist for reviewing agent-authored PRs so review quality is consistent and aligned with repo policy.

---

# In Scope

- Add `docs/conventions/review-checklist.md`
- Cover pre-diff, in-diff, and pre-merge review checks
- Include review checks for spec alignment, testing, LLM-dependent changes, docs, and ADR follow-through

---

# Out of Scope

- Changes to implementation code or tests
- Changes to CI configuration
- Broader edits to existing convention documents

---

# Acceptance Criteria

- [x] `docs/conventions/review-checklist.md` exists
- [x] The file includes the required top note verbatim
- [x] The file includes all requested checks under the three review phases
- [x] The file is under 60 lines

---

# Test Plan

- Manual review against the request
- Manual line-count check for `docs/conventions/review-checklist.md`

---

# Risks and Unknowns

**Risks**:
- The checklist could drift from repo policy if conventions change later

**Unknowns**:
- Whether the maintainer will want this checklist linked from other convention docs in a follow-up change

---

# Open Questions

- None for this scoped documentation addition
