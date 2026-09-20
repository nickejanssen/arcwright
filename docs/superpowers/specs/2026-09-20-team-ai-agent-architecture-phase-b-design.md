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

> Current version: v1.0
> Last updated: 2026-09-20
> Status: Draft — awaiting founder review
> Canonical path: `docs/superpowers/specs/2026-09-20-team-ai-agent-architecture-phase-b-design.md`
> Parent spec: `docs/specs/0089-team-ai-agent-architecture.md` (v1.4)

---

# Why this document exists

Spec 0089 describes Phase B as a bullet list: three enforcement skills, four
hooks, a workflows manifest section, and a golden-question eval gate. This
document gives Phase B the design depth Phase A got, and records the decisions
the founder made on 2026-09-20 during the design session.

It also records four measurements taken against the real repositories during
that session. Three of them changed the design. They are stated first, because
the design does not make sense without them.

---

# Measurements that reshaped Phase B

## M1 — The eval gate, run today, reports zero

An 11-question probe set was written to the generation rules in the founder's
brief (paraphrased so questions do not reuse their source document's
distinctive terms; two out-of-scope questions whose correct outcome is refusal)
and replayed through the existing `run-evals` harness against the real instance:

| metric | value | gate | result |
|---|---|---|---|
| hitRate | 22.2% | 80% | FAIL |
| routingAccuracy | 0.0% | 80% | FAIL |
| refusalRate | 0.0% | 100% | FAIL |
| namespaceAccuracy | 18.2% | 80% | FAIL |
| citationValidity | 100% | 100% | PASS |

Nine of eleven questions routed to `engineering-practice-sme` or
`product-roadmap-sme`. Both out-of-scope questions routed confidently rather
than refusing. Three mechanisms account for all of it:

1. **Paraphrase defeats the keyword step.** Routing step 1 is whole-word
   keyword matching. Paraphrased questions score zero for every domain, so
   almost everything falls through to retrieval. This is the measurement being
   honest, not a defect.
2. **Retrieval routes on the single top hit's namespace, and the corpus is 88%
   two namespaces.** `docs/roadmap/`, `docs/decisions/` and `docs/product/` are
   all `product-roadmap` (213 documents). `docs/specs/` and `docs/design/` are
   all `engineering-practice` (180). That is 393 of 447. So the top hit is
   almost always drawn from a mega-namespace.
3. **Refusal is structurally unreachable.** The refuse branch fires when the top
   hit scores below 0.2. "How many weeks of paid parental leave does the company
   offer?" — unrelated to Arcwright — scores **0.835**, above the top hit for a
   genuine knowledge-graph question. Lexical scores on this corpus carry no
   signal about whether the corpus covers the question, so no absolute
   threshold separates the two cases.

**What this proves and does not prove.** It proves `run-evals` cannot serve as
a merge gate today, and that lexical top-hit routing is unusable on this
corpus. It does **not** prove that Claude Code's delegation to the 17 emitted
agents is broken. That path is unmeasured (see M2).

## M2 — The scored router is not in the delivery path

Each emitted agent under `.claude/agents/team-ai-*.md` carries a search
procedure telling it to grep the knowledge base for its own namespace marker,
read what it finds, and answer from it. There is no scoring, no threshold, and
no top-hit namespace resolution anywhere in the delivery path. That machinery
exists only inside `run-evals`.

Consequence: improving the scored router would raise a number on a report
describing a component that never runs in Arcwright. Phase B does not do it.

## M3 — 43% of every emitted agent is instructions to call tools that do not exist

Every emitted agent ends with an `## Original instructions` block directing it
to call `kb_manifest`, `kb_search` and `kb_coverage_gap` — tools that do not
exist, because D6 chose built-in search over an MCP server — immediately after
a line stating that those tool names are unavailable.

Across the 17 agents: 20,831 characters total, of which 8,993 (43%, roughly
2,250 tokens) are the dead block. It costs tokens on every invocation and
invites fabricated tool calls, which is the failure mode this system exists to
prevent.

## M4 — Seven of thirteen specialists own one document

