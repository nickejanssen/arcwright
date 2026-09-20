---
id: engineeringpractice.superpowers.specs.2026-09-20-team-ai-agent-architecture-phase-b-design
namespace: engineering-practice
title: team-ai Agent Architecture Phase B Design
owner: Nico Janssen
status: active
review_by: "2027-03-20"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# team-ai Agent Architecture Phase B Design

> Current version: v3.0
> Last updated: 2026-09-20
> Status: Approved and built. Amended twice during implementation by measurement — see *M6* and *M7*. Frozen at Phase B close.
> Canonical path: `docs/superpowers/specs/2026-09-20-team-ai-agent-architecture-phase-b-design.md`
> Parent spec: `docs/specs/0089-team-ai-agent-architecture.md` (v1.5)

---

# Summary

Spec 0089 describes Phase B as three enforcement skills, four hooks, a
workflows manifest section, and a golden-question eval gate. Measurement
against the real repositories shows that list is organised by artifact type
rather than by dependency, and that it defers the one thing everything else
depends on.

**The binding constraint is findability.** On the committed 37-question set the
correct source document reaches the top eight results 48.5% of the time,
against a target of 80%. Phase B first removes a scoring defect that made every
score meaningless, re-measures, and only then decides whether semantic
retrieval is needed — and for which domains.

Version 2.0 replaced v1.0, which treated routing as the problem and deferred
retrieval to Phase C. Version 2.1 records what implementation measured: the
scoring fix does not by itself improve retrieval, and refusal is not achievable
from term statistics at all. See *M6*.

---

# Measurements

All taken on 2026-09-20 against Arcwright `main` and team-ai v0.5.0.

## M1 — Lexical scoring is measuring common-word mass, not relevance

| query | top score |
|---|---|
| "How many weeks of paid parental leave does the company offer?" | 0.835 |
| "parental leave" — the same question's distinctive terms only | 0.750 |
| "how does the of a to and it" — pure stopwords, no meaning | **0.731** |

A query with no meaning scores 0.731, and padding a real question with
meaningless words *raises* its score.

**Cause.** `sanitizeQuery` in the lexical adapter joins every query token with
`OR`, so a chunk matching any common word matches, and BM25 accumulates score
across all matched terms. The transform `score = rel / (rel + 3)` then
saturates toward 1 as that accumulation grows, compressing everything into the
0.7–0.9 band. The source comment records that the constant was tuned against a
fixture knowledge base with short queries; it was never exercised against long
natural-language questions over a ~966,000-token corpus.

**This one defect explains three symptoms** previously treated as separate
problems: refusal cannot fire because nothing scores low; hit rate is poor
because ranking follows common-word mass; routing accuracy is zero because it
routes on a top hit that is noise.

## M2 — The eval harness reports zero today

An 11-question probe set written to the founder's generation rules
(paraphrased; two out-of-scope questions whose correct outcome is refusal),
replayed through `run-evals`:

| metric | value | gate | result |
|---|---|---|---|
| hitRate | 22.2% | 80% | FAIL |
| routingAccuracy | 0.0% | 80% | FAIL |
| refusalRate | 0.0% | 100% | FAIL |
| namespaceAccuracy | 18.2% | 80% | FAIL |
| citationValidity | 100% | 100% | PASS |

**hitRate is the headline, not routingAccuracy.** Hit rate measures whether the
correct document can be found at all. Everything downstream — routing,
refusal, citation, the agents themselves — is bounded by it.

Lexical search also collapses under paraphrase, which is the behaviour the
generation rules were designed to expose:

| phrasing of the same question | rank of the correct document |
|---|---|
| using the document's own distinctive terms | 5th |
| paraphrased, those terms avoided | not in the top 8 |

## M3 — The scored retrieval path is not the delivery path

Emitted agents carry `tools: Read, Grep, Glob` and a procedure telling them to
grep the knowledge base for their namespace marker and read what they find.
The ranked index — 447 documents, 4,343 chunks, rebuilt in 5.4 seconds — is
used by `run-evals` and by nothing else.

