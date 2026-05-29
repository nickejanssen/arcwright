# GitHub Tracker Alignment

This file is the operational companion to the roadmap. The GitHub Project, milestones, labels, and M1 Epic A issues already exist; this doc explains both how they stay aligned with the canonical roadmap in `docs/roadmap/` and how to rebuild them from the repo if needed.

## Ownership Split

- Roadmap Markdown files are the source of truth for scope and sequencing.
- `index.json` is the machine-readable join layer between roadmap IDs and live GitHub objects.
- GitHub Issues, milestones, and the project board are the execution surface for active work.

## Current Live References

- Repository: `nickejanssen/arcwright`
- Milestone `M1`: [milestone 1](https://github.com/nickejanssen/arcwright/milestone/1)
- Epic `M1-A`: [issue #1](https://github.com/nickejanssen/arcwright/issues/1)
- Task `AW-101`: [issue #2](https://github.com/nickejanssen/arcwright/issues/2)
- Task `AW-102`: [issue #3](https://github.com/nickejanssen/arcwright/issues/3)

## What The Repo Already Captures

- Issue creation shape lives in `.github/ISSUE_TEMPLATE/feature.md` and `.github/ISSUE_TEMPLATE/bug.md`
- PR review expectations live in `.github/pull_request_template.md`
- Canonical epic and task scope lives in `docs/roadmap/epics/` and `docs/roadmap/tasks/`
- Live GitHub cross-references live in `docs/roadmap/index.json`

## What Was Missing Before

Before this update, the repo did not contain a reproducible definition of labels, milestones, or project fields. That meant the live setup could be referenced, but not rebuilt cleanly from repo state alone.

The rebuild source now lives in:

- `.github/tracker/labels.json`
- `.github/tracker/milestones.json`
- `.github/tracker/project.json`
- `.github/tracker/README.md`

## Rebuild From Scratch

If the GitHub tracker had to be recreated:

1. Create the repository labels from `.github/tracker/labels.json`.
2. Create milestones from `.github/tracker/milestones.json`.
3. Create a table-style GitHub Project named `Arcwright Build`.
4. Recreate the project fields from `.github/tracker/project.json`.
5. Create the seed issues listed in `.github/tracker/project.json` using the roadmap files referenced by each `roadmap_path`.
6. Add those issues to the project and set their `Size`, `Status`, and `Epic` fields as appropriate.
7. Record any newly created GitHub numbers back into `docs/roadmap/index.json`.

This keeps the rebuild process deterministic without pretending that the live GitHub tracker is the source of truth.

## Cross-Reference Policy

- Keep canonical IDs like `M1-A` and `AW-101` in every GitHub epic or task title.
- Do not paste live issue numbers or URLs into every roadmap Markdown file.
- Store known live GitHub numbers and URLs in `docs/roadmap/index.json`.
- If a GitHub issue changes title, preserve the roadmap ID prefix so agents can still resolve it quickly.

## Working Pattern Going Forward

1. Write or update the roadmap Markdown file first.
2. Create or update the GitHub issue from that canonical file.
3. Add the GitHub issue number and URL to `docs/roadmap/index.json`.
4. Use the existing issue templates in `.github/ISSUE_TEMPLATE/` for issue body structure when creating net-new tracker items.
5. Use `.github/pull_request_template.md` so shipped work always links back to the relevant spec and notes which agents contributed.

## Why The Links Live In The Manifest

Issue numbers, milestone numbers, and project URLs are external execution details that can change independently of roadmap content. Keeping those cross-references in `index.json` makes them easy for agents to query without turning every roadmap file into a tracker mirror.
