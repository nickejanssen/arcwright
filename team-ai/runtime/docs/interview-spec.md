# `create-team-ai` Interview Spec

**Version:** 0.3
**Companions:** `team-ai-scaffold-architecture.md`, `README.md`
**Purpose:** Define the guided interview the toolkit runs, so a team can stand up their AI capability by answering questions instead of reading a spec.

**What changed from 0.2:** the hosting question no longer assumes a server. It offers "no server" as the default and treats local and remote as separately gated later decisions. Preflight adds a connector probe that tests whether an existing repo connector already covers the chat-app case.

**What changed from 0.1:** Act 0 preflight for existing AI infrastructure, with a stand-down outcome; mode selection up front; cost and model tier questions; catalog override questions; `doctor` command; seed knowledge so the first search returns something real.

---

## 1. Principles

1. **One question bank, two runtimes.** The same `questions.yaml` drives the CLI prompts and the in-Claude skill. Never maintain two copies.
2. **Multiple choice by default.** Free text only for names and one-line descriptions.
3. **"Decide later" is a real answer.** It records a TODO, applies a safe default, and moves on. Nothing should block on an unmade decision.
4. **"Recommend one" is a real answer.** The toolkit prints the tradeoff, picks, and says why.
5. **Answers are data.** Everything lands in `team-profile.yaml`, which is committed. Re-running reads it and only asks what changed.
6. **Preflight before questions.** Never ask someone to design something the org already has.
7. **Three gates, not one.** Strategy, architecture, and agent plan each get a confirm step. Nothing is written until the last gate passes.
8. **Ask only what applies.** Every question has an `ask_if`. Answering "no external users" should never produce sensitivity tier questions.
9. **Defaults must be visible.** Anything taken by defer or recommend appears in the deferred list at gate 1 and in `docs/architecture.md`, so the team knows what it did not actually choose.

---

## 2. Flow

```
Act 0  Preflight              automatic scan, 1 to 2 questions
       ── possible early exit: STAND DOWN ──
Act 1  Mode and team context  7 questions
Act 2  Knowledge model        6 questions
       ── GATE 1: confirm strategy ──────────► docs/strategy.md
Act 3  Architecture and cost  7 questions
       ── GATE 2: confirm architecture ──────► docs/architecture.md
Act 4  Agents and skills      6 questions
       ── GATE 3: confirm agent plan ────────► docs/agent-plan.md
Act 5  Dry run, write, doctor
```

Typical run: about 25 questions, most one tap. Roughly 15 minutes on a recommend-heavy path.

Controls at any point: `back`, `skip` (defer), `why` (rationale for the question), `save` (exit and resume later).

---

## 3. Question bank schema

```yaml
- id: kb.substrate
  act: 2
  type: single_select            # single_select | multi_select | text | confirm | rank
  prompt: Where should the knowledge itself live?
  why: >
    This is the storage decision. It sets what kinds of questions the
    system answers well and how much maintenance it costs.
  options:
    - value: md-git
      label: Markdown in git, index derived from it
      tradeoff: >
        Simplest. Diffable, reviewable, humans can edit directly. Any
        index can be rebuilt or swapped later with no migration.
      implies: { index_driver_default: lexical, write_back: pr-only }
    - value: db-native
      label: A database as the source of truth
      tradeoff: >
        Only worth it if your knowledge is already structured records
        rather than documents. You lose git history, review, and human
        editing, and index changes become migrations.
      implies: { warn: true }
  default: md-git
  recommend: md-git
  recommend_why: >
    Keep documents as the source of truth and treat every index as
    disposable. Lexical, vector, and graph all become reversible
    config choices instead of migrations.
  allow_defer: true
  ask_if: always
```

Field notes:

- `implies` pre-fills later answers, which the user can still override.
- `warn: true` surfaces the downside once, then respects the choice.
- `recommend_why` always prints when "recommend one" fires, so nobody is silently steered.

---

## 4. Act 0: Preflight

Runs automatically before any question. Scans for existing AI infrastructure per architecture section 4.

Output, printed before anything else:

```
PREFLIGHT

Found
  ✓ MCP servers configured: github, jira, confluence, aws
  ✓ Agent config present: CLAUDE.md at repo root
  ✗ No existing vector store detected
  ? Possible org-wide search: Confluence AI is enabled on your space

Assessment: EXTEND
  A harness already exists. This will register alongside it and adopt
  CLAUDE.md rather than creating a parallel config.

Overlap worth checking: Confluence AI already searches the same pages
you listed as sources. If your team's questions are mostly "where is
the doc", you may not need an index at all.
```

