# Build Roadmap

This directory is the canonical home for Arcwright's execution roadmap.

## Why This Structure Exists

The original roadmap was written as one long planning document. That is useful for human review, but inefficient for AI agents that are usually handed one task, one epic, or one milestone at a time.

This split structure keeps Markdown as the human-editable source of truth while making milestones, epics, and task specs directly addressable.

## Canonical Rules

- Markdown files in this directory are the canonical roadmap source of truth.
- `index.json` is a lookup manifest for agents and scripts. It should match the Markdown files, but it is not authoritative over them.
- If a split file and the architecture or PRD disagree, the architecture or PRD wins. Update the roadmap file.

## GitHub Relationship

- The roadmap in `docs/roadmap/` is the canonical planning source.
- GitHub milestones, issues, and the live project are the execution mirror for work in flight.
- Stable roadmap IDs such as `M1`, `M1-A`, and `AW-101` are the join key between docs and GitHub.
- Live GitHub numbers and URLs should live in `index.json`, not be repeated throughout every Markdown task file.
- If a GitHub issue title and a roadmap ID ever diverge, fix the GitHub title to include the roadmap ID rather than inventing a second identifier.

## Recommended Reading Order

For a human orienting to the build:

1. [00-overview.md](./00-overview.md)
2. The relevant milestone file under [milestones/](./milestones/)
3. The relevant epic file under [epics/](./epics/)
4. The specific task file under [tasks/](./tasks/)

For an AI agent handed a task ID:

1. Open [index.json](./index.json) and locate the task by `id`
2. Read the task file path listed there
3. Read the parent epic and milestone if the task depends on broader context
4. Read the referenced architecture and PRD sections from `docs/architecture/` and `docs/prd/`

For an AI agent handed a GitHub issue number or URL:

1. Read the issue title and extract the roadmap ID such as `AW-101` or `M1-A`
2. Open [index.json](./index.json) and locate that roadmap ID
3. Use the manifest path to open the canonical roadmap file
4. Treat the GitHub issue as execution status and discussion, not the source of truth for scope

## Directory Layout

- `00-overview.md`: roadmap-wide usage, milestone map, decomposition policy, and override notes
- `milestones/`: one file per milestone
- `epics/`: one file per epic
- `tasks/`: one file per agent-sized task spec
- `operations/`: supporting operational docs, such as GitHub project setup and roadmap maintenance notes
- `index.json`: machine-readable manifest for lookup by ID, dependency, and file path

## Maintenance Guidance

- When a future roadmap revision adds or changes tasks, update the split Markdown files first.
- After the Markdown updates, update `index.json` so agents can still locate the right file quickly.
- When a live GitHub issue or milestone is created for a roadmap item, add the cross-reference in `index.json` rather than editing every Markdown file.
- M2 through M6 are decomposed into agent-sized task files as of AW-201. M4 implementation tasks remain explicitly gated by AW-202 until the external Nightcap platform decision is complete.
