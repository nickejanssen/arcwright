---
id: productroadmap.roadmap.tasks.aw-365-keep-phones-updating-during-the-mini-game-without-a-live-stream
namespace: product-roadmap
title: "AW-365: Keep Phones Updating During The Mini-Game When The Live Stream Is Unavailable"
owner: Nico Janssen
status: draft
review_by: "2027-02-26"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-365: Keep Phones Updating During The Mini-Game When The Live Stream Is Unavailable

**Milestone / Epic:** M7 / M7-C
**Size:** M
**Product:** Arcwright (dashboard mini-game kit), with Nightcap as the first user
**Owner:** One build session, after founder approval of its plan
**GitHub issue:** [#509](https://github.com/nickejanssen/arcwright/issues/509)  
**Target date:** 2026-11-29

## Plain-English Summary

The mini-game screen moves to the next question only when a live event stream tells it to. The Cloudflare quick tunnel used so far does not carry that kind of stream, and the screen also stops listening after about two seconds of failures. A phone could sit on one question until reloaded.

## Why This Matters

- Found during AW-308 (#362) by reading the code. **The effect on a real phone is inferred and has not been seen.**
- [Cloudflare's Quick Tunnels limits](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/): no Server-Sent Events.
- `dashboard/src/mini-games/client.ts`: one read at start, then refreshes from the stream (plus a timer during a result hold only); gives up after three retries.
- The other screens also re-read every two seconds (`dashboard/src/shell/useFeed.ts`).
- Until fixed, the host cheat sheet says to connect phones over home Wi-Fi.

## Technical Scope

1. Reproduce through a quick tunnel on a real phone.
2. Make the mini-game stage re-read its state on a steady beat while it is on screen, and keep retrying the stream.
3. Keep it game-agnostic and keep private state filtered as today.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. The founder approves the plan in their own words before any code.

## Acceptance Criteria

1. A test shows the stage reaching the next question when the event stream never answers.
2. A test shows it recovering after more than three failed stream attempts.
3. No private state reaches a surface that cannot read it today.

## Tests/Verification

- `npm test --prefix dashboard`.
- One run through a tunnel on a real phone, reported separately from merged.

## Dependencies

- None.

## Must Not Do

- Do not open or quote files in `nightcap/cases/`.
- Do not add a dependency without approval.