### Connector probe

If a repo or drive connector is already configured, preflight runs five golden questions against a small structured document set through it, before asking anything:

```
CONNECTOR PROBE

  Ran 5 sample questions through your existing GitHub connector.
  3 of 5 returned a usable answer with a findable source.

  Meaning: for "where is the doc about X", what you have may be enough.
  What you would still be missing: ranked retrieval, namespace scoping,
  enforced citations, per-query sensitivity filtering, shared caching,
  cost telemetry.
```

| id | Prompt | Type |
|---|---|---|
| `pre.assessment` | Confirm how to proceed | single: extend, coexist, stand down, explain the difference |
| `pre.overlap` | Existing search already covers some of this. What do you want? | single: build anyway, contribute to it and skip the index, decide later. Asked only when overlap is detected |
| `pre.probe_result` | The probe answered most sample questions. Continue? | single: continue, scale back to documents only, stop here. Asked only when the probe scores well |

**Stand down is a real outcome.** If chosen, the toolkit generates only the manifest, agents, personas, and skills layers, wires them to the existing search, and skips the KB server entirely. That is a legitimate and much cheaper success.

---

## 5. Act 1: Mode and team context

| id | Prompt | Type | Options |
|---|---|---|---|
| `mode` | What are you setting up? | single | New team instance, a spoke for an existing instance, attach an existing repo, not sure |
| `team.name` | What is the team called? | text | |
| `team.mission` | One line: what does this team do? | text | |
| `team.size` | How many people? | single | 1-3, 4-8, 9-20, 20+ |
| `team.surfaces` | Where will people use this? | multi | Coding agent, chat apps, read-only stakeholders, other MCP clients |
| `team.sources` | Where does knowledge live today? | multi | Confluence, Jira, GitHub, Drive, Notion, Slack, mostly in people's heads |
| `team.consumers` | Who asks this system questions? | multi | Engineers, customer or partner facing, leadership, people outside the company |

Branching:

- `mode` of spoke or attach skips Acts 2 and 3 entirely and jumps to a short version of Act 4. Attaching a repo should take under two minutes.
- External consumers force sensitivity tiers on and enable the read-only scope.
- Confluence or Jira in sources triggers the sync-versus-link question.
- Size 1-3 suppresses role subagent questions and suggests domain agents only.

---

## 6. Act 2: Knowledge model

| id | Prompt | Type | Notes |
|---|---|---|---|
| `kb.substrate` | Where should the knowledge live? | single | Section 3 above |
| `kb.namespaces` | Pick a starting layout | single | Presets: partner solutions, engineering, support, generic, custom |
| `kb.catalog_override` | Want to customize roles and skills offered? | single | Use the preset, review and edit now, point at an org catalog repo |
| `kb.sources_strategy` | How do we treat existing systems? | single | Link only, sync read-only, import and own, mixed |
| `kb.sensitivity` | Do you need sensitivity tiers? | single | Three standard tiers, custom tiers, none. Forced on if external consumers |
| `kb.write_back` | Can agents change the knowledge base? | single | Propose via PR (recommended), direct write with review, read only |

### The graph question, handled honestly

Graph is offered as an index in Act 3, not as a store here. If someone picks it there, one follow-up fires first:

> Name two questions you want answered that keyword or vector search cannot handle.

Ordinary lookups get an honest "defer this to the phase 7 checkpoint." Genuinely relational answers, such as which partners depend on a given endpoint or what breaks if auth changes, get accepted and turn on the `relations` block in front matter:

```yaml
relations:
  depends_on: [ps.platform.auth]
  used_by_partner: [acme, globex]
  owned_by_role: architect
```

The toolkit turns that block on whenever graph is chosen **or deferred**, because filling it from day one is cheap and it is the only prerequisite for adding a graph index later without a migration.

---

## 7. Gate 1: Confirm strategy

One page, nothing written yet.

