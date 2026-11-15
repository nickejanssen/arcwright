---
id: productroadmap.roadmap.tasks.aw-299-reconcile-the-tracker-with-the-rebuild
namespace: product-roadmap
title: "AW-299: Reconcile The Tracker With The Rebuild"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-299: Reconcile The Tracker With The Rebuild

**Milestone / Epic:** M7 / M7-A  
**Size:** M  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One planner session, with founder approval of wording  
**Target date:** 2026-11-28

## Plain-English Summary

Finish making GitHub describe the game being built. The 15 November pass added labels, a milestone and the missing tasks; this task does the parts that need checking or founder wording.

## Why This Matters

The tracker was written for the superseded Couch Race design. D-109 makes GitHub the owner of task status, so a tracker that describes the wrong game sends every session in the wrong direction.

## Technical Scope

- Test the acceptance criteria of #284, #202, #201 and #123, whose work is merged, then close each with the evidence or say what is missing.
- Read the stated blocker on each of the 13 issues labelled `blocked` and remove the label where the blocker is gone.
- Fix duplicate IDs: AW-270 names both #190 and #202; AW-218 names both #132 and #71. Give #138 a real ID.
- Fix milestone mismatches reported by `python scripts/roadmap_status.py` (#114, #202, #303).
- Rewrite the bodies of the twelve issues marked revise in the reset audit so they describe the Master GDD game, roadmap file first, then the issue.
- Rewrite the M5 and M6 exit criteria for the Master GDD game, with founder approval of the wording.
- Create issues for AW-288 and AW-292 or record them as superseded.
- Fix the index gap: three M1 epics are listed with no issue although #12, #17 and #25 exist.
- Sample ten closed issues from M4 and M5 and check the work exists in code; the reset audit inspected only four of 100 closed issues.

## Human Collaboration Contract

**Interaction profile:** Decision interview. Rewriting milestone exit criteria and closing issues are founder calls; everything else is mechanical.

## Acceptance Criteria

- [ ] `python scripts/roadmap_status.py` reports no duplicate IDs and no milestone mismatches.
- [ ] No open issue describes Couch Race as current scope without a `superseded` label.
- [ ] Each closed issue carries a comment linking the commit and the criteria checked.
- [ ] M5 and M6 milestone files and GitHub descriptions describe the Master GDD game, with the founder's approval recorded.

## Tests/Verification

- `python scripts/roadmap_status.py`
- `python scripts/checks/scope_evidence_check.py`

## Dependencies

- None
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not close an issue because its code merged; check its criteria (see `HANDOVER.md`, "a closed issue is not proof").
- Do not decide any row the reset audit marks as needing a founder decision.
