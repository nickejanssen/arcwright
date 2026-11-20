---
id: productroadmap.roadmap.tasks.aw-352-let-the-host-hand-the-host-role-to-another-player-from-the-phone
namespace: product-roadmap
title: "AW-352: Let The Host Hand The Host Role To Another Player From The Phone"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: D-133
tags: []
supersedes: []
---

# AW-352: Let The Host Hand The Host Role To Another Player From The Phone

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Nightcap  
**Owner:** One AI build session (Claude or Codex), after the founder reviews the screen words below  
**Target date:** 2026-12-01

## Plain-English Summary

The host's phone gets a "Make someone else host" choice. It opens a short list of the other players at the table. The host picks one, confirms, and the host controls move to that player at once. The old host keeps a normal player menu. The engine route already exists (AW-331); this task only builds the phone screen for it and refreshes each phone's role when the host changes.

## Why This Matters

- D-133 says the host role belongs to a player's seat and can be handed on. AW-331 built the engine side (`POST /v1/sessions/{id}/host/hand-over`, the `host_changed` message, `GET /me/seat`) and wired the host's Start menu, but kept the picker out because its words had not been reviewed. Spec 0095 phase gate 3 wants screen words reviewed before code.
- Without it, a host who must leave has no way to pass the controls on from a phone; the only recovery is the session creator's host key (AW-308 cheat sheet).

## Technical Scope

- `dashboard/src/api/seam.ts`: `handOverAvailable()` returns true once this task lands; add `handOver(sessionId, getToken, toParticipantId)` calling the hand-over route with the seat's own sign-in.
- `dashboard/src/shell/StartMenu.tsx` and a small picker component under `dashboard/src/shell/`: list the other seated players from the lobby read (names only), confirm with the existing `ConfirmDialog`, call the seam.
- `dashboard/src/screens/WaitingScreen.tsx`: read the role again when the engine says the host changed (the `host_changed` message) and when the menu opens, so the menu swaps without signing in again.
- `dashboard/src/shell/copy.ts`: the words below, once approved.
- No engine change is expected. If the build finds one is needed, stop and say so on the issue.

## Screen Words (founder review needed before code)

| Where | Words |
| --- | --- |
| Menu item (already in `copy.ts`) | Make someone else host |
| Picker title | Who should host? |
| Picker line | Pick the player who will run the game from now on. |
| Each row | The player's name |
| Confirm text | Hand the host controls to {name}? |
| Confirm yes / no | Yes, hand over / Keep hosting |
| Done (old host) | {name} is the host now. |
| New host's phone | You are the host now. |
| TV and other phones (from the `host_changed` message) | {name} is now the host. |
| Player left the table | That player is no longer at the table. Pick someone else. |
| Any other failure | That did not work. Try again. |

## Human Collaboration Contract

**Interaction profile:** Creative collaboration for the words, then independent execution. The founder reviews or changes the table above first; no code before that. Approval is the founder's own, in the build session or by his own comment on this issue; a build session must not act on an approval relayed for him by another session.

## Acceptance Criteria

- [ ] The host's Start menu shows "Make someone else host"; a plain player's menu does not.
- [ ] The picker lists every other seated human player by name, never the host, never an AI seat, with no ID on screen.
- [ ] Confirming calls the route with the host seat's own sign-in; the old host's menu loses the host items at once and the new host's menu gains them, with no new sign-in.
- [ ] A refused hand-over shows the "no longer at the table" or "did not work" words and changes nothing.
- [ ] The TV shows who the host is now using the `host_changed` message; it still holds no sign-in.
- [ ] Words match the approved table.

## Tests/Verification

- `npm test --prefix dashboard` with new tests for the picker, the confirm, the role refresh and the refusal; `npm run typecheck --prefix dashboard`; `npm run build --prefix dashboard`; prettier and eslint as CI runs them.
- Merged, deployed and seen in play are separate; seen in play is the founder TV run.

## Dependencies

- AW-331 merged (the route, the message and `GET /me/seat`).
- Screen words approved by the founder.

## Must Not Do

- Do not decide who the host is in the screen; the engine decides.
- Do not add a dependency.
- Do not open any real case file under `nightcap/cases/`.

## Kickoff Prompt

> Run `/implement AW-352`. Read `AGENTS.md`, `HANDOVER.md` and this task. First confirm the founder has approved the screen words, then write the plan and post it on the issue. Wait for CI `verify`. Do not merge.