So the agents that actually answer questions use grep, which is strictly worse
than the index under paraphrase.

## M4 — 43% of every emitted agent is instructions to call tools that do not exist

Each emitted agent ends with an `## Original instructions` block directing it
to call `kb_manifest`, `kb_search` and `kb_coverage_gap` — none of which exist,
because D6 chose built-in search over an MCP server — immediately after a line
stating those names are unavailable.

Across the 17 agents: 20,831 characters, of which 8,993 (43%, ~2,250 tokens)
are that dead block. It costs tokens on every invocation and invites fabricated
tool calls.

## M5 — Corpus mass is concentrated in three domains

| namespace | docs | tokens |
|---|---|---|
| engineering-practice | 181 | 609,458 |
| product-roadmap | 213 | 255,722 |
| nightcap | 35 | 49,854 |
| monster-rpg | 1 | 13,698 |
| arc-execution | 5 | 10,845 |
| playtest-ops | 3 | 7,839 |
| developer-api | 1 | 3,653 |
| session-runtime | 2 | 3,398 |
| model-routing | 2 | 3,139 |
| character-behavior | 1 | 2,724 |
| knowledge-graph | 1 | 1,926 |
| daily-case | 1 | 1,835 |
| safety | 1 | 1,722 |
| nightcap-couch-race | 1 | 232 |
| **total** | **447** | **966,050** |

Three domains hold **94.7%** of the corpus. The other eleven hold 51,016
tokens between them — 5.3%.

The architecture is inverted at both ends. `engineering-practice-sme` owns
609,458 tokens and is told to "search only your documents"; it cannot read them
and grep fails on paraphrase. `knowledge-graph-sme` owns 1,926 tokens — less
than the cost of searching — yet still greps, reads, then paraphrases.

Spec and plan creation draws on `docs/specs/` and `docs/roadmap/`, which are
precisely the two largest and worst-served domains.

## M6 — Amendment: the lexical fix does not improve retrieval, and refusal is not lexically achievable

Added 2026-09-20 during implementation, against the committed 37-question set.
Two findings overturn parts of this document; they are recorded here rather
than quietly edited in.

**The stopword fix as specified was a regression.**

| metric | baseline | stopwords filtered out | stopwords used only as a gate |
|---|---|---|---|
| hitRate | 48.5% | 42.4% | 48.5% |
| routingAccuracy | 24.3% | 16.2% | 24.3% |
| namespaceAccuracy | 35.1% | 27.0% | 35.1% |

BM25 already discounts common terms by inverse document frequency, so removing
them discards disambiguating context and buys nothing. The corrected form uses
the stopword list as a *gate* — a query with no content word retrieves
nothing — while every token still reaches the match expression. That keeps
the desirable property at no cost.

Normalising by query term count is rank-preserving within a query, since the
divisor is constant across that query's hits. It therefore cannot change hit
rate, and did not. It remains correct and is kept: it is what makes scores
comparable *between* queries.

**Refusal cannot be decided from term statistics on this corpus.** Three
mechanisms were measured; all three overlap completely:

| mechanism | out-of-scope | in-scope | separable? |
|---|---|---|---|
| absolute top score | 0.547 – 0.773 | 0.525 – 0.686 | no |
| peakedness (top ÷ mean of hits 2–8) | 1.088 – 1.436 | 1.026 – 1.278 | no |
| content-word coverage | 0.67 – 1.00 | 0.80 – 1.00 | no |

966,000 tokens of English prose contains nearly every common English word, so
an unrelated question still finds genuine matches; only proper nouns miss. No
threshold over term statistics can express "this corpus does not cover this
question".

This also corrects an inconsistency in v2.0: *routingAccuracy* and
*namespaceAccuracy* were demoted to diagnostics because they describe the
deterministic harness rather than the delivery path, but *refusalRate* was left
as a gate despite describing the same harness. It is now a diagnostic too.
Refusal in the delivery path is an agent reading its documents and saying they
do not answer — a judgement over content, measured by the Arcwright-side
observation log and real use (D-B14).

