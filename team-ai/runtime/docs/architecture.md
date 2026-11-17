# Team AI Scaffold: Architecture and File Tree Spec

**Version:** 0.3
**Owner:** Partner Solutions
**Companions:** `create-team-ai-interview-spec.md`, `README.md`

**What changed from 0.2:** the MCP server is no longer phase 1. It is demand-gated and split into two separate gates, local and remote, each earned by an audience that actually exists. Phases 1 through 3 run on scripts and a repo with no server at all. Preflight now probes whether the existing GitHub connector already covers the chat-app case. The toolkit is extracted from a validated instance rather than built first, so the project starts as one repo, not two.

**What changed from 0.1:** vendor neutrality made structural rather than assumed; an explicit cost model with an executor ladder, model tiers, caching, and budgets; harness preflight; attach mode; catalog overrides; audits reclassified from skills to scripts; a one-hop cap on delegation; kill criteria.

---

## 1. Goals and non-goals

### Goals

- One place where a team's knowledge lives, usable by humans and agents.
- A top-level SME that knows what exists, answers what it can, and routes the rest.
- Domain and role subagents that inherit shared plumbing instead of reinventing it.
- Deterministic, testable tools for touching the knowledge base.
- Works from Claude Code, from the Claude apps, and for non-technical stakeholders.
- Portable across models and clients. No lock-in below the MCP boundary.
- Cheap to run, with the cost of every answer path visible and bounded.
- A generator so team #2 does not have to read this document to get started.

### Non-goals

- Not a chatbot product. No custom UI is being built.
- Not a replacement for Confluence or Jira. It reads from them and points back to them.
- Not an autonomous writer. Agents propose knowledge changes, humans merge them.
- Not a fine-tuning project.
- Not a competitor to an existing org-wide enterprise search deployment. If one exists, this either feeds it or stands down. See section 4.

---

## 2. Design principles

1. **Git is the source of truth. Every index is disposable.** Any index can be deleted and rebuilt from the repos in one command. This is what keeps the storage decision reversible.
2. **Retrieval hides behind one interface.** Skills and agents never talk to a database. They call `kb_search`. Lexical, vector, and graph are swappable config.
3. **Cheapest correct executor wins.** For any unit of work, pick the lowest rung that can do it correctly: no model, then a script, then a small model, then a large model. Section 10 makes this concrete.
4. **Deterministic tools, probabilistic agents.** Anything with a right answer is code. Anything requiring judgment is an agent calling that code.
5. **Every internal claim carries a citation.** If the system cannot cite a KB path, it says it does not know and logs a gap.
6. **MCP is the portability boundary.** Nothing vendor-specific may exist below it. Client-specific formats are emitted at build time, never hand-authored.
7. **One hop.** The router may delegate to a subagent. A subagent may not delegate further. Every hop is a fresh context and a new bill.
8. **Thin spokes.** A spoke contributes docs, a manifest entry, and optionally an agent. Nothing else.
9. **Access control lives server-side.** Sensitivity is enforced by the server's token scope, never by an instruction in a prompt.
10. **Boring first.** Ship lexical retrieval and prove the workflow before spending a sprint on embeddings or graphs.
11. **Infrastructure is earned, not assumed.** Every piece of running infrastructure, starting with the MCP server itself, is added when a real audience asks for it twice. Scripts and a git repo already serve coding agents. Build the server when someone who cannot clone a repo needs an answer, not before.

---

## 3. Repo topology

Three roles. **Start with one repo.**

| Repo | Role | Contents | Who consumes it |
|---|---|---|---|
| `team-ai` | **Toolkit** | Generator, MCP server, retrieval adapters, schemas, emitters, reusable CI actions, catalogs | Every team in the org |
| `ps-ai-core` | **Instance** | Your KB, your manifest, your agents and personas, your evals | Partner Solutions |
| `ps-spoke-*` | **Spoke** | Domain knowledge and one domain agent | Optional, only when a real one appears |

The toolkit and instance split is what makes this portable, but it is the **end state, not the starting point.** Build the instance first. Extract the toolkit at phase 7, once the thing being templatized has been validated by real use. Templatizing before validation means paying twice.

Do not create spokes on day one either. Start with namespaces inside the instance. Split out a spoke when a domain has its own owner, its own release cadence, or access rules that differ. The spoke contract exists from the start so splitting is a move, not a rewrite.

