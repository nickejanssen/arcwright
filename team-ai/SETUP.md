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

The index is local to the checkout. Search verifies indexed Markdown contents,
paths, effective `index.lock`, and the tracked indexer/parser/chunker code and
schema against the last successful rebuild. An old, changed, or unverifiable
index is refused rather than searched silently. Run the reindex command above
once in each checkout after this update and again when search reports a stale
index. If an index is corrupt, stop processes using it, remove that checkout's
rebuildable `team-ai/.team-ai/index.sqlite` and SQLite sidecars, then reindex.
The wrapper supplies a plain-search fallback when ranked search is unavailable.
Excluded documents do not require a rebuild; the roadmap ID map is read live.

The fingerprint is a local drift check, not a tamper-proof attestation. It
tracks an audited list of runtime modules and `package-lock.json`, but does not
prove installed dependencies match the lock or automatically discover future
transitive imports. During rebuild, a source can change after the fingerprint check but before the
database transaction commits. This can leave an immediately stale index; the
next search checks the current corpus against that index and refuses mismatches.
This is accepted for a local, rebuildable cache, not as an atomic filesystem
snapshot: a change after a search’s final check or a change-and-revert between
checks may escape detection. Maintain the
module list when indexing dependencies change and use source authority checks
for consequential decisions. The committed golden questions are in
`team-ai/evals/golden/`; the knowledge-base root and exclusions are in
`team-ai/index.lock`. Existing eval thresholds and their limits are documented
in the infrastructure plan and knowledge-base upkeep guide.

This instance has no server registered by these steps. Namespace access for
coding clients is governed by the existing agent instructions and hooks.
