# Local Setup

## Pre-Commit Hooks

Arcwright uses `pre-commit` for repo-wide local hooks because the repo mixes Python and TypeScript.

Install the repo's JS/TS tooling dependencies at the repo root:

```bash
npm install
```

Install the hook runner:

```bash
pip install pre-commit
```

Install the Git hooks in your local clone:

```bash
pre-commit install
```

Run the full hook suite manually before a PR if you want an early check:

```bash
pre-commit run --all-files
```

The configured hooks are check-only. They fail loudly for formatting, lint, secrets, and temporary debug markers, but they do not rewrite files during commit. The JS/TS hooks use the repo-root `node_modules`, so rerun `npm install` if those tool dependencies are missing.