**Attach mode** is the fourth case: an existing code repo that wants a role subagent and skills but has no knowledge of its own. It gets a small config pointing at the instance and nothing else. Most of your repos are this.

---

## 4. Harness preflight

Before generating anything, the toolkit scans for what already exists. Duplicating an org's AI infrastructure is the fastest way to get this shut down.

What it looks for:

| Signal | Where | Meaning |
|---|---|---|
| Existing MCP servers | `.mcp.json`, client config, org registry | Tools already available, do not rebuild |
| Existing agent config | `CLAUDE.md`, `.claude/`, `AGENTS.md`, equivalents | A harness exists, extend it |
| Existing vector store | env vars, infra as code, team docs | Reuse the store, add a namespace |
| Org enterprise search | Confluence AI, Glean-class tools, internal search | Possible full overlap |
| Existing skills or plugins | marketplace registries, plugin directories | Import rather than duplicate |

Three outcomes, and the toolkit states which one applies:

1. **Extend.** A harness exists and is compatible. Generate into it. Register the KB server alongside existing servers, adopt the existing agent config file rather than creating a parallel one.
2. **Coexist.** Something exists but is scoped differently. Generate separately and record the boundary in `docs/architecture.md` so the overlap is deliberate.
3. **Stand down.** The org already has good enterprise search over the same content. The honest recommendation is to contribute documents to it and skip the index entirely, keeping only the manifest, agents, and skills layers. The toolkit says this out loud rather than building a duplicate.

### The connector probe

Preflight also tests the cheapest possible version of the whole system: whether an existing repo connector already answers the chat-app case. If a GitHub or Drive connector is configured, it points the client at a small structured document set and runs five of the golden questions against it.

If that returns useful cited answers, the honest report is that phases 5 and beyond may never be needed, and the project reduces to writing good documents in a well-structured repo. What you lose without a server is ranked retrieval, namespace scoping, enforced citations, per-query sensitivity filtering, a shared cache, and cost telemetry. Some teams do not need any of that.

Preflight output is written to `docs/preflight.md` and re-run by `team-ai doctor`.

---

## 5. System overview

```
                    ┌──────────────────────────────────┐
                    │  Clients (any MCP-capable)       │
                    │  Claude Code · Claude apps ·     │
                    │  read-only stakeholders · other  │
                    └───────────────┬──────────────────┘
                                    │  MCP  ◄── portability boundary
                    ┌───────────────▼──────────────────┐
                    │  Router (SME)                    │
                    │  manifest lookup, no model call  │
                    │  on the deterministic path       │
                    └───────┬──────────────────┬───────┘
                            │                  │
              ┌─────────────▼───┐        ┌─────▼────────────┐
              │ Domain subagents│        │ Role subagents   │
              │ tier: small     │        │ tier varies      │
              └─────────────┬───┘        └─────┬────────────┘
                            │                  │
                    ┌───────▼──────────────────▼───────┐
                    │  Skills (fixed tool sequences)   │
                    └───────────────┬──────────────────┘
                                    │
                    ┌───────────────▼──────────────────┐
                    │  KB MCP server                   │
                    │  + answer cache + budget guard   │
                    └───────────────┬──────────────────┘
                                    │
                    ┌───────────────▼──────────────────┐
                    │  Retrieval adapter               │
                    │  lexical | vector | graph | hybrid│
                    └───────────────┬──────────────────┘
                                    │
                    ┌───────────────▼──────────────────┐
                    │  Knowledge base: markdown in git │
                    └───────────────┬──────────────────┘
                                    │
                    ┌───────────────▼──────────────────┐
                    │  Scripts: reindex · validate ·   │
                    │  audit · manifest · evals        │
                    │  no model calls at all           │
                    └──────────────────────────────────┘
```

---

## 6. Surfaces

### 6.1 Does this need a server at all?

Not at first. Three access tiers, each earned separately.

| Tier | Serves | What it costs | Phase |
|---|---|---|---|
| **Repo and scripts, no server** | Anyone with a coding agent and a clone. Search, citations, validation, audits, evals all work | Nothing. No infra, no auth, no ops | 1 |
| **Local stdio MCP** | Same people, plus clean tool contracts and portability across coding clients | Nothing to run, per-machine setup | 4, gated |
| **Remote HTTP MCP** | Chat apps, read-only stakeholders, any other MCP client. Adds shared cache, per-query sensitivity filtering, cost telemetry | Deploy, auth, token issuance, ongoing ops | 5, gated |

