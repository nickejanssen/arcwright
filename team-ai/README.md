# Arcwright — AI capability

This directory holds Arcwright's agent definitions, manifest, skills and evals.
The knowledge base is the Markdown under `../docs/`, subject to the root and
exclusions in `index.lock`. See `../docs/README.md` for source authority and
`../docs/conventions/knowledge-base-upkeep.md` for maintenance.

| Path | Purpose |
|---|---|
| `agents/` | Domain specialist definitions and manifest fragment. |
| `manifest.yaml` | Generated domain and agent manifest. |
| `skills/` | Instance skills and routing procedures. |
| `evals/golden/` | Committed evaluation questions. |
| `evals/gates.yaml` | Existing evaluation thresholds. |
| `index.lock` | Retrieval configuration and knowledge-base scope. |

The current CLI is built from the separate team-ai repository. The approved
migration in `../docs/superpowers/plans/2026-11-17-ai-development-infrastructure.md`
aims to remove that runtime dependency; until it lands, follow `SETUP.md`.