**Eval-set contamination.** An out-of-scope probe question quoted verbatim in
this document and in the plan afterwards scored 0.773 against those two files,
the highest in the out-of-scope set. Retrieval was correct; the question had
stopped being out-of-scope the moment it was documented. Golden questions and
the corpus must stay disjoint, and the plan now checks it.

**Task 7 post-fix measurement.** The committed baseline and the rebuilt
evaluator report these results:

| metric | before | after |
|---|---:|---:|
| hitRate | 48.5% | 48.5% |
| citationValidity | 100.0% | 100.0% |
| routingAccuracy | 24.3% | 24.3% |
| refusalRate | 0.0% | 0.0% |
| namespaceAccuracy | 35.1% | 35.1% |
| coverage | not recorded | 97.0% |
| tierCeiling | 100.0% | 100.0% |
| questions | 37 | 37 |

Hit rate is not adequate: it remains 48.5% against the 80% target. Semantic
retrieval is therefore still conditionally needed for the domains that remain
below target after Task 9's per-domain strategy measurement. It is not
commissioned as a blanket change by this measurement; only the ranked-
retrieval domains may justify it.

---

## M7 — What was built, and what the phase cost

Recorded at Phase B close.

**Verified outcomes**

| item | result |
|---|---|
| Framework release | team-ai `0.6.0` published; a second tag follows for the resolver |
| Full framework suite | 72 files, 695 tests, 0 failures |
| Framework neutrality | `check-agnostic` clean; 165 files, 0 denied tokens |
| Knowledge base | `validate-kb` OK on 449 documents, including instance `x-` fields |
| Enforcement checks | all three pass on a clean tree with **no exception list** |
| Hook loop | `Stop` 216ms, `SessionStart` 219ms — neither blocks |
| Agent split | 3 search, 10 read-all, 3 delegate, 1 route |
| Cost tier | every agent carries a `model`; previously all ran the session default |
| Dead instructions | removed — was 43% of every emitted agent |

**What the phase actually cost.** Thirteen implementer blocks, each one a real
defect. Six were gaps in the framework rather than the instance — Arcwright is
the first corpus to exercise team-ai at scale, and roughly half of what went
wrong was the framework meeting a million tokens for the first time. Two were
defects introduced by corrections to earlier defects, which is the argument for
freezing this plan rather than continuing to amend it.

The implementer caught five errors in this plan by reading the code before
writing it. That discipline found more than either review pass did.

**What is still unfixed, and deliberately so.** Hit rate is 48.5% against a
target of 80%, in the three domains holding 94.7% of the corpus. Lexical levers
are exhausted. That is the entire content of Phase C, and it is scoped by a
number rather than a wishlist.

---

---

# Decisions

Approved by the founder on 2026-09-20.

**D-B1 — Fix lexical scoring before buying retrieval infrastructure.** M1 is a
defect, not a missing feature. Semantic embeddings would have hidden it and
paid for it on every future query. **Amended by M6:** the fix makes scores
meaningful and comparable, which was its stated purpose, but it does not
improve retrieval — hit rate is unchanged at 48.5%. Sequencing it first was
still right: it cost little and it is what established that the remaining gap
is not a scoring artefact.

**D-B2 — Semantic retrieval is conditional, not scheduled.** After the scoring
fix, hit rate is re-measured. Embeddings are commissioned only if the gap
remains, and sized to the domains that still miss.

**The condition was evaluated (M6) and the gap remains:** hit rate is
48.5% against a target of 80%, and the lexical levers are exhausted. But the
decision waits for the per-domain strategy in Task 9, not for this measurement.
Eleven of fourteen domains are small enough to read outright, where findability
becomes 100% by construction and no retrieval runs at all. Only the three
domains holding 94.7% of the corpus need ranked retrieval, so any embedding
work should be scoped and justified against those three alone — measured
after Task 9, not before.