**Gate for local stdio:** a second coding client, or tool contracts stable enough that hand-rolled script invocation is the friction.

**Gate for remote:** two real requests from people who cannot clone a repo. Not an anticipated audience. Two actual asks.

Coarser alternatives that cost nothing and are worth using until the gates open:

- Sensitivity separation by putting confidential content in a second repo with different git permissions, instead of per-query filtering.
- Chat-app access through an existing repo connector, if the preflight probe in section 4 showed it works.

### 6.2 Once the server exists

One server, three token scopes. Do not fork the server per audience.

| Surface | Who | Connection | Scope |
|---|---|---|---|
| Coding agent | Engineers, SA | Local stdio or remote MCP | Full: search, get, propose, audit |
| Chat apps, desktop and mobile | You, partner-facing work | Remote MCP connector | Full minus repo-write skills |
| Read-only stakeholders | Partner Success, Strategic Partnerships, leadership | Remote MCP, restricted token | `kb_search`, `kb_get`, `kb_manifest`; confidential filtered out |
| Any other MCP client | Future | Remote MCP | Whatever scope the token grants |

The tool contracts in section 10 are written as MCP tools because that is where they land. Until then the same seven operations exist as scripts with identical signatures, which is what makes the later wrapping cheap.

---

## 7. Portability and vendor neutrality

The rule: **nothing below the MCP server may know which model or client is calling it.**

| Layer | Portable | Notes |
|---|---|---|
| KB markdown and front matter | Yes | Plain files |
| Schemas and validators | Yes | JSON Schema |
| Retrieval adapters | Yes | Embedding provider is a config value, pinned in `index.lock` |
| MCP server and tools | Yes | MCP is an open protocol |
| Scripts, evals, CI | Yes | Plain code |
| Manifest and agent definitions | Yes | Neutral YAML plus markdown, stored once |
| Client-specific agent files | No, and they are **generated** | Emitters render the neutral definitions per client |

### Neutral agent definition

Authored once, in `agents/*.yaml` with prose in a sibling `.md`:

```yaml
name: platform-sme
kind: subagent                 # router | subagent | persona
description: Offer API auth, rate limits, error semantics
model_tier: small              # none | small | large
kb_namespaces: [platform, patterns]
tools: [kb_search, kb_get, kb_list, kb_coverage_gap]
max_hops: 0                    # cannot delegate further
escalate_to: platform-eng
instructions_file: agents/platform-sme.md
```

### Emitters

```
team-ai emit --target claude-code   # client agent files, plugin manifest
team-ai emit --target mcp-only      # server-side prompt registry, for app clients
team-ai emit --target generic       # portable bundle for another harness
```

Emitted files are gitignored build artifacts. If a client format changes, you rewrite one emitter, not fifty agent files. Porting to a different model provider means changing the embedding config and the emitter target, and nothing else.

**Embedding portability caveat, stated plainly:** switching embedding providers requires a full reindex. That is cheap because the source is markdown in git. It is the main reason not to make a database the store.

---

## 8. Knowledge base design

### 8.1 Front matter

```yaml
---
id: ps.platform.rate-limits            # permanent, never reused
namespace: platform
title: Offer API rate limits
owner: solutions-architect
status: active                          # draft | active | deprecated
review_by: 2026-12-01
sensitivity: internal                   # public | internal | confidential
source: authored                        # authored | synced:<system>
source_url:
tags: [offer-api, errors, 429]
supersedes: []
relations:                              # optional, enables a graph index later
  depends_on: [ps.platform.auth]
  used_by_partner: [acme, globex]
  owned_by_role: solutions-architect
---
```

Rules:

- `id` is permanent. Renaming a file does not change it.
- `synced:*` documents are read-only here. Fix them at the source.
- `deprecated` documents stay indexed, rank lower, and are flagged inline in every citation.
- `relations` is cheap to fill from day one and is the only prerequisite for adding a graph index later without a migration.

### 8.2 Namespaces

Namespaces are the routing and permission unit. Every preset uses the same second-level shape so cross-team routing stays predictable:

```
operating/     charter, roles, ceremonies, how the team works
platform/      the systems this team owns or integrates with
patterns/      reference approaches and worked examples
playbooks/     repeatable procedures
decisions/     ADRs and why-we-did-that records
<domain>/      team-specific, for example partners/<name>/
```