| domain | documents owned |
|---|---|
| knowledge-graph, character-behavior, developer-api, safety | 1 each |
| daily-case, monster-rpg, nightcap-couch-race | 1 each |
| session-runtime, model-routing | 2 each |
| playtest-ops | 3 |
| arc-execution | 5 |
| nightcap | 35 |
| engineering-practice | 180 |
| product-roadmap | 213 |

An agent whose entire corpus is one file is a slower, costlier and less
accurate path than reading that file, because it adds a cold context and a
paraphrase step. The domain split followed `docs/architecture/`'s table of
contents rather than where corpus mass sits.

**This questions merged Phase A work and is not decided here.** Phase B
measures coverage; the topology decision follows on that evidence (D-B8).

---

# Decisions

All approved by the founder on 2026-09-20 unless noted.

**D-B1 — The eval gate measures coverage in team-ai and delegation in Arcwright.**
Two separate things. A deterministic coverage check lives in team-ai and gates
CI at no per-run cost. A model-based delegation eval lives on the Arcwright
side and runs on demand, so team-ai stays free of model calls. Supersedes an
earlier decision in the same session to fix the scored router, which M2
invalidated.

**D-B2 — `scope-evidence-check` enforces reference integrity plus a declared
evidence field.** The skill cannot detect scope claims, because separating "we
will build X" from "do not build X" from "X was approved in June" is reading
comprehension, and these skills are plain scripts by design. It instead
verifies that every decision id and ADR reference resolves to a real record,
and that new specs and roadmap tasks declare their approval evidence.

**D-B3 — The declared evidence field is required only on newly added documents.**
Scoped by comparison against the pull request's base branch. The 95 existing
specs and 154 existing roadmap tasks are untouched. The field accepts an
explicit `none`, meaning *this document claims no new product scope* — a
positive statement a reviewer can disagree with, rather than a blank.

**D-B4 — All four hooks ship, redesigned as a loop.** The founder rejected a
two-hook proposal and restated the decision filter. The correct reading is keep
the capability and make it cheap, not drop the capability. See *Hooks* below.

**D-B5 — No workflow engine. A `/doc-review` slash command instead.** team-ai
has no software that executes a step recipe, and building one is the largest
item in Phase B to orchestrate a sequence runnable by hand in one command. The
`workflows` manifest section is dropped with it. The founder-approval gate
becomes a real interactive review, which is what
`docs/conventions/human-collaboration.md` requires anyway.

**D-B6 — `provider-leak-check` skips test files and the one real comment is
reworded.** Seven of the eight violating lines are in test files; a test of the
provider mapping must name the provider. The eighth is a comment in
`engine/safety/l3.py`. Result: no exception list at all, which is the only state
in which a green result keeps meaning something.

**D-B7 — The dead `## Original instructions` block is no longer emitted** in
built-in-search mode (M3).

**D-B8 — The 17-to-8 topology question is deferred to after Phase B's coverage
measurement.** Deciding it on judgement now would repeat the Phase A mistake of
following a document taxonomy instead of the evidence.

---

# Design

## Three enforcement skills

Plain scripts. No model calls, no network. Each enforces a rule `AGENTS.md`
already declares.

### `provider-leak-check`

**Rule.** No provider or model name outside `config/routing_table.json` and
`engine/routing/router.py`. The rule is commercial: names confined to two files
make switching providers a settings edit rather than a codebase hunt, which is
what preserves the ability to shop for cheaper models.

**Scope.** `engine/`, `api/`, `sdk/`, `dashboard/`, `config/`, excluding files
matching test patterns. Documentation is governed separately by
`docs/README.md`; 44 documents on `main` contain provider strings and are a
separate cleanup, not an exemption.

**Baseline.** Eight violating lines exist today, in three files:

```
engine/tests/test_routing.py      6 lines   env-var mapping assertions
engine/tests/test_safety_l3.py    1 line    quotes the comment below
engine/safety/l3.py               1 line    comment naming a provider's cache feature
```

Excluding tests removes seven. The eighth is reworded from "Anthropic's
`cache_control`" to "the provider's `cache_control`", which loses no
information. After that the check passes on a clean tree with nothing excused.