```
STRATEGY SUMMARY

Preflight     Extend an existing harness (CLAUDE.md, 4 MCP servers)
Team          Partner Solutions, 4 people
Mission       Partners integrate our offer API to reach their users
Surfaces      Coding agent, chat apps, read-only stakeholders
Knowledge     Markdown in git, lexical index now
Namespaces    operating, platform, patterns, partners, playbooks, decisions
Catalog       Partner solutions preset, roles reviewed and edited
Sources       Confluence and Jira linked, not synced
Sensitivity   3 tiers, external readers get internal and below
Write-back    Agents propose via PR, humans merge

WHAT THIS MEANS
  Cited answers from documents your team owns and edits.
  Nothing auto-publishes. Every choice above is reversible except
  namespace names, which are cheap to rename but touch every doc id.

DEFERRED (defaults applied, revisit later)
  Index driver     → lexical, revisit at phase 7 with eval data
  Graph index      → off, relations block enabled so it stays possible

  [confirm]  [edit an answer]  [start over]  [save and exit]
```

---

## 8. Act 3: Architecture and cost

| id | Prompt | Type | Options |
|---|---|---|---|
| `arch.index_driver` | Which retrieval driver first? | single | Lexical, vector embedded, vector on Postgres, vector hosted, graph, decide later |
| `arch.hosting` | Do you need a server? | single | **No server for now (recommended)**, local stdio, remote. Selecting apps or stakeholders in Act 1 does not force this, it records the gate condition instead |
| `arch.language` | TypeScript or Python? | single | |
| `arch.ci` | CI provider? | single | GitHub Actions, other, none for now |
| `arch.topology` | Repo layout? | single | Toolkit plus instance (recommended), single repo for now |
| `arch.model_tiers` | How aggressive on cost? | single | Strict (prefer no model, then small), balanced, no constraints |
| `arch.cache` | Enable the answer cache? | single | Yes (recommended), no |

Guardrails:

- `no server for now` is the default even when chat apps and stakeholders were selected. Those audiences record **gate conditions** in `docs/architecture.md` rather than triggering a build: local stdio when a second coding client appears, remote after two real asks from people who cannot clone a repo. The toolkit prints both gates so the deferral is deliberate rather than forgotten.
- Choosing `remote` up front prints one warning: it is the largest single line item in the plan, and it is being bought before the demand is observed.
- `decide later` on the driver sets lexical and records the phase 8 checkpoint. Not a blocker.
- `none for now` on CI prints one warning that eval gates and freshness audits will not run, then respects it.
- `single repo for now` still generates the spoke and attach contract files, so splitting later is a move, not a rewrite.
- `no constraints` on tiers prints the tradeoff once: unbounded tier selection is the single largest driver of running cost.

---

## 9. Gate 2: Confirm architecture

Prints the layered diagram with the chosen driver and hosting filled in, the collapsed file tree, the MCP tool list with per-surface scopes, and a cost preview:

```
COST PREVIEW (estimated, per 100 questions)

  Cache hits                     ~40   no model
  Deterministic route + refuse   ~15   no model
  Retrieve and cite              ~40   small model
  Synthesis and review           ~5    large model

  Portability: nothing below the tool boundary is vendor-specific.
  Switching model provider = change embedding config + emitter target.

  Infrastructure this build: none. Scripts and a repo.
  Gate: local stdio server    when a second coding client appears
  Gate: remote server         after 2 asks from non-repo users

  [confirm]  [edit an answer]  [see full file tree]  [back to strategy]
```

The mix shown is illustrative until phase 4 telemetry replaces it with measured numbers.

---

## 10. Act 4: Agents, subagents, personas, skills

| id | Prompt | Type | Notes |
|---|---|---|---|
| `agents.roles` | Which role hats does this team wear? | multi + custom | Suppressed for teams of 1-3. Each becomes a role subagent |
| `agents.domains` | Name 1 to 3 starting domains | text list | Each becomes a manifest entry and a domain subagent |
| `agents.personas` | Which audiences do you write for? | multi | Internal technical, partner or customer facing, executive brief, custom |
| `agents.skills` | Pick starting skills | multi from catalog | Core KB skills pre-checked, cannot be unchecked |
| `agents.strictness` | What happens when the KB has no answer? | single | Refuse and log a gap (recommended), answer from general knowledge but label it, answer freely |
| `agents.seed` | Seed the KB so the first search works? | single | Yes with 5 starter docs from the preset, no, I will write my own |

Notes:

- Anything other than refuse prints the tradeoff once: unlabeled improvisation about your own systems is the main way these setups lose trust.
- The skills catalog is filtered by the chosen preset. A support team is not offered an integration review skill.
- Custom roles and domains generate a stub with a TODO block, never a guess.
- Seeding matters more than it sounds. An empty KB on day one is how these die in week one.