Presets ship in the toolkit and are overridable. See section 15.

### 8.3 Chunking

- Split on H2 and H3, target 800 tokens, hard cap 1200.
- Every chunk inherits the document's full front matter as metadata.
- Every chunk stores its heading path, so citations resolve to `path#heading`.
- Chunking config, retrieval driver, and embedding model plus version are pinned in `index.lock`. Changing any forces a full reindex.

### 8.4 Lifecycle

| Stage | Trigger | Action | Executor |
|---|---|---|---|
| Create | Human or `kb_propose_change` | PR with validated front matter | Script validates |
| Refresh | `review_by` passes | Issue opened, assigned to `owner` | Script |
| Deprecate | Superseded | `status: deprecated`, `supersedes` set | Human |
| Gap | System cannot answer | Appended to the gap log | Script called by agent |

The gap log is the highest-value artifact here. It tells you exactly what to document next, based on what people actually asked and did not get.

---

## 9. Retrieval adapter

One interface, several drivers. The storage decision does not change when the driver does.

```ts
interface RetrievalAdapter {
  search(query: string, opts: {
    namespace?: string | string[];
    k?: number;                                   // default 8, hard cap 20
    filters?: { status?: string[]; sensitivity?: string[];
                tags?: string[]; owner?: string };
    mode?: "lexical" | "vector" | "graph" | "hybrid";
  }): Promise<Hit[]>;

  get(idOrPath: string, section?: string): Promise<Document>;
  neighbors?(id: string, relation?: string, depth?: number): Promise<Hit[]>;
  reindex(paths?: string[]): Promise<IndexStats>;
}

interface Hit {
  doc_id: string;
  chunk_id: string;
  path: string;          // repo-relative, citation target
  heading_path: string;
  score: number;         // normalized 0..1 across all drivers
  text: string;
  metadata: FrontMatter;
}
```

| Driver | Backing | Good when | Cost |
|---|---|---|---|
| `lexical` | SQLite FTS5 over the repo | Day one, hundreds of docs | Zero infra, zero per-query cost |
| `vector-embedded` | LanceDB or sqlite-vec, file-backed | Fuzzy questions, no new infra | Embedding cost at index time only |
| `vector-pgvector` | Postgres you already run | One place for everything | Existing infra |
| `vector-hosted` | Managed vector service | Multi-team scale | Per-seat or per-query |
| `graph` | Kùzu embedded, or a server-based graph DB | Relational questions dominate | Ontology upkeep is the real cost |
| `hybrid` | Lexical plus vector, RRF fused | Evals show it wins | Sum of both |

**Graph is an index, not a store.** It is built from the `relations` block plus front matter. Choosing it does not move your documents out of git.

**Decision rule so the choice can be deferred honestly:** ship `lexical`, build the eval set, then run the eval set against a vector or graph driver before committing to infra. If hit rate does not improve meaningfully, you saved a project. This is the phase 7 checkpoint in section 19.

---

## 10. Cost model

The architecture's main cost claim: most spend in systems like this goes to models doing work that code can do. Four mechanisms enforce that.

### 10.1 Executor ladder

For every unit of work, use the lowest rung that is correct.

| Rung | Use when | Examples |
|---|---|---|
| 0. No model | Output fully determined by input | Manifest lookup, cache hit, `kb_list`, citation resolution, validation |
| 1. Script | Deterministic transformation or check | Reindex, freshness audit, eval run, manifest assembly, spoke validation, gap logging |
| 2. Small model | Retrieve, extract, summarize, format against provided context | `kb-answer`, routing disambiguation, drafting a doc from a transcript |
| 3. Large model | Genuine synthesis, design judgment, tradeoffs | Integration review, architecture critique, adversarial review |

Every skill and agent declares `model_tier`. The router reads the tier from the manifest rather than deciding in the moment, which keeps tier selection deterministic and auditable.

### 10.2 The zero-model path

The router's happy path costs nothing. `kb_manifest` returns the routing table, an exact keyword or namespace match resolves to one domain, and the request is handed straight to that subagent with the namespace pre-scoped. No model is invoked to decide. Only ambiguous requests, where two or more domains match, escalate to a small model for disambiguation.

Refusal is also a zero-model path. If no domain matches and search returns nothing above threshold, the system refuses and logs a gap without ever invoking a model.

### 10.3 Answer cache

