---
id: productroadmap.roadmap.tasks.aw-366-stop-the-dashboard-dev-server-serving-case-files
namespace: product-roadmap
title: "AW-366: Stop The Dashboard Dev Server Serving Case Files To Phones"
owner: Nico Janssen
status: draft
review_by: "2027-02-26"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-366: Stop The Dashboard Dev Server Serving Case Files To Phones

**Milestone / Epic:** M7 / M7-C
**Size:** S
**Product:** Shared
**Owner:** One build session, after founder approval of its plan
**GitHub issue:** [#510](https://github.com/nickejanssen/arcwright/issues/510)  
**Target date:** 2026-11-28

## Plain-English Summary

The program that serves the game screens will also hand out other files from the project folder to anyone who can reach it and knows the file's location. The case files, which hold the solution, are not on its blocked list.

## Why This Matters

- Found during AW-308 (#362). **Checked** on 2026-11-26 with a harmless made-up file under `nightcap/`: the dev server returned it, while a file under `engine/` was refused. No case file was opened or requested.
- `dashboard/vite.config.ts` (and the committed `vite.config.js`) `server.fs.deny` lists `.env`, keys, mini-game server folders and `engine/` only.
- D-153: solutions stay out of anywhere players could read them.
- A player would need to know or find the file's full path (inferred: not tried).

## Technical Scope

1. Deny the case folder in both Vite config files, and review what else players should not read.
2. Prefer an allow list of the folders the screens need if that stays small.
3. Add a test that the case folder is refused, using a made-up path.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. The founder approves the plan in their own words before any code.

## Acceptance Criteria

1. A request for any file under the case folder is refused by the dev server.
2. Mini-game screens still load.
3. No test or log opens or prints a case file.

## Tests/Verification

- `npm test --prefix dashboard`.
- A request for a made-up path under the case folder returns 403.

## Dependencies

- None.

## Must Not Do

- Do not open or quote files in `nightcap/cases/`.
- Do not add a dependency without approval.
