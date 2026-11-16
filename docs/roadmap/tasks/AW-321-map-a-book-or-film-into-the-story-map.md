---
id: productroadmap.roadmap.tasks.aw-321-map-a-book-or-film-into-the-story-map
namespace: product-roadmap
title: "AW-321: Map A Book Or Film Into The Story Map"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-119
tags: []
supersedes: []
---

# AW-321: Map A Book Or Film Into The Story Map

**Milestone / Epic:** M6 / M6-D  
**Size:** M  
**Product:** Arcwright  
**Owner:** One AI build session; founder picks the stories and judges the maps  
**Target date:** 2027-02-13, or later: it waits for Nightcap to be live unless the founder pulls it forward

## Plain-English Summary

The founder's idea, 16 November 2026: pick a book or a film and have its story drawn in the same graphic story map planned for our own games. The aims are to see a story at a glance instead of reading it like a book, to learn from stories we admire, and to let that guide how the technology grows. This task tests the idea on two stories before anything larger is built.

## Why This Matters

- One map format for our own cases and for outside stories lets them be compared side by side.
- It reuses two planned pieces instead of adding a third: the story breakdown from the story library experiment (AW-314) and the read-only viewer (AW-317).
- Captured under D-119. It is an idea under test, not approved build scope.
- Founder direction, 16 November 2026: the story map is built for use with Arcwright. Priority 1 is mapping Arcwright and its games, a stretch item for the thin version (AW-306 and AW-317). Priority 2 is importing outside material and building its map (this task), which can wait until Nightcap is live unless the founder decides it is needed sooner. Viewing, editing and building a story are one tool, adopted first (AW-306).

## Technical Scope

- Use the same structure as AW-314: characters, secrets, motives, clue routes, story units, plus who learns what and when.
- Map two stories: one public-domain mystery worked from its full text, and one story the founder knows well enough to check the map himself.
- Show both in the adopted story tool (AW-306), or in the viewer proposed in AW-317 if that is where maps are read, next to one of our own cases the founder has already played.
- Work from the source text, a script or a detailed synopsis. A map made from a model's memory of a book invents plot points, so every node must point to where in the source it comes from.
- A book or film follows one path; our games branch. Mark clearly which parts of a map are the single path of the source.
- Limit: two build days, two founder hours, under $10 of model usage.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration. The founder picks the stories and judges whether each map is accurate and useful.

- Next gate: the founder reviews the two maps against what he knows of each story.
- Approval: the founder's written verdict on the issue, and whether to continue.

## Acceptance Criteria

- [ ] Two stories are mapped, and every node cites its place in the source.
- [ ] The founder scores each map 1 to 5 for accuracy and for whether it taught him something about story structure.
- [ ] Stop rule applied: if either score averages below 3, shelve the idea and record that.
- [ ] At least one finding is written down as a question for a Nightcap or Arcwright design decision.

## Tests/Verification

- The recorded scores and the founder's verdict.

## Dependencies

- AW-314 (the story breakdown format)
- AW-306 (the adopted story tool)
- AW-317 (the viewer proposal, for anything the adopted tool cannot show)

## Must Not Do

- Do not ship, publish or share maps of copyrighted books or films, and do not store their full text in the repository. Study maps are for internal use; get legal advice before any outside use.
- Do not show the founder the map of a case he has not yet played; it spoils the solution.
- Do not build a story editor in this task (D-114); the imported map opens in the adopted tool.
- An imported map informs writing and design only; it never decides what happens in a session.
