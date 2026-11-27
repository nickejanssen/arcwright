---
id: productroadmap.roadmap.tasks.aw-369-keep-authored-case-validation-from-freezing-the-api
namespace: product-roadmap
title: "AW-369: Keep Authored-Case Validation From Freezing The API"
owner: Nico Janssen
status: draft
review_by: "2027-02-26"
sensitivity: internal
source: authored
x-scope-evidence: "D-124, D-139"
tags: []
supersedes: []
---

# AW-369: Keep Authored-Case Validation From Freezing The API

- **Milestone / Epic:** M7 / M7-B
- **Size:** M
- **Product:** Shared
- **Owner:** One build session after founder approval of its plan
- **GitHub issue:** [#513](https://github.com/nickejanssen/arcwright/issues/513)
- **Target date:** 2026-11-30 (proposed before the founder rehearsal)

## Plain-English Summary

Opening the TV for a new case can leave it on Connecting for minutes. In the local 1a dress rehearsal, opening the TV also stopped the API from answering its health endpoint. Other games on the same API could be affected while the check runs.

## Why This Matters

- Observed during the 2026-11-26 local browser rehearsal from AW-301 (#354). The API created a 1a session, then the TV's first room read stalled before the lobby. The API recovered after roughly four minutes.
- Local stack samples put the request in `room_view` → `closing_view` → authored-case rule A3. The case search runs synchronously on the same thread handling the API. `load_arc_case` also performs synchronous validation when the host starts a session.

## Technical Scope

1. Keep lobby reads responsive while an authored case is checked. Avoid loading the case for public closing data before the closing phases need it.
2. Keep the API responsive during checks triggered by Start. Preserve exact A3 results and the refusal of an invalid case before play begins.
3. Define how successful validation can be reused and when a changed file must be checked again. Keep the runtime game-agnostic.

## Human Collaboration Contract

**Interaction profile:** Independent execution after explicit founder approval of the implementation plan. The plan must cover validation ownership and the boundary between the case and session modules before changing either.

## Acceptance Criteria

- [ ] On a cold process, the session's TV lobby loads and loopback health requests continue to complete while a slow case check is in progress.
- [ ] Start waits for a valid case and refuses an invalid case. A changed case is checked again.
- [ ] The authored-case checker returns the same decisions and minimum paid-choice counts for passing and failing fixtures.
- [ ] The 1a browser rehearsal is repeated at two and four seats, with a spoiler-free update on #354.

## Tests/Verification

- Authored-case, session-start, room-view and API tests, using synthetic content for any new checked-in fixture.
- Repeat the cold local 1a smoke test. Record elapsed time and checkpoint statuses outside the case data.

## Dependencies

- AW-324 and the local converted 1a case for verification.

## Must Not Do

- Do not weaken or bypass case validation, add a dependency, or add Nightcap-specific rules to the engine.
- Keep the converted case and its contents out of Git and GitHub (D-153).