**D-B3 — Retrieval strategy is chosen per domain by corpus size.** Small
domains read their whole corpus; large domains use ranked retrieval. Uniform
strategy is wrong at both ends of a 232-to-609,458-token range.

**D-B4 — Phases are re-cut by dependency, not by artifact type.** Spec 0089
ordered work as skills, hooks, workflows, evals, graph, retrieval — a filing
system that placed the dependency of everything last.

**D-B5 — The eval gate measures coverage deterministically in team-ai.**
team-ai stays free of model calls. Delegation was to have been measured by a
model-based eval on the Arcwright side; that was cut under D-B14 and is
assessed from real use instead.

**D-B6 — `scope-evidence-check` enforces reference integrity plus a declared
evidence field**, because detecting a scope claim is reading comprehension and
these are plain scripts by design.

**D-B7 — That field is required only on newly added documents**, scoped against
the pull request's base branch, and accepts an explicit `none`.

**D-B8 — All four hooks ship, redesigned as a non-blocking loop.**

**D-B9 — No workflow engine. A `/doc-review` slash command instead.** The
`workflows` manifest section is dropped with it.

**D-B10 — `provider-leak-check` skips test files; the one real comment is
reworded.** No exception list.

**D-B11 — The dead `## Original instructions` block is no longer emitted.**

**D-B13 — Emit the declared cost tier as a host `model`. Approved
2026-09-20.** Every domain declares `model_tier: small` and the
router declares `none`, but that field is team-ai's own vocabulary and the host
does not read it. No emitted agent sets `model`, so all 17 run on the session
default — the most expensive option — while the architecture marks every
one of them cheap-tier work. Principle 6 forbids exactly that.

The founder approved adding the task on 2026-09-20. **What is not settled is
the rule question it raises**, and an automated review of the plan flagged it:
setting `model` puts a model alias into all 17 `.claude/agents/team-ai-*.md`
files, and `AGENTS.md` states that no model string may appear *anywhere*
outside `config/routing_table.json` and `engine/routing/router.py`, treating any
violation as a bug.

**Resolved as an interpretation of the existing rule, not an amendment to it.**
Principle 8's enforcement clause — "No provider name or model string may
appear anywhere outside..." — is the third bullet of a principle whose first
two bullets scope it explicitly to *platform operations* and *model calls*, and
the parallel statement sits under a heading reading **Key Engine Constraints**.
A Claude Code subagent definition is neither: it is development tooling that
makes no model call through the abstraction layer.

The strongest evidence is the repository's own behaviour. `provider-leak-check`,
approved under B-S1, scans `engine/`, `api/`, `sdk/`, `dashboard/` and `config/`
and deliberately not `.claude/`. The working interpretation has been "product
code" since before this question was asked.

So the rule reaches the product's runtime inference, which is what it exists to
protect: a hardcoded model in shipped code costs commercial flexibility. It does
not reach development tooling, which costs nothing to change.

**This also closes Q1.** The embedding model identifier indexes internal
documentation at development time — the same category — so it lives in
`team-ai/index.lock` and needs no exemption either.

**The alternative, had this gone the other way,** was a narrow exemption naming
`.claude/agents/`. Rejected under Occam: it starts an exemption list, and every
future development tool needing a model name lengthens it until nobody reads it.

**Reversal cost is low.** If the founder later prefers the absolute reading, the
mapping is one constant in team-ai's emitter and the agents regenerate.

**Still requiring founder approval, separately:** adding a sentence to
`AGENTS.md` making this scope explicit, so the question does not recur. That
text is a non-negotiable constraint and is not edited on the strength of this
decision.

Either way the tier-to-alias mapping lives in team-ai's Claude Code emitter, so
no model string enters Arcwright's own source or docs. A host-specific value
belongs in the host-specific emitter.

**Rejected as part of this:** unifying the mapping with
`config/routing_table.json`. That file routes the *product's* task types —
character dialogue, safety classification — to models at runtime. Which model
answers a documentation question during development is a different concern, and
merging them would couple the product's routing to a development tool.

