---
id: operating.roadmap.tasks.aw-250-mini-game-content-resolution-and-safety
namespace: operating
title: "AW-250: Mini-game Content Resolution And Safety"
owner: Nico Janssen
status: active
review_by: "2027-01-08"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# AW-250: Mini-game Content Resolution And Safety

**Milestone / Epic:** M4 / M4-E
**Size:** M
**Status:** Complete

## Plain-English Summary

Resolve authored, generative, and hybrid content into one safe, immutable
runtime snapshot.

## Acceptance Criteria

- [ ] All content modes resolve to one versioned contract.
- [ ] Generative resolution uses provider-agnostic routing.
- [ ] Unsafe or invalid content cannot reach runtime execution.
- [ ] Aesthetic adaptation cannot change deterministic rules or state.
- [ ] Prompt and eval work receives explicit approval.

## Dependencies

- AW-249

## Must Not Do

- Do not let AI score games, select outcomes, unlock clues, or mutate state.
- Do not implement persistence, transport, or rendering.

## References

- `docs/specs/0047-aw-250-mini-game-content-resolution-and-safety.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`

