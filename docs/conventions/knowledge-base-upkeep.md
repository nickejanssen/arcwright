---
id: engineeringpractice.conventions.knowledge-base-upkeep
namespace: engineering-practice
title: Knowledge Base Upkeep And Accuracy Check
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

> Current version: v1.0
> Last updated: 2026-11-15
> Status: Current
> Canonical path: docs/conventions/knowledge-base-upkeep.md

# Knowledge Base Upkeep And Accuracy Check

How knowledge gets into the right place, and how we check that the specialist agents answer from it correctly. This is a routine and a manual check. It adds no tooling, so it is allowed under the tooling freeze (D-110, D-111). Owner: the Scribe role (`docs/agents/scribe.md`).

## Where each kind of knowledge goes

One home per kind. If the home already has a document on the topic, fold the new material into it; do not add a parallel document.

| Kind of knowledge | Home | Who can read it |
| --- | --- | --- |
| A founder decision | `docs/product/decisions-log.csv`; an ADR in `docs/decisions/` when it shapes architecture | Every agent and the specialist agents |
| A question not yet answered | `docs/product/open-questions-log.csv` | Same |
| Work to be done | `docs/roadmap/tasks/` plus a GitHub issue (D-119) | Same |
| Whether work is open or closed | GitHub only (D-109) | `python scripts/roadmap_status.py` |
| The stack and what we adopt | `docs/architecture/02-technology-stack.md` | Same |
| Game design | `docs/gdd/nightcap/` | Same |
| What a play session showed | The GDD validation pages | Same |
| What every session must know before starting | `HANDOVER.md` | Every agent |
| How the founder wants to be worked with | `docs/conventions/human-collaboration.md` | Every agent |
| A tool's private notes (for example Claude's memory) | Only preferences about that tool. Project facts do not belong there; move them to `HANDOVER.md` or the docs | That tool only |

A document enters the knowledge base when it is under `docs/`, carries the standard front matter (`id`, `namespace`, `owner`, `status`, `review_by`) and is merged to main. The `team-ai` check validates the front matter on every pull request.

## The routine

- **After every merged pull request:** one dated line in the `HANDOVER.md` log.
- **After every founder decision:** a row in the decisions log, recorded with explicit approval evidence.
- **After every play session:** findings go into the GDD validation pages, not chat.
- **After any change to how docs are organised, and after the agent guard is fixed (AW-296):** run the ten-question check below (AW-297).

## The ten-question check

Each question has an answer verified from a source on 2026-11-14 or 15. One session asks the owning specialist agent and scores four things per question: answered, correct, cited the right file, and flagged a known conflict where one exists.

| # | Question | Verified answer |
| --- | --- | --- |
| 1 | Is spec 0092 approved? | No. Draft |
| 2 | When does the tooling freeze end? | At the rebuild's first TV session (D-111) |
| 3 | Has Gate 1 passed? | No |
| 4 | What is the two-player rule? | Two players is mandatory and first-class |
| 5 | Who decides a state transition? | Deterministic rules, never a model |
| 6 | Which source owns task status? | GitHub (D-109) |
| 7 | Is contradiction-catching a current Nightcap mechanic? | Parked |
| 8 | What breaks ties among solvers? | Mini-game performance |
| 9 | Which second game do the docs name? | Two candidates; the agent should flag the conflict |
| 10 | Is Couch Race the current design? | No. Superseded |

**Target:** at least eight of ten correct with the right citation. Every miss becomes a GitHub issue naming the document or agent to fix.

## Results

| Date | Answered | Correct | Right citation | Conflict flagged | Notes |
| --- | --- | --- | --- | --- | --- |
| 2026-11-14 | 0 of 3 probes | Does not apply | Does not apply | Does not apply | All three probes were refused access to `docs/` from a worktree session. Cause and fix: AW-296. The ten questions have not been run yet |

## Measures

| Measure | How |
| --- | --- |
| Citation accuracy | The score on the ten questions |
| Time to a useful answer | Minutes from question to a cited answer, on the same ten |
| Repeated rework | The founder's weekly tally of things explained twice, plus pull requests reopened |
