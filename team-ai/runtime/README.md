# team-ai

A forkable toolkit for standing up a team's AI capability: a knowledge base your
team owns, an SME that routes questions to the right place or refuses, and role
and domain agents that share one set of plumbing.

Clone and build it once, answer about 25 questions, get a working repo.

```
git clone https://github.com/nickejanssen/team-ai.git
cd team-ai
nvm use 22                # Node 22+ all get prebuilt native SQLite bindings
npm ci && npm run build
npm link                  # puts `team-ai` on your PATH
team-ai init              # run from the directory you want to generate into
```

> **Do not run `npx team-ai`.** team-ai is not published to npm, and the
> `team-ai` name on the npm registry belongs to an unrelated package. `npx team-ai`
> would download and execute that package instead. Install from this repository
> as shown above. Full steps are under [Setup](#setup).

**Status: 0.1.0.** First tagged release. The deterministic layer is complete and
tested; the parts that need a running service or a second retrieval driver are
honest stubs, described under [Known limitations](#known-limitations-for-010)
below. Read that section before you build on this.

**Full specs:** [`docs/architecture.md`](docs/architecture.md) ·
[`docs/interview-spec.md`](docs/interview-spec.md) ·
[`docs/quality-bar.md`](docs/quality-bar.md) ·
[`docs/design/2026-08-30-team-ai-framework-design.md`](docs/design/2026-08-30-team-ai-framework-design.md)

---

## Start here: do you actually need this?

Be honest with these before installing anything. The toolkit's preflight asks the
same questions and will tell you to stand down if the answer is no.

### You probably need it if

- New people repeatedly ask the same questions, and the answers live in someone's
  head or in a Slack thread from eight months ago.
- Your team wears several hats, and the person who wears one hat well is a
  bottleneck for everyone else.
- You have knowledge that is specific to your systems and partners, which no
  general model can know.
- People already use AI assistants for work, and they are getting confidently
  wrong answers about your systems.

### You probably do not need it if

- Your org already runs good enterprise search over the same content. Contribute
  documents to it instead. Preflight will detect this and recommend standing down.
- Your knowledge is genuinely small. Under about thirty documents, a
  well-organized folder and a search box beats any of this.
- Nobody will maintain it. This decays into a confidently wrong knowledge base
  within a quarter without an owner.
- The real problem is that the knowledge does not exist yet. Write it first. This
  system retrieves knowledge, it does not create it.

### The honest test

Write down the last ten questions someone on your team asked that took more than
ten minutes to answer. If most of them have answers that exist somewhere in
writing, this helps. If most of them require judgment or do not have written
answers, fix that first.

---

## Why this design

Five decisions do most of the work. Each one is reversible, which is the point.

### 1. Markdown in git is the source of truth. Every index is disposable.

Vector databases and graph databases are indexes here, not stores. You can delete
any index and rebuild it from the same documents in one command.

That single choice makes the hardest decision reversible. Not sure whether you
need vectors or a graph? Ship lexical search, collect real questions, and swap
the driver later with no migration. In 0.1.0 the lexical driver is the only one
implemented; the interface for the others is real and their stubs fail loudly.

It also means humans edit knowledge with the tools they already use: a text
editor, a pull request, code review.

### 2. Cheapest correct executor

For any unit of work, use the lowest rung that produces a correct result:

| Rung | Use for | Cost |
|---|---|---|
| No model | Lookups, cache hits, validation, citation resolution | Nothing |
| Script | Reindex, audits, evals, manifest assembly | Nothing |
| Small model | Retrieve, cite, summarize, format | Low |
| Large model | Synthesis, design judgment, review | High |

Every deterministic operation in this repo is a script that calls no model. The
model-tier work ships as skill templates into your instance, never as framework
code. Every agent declares its tier in config, so tier selection is auditable
rather than improvised.

### 3. Cite or refuse

Every claim about your systems carries a path to the document it came from. When
the knowledge base has no answer, the system is meant to say so, name the likely
owner, and write the question to a gap log. That gap log tells you exactly what
to document next, based on what people actually asked and did not get. The
refusal path is a first-class outcome and is exercised by the eval harness.

### 4. MCP is the portability boundary

Knowledge, schemas, retrieval, scripts, evals, and agent definitions are all
stored in neutral formats. Client-specific files are generated by emitters at
build time (`team-ai emit` targets claude-code, mcp-only, or generic). Changing
client means running a different emitter, not rebuilding.

`team-ai check-agnostic` scans the shipped source against a denylist and fails if
a provider name, model string, or team's proper noun leaks into framework code.

### 5. Infrastructure is earned, not assumed

0.1.0 has no server, no deployment, no auth, and no ops. A git repo and a set of
scripts already give your team ranked search, citations, validation, and audits.
The interview records the gate conditions for a server (a second coding client
for the local stdio server; two real asks from people who cannot clone the repo
for a remote one) rather than triggering a build. The MCP server ships only as a
generated template, off by default.

---

## What you get in 0.1.0

```
THE DETERMINISTIC LAYER — no infrastructure, no model cost
  Knowledge base      markdown in git, schema-validated
  Retrieval           lexical only: SQLite FTS5 ranked keyword search
  18 CLI commands     10 deterministic scripts + 8 interview/generator commands
  Eval harness        hit rate, routing accuracy, refusal, tier ceiling, cost
  Catalogs            4 namespace presets, roles, personas, skills — overridable
  Generator           non-destructive; never clobbers hand-edited files

THE INTERVIEW
  CLI runtime         `team-ai init` — ~25 questions, 3 confirmation gates
  Claude skill        the same question bank, runnable inside a chat client

HONEST BOUNDARIES (see Known limitations)
  Retrieval           only the `lexical` driver is implemented; vector and graph
                      are real interfaces whose stubs throw NotImplementedError,
                      to be evaluated at the phase-8 index checkpoint
  MCP server          a generated template only — not a running service, off by
                      default
  No hosted layer     no remote/hosted server, no auth, no deployment
```

Three repo modes:

| Mode | For | Footprint |
|---|---|---|
| **Instance** | Your team's knowledge base and agents | A full repo |
| **Spoke** | A domain with its own owner or access rules | `spoke.yaml` plus docs |
| **Attach** | An existing code repo that wants agents but no knowledge base | One config file |

---

## Setup

### Install

team-ai is installed from this repository. It is not published to npm, and the
`team-ai` name on npm belongs to an unrelated package, so never use `npx team-ai`.

**Use Node 22 or newer** (22 is pinned in `.nvmrc` as the default). Search uses
`better-sqlite3`, a native SQLite module built on Node-API (N-API), so the
same prebuilt binary works across Node 22, 24, and later majors on Windows,
macOS, and Linux without a C++ toolchain. Only an unsupported platform/arch
combination without a prebuilt binary falls back to compiling from source
(Visual Studio Build Tools with "Desktop development with C++" on Windows,
Xcode Command Line Tools on macOS, `build-essential` and Python on Linux).

```
git clone https://github.com/nickejanssen/team-ai.git
cd team-ai
nvm use 22                # or install Node 22 or newer directly
npm ci
npm run build
npm link                  # optional: puts `team-ai` on your PATH
```

- **Pin a version** by checking out a release tag (see Releases) before `npm ci`.
- **Skip `npm link`** if you prefer, and run the CLI by path instead:
  `node /path/to/team-ai/bin/team-ai.js <command>`.
- **On Windows, clone to a short path.** If the native module does have to
  compile, paths longer than 260 characters make the build fail.

### Use

```
team-ai init              # interview, three confirmation gates, then generate
team-ai doctor            # what is still missing
```

For an existing repo:

```
team-ai adopt             # deterministic: measure the repo, write an adoption plan
```

`adopt` reads the target repo and writes only `adoption-plan.yaml` and
`docs/adoption-plan.md` under its `--out` directory. It never writes into the
repo it measures.

The interview runs preflight first and scans for AI infrastructure you already
have (`.mcp.json`, `.claude/`, `CLAUDE.md`, `AGENTS.md`, a vector store,
connector config). It will tell you to extend it, coexist with it, or stand
down, rather than quietly building a duplicate.

Three gates confirm strategy, architecture, and the agent plan. Nothing is
written to disk until the last one passes. Every answer is saved to
`team-profile.yaml`, so you can `resume`, `review`, or `upgrade` later.

If you do not want a terminal, the same interview runs as a skill inside a chat
client (`skills/scaffold-interview/`). Answer on your phone, hand the resulting
profile to an engineer.

---

## Cost

Running cost is bounded by design: an answer cache keyed to the knowledge base
commit, a hard cap of one delegation hop, a retrieval context budget, and
per-tier limits enforced in config. The eval harness logs cost per answer and a
per-question tier ceiling, and gates both against thresholds.

Build cost is deliberately back-loaded. The deterministic layer plus the
interview is the whole system for your own team. The server and the generator for
a second team, the two largest line items, are gated behind observed demand and a
validated instance.

---

## Known limitations for 0.1.0

Pulled from `docs/dogfood-notes.md`, which records three runs of the framework
against itself and the five bugs those runs fixed.

- **Lexical retrieval only.** The `vector-embedded`, `vector-pgvector`,
  `vector-hosted`, `graph`, and `hybrid` drivers are real classes that satisfy
  the `RetrievalAdapter` interface, but every method throws
  `NotImplementedError` pointing at the phase-8 index checkpoint. Pick `lexical`
  in the interview.
- **The MCP server is a template, not a running service.** `templates/mcp-server/`
  renders a local stdio server on request. There is no hosted or remote server,
  no auth, and no deployment tooling.
- **`resume` is minimal.** It re-opens a saved interview and asks only newly
  relevant questions; it does not deeply diff a changed question bank.
- **Preflight's skill scan misses `.agents/skills/`.** It checks `skills/` and
  `.claude/skills/` only, so an SME implemented as a skill in `.agents/skills/`
  reads as "router / SME agent: none".
- **A few Act 0 questions are asked unconditionally.** `pre.overlap` and
  `pre.probe_result` fire with prompts that assume a positive detection even when
  preflight found nothing; `ask_if` is not yet wired to preflight-derived facts.
  "Decide later" / "continue" are safe answers.
- **Custom domains and free-text namespaces generate TODO stubs, never guesses.**
  A custom domain agent gets a `description: "TODO: ..."` and empty keywords that
  the operator must fill in before the domain agent is useful. This is
  intentional (quality-bar Q11) but means the generated instance is not
  turn-key for custom domains.

---

## Contributing

Namespace layouts, role definitions, skills, and personas all live in `catalog/`
and are overridable per org and per instance. See
[`CONTRIBUTING.md`](CONTRIBUTING.md) and
[`docs/quality-bar.md`](docs/quality-bar.md) — the 17 questions the framework is
judged against. If your team builds a preset that works, send it back.
