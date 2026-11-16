---
id: productroadmap.roadmap.tasks.aw-320-friend-voiced-characters-recorded-lines-first
namespace: product-roadmap
title: "AW-320: Friend-Voiced Characters, Recorded Lines First"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-119
tags: []
supersedes: []
---

# AW-320: Friend-Voiced Characters, Recorded Lines First

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Nightcap  
**Owner:** One AI build session; the founder and friends record  
**Target date:** 2026-12-09

## Plain-English Summary

The founder's idea, 16 November 2026: he and friends voice the characters, tools clean the audio, and in time a character plus its voice can be placed in any story or game. For the thin version this is a stretch item: do it only if there is room once everything else for session 1 is complete, and take the most affordable route with the highest quality and the lowest difficulty.

## Why This Matters

- Story presentation is animation plus audio plus text (D-070), and interrogation audio is a hard quality gate (D-090). Real voices from friends are the cheapest way to get good audio for authored lines.
- A voice as one more attribute of a character fits the unified character model, so the same character could be reused across stories later.
- Captured under D-119. Founder direction on scope and route given in session on 16 November 2026.

## Technical Scope

Route for the thin version (cheapest, lowest difficulty): friends record the authored lines directly. No voice cloning.

- List the authored spoken lines of the first case (AW-305) per character, without spoilers in anything the founder reads.
- Friends record on phones. Clean the recordings with a free or already-owned noise-removal tool.
- Store the audio as content beside the case in `nightcap/`. The screen plays a stored clip when an event's voice hint points to one. The engine does not handle audio.
- First step, before any recording: check whether the session 1 screens can already play a stored clip for an event. This was not verified when the task was written.
- Lines the AI improvises at run time stay as they are in the thin version (no live generated speech).
- After session 1, as a separate step: compare recorded lines with a cloned voice for one character and one consenting friend, with current provider prices and recording needs checked at that time.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration and a founder action (recording).

- Founder inputs: who voices whom, and each friend's written consent.
- Next gate: the founder confirms there is room, meaning every other session 1 task is done.
- Approval: the founder's go-ahead on the issue. Any paid tool or new package needs explicit approval first.

## Acceptance Criteria

- [ ] Started only after every other session 1 task is complete; otherwise moved to after session 1 and recorded as such.
- [ ] Each person who records has agreed in writing to how their voice may be used and how to withdraw it.
- [ ] Authored lines for at least one character play as recorded audio in a full run on the TV.

## Tests/Verification

- One full run on the TV with the recorded lines heard at the right moments. Say separately what is merged and what was seen in play.

## Dependencies

- AW-305 (the first case, whose authored lines are recorded)

## Must Not Do

- Do not let this delay session 1; it is the first thing to cut.
- Do not clone anyone's voice in the thin version, and never without written consent.
- Do not put audio or playback logic in `engine/`.
- Do not add a paid service or a new dependency without the founder's approval.
- Do not reveal the first case's solution in line lists or recording scripts shown to anyone who will play it.
