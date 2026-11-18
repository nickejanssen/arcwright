# Arcwright — AI capability

This directory holds Arcwright's agent definitions, manifest, skills and evals.
The knowledge base is the Markdown under `../docs/`, subject to the root and
exclusions in `index.lock`. See `../docs/README.md` for source authority and
`../docs/conventions/knowledge-base-upkeep.md` for maintenance.

| Path | Purpose |
|---|---|
| `runtime/` | Arcwright-owned knowledge CLI source and its dependencies. |
| `agents/` | Domain specialist definitions and manifest fragment. |
| `manifest.yaml` | Generated domain and agent manifest. |
| `skills/` | Instance skills and routing procedures. |
| `evals/golden/` | Committed evaluation questions. |
| `evals/gates.yaml` | Existing evaluation thresholds. |
| `index.lock` | Retrieval configuration and knowledge-base scope. |

The CLI source is maintained in `runtime/`. Follow `SETUP.md` to build it;
`runtime/ARCWRIGHT.md` records its origin and compatibility scope.

For a standalone `AW-NNN` search, the CLI may identify the indexed task record
using the roadmap index. A `canonical-roadmap-id` match identifies the record;
it does not establish that the local index is fresh or that the task is open.
GitHub owns task status. Rebuild the index as described in `SETUP.md`.