Cache key is `hash(normalized_query + namespace + scope + kb_commit_sha + index_version)`.

- A KB commit invalidates exactly the affected namespaces, not the whole cache.
- Cached answers still carry citations, and citation validity is rechecked cheaply on serve.
- The cache lives with the server, not the client, so a stakeholder asking a question an engineer already asked pays nothing.

### 10.4 Budgets and telemetry

Per-request guards, enforced server-side:

| Guard | Default |
|---|---|
| `k` cap | 20 hits |
| Retrieved context per answer | ~6k tokens |
| Hops | 1, router to subagent, no further |
| Tool calls per answer | 8 |

Every answer logs: path taken (cache, zero-model, small, large), tokens in and out, hits retrieved, latency, and whether it cited or refused. Cost per answer path is a CI-visible metric, and a regression fails the build the same way a failing test does.

### 10.5 Build-time cost discipline

- Never templatize before the thing being templatized is validated. The toolkit and generator are phase 7 for this reason.
- Never build infrastructure before an audience asks for it twice. The server was the largest line item in earlier drafts of this plan, and it existed to serve demand that was assumed rather than observed. It is now two separate gates.
- Schema and eval design happen in cheap conversation. The retrieval and script layer is one focused coding session.
- Everything after phase 3 is configuration or wrapping, which is cheap to generate and cheap to review.

---

## 11. Skills and scripts

The split follows the executor ladder. Reclassified from v0.1: audits are scripts with a thin summarizing skill on top, not skills.

### Scripts, rung 0 and 1, no model

| Script | Purpose |
|---|---|
| `reindex` | Rebuild the index from git |
| `validate-kb` | Front matter schema, id uniqueness, relation targets exist |
| `validate-citations` | Every cited path resolves |
| `assemble-manifest` | Instance plus spokes into `manifest.yaml` |
| `freshness-audit` | Stale, orphaned, unowned docs. Emits JSON and opens issues |
| `run-evals` | Golden set: hit rate, routing accuracy, refusal rate, cost |
| `validate-spoke` | Spoke contract compliance |
| `emit` | Neutral definitions to client formats |
| `doctor` | Preflight and setup completeness check |

### Skills, rung 2 and 3

| Skill | Tier | What it does |
|---|---|---|
| `kb-answer` | small | Search, answer strictly from hits, cite, log a gap on failure |
| `kb-contribute` | small | Turn a chat, PR, or call summary into a front-mattered doc and open a PR |
| `audit-summary` | small | Summarize `freshness-audit` JSON and draft owner messages. The audit itself is a script |
| `kb-onboard-domain` | small | Stamp a new namespace with the standard doc set |
| `sme-route` | none or small | Deterministic first, small model only to disambiguate |
| Role skills | varies | Team-specific, see section 15 |

---

## 12. Agents

### 12.1 Vocabulary

| Term | Definition | Own context | Calls tools | Costs |
|---|---|---|---|---|
| **Script** | Deterministic code | No | N/A | Nothing |
| **Skill** | Fixed sequence of steps | No | Via caller | Caller's tier |
| **Subagent** | Scoped context, tool allowlist, instructions | Yes | Allowlisted | A full context |
| **Persona** | Tone and audience shaping | No | No new authority | Nothing |

A persona never grants access. Partner-facing and internal personas can sit on the same subagent with the same scope.

### 12.2 The router

Job: know what exists, not know everything.

Manifest entry:

```yaml
domains:
  - id: offer-api-platform
    description: Offer API auth, rate limits, error semantics
    keywords: [offer api, auth, rate limit, 429, webhook signature]
    kb_namespace: platform
    repo: github.com/upside/ps-ai-core
    subagent: platform-sme
    model_tier: small
    owner: solutions-architect
    escalate_to: platform-eng
```

Routing procedure:

1. `kb_manifest`, then exact keyword or namespace match. One match means delegate immediately. **No model call.**
2. Multiple matches: `kb_search` across candidates, delegate to the best-scoring domain, state which and why. Small model.
3. No match: broad `kb_search`. Good hits means answer with citations. Small model.
4. No good hits: say you do not know, name the likely owner from the manifest, call `kb_coverage_gap`. **No model needed to refuse.**

Step 4 is the one people skip and the one that makes the system trustworthy.

### 12.3 Subagents

Two families, same definition format. Domain subagents are namespace-scoped and narrow. Role subagents are cross-namespace and skill-scoped.

