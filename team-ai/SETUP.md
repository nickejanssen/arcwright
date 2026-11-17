# Setup — Arcwright

Use an existing Arcwright checkout. Read `../AGENTS.md`, `../HANDOVER.md`
and `../docs/conventions/knowledge-base-upkeep.md` first.

The current CI and specialist search rely on the team-ai CLI. Until the
Arcwright-owned replacement is implemented, clone the framework beside the
main Arcwright checkout, check out the version pinned in
`../.github/workflows/team-ai.yml`, and run `npm ci` and `npm run build`
there with Node 22 or later. A worktree resolves the sibling relative to its
main checkout. To use another built CLI, set `TEAM_AI_CLI` to its
`dist/cli.js` path.

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