Reviewers also noted this is plan-only build scope until recorded. That is the
gap this entry closes: Task 14b is blocked until this decision is marked
approved.

**D-B14 — The delegation eval is cut. Approved 2026-09-20.** It would ask a
stand-in model to predict which agent the host picks from 17 descriptions. The
host's real delegation has the whole session in context, not just descriptions,
so the proxy does not measure the same mechanism — and the one decision it
feeds, D-B12, is better served by evidence this phase already produces: the
observation log records which documents sessions actually touch, and real
questions asked in anger are a stronger signal than 37 synthetic ones.

Nothing depends on it, so the phase is complete without it. Cutting it also
removes the last external-transmission question in the phase. The information
need is not dropped: Task 20 records that delegation quality is assessed from
real use and the observation log at the one-month mark, alongside the kill
criteria.

Do not build a proxy for something that becomes directly observable, at no
cost, the moment the system is used.

**D-B12 — The 17-to-8 topology question is deferred** to the coverage and
usage evidence Phase B produces.

---

# Design

## 1. Retrieval correctness

### 1.1 Fix the scoring defect

Three changes to team-ai's lexical adapter:

1. **Drop stopwords and very common terms** before building the FTS5 match
   expression, so a question matches on its distinctive terms.
2. **Stop rewarding query length.** Normalise the BM25 result by the number of
   effective query terms so scores are comparable across queries of different
   lengths, instead of accumulating without bound.
3. **Re-tune the refusal threshold** against long natural-language questions on
   a real corpus, replacing a constant tuned on a fixture with short queries.

**Acceptance is empirical, not structural.** A meaningless stopword query must
score near zero, and an out-of-scope question must fall below the refusal
threshold while in-scope questions stay above it.

### 1.2 Per-domain retrieval strategy

| corpus | strategy | rationale |
|---|---|---|
| under ~25,000 tokens | read the whole corpus | perfect recall, no retrieval step to fail, cheaper than searching |
| above it | ranked retrieval | cannot be read; grep demonstrably fails on paraphrase |

Eleven of fourteen domains fall under the threshold. The generator needs each
domain's corpus size, which team-ai already computes while indexing. The
threshold is a setting, tuned once against measurement.

**Reporting requirement.** Domains that read everything score 100% findability
by construction. The report separates the two strategies, or it measures its
own design choice.

### 1.3 Give the large domains the index

The three domains holding 94.7% of the corpus cannot be read, so they need the
ranked index that already exists and is currently unused (M3). Emitted agents
for those domains gain permission to run the single search command, scoped in
`.claude/settings.json` to that command alone rather than general shell access.

**Token effect.** An agent that greps, misses, and reads whole files spends tens
of thousands of tokens and may still answer wrong. Eight ranked passages is
roughly 6,400 tokens with citations. That is a five- to tenfold reduction per
query, with accuracy rising rather than falling.

### 1.4 Semantic retrieval, conditional

Commissioned only if hit rate remains short after 1.1–1.3, and then only for
the domains still missing. If it proceeds, the parent spec's design holds: a
local model, no API, no key, no network, no per-query cost, vectors in the
existing database, brute-force comparison.

**Where the model identifier lives.** `AGENTS.md` confines provider and model
names to two files. That rule protects commercial flexibility over *runtime
inference*. A local embedding model indexing internal documentation at
development time is neither runtime inference nor a provider dependency. The
recommendation is a narrow decision record scoping the rule to runtime
inference, with the identifier in `team-ai/index.lock`, which already carries
an `embedding: null` slot. Putting it in `config/routing_table.json` would
place a documentation-index setting in the runtime routing table.

### 1.5 Chunking is a measured parameter

Chunks target 800 tokens, splitting on `h2`/`h3`. That is large for
precision — a chunk spanning several subtopics dilutes its own relevance. A
full rebuild takes 5.4 seconds, so the size is cheap to test. Phase B measures
hit rate at two or three chunk sizes rather than assuming the current one.

## 2. Three enforcement skills

Plain scripts. No model calls, no network. Each enforces a rule `AGENTS.md`
already declares, and each passes on a clean tree with nothing excused.