For a small team where one engineer is strong at build but does not love sales engineering, and where the architect holds the deepest technical context, role subagents are the higher-leverage half. They let someone wear a hat competently without waiting on the person who normally wears it.

`max_hops: 0` on every subagent. Delegation chains are the fastest way to turn a cheap system into an expensive one.

---

## 13. Repo modes

### Spoke mode

A repo contributing knowledge and a domain agent.

```yaml
# spoke.yaml
name: ps-spoke-acme
kb_namespace: partners/acme
owner: nico
core_repo: github.com/upside/ps-ai-core
toolkit_version: ">=0.2"
domains:
  - id: acme-integration
    description: Acme's offer API integration, webhook quirks, rollout history
    keywords: [acme, acme webhooks, acme rollout]
    subagent: acme-sme
    model_tier: small
    escalate_to: partner-success
exports:
  skills: [acme-webhook-debug]
  agents: [acme-sme]
```

Requirements: `spoke.yaml`, a `kb/` directory passing validation, optional `skills/` and `agents/`, and CI calling the toolkit's reusable `validate-spoke` workflow. A spoke ships no retrieval code, no server, no index.

### Attach mode

An existing code repo that wants agents and skills but has no knowledge of its own.

```yaml
# .team-ai.yaml
mode: attach
instance: github.com/upside/ps-ai-core
agents: [build-engineer]
skills: [build-task-runner, kb-answer]
kb_namespaces: [platform, patterns, decisions]
```

That is the entire footprint. Emitted client files are gitignored. This is what most repos need.

---

## 14. The generator

`create-team-ai` runs a guided interview: preflight, team context, capability choices, then three confirmation gates covering strategy, architecture, and the agent plan. Nothing is written until the last gate passes.

Full question bank, branching, and gate summaries live in `create-team-ai-interview-spec.md`.

Commands:

```
team-ai init            # full interview, new instance
team-ai spoke           # generate a spoke
team-ai attach          # attach mode in an existing repo
team-ai doctor          # preflight and setup completeness
team-ai resume          # ask only new or changed questions
team-ai review          # replay the three gates, change nothing
team-ai upgrade         # newer plumbing, leaves kb/ and agents/ alone
team-ai emit --target   # regenerate client files
```

---

## 15. Versatility: catalogs and presets

Nothing team-specific is hardcoded. Every catalog is overridable.

| Catalog | Ships with | Override |
|---|---|---|
| `catalog/namespaces/*.yaml` | partner-solutions, engineering, support, generic | Add a file, or edit after generation |
| `catalog/roles/*.yaml` | architect, sales engineer, build engineer, support engineer, PM | Custom roles get a stub with a TODO block, never a guess |
| `catalog/skills/*.yaml` | Core KB skills plus per-preset extras | Filtered by chosen preset |
| `catalog/personas/*.md` | internal-technical, partner-facing, executive-brief | Freely added |

Resolution order: toolkit defaults, then org-level overrides if an org catalog repo is configured, then the instance's own `catalog/`. Teams contribute presets back to the toolkit by PR, which is how the second and third teams make it better for the fourth.

---

## 16. Evals and quality gates

Write the golden set before the agents. Twenty questions with known answers per namespace, in `evals/golden/`.

```yaml
- id: eval.platform.rate-limit-429
  question: What does a partner do when they start getting 429s?
  expect_namespace: platform
  expect_paths: [kb/platform/rate-limits.md]
  expect_route: platform-sme
  expect_tier_max: small
  must_cite: true
```

CI gates on every KB or agent change:

| Metric | Gate |
|---|---|
| Retrieval hit rate @8 | Expected path present |
| Citation validity | 100 percent of cited paths resolve |
| Routing accuracy | Router picks `expect_route` |
| Refusal on out-of-KB questions | Refuses and logs a gap, does not improvise |
| Front matter validation | All docs pass schema |
| Cost per answer | No regression beyond threshold, no answer exceeds `expect_tier_max` |

The refusal metric matters most. A system that confidently invents details about a partner integration is worse than no system.

---

## 17. Security and access

- Sensitivity filtering happens server-side before results leave, keyed to token scope. Never in a prompt instruction.
- `confidential` documents are excluded from `reader` scope entirely, including from result counts.
- `kb_propose_change` requires `contributor` and always opens a PR. There is no write path to main.
- Secrets never enter the KB. Reference the secret manager path. CI scans for key patterns.
- Synced documents inherit their source system's access assumptions. Prefer linking over copying for anything sensitive.

