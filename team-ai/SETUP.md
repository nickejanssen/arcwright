# Setup — Arcwright

Use an existing Arcwright checkout. Read `../AGENTS.md`, `../HANDOVER.md`
and `../docs/conventions/knowledge-base-upkeep.md` first.

The runtime lives in `runtime/` and is built from the main Arcwright checkout
with Node 22 or later. From the main checkout, run:

```bash
cd team-ai/runtime
npm ci
npm run build
```

A linked worktree uses the built runtime from the main checkout, while its
index remains local to that worktree. `TEAM_AI_CLI` can explicitly select
another built CLI; only use a path you trust. See `runtime/ARCWRIGHT.md`
for the snapshot provenance and maintenance boundaries.

From the Arcwright checkout root:

```bash
python scripts/team_ai_cli.py validate-kb --instance team-ai
python scripts/team_ai_cli.py validate-manifest --root team-ai
python scripts/team_ai_cli.py reindex --root team-ai
python scripts/team_ai_cli.py run-evals --root team-ai
python scripts/team_ai_cli.py freshness-audit --instance team-ai
```

The index is local to the checkout. Rebuild it after pulling changes before
relying on ranked search. The committed golden questions are in
`team-ai/evals/golden/`; the knowledge-base root and exclusions are in
`team-ai/index.lock`. Existing eval thresholds and their limits are documented
in the infrastructure plan and knowledge-base upkeep guide.

This instance has no server registered by these steps. Namespace access for
coding clients is governed by the existing agent instructions and hooks.
