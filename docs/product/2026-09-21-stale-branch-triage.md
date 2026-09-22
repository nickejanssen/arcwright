---
id: productroadmap.product.2026-09-21-stale-branch-triage
namespace: product-roadmap
title: Stale Branch Triage, 2026-09-21
owner: Nico Janssen
status: active
review_by: "2027-03-21"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

> Current version: v1.0
> Status: active
> Last updated: 2026-09-21
> Canonical path: `docs/product/2026-09-21-stale-branch-triage.md`

# Stale Branch Triage, 2026-09-21

Fifteen git worktrees had accumulated across `.codex/`, `.claude/`, and two
other locations. Nine held work that was already merged. This record exists so
the next person does not have to redo the triage, and so the one branch that
looked valuable is not resurrected on the strength of its commit messages.

## Why merged branches looked unmerged

team-ai and this repository both squash-merge. A squash rewrites the branch's
commits into one new commit with a different hash, so the originals are never
ancestors of `main`. `git log origin/main..<branch>` therefore lists them
forever, and `git branch --merged` never names the branch.

**Check content, not ancestry.** `git cherry -v origin/main <branch>` marks
patch-equivalent commits with `-`, and `git diff --stat origin/main <branch>`
shows whether anything of substance differs. A branch whose diff against `main`
is mostly deletions is behind `main`, not ahead of it.

## `claude/nightcap-three-axis-solve-6ea409`: retired, do not merge

Eleven commits, last dated 2026-08-09, 467 documentation files differing from
`main`. Superficially the most valuable branch on disk. Every item was checked
against `main`:

| Branch commit | Verdict |
|---|---|
| `docs(decisions)`: three-axis Couch Race solve as ADR-0023 | **Superseded and unsafe.** `main` has a different ADR at 0023, `0023-nightcap-master-gdd-authority.md` (D-108, 2026-08-31), which retires Couch Race authority in favour of `docs/gdd/nightcap/`. Merging would both duplicate the ADR number and resurrect a decision a later one replaced |
| `docs(product)`: 2026-08-08 docs currency findings | Already on `main`; patch-equivalent |
| `fix(product)`: quote the D-106 Decision field | Unnecessary. The field contains no comma, so `main`'s unquoted row is valid CSV and parses |
| `docs(prd,architecture)`: replace Notion-authority headers | Superseded. Phase B's front-matter backfill (ADR-0024) replaced those headers with KB front matter carrying `id`, `namespace`, `status` and `review_by` |
| `docs(prd)`: fold the ADR-0013 amendment into MVP scope | Superseded. `docs/prd/03-scope.md` now carries both the historical ADR-0013 amendment and the current ADR-0023 / D-108 amendment |
| `docs(prd)`: rewrite the Nightcap Reference Implementation section | Superseded by the ADR-0023 authority override already in `docs/prd/02-requirements.md` |
| `docs(readme)`: fix stale Notion links | Superseded. `README.md` on `main` mentions Notion nowhere |
| `docs`: deprecate Notion as a documentation source | Superseded |
| `chore(docs-bundles)`: remove stale pre-pivot snapshots | **Correct, and still pending.** Applied here |
| `docs(architecture,roadmap)`: propagate ADR-0013/0023 | Superseded by D-108 |
| `docs(product)`: log the TMST player-floor conflict | Moot. D-108 makes two-player mandatory and four a reference configuration, and retires the Couch Race fixed shape the conflict was about |
| `docs(product)`: log Notion-draft-recovery risk | **Wrong on two counts.** It cites D-107 for deprecating Notion; D-107 on `main` is the Playtest Lab contract. And the Monster RPG Story Bible it reports as possibly unreachable is in this repository at `docs/story-bibles/monster-rpg.md` |

The branch is retained as a recoverable ref and its worktree removed. Nothing on
it should be merged.

## Changes made under this triage

- The stale `docs-bundles/` snapshots are deleted and the directory is now
  ignored. They were generated 2026-06-12, before the Couch Race and GDD
  pivots, and listed Notion exports in their manifests. The
  `arcwright-doc-bundler` skill regenerates them on demand and its own
  `SKILL.md` states bundles are snapshots and never source of truth. They
  carried no KB front matter, so they were never in the 449-document index,
  but any agent falling back to `Grep` could reach 21,337 lines of pre-pivot
  content and cite it as current.
- Both `Q-115` rows in `docs/product/open-questions-log.csv` said the Monster
  RPG Story Bible v0.9 draft lived in Notion. It is in this repository at
  `docs/story-bibles/monster-rpg.md`, status `draft`. The rows now say so. The
  questions stay open: v1.0 finalization still depends on Q-113 and Q-114.

## Standing rule

A generated artifact does not belong in version control unless something reads
it from there. Bundles, snapshots and indexes regenerate; a committed copy only
ages. Where one must be committed, the check that regenerates it belongs in CI
so drift fails loudly rather than being discovered a quarter later.