---

## 18. File trees

The trees below are the **end state**, after phase 7. Phase 1 starts as a single instance repo containing `kb/`, `scripts/`, `schemas/`, `evals/`, and `docs/`, with no `server/` directory and no toolkit repo. Both appear by extraction, not up front.

### 18.1 Toolkit: `team-ai`

```
team-ai/
├── README.md
├── docs/
│   ├── architecture.md
│   └── interview-spec.md
├── bin/cli.ts                        # init | spoke | attach | doctor | resume | review | upgrade | emit
├── src/
│   ├── interview/
│   │   ├── questions.yaml            # single source of truth for both runtimes
│   │   ├── run.ts
│   │   └── gates/{strategy,architecture,agent-plan}.hbs
│   ├── preflight/
│   │   ├── scan.ts                   # existing harness, servers, stores, search
│   │   └── report.ts
│   ├── render/
│   │   ├── render.ts                 # idempotent template application
│   │   └── dry-run.ts
│   └── emit/
│       ├── claude-code.ts
│       ├── mcp-only.ts
│       └── generic.ts
├── server/                           # the KB MCP server, shipped as a package
│   ├── src/
│   │   ├── index.ts
│   │   ├── tools/{search,get,list,manifest,propose-change,freshness,gap}.ts
│   │   ├── adapters/
│   │   │   ├── types.ts
│   │   │   ├── lexical.ts
│   │   │   ├── vector-embedded.ts
│   │   │   ├── vector-pgvector.ts
│   │   │   ├── vector-hosted.ts
│   │   │   ├── graph.ts
│   │   │   └── hybrid.ts
│   │   ├── cache/answer-cache.ts
│   │   ├── budget/guard.ts
│   │   ├── telemetry/cost.ts
│   │   ├── kb/{frontmatter,chunk,loader,citations,relations}.ts
│   │   └── auth/scopes.ts
│   └── test/
├── scripts/
│   ├── reindex.ts
│   ├── validate-kb.ts
│   ├── validate-citations.ts
│   ├── validate-spoke.ts
│   ├── assemble-manifest.ts
│   ├── freshness-audit.ts
│   ├── run-evals.ts
│   └── doctor.ts
├── schemas/
│   ├── frontmatter.schema.json
│   ├── agent.schema.json
│   ├── manifest.schema.json
│   ├── spoke.schema.json
│   └── team-profile.schema.json
├── catalog/
│   ├── namespaces/{partner-solutions,engineering,support,generic}.yaml
│   ├── roles/*.yaml
│   ├── skills/*.yaml
│   └── personas/*.md
├── templates/
│   ├── instance/
│   ├── spoke/
│   └── attach/
└── .github/workflows/
    ├── validate-spoke.reusable.yml
    ├── validate-kb.reusable.yml
    └── evals.reusable.yml
```

### 18.2 Instance: `ps-ai-core`

```
ps-ai-core/
├── README.md
├── SETUP.md
├── team-profile.yaml                 # every interview answer, resumable
├── manifest.yaml                     # assembled routing table
├── index.lock                        # driver, chunking, embedding model + version
├── docs/
│   ├── preflight.md
│   ├── strategy.md
│   ├── architecture.md
│   ├── agent-plan.md
│   └── decisions/adr-0001-scaffold-choices.md
├── kb/
│   ├── operating/{charter,roles,ceremonies}.md
│   ├── platform/{offer-api-overview,auth,webhooks,rate-limits}.md
│   ├── patterns/reference-integration.md
│   ├── playbooks/{partner-onboarding,sales-engineering,escalation}.md
│   ├── partners/<name>/{overview,integration-history,known-issues}.md
│   ├── decisions/
│   └── _backlog/coverage-gaps.md
├── agents/
│   ├── sme.yaml + sme.md
│   ├── platform-sme.yaml + .md
│   └── roles/{architect,sales-engineer,build-engineer}.yaml + .md
├── personas/{internal-technical,partner-facing,executive-brief}.md
├── skills/
│   ├── kb-answer/SKILL.md
│   ├── kb-contribute/SKILL.md
│   ├── audit-summary/SKILL.md
│   ├── sme-route/SKILL.md
│   └── <role skills>/SKILL.md
├── catalog/                          # instance-level overrides only
├── evals/golden/{platform,playbooks,routing}.yaml
├── .mcp.json                         # generated
├── .gitignore                        # ignores emitted client directories
└── .github/workflows/{validate,evals,reindex,freshness}.yml
```

