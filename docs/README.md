# Arcwright Documentation

This directory is the canonical documentation workspace for Arcwright. It separates active source-of-truth docs from raw exports and historical context.

## Canonical Reading Order

For product or architecture work:

1. [prd/](prd/)
2. [architecture/](architecture/)
3. **Experience authority:** for Nightcap use [gdd/nightcap/](gdd/nightcap/); for other experiences use the current authority identified by [story-bibles/README.md](story-bibles/README.md)
4. [roadmap/](roadmap/)
5. [specs/](specs/)
6. [decisions/](decisions/)
7. [product/](product/)

For Nightcap design work, begin with `docs/gdd/nightcap/README.md` and its required read order. Do **not** use the archived Nightcap Story Bibles as current canon.

For implementation tasks, start with the relevant spec in [specs/](specs/), then read the referenced PRD and architecture sections plus the current experience authority before changing code. If an older implementation spec conflicts with the current Nightcap GDD, record and reconcile the implementation gap rather than assuming the old spec still defines product intent.

## Versioning Policy

Canonical documentation uses stable filenames. Do not create a new active file for each version. Record version changes inside the file header and rely on git history for prior versions.

Use this pattern for active docs:

```
> Current version: vX.Y
> Last updated: YYYY-MM-DD
> Status: Current
> Canonical path: docs/path/to/file.md
```

Archived source exports and superseded design artifacts may retain versioned or historical filenames. They are traceability artifacts, not active docs.

## Folder Map

- [prd/](prd/): Canonical split Product Requirements Document sections
- [architecture/](architecture/): Canonical split Technical Architecture sections
- [gdd/](gdd/): Current Game Design Documents; `gdd/nightcap/` is the Nightcap design source of truth
- [story-bibles/](story-bibles/): Current story bibles for experiences still using that authority model, plus compatibility redirects for archived Nightcap bibles
- [roadmap/](roadmap/): Milestones, epics, tasks, and the roadmap manifest
- [specs/](specs/): Approved task and feature specifications
- [decisions/](decisions/): Architecture and durable decision records
- [product/](product/): Product decision logs, open-question logs, and related product records
- [conventions/](conventions/): Coding, testing, AI contribution, and cost policies
- [agents/](agents/): Development-role contracts
- [skills/](skills/): Reusable role skills
- [archive/nightcap-story-bibles/](archive/nightcap-story-bibles/): Former Nightcap Story Bible authorities retained for provenance
- [archive/notion-export/](archive/notion-export/): Raw Notion exports and historical workspace artifacts

## AI Cost And Context Rules

- Read [README.md](README.md) first for documentation routing, then read only the smallest canonical files needed for the task.
- Prefer canonical current docs over archived exports or superseded design documents. Do not compare archived versions by default.
- For Nightcap, use `gdd/nightcap/00-governance/00-decision-ledger.md` before older product/design records when resolving current gameplay intent.
- Use archive material only when canonical docs are silent, a source-recovery question requires it, or a conflict must be investigated.
- Do not manually maintain duplicate mirrors such as `_all.csv` unless the task is explicitly about import reconciliation.
- For roadmap work, use [roadmap/index.json](roadmap/index.json) to locate the relevant milestone, epic, or task instead of scanning all roadmap files.
- For product context, read the relevant PRD section, current experience authority, and product/ADR record rather than loading full exports.

## Editing Rules

- Read relevant PRD and architecture files before writing new docs or code.
- Prefer updating canonical split docs over editing raw exports.
- Keep active docs at stable paths and update in-file version metadata instead of creating versioned duplicate files.
- Preserve archived artifacts unless the task explicitly requires moving or indexing them.
- Do not delete historical artifacts during cleanup. Move, index, and document them.
- Do not hardcode secrets, API keys, model names, or provider strings in docs.
- Use conventional commit format for commits.

## Source of Truth

Canonical repo docs win over archived exports. For Nightcap game design, the current Master GDD at `docs/gdd/nightcap/` supersedes the former Nightcap Story Bibles. Historical ADRs and product decisions remain valid as records of what was decided at the time, but they do not override a later explicit GDD decision when defining current Nightcap gameplay intent.

A GDD migration does not silently change architecture or deployed code. If current implementation/spec behavior differs from the current GDD, reconcile it explicitly through the appropriate spec/ADR/roadmap workflow.

Product-scope commitments need durable approval evidence before they become build scope. Use product decision records and add an ADR or approved spec when a decision affects roadmap, architecture, privacy, APIs, or implementation sequencing.
