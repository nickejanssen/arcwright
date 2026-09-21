---
id: engineeringpractice.specs.0089-team-ai-agent-architecture
namespace: engineering-practice
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

**Status**: Approved. Phase A implemented. Phase B completed 2026-09-20 as a
21-task phase, with the model-based delegation eval deliberately cut and the
framework resolver release still pending.

**Version**: 1.7 | **Last updated**: 2026-09-20 | **Canonical path**: `docs/specs/0089-team-ai-agent-architecture.md`

**Author**: Claude (with founder) | **Date**: 2026-09-13

---

# References

- Canonical agent rules: [`AGENTS.md`](../../AGENTS.md) — architecture principles 5 (knowledge graph), 6 (cost-aware), 8 (provider-agnostic routing); agent-local files section
- Documentation rules: [`docs/README.md`](../README.md) — no model names or provider strings in docs
- Architecture sections: [`docs/architecture/01`–`15`](../architecture/) — the source of the engine domain split
- Framework: [github.com/nickejanssen/team-ai](https://github.com/nickejanssen/team-ai); framework design note `docs/design/2026-09-13-agent-topology-design.md`
- Prior work merged: PR #308 — `docs: backfill KB front matter via team-ai adopt`
- Framework prerequisites: team-ai PR #4 (install without `npx`) and PR #5 (generator path containment)
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

Version 1.2 incorporates an adversarial review of version 1.1 whose verdict was
"redesign needed". Every finding is resolved in this version or explicitly
pushed back on with evidence; see *Review Resolution*.

---

# In Scope

Delivered in three phases, each independently reviewable.

**Phase A — Agent layer and namespace migration**

- Framework prerequisites in team-ai: manifest schema extension, a manifest
  invariant validator, per-domain namespace scoping, instance catalogs wired
  through `init`/`resume`/`upgrade`, answers keyed by question id, a
  configurable KB root with exclusions, a conflict-safe namespace remapper,
  emitter options for committed Claude Code agents, and removal of every `npx
  team-ai` invocation from generated servers and workflows
- Migrate all seven namespace values written by PR #308 to 14 Arcwright
  namespaces: 13 specialist domains plus the archived `nightcap-couch-race`
- Generate the router and 13 specialists into `team-ai/`; hand-author and
  register the three tier-2 group SMEs
- Emit the 17 agents as Claude Code subagents under `.claude/agents/team-ai-*.md`
- Emit the `domains`, `agents`, and `skills` manifest sections

**Phase B — Retrieval correctness, enforcement, hooks, measurement**

Redesigned 2026-09-20 after measurement. The design of record is
[`docs/superpowers/specs/2026-09-20-team-ai-agent-architecture-phase-b-design.md`](../superpowers/specs/2026-09-20-team-ai-agent-architecture-phase-b-design.md)
(v2.1); the plan is
[`docs/superpowers/plans/2026-09-20-team-ai-agent-architecture-phase-b.md`](../superpowers/plans/2026-09-20-team-ai-agent-architecture-phase-b.md).
Where this section and that design differ, the design wins.

- Fixed the lexical scoring defect in team-ai and re-measured it. Stopword-only
  queries now return no results, padding does not improve ranking, and query
  scores are normalized by term count. Hit rate remained 48.5%.
- Chose retrieval strategy per domain by corpus size: eleven domains holding
  5.3% of the corpus read their documents outright; the three holding 94.7%
  use the ranked index through the scoped search command.
- Added three deterministic enforcement skills.
- Added four Claude Code hooks as a non-blocking loop. Stop returns in 216ms
  and SessionStart returns in 219ms.
- Added the 37-question golden set, coverage metric, and ratcheted gates.
  Coverage reached 97.0%; hit rate remained 48.5% against the 80% target.
- Added the `/doc-review` slash command, which reports stale or orphaned
  documents and pauses for named approval before changes.

**Dropped from Phase B**, with reasons recorded in the design:

- Scored-router improvements — not in the delivery path
- The `workflows` manifest section and any workflow engine — nothing would
  execute the section, and the engine would be the largest item in the phase
- Semantic retrieval, unconditionally — conditional on post-fix measurement
- Topology change from 17 agents to 8 — deferred to real-use evidence
- A model-based delegation eval — D-B14; a proxy for what real use shows for
  free
- Corpus re-namespacing — a second migration over roughly 390 documents would
  not fix scoring

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
  skills in `docs/skills/`. Those are registered in the manifest, not rewritten.
- Retroactive rewriting of `docs/archive/`, which stays outside the KB.
- A repository-wide, id-aware citation validator (see *Review Resolution*, R14).

---

# Human Collaboration Contract

**Interaction profiles:** Decision interview | Creative collaboration

**Classification rationale:** Domain boundaries and authority levels encode
founder judgement about how expertise actually divides and which sources are
canonical — neither is derivable from the repo. The namespace migration
rewrites `id` on every KB document, which is irreversible in practice once
other artifacts reference the new ids.

**Required founder inputs:**

- Confirmation of the domain split and each domain's `authority` value
- Approval of the per-file namespace migration proposal before it runs
- Golden question set review — the questions define what "correct routing" means

**Phase gates:**

- Phase A: team-ai PRs #4 and #5 merged and team-ai 0.4.0 released before any
  generation; the migration proposal approved before any `id` rewrite; generated agents reviewed before merge
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
- *Layout approval.* On 2026-09-13 the founder approved the generated-file layout
  in *Generated file layout*, including the narrow `.claude/agents/team-ai-*.md`
  exception to the agent-local files rule ("Approve, with .claude exception").
- *Group SME approval.* On 2026-09-13 the founder chose to hand-author and
  register the three tier-2 group SMEs (D5) rather than generate them.
- *Decision approvals.* On 2026-09-13 the founder confirmed D1, D2, D3, and D6
  (built-in search, no MCP server).
- *Not covered by any approval yet.* The version 1.1–1.4 revisions. Versions
  through 1.3 merged in PR #309; 1.4 corrects defects found while preparing
  implementation, including the D1 clarification above.
- *Not an implementation authorization.* Design approval authorizes planning
  only. The per-file migration proposal requires its own explicit founder
  approval, recorded in the Phase A PR, before `--apply` runs.

**Owner actions:** None external.

---

# Architecture

## Three-tier topology

```
TIER 1  sme (router)          model_tier: none   max_hops: 2    generated
        Keyword→domain match against manifest.yaml. Refuses when no
        domain owns the question.

TIER 2  engine-sme            model_tier: small  max_hops: 1    hand-authored (D5)
        title-sme             Cross-cutting questions spanning >1 specialist.
        practice-sme

TIER 3  Specialists           model_tier: small  max_hops: 0    generated
        engine:   arc-execution · knowledge-graph · character-behavior
                  model-routing · session-runtime · safety · developer-api
        title:    nightcap (canonical) · monster-rpg · daily-case (provisional)
        practice: product-roadmap · engineering-practice · playtest-ops
```

17 agents: 14 generated from team-ai templates and 3 hand-authored. The
generator produces the router from `agents/sme.yaml.hbs` and one specialist per
`agents.domains` entry from `agents/_domain-sme.yaml.hbs`. team-ai has no
group-SME template, and `team.size: 1-3` suppresses generated role subagents,
so tier 2 is authored by hand and registered with `source: authored`.

**These are validated invariants, not runtime guarantees.** team-ai has no
agent runtime of its own; delegation happens in the host (Claude Code). What
team-ai can and does do is refuse to ship a configuration that breaks the
invariants:

| Invariant | Enforced by |
|---|---|
| Router has `kind: router` and `model_tier: none` | `team-ai validate-manifest`, run in CI |
| Every tier-3 agent has `max_hops: 0` and exactly one `kb_namespaces` entry | `validate-manifest` |
| No two tier-3 agents share a namespace | `validate-manifest` |
| Every domain's `subagent` names an agent in the manifest | `validate-manifest` |
| `authority` is one of `canonical`, `provisional`, `archived` | manifest JSON Schema |
| A provisional source is cited as provisional | agent instructions only — **not** enforced; measured by the Phase B golden set |

Routing refusal and hop limits at runtime depend on the host honouring the
emitted definitions. That limitation is stated rather than hidden.

## Generated file layout

Approved by the founder on 2026-09-13.

| Path | Contents | Tracked |
|---|---|---|
| `team-ai/` | `manifest.yaml`, `agents/manifest.fragment.yaml`, generated and hand-authored agent definitions, skills, personas, `catalog/`, `team-profile.yaml`, `answers.yaml`, `index.lock`, `namespace-remap.yaml`, `inventory.txt`, remap proposal | yes |
| `.team-ai/` | search index, caches | no — gitignored |
| `.claude/agents/team-ai-*.md` | emitted Claude Code subagents, one per agent | yes, generated; CI fails if they drift from regeneration |
| `docs/**` | front-matter `namespace` and `id` lines only, during migration | yes |
| `AGENTS.md`, `.github/copilot-instructions.md` | the scoped exception below, kept in sync | yes |

`team-ai/` is team-ai's built-in `subdir` reconcile strategy, which renders an
instance into `<repo>/team-ai/`, so no new path code is needed.

**The `.claude` exception**, added to the agent-local files section of
`AGENTS.md` and mirrored in `.github/copilot-instructions.md`:

> Exception: files matching `.claude/agents/team-ai-*.md` are generated from
> `team-ai/` by `team-ai emit` and are intentionally tracked. Do not edit them
> by hand; regenerate them. This exception covers no other path under `.claude/`.

Nothing else under `.claude/`, `.codex/`, or `.cursor/` is created or modified.
The existing `.claude/agents/implementer.md`, `reviewer.md`, and
`.claude/commands/` are untouched.

## How agents reach the knowledge base

The knowledge base is the Markdown already committed under `docs/`, in its
existing directories. Every developer who clones the repository has it.
Namespaces are front-matter metadata over those files, so nothing moves.
Agents read the local clone the same way a developer does.

**D6 (approved 2026-09-13): built-in search, no server.** Emitted subagents get
Claude Code's `Read`, `Grep`, and `Glob` tools plus a generated *Search
procedure* that comes before, and overrides, the templates' tool-specific steps. A specialist lists its documents by
searching the KB root for its `namespace:` front-matter line, then reads and
searches only those.

- No MCP server, no root `.mcp.json`, no new dependency, no per-machine setup.
- No derived index is committed or has to be kept in sync.
- Trade-off accepted: no ranked search and no retrieval-level "nothing found"
  signal. Refusal comes from the agent instructions, and the Phase B golden set
  measures whether this lookup misses relevant documents.

Revisit team-ai's local MCP server only if the golden set shows this lookup
missing documents that ranked search would find, or a second coding client
needs the same tools. team-ai still removes `npx` from its MCP server template,
because that template ships to other teams.

## Namespace migration

PR #308 wrote **seven** namespace values. Both `namespace` and `id` carry the
value (`id: platform.architecture.04-knowledge-graph`), so migration rewrites
both. Counts from `main` on 2026-09-13:

| Current value | Docs | Found in | Migrates to |
|---|---|---|---|
| `operating` | 187 | `prd/`, `product/`, `roadmap/`, `agents/` | `product-roadmap` |
| `patterns` | 129 | `conventions/`, `design/`, `specs/` | `engineering-practice` |
| `playbooks` | 48 | `superpowers/` (47), `skills/` (1) | `engineering-practice`; playtest-related files → `playtest-ops` per file |
| `custom` | 38 | `gdd/` (33), `story-bibles/` (5) | `nightcap`; story bibles per file → `monster-rpg`, `daily-case`, `nightcap-couch-race` |
| `decisions` | 25 | `decisions/` | `product-roadmap`, which owns ADRs |
| `platform` | 17 | `architecture/` | per file across the seven engine domains, by section |
| `unmapped` | 1 | `docs/README.md` | `engineering-practice` — documentation access, versioning, and AI-cost rules |

**Scope.** The remapper operates only on files under the configured KB root
that carry KB front matter. On `main`, 706 Markdown files live under `docs/` and
445 carry KB front matter. The rest are skipped and listed, never counted as
conflicts:

| Excluded from the KB root | Files | Why |
|---|---|---|
| `docs/archive/` | 234 | historical exports; canonical docs win |
| `docs/design/line-libraries/` | 15 | draft line libraries without KB front matter |
| `docs/skills/*/SKILL.md` | 9 | skill manifests with their own front matter, not KB docs |
| `docs/adoption-plan.md` | 1 | the `team-ai adopt` report, not a KB document |
| `docs/decisions/0000-template.md` | 1 | the ADR template |
| `docs/specs/0041-aw-217-session-lifecycle-api-and-auth.md` | 1 | carries its own non-KB front matter (`spec_id`, `issue`, `milestone`); reconciled separately rather than rewritten during migration |

**Rules:**

1. A committed inventory (`team-ai/inventory.txt`) lists every KB document,
   its current namespace, and its target, generated by a deterministic command.
   Counts in this spec are never trusted over the inventory.
2. The remapper fails if any KB document's namespace has no mapping rule.
3. A file whose front matter does not parse, or whose `id`/`namespace` line is
   quoted or carries a trailing comment, is a **conflict**. On `main` there are
   zero quoted or commented lines; the rule exists so the rewrite never silently
   drops quoting it did not expect.
4. `--apply` refuses to write anything while the proposal contains any conflict.
   Exclusions go in the mapping file, where they are reviewed.
5. The founder approves the per-file proposal before `--apply`.

## Validation that actually covers Arcwright

- `index.lock` gains an optional `kb` block — `root: ../docs` and the exclusions
  above — read by `validate-kb`, `reindex`, `search`, `freshness-audit`, and the
  MCP server when no flag overrides it.
- `validate-kb` reports each unparseable file as its own failure instead of
  aborting the whole run (the same class of crash fixed in `team-ai adopt` 0.3.1,
  triggered by the same `arcwright-minigame` SKILL.md).
- Front-matter parsing normalizes line endings first. Windows checkouts with
  `core.autocrlf=true` (Arcwright has no `.gitattributes`) put CRLF on every
  line, and the parser otherwise throws on `tags: []` or keeps a trailing
  carriage return on every value, so no id or namespace would ever match.
- After migration, the check that ids did not break is a grep for any token
  starting with one of the seven prior namespace values across the repository
  outside `docs/archive/`. It must return zero.

## Manifest

`team-ai/manifest.yaml` is generated by `assemble-manifest` from fragments. Four
sections:

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
    source: generated

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
| `provider-leak-check` | No provider or model name outside `config/routing_table.json` and `engine/routing/router.py` | Runtime code and config: `engine/`, `api/`, `sdk/`, `dashboard/`, `config/`. Documentation is governed separately by `docs/README.md`, which forbids model names and provider strings in docs; 44 docs on `main` currently contain such strings and are candidates for a separate cleanup, not an exemption |
| `scope-evidence-check` | Claimed product scope has durable approval in `docs/product/decisions-log.csv`, an ADR, or a spec | Specs and roadmap entries |
| `knowledge-query-guard` | Knowledge-state query precedes every AI character generation call | `engine/` |

## Hooks

| Hook | Action |
|---|---|
| `SessionStart` | Inject domain map + currently-stale docs — session-to-session carryover |
| `PreToolUse` (Write/Edit) | Block edits to generated files and agent-local dirs |
| `PostToolUse` (Write) | Record the session's observations in that session's own file under `team-ai/graph/observations/` |
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
`team-ai/graph/observations/<YYYY-MM>/<session-id>.jsonl`. They are never
appended to a shared file: two branches that each append to the end of one
shared file produce an ordinary git conflict. A per-session file is only ever
added, never edited, so two branches cannot conflict on it. `decay-sweep` reads
every file; any compaction it performs produces a derived, uncommitted cache.

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
never model-inferred. It also does not eliminate them.

## Retrieval

Hybrid: existing FTS5 lexical plus local semantic vectors, merged by reciprocal
rank fusion.

- **Model:** a small local sentence-embedding model — CPU only, on the order of
  384 dimensions and ~100MB on disk. The concrete model is chosen in the Phase C
  design; this spec deliberately names none. Where its identifier lives is an
  open question (Q1).
- **Storage:** vectors as BLOBs in the existing SQLite index — ~7.7MB for a
  ~5,000-chunk corpus at 384 dimensions.
- **Search:** brute-force cosine. ~2M FLOPs per query, sub-millisecond in JS.
- No vector database, no service to run, no API key, no per-query spend.
- Behind the existing `RetrievalAdapter` interface.

**The model runs at two points.** Every chunk is embedded at index time, and
**every search query is embedded at query time** into the same vector space:

1. **Load lazily, keep warm** — loaded on the first semantic query in a process.
2. **Embed the query** — expected low tens of milliseconds on CPU; to be measured.
3. **Cache** — query vectors keyed by normalized query text plus model version.
4. **Fall back, don't fail** — on load failure or timeout, return lexical-only
   results and report the fallback.

---

# Acceptance Criteria

**Phase A**

- [ ] team-ai PRs #4 and #5 merged; team-ai 0.4.0 tagged and released
- [ ] No `npx team-ai` invocation remains in team-ai's MCP server template, instance workflow templates, or reusable workflows
- [ ] `team-ai/inventory.txt` is committed and lists every KB document with its current and target namespace
- [ ] The migration proposal has zero conflicts and is explicitly approved by the founder before any write
- [ ] After migration, `validate-kb` passes against the configured KB root, `git grep -h '^namespace:' -- docs ':!docs/archive'` reports only the 14 target namespaces, and a repository grep outside `docs/archive/` finds no id beginning with any of the seven prior values
- [ ] 14 agents generated and 3 hand-authored; `team-ai validate-manifest` passes
- [ ] 17 files exist at `.claude/agents/team-ai-*.md`, each with `tools: Read, Grep, Glob`, and regenerating them produces no diff
- [ ] `nightcap` is `authority: canonical`; `monster-rpg` and `daily-case` are `provisional`; `nightcap-couch-race` is `archived`
- [ ] Every changed path is inside the approved layout: `team-ai/`, `.claude/agents/team-ai-*.md`, `docs/**` front-matter `namespace`/`id` lines, `AGENTS.md`, `.github/copilot-instructions.md`, `.gitignore`, and the CI workflow file
- [ ] `docs/agents/`, `docs/skills/`, and every other file under `.claude/` are unchanged

**Phase B** — completed 2026-09-20. The design carries the detailed verify
commands; the results below record the real outcome:

- [x] A pure-stopword query returns no results, and padding a question with
      meaningless words does not raise its score
- [x] Refusal remains a diagnostic rather than a lexical gate: term statistics
      do not separate in-scope from out-of-scope questions on this corpus
- [x] Hit rate is measured before and after the scoring fix: 48.5% before and
      48.5% after
- [x] Each domain's emitted agent states the retrieval strategy matching its
      corpus size; the three large domains can run the search command and nothing else
- [x] No emitted agent references `kb_manifest`, `kb_search` or `kb_coverage_gap`,
      and regenerating produces no diff
- [x] `provider-leak-check` passes on the clean tree with no exception list, and
      fails on a planted provider string
- [x] `scope-evidence-check` reports zero dangling references, fails on a
      fabricated decision id, and requires declared evidence on newly added
      specs and roadmap tasks only
- [x] `knowledge-query-guard` fails on a `character_dialogue` generation with no
      preceding knowledge query, and does not flag narration or mini-game resolution
- [x] All four hooks fire, are individually disableable, and session stop is not delayed
- [x] Golden set of ≥ 30 paraphrased questions carrying source path, expected
      domain, expected refuse, generation date and answer evidence; coverage
      reported per domain
- [x] `/doc-review` reports and pauses for approval without changing anything

**Two criteria from version 1.4 are withdrawn**, not merely unmet:
`manifest.yaml` validating "with all four sections" and the
`doc-currency-review` workflow running end to end. Both assumed a `workflows`
section and an engine to execute it, which Phase B does not build.

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

- **Unit**: manifest invariants; namespace migration mapping including an
  unmapped-namespace failure and quoted/commented-line conflicts; `--apply`
  refusing on conflict; KB exclusions and per-file parse failures; answers keyed
  by question id including unknown and missing ids; emitter built-in search mode
  and prefixing; MCP server template CLI resolution without `npx`
- **Integration**: generate the full instance into a temp copy of Arcwright and
  assert every changed path is inside the approved layout; regenerate emitted
  agents and assert no diff; merge two branches that both recorded observations
- **Eval**: golden question set through the router — routing accuracy, refusal
  rate, citation validity; hybrid vs lexical-only compared on identical inputs
- **Manual**: founder reviews the inventory, the migration proposal, and the
  generated agent instructions before any is applied

---

# Risks and Unknowns

**Risks**

- **`id` rewrite is effectively irreversible.** Mitigation: nothing in the
  repository references KB ids today (zero references outside front matter and
  adopt's own inventory files on 2026-09-13), the proposal is approved before
  apply, and the post-migration grep proves no old id survives.
- **Runtime behaviour depends on the host.** Hop limits and refusal are honoured
  by Claude Code reading the emitted definitions; team-ai validates them but
  cannot enforce them at runtime.
- **Refusal rate may frustrate.** Mitigation: the golden set measures it;
  `not_owned` and keyword tuning are cheap to iterate.
- **17 agents is real maintenance surface** for a solo founder. Mitigation: 14
  are generated; each agent's description stays to one line because Claude Code
  keeps subagent descriptions in context for delegation.
- **Local embedding model adds a dependency and per-query CPU work.** Mitigation:
  automatic lexical fallback.
- **Breaks team-ai's zero-model-call rule** in Phase C. Must be recorded as an
  explicit decision in team-ai's design of record.

**Unknowns**

- Whether 13 specialists is the right granularity in daily use. The golden set
  will show which domains never get routed to.
- Real decay half-life; pruning stays disabled until parameters are reviewed.
- Which `design/` and `specs/` documents warrant per-file overrides away from
  `engineering-practice`. Settled during review of the migration proposal.
- Whether `docs/design/line-libraries/` should become KB documents later.

---

# Open Questions

- **Q1 — RESOLVED 2026-09-20 by D-B13.** The identifier lives in
  `team-ai/index.lock`. The provider-and-model rule scopes itself to platform
  operations and model calls — principle 8's own first two bullets — and
  `provider-leak-check` already scans product code only. A model indexing
  internal documentation at development time is outside it, and needs no
  exemption. Original question retained below for the record.

- **Q1 (original) — Where does the embedding model identifier live?** Historical
  wording retained for traceability. D-B13 resolved the rule question: a local
  embedding model used for development-time indexing belongs in
  `team-ai/index.lock`, not the runtime routing table, if Phase C proceeds. Phase
  B did not commission semantic retrieval unconditionally.

---

# Approved Decisions

## Phase B sign-offs — approved 2026-09-20

Four boundary exceptions, each approved explicitly and separately by the
founder. They authorise the Phase B implementation session and nothing beyond
what is scoped here.

**B-S1 — One `engine/` comment line may be reworded.** `engine/safety/l3.py:196`
changes "Anthropic's `cache_control`" to "the provider's `cache_control`". This
is a narrow, named exception to *Out of Scope*, which otherwise forbids any
`engine/` change in this spec. It covers that one line and no other `engine/`
edit. It exists so `provider-leak-check` passes on a clean tree with no
exception list, since an exception list is how such a check stops being trusted.

**B-S2 — Scoped shell access for the three large-corpus agents.**
`engineering-practice-sme`, `product-roadmap-sme` and `nightcap-sme` may run the
team-ai `search` command, permitted in `.claude/settings.json` as that
subcommand alone. A bare `Bash` or `Bash(node:*)` permission is **not**
authorised. The other fourteen agents keep `Read, Grep, Glob`.

**B-S3 — The 17-file regeneration diff is approved.** Removing the emitted
`## Original instructions` block rewrites all 17 files under
`.claude/agents/team-ai-*.md`, cutting roughly 43% from each. Those files are
generated; the diff is the expected consequence of the emitter fix.

**B-S5 — `AGENTS.md` states the scope of the provider-and-model rule.**
Approved 2026-09-20. One bullet added under principle 8 recording that the rule
governs product code — `engine/`, `api/`, `sdk/`, `dashboard/`, `config/`,
which is exactly what `provider_leak_check.py` scans — and not development
tooling that makes no platform model call. This is a clarification, not a
relaxation: it writes down the interpretation already in force when
`provider-leak-check`'s scope was approved under B-S1, so the question stops
recurring. The prohibition is unchanged wherever it earns its keep. Mirrored to
`.github/copilot-instructions.md`. See D-B13.

**B-S4 — The `AGENTS.md` `.claude/` rule is corrected.** The rule states the
`team-ai-*.md` exception "covers no other path under `.claude/`", which is
inaccurate: `.claude/settings.json`, `.claude/commands/`,
`.claude/agents/implementer.md` and `.claude/agents/reviewer.md` are already
tracked and were committed earlier. The rule is replaced with an accurate list,
adding hook registration in `.claude/settings.json`. No path outside that list
becomes writable, and `.github/copilot-instructions.md` is re-mirrored to match.

## Phase B design decisions — approved 2026-09-20

Recorded in full, with the measurements behind each, in the Phase B design
document. In brief: fix lexical scoring before buying retrieval infrastructure
(D-B1); semantic retrieval is conditional on the post-fix measurement rather
than scheduled (D-B2); retrieval strategy is chosen per domain by corpus size
(D-B3); phases are cut by dependency rather than artifact type (D-B4); the eval
gate measures coverage deterministically in team-ai and delegation on the
Arcwright side (D-B5); `scope-evidence-check` enforces reference integrity plus
a declared evidence field (D-B6) required only on newly added documents (D-B7);
all four hooks ship as a non-blocking loop (D-B8); no workflow engine (D-B9);
`provider-leak-check` skips test files (D-B10); the dead instruction block is no
longer emitted (D-B11); the 17-to-8 topology question waits for Phase B's
evidence (D-B12).

---

**D1 — Existing agents and skills are registered, never regenerated.** Approved
2026-09-13. The hand-authored contracts in `docs/agents/` and skills in
`docs/skills/` are registered in the manifest as `source: authored`. Generation
never writes to their paths; team-ai PR #5 makes that a checked property.
Only the six role contracts in `docs/agents/` are registered; its `README.md`,
`USAGE.md`, `expert-personas.md`, and `road-to-live-playbook.md` are not agents.
Registered contracts have no team-ai agent definition, so they are never
emitted as subagents (clarified in version 1.4).

**D2 — `nightcap-couch-race` gets an `authority: archived` domain.** Approved
2026-09-13. Questions about Couch Race route to `title-sme`, which answers that
it is archived and superseded. One manifest entry, no new agent.

**D3 — The founder is `owner` on every domain until the team grows.** Approved
2026-09-13. Consistent with the `owner` value PR #308 wrote across the corpus.

**D6 — Agents search the KB with built-in tools; no MCP server.** Approved
2026-09-13. See *How agents reach the knowledge base*.

**D5 — Tier-2 group SMEs are hand-authored and registered.** Approved
2026-09-13. `engine-sme`, `title-sme`, and `practice-sme` are written by hand
under `team-ai/agents/` and registered with `source: authored`. No group-SME
generation is added to team-ai.

**Layout — approved 2026-09-13**, as specified in *Generated file layout*.

---

# Kill Criteria

Approved 2026-09-20, before the system was operated, while it was still easy to
be honest. Adapted from team-ai's own design, section 21.

The return on this system depends entirely on it being used. 17 agents, 449
documents, a golden set and a measurement harness are sunk cost if nobody asks
them anything. These conditions say when to cut back rather than extend.

Reviewed at the end of each month of operation:

- **The coverage gap log goes unread for a month** → cut the agent layer back.
- **Hit rate sits below the ratcheted gate and no one is fixing documents**
  → stop building retrieval. The corpus is the problem, not the machinery.
- **Fewer than a handful of real SME questions a week, one month after Phase B
  closes** → cut back to the three enforcement checkers and `/doc-review`.
  Those pay for themselves without anyone asking them anything; the agent layer
  does not.
- **Measured cost per answer exceeds the time it saves** → stop.

**The temporal graph is cancelled, not postponed, if** three months after the
observation log starts collecting it shows no repeated cross-domain access
patterns and freshness still reports zero stale documents. Three of its four
stated uses — staleness propagation, gap detection, routing hints — have
no data today, and the fourth is marginal.

**Phase C is one thing:** semantic retrieval for the three domains that hold
94.7% of the corpus, gated on hit rate. When that gate clears, the build is
finished and the system is operated rather than extended. There is no Phase D.

A stale knowledge base that answers confidently is worse than no knowledge base.
These criteria and the gap log are what prevent that, and they only work if
someone reads them.

**Delegation quality** is assessed from real use and the observation log,
reviewed at the one-month mark alongside these criteria. If SME questions are
being asked and the wrong agent is picked repeatedly, that is the evidence for
the 17-to-8 topology decision. If no questions are being asked, that decision is
moot and the agent layer is cut back under the criteria above.

---

# Review Resolution

Resolution of the 14 findings from the adversarial review of version 1.1.

| # | Finding | Resolution |
|---|---|---|
| R1 | Instance catalog unwired in `init` | Accepted. Confirmed `buildContext(engine)` at `init.ts:137`, `resume.ts:148`, `upgrade.ts:88`. Catalog directory threaded through all three with a CLI option |
| R2 | Remap strips quotes and comments | Accepted as a false claim; zero affected lines on `main`. Quoted or commented lines become conflicts. CRLF concern refuted by the review itself |
| R3 | Model/provider strings in docs | Accepted. Model name removed in 1.1; commit-attribution trailers containing model names removed from the plan in 1.2 |
| R4 | Neutrality scan narrower than implied | Partly accepted. The plan's wording is corrected. **Pushback:** excluding docs, tests, and fixtures is by design — the denylist protects shipped source. `check-agnostic` has no options to ignore; it scans the working directory |
| R5 | Generator cannot produce 17 agents | Accepted. 14 generated, 3 hand-authored (D5) |
| R6 | Remapper cannot reach zero conflicts; partial apply | Accepted, and larger than reported: 261 of 706 Markdown files lack KB front matter. Scoped to KB documents; `--apply` refuses on any conflict |
| R7 | Topology guarantees are declarative | Accepted. `validate-manifest` enforces the checkable invariants in CI; wording changed to "validated invariants". **Pushback:** runtime enforcement belongs to the host, not team-ai |
| R8 | Namespace map omits live namespaces | Resolved in 1.1; 1.2 adds a hard failure on any unmapped namespace and a committed inventory |
| R9 | 459-file count unsupported | Resolved in 1.1; 1.2 replaces all counts with the committed inventory |
| R10 | Positional answers not replayable | Accepted. Answers file keyed by question id |
| R11 | Acceptance criteria contradict `AGENTS.md` | Accepted. Exact path allowlist; `.claude` limited to the founder-approved `team-ai-*.md` exception |
| R12 | Verdict: redesign needed | Accepted; this version is the redesign |
| R13 | Path traversal bypasses D1 | Accepted and reproduced. Fixed in team-ai PR #5 |
| R14 | Validation commands do not validate Arcwright | Accepted for `validate-kb` (configurable KB root, per-file parse failures). **Pushback on a repository-wide id-aware citation validator:** nothing in the repository references KB ids today, and migration changes ids, not file paths, so link validation proves nothing about it. A grep for surviving prior-namespace ids is the check that matches the risk |

Additional defects found while resolving the review, not raised by it:

- team-ai's MCP server template runs `npx --yes team-ai`, which fetches an
  unrelated npm package; its `ROOT` is computed from `URL.pathname`, which is
  wrong on Windows; and its freshness tools hard-code `kb/`.
- team-ai's reusable validation workflows run `npx team-ai@latest`.
- Emitted Claude Code agents named tools that do not exist without the MCP
  server, and in a form Claude Code does not resolve.