### `provider-leak-check`

**Rule.** No provider or model name outside `config/routing_table.json` and
`engine/routing/router.py`. The rule is commercial: names confined to two files
make switching providers a settings edit rather than a codebase hunt.

**Scope.** `engine/`, `api/`, `sdk/`, `dashboard/`, `config/`, excluding test
files. Documentation is governed separately by `docs/README.md`; 44 documents
on `main` contain provider strings and are a separate cleanup, not an
exemption.

**Baseline.** Eight violating lines in three files:

```
engine/tests/test_routing.py      6   env-var mapping assertions
engine/tests/test_safety_l3.py    1   quotes the comment below
engine/safety/l3.py               1   comment naming a provider's cache feature
```

Excluding tests removes seven. The eighth is reworded to "the provider's
`cache_control`", losing no information. **Founder sign-off required:** spec
0089's *Out of Scope* forbids `engine/` changes, and that is one.

### `scope-evidence-check`

1. **Reference integrity.** Every `D-NNN` and `ADR-NNNN` reference under
   `docs/specs/` and `docs/roadmap/` resolves to a real record. Measured today:
   46 decision ids and 22 ADR references, **zero dangling**.
2. **Declared evidence.** Specs and roadmap tasks newly added in a change set
   carry a front-matter field naming their approval record, or `none`.

**Two requirements found by building it.** Decision ids sit as a prefix inside
the CSV's quoted `Decision` column, so the script must parse CSV — a
line-based grep falsely reports 10 failures including the heavily-cited
`D-034`. Ids are inconsistently zero-padded (`D-45` against `D-045`) and must
be normalised. 108 of 191 rows carry an id.

### `knowledge-query-guard`

Four call sites in `engine/` generate text outside the routing module:

| call site | task type | in scope |
|---|---|---|
| `engine/characters/dialogue.py:173` | `character_dialogue` | yes |
| `engine/characters/initiative.py:418` | `character_dialogue` | yes |
| `engine/mini_games/resolver.py:174` | `narrative_generation` | no |
| `engine/narrator/bridge.py:97` | `narrator_bridge` | no |

**Rule.** A function calling `generate()` with `task_type="character_dialogue"`
must call `build_character_generation_context()` earlier in the same function
body. Narration and mini-game resolution are not characters and must not be
caught. Both in-scope sites already comply.

## 3. Four hooks as a loop

As four independent additions they cost ~16 seconds per session (`validate-kb`
6.2s, `validate-manifest` 3.9s, `freshness-audit` 5.6s, measured). As a loop
they cost nothing and each improves another.

| hook | behaviour | cost |
|---|---|---|
| `PreToolUse` | Block edits to generated files and agent-local directories | negligible |
| `PostToolUse` | Append one raw record — session id, timestamp, path written | one file append |
| `Stop` | Fire validation and freshness checks detached; write a snapshot | nothing blocking |
| `SessionStart` | Read that snapshot; inject the domain map and the last session's findings | one file read |

**`PostToolUse` records facts, not interpretations.** No edge type, no weight,
no relationship — a record that "this session touched these paths" cannot be
wrong, so Phase C derives edges from it rather than reshaping it. It has a
Phase B consumer: it is the evidence for D-B12 and for identifying unused
documents among the 447. Sharded per session at
`team-ai/graph/observations/<YYYY-MM>/<session-id>.jsonl`, which is only ever
added to, so two branches cannot conflict.

**`Stop` never blocks.** *To verify in implementation:* reliable background
detachment from a hook on Windows. Fallback, if it is not dependable: run the
checks only when the session touched `docs/` or `team-ai/`, and in parallel —
about 6 seconds on those sessions, nothing on the rest.

**`SessionStart` reports deltas.** The audit reports 0 stale, 0 unowned, and
**436 orphaned of 447**. A constant 436 is noise, so the snapshot holds a
committed baseline and the hook injects the change against it.

**Per-hook enable flags** in `.claude/settings.json`.

## 4. Measurement

