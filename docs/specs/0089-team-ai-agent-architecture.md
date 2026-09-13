# team-ai Agent Architecture for Arcwright

**Status**: Draft

**Author**: Claude (with founder) | **Date**: 2026-09-13

---

# References

- Canonical agent rules: [`AGENTS.md`](../../AGENTS.md) — architecture principles 5 (knowledge graph), 6 (cost-aware), 8 (provider-agnostic routing)
- Architecture sections: [`docs/architecture/01`–`15`](../architecture/) — the source of the engine domain split
- Framework: [github.com/nickejanssen/team-ai](https://github.com/nickejanssen/team-ai) v0.3.1
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
- Migrate the 5 generic namespaces merged in PR #308 to 13 Arcwright domains
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
- JSONL observation log for edges that cannot be derived
- Confidence decay, reinforcement, pruning
- Staleness propagation along edges
- Local MiniLM vectors in SQLite, fused with FTS5 via reciprocal rank fusion

---

# Out of Scope

- Any change to `engine/`, `api/`, `sdk/`, or `dashboard/` runtime code. This
  spec concerns documentation, knowledge, and development-time agents only.
- Hosted embedding providers. The adapter interface permits one later; this
  spec builds only the local driver.
- A graph database. Edges are derived or appended; brute-force cosine over
  ~5,000 chunks is faster than a network hop to a vector service.
- Replacing the existing hand-authored role contracts in `docs/agents/` or the
  skills in `docs/skills/`. Those are mapped into the manifest, not rewritten.
- Retroactive rewriting of `docs/archive/notion-export/`.

---

# Human Collaboration Contract

**Interaction profiles:** Decision interview | Creative collaboration

**Classification rationale:** Domain boundaries and authority levels encode
founder judgement about how expertise actually divides and which sources are
canonical — neither is derivable from the repo. The namespace migration
rewrites `id` on 459 files, which is irreversible in practice once referenced.

**Required founder inputs:**

- Confirmation of the 13-domain split and each domain's `authority` value
- Approval of the namespace migration mapping before it runs
- Golden question set review — the questions define what "correct routing" means

**Phase gates:**

- Phase A: migration mapping approved before any `id` rewrite; generated agents
  reviewed before merge
- Phase B: golden questions approved before the eval gate is made blocking
- Phase C: decay parameters reviewed against real observed data before pruning
  is enabled

**Review package:** Each phase ships a PR with the generated diff plus a
plain-language summary of what changed and what it means. Out-of-date or
deprecated items surface through an interactive approval form, not raw YAML.

**Approval evidence:** This spec, approved at the design gate on 2026-09-13
(topology, manifest split, graph model, retrieval approach recorded in the
design conversation). Phase approvals recorded per-PR.

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

PR #308 wrote 5 generic namespaces. Both `namespace` and `id` carry the value
(`id: platform.architecture.04-knowledge-graph`), so migration rewrites both.

| Current | Migrates to |
|---|---|
| `platform` (architecture/) | `arc-execution`, `knowledge-graph`, `character-behavior`, `model-routing`, `session-runtime`, `safety`, `developer-api` — split by architecture section |
| `custom` (gdd/) | `nightcap` |
| `custom` (story-bibles/) | `monster-rpg`, `daily-case` (couch-race → archived) |
| `operating` (prd/, product/, roadmap/, agents/) | `product-roadmap` |
| `patterns` (conventions/, design/, specs/) | `engineering-practice` |
| `playbooks` (skills/, superpowers/) | `playtest-ops`, `engineering-practice` |

Two mappings are one-to-many and require judgement: `platform` splits per-file
by architecture section number, and `playbooks` splits between `playtest-ops`
and `engineering-practice` by whether a skill serves playtest operations or
development practice. Every one-to-many mapping is generated as a per-file
proposal for founder approval and is never applied unreviewed. The remaining
mappings are one-to-one and apply directly.

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
    owner: unassigned
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

| Skill | Enforces |
|---|---|
| `provider-leak-check` | No provider/model name outside `config/routing_table.json` and `engine/routing/router.py` |
| `scope-evidence-check` | Claimed product scope has durable approval in `docs/product/decisions-log.csv`, an ADR, or a spec |
| `knowledge-query-guard` | Knowledge-state query precedes every AI character generation call |

## Hooks

| Hook | Action |
|---|---|
| `SessionStart` | Inject domain map + currently-stale docs — session-to-session carryover |
| `PreToolUse` (Write/Edit) | Block edits to generated files and agent-local dirs |
| `PostToolUse` (Write) | Append a co-edit observation to the edge log |
| `Stop` | Run `validate-graph`; report freshness delta |

## Temporal graph

**Derive, don't store.** A machine-rewritten YAML edge file produces merge
conflicts on nearly every PR once more than one person contributes, and storing
co-edit edges duplicates git, which already is that graph.

| Edge type | Source | Storage |
|---|---|---|
| `co_edited` | `git log --name-only`, one batched traversal | none — derived |
| `declared`, `supersedes` | front matter `relations` | none — already there |
| `co_cited`, `co_retrieved` | agent answers, retrieval results | append-only JSONL |

JSONL appends merge cleanly in git; YAML rewrites do not.

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

- Model: `all-MiniLM-L6-v2`, 384 dimensions, CPU, cached once (~90MB)
- Storage: vectors as BLOBs in the existing SQLite index — ~7.7MB for a
  ~5,000-chunk corpus
- Search: brute-force cosine. ~2M FLOPs per query, sub-millisecond in JS, and
  faster than a network hop to a vector service at this scale
- No vector database, no service to run, no API key, no per-query cost
- Behind the existing `RetrievalAdapter` interface, so a hosted driver can be
  added later without touching callers

This is the one place team-ai makes a model call, and only at index time.
Revisit past roughly 100k chunks (~20× current corpus).

---

# Acceptance Criteria

**Phase A**

- [ ] Migration proposal lists every `id`/`namespace` change for founder approval before any write
- [ ] After migration, `team-ai validate-kb` passes on all 459 docs with 13 namespaces
- [ ] 17 agent definitions generated, each validating against `agent.schema.json`
- [ ] Every specialist has `max_hops: 0` and exactly one `kb_namespace`
- [ ] Router has `model_tier: none`
- [ ] `nightcap` domain is `authority: canonical`; `monster-rpg` and `daily-case` are `authority: provisional`
- [ ] No file outside `docs/` and `.claude/` is modified

**Phase B**

- [ ] `manifest.yaml` validates against the extended schema with all four sections
- [ ] `provider-leak-check` fails on a planted provider string outside the two allowed files and passes on the clean tree
- [ ] `scope-evidence-check` fails for scope with no decision record and passes with one
- [ ] `knowledge-query-guard` fails on a generation call with no preceding knowledge query
- [ ] All four hooks fire and are individually disableable
- [ ] Golden set of ≥ 30 real questions with known-correct domains; routing accuracy reported as a number
- [ ] `doc-currency-review` workflow runs end to end and pauses at the approval gate

**Phase C**

- [ ] Co-edit edges derived from git match a hand-verified sample
- [ ] Decay reduces an unobserved edge's confidence over simulated time; authored edges unchanged
- [ ] Staleness propagation pulls in `review_by` for high-confidence neighbours of a changed doc
- [ ] Semantic retrieval answers a semantically-phrased query that lexical search misses
- [ ] Hybrid retrieval scores ≥ lexical-only on the golden set
- [ ] Full index rebuild completes in < 60s on the current corpus

---

# Test Plan

- **Unit**: namespace migration mapping; manifest schema validation; each
  enforcement skill against planted violations and clean trees; decay,
  reinforcement, and pruning arithmetic; RRF fusion ordering
- **Integration**: generate the full instance into a temp copy of Arcwright and
  assert the repo is otherwise untouched (extends team-ai's existing dogfood
  test); run each workflow end to end including gate pause
- **Eval**: golden question set through the router — routing accuracy, refusal
  rate, citation validity; hybrid vs lexical-only compared on identical inputs
- **Manual**: founder reviews the migration proposal and the generated agent
  instructions before either is applied

---

# Risks and Unknowns

**Risks**

- **`id` rewrite is effectively irreversible.** `id` embeds the namespace, so
  migration changes 459 ids. Anything referencing an old id breaks. Mitigation:
  `validate-citations` runs before and after; migration is one reviewed commit.
- **Refusal rate may frustrate.** Keyword routing refuses unusual phrasings.
  Mitigation: golden set measures it; `not_owned` and keyword tuning are cheap
  to iterate; semantic retrieval in Phase C reduces it.
- **17 agents is real maintenance surface** for a solo founder. Mitigation:
  generated from templates, so a domain change is a fragment edit plus a
  re-render, not hand editing 17 files.
- **Local embedding model adds a sizeable dependency** with native build
  implications on some platforms. Mitigation: index-time only; lexical
  retrieval continues to work if the model is unavailable.
- **Breaks team-ai's zero-model-call rule.** Narrowed to index time and a local
  model, but the invariant is genuinely weakened and should be documented in
  team-ai's own README rather than quietly dropped.

**Unknowns**

- Whether 13 domains is the right granularity in daily use, or whether some
  specialists are too thin to justify their own agent. The golden set will show
  which domains never get routed to.
- Real decay half-life. Parameters are guesses until there is observed data;
  pruning stays disabled until they are reviewed.
- Whether `docs/playtests/` (currently empty) warrants its own domain or folds
  into `playtest-ops` backed by the existing skills.

---

# Open Questions

- Q1: Should the existing hand-authored agents in `docs/agents/` and skills in
  `docs/skills/` be registered in the manifest as tier-2 personas, or stay
  outside the generated topology and be referenced only?
- Q2: Should `nightcap-couch-race` get an `authority: archived` domain so
  questions about it route somewhere that explains it is archived, or should it
  be absent so such questions refuse?
- Q3: Who is `owner` for each domain in a solo-founder context — is
  `unassigned` honest, or should everything be the founder until the team grows?
