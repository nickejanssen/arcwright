# Agent Topology Support — Design Note

**Date:** 2026-09-13
**Status:** Approved, pending implementation (target release 0.4.0)
**Companions:** [`2026-08-30-team-ai-framework-design.md`](2026-08-30-team-ai-framework-design.md), [`../architecture.md`](../architecture.md)

---

## 1. Why

The generator can describe a team with a handful of broad domains. It can't yet
describe a team whose expertise divides into many narrow domains, each needing
its own tightly scoped agent. Running it against a real repo with a dozen
distinct expertise areas surfaced four gaps:

1. **Every domain SME got the same namespace.** `renderEntityFiles` scopes each
   generated domain subagent to `namespaces[0]`. With N domains you get N agents
   all reading one namespace, so the per-agent context bound that `max_hops: 0`
   and single-namespace scoping are meant to give doesn't exist.
2. **A repo can't bring its own namespace preset.** `resolveCatalog` supports
   toolkit → org → instance layers, but `loadCatalog()` only wires the toolkit
   layer. `kb.catalog_override: org-catalog-repo` is recorded into the profile
   and consumed by nothing. On top of that, `kb.namespaces` is a `single_select`
   that throws on any value outside its options, so `custom` is the only answer
   that could name a repo-supplied preset, and today it resolves to nothing and
   silently falls back to the five defaults.
3. **The manifest is flat.** It lists domains but can't express which tier an
   agent sits in, what a domain explicitly does *not* own, which domains depend
   on which, or whether a source is canonical or a placeholder.
4. **There's no way to change namespaces after adoption.** `adopt` writes
   namespace values into front matter, and `id` embeds the namespace. Once
   written there's no tool to migrate them, so an early namespace choice is
   effectively permanent.

## 2. Changes

All of this is deterministic, with zero model calls. The framework's founding
invariant is unchanged by this release.

### 2.1 Domain fields (optional, back-compatible)

| Field | Type | Purpose |
|---|---|---|
| `group` | string | The tier-2 parent that handles questions spanning several narrow domains |
| `authority` | `canonical` \| `provisional` \| `archived` | Lets a placeholder source be declared as one in data, so it can never be cited as canon. This doesn't rely on a prompt remembering |
| `not_owned` | string[] | Anti-scope. Declaring what a domain excludes sharpens routing: near-miss questions get refused instead of absorbed |
| `depends_on` | string[] | Domain → domain edges, so a question genuinely spanning two domains can pull both contexts |

Omitting all four is valid, so existing manifests and spokes keep validating.

### 2.2 `agents` and `skills` manifest sections (optional)

`agents` records each agent's `tier` (1–3), `kind`, `group`, `max_hops`,
`kb_namespaces`, `skills`, `escalate_to`, and `source`. `skills` records `id`,
`deterministic`, `script`, `used_by`, `path`, and `source`.

`source: authored` marks agents and skills that existed before generation. They
get registered so the router can reach them, and they're never regenerated. The
renderer already refuses to clobber hand-authored files. This makes that work
routable instead of invisible.

### 2.3 Per-domain namespace

`buildContext` emits `domains[].namespace`. A domain whose slug matches a
namespace name owns that namespace. Otherwise it falls back to `namespaces[0]`,
so presets whose namespaces aren't per-domain behave exactly as before.

### 2.4 Instance catalog layer

`loadCatalog(instanceDir?)` passes an instance directory through to
`resolveCatalog`. Entries are keyed by **filename stem**, so a repo that
supplies `catalog/namespaces/custom.yaml` makes the existing `custom` answer to
`kb.namespaces` resolve to its own preset. There are no question-bank or engine
changes, and a missing directory is ignored.

### 2.5 `team-ai remap-namespaces`

This rewrites `namespace` and the first segment of `id` across a KB, driven by a
mapping file:

```yaml
namespaces:          # one-to-one rules
  old-ns: new-ns
files:               # per-file overrides — how one-to-many splits are expressed
  docs/some/file.md: other-ns
```

- **Proposal by default.** Without `--apply` it writes only the proposal, so
  every doc stays byte-identical.
- **Surgical.** It rewrites just the two scalar lines inside the front-matter
  block. Key order, quoting, comments, line endings, and the body are untouched.
- **Safe.** Unmapped namespaces are reported `unchanged`. Unparseable front
  matter is a `conflict`, not a crash, and a second run is a no-op.

A one-to-many split is a human judgement, which is why it lives in `files`
rather than being inferred.

## 3. The pattern this enables

The schema now supports a three-tier topology without prescribing it:

| Tier | Role | Typical settings | What it guarantees |
|---|---|---|---|
| 1 | Router | `model_tier: none`, `max_hops: 2` | Routing is free and can't hallucinate a destination. It refuses when nothing owns the question |
| 2 | Group SME | `model_tier: small`, `max_hops: 1` | Cross-cutting questions within a group |
| 3 | Specialist | `model_tier: small`, `max_hops: 0`, one namespace | Terminal: no fan-out, context bounded by construction |

A small team can keep using one tier with a few broad domains. Nothing here
forces the pattern.

## 4. Not in this release

These are designed but out of scope, and each will get its own design note
before implementation:

- **Hooks and workflows.** Session-start context injection, guards on generated
  files, and a `workflows` manifest section mixing scripts, agents, and human
  approval gates.
- **Temporal graph.** Edges derived from git history and front matter rather than
  stored (co-edit and supersedes), plus an append-only log for co-citation, with
  decay and staleness propagation.
- **Semantic retrieval.** A local embedding driver behind `RetrievalAdapter`,
  fused with lexical results. This **would** add a model call, at index time
  only. It needs an explicit decision recorded against §1 of the framework
  design before it ships.

## 5. First adopter

The first instance using these changes is specified in
[arcwright `docs/specs/0089-team-ai-agent-architecture.md`](https://github.com/nickejanssen/arcwright/blob/main/docs/specs/0089-team-ai-agent-architecture.md),
with its implementation plan alongside. That repo carries the instance-specific
content: its domains, its namespace mapping, and its authority decisions. None
of that content belongs here.
