---
id: patterns.specs.0089-team-ai-agent-architecture
namespace: patterns
title: team-ai Agent Architecture for Arcwright
owner: Nico Janssen
status: active
review_by: "2027-03-12"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# team-ai Agent Architecture for Arcwright

**Status**: Approved (design) — revisions since approval pending founder confirmation

**Version**: 1.1 | **Last updated**: 2026-09-13 | **Canonical path**: `docs/specs/0089-team-ai-agent-architecture.md`

**Author**: Claude (with founder) | **Date**: 2026-09-13

---

# References

- Canonical agent rules: [`AGENTS.md`](../../AGENTS.md) — architecture principles 5 (knowledge graph), 6 (cost-aware), 8 (provider-agnostic routing)
- Architecture sections: [`docs/architecture/01`–`15`](../architecture/) — the source of the engine domain split
- Framework: [github.com/nickejanssen/team-ai](https://github.com/nickejanssen/team-ai) v0.3.1; framework design note `docs/design/2026-09-13-agent-topology-design.md`
- Prior work merged: PR #308 — `docs: backfill KB front matter via team-ai adopt`
- Related specs: [`0019-multi-agent-operating-model.md`](0019-multi-agent-operating-model.md), [`0021-operating-model-business-and-architect-roles.md`](0021-operating-model-business-and-architect-roles.md)
- Collaboration rules: [`docs/conventions/human-collaboration.md`](../conventions/human-collaboration.md)

---

# Overview

Defines the agent architecture that `team-ai` generates into Arcwright: a
three-tier orchestrator/SME topology, the YAML manifest describing every
relationship between agents, skills, domains and roles, a temporal knowledge
graph derived from git and front matter, and hybrid lexical+semantic retrieval.

`team-ai adopt` (PR #308) measured the repo and backfilled front matter. It does
not generate agents — that is this spec.

---

# In Scope

Delivered in three phases, each independently reviewable.

**Phase A — Agent layer and namespace migration**

- Extend `manifest.schema.json` with the fields the topology requires:
  `group`, `authority`, `not_owned`, `depends_on`, and the `agents` and
  `skills` sections. The schema must land before anything emits against it.
- Migrate all seven namespace values written by PR #308 to 14 Arcwright
  namespaces: 13 specialist domains plus the archived `nightcap-couch-race`
- Generate the three-tier agent topology (1 router, 3 group SMEs, 13 specialists)
- Generate per-agent instruction files and the four base skills
- Emit the `domains`, `agents`, and `skills` manifest sections

**Phase B — Enforcement skills, hooks, workflows, measurement**

- Three deterministic enforcement skills
- Four Claude Code hooks
- `workflows` manifest section with human approval gates
- Golden question set and routing-accuracy eval gate

**Phase C — Temporal graph and hybrid retrieval**

- Derived edge computation from git history and front matter
- Per-session observation files for edges that cannot be derived — never a
  shared append target
- Confidence decay, reinforcement, pruning
- Staleness propagation along edges
- Local embedding vectors in SQLite, fused with FTS5 via reciprocal rank fusion,
  with the search query embedded by the same model at query time

---

# Out of Scope

- Any change to `engine/`, `api/`, `sdk/`, or `dashboard/` runtime code. This
  spec concerns documentation, knowledge, and development-time agents only.
- Hosted embedding providers. The adapter interface permits one later; this
  spec builds only the local driver.
- A graph database. Edges are derived or recorded in per-session files;
  brute-force cosine over ~5,000 chunks is faster than a network hop to a
  vector service.
- Replacing the existing hand-authored role contracts in `docs/agents/` or the
  skills in `docs/skills/`. Those are mapped into the manifest, not rewritten.
- Retroactive rewriting of `docs/archive/notion-export/`.

---

# Human Collaboration Contract

**Interaction profiles:** Decision interview | Creative collaboration

**Classification rationale:** Domain boundaries and authority levels encode
founder judgement about how expertise actually divides and which sources are
canonical — neither is derivable from the repo. The namespace migration
rewrites `id` on every document with front matter (445 on `main` on
2026-09-13), which is irreversible in practice once other artifacts reference
the new ids.

**Required founder inputs:**

- Confirmation of the domain split and each domain's `authority` value
- Confirmation of proposed decisions D1–D3 (see below)
- Approval of the per-file namespace migration proposal before it runs
- Golden question set review — the questions define what "correct routing" means

**Phase gates:**

- Phase A: D1–D3 confirmed and the migration proposal approved before any `id`
  rewrite; generated agents reviewed before merge
- Phase B: golden questions approved before the eval gate is made blocking
- Phase C: decay parameters reviewed against real observed data before pruning
  is enabled; placement of the embedding model identifier decided before any
  model is pinned

**Review package:** Each phase ships a PR with the generated diff plus a
plain-language summary of what changed and what it means. Out-of-date or
deprecated items surface through an interactive approval form, not raw YAML.

**Approval evidence:**

- *Design approval.* The founder approved this spec on 2026-09-13 with the
  message "Approve spec", given against commit `f11398e` (version 1.0). That
  approval covers the design recorded at that commit: topology, manifest split,
  graph model, and retrieval approach.
- *Not covered by that approval.* Decisions D1–D3 (added in `2a606a5`) and the
  review revisions in version 1.1 were made after it. They are proposals pending
  founder confirmation.
- *Not an implementation authorization.* Design approval authorizes planning
  only. It does not authorize the namespace migration: the per-file migration
  proposal requires its own explicit founder approval, recorded in the Phase A
  PR, before `--apply` runs.

**Owner actions:** None external.

---

# Architecture

## Three-tier topology

```
TIER 1  sme (router)          model_tier: none   max_hops: 2
        Deterministic keyword→domain match against manifest.yaml.
        Zero model calls. Refuses when no domain owns the question.

TIER 2  engine-sme            model_tier: small  max_hops: 1
        title-sme             Cross-cutting questions spanning >1 specialist.
        practice-sme

TIER 3  Specialists           model_tier: small  max_hops: 0  (terminal)
        engine:   arc-execution · knowledge-graph · character-behavior
                  model-routing · session-runtime · safety · developer-api
        title:    nightcap (canonical) · monster-rpg · daily-case (provisional)
        practice: product-roadmap · engineering-practice · playtest-ops
```

Cost, context, and hallucination control are structural, not prompted:

| Mechanism | Guarantee |
|---|---|
| Router `model_tier: none` | Routing is free and cannot hallucinate a destination |
| Specialist `max_hops: 0` | No recursive fan-out — the main cost blowup in agent systems |
| One `kb_namespace` per specialist | Context bounded by construction |
| Router refuses on no match | No confident wrong answer when nothing owns it |
| `authority` field | A provisional source can never be cited as canon |

## Namespace migration

PR #308 wrote **seven** namespace values. Both `namespace` and `id` carry the
value (`id: platform.architecture.04-knowledge-graph`), so migration rewrites
both. Counts are from `main` on 2026-09-13:

| Current value | Docs | Found in | Migrates to |
|---|---|---|---|
| `operating` | 187 | `prd/`, `product/`, `roadmap/`, `agents/` | `product-roadmap` |
| `patterns` | 129 | `conventions/`, `design/`, `specs/` | `engineering-practice` |
| `playbooks` | 48 | `superpowers/` (47), `skills/` (1) | `engineering-practice`; playtest-related files → `playtest-ops` per file |
| `custom` | 38 | `gdd/` (33), `story-bibles/` (5) | `nightcap`; story bibles per file → `monster-rpg`, `daily-case`, `nightcap-couch-race` |
| `decisions` | 25 | `decisions/` | `product-roadmap`, which owns ADRs |
| `platform` | 17 | `architecture/` | per file across the seven engine domains, by section |
| `unmapped` | 1 | `docs/README.md` | `engineering-practice` — it holds documentation access, versioning, and AI-cost rules |

**Every current value has a default rule**, so no document can be left on an
old namespace. The one-to-many cases (`platform`, `playbooks`, and the story
bibles under `custom`) are expressed as per-file overrides. The complete
per-file proposal is generated and approved by the founder before anything is
written. Because the counts drift as docs are added, the migration verifies
against the live tree rather than these numbers.

## Manifest

`manifest.yaml` is generated by `assemble-manifest` from fragments. Four sections:

```yaml
domains:
  - id: knowledge-graph
    description: "Who knows what, when they learned it, and from whom."
    keywords: [knowledge state, knows, learned, epistemic]
    not_owned: [character personality, arc transitions]
    kb_namespace: knowledge-graph
    subagent: knowledge-graph-sme
    group: engine
    authority: canonical          # canonical | provisional | archived
    depends_on: [arc-execution, character-behavior]
    model_tier: small
    owner: Nico Janssen
    escalate_to: engine-sme

agents:
  - name: knowledge-graph-sme
    tier: 3
    kind: subagent
    group: engine
    max_hops: 0
    kb_namespaces: [knowledge-graph]
    skills: [kb-answer, kb-contribute]

skills:
  - id: provider-leak-check
    deterministic: true
    script: scripts/provider-leak-check
    used_by: [model-routing-sme]

workflows:
  - id: doc-currency-review
    steps:
      - script: freshness-audit
      - agent: practice-sme
      - gate: founder-approval
      - script: apply-approved
```

`not_owned` is anti-scope: declaring what a domain excludes sharpens routing,
because near-miss questions refuse rather than get absorbed.

## Deterministic enforcement skills

Each enforces a rule `AGENTS.md` already declares, with zero model calls:

| Skill | Enforces | Scope |
|---|---|---|
| `provider-leak-check` | No provider or model name outside `config/routing_table.json` and `engine/routing/router.py` | Runtime code and config: `engine/`, `api/`, `sdk/`, `dashboard/`, `config/`. Documentation is excluded — 44 docs on `main` legitimately describe providers and models, so a repo-wide scan could never pass on the clean tree |
| `scope-evidence-check` | Claimed product scope has durable approval in `docs/product/decisions-log.csv`, an ADR, or a spec | Specs and roadmap entries |
| `knowledge-query-guard` | Knowledge-state query precedes every AI character generation call | `engine/` |

## Hooks

| Hook | Action |
|---|---|
| `SessionStart` | Inject domain map + currently-stale docs — session-to-session carryover |
| `PreToolUse` (Write/Edit) | Block edits to generated files and agent-local dirs |
| `PostToolUse` (Write) | Record the session's observations in that session's own file under `graph/observations/` |
| `Stop` | Run `validate-graph`; report freshness delta |

## Temporal graph

**Derive, don't store.** A machine-rewritten edge file produces merge conflicts
on nearly every PR once more than one person contributes, and storing co-edit
edges duplicates git, which already is that graph.

| Edge type | Source | Storage |
|---|---|---|
| `co_edited` | `git log --name-only`, one batched traversal | none — derived |
| `declared`, `supersedes` | front matter `relations` | none — already there |
| `co_cited`, `co_retrieved` | agent answers, retrieval results | one new file per session |

**Observations are sharded per session**, at
`graph/observations/<YYYY-MM>/<session-id>.jsonl`. They are never appended to a
shared file: two branches that each append to the end of one shared file
produce an ordinary git conflict, which would recreate the problem this design
exists to avoid. A per-session file is only ever added, never edited, so two
branches can't conflict on it. `decay-sweep` reads every file. Any compaction it
does produces a derived cache that isn't committed.

Each edge carries `weight`, `first_observed`, `last_observed`, `confidence`,
`source`. Four deterministic rules: confidence decays exponentially with time
since last observation; new observations reinforce weight and reset the clock;
edges below a confidence floor are pruned; authored edges never decay.

**What the graph is for:**

1. **Staleness propagation** — when a doc changes, high-confidence neighbours
   become suspect and their `review_by` pulls in. Arithmetic, not judgement.
2. **Gap detection** — high query volume against thin or weakly-connected
   domains surfaces as a knowledge gap.
3. **Retrieval boost** — strong neighbours of a top hit gain a small score bonus.
4. **Routing hints** — persistent strong cross-edges indicate a tier-2 group SME
   should take the question rather than one specialist.

The graph cannot cause hallucinations — every edge is observed or declared,
never model-inferred. It also does not eliminate them; that is the job of the
four structural constraints in the topology table.

## Retrieval

Hybrid: existing FTS5 lexical plus local semantic vectors, merged by reciprocal
rank fusion.

- **Model:** a small local sentence-embedding model — CPU only, on the order of
  384 dimensions and ~100MB on disk. The concrete model is chosen in the
  Phase C design. Where its identifier lives is an open decision, because
  `AGENTS.md` forbids model strings outside the two routing files (see Open
  Questions). This spec deliberately names no model.
- **Storage:** vectors as BLOBs in the existing SQLite index — ~7.7MB for a
  ~5,000-chunk corpus at 384 dimensions.
- **Search:** brute-force cosine. ~2M FLOPs per query, sub-millisecond in JS,
  and faster than a network hop to a vector service at this scale.
- No vector database, no service to run, no API key, no per-query spend.
- Behind the existing `RetrievalAdapter` interface, so a hosted driver can be
  added later without touching callers.

**The model runs at two points, not one.** Every chunk is embedded at index
time. **Every search query must also be embedded, at query time**, into the
same vector space before cosine similarity can run. Precomputed document vectors
alone cannot serve a query nobody has seen before. The query path is specified
as:

1. **Load lazily, keep warm.** The model loads on the first semantic query in a
   process and stays loaded; it is never reloaded per query.
2. **Embed the query.** A single short input. Expected latency is low tens of
   milliseconds on CPU; this is an estimate to be measured, not a guarantee.
3. **Cache.** Query vectors are cached keyed by normalized query text plus model
   version, so repeated questions skip inference.
4. **Fall back, don't fail.** If the model fails to load or exceeds a timeout,
   the search returns lexical-only results and reports that it fell back.

Semantic retrieval is the only place team-ai calls a model — at index time and
at query time, both locally. Revisit past roughly 100k chunks (~20× current
corpus).

---

# Acceptance Criteria

**Phase A**

- [ ] Founder has confirmed D1–D3 before any agent is generated
- [ ] Migration proposal lists every `id`/`namespace` change and is explicitly approved by the founder before any write
- [ ] After migration, `team-ai validate-kb` passes and `git grep -h '^namespace:' -- docs` reports only the 14 target namespaces — none of the seven prior values (`operating`, `patterns`, `playbooks`, `custom`, `decisions`, `platform`, `unmapped`) survives
- [ ] 17 agent definitions generated, each validating against `agent.schema.json`
- [ ] Every specialist has `max_hops: 0` and exactly one `kb_namespace`
- [ ] Router has `model_tier: none`
- [ ] `nightcap` domain is `authority: canonical`; `monster-rpg` and `daily-case` are `authority: provisional`; `nightcap-couch-race` is `authority: archived`
- [ ] No file outside `docs/` and `.claude/` is modified

**Phase B**

- [ ] `manifest.yaml` validates against the extended schema with all four sections
- [ ] `provider-leak-check` fails on a provider string planted in runtime code outside the two allowed files, and passes on the clean tree
- [ ] `scope-evidence-check` fails for scope with no decision record and passes with one
- [ ] `knowledge-query-guard` fails on a generation call with no preceding knowledge query
- [ ] All four hooks fire and are individually disableable
- [ ] Golden set of ≥ 30 real questions with known-correct domains; routing accuracy reported as a number
- [ ] `doc-currency-review` workflow runs end to end and pauses at the approval gate

**Phase C**

- [ ] Co-edit edges derived from git match a hand-verified sample
- [ ] Decay reduces an unobserved edge's confidence over simulated time; authored edges unchanged
- [ ] Staleness propagation pulls in `review_by` for high-confidence neighbours of a changed doc
- [ ] Two branches that each record observations merge without conflict
- [ ] Semantic retrieval answers a semantically-phrased query that lexical search misses
- [ ] Query embedding latency is measured and reported at p50 and p95
- [ ] With the model unavailable, search returns lexical-only results and reports the fallback
- [ ] Hybrid retrieval scores ≥ lexical-only on the golden set
- [ ] Full index rebuild completes in < 60s on the current corpus

---

# Test Plan

- **Unit**: namespace migration mapping, including a default rule for each of
  the seven prior values; manifest schema validation; each enforcement skill
  against planted violations and clean trees; decay, reinforcement, and pruning
  arithmetic; RRF fusion ordering; query-vector cache keying
- **Integration**: generate the full instance into a temp copy of Arcwright and
  assert the repo is otherwise untouched (extends team-ai's existing dogfood
  test); run each workflow end to end including gate pause; merge two branches
  that both recorded observations
- **Eval**: golden question set through the router — routing accuracy, refusal
  rate, citation validity; hybrid vs lexical-only compared on identical inputs;
  query embedding latency and the lexical fallback path
- **Manual**: founder reviews the migration proposal and the generated agent
  instructions before either is applied

---

# Risks and Unknowns

**Risks**

- **`id` rewrite is effectively irreversible.** `id` embeds the namespace, so
  migration changes the id of every document with front matter. Anything
  referencing an old id breaks. Mitigation: `validate-citations` runs before and
  after; migration is one reviewed commit.
- **Refusal rate may frustrate.** Keyword routing refuses unusual phrasings.
  Mitigation: golden set measures it; `not_owned` and keyword tuning are cheap
  to iterate; semantic retrieval in Phase C reduces it.
- **17 agents is real maintenance surface** for a solo founder. Mitigation:
  generated from templates, so a domain change is a fragment edit plus a
  re-render, not hand editing 17 files.
- **Local embedding model adds a sizeable dependency** with native build
  implications on some platforms, and adds per-query CPU work. Mitigation:
  queries fall back to lexical retrieval automatically when the model is
  unavailable or slow.
- **Breaks team-ai's zero-model-call rule.** Narrowed to a local model at index
  and query time, but the invariant is genuinely weakened and must be recorded
  as an explicit decision in team-ai's design of record rather than quietly
  dropped.

**Unknowns**

- Whether 13 domains is the right granularity in daily use, or whether some
  specialists are too thin to justify their own agent. The golden set will show
  which domains never get routed to.
- Real decay half-life. Parameters are guesses until there is observed data;
  pruning stays disabled until they are reviewed.
- Whether `docs/playtests/` (currently empty) warrants its own domain or folds
  into `playtest-ops` backed by the existing skills.
- Which `design/` and `specs/` documents describe a single title or playtest
  operations closely enough to warrant per-file overrides away from the
  `engineering-practice` default. Settled during review of the migration
  proposal.

---

# Open Questions

- **Q1 — Where does the embedding model identifier live?** `AGENTS.md` states
  that no provider name or model string may appear outside
  `config/routing_table.json` and `engine/routing/router.py`. Retrieval is
  development-time tooling rather than an engine operation, but a model id in a
  generated `index.lock` would still sit in this repository. Options: add an
  embedding task type to `config/routing_table.json`, or record an explicit,
  narrow exemption for retrieval index configuration in an ADR. Must be decided
  before Phase C pins a model.

---

# Proposed Decisions (pending founder confirmation)

These were written by Claude after the founder approved version 1.0. They have
not been individually confirmed and do not carry that approval. Confirmation is
a Phase A gate.

**D1 — Existing agents and skills are registered, never regenerated.**
The hand-authored contracts in `docs/agents/` and skills in `docs/skills/` are
entered into the manifest as `source: authored` entries and referenced by the
topology. Generation never writes to their paths. Rationale: the standing
requirement is that an existing SME is reused without loss of information rather
than replaced, and team-ai's renderer already treats a hand-authored file as a
collision it must not clobber. Registering them makes them routable; leaving
them unregistered would mean the router cannot reach work that already exists.

**D2 — `nightcap-couch-race` gets an `authority: archived` domain.**
A question about Couch Race routes somewhere that answers "this is archived,
superseded by X" rather than refusing. Rationale: the file already self-declares
archived status, so the information exists and is useful; a bare refusal would
be strictly less helpful and would register as a coverage gap in the eval set.
Cost is one manifest entry and no new agent — archived domains route to
`title-sme` rather than to a dedicated specialist.

**D3 — The founder is `owner` on every domain until the team grows.**
Rationale: `unassigned` propagates into generated front matter and makes
ownership and freshness reporting meaningless, and PR #308 already wrote
`owner: Nico Janssen` across the corpus — so this is consistency with what is
already on `main`. Revisit when there are other named owners.

All three are low-cost to reverse: D1 and D2 are manifest entries, D3 is a
single generation parameter.