**Founder sign-off required.** Spec 0089's *Out of Scope* states Phase B makes
no change to `engine/` code. That one comment line is an `engine/` change and
needs an explicit narrow exception recorded in the spec.

### `scope-evidence-check`

**Two checks in one script.**

1. **Reference integrity.** Every `D-NNN` decision id and every `ADR-NNNN` or
   `docs/decisions/NNNN-` reference cited under `docs/specs/` and
   `docs/roadmap/` must resolve to a real record. Measured today: 46 decision
   ids and 22 ADR references cited, **zero dangling**. It can block from day
   one.
2. **Declared evidence.** Specs and roadmap tasks newly added in a change set
   must carry a front-matter field naming their approval record, or the literal
   `none`. Any id in it must resolve.

**Two implementation requirements, both found by building it.** Decision ids
live as a prefix inside the CSV's quoted `Decision` text column, not in a
column of their own, so the script must parse CSV properly — a line-based grep
falsely reports 10 failures, including the heavily-cited `D-034`. And citations
are inconsistently zero-padded (`D-45` against `D-045`), so ids must be
normalised before comparison. 108 of 191 rows carry an id at all.

### `knowledge-query-guard`

**Rule.** A knowledge-state query precedes every AI character generation.

**Precise form.** Four call sites in `engine/` generate text outside the routing
module:

| call site | task type | in scope |
|---|---|---|
| `engine/characters/dialogue.py:173` | `character_dialogue` | yes |
| `engine/characters/initiative.py:418` | `character_dialogue` | yes |
| `engine/mini_games/resolver.py:174` | `narrative_generation` | no |
| `engine/narrator/bridge.py:97` | `narrator_bridge` | no |

So the rule is: *a function calling `generate()` with
`task_type="character_dialogue"` must call
`build_character_generation_context()` earlier in the same function body.*
Narration and mini-game resolution are not characters and must not be caught.

**Baseline.** Both in-scope sites already comply (context built at lines 127
and 392/397 respectively). Passes on a clean tree with nothing excused.

## Four hooks, designed as a loop

Specified as four independent additions they cost about 16 seconds per session
(`validate-kb` 6.2s, `validate-manifest` 3.9s, `freshness-audit` 5.6s, all
measured). Designed as a loop they cost nothing, and each makes another better.

| hook | behaviour | cost |
|---|---|---|
| `PreToolUse` (Write/Edit) | Block edits to generated files and agent-local directories | negligible |
| `PostToolUse` (Write) | Append one raw record — session id, timestamp, path written — to that session's own file | one file append |
| `Stop` | Fire the validation and freshness checks detached; write the result to a snapshot file. Never waits | nothing blocking |
| `SessionStart` | Read that snapshot file and inject the domain map plus the last session's findings | one file read |

**`PostToolUse` records facts, not interpretations.** No edge type, no weight,
no relationship. A record saying "this session touched these paths" cannot be
wrong, so Phase C cannot be forced to reshape it — Phase C derives edges from
it. This removes the format lock-in the founder's brief identified, and the log
has standalone value now as the only durable record of which documents sessions
actually use, which is the input the spec's gap detection needs. Files are
sharded per session under `team-ai/graph/observations/<YYYY-MM>/<session-id>.jsonl`,
matching the parent spec's conflict-free design: a per-session file is only
ever added, never edited, so two branches cannot conflict on it.

**`Stop` never blocks.** The same checks CI already runs are fired detached and
their result is written where `SessionStart` will read it. **To verify during
implementation:** reliably detaching a background process from a hook on
Windows. If it cannot be made dependable, the fallback is to run the checks
only when the session touched `docs/` or `team-ai/`, and in parallel rather
than in series — roughly 6 seconds on those sessions and nothing on the rest.

**`SessionStart` reports deltas, not totals.** The freshness audit today
reports 0 stale, 0 unowned and **436 orphaned of 447**. A constant 436 is
noise, so the snapshot records a committed baseline and the hook injects the
change against it.

**Per-hook enable flags** live in `.claude/settings.json`, satisfying the
parent spec's "individually disableable" criterion.

## Coverage measurement

**Generation is a one-time authoring step** performed by the working session
from the knowledge base, the code and the specs, producing committed files.
It is not a team-ai runtime feature, so team-ai stays free of model calls.

