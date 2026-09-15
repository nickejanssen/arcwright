# Setup — Arcwright

These steps are manual and one-time. Nothing here runs automatically.

## 1. Put the repo somewhere

```bash
git init
git add -A
git commit -m "chore: generated team-ai instance"
git branch -M main
git remote add origin <your-remote-url>
git push -u origin main
```

## 2. Mint MCP tokens per scope

Each surface people ask from gets its own token with its own scope. Do not
reuse one token across surfaces.

- `arc-execution` namespace access — mint a token scoped to read `arc-execution`.
- `knowledge-graph` namespace access — mint a token scoped to read `knowledge-graph`.
- `character-behavior` namespace access — mint a token scoped to read `character-behavior`.
- `model-routing` namespace access — mint a token scoped to read `model-routing`.
- `session-runtime` namespace access — mint a token scoped to read `session-runtime`.
- `safety` namespace access — mint a token scoped to read `safety`.
- `developer-api` namespace access — mint a token scoped to read `developer-api`.
- `nightcap` namespace access — mint a token scoped to read `nightcap`.
- `monster-rpg` namespace access — mint a token scoped to read `monster-rpg`.
- `daily-case` namespace access — mint a token scoped to read `daily-case`.
- `nightcap-couch-race` namespace access — mint a token scoped to read `nightcap-couch-race`.
- `product-roadmap` namespace access — mint a token scoped to read `product-roadmap`.
- `engineering-practice` namespace access — mint a token scoped to read `engineering-practice`.
- `playtest-ops` namespace access — mint a token scoped to read `playtest-ops`.

Record where each token lives (a secret manager, not this repo). The
`.gitignore` already excludes `.team-ai/` and `*.sqlite`.

## 3. Register the connector

This instance ships as a repo with no server. Coding clients read the repo
directly. Add a server later only when a second client or a non-repo audience
actually appears — the reasons are recorded in `docs/architecture.md`.

## 4. Fill in the golden eval set

`evals/golden/` is empty. Add real question files (see
`team-ai run-evals --help`) so `run-evals` has something to replay. Until
then the eval gate has no signal.

## 5. Seed or write the knowledge base

`kb/` has no starter documents. Add your first few before anyone relies on
search — an empty knowledge base returns nothing on day one.
