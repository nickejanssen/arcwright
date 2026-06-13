# Arcwright Documentation

This directory is the canonical documentation workspace for Arcwright. It separates active source-of-truth docs from raw Notion exports and historical context.

## Canonical Reading Order

For product or architecture work:

1. [prd/](prd/)
2. [architecture/](architecture/)
3. [story-bibles/](story-bibles/)
4. [roadmap/](roadmap/)
5. [specs/](specs/)
6. [decisions/](decisions/)
7. [product/](product/)

For implementation tasks, start with the relevant spec in [specs/](specs/), then read the referenced PRD and architecture sections before changing code.

## Versioning Policy

Canonical documentation uses stable filenames. Do not create a new active file for each version. Record version changes inside the file header and rely on git history for prior versions.

Use this pattern for active docs:

```
> Current version: vX.Y
> Last updated: YYYY-MM-DD
> Status: Current
> Canonical path: docs/path/to/file.md
```

Archived source exports may retain versioned or hash-based filenames. They are traceability artifacts, not active docs.

## Folder Map

- [prd/](prd/): Canonical split Product Requirements Document sections
- [architecture/](architecture/): Canonical split Technical Architecture sections
- [story-bibles/](story-bibles/): Canonical game and experience story bibles
- [roadmap/](roadmap/): Milestones, epics, tasks, and the roadmap manifest
- [specs/](specs/): Approved task and feature specifications
- [decisions/](decisions/): Architecture Decision Records
- [product/](product/): Product decision logs, open-question logs, and related product records
- [conventions/](conventions/): Coding, testing, AI contribution, and cost policies
- [agents/](agents/): Development-role contracts
- [skills/](skills/): Reusable role skills
- [archive/notion-export/](archive/notion-export/): Raw Notion exports and historical workspace artifacts

## AI Cost And Context Rules

- Read [README.md](README.md) first for documentation routing, then read only the smallest canonical files needed for the task.
- Prefer canonical current docs over archived exports. Do not compare archived versions by default.
- Use [archive/notion-export/](archive/notion-export/) only when canonical docs are silent, a source-recovery question requires it, or a conflict must be investigated.
- Do not manually maintain duplicate mirrors such as `_all.csv` unless the task is explicitly about import reconciliation.
- For roadmap work, use [roadmap/index.json](roadmap/index.json) to locate the relevant milestone, epic, or task instead of scanning all roadmap files.
- For product context, read the relevant PRD section, story bible section, and product log entry rather than loading full exports.

## Editing Rules

- Read relevant PRD and architecture files before writing new docs or code.
- Prefer updating canonical split docs over editing raw exports.
- Keep active docs at stable paths and update in-file version metadata instead of creating versioned duplicate files.
- Preserve archived Notion exports unless the task explicitly requires moving or indexing them.
- Do not delete historical artifacts during cleanup. Move, index, and document them.
- Do not hardcode secrets, API keys, model names, or provider strings in docs.
- Use conventional commit format for commits.

## Source of Truth

Canonical repo docs win over archived exports. Archived exports exist for traceability and recovery. If a raw export conflicts with the split PRD, split architecture, roadmap, or accepted ADRs, update the canonical doc and record the reason in a spec or ADR when the decision has lasting impact.