**Generation is one-time authoring** by the working session, from the knowledge
base, the code and the specs, producing committed files. Not a runtime feature,
so team-ai stays free of model calls.

Each question records:

| field | purpose |
|---|---|
| source path | the document, spec or code file it came from |
| expected domain | derived from the source's namespace, never guessed |
| expected refuse | true for out-of-scope questions |
| generated on | date, for the staleness rule below |
| answer evidence | a distinctive phrase from the source any correct answer must rest on |

**Generation rules.** Paraphrase required — a question must not reuse its
source's distinctive terms, or keyword matching passes trivially and the score
overstates accuracy. Include out-of-scope questions whose correct outcome is
refusal, questions spanning two domains, and questions grounded in code and
specs rather than only prose.

**Gates.** `hitRate` is the primary gate, set from the first measurement after
the scoring fix and ratcheting upward only. `refusalRate` becomes meaningful
once scoring is fixed and is gated once it does. Coverage — does the
answer-evidence phrase still exist in a document of the expected domain — is
reported alongside, and makes the set a regression test on the knowledge base
itself. `routingAccuracy` and `namespaceAccuracy` remain in the report as
diagnostics, labelled as describing the scored router, which M3 shows is not
the delivery path.

**Staying current.** Any question whose source document changed since its
generation date is flagged for review — generation date, source path, and git
history on that path.

**Where it runs.** Coverage is a new metric inside `run-evals`, whose input is
already the golden files. The schema currently sets
`additionalProperties: false` over exactly seven fields and must be extended;
the existing seven stay, so other instances keep validating.

**Delegation eval, Arcwright side.** A model receives the agent descriptions
and a question and picks an agent; the check records whether it picked the
expected one and whether that agent's scope retrieves what it needs. Reuses the
same golden questions, so marginal cost is low. Runs on demand.

## 5. `/doc-review`

Runs the freshness audit, reports in plain language which documents are stale
and why each matters, takes the founder's decision, acts on what was approved,
and stops. Lives beside `/implement`, `/review-pr` and `/scribe`.

---

# What Phase B does not build

| dropped | reason |
|---|---|
| Scored-router improvements | M3 — not in the delivery path |
| `workflows` manifest section | D-B9 — nothing would execute it |
| Workflow engine | D-B9 — largest item in the phase, for a one-command sequence |
| Semantic retrieval, unconditionally | D-B2 — conditional on post-fix measurement |
| Topology change (17 agents to 8) | D-B12 — deferred to evidence |
| A model-based delegation eval | D-B14 — a proxy for something real use shows for free |
| Corpus re-namespacing | A second migration over ~390 documents; would not fix scoring |

---

# Acceptance criteria

**Retrieval correctness**

- [ ] A pure-stopword query scores near zero — *Verify:* search
      `"how does the of a to and it"`; expect top score below the refusal
      threshold
- [ ] Padding a question with meaningless words does not raise its score
      — *Verify:* compare the full sentence against its distinctive terms
- [ ] An out-of-scope question falls below the refusal threshold while
      in-scope questions stay above it
- [ ] Paraphrased questions surface their source document — *Verify:* hit rate
      on the committed set, before and after, both reported
- [ ] Hit rate is measured at two or three chunk sizes and the chosen size is
      recorded with its number
- [ ] Hit rate is reported separately for read-everything and retrieval domains

**Per-domain strategy**

- [ ] Each domain's emitted agent states the strategy matching its corpus size
- [ ] The eleven small domains read their corpus rather than searching it
- [ ] The three large domains can run the search command and nothing else
      — *Verify:* the settings permission names that one command

**Enforcement skills**

- [ ] `provider-leak-check` passes on the clean tree with no exception list
- [ ] It fails on a provider string planted in `engine/session/`
      — *Verify:* plant, run, expect non-zero, revert
- [ ] `scope-evidence-check` reports zero dangling references on the clean tree
- [ ] It fails on a spec citing a fabricated `D-999`
- [ ] It fails on a newly added spec with no evidence field, and passes when
      that spec declares `none`
