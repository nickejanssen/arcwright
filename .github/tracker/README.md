# GitHub Tracker Config

This directory captures the intended GitHub tracker state for Arcwright in repo-owned files.

## What Lives Here

- `labels.json`: repository labels that the workflow relies on
- `milestones.json`: milestone titles and descriptions derived from the roadmap
- `project.json`: GitHub Project metadata, fields, and the initial issue set to seed into the tracker

## What Does Not Live Here

- Issue bodies for roadmap work items. Those stay in `docs/roadmap/epics/` and `docs/roadmap/tasks/`.
- PR review rules. Those live in templates and workflows under `.github/`.

## Rebuild Principle

Use these files together with `docs/roadmap/index.json` and `docs/roadmap/operations/github-project-setup.md` to recreate the tracker if GitHub state ever needs to be rebuilt from scratch.