**Each question records:**

| field | purpose |
|---|---|
| source path | the document, spec or code file it came from |
| expected domain | derived from the source's namespace, never guessed |
| expected refuse | true for out-of-scope questions |
| generated on | date, used for the staleness rule below |
| answer evidence | a short distinctive phrase from the source that any correct answer must rest on |

**Generation rules**, per the founder's brief:

- Paraphrase required. A question must not reuse its source's distinctive
  terms, because a question lifted from a document passes keyword routing
  trivially and the score then overstates accuracy.
- Include out-of-scope questions whose correct outcome is refusal.
- Include questions spanning two domains.
- Include questions grounded in code and specs, not only prose documents.

**What coverage means.** For each question: does the answer-evidence phrase
still exist, in a document belonging to the expected domain? That makes the set
a regression test on the knowledge base itself — if a document is rewritten and
the fact deleted, the check fails and names the question.

**How the set stays current.** Any question whose source document has changed
since the question's generation date is flagged for review. Deterministic:
generation date plus source path plus git history on that path.

**Expected result.** Most single-document domains will cover very little. That
is the finding worth having, and it is the evidence for D-B8.

**Where it runs.** Coverage is a new metric inside the existing `run-evals`
command, because the golden files are already that command's input and a
separate command would duplicate its loading and reporting. The routing,
refusal and namespace metrics stay in the report but are labelled as
describing the scored router, which M2 establishes is not the delivery path —
they are diagnostic, not gates.

**Schema change required in team-ai.** The golden question schema currently
sets `additionalProperties: false` and requires exactly seven fields, so the
provenance and evidence fields cannot be added without extending it. The
existing seven fields stay, so any instance's current golden files keep
validating.

**Gate thresholds.** Coverage is the only new gate. It is set from the first
measured run and may only move upward, so it ratchets rather than being guessed
in advance.

## Delegation eval, Arcwright side

Measures the path that actually ships: a model receives the 17 agent
descriptions and a question, and picks an agent. Checks whether it picks the
expected one, and whether that agent's grep scope retrieves the documents
needed. Runs on demand, not per pull request, so it costs nothing routinely and
team-ai stays model-free.

## `/doc-review` slash command

Runs the freshness audit, reports in plain language which documents are stale
and why each matters, takes the founder's decision on which to fix, acts on
what was approved, and stops. Lives beside the existing `/implement`,
`/review-pr` and `/scribe` commands.

---

# What Phase B does not build, and why

| dropped | reason |
|---|---|
| Scored-router improvements | M2 — not in the delivery path |
| `workflows` manifest section | D-B5 — nothing would execute it |
| Workflow engine in team-ai | D-B5 — largest item in the phase, for a one-command sequence |
| Topology change (17 agents to 8) | D-B8 — deferred to coverage evidence |
| Corpus re-namespacing | Would be a second migration over ~390 documents, and would not fix refusal, which is a scoring problem |

---

# Acceptance criteria

Each criterion names a command that proves it.

**Enforcement skills**

- [ ] `provider-leak-check` passes on the clean tree with no exception list
      — *Verify:* run it; expect exit 0 and an empty findings list
- [ ] `provider-leak-check` fails on a provider string planted in
      `engine/session/` — *Verify:* plant, run, expect non-zero, revert
- [ ] `scope-evidence-check` reports zero dangling references on the clean tree
      — *Verify:* run it; expect exit 0
- [ ] `scope-evidence-check` fails on a spec citing a fabricated `D-999`
      — *Verify:* plant, run, expect non-zero naming the id and file
- [ ] `scope-evidence-check` fails on a newly added spec with no evidence field
      — *Verify:* add a spec without the field on a branch, run against base,
      expect non-zero
- [ ] `scope-evidence-check` passes when that spec declares `none`
- [ ] Existing specs and roadmap tasks without the field do not fail
      — *Verify:* run against `main` as base with no added specs; expect exit 0
- [ ] `knowledge-query-guard` passes on the clean tree
- [ ] `knowledge-query-guard` fails on a `character_dialogue` generation with no
      preceding context build — *Verify:* plant, run, expect non-zero, revert
