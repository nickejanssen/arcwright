# AW-254: First Production Nightcap Mini-game And Rehearsal

**Status**: Draft

**Author**: Codex | **Date**: 2026-06-20

---

# References

- Related ADRs: `docs/decisions/0009-mini-game-runtime-boundary.md`
- Related specs: `docs/specs/0050-aw-253-nightcap-web-mini-game-rendering.md`
- Story bible: `docs/story-bibles/nightcap-murder-mystery.md`
- GitHub issue: #148

---

# Overview

Promote one founder-selected mini-game from playtest to active and verify the
complete clue-gated flow on real devices.

---

# In Scope

- Founder-approved rules, content, assets, placement, and lifecycle promotion
- Normal completion and delayed fallback paths
- Privacy, safety, accessibility, reconnect, pause/resume, and behavioral output
  verification
- Rehearsal findings and blocker triage

---

# Out Of Scope

- Selecting or inventing the production game without founder approval
- Activating non-shipping fixtures
- v1.1 killer-assignment or cross-session behavioral use

---

# Acceptance Criteria

- [ ] The founder names the production game ID before implementation starts.
- [ ] The selected package passes content, asset, safety, and schema review.
- [ ] The active game runs end-to-end on supported devices.
- [ ] Completion and timeout fallback both preserve a solvable clue path.
- [ ] Privacy, reconnect, pause/resume, behavioral output, and accessibility
  checks pass.
- [ ] Every rehearsal blocker is triaged before AW-231 completes.

---

# Test Plan

- Package validation and content review
- Automated completion and timeout paths
- Real-device privacy and accessibility matrix
- Human rehearsal with recorded findings

---

# Risks and Unknowns

**Risks**: Production activation before content approval could expose unsafe or
unsolvable material.

**Unknowns**: The first production game is intentionally unselected.

---

# Open Questions

- Which authored game package will the founder select?
