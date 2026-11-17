# Quality bar

**Status:** authoritative · **Last updated:** 2026-08-31 · **Canonical path:** `docs/quality-bar.md`

These are the seventeen questions the `team-ai` framework is judged against. Each
question below carries the answer the architecture actually gives and the real
files in this repo where that answer is enforced. Every interview question's
`why` text in `src/interview/questions.yaml` cites one of these anchors.

> **Sixteen vs seventeen.** The design docs sometimes say "sixteen questions".
> There are 17. The seventeenth — detect existing AI infrastructure and avoid
> duplicating it — was added later. This file is authoritative.

How to read a section: **Question** is the bar. **The answer the architecture
gives** is what the built system does about it, in plain terms. **Where it's
enforced** lists the files that make the answer true — if you change one, re-read
the answer and confirm it still holds.

---

<a id="q1"></a>

## Q1. Can a team choose their KB substrate and index?

**Question.** Can a team choose their knowledge-base substrate and its index?

**The answer the architecture gives.** The interview's `kb.substrate` question
offers Markdown-in-git or a database as the source of truth, and
`arch.index_driver` picks the retrieval driver independently of that choice.
Every driver implements one interface, so the index is a reversible config
choice rather than a migration — only `lexical` is built, and the other five
drivers throw a documented `NotImplementedError` that points at the phase-8
checkpoint. Swapping the index later rebuilds from the same documents with no
data loss.

**Where it's enforced:** `src/retrieval/factory.ts`, `src/retrieval/index-lock.ts`, `src/retrieval/stubs.ts`, `src/retrieval/not-implemented.ts`, `src/interview/questions.yaml`

---

<a id="q2"></a>

## Q2. Are agents, personas, and SMEs defined in a readable, editable format?

**Question.** Are agents, personas, and SMEs defined in a format a human can read and edit?

**The answer the architecture gives.** Agents are YAML validated against
`schemas/agent.schema.json`; personas are plain Markdown; both are generated
into the instance as files a human edits and reviews through a pull request.
No part of an agent's identity, tier, or scope lives in framework code — it all
flows from catalog presets into generated entity files.

**Where it's enforced:** `schemas/agent.schema.json`, `templates/instance/agents/`, `catalog/roles/`, `catalog/personas/`

---

<a id="q3"></a>

## Q3. Can it set up agents in repos that have no knowledge base of their own?

**Question.** Can it set agents up in a repo that has no knowledge base of its own?

**The answer the architecture gives.** `team-ai attach` wires an existing repo
to an instance: it drops in agent files, skill files, and a citation contract
without creating a `kb/` tree in that repo. The `mode` question routes
new-instance versus spoke versus attach up front, so the attach path never walks
the knowledge-model act.

**Where it's enforced:** `templates/attach/`, `src/generator/attach.ts`, `src/interview/questions.yaml`

---

<a id="q4"></a>

## Q4. Is the repo topology right, and when does it split?

**Question.** Is the repository topology right, and is the split point defined?

**The answer the architecture gives.** `arch.topology` defaults to a toolkit
plus a separate instance repo, and the spoke and attach contract files are
generated from day one, so extracting the toolkit later is a move rather than a
rewrite. `team.size` gates role subagents: teams of 1–3 get domain agents only,
because that is the honest choice at that size.

**Where it's enforced:** `src/generator/init.ts`, `src/generator/spoke.ts`, `templates/spoke/`, `schemas/spoke.schema.json`

---

<a id="q5"></a>

## Q5. Has the design been adversarially reviewed?

**Question.** Has the design been through an adversarial review?

**The answer the architecture gives.** Phase 2.5 of the build sequence is a
dedicated adversarial review with a fixed five-claim target list: router value,
lexical-first fit, the cost model, spoke and attach contract thinness, and
whether the server gates are set correctly. It runs after phase 2, not before,
and any claim that fails is simplified out rather than defended.

**Where it's enforced:** `docs/architecture.md` section 19 (Phase 2.5), `docs/design/2026-08-30-team-ai-framework-design.md`

---

<a id="q6"></a>

## Q6. Is running cost optimized, and is it measured?

**Question.** Is running cost optimized, and is it actually measured?

**The answer the architecture gives.** The eval harness measures cost per answer
and a per-question tier ceiling on every KB or agent change, gated against
thresholds in `DEFAULT_GATES`. The `arch.model_tiers` question sets the routing
policy and prints the tradeoff once when a team selects "no constraints".

**Where it's enforced:** `src/evals/metrics.ts`, `src/evals/run.ts`, `src/commands/run-evals.ts`, `evals/gates.yaml`

---

<a id="q7"></a>

## Q7. Does it adapt to teams with different roles, repos, and needs?

**Question.** Does it adapt to teams that have different roles, repos, and needs?

**The answer the architecture gives.** Namespaces, roles, skills, and personas
all come from catalog presets resolved in the order toolkit, then org catalog,
then instance. Custom roles, domains, and namespaces generate a stub with a TODO
block, never a guess. Selecting external consumers in `team.consumers` forces
sensitivity tiers and the read-only scope on.

**Where it's enforced:** `src/catalog/resolve.ts`, `src/catalog/stub.ts`, `catalog/namespaces/`, `catalog/roles/`

---

<a id="q8"></a>

## Q8. Is setup easy, and does it tell you what is still missing?

**Question.** Is setup easy, and does the tool tell you what is still missing?

**The answer the architecture gives.** One command and roughly 25 questions
produce a working repo, and `agents.seed` seeds five starter documents so the
first search returns a real, cited answer. `team-ai doctor` reports what is
incomplete — missing manifest, empty namespaces, an unbuilt index, no golden
set — so the gaps are visible rather than silent.