---

## 11. Gate 3: Confirm the agent plan

The most important gate. Exactly what will exist, what each thing can do, and what it costs.

```
AGENT PLAN

ROUTER
  sme                  tier: none → small on ambiguity only
                       tools: kb_manifest, kb_search, kb_coverage_gap
                       refuses and logs a gap when uncited

DOMAIN SUBAGENTS                                    tier   hops
  platform-sme         ns: platform, patterns       small   0
  acme-sme             ns: partners/acme, platform  small   0

ROLE SUBAGENTS
  architect            ns: all      skills: integration-review    large  0
  sales-engineer       ns: all      skills: discovery-prep        small  0
  build-engineer       ns: platform, patterns, decisions          small  0

PERSONAS  (tone only, grant no access)
  internal-technical, partner-facing, executive-brief

SKILLS      core: kb-answer, kb-contribute, audit-summary, sme-route
            team: discovery-prep, integration-review, task-runner,
                  partner-escalation

SCRIPTS (no model, no cost)
  reindex, validate-kb, validate-citations, freshness-audit,
  assemble-manifest, run-evals, validate-spoke, emit, doctor

EVALS   20 golden questions stubbed across 3 namespaces.
        Fill in expected answers before the CI gate turns on.

  [confirm and write]  [edit an answer]  [see a sample agent file]
```

---

## 12. Act 5: Dry run, write, doctor

1. Print the full file tree with counts of files created and files skipped as already present.
2. `--dry-run` stops here.
3. Otherwise write, then run `doctor` immediately and print what is still missing:

```
DOCTOR

  ✓ Repo structure valid
  ✓ 5 seed documents pass front matter validation
  ✓ Index built, 23 chunks
  ✓ Manifest assembled, 3 domains
  ✗ MCP token for the reader scope not minted
  ✗ Connector not registered in the chat apps
  ✗ 20 golden eval answers not yet filled in

  3 items remaining. See SETUP.md.
```

`SETUP.md` contains only what a script cannot do: create and push the repos, mint tokens per scope, register the connector, add the marketplace, fill in the eval answers.

---

## 13. Outputs

| File | Contents |
|---|---|
| `team-profile.yaml` | Every answer, timestamped, with `deferred: []` |
| `docs/preflight.md` | What was found, which assessment applied, and why |
| `docs/strategy.md` | Gate 1 summary in prose |
| `docs/architecture.md` | Gate 2 output, deferred decisions, and their checkpoints |
| `docs/agent-plan.md` | Gate 3 table, plus the tool scope and tier of every agent |
| `docs/decisions/adr-0001-scaffold-choices.md` | Choices with tradeoffs, so the next person understands why |
| `index.lock` | Driver, chunking config, embedding model and version if applicable |

Re-run commands:

```
team-ai resume     # only new or changed questions
team-ai review     # replay the three gates, change nothing
team-ai upgrade    # newer plumbing, leaves kb/ and agents/ alone
team-ai doctor     # re-check preflight and setup completeness
```

---

## 14. Running it inside Claude instead of a terminal

Same question bank, different renderer. A `scaffold-interview` skill:

1. Reads `questions.yaml`.
2. Asks each act using the interactive question UI, at most 3 questions per turn so it stays readable on a phone.
3. Renders the three gates as text summaries with confirm options.
4. Writes `team-profile.yaml` and hands off to the CLI, or writes the tree directly when it has filesystem access.

This matters for adoption. An EM on another team can complete the interview from a phone and hand the profile to an engineer to execute.

---

## 15. Question bank file layout

```
team-ai/src/interview/
├── questions.yaml              # single source of truth
├── run.ts
├── gates/
│   ├── strategy.hbs
│   ├── architecture.hbs
│   └── agent-plan.hbs
└── ../../catalog/              # presets, roles, skills, personas
```

Catalog resolution order: toolkit defaults, then an org catalog repo if configured, then the instance's own `catalog/`.

---

## 16. What to watch for

- **Interview drift.** Every question needs a real branching consequence. If an answer changes nothing generated, delete the question.
- **Gates nobody reads.** One screen each. If a summary needs scrolling, it is doing too much.
- **Defaults doing the deciding.** Deferred and recommended answers must always surface in the deferred list and in `docs/architecture.md`.
- **Preflight being skipped.** The stand-down outcome is the most valuable one the toolkit can produce, and it only fires if preflight actually runs.