### 18.3 Spoke and attach

```
ps-spoke-acme/                        ps-service-foo/
├── spoke.yaml                        └── .team-ai.yaml
├── kb/*.md
├── agents/acme-sme.yaml + .md
├── skills/acme-webhook-debug/
└── .github/workflows/validate.yml
```

---

## 19. Build sequence

Three of these phases are gates, not schedule items. A gate that never opens is a saved project, not a failure.

| Phase | Output | Size | Gate to start | Done when |
|---|---|---|---|---|
| 0 | Preflight and connector probe, namespaces, front matter schema, 20 golden questions | Days, cheap conversation | Preflight says extend or coexist | Schema agreed, evals written before any code |
| 1 | Instance repo, 20 to 40 real documents, scripts, lexical search. **No server** | ~1 week | Phase 0 done | Your team gets cited answers from a clone |
| 2 | Router, manifest, one domain subagent, skills, routing and refusal evals | ~1 week | Phase 1 answers are useful | Zero-model routing and refusal measurably work |
| 2.5 | **Adversarial review** | ~1 day | Phase 2 done | Four claims tested, see below |
| 3 | Role subagents, cost telemetry | ~1 week | Review passed | Each teammate has used theirs on real work |
| 4 | **Local stdio MCP server** wrapping the same scripts | ~3 to 4 days | A second coding client, or script invocation is the friction | Same evals pass through the server |
| 5 | **Remote MCP server**, token scopes, shared cache | ~1.5 weeks | Two real asks from people who cannot clone a repo | A stakeholder gets a cited answer with no repo |
| 6 | First spoke or first attach | ~1 week | A domain has its own owner or access rules | Contributes with zero core edits |
| 7 | **Toolkit extraction**, generator, interview, catalogs | ~1 week | A second team wants this | They stand up from `SETUP.md` alone |
| 8 | **Index checkpoint** | ~3 days | Golden set exists and lexical is measurably falling short | Vector or graph evaluated. Data decides |

Phases 1 through 3 are the whole system for your own team. Everything after is expansion, and each piece is bought with observed demand.

### Phase 2.5: adversarial review

Run it after phase 2, not before, and give it a fixed target list or it will re-architect for sport. Five claims to attack:

1. The router beats plain search across the whole KB. If it does not, delete the router.
2. Lexical-first is right for this corpus size. Test against the golden set.
3. The cost model holds. Compare measured cost per answer against the claim.
4. The spoke and attach contracts are actually thin. Try one and count the core edits required.
5. The server gates in phases 4 and 5 are set correctly. Argue both that they are too strict and too loose.

Any claim that fails gets simplified out rather than defended.

---

## 20. Open decisions

| # | Decision | Notes |
|---|---|---|
| 1 | Index driver | Deferred to phase 8 by design. The adapter interface protects you either way |
| 2 | Embedding provider, if vector wins | Pin the version in `index.lock`. Switching means a reindex, which is cheap |
| 3 | Confluence and Jira: sync or link | Link first, sync only high-traffic pages |
| 4 | Whether to build a server at all | Not a phase 1 decision anymore. Local stdio is gated on a second client, remote on two real stakeholder asks. Pick the host only when the remote gate opens |
| 5 | Language | TypeScript assumed for MCP ecosystem fit. Python is fine |
| 6 | KB ownership model | Everyone contributes, the `owner` field assigns accountability, the freshness audit makes it real |
| 7 | Org catalog repo | Worth creating once a third team adopts, not before |

---

## 21. Kill criteria

Write these down now, while it is still easy to be honest.

Shut this down or cut it back if, after one quarter:

- Nobody has reviewed the coverage gap log in a month.
- Retrieval hit rate on the golden set is below your agreed threshold and nobody is fixing documents.
- More than a third of the KB is past `review_by` with no owner action.
- The team asks the SME fewer than a handful of real questions a week.
- Measured cost per answer exceeds what the time saved is worth.
- A gate you built ahead of never opened. If the remote server is running and no stakeholder has used it in a month, turn it off rather than maintaining it.

A stale knowledge base that answers confidently is worse than no knowledge base. The audits and the gap log are what keep that from happening, and they only work if someone reads them.