- [ ] `knowledge-query-guard` does not flag `mini_games/resolver.py` or
      `narrator/bridge.py`

**Hooks**

- [ ] All four hooks fire — *Verify:* run a session touching `docs/`, confirm
      the observation file, the snapshot file, and the injected domain map
- [ ] Each hook is individually disableable — *Verify:* disable each in turn via
      its settings flag and confirm it does not fire
- [ ] `PreToolUse` blocks a write to `.claude/agents/team-ai-sme.md`
- [ ] Session stop is not delayed — *Verify:* time a session stop after editing
      `docs/`; expect no perceptible wait, or the documented ~6s fallback
- [ ] Two branches that each recorded observations merge without conflict
      — *Verify:* record on two branches, merge, expect no conflict
- [ ] `SessionStart` injects a freshness delta, not the raw 436 orphaned count

**Emitted agents**

- [ ] No emitted agent contains `kb_manifest`, `kb_search` or
      `kb_coverage_gap` — *Verify:* grep `.claude/agents/`; expect no matches
- [ ] Regenerating emitted agents produces no diff — *Verify:* re-run `emit`,
      then `git diff --exit-code -- .claude/agents`

**Coverage and delegation**

- [ ] At least 30 questions committed, each carrying source path, expected
      domain, expected refuse, generation date and answer evidence
- [ ] No question reuses a distinctive term from its source document
      — *Verify:* the generation script reports term overlap per question
- [ ] The set includes out-of-scope, cross-domain, and code- or spec-grounded
      questions — *Verify:* counts reported per category
- [ ] Coverage is reported as a number per domain
- [ ] Coverage fails when an answer-evidence phrase is deleted from its source
      — *Verify:* delete one, run, expect the question named, revert
- [ ] Questions whose source changed since their generation date are flagged
- [ ] The delegation eval reports which agent was chosen per question
- [ ] The extended golden-question schema accepts the new fields and still
      rejects unknown ones — *Verify:* run the coverage check against the
      committed set (exit 0), then against a question carrying a misspelled
      field (non-zero)

**Boundaries**

- [ ] The only `engine/` change is the one reworded comment in
      `engine/safety/l3.py` — *Verify:* `git diff --stat main -- engine/`
- [ ] No change to `api/`, `sdk/` or `dashboard/`
- [ ] `docs/agents/` and `docs/skills/` unchanged
- [ ] Every `.claude/` change is inside the founder-approved paths

---

# Founder sign-offs still required

1. **One `engine/` comment line** reworded, against spec 0089's *Out of Scope*
   (D-B6).
2. **`.claude/` paths.** Hook configuration lives in `.claude/settings.json`.
   `AGENTS.md` states the `.claude/agents/team-ai-*.md` exception "covers no
   other path under `.claude/`", but `.claude/settings.json`,
   `.claude/commands/` and `.claude/agents/implementer.md` are **already
   tracked** and were committed earlier. The rule as written is inaccurate and
   needs correcting regardless of this phase.
3. **The 17-file regeneration diff** from removing the dead instruction block.

---

# Risks

- **Coverage will read low, and that is the point.** A low number invites
  treating the measurement as broken rather than the corpus as thin. The report
  must name which domains cover nothing.
- **Windows background detachment for the `Stop` hook** is unverified. Fallback
  is specified above.
- **The declared-evidence field can be filled carelessly** to clear the check.
  The `none` value is designed to make a careless entry visible to a reviewer
  rather than indistinguishable from a blank.
- **The delegation eval costs model calls.** It runs on demand, not per pull
  request, and is the only way to measure the path that actually ships.

---

# References

- Parent spec: `docs/specs/0089-team-ai-agent-architecture.md` (v1.4)
- Phase A plan: `docs/superpowers/plans/2026-09-13-team-ai-agent-architecture-phase-a.md`
- Canonical agent rules: `AGENTS.md`
- Documentation rules: `docs/README.md`
- Collaboration rules: `docs/conventions/human-collaboration.md`
- Framework: team-ai v0.5.0; `docs/design/2026-08-30-team-ai-framework-design.md`,
  `docs/design/2026-09-13-agent-topology-design.md`