**Where it's enforced:** `src/commands/doctor.ts`, `src/doctor/checks.ts`

---

<a id="q9"></a>

## Q9. Does it explain why this design and how to tell if you need it?

**Question.** Does it explain why this design exists and how to tell whether you need it?

**The answer the architecture gives.** `docs/README.source.md` opens with an
honest "do you actually need this" section, and preflight reaches the same
stand-down verdict mechanically instead of only in prose. This file records the
answer the architecture gives for every quality-bar line, and the interview's
`why` text traces each question back to one of them.

**Where it's enforced:** `docs/README.source.md`, `docs/quality-bar.md`, `docs/architecture.md`

---

<a id="q10"></a>

## Q10. Is the phasing efficient, and does it avoid building ahead of demand?

**Question.** Is the phasing efficient, and does it avoid building ahead of demand?

**The answer the architecture gives.** The MCP server is demand-gated into two
separate phases — local stdio on a second coding client, remote on two real asks
from people who cannot clone a repo — and the interview records those gate
conditions rather than triggering a build. Phases 1–3 are the whole system for
one team; everything after is expansion bought with observed demand.

**Where it's enforced:** `docs/architecture.md` section 19, `src/interview/questions.yaml`

---

<a id="q11"></a>

## Q11. Is the architecture itself powerful and cheap, or just cheap?

**Question.** Is the architecture itself both powerful and cheap, or only cheap?

**The answer the architecture gives.** Lexical retrieval is SQLite FTS5 — ranked
keyword search with zero infrastructure to run — and the adapter interface keeps
vector or graph a later, data-driven decision made against the golden set. Graph
is only offered when a team can name two genuinely relational questions that
keyword and vector search cannot answer.

**Where it's enforced:** `src/retrieval/lexical.ts`, `src/retrieval/not-implemented.ts`, `src/interview/questions.yaml`

---

<a id="q12"></a>

## Q12. Does it mix deterministic and non-deterministic work correctly?

**Question.** Does it put deterministic work in scripts and non-deterministic work in models?

**The answer the architecture gives.** The `src/commands` operations are pure
deterministic scripts that call no models; the only model-tier work ships as
`SKILL.md` templates into the instance, never as framework code. The
`kb.sources_strategy` question keeps linking the default, so importing content —
which is a sync pipeline you then maintain — is chosen deliberately per source.

**Where it's enforced:** `src/commands/`, `templates/instance/skills/`, `docs/design/2026-08-30-team-ai-framework-design.md` section 3

---

<a id="q13"></a>

## Q13. Does it use scripts wherever a script would do?

**Question.** Does it use a script wherever a script would do the job?

**The answer the architecture gives.** Every repeatable operation — reindex,
validate-kb, validate-citations, validate-spoke, assemble-manifest,
freshness-audit, run-evals, doctor, search, reconcile — is a deterministic
command rather than a prompt, and CI runs them directly.

**Where it's enforced:** `src/commands/`, `.github/workflows/ci.yml`

---

<a id="q14"></a>

## Q14. Is the result easier to understand than what it replaces?

**Question.** Is the generated result easier to understand than what it replaces?

**The answer the architecture gives.** Generation is non-destructive: `reconcile`
diffs template output against what a human has already edited and never clobbers
hand-written content. The output is plain Markdown, YAML, and small scripts —
diffable and reviewable in a pull request, not a black box.

**Where it's enforced:** `src/generator/reconcile.ts`, `src/generator/render.ts`

---

<a id="q15"></a>

## Q15. Is it model and platform agnostic?

**Question.** Is it agnostic to the model and the platform it runs on?

**The answer the architecture gives.** Framework code calls no models and
hardcodes no provider name, model string, or team name. `team-ai check-agnostic`
scans `src/`, `schemas/`, `catalog/`, and `templates/` against a shipped
denylist, and the emitters target claude-code, mcp-only, or generic surfaces
from the same team profile.

**Where it's enforced:** `src/emit/`, `src/commands/check-agnostic.ts`, `agnostic-denylist.txt`

---

<a id="q16"></a>

## Q16. Does it select the minimum sufficient model per task?

**Question.** Does it pick the smallest model that clears the bar for each task?

**The answer the architecture gives.** Every agent carries a `model_tier`
(`none`, `small`, or `large`) validated by schema, the router resolves
zero-model and small-model routes before any large-model call, and an eval fails
when an answer exceeds its `expect_tier_max`. The `arch.cache` question keeps the
answer cache on by default so repeat and near-repeat questions cost nothing.

**Where it's enforced:** `schemas/agent.schema.json`, `src/evals/run.ts`, `src/interview/questions.yaml`

---

<a id="q17"></a>

## Q17. Does it detect existing AI infrastructure and avoid duplicating it?

**Question.** Does it detect AI infrastructure a team already has and avoid standing up a parallel one?

**The answer the architecture gives.** Preflight scans for an existing harness
(`.mcp.json`, `.claude/`, `CLAUDE.md`, `AGENTS.md`, vector-store environment
variables, connector config), and a connector probe prepares — but never runs —
five golden questions for the operator to score. The `pre.assessment`,
`pre.overlap`, and `pre.probe_result` questions then steer toward extend,
coexist, or stand down, and standing down is treated as a successful outcome.

**Where it's enforced:** `src/interview/preflight.ts`, `src/interview/preflight-signals.ts`, `src/interview/preflight-report.ts`

---

## Contributor checklist

Before merging, confirm your change keeps every answer above honest. Walk the
sections your change touches and check that the "Where it's enforced" files still
enforce what the answer claims. The PR template asks which of the 17 lines you
touched — fill that in.
