# AW-254: First Production Nightcap Mini-game And Rehearsal

**Status**: Draft, blocked on AW-257

**Author**: Codex | **Date**: 2026-06-20

---

# Gate Outcome (2026-06-24)

A pre-implementation gate check found no founder-selected production game ID in
canonical docs, specs, or decision records, and no `active`-lifecycle package in
`nightcap/mini_games/` (only non-shipping `_fixtures/*` and `_template`). The
Open Question below ("Which authored game package will the founder select?") is
unresolved because no production package exists yet. Per founder direction
(D-061), the first production game is authored as precursor task AW-257; AW-254
depends on AW-257 and remains blocked until that package is authored, reviewed,
and founder-approved. No runtime or test code was changed by this gate check.

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
