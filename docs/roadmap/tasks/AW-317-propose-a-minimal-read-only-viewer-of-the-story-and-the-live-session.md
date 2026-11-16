---
id: productroadmap.roadmap.tasks.aw-317-propose-a-minimal-read-only-viewer-of-the-story-and-the-live-session
namespace: product-roadmap
title: "AW-317: Propose A Minimal Read-Only Viewer Of The Story And The Live Session"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-317: Propose A Minimal Read-Only Viewer Of The Story And The Live Session

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Arcwright  
**Owner:** One spec-author session; founder decides whether to pull it forward  
**Target date:** 2026-12-05 (stretch for the thin version)

## Plain-English Summary

The founder said a visual view would help him understand how Arcwright is working. Propose the smallest read-only viewer that does that, using an existing graph-drawing library, and map it onto the four existing inspection tasks.

## Why This Matters

The roadmap's first visual-editor phase is read-only inspection (AW-236 to AW-239). None is built. The reset read only one paragraph of the PRD's five-phase plan.

## Technical Scope

- Read the PRD's Visual Storyworld plan in full and summarise the five phases in plain words.
- Propose two views: the story structure (beats, their conditions, bound mini-games) and the live session (current beat, who knows what).
- Draw graphs with React Flow (MIT) or Cytoscape.js (MIT); do not hand-draw them.
- Do not build a general story editor; writing happens in an adopted tool (AW-306). Show only what Arcwright alone knows.
- Trigger to build: the founder cannot tell why something happened during a debrief.
- Founder direction, 16 November 2026: this is a stretch item for the thin version. "I need to be able to read and manipulate the stories graphically. Story editing, story building, and story viewing are all part of the same tool. That tool can be adopted or built. We are currently going to adopt instead of build to start with so we can save time."
- So the first step is to check what the adopted story tool (AW-306) already shows and lets the founder change graphically. This proposal covers only what that tool cannot show, such as the live session and who knows what.
- Priority 1 is mapping Arcwright and its games. Priority 2 is importing outside material such as a book or film (AW-321).

## Human Collaboration Contract

**Interaction profile:** Decision interview. Whether to build it before session 2 is the founder's call (#51).

## Acceptance Criteria

- [ ] A two-page proposal with a sketch, a size estimate and the mapping to AW-236 to AW-239.
- [ ] The founder's decision on timing is recorded on #51.

## Tests/Verification

- Founder review.

## Dependencies

- None
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- No implementation in this task.
- Do not build editing features here; editing and building happen in the adopted tool (AW-306) for now.