- [ ] Existing specs and roadmap tasks without the field do not fail
      — *Verify:* run against `main` as base with no added specs
- [ ] `knowledge-query-guard` passes on the clean tree
- [ ] It fails on a `character_dialogue` generation with no preceding context
      build, and does not flag `mini_games/resolver.py` or `narrator/bridge.py`

**Hooks**

- [ ] All four fire — *Verify:* run a session touching `docs/`; confirm the
      observation file, the snapshot, and the injected domain map
- [ ] Each is individually disableable
- [ ] `PreToolUse` blocks a write to `.claude/agents/team-ai-sme.md`
- [ ] Session stop is not delayed — *Verify:* time a stop after editing
      `docs/`; expect no perceptible wait, or the documented ~6s fallback
- [ ] Two branches that each recorded observations merge without conflict
- [ ] `SessionStart` injects a delta, not the raw 436 orphaned count

**Emitted agents**

- [ ] No emitted agent contains `kb_manifest`, `kb_search` or
      `kb_coverage_gap` — *Verify:* grep `.claude/agents/`
- [ ] Regenerating produces no diff — *Verify:* re-run `emit`, then
      `git diff --exit-code -- .claude/agents`

**Measurement**

- [ ] At least 30 questions committed, each carrying all five recorded fields
- [ ] No question reuses a distinctive term from its source
      — *Verify:* the generation script reports term overlap per question
- [ ] The set includes out-of-scope, cross-domain, and code- or spec-grounded
      questions — *Verify:* counts per category
- [ ] Coverage fails when an answer-evidence phrase is deleted from its source
- [ ] Questions whose source changed since their generation date are flagged
- [ ] The extended schema accepts the new fields and still rejects unknown ones

**Boundaries**

- [ ] The only `engine/` change is the reworded comment in
      `engine/safety/l3.py` — *Verify:* `git diff --stat main -- engine/`
- [ ] No change to `api/`, `sdk/` or `dashboard/`
- [ ] `docs/agents/` and `docs/skills/` unchanged
- [ ] Every `.claude/` change is inside the founder-approved paths

---

# Founder sign-offs still required

1. **One `engine/` comment line**, against spec 0089's *Out of Scope* (D-B10).
2. **`.claude/` paths.** Hook configuration and the scoped search permission
   live in `.claude/settings.json`. `AGENTS.md` states the
   `.claude/agents/team-ai-*.md` exception "covers no other path under
   `.claude/`", but `.claude/settings.json`, `.claude/commands/` and
   `.claude/agents/implementer.md` are **already tracked** and were committed
   earlier. The rule as written is inaccurate and needs correcting regardless.
3. **The 17-file regeneration diff** from removing the dead instruction block.
4. **Scoped shell access** for the three large-domain agents, which currently
   hold read-only tools.

---

# Risks

- **The scoring fix may not recover enough hit rate.** That is why semantic
  retrieval is conditional rather than cancelled, and why the measurement is
  taken before and after.
- **Coverage will read low for thin domains.** That is the measurement working.
  The report must name which domains cover nothing, or a low number will be
  read as a broken check.
- ~~Windows background detachment is unverified.~~ **Verified 2026-09-20:** the `Stop` hook returns in 216ms and the detached child writes the snapshot; `SessionStart` reads it in 219ms. The documented fallback is not needed.
- **Widening agent tool access** is a real boundary change, scoped to one
  command and listed for sign-off.
- **The declared-evidence field can be filled carelessly.** The `none` value
  makes a careless entry visible to a reviewer rather than indistinguishable
  from a blank.

---

# References

- Parent spec: `docs/specs/0089-team-ai-agent-architecture.md` (v1.4)
- Phase A plan: `docs/superpowers/plans/2026-09-13-team-ai-agent-architecture-phase-a.md`
- Canonical agent rules: `AGENTS.md`; documentation rules: `docs/README.md`
- Collaboration rules: `docs/conventions/human-collaboration.md`
- Framework: team-ai v0.5.0
