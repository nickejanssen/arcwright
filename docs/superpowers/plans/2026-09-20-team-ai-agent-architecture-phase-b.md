---
id: engineeringpractice.superpowers.plans.2026-09-20-team-ai-agent-architecture-phase-b
namespace: engineering-practice
title: team-ai Agent Architecture Phase B Implementation Plan
owner: Nico Janssen
status: active
review_by: "2027-03-20"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# team-ai Agent Architecture Phase B Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Arcwright's knowledge agents actually find things — fix the lexical scoring defect, size retrieval strategy to each domain's corpus, and put deterministic guardrails and measurement around the result.

**Architecture:** Two repositories. `team-ai` (the framework, at `../team-ai` relative to the Arcwright checkout) owns retrieval scoring, the emitter, and the eval harness. Arcwright owns its instance content under `team-ai/`, the checker scripts, hooks, and CI. Every change is deterministic — no model calls in the framework.

**Tech Stack:** TypeScript + Vitest (team-ai), Python + pytest (Arcwright checkers), SQLite FTS5, Node 22+, GitHub Actions.

**User decisions (already made):**
- "Fix lexical scoring before buying retrieval infrastructure" — semantic embeddings would have hidden the defect (D-B1).
- "Semantic retrieval is conditional, not scheduled" — commissioned only if hit rate stays short after the fix (D-B2).
- "Retrieval strategy is chosen per domain by corpus size" — small domains read everything (D-B3).
- "Both: coverage in team-ai, path eval in Arcwright" — team-ai stays free of model calls (D-B5).
- "Also require new docs to name their approval up front" — plus reference integrity (D-B6).
- "Files added in the change set" — the evidence field is not backfilled (D-B7).
- "All four as specified" — all four hooks ship, redesigned as a non-blocking loop (D-B8).
- "You type /doc-review and it walks you through it" — no workflow engine (D-B9).
- Provider-leak-check skips test files; the one real comment is reworded (D-B10).

**Reference:** `docs/superpowers/specs/2026-09-20-team-ai-agent-architecture-phase-b-design.md`

---

## Repository paths

| name | path used in this plan |
|---|---|
| Arcwright checkout | the working directory |
| team-ai checkout | `../team-ai` (adjust if yours differs; confirm with `ls ../team-ai/package.json`) |
| team-ai CLI, built | `node ../team-ai/dist/cli.js` |

Build team-ai once before starting: `cd ../team-ai && npm ci && npm run build`

---

## File structure

**team-ai (framework):**

| file | responsibility |
|---|---|
| `src/retrieval/lexical.ts` | Query sanitisation and BM25 score normalisation — the defect |
| `src/retrieval/lexical.test.ts` | Unit tests for both |
| `schemas/golden.schema.json` | Golden question shape — gains five fields |
| `src/evals/metrics.ts` | Adds the coverage metric |
| `src/evals/run.ts` | Computes coverage per question |
| `src/emit/index.ts` | Adds per-namespace corpus sizes to the emit input |
| `src/emit/claude-code.ts` | Per-domain search strategy; tier-to-model mapping; stops emitting the dead block |

**Arcwright (instance):**

| file | responsibility |
|---|---|
| `team-ai/evals/golden/*.golden.yaml` | The committed question set |
| `team-ai/evals/gates.yaml` | Ratcheted thresholds |
| `scripts/checks/provider_leak_check.py` | Provider-name checker |
| `scripts/checks/scope_evidence_check.py` | Reference integrity + declared evidence |
| `scripts/checks/knowledge_query_guard.py` | Character-generation guard |
| `scripts/hooks/` | The four hook scripts |
| `.claude/settings.json` | Hook registration, per-hook flags, scoped search permission |
| `.claude/commands/doc-review.md` | The `/doc-review` command |
| `.github/workflows/team-ai.yml` | CI wiring |

---

## Part 1 — Retrieval correctness

> **Framework code names no instance.** `team-ai` ships to any team, and
> `check-agnostic` fails the build when a team's proper noun appears in shipped
> source — `src/` (non-test, non-fixture), `schemas/`, `catalog/`, `templates/`,
> `bin/`. That includes comments. When pasting a measurement into a framework
> comment, describe the corpus ("a 37-question golden set over a ~966,000-token
> corpus"), never whose it is. Instance-specific findings belong in this repo's
> design document. *Verify before every team-ai commit:*
> `cd ../team-ai && node dist/cli.js check-agnostic`


### Task 1: Extend the golden question schema

**Repository:** team-ai

**Goal:** The golden question shape accepts provenance and answer-evidence fields, while still rejecting unknown ones and keeping existing instances valid.

**Files:**
- Modify: `schemas/golden.schema.json`
- Modify: `src/schema/types.ts` (the `GoldenQuestion` interface)
- Test: `src/schema/validate.test.ts`

**Acceptance Criteria:**
- [ ] A question carrying `source_path`, `generated_on`, `answer_evidence` validates
- [ ] The five original fields remain required; the new ones are optional
- [ ] A question with a misspelled field still fails validation
- [ ] Existing golden files with only the original seven fields still validate

**Verify:** `cd ../team-ai && npx vitest run src/schema/validate.test.ts` → all pass

**Steps:**

- [ ] **Step 1: Write the failing tests**

Add to `src/schema/validate.test.ts`:

```ts
describe("golden schema provenance fields", () => {
  const base = {
    id: "eval.kg.example",
    question: "Where is second-hand knowledge recorded?",
    expect_namespace: "knowledge-graph",
    expect_paths: ["architecture/04-knowledge-graph.md"],
    expect_route: "knowledge-graph-sme",
    expect_tier_max: "small",
    must_cite: true,
  };

  it("accepts the original seven fields alone", () => {
    expect(validate("golden", base).ok).toBe(true);
  });

  it("accepts provenance and answer evidence", () => {
    const withProvenance = {
      ...base,
      source_path: "architecture/04-knowledge-graph.md",
      generated_on: "2026-09-20",
      answer_evidence: "who knows what, when they learned it, and from whom",
    };
    expect(validate("golden", withProvenance).ok).toBe(true);
  });

  it("still rejects an unknown field", () => {
    expect(validate("golden", { ...base, sorce_path: "x" }).ok).toBe(false);
  });
});
```

- [ ] **Step 2: Run to confirm failure**

Run: `cd ../team-ai && npx vitest run src/schema/validate.test.ts`
Expected: the provenance test FAILS (`additionalProperties` rejects the new keys).

- [ ] **Step 3: Add the fields to the schema**

In `schemas/golden.schema.json`, inside `properties`, after `must_cite`:

```json
    "source_path": { "type": "string" },
    "generated_on": { "type": "string", "format": "date" },
    "answer_evidence": { "type": "string" }
```

Leave `required` and `additionalProperties: false` unchanged.

- [ ] **Step 4: Add them to the TypeScript type**

In `src/schema/types.ts`, on the `GoldenQuestion` interface:

```ts
  source_path?: string;
  generated_on?: string;
  answer_evidence?: string;
```

- [ ] **Step 5: Run to confirm all pass**

Run: `cd ../team-ai && npx vitest run src/schema/validate.test.ts`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
cd ../team-ai && git add schemas/golden.schema.json src/schema/types.ts src/schema/validate.test.ts && git commit -m "feat(evals): golden questions carry provenance and answer evidence"
```

---

### Task 2: Author the Arcwright golden set and record the baseline

**Repository:** Arcwright

**Goal:** At least 30 committed questions with full provenance, and the before-fix metrics recorded so the scoring fix can be judged.

**Files:**
- Create: `team-ai/evals/golden/arcwright.golden.yaml`
- Create: `team-ai/evals/baseline-2026-09-20.json`

**Acceptance Criteria:**
- [ ] ≥ 30 questions, each with all five recorded fields
- [ ] No question reuses a distinctive term from its own source document
- [ ] At least 4 out-of-scope questions with `expect_route: __refuse__`
- [ ] At least 3 questions spanning two domains
- [ ] At least 5 questions grounded in code or specs rather than prose
- [ ] Every domain with ≥ 1 document has ≥ 1 question
- [ ] **No question appears verbatim anywhere under `docs/`.** A question
      written into a design document, plan or spec becomes part of the corpus
      being measured, and retrieval then finds the question rather than the
      answer. This happened on 2026-09-20: an out-of-scope probe question was
      quoted in the Phase B design and plan, and afterwards scored 0.773
      against those two documents — the highest score in the whole
      out-of-scope set. Eval questions and the corpus must stay disjoint, the
      same separation a test set needs from training data
- [ ] The baseline file records hitRate, refusalRate, routingAccuracy, namespaceAccuracy

**Verify:** `node ../team-ai/dist/cli.js run-evals --root team-ai --json > team-ai/evals/baseline-2026-09-20.json; python -c "import json;d=json.load(open('team-ai/evals/baseline-2026-09-20.json'));print(d['metrics'])"` → prints the metric object

**Steps:**

- [ ] **Step 1: List each domain's documents**

```bash
python - <<'PY'
import pathlib,re,collections
m=collections.defaultdict(list)
for p in pathlib.Path('docs').rglob('*.md'):
    if 'archive' in p.parts: continue
    t=p.read_text(encoding='utf-8',errors='replace')
    n=re.search(r'^namespace:\s*(\S+)',t,re.M)
    if n: m[n.group(1)].append(p.relative_to('docs').as_posix())
for k in sorted(m): print(k, len(m[k]))
PY
```

- [ ] **Step 2: Write the questions**

One YAML list at `team-ai/evals/golden/arcwright.golden.yaml`. Paths in `expect_paths` and `source_path` are relative to the KB root (`docs/`), matching what `search` prints. Example entries covering each required category:

```yaml
- id: eval.kg.secondhand
  question: Where do we record that someone only found something out from another guest, and when?
  expect_namespace: knowledge-graph
  expect_paths: [architecture/04-knowledge-graph.md]
  expect_route: knowledge-graph-sme
  expect_tier_max: small
  must_cite: true
  source_path: architecture/04-knowledge-graph.md
  generated_on: "2026-09-20"
  answer_evidence: who knows what, when they learned it, and from whom

- id: eval.safety.authored-cannot-bypass
  question: Can an authored scenario file switch off the protections that stop harmful output?
  expect_namespace: safety
  expect_paths: [architecture/10-content-safety.md]
  expect_route: safety-sme
  expect_tier_max: small
  must_cite: true
  source_path: architecture/10-content-safety.md
  generated_on: "2026-09-20"
  answer_evidence: enforced at the engine layer

- id: eval.cross.knowledge-and-character
  question: Can a system-driven guest mention something they were never told?
  expect_namespace: knowledge-graph
  expect_paths: [architecture/04-knowledge-graph.md, architecture/07-character-behavior.md]
  expect_route: knowledge-graph-sme
  expect_tier_max: small
  must_cite: true
  source_path: architecture/04-knowledge-graph.md
  generated_on: "2026-09-20"
  answer_evidence: constrained by character knowledge state

- id: eval.refuse.<topic>
  question: <a question about something Arcwright holds no documents on>
  expect_namespace: ""
  expect_paths: []
  expect_route: __refuse__
  expect_tier_max: small
  must_cite: false
  generated_on: "2026-09-20"
```

The refusal entry is deliberately a placeholder. **Write your own, and do not
paste it into any file under `docs/`.** A question recorded in a document
becomes part of the corpus and stops being out-of-scope. The parental-leave
question used during design is permanently burned for exactly this reason: it
is quoted in this plan and in the design document as the record of a
measurement that was taken, and that record must not be edited to make an old
question legal again. Pick a different one.

Rules while writing, per the design document:
- Open each `source_path`, note its distinctive terms, and phrase the question without them.
- `expect_namespace` is the source document's own `namespace:` value — read it, never guess.
- `answer_evidence` is a short phrase copied verbatim from the source.
- Refusal questions carry no `source_path` or `answer_evidence`.

- [ ] **Step 3: Check no question reuses its source's distinctive terms**

```bash
python - <<'PY'
import yaml,pathlib,re,collections
qs=yaml.safe_load(open('team-ai/evals/golden/arcwright.golden.yaml',encoding='utf-8'))
STOP=set("a an and are as at be but by do does for from how i if in is it its of on or that the their them then there these they this to was we were what when where which who why will with you your can could".split())
corpus=collections.Counter()
docs={}
for p in pathlib.Path('docs').rglob('*.md'):
    if 'archive' in p.parts: continue
    w=set(re.findall(r'[a-z][a-z-]{3,}',p.read_text(encoding='utf-8',errors='replace').lower()))
    docs[p.relative_to('docs').as_posix()]=w
    corpus.update(w)
bad=0
for q in qs:
    sp=q.get('source_path')
    if not sp or sp not in docs: continue
    qw={w for w in re.findall(r'[a-z][a-z-]{3,}',q['question'].lower()) if w not in STOP}
    # distinctive = appears in this doc and in fewer than 20 docs overall
    distinctive={w for w in qw & docs[sp] if corpus[w]>0 and sum(1 for d in docs.values() if w in d)<20}
    if distinctive:
        print("REUSES:",q['id'],sorted(distinctive)); bad+=1
print("questions:",len(qs),"reusing distinctive terms:",bad)
PY
```
Expected: `reusing distinctive terms: 0`. Rephrase any that are listed and re-run.

- [ ] **Step 4: Check for corpus contamination**

```bash
python - <<'EOF'
import yaml, subprocess
qs = yaml.safe_load(open('team-ai/evals/golden/arcwright.golden.yaml', encoding='utf-8'))
bad = 0
for q in qs:
    hit = subprocess.run(['git', 'grep', '-l', '-F', q['question'], '--', 'docs'],
                         capture_output=True, text=True).stdout.strip()
    if hit:
        print('CONTAMINATED:', q['id'], '->', hit.replace(chr(10), ', '))
        bad += 1
print('questions:', len(qs), 'appearing verbatim in the corpus:', bad)
EOF
```
Expected: `appearing verbatim in the corpus: 0`. Rephrase any that are listed.
Do not quote the replacements into any document under `docs/`.

- [ ] **Step 4: Check category counts**

```bash
python - <<'PY'
import yaml
qs=yaml.safe_load(open('team-ai/evals/golden/arcwright.golden.yaml',encoding='utf-8'))
print("total:",len(qs))
print("refusal:",sum(1 for q in qs if q['expect_route']=='__refuse__'))
print("cross-domain:",sum(1 for q in qs if len(q.get('expect_paths',[]))>1))
print("code/spec-grounded:",sum(1 for q in qs if str(q.get('source_path','')).startswith(('specs/','engine/','api/'))))
import collections
print(collections.Counter(q['expect_namespace'] for q in qs))
PY
```
Expected: total ≥ 30, refusal ≥ 4, cross-domain ≥ 3, code/spec-grounded ≥ 5.

- [ ] **Step 5: Record the baseline**

```bash
node ../team-ai/dist/cli.js run-evals --root team-ai --json > team-ai/evals/baseline-2026-09-20.json
python -c "import json;print(json.load(open('team-ai/evals/baseline-2026-09-20.json'))['metrics'])"
```
Expected: a metrics object. It will FAIL the gates — that is the point of a baseline. Record the numbers.

- [ ] **Step 6: Commit**

```bash
git add team-ai/evals/golden/arcwright.golden.yaml team-ai/evals/baseline-2026-09-20.json
git commit -m "test(evals): Arcwright golden question set and pre-fix baseline"
```

---

### Task 3: Stop the query from matching on stopwords

**Repository:** team-ai

**Goal:** A question matches on its distinctive terms. A query made only of stopwords returns nothing rather than scoring 0.731.

**Files:**
- Modify: `src/retrieval/lexical.ts` (`sanitizeQuery`, around line 222)
- Test: `src/retrieval/lexical.test.ts`

**Acceptance Criteria:**
- [ ] `sanitizeQuery` uses the stopword list as a gate, not as a filter — every token still reaches the match expression
- [ ] A query of only stopwords returns `null`, so search returns `[]`
- [ ] Hit rate does not regress against the Task 2 baseline — *Verify:* `run-evals` hitRate is at or above the recorded baseline
- [ ] Existing lexical tests still pass

**Verify:** `cd ../team-ai && npx vitest run src/retrieval/lexical.test.ts` → all pass

**Steps:**

- [ ] **Step 1: Export the function so it can be unit tested**

In `src/retrieval/lexical.ts`, change the declaration:

```ts
export function sanitizeQuery(query: string): string | null {
```

- [ ] **Step 2: Write the failing tests**

Add to `src/retrieval/lexical.test.ts`:

```ts
import { LexicalAdapter, sanitizeQuery } from "./lexical.js";

describe("sanitizeQuery", () => {
  it("keeps every token when the query has at least one content word", () => {
    expect(sanitizeQuery("the 429 errors")).toBe('"the" OR "429" OR "errors"');
  });

  it("returns null when every token is a stopword", () => {
    expect(sanitizeQuery("how does the of a to and it")).toBeNull();
  });

  it("returns null for empty input", () => {
    expect(sanitizeQuery("   ")).toBeNull();
  });

  it("keeps hyphenated and numeric terms", () => {
    expect(sanitizeQuery("the 429 rate-limit errors"))
      .toBe('"the" OR "429" OR "rate-limit" OR "errors"');
  });
});
```

- [ ] **Step 3: Run to confirm failure**

Run: `cd ../team-ai && npx vitest run src/retrieval/lexical.test.ts`
Expected: the stopword tests FAIL — current output ORs every token.

- [ ] **Step 4: Implement**

Replace `sanitizeQuery` in `src/retrieval/lexical.ts` with:

```ts
// A query made only of function words carries no retrieval intent and must
// retrieve nothing. The list below is used as a GATE for that purpose — it is
// deliberately NOT used to filter terms out of the match expression.
//
// Measured on a 37-question golden set over a ~966,000-token corpus: filtering
// stopwords out of the match cost 6.1 points of hit rate (48.5% -> 42.4%) and
// 8.1 points of routing accuracy (24.3% -> 16.2%). BM25 already discounts common terms by
// inverse document frequency, so removing them discards disambiguating context
// and buys nothing. Gating on them preserves the "no content words retrieves
// nothing" property at zero cost.
const STOPWORDS = new Set([
  "a", "about", "an", "and", "any", "are", "as", "at", "be", "been", "but", "by",
  "can", "could", "did", "do", "does", "for", "from", "get", "had", "has", "have",
  "how", "i", "if", "in", "into", "is", "it", "its", "just", "may", "might",
  "much", "must", "my", "no", "not", "of", "on", "or", "our", "out", "over",
  "should", "so", "some", "such", "than", "that", "the", "their", "them", "then",
  "there", "these", "they", "this", "those", "to", "up", "was", "we", "were",
  "what", "when", "where", "which", "while", "who", "why", "will", "with",
  "would", "you", "your",
]);

// Turn arbitrary user text into a safe FTS5 MATCH string. FTS5 treats bare
// punctuation and quotes as syntax and throws on malformed input, so we reduce
// the query to alphanumeric/hyphen tokens, quote each one, and OR them
// together. Returns null when the query contains no content word at all — such
// a query should retrieve nothing, not everything.
export function sanitizeQuery(query: string): string | null {
  const tokens = query
    .split(/\s+/)
    .map((t) => t.replace(/[^\w-]/g, ""))
    .filter((t) => /\w/.test(t));
  const hasContentWord = tokens.some((t) => !STOPWORDS.has(t.toLowerCase()));
  if (!hasContentWord) return null;
  return tokens.map((t) => `"${t}"`).join(" OR ");
}
```

**If you have already implemented the filtering version**, this is the
correction: keep the gate (`hasContentWord`), and match on `tokens`, not on the
filtered list. Re-run `run-evals` and confirm hit rate returns to the recorded
baseline rather than sitting below it.

- [ ] **Step 5: Run to confirm all pass**

Run: `cd ../team-ai && npx vitest run src/retrieval/lexical.test.ts`
Expected: PASS, including the pre-existing tests.

- [ ] **Step 6: Commit**

```bash
cd ../team-ai && git add src/retrieval/lexical.ts src/retrieval/lexical.test.ts && git commit -m "fix(retrieval): drop stopwords so BM25 ranks on distinctive terms"
```

---

### Task 4: Make scores comparable across query lengths

**Repository:** team-ai

**Goal:** A score reflects per-term relevance, so adding words to a query no longer inflates it and the refusal threshold becomes usable.

**Files:**
- Modify: `src/retrieval/lexical.ts` (`scoreFromBm25`, around line 281; its call site around line 181)
- Test: `src/retrieval/lexical.test.ts`

**Acceptance Criteria:**
- [ ] `scoreFromBm25` divides relevance by the number of effective query terms
- [ ] Padding a query with extra content words does not raise its top score
- [ ] A non-match (`bm25 >= 0`) still scores 0
- [ ] Existing lexical tests still pass

**Verify:** `cd ../team-ai && npx vitest run src/retrieval/lexical.test.ts` → all pass

**Steps:**

- [ ] **Step 1: Write the failing test**

Add to `src/retrieval/lexical.test.ts`:

```ts
import { scoreFromBm25 } from "./lexical.js";

describe("scoreFromBm25", () => {
  it("scores a non-match as zero", () => {
    expect(scoreFromBm25(0, 3)).toBe(0);
    expect(scoreFromBm25(1.5, 3)).toBe(0);
  });

  it("does not reward accumulation across more terms", () => {
    // Same per-term relevance, different term counts, must score the same.
    expect(scoreFromBm25(-6, 3)).toBeCloseTo(scoreFromBm25(-12, 6), 10);
  });

  it("scores stronger per-term relevance higher", () => {
    expect(scoreFromBm25(-12, 3)).toBeGreaterThan(scoreFromBm25(-6, 3));
  });
});
```

- [ ] **Step 2: Run to confirm failure**

Run: `cd ../team-ai && npx vitest run src/retrieval/lexical.test.ts`
Expected: FAIL — `scoreFromBm25` currently takes one argument and is not exported.

- [ ] **Step 3: Implement**

Replace the score block in `src/retrieval/lexical.ts`:

```ts
// Score normalization (documented formula):
//   FTS5 bm25() is negative for a match and more negative = more relevant; a
//   non-match or a value >= 0 scores 0.
//   Let rel = -bm25 (positive; larger = better), and n = the number of terms in
//   the sanitized query. BM25 sums a contribution per matched term, so rel grows
//   with query length; dividing by n makes the score describe per-term relevance
//   and therefore comparable across queries of different lengths. Without this,
//   a long question of ordinary words outscores a short precise one and the
//   "cite or refuse" threshold becomes unreachable.
//     score = (rel / n) / ((rel / n) + BM25_K)
const BM25_K = 1.5;

export function scoreFromBm25(bm25: number, termCount: number): number {
  const rel = -bm25;
  if (rel <= 0) return 0;
  const perTerm = rel / Math.max(1, termCount);
  return Math.min(1, Math.max(0, perTerm / (perTerm + BM25_K)));
}
```

- [ ] **Step 4: Pass the term count at the call site**

In the `search` method, compute the count once from the sanitized query and pass it. Around line 159–181:

```ts
    const match = sanitizeQuery(query);
    if (match === null) return [];
    const termCount = match.split(" OR ").length;
```

and change the row mapping:

```ts
      score: scoreFromBm25(row.bm25, termCount),
```

- [ ] **Step 5: Run to confirm all pass**

Run: `cd ../team-ai && npx vitest run src/retrieval/lexical.test.ts`
Expected: PASS.

- [ ] **Step 6: Build and check the real corpus behaviour**

```bash
cd ../team-ai && npm run build && cd -
node ../team-ai/dist/cli.js reindex --root team-ai
echo "--- meaningless query, expect no results ---"
node ../team-ai/dist/cli.js search "how does the of a to and it" --root team-ai --k 1
echo "--- out-of-scope, expect a low score ---"
node ../team-ai/dist/cli.js search "How many weeks of paid parental leave does the company offer?" --root team-ai --k 1
echo "--- in-scope, expect a clearly higher score ---"
node ../team-ai/dist/cli.js search "Where do we record that someone only found something out from another guest?" --root team-ai --k 1
```
Expected: the first prints no hits; the out-of-scope score is visibly below the in-scope score. Record both numbers — Task 6 sets the threshold from them.

- [ ] **Step 7: Commit**

```bash
cd ../team-ai && git add src/retrieval/lexical.ts src/retrieval/lexical.test.ts && git commit -m "fix(retrieval): normalize BM25 by query term count"
```

---

### Task 5: Demote refusal to a diagnostic — lexical refusal is not achievable

**Repository:** team-ai

**Goal:** Stop gating CI on a metric that measurement shows cannot be satisfied
lexically, and record why, so nobody re-attempts it.

**This task replaces "re-tune the refusal threshold", whose premise was
falsified on 2026-09-20.** Three mechanisms were tested on the 37-question
Arcwright set. All three overlap completely between in-scope and out-of-scope
questions:

| mechanism | out-of-scope | in-scope | separable? |
|---|---|---|---|
| absolute top score | 0.547 – 0.773 | 0.525 – 0.686 | no |
| peakedness (top ÷ mean of hits 2–8) | 1.088 – 1.436 | 1.026 – 1.278 | no |
| content-word coverage | 0.67 – 1.00 | 0.80 – 1.00 | no |

The reason is structural: 966,000 tokens of English prose contains nearly every
common English word, so "what is the best recipe for a French dessert?" finds
real matches for *recipe*, *best* and *traditional*. Only proper nouns miss.
Term statistics cannot express "this corpus does not cover this question", and
no threshold over them will.

**Refusal still happens — in the delivery path, not here.** Emitted agents are
instructed to read their documents and say so when those documents do not
answer. That is a judgement over actual content, and it is measured by the
Arcwright-side delegation eval in Task 19. `run-evals` measures the
deterministic harness, which the design establishes is not what ships.

**Files:**
- Modify: `src/evals/metrics.ts` (move the three harness metrics out of the gated set)
- Modify: `src/evals/run.ts` (`DEFAULT_GATES`, `REFUSE_THRESHOLD` and its comparison)
- Modify: `src/commands/run-evals.ts` (print it under diagnostics)
- Modify: `evals/gates.yaml` (team-ai's own reference copy of the defaults)
- Test: `src/evals/metrics.test.ts`
- Test: `src/commands/search.test.ts` — one absolute-score assertion
- Test: `src/evals/run.test.ts` — five tests here depend on what this task
  changes. Updating them is part of this change, not a widening of it.

**Acceptance Criteria:**
- [ ] `refusalRate`, `routingAccuracy` and `namespaceAccuracy` are reported but
      none of them gates the run
- [ ] All three print under a "diagnostics" heading; the gated set after this
      task is exactly `hitRate` and `citationValidity`. `coverage` is added by
      Task 6 and must not be pulled forward — each task has to verify and
      commit on its own
- [ ] `REFUSE_THRESHOLD` carries a comment recording the three measured
      distributions and why no value separates them
- [ ] A run whose only failing metrics are diagnostics exits 0
- [ ] No `gates.yaml`, in the framework or the instance, names a metric that is
      no longer gated
- [ ] The whole `src/evals/` suite passes — *Verify:* `npx vitest run src/evals/`
      reports 0 failures
- [ ] The word-boundary routing test still expects `platform-sme`

**Verify:** `node ../team-ai/dist/cli.js run-evals --root team-ai --json | python -c "import sys,json;r=json.load(sys.stdin);print('gated:', sorted(r['gates']))"` → exactly `['citationValidity', 'hitRate']`

**Steps:**

- [ ] **Step 1: Write the failing test**

Add to `src/evals/metrics.test.ts`:

```ts
it("reports refusalRate without gating on it", () => {
  const outcomes = [
    outcome({ id: "a", refuseExpected: true, refuseCorrect: false }),
  ];
  const report = computeReport(outcomes, DEFAULT_GATES);
  expect(report.metrics.refusalRate).toBe(0);
  expect(report.gates.refusalRate).toBeUndefined();
  expect(report.pass).toBe(true);
});
```

- [ ] **Step 2: Run to confirm failure**

Run: `cd ../team-ai && npx vitest run src/evals/metrics.test.ts`
Expected: FAIL — `refusalRate` currently gates and the report fails.

- [ ] **Step 3: Remove all three harness metrics from the gates**

`refusalRate`, `routingAccuracy` and `namespaceAccuracy` all describe the
deterministic harness, which the design establishes is not the delivery path.
Step 4 prints all three as diagnostics, so all three must leave the gate set —
gating on a metric while labelling it "not gated" is the inconsistency this
task exists to remove.

In `src/evals/run.ts`, drop `refusalRate`, `routingAccuracy` and
`namespaceAccuracy` from `DEFAULT_GATES`, from the `GateThresholds` type, and
from `loadGates`. What remains gated is `hitRate`, `citationValidity` and
`coverage` — the three that describe whether the knowledge base can answer.
Replace the `REFUSE_THRESHOLD` comment with the measured finding:

```ts
// Measured against a 37-question golden set on a ~966,000-token corpus: no
// threshold over term statistics separates answerable from unanswerable
// questions at that scale. Out-of-scope top scores ran 0.547-0.773 against
// in-scope 0.525-0.686; peakedness and content-word coverage overlap likewise.
// A corpus that large contains nearly every common English word, so an
// unrelated question still finds real matches. Refusal is a judgement over
// retrieved content, made by the agent in the delivery path and measured
// instance-side, not by this harness. The threshold below only suppresses
// genuinely empty result sets.
const REFUSE_THRESHOLD = 0.2;
```

- [ ] **Step 4: Print it as a diagnostic**

In `src/commands/run-evals.ts`, move `refusalRate`, `routingAccuracy` and
`namespaceAccuracy` out of the gated table into a diagnostics block printed
after it, labelled:

```ts
  console.log("");
  console.log("diagnostics (reported, not gated — these describe the");
  console.log("deterministic harness, which is not the delivery path):");
```

- [ ] **Step 5: Correct the refusal threshold to match its new job**

Task 4 divides BM25 relevance by the query's term count, which lowers every
absolute score. `REFUSE_THRESHOLD = 0.2` was calibrated against the old scale,
so a correctly-routed query can now fall under it. Verified on the fixture
knowledge base: `routeQuestion("how does our cryptography key rotation work")`
returns `__refuse__` at 0.2 and routes correctly to `platform-sme` at a
near-zero threshold.

Since refusal is no longer a lexical decision, the threshold's only remaining
job is to suppress genuinely empty result sets. In `src/evals/run.ts`:

```ts
// Refusal is not decidable from term statistics (see the design document, M6),
// so this no longer expresses "too weak to answer" — it only rejects a
// non-match. `scoreFromBm25` returns exactly 0 when FTS5 reports no match, and
// `sanitizeQuery` returns null for a query with no content word, so a strict
// `>` here means: refuse when nothing matched at all, and otherwise route.
const REFUSE_THRESHOLD = 0;
```

and change the comparison from `>=` to `>`:

```ts
  if (top !== undefined && top.score > REFUSE_THRESHOLD) {
```

- [ ] **Step 6: Update the five dependent tests in `src/evals/run.test.ts`**

Three encode the old gate set and are a straightforward contract update. Two
depend on the old threshold and need judgement:

| test | what to do |
|---|---|
| `loadGates > returns the shipped defaults when no gates.yaml is present` | drop all three demoted metrics from the expectation |
| `loadGates > reads overrides from <instance>/evals/gates.yaml` | drop the demoted overrides and their assertions |
| `loadGates > keeps the reference evals/gates.yaml in sync with DEFAULT_GATES` | remove all three demoted metrics from `evals/gates.yaml` at the team-ai repo root, so the file and the defaults agree again. **Stage that file in Step 8** — the test reads the working tree, so an unstaged fix passes locally and fails in CI |
| `routeQuestion > matches keywords on word boundaries, not as interior substrings` | **leave the expectation alone.** It asserts `platform-sme`, and after Step 5 it gets it. Its purpose is to prove a keyword does not fire as an interior substring; changing it to expect `__refuse__` would record a regression as intended behaviour |
| `routeQuestion > refuses when the stub search top hit is below the 0.2 threshold` | rewrite. "Below 0.2" is no longer a behaviour this code has. Change the stub's score to `0` and rename it to `refuses when the top hit is a non-match`, which is the behaviour that survives |
| `src/commands/search.test.ts > search > prints ranked lines for a relevant query` | asserts a top score above `0.5`; Task 4's rescaling makes it 0.46. The ranking assertion still passes, so only the absolute floor is stale. Do not simply lower the number — replace the floor with a relative assertion: a relevant query's top score must exceed the top score for a nonsense query. That survives the next rescaling too |

**The rule for every one of these:** a test may be changed when it encodes a
contract this task deliberately replaced. A test may never be changed to make a
regression look intended. If you cannot say which of the two a failure is, stop
and ask — that distinction is the whole value of the suite.

- [ ] **Step 7: Remove the stale instance override**

Delete `refusalRate`, `routingAccuracy` and `namespaceAccuracy` from
`team-ai/evals/gates.yaml` in the Arcwright instance, so the file does not
claim to set gates that no longer exist. Task 7 rewrites this file later; its
template has been kept in step with this change.

- [ ] **Step 8: Run and commit**

```bash
cd ../team-ai && npx vitest run src/evals/ && npm run build && cd -
node ../team-ai/dist/cli.js run-evals --root team-ai
cd ../team-ai && git add src/evals src/commands/run-evals.ts evals/gates.yaml && git commit -m "fix(evals): refusal is a delivery-path judgement, not a lexical gate"
```

---

### Task 6: Add the coverage metric

**Repository:** team-ai

**Goal:** `run-evals` reports, per domain, whether each question's `answer_evidence` still exists in a document of the expected namespace — a regression test on the knowledge base itself.

**Files:**
- Modify: `src/evals/metrics.ts` (`EvalOutcome`, `EvalReport`, `computeReport`)
- Modify: `src/evals/run.ts` (`runGoldenFile`)
- Modify: `src/commands/run-evals.ts` (`printReport`)
- Test: `src/evals/metrics.test.ts`

**Acceptance Criteria:**
- [ ] Each outcome carries `covered: boolean | null` (`null` when the question has no `answer_evidence`)
- [ ] `coverage` is reported overall and per expected namespace
- [ ] Deleting an evidence phrase from its source makes that question uncovered
- [ ] Questions whose source changed since `generated_on` are listed as needing review
- [ ] Coverage is reported separately for read-everything and retrieval domains
- [ ] `coverage` joins the gated set, which becomes exactly `hitRate`,
      `citationValidity` and `coverage` — the three that describe whether the
      knowledge base can answer

**Verify:** `node ../team-ai/dist/cli.js run-evals --root team-ai` → prints a `coverage` row and a per-namespace table, and `node ../team-ai/dist/cli.js run-evals --root team-ai --json | python -c "import sys,json;r=json.load(sys.stdin);print('gated:', sorted(r['gates']))"` → exactly `['citationValidity', 'coverage', 'hitRate']`

**Steps:**

- [ ] **Step 1: Write the failing test**

`src/evals/metrics.test.ts` already has an `outcome(overrides)` helper and its
own local `DEFAULT_GATES`. Add the three new fields to the helper's defaults
and `coverage: 0.8` to that local gates object, then add this test:

```ts
it("reports coverage overall and per namespace", () => {
  const outcomes = [
    outcome({ id: "a", expectNamespace: "kg", covered: true }),
    outcome({ id: "b", expectNamespace: "kg", covered: false }),
    outcome({ id: "c", expectNamespace: "safety", covered: true }),
    outcome({ id: "d", expectNamespace: "", covered: null }),
  ];
  const report = computeReport(outcomes, DEFAULT_GATES);
  expect(report.metrics.coverage).toBeCloseTo(2 / 3, 10);
  expect(report.coverageByNamespace["kg"]).toBeCloseTo(0.5, 10);
  expect(report.coverageByNamespace["safety"]).toBeCloseTo(1, 10);
});
```

The helper's added defaults:

```ts
    covered: null,
    expectNamespace: "domain",
    sourceChangedSinceGenerated: false,
```

- [ ] **Step 2: Run to confirm failure**

Run: `cd ../team-ai && npx vitest run src/evals/metrics.test.ts`
Expected: FAIL — `coverage` is not defined.

- [ ] **Step 3: Compute coverage in the runner**

In `src/evals/run.ts`, inside `runGoldenFile`'s question loop, before pushing the outcome:

```ts
      const evidence = question.answer_evidence;
      let covered: boolean | null = null;
      if (evidence !== undefined && evidence.length > 0) {
        const needle = evidence.toLowerCase();
        covered = docs.some(
          (doc) =>
            doc.frontmatter.namespace === question.expect_namespace &&
            doc.body.toLowerCase().includes(needle),
        );
      }

      const source = question.source_path;
      const generatedOn = question.generated_on;
      const sourceChangedSinceGenerated =
        source !== undefined && generatedOn !== undefined
          ? sourceChangedSince(scope.root, source, generatedOn)
          : false;
```

Add all three — `covered`, `expectNamespace: question.expect_namespace`, and
`sourceChangedSinceGenerated` — to the pushed outcome object, and declare them
on `EvalOutcome` in Step 4. `sourceChangedSince` is defined in Step 6.

- [ ] **Step 4: Aggregate in metrics**

In `src/evals/metrics.ts`, add three fields to `EvalOutcome`:

```ts
  covered: boolean | null;
  expectNamespace: string;
  sourceChangedSinceGenerated: boolean;
```

plus `coverage: number` to the metrics and `coverageByNamespace: Record<string, number>` to `EvalReport`. In `computeReport`:

```ts
  const scored = outcomes.filter((o) => o.covered !== null);
  const coverage = scored.length === 0 ? 1 : scored.filter((o) => o.covered).length / scored.length;

  const byNs: Record<string, number> = {};
  for (const ns of new Set(scored.map((o) => o.expectNamespace))) {
    const group = scored.filter((o) => o.expectNamespace === ns);
    byNs[ns] = group.filter((o) => o.covered).length / group.length;
  }
```

Add `coverage` to the returned metrics and `coverageByNamespace: byNs` to the report.

- [ ] **Step 5: Print it**

In `src/commands/run-evals.ts`, add `gateRow("coverage", metrics.coverage)` to `rows`, and after the metric table:

```ts
  console.log("");
  console.log("coverage by namespace:");
  for (const [ns, value] of Object.entries(report.coverageByNamespace).sort()) {
    console.log(`  ${ns.padEnd(24)} ${pct(value)}`);
  }
```

Add `coverage: 0.8` to `DEFAULT_GATES` in `src/evals/run.ts` and to `GateThresholds` and `loadGates`.

- [ ] **Step 6: Flag questions whose source changed**

In `src/commands/run-evals.ts`, after the coverage table:

```ts
  const staleQuestions = report.outcomes.filter((o) => o.sourceChangedSinceGenerated);
  if (staleQuestions.length > 0) {
    console.log("");
    console.log("questions whose source document changed since they were written:");
    for (const o of staleQuestions) console.log(`  ${o.id}`);
  }
```

In `run.ts`, set that flag by comparing `generated_on` against the source's last commit date:

```ts
import { execFileSync } from "node:child_process";

function sourceChangedSince(root: string, path: string, since: string): boolean {
  try {
    const out = execFileSync("git", ["log", "-1", "--format=%cs", "--", path], {
      cwd: root,
      encoding: "utf8",
    }).trim();
    return out.length > 0 && out > since;
  } catch {
    return false;
  }
}
```

- [ ] **Step 7: Run and commit**

```bash
cd ../team-ai && npx vitest run src/evals/ && npm run build && cd -
node ../team-ai/dist/cli.js run-evals --root team-ai
cd ../team-ai && git add src/evals src/commands/run-evals.ts && git commit -m "feat(evals): coverage metric with per-namespace breakdown"
```

---

### Task 7: Record the post-fix measurement and set ratcheted gates

**Repository:** Arcwright

**Goal:** The improvement is recorded as a before-and-after, and gate thresholds are set from the measured result rather than guessed.

**Files:**
- Create: `team-ai/evals/measured-2026-09-20.json`
- Modify: `team-ai/evals/gates.yaml`
- Modify: `docs/superpowers/specs/2026-09-20-team-ai-agent-architecture-phase-b-design.md` (record the numbers)

**Acceptance Criteria:**
- [ ] Before and after numbers are recorded side by side
- [ ] Each gate is set at or just below the measured value, never above
- [ ] A comment in `gates.yaml` states the thresholds ratchet upward only
- [ ] The design document records whether semantic retrieval is still needed (D-B2)

**Verify:** `node ../team-ai/dist/cli.js run-evals --root team-ai` → exits 0

**Steps:**

- [ ] **Step 1: Measure**

```bash
node ../team-ai/dist/cli.js run-evals --root team-ai --json > team-ai/evals/measured-2026-09-20.json
python - <<'PY'
import json
b=json.load(open('team-ai/evals/baseline-2026-09-20.json'))['metrics']
a=json.load(open('team-ai/evals/measured-2026-09-20.json'))['metrics']
print(f"{'metric':22}{'before':>10}{'after':>10}")
for k in sorted(set(b)|set(a)):
    if isinstance(b.get(k),(int,float)) and isinstance(a.get(k),(int,float)):
        print(f"{k:22}{b[k]:>10.3f}{a[k]:>10.3f}")
PY
```

- [ ] **Step 2: Set the gates**

Edit `team-ai/evals/gates.yaml` to the measured values, rounded down to the nearest 0.05:

```yaml
# Thresholds are set from measurement, not guessed, and ratchet upward only.
# Never lower a value to make a run pass — that removes the signal.
# Measured 2026-09-20 after the lexical scoring fix. Before/after in
# team-ai/evals/baseline-2026-09-20.json and measured-2026-09-20.json.
hitRate: <MEASURED>
citationValidity: 1.0
coverage: <MEASURED>
```

Only these three are gated. `routingAccuracy`, `namespaceAccuracy` and
`refusalRate` are diagnostics after Task 5 and must not reappear here —
listing them would re-add gates that `GateThresholds` and `loadGates` no longer
have, and silently undo Task 5.

- [ ] **Step 3: Record the conditional-semantic decision**

Add the before/after table to the design document under *Measurements*, and state plainly whether hit rate is now adequate. If it is not, note which domains still miss — that is the scope of any future semantic work.

- [ ] **Step 4: Commit**

```bash
git add team-ai/evals/ docs/superpowers/specs/2026-09-20-team-ai-agent-architecture-phase-b-design.md
git commit -m "test(evals): post-fix measurement and ratcheted gate thresholds"
```

---

### Task 8: Measure hit rate at two other chunk sizes

**Repository:** Arcwright

**Goal:** The chunk size is a measured choice rather than an inherited default.

**Files:**
- Modify: `team-ai/index.lock` (temporarily, then set to the winner)
- Create: `team-ai/evals/chunk-sweep-2026-09-20.md`

**Acceptance Criteria:**
- [ ] Hit rate is recorded at target sizes 400, 800 and 1200
- [ ] The chosen size is the best measured, and `index.lock` holds it
- [ ] The comparison is committed

**Verify:** `cat team-ai/evals/chunk-sweep-2026-09-20.md` → shows three rows with hit rates

**Steps:**

- [ ] **Step 1: Sweep**

```bash
for n in 400 800 1200; do
  python - "$n" <<'PY'
import sys,re,pathlib
n=sys.argv[1]
p=pathlib.Path('team-ai/index.lock'); t=p.read_text(encoding='utf-8')
t=re.sub(r'target_tokens: \d+', f'target_tokens: {n}', t)
p.write_text(t,encoding='utf-8')
PY
  node ../team-ai/dist/cli.js reindex --root team-ai >/dev/null
  echo -n "target_tokens=$n  "
  node ../team-ai/dist/cli.js run-evals --root team-ai --json | python -c "import sys,json;m=json.load(sys.stdin)['metrics'];print('hitRate',round(m['hitRate'],3),'coverage',round(m['coverage'],3))"
done
```

- [ ] **Step 2: Write up and set the winner**

Record the three rows in `team-ai/evals/chunk-sweep-2026-09-20.md`, set `target_tokens` in `team-ai/index.lock` to the best, reindex, and re-run `run-evals` to confirm it still passes. If 800 wins, say so — a confirmed default is a result.

- [ ] **Step 3: Commit**

```bash
git add team-ai/index.lock team-ai/evals/chunk-sweep-2026-09-20.md
git commit -m "test(evals): chunk size chosen by measurement"
```

---

### Task 9: Per-domain retrieval strategy in the emitter

**Repository:** team-ai

**Goal:** A domain whose whole corpus is small tells its agent to read everything; a large one tells it to use ranked search. Uniform strategy is wrong at both ends of a 232-to-609,458-token range.

**Files:**
- Modify: `src/commands/emit.ts` (compute corpus sizes for the one path that needs them)
- Modify: `src/emit/claude-code.ts` (`searchSection`)
- Test: `src/emit/claude-code.test.ts`

**Acceptance Criteria:**
- [ ] `corpusTokens` is an option on the claude-code emitter, not a field on
      `EmitInput`, and is computed only for `--target claude-code --builtin-search`
- [ ] `loadEmitInput` still reads no knowledge base, so `mcp-only` and `generic`
      emits keep working on an instance that has none
- [ ] A missing or unreadable knowledge base fails loudly on the path that needs
      it, and never silently reports zero tokens
- [ ] A tier-2 group SME (`max_hops > 0`) is told to delegate, and is given
      neither ranked search nor a read-everything instruction over its aggregate
- [ ] A specialist whose namespaces total under the threshold reads every document
- [ ] A specialist above it runs the ranked search command, scoped to its namespaces
- [ ] The threshold is a named constant with the rationale in a comment
- [ ] The router agent's section is unchanged

**Verify:** `cd ../team-ai && npx vitest run src/emit/claude-code.test.ts` → all pass

**Steps:**

- [ ] **Step 1: Write the failing tests**

Add to `src/emit/claude-code.test.ts`:

```ts
it("tells a small-corpus agent to read every document", () => {
  const out = emitClaudeCode(
    inputWith({ name: "knowledge-graph-sme", kb_namespaces: ["knowledge-graph"] }, { "knowledge-graph": 1926 }),
    tmpDir,
    { builtinSearch: true },
  );
  const body = readFileSync(out[0], "utf8");
  expect(body).toContain("Read every one of them");
  expect(body).not.toContain("cli.js search");
});

it("tells a large-corpus agent to use ranked search", () => {
  const out = emitClaudeCode(
    inputWith({ name: "engineering-practice-sme", kb_namespaces: ["engineering-practice"] }, { "engineering-practice": 609458 }),
    tmpDir,
    { builtinSearch: true },
  );
  const body = readFileSync(out[0], "utf8");
  expect(body).toContain("cli.js search");
  expect(body).toContain("--namespace engineering-practice");
});
```

- [ ] **Step 2: Run to confirm failure**

Run: `cd ../team-ai && npx vitest run src/emit/claude-code.test.ts`
Expected: FAIL.

- [ ] **Step 3: Add corpus sizes to the emit input**

**Do not put this on `EmitInput` and do not load it in `loadEmitInput`.**
`commands/emit.ts` calls `loadEmitInput(dir)` once, before it dispatches on
target, so a knowledge-base load there would make every `mcp-only` and
`generic` emit fail on an instance that has no `kb/` — and would break the
twelve existing emitter tests, whose fixture deliberately has none.

Corpus size is needed by exactly one path: `--target claude-code` with
`--builtin-search`. Scope the dependency to it.

Add the map to `EmitClaudeCodeOptions` in `src/emit/claude-code.ts`:

```ts
export interface EmitClaudeCodeOptions {
  filePrefix?: string;
  pluginManifest?: boolean;
  builtinSearch?: boolean;
  corpusTokens?: Record<string, number>;
}
```

Then in `src/commands/emit.ts`, compute it only on that path and fail loudly if
the knowledge base cannot be read — a silent zero would tell a
609,000-token domain to read its whole corpus:

```ts
import { loadKb } from "../kb/loader.js";
import { resolveKbScope } from "../retrieval/index-lock.js";

// Token counts drive the per-domain retrieval strategy in the emitters. A
// 4-chars-per-token estimate is accurate enough to pick a strategy and costs
// nothing; the exact figure never matters, only which side of the threshold
// a namespace falls.
async function corpusTokensByNamespace(instanceDir: string): Promise<Record<string, number>> {
  // Let a missing or unreadable KB throw. Reporting zero here would emit
  // "read your whole corpus" instructions to a 609,000-token domain.
  const scope = resolveKbScope(instanceDir);
  const docs = await loadKb(scope.root, { exclude: scope.exclude });
  const out: Record<string, number> = {};
  for (const doc of docs) {
    const ns = doc.frontmatter.namespace;
    if (typeof ns !== "string") continue;
    out[ns] = (out[ns] ?? 0) + Math.ceil(doc.body.length / 4);
  }
  return out;
}
```

Call it from `run` in `src/commands/emit.ts`, only for the path that needs it:

```ts
  const corpusTokens =
    target === "claude-code" && opts.builtinSearch === true
      ? await corpusTokensByNamespace(dir)
      : undefined;
```

and pass it through to `emitClaudeCode(input, outResolved, { ..., corpusTokens })`.

In `searchSection`, treat an absent map as a programming error rather than an
empty corpus:

```ts
  const sizes = corpusTokens ?? {};
  const total = namespaces.reduce((sum, ns) => sum + (sizes[ns] ?? 0), 0);
```

is **wrong** — it silently yields the read-everything branch. Require it:

```ts
  if (corpusTokens === undefined) {
    throw new Error("builtin-search emit requires corpus sizes; none were computed");
  }
```

**The tests need no knowledge-base fixture.** They pass `corpusTokens` directly
as an option, which is what the tests in Step 1 already assume.

- [ ] **Step 4: Branch the search section**

In `src/emit/claude-code.ts`, replace the subagent branch of `searchSection`:

```ts
// A domain small enough to read outright needs no retrieval step at all:
// reading gives perfect recall, cannot miss on paraphrase, and costs less than
// searching. Above this size the corpus cannot be read and ranked search is the
// only option. 25,000 tokens sits comfortably inside a subagent's context
// alongside its task.
//
// The threshold applies only to agents that OWN content. A tier-2 group SME
// (max_hops > 0) delegates: its hand-authored instructions say "delegate a
// single-domain question to that domain's specialist", and every specialist
// beneath it already carries the right strategy for its own corpus. Summing a
// group's namespaces and handing it ranked search would give practice-sme an
// 873,000-token search it never needs, because the content is always one hop
// away.
const READ_ALL_TOKEN_LIMIT = 25_000;

function searchSection(agent: EmitAgent, corpusTokens: Record<string, number>): string {
  const common = [
    "## Search procedure",
    "",
    "The knowledge base is the Markdown under the KB root in `team-ai/index.lock`.",
    "",
  ];
  if (agent.def.kind === "router") {
    // unchanged — see existing router branch
  }

  const namespaces = agent.def.kb_namespaces;

  // Tier-2 group SME: delegate rather than search or read an aggregate corpus.
  if (agent.def.max_hops > 0) {
    return [
      ...common,
      "You delegate. You do not search your group's corpus yourself.",
      "",
      "- Read `team-ai/manifest.yaml` and find which of your domains owns the question.",
      `- Your domains: ${namespaces.join(", ")}.`,
      "- Hand off to that domain's subagent and stop.",
      "- Only when a question genuinely spans two of your domains, delegate to",
      "  both and reconcile their cited answers. Never answer from memory.",
      "- If none of your domains owns it, say so and name the likely owner.",
    ].join("
");
  }
  const total = namespaces.reduce((sum, ns) => sum + (corpusTokens[ns] ?? 0), 0);
  const listing = namespaces
    .map((ns) => `- Grep the KB root for \`^namespace: ${ns}\` to list your documents.`)
    .join("\n");

  if (total <= READ_ALL_TOKEN_LIMIT) {
    return [
      ...common,
      "Use Read, Grep and Glob.",
      "",
      listing,
      "",
      `Your whole corpus is about ${total.toLocaleString()} tokens. Read every one of them before answering — do not guess which is relevant, and do not answer from a grep match alone.`,
      "",
      "Answer only from those documents, citing paths. If they do not answer the question, say so and name the owner.",
    ].join("\n");
  }

  const nsFlags = namespaces.map((ns) => `--namespace ${ns}`).join(" ");
  return [
    ...common,
    `Your corpus is about ${total.toLocaleString()} tokens — far too large to read. Use ranked search:`,
    "",
    "```bash",
    `node ../team-ai/dist/cli.js search "<the question, in full>" --root team-ai ${nsFlags} --k 8`,
    "```",
    "",
    "Read the files behind the top hits, then answer only from them, citing paths.",
    "Grep is a fallback for an exact string you already know, not a way to find relevant material — it misses any wording the document does not use.",
    "",
    "If nothing scores above the threshold, say you do not know and name the owner.",
  ].join("\n");
}
```

`frontMatter` receives a single agent (`EmitInput["agents"][number]`), and the
corpus sizes now arrive on `opts`, so no extra parameter is needed — read
them from the options it already has:

```ts
function frontMatter(
  input: EmitInput["agents"][number],
  opts: EmitClaudeCodeOptions,
): string {
  const body =
    opts.builtinSearch === true
      ? searchSection(input, opts.corpusTokens)
      : input.instructions.trim();
```

Its call site inside `emitClaudeCode` is unchanged.

- [ ] **Step 5: Run to confirm all pass**

Run: `cd ../team-ai && npx vitest run src/emit/`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
cd ../team-ai && git add src/emit src/commands/emit.ts && git commit -m "feat(emit): choose retrieval strategy per domain by corpus size"
```

---

### Task 10: Stop emitting instructions for tools that do not exist

**Repository:** team-ai

**Goal:** Remove the `## Original instructions` block in built-in-search mode — 43% of every emitted agent, telling it to call three tools that do not exist.

**Files:**
- Modify: `src/emit/claude-code.ts` (`frontMatter`, around line 89)
- Test: `src/emit/claude-code.test.ts`

**Acceptance Criteria:**
- [ ] With `builtinSearch: true`, the emitted body is the search section alone
- [ ] Without it, the original instructions are emitted unchanged
- [ ] No emitted file mentions `kb_manifest`, `kb_search` or `kb_coverage_gap`

**Verify:** `cd ../team-ai && npx vitest run src/emit/claude-code.test.ts` → all pass

**Steps:**

- [ ] **Step 1: Write the failing test**

```ts
it("omits the original instructions in builtin-search mode", () => {
  const out = emitClaudeCode(inputWithKbTools(), tmpDir, { builtinSearch: true });
  const body = readFileSync(out[0], "utf8");
  expect(body).not.toContain("Original instructions");
  expect(body).not.toContain("kb_search");
  expect(body).toContain("## Search procedure");
});

it("keeps the original instructions when not in builtin-search mode", () => {
  const out = emitClaudeCode(inputWithKbTools(), tmpDir, { builtinSearch: false });
  expect(readFileSync(out[0], "utf8")).toContain("kb_search");
});
```

- [ ] **Step 2: Run to confirm failure**

Run: `cd ../team-ai && npx vitest run src/emit/claude-code.test.ts`
Expected: the first test FAILS.

- [ ] **Step 3: Implement**

In `src/emit/claude-code.ts`, replace the body expression in `frontMatter`:

```ts
  // In builtin-search mode the agent has Read/Grep/Glob and none of the MCP
  // tools the authored instructions name, so emitting them tells the agent to
  // call things that do not exist — 43% of every file, and an invitation to
  // fabricate a tool call. The search section fully replaces them.
  const body =
    opts.builtinSearch === true
      ? searchSection(input, opts.corpusTokens)
      : input.instructions.trim();
```

Task 9 already put `corpusTokens` on `EmitClaudeCodeOptions`, so this line is
the same one that task leaves behind. If Task 9 is done, the only change here
is deleting the `## Original instructions` concatenation around it.

Also drop the now-false clause in `searchSection`'s `common` array: `"Use Read, Grep, and Glob to search it. The tool names under Original instructions are unavailable."` — Task 9 already replaced it per branch.

- [ ] **Step 4: Run and commit**

```bash
cd ../team-ai && npx vitest run src/emit/ && npm run build
git add src/emit && git commit -m "fix(emit): stop emitting instructions for tools that do not exist"
```

---

### Task 11: Regenerate Arcwright's agents and scope the search permission

**Repository:** Arcwright

**Goal:** The 17 emitted agents carry the right strategy for their role and no dead block, and exactly the three agents named in sign-off B-S2 can run the search command and nothing else.

**Files:**
- Modify: `.claude/agents/team-ai-*.md` (regenerated, 17 files)
- Modify: `.claude/settings.json`
- Modify: `.github/workflows/team-ai.yml` (pin `ref: v0.6.0`)

**Acceptance Criteria:**
- [ ] No emitted agent mentions `kb_manifest`, `kb_search` or `kb_coverage_gap`
- [ ] The split is exactly 3 specialists searching, 10 specialists reading,
      3 group SMEs delegating and 1 router routing — 17 emitted agents
      — *Verify:* `grep -l "cli.js search" .claude/agents/team-ai-*.md | wc -l` → `3`
- [ ] `engine-sme`, `practice-sme` and `title-sme` are told to delegate, and
      none of them mentions `cli.js search`. Summing a group's namespaces would
      push all three over the threshold; they own no content, so the threshold
      does not apply to them and sign-off B-S2 is not exceeded
- [ ] `engineering-practice-sme`, `product-roadmap-sme` and `nightcap-sme` are told to use ranked search
- [ ] `.claude/settings.json` permits the search command only, not general
      shell access, and no agent outside B-S2's three needs it
- [ ] Regenerating produces no diff

**Verify:** `node ../team-ai/dist/cli.js emit --target claude-code --dir team-ai --out .. --file-prefix team-ai- --no-plugin-manifest --builtin-search --allow-tracked && git diff --exit-code -- .claude/agents` → exit 0

**Steps:**

- [ ] **Step 1: Regenerate**

```bash
node ../team-ai/dist/cli.js emit --target claude-code --dir team-ai --out .. --file-prefix team-ai- --no-plugin-manifest --builtin-search --allow-tracked
git diff --stat -- .claude/agents
```
Expected: 17 files changed, each substantially smaller.

- [ ] **Step 2: Check the strategy split**

```bash
grep -L "cli.js search" .claude/agents/team-ai-*.md | wc -l   # expect 14 (11 small + router + 2 group SMEs as applicable)
grep -l "cli.js search" .claude/agents/team-ai-*.md            # expect the large-corpus agents
grep -l "kb_search\|kb_manifest\|kb_coverage_gap" .claude/agents/ -r || echo "no dead tool references"
```

- [ ] **Step 3: Add the scoped permission**

In `.claude/settings.json`, inside `permissions.allow`:

```json
      "Bash(node ../team-ai/dist/cli.js search:*)"
```

This permits the search subcommand only. Do not add a bare `Bash(node:*)`.

- [ ] **Step 4: Pin CI to the new framework version**

Tag team-ai `v0.6.0` and update `.github/workflows/team-ai.yml`:

```yaml
          ref: v0.6.0
```

- [ ] **Step 5: Confirm regeneration is stable and commit**

```bash
git add .claude/agents          # snapshot the first emit; HEAD is not the baseline yet
node ../team-ai/dist/cli.js emit --target claude-code --dir team-ai --out .. --file-prefix team-ai- --no-plugin-manifest --builtin-search --allow-tracked
git diff --exit-code -- .claude/agents && echo "stable"
git add .claude/agents .claude/settings.json .github/workflows/team-ai.yml
git commit -m "feat(agents): per-domain retrieval strategy; drop dead tool instructions"
```

---

## Part 2 — Enforcement checks

### Task 12: provider-leak-check

**Repository:** Arcwright

**Goal:** A script that fails when a provider or model name appears outside the two permitted files, passing on a clean tree with no exception list.

**Files:**
- Create: `scripts/checks/provider_leak_check.py`
- Create: `scripts/checks/tests/test_provider_leak_check.py`
- Modify: `engine/safety/l3.py:196` (one comment)

**Acceptance Criteria:**
- [ ] Scans `engine/`, `api/`, `sdk/`, `dashboard/`, `config/`, skipping test files
- [ ] Permits `config/routing_table.json` and `engine/routing/router.py`
- [ ] Exits 0 on the current tree after the comment reword
- [ ] Exits non-zero on a planted violation, naming file and line
- [ ] No allowlist or exception file exists

**Verify:** `python scripts/checks/provider_leak_check.py` → exit 0, `python -m pytest scripts/checks/tests/ -q` → pass

**Steps:**

- [ ] **Step 1: Write the failing test**

Create `scripts/checks/tests/test_provider_leak_check.py`:

```python
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "checks" / "provider_leak_check.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT
    )


def test_passes_on_clean_tree():
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr


def test_fails_on_planted_violation(tmp_path):
    planted = ROOT / "engine" / "session" / "_leak_probe.py"
    planted.write_text('MODEL = "anthropic/claude-haiku-4-5-20251001"\n', encoding="utf-8")
    try:
        result = run()
        assert result.returncode != 0
        assert "_leak_probe.py" in result.stdout
    finally:
        planted.unlink()


def test_permits_the_two_routing_files():
    result = run()
    assert "routing_table.json" not in result.stdout
    assert "routing/router.py" not in result.stdout
```

- [ ] **Step 2: Run to confirm failure**

Run: `python -m pytest scripts/checks/tests/test_provider_leak_check.py -q`
Expected: FAIL — the script does not exist.

- [ ] **Step 3: Write the script**

Create `scripts/checks/provider_leak_check.py`:

```python
"""Fail when a provider or model name appears outside the two permitted files.

AGENTS.md confines provider and model names to config/routing_table.json and
engine/routing/router.py. The rule is commercial: names confined to two files
make switching providers a settings edit rather than a codebase hunt.

Test files are out of scope by design. A test of the router's environment
mapping must name the real variable to prove the mapping; importing the name
from the router would make the test pass whatever the router did.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SCAN_DIRS = ("engine", "api", "sdk", "dashboard", "config")
SCAN_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".yaml", ".yml"}

PERMITTED = {
    Path("config/routing_table.json"),
    Path("engine/routing/router.py"),
}

SKIP_DIR_PARTS = {"node_modules", "__pycache__", ".venv", "dist", "build", "tests"}

TERMS = (
    "anthropic", "groq", "openai", "cohere", "mistral", "bedrock", "vertex",
    "claude-", "gpt-", "llama-", "gemini-", "sonnet", "haiku", "opus",
)
PATTERN = re.compile("|".join(re.escape(t) for t in TERMS), re.IGNORECASE)


def is_test_path(path: Path) -> bool:
    name = path.name
    return (
        name.startswith("test_")
        or name.endswith("_test.py")
        or ".test." in name
        or ".spec." in name
    )


def scan() -> list[str]:
    findings: list[str] = []
    for directory in SCAN_DIRS:
        base = ROOT / directory
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
                continue
            if SKIP_DIR_PARTS & set(path.parts):
                continue
            if is_test_path(path):
                continue
            rel = path.relative_to(ROOT)
            if rel in PERMITTED:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for number, line in enumerate(text.splitlines(), start=1):
                if PATTERN.search(line):
                    findings.append(f"{rel.as_posix()}:{number}: {line.strip()}")
    return findings


def main() -> int:
    findings = scan()
    if findings:
        print("provider-leak-check: provider or model name outside the permitted files")
        for finding in findings:
            print(f"  {finding}")
        print("\nPermitted: config/routing_table.json, engine/routing/router.py")
        return 1
    print("provider-leak-check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Reword the one real violation**

In `engine/safety/l3.py` line 196, change `Anthropic's` to `the provider's`:

```python
    the provider's `cache_control`.  Merging the policy into that message means
```

This is the single `engine/` change in Phase B and requires the founder sign-off recorded in the design document.

- [ ] **Step 5: Run to confirm pass**

```bash
python scripts/checks/provider_leak_check.py
python -m pytest scripts/checks/tests/test_provider_leak_check.py -q
```
Expected: `provider-leak-check: OK`, tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/checks/provider_leak_check.py scripts/checks/tests/test_provider_leak_check.py engine/safety/l3.py
git commit -m "feat(checks): provider-leak-check with no exception list"
```

---

### Task 13: scope-evidence-check

**Repository:** Arcwright

**Goal:** Every cited decision id and ADR reference resolves to a real record, and newly added specs and roadmap tasks declare their approval evidence.

**Files:**
- Modify (team-ai): `schemas/frontmatter.schema.json`, `src/schema/validate.test.ts`
- Create: `scripts/checks/scope_evidence_check.py`
- Create: `scripts/checks/tests/test_scope_evidence_check.py`
- Modify: `docs/specs/0000-template.md` (add the field)
- Modify: `docs/roadmap/tasks/` template or convention doc (add the field)

**Acceptance Criteria:**
- [ ] Parses the CSV properly — `D-034`, whose row is quoted, resolves
- [ ] Normalises zero-padding so `D-45` and `D-045` are the same id
- [ ] Reports zero dangling references on the current tree
- [ ] Fails on a fabricated `D-999`
- [ ] Requires `x-scope-evidence` on files added against the base branch, accepting `none`
- [ ] `validate-kb` still passes on every document carrying the new field
- [ ] Does not fail existing files that lack the field

**Verify:** `python scripts/checks/scope_evidence_check.py --base main` → exit 0

**Steps:**

- [ ] **Step 0 (team-ai): let instances add their own front-matter fields**

`schemas/frontmatter.schema.json` sets `additionalProperties: false`, so an
instance cannot add any field of its own — `validate-kb` rejects the document.
That is a framework limitation, not a problem with this field: every instance
that ever wants its own metadata hits it.

Fix it generically, reserving an `x-` prefix for instance extensions. Keep
`additionalProperties: false` so a misspelled core field (`reviewby:`) is still
caught — only keys that explicitly announce themselves as extensions are
allowed through:

```json
  "patternProperties": {
    "^x-[a-z0-9-]+$": {}
  },
```

Add it alongside `properties` in `schemas/frontmatter.schema.json`. Do **not**
add `scope-evidence` itself to the framework schema — Arcwright's approval
process is instance content, and the framework must not learn about it.

Test in `src/schema/validate.test.ts`:

```ts
it("allows instance extension fields under the x- prefix", () => {
  expect(validate("frontmatter", { ...validFrontMatter(), "x-scope-evidence": "none" }).ok)
    .toBe(true);
});

it("still rejects a misspelled core field", () => {
  expect(validate("frontmatter", { ...validFrontMatter(), reviewby: "2027-01-01" }).ok)
    .toBe(false);
});
```

Verify: `cd ../team-ai && npx vitest run src/schema/ && npm run build`, then
from Arcwright `node ../team-ai/dist/cli.js validate-kb --instance team-ai`.

Commit in team-ai: `feat(kb): reserve the x- prefix for instance front-matter fields`

- [ ] **Step 1: Write the failing test**

Create `scripts/checks/tests/test_scope_evidence_check.py`:

```python
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "checks" / "scope_evidence_check.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT
    )


def test_clean_tree_has_no_dangling_references():
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr


def test_resolves_a_quoted_csv_row():
    # D-034's row is quoted in the CSV; a line-based grep misses it.
    result = run("--explain", "D-034")
    assert "resolved" in result.stdout


def test_normalises_zero_padding():
    result = run("--explain", "D-45")
    assert "resolved" in result.stdout


def test_fails_on_a_fabricated_id():
    planted = ROOT / "docs" / "specs" / "9999-probe.md"
    planted.write_text("Approved per D-999.\n", encoding="utf-8")
    try:
        result = run()
        assert result.returncode != 0
        assert "D-999" in result.stdout
    finally:
        planted.unlink()
```

- [ ] **Step 2: Run to confirm failure**

Run: `python -m pytest scripts/checks/tests/test_scope_evidence_check.py -q`
Expected: FAIL — the script does not exist.

- [ ] **Step 3: Write the script**

Create `scripts/checks/scope_evidence_check.py`:

```python
"""Verify that claimed approval evidence points at records that exist.

Two checks:

1. Reference integrity — every D-NNN and ADR-NNNN reference under docs/specs/
   and docs/roadmap/ resolves to a real record.
2. Declared evidence — specs and roadmap tasks added in this change set carry a
   `x-scope-evidence` front-matter field naming their approval record, or the
   literal `none` meaning the document claims no new product scope.

Detecting a scope *claim* is reading comprehension and out of reach for a
plain script; verifying a claimed *citation* is not, and catches the realistic
failure: an agent inventing a plausible decision id.

Two things this must get right, both found by building it:
  - Decision ids sit as a prefix inside the CSV's quoted `Decision` column, so
    the CSV must be parsed. A line-based grep falsely reports 10 failures,
    including the heavily-cited D-034.
  - Citations are inconsistently zero-padded (D-45 against D-045).
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DECISIONS_CSV = ROOT / "docs" / "product" / "decisions-log.csv"
ADR_DIR = ROOT / "docs" / "decisions"
SCAN_DIRS = (ROOT / "docs" / "specs", ROOT / "docs" / "roadmap")

DECISION_REF = re.compile(r"\bD-(\d+)\b")
ADR_REF = re.compile(r"\bADR[- ]?(\d{4})\b")
ADR_PATH_REF = re.compile(r"docs/decisions/(\d{4})-")
FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)
SCOPE_EVIDENCE = re.compile(r"^x-scope-evidence:\s*(.+?)\s*$", re.MULTILINE)


def normalise(number: str) -> str:
    return f"D-{int(number):03d}"


def known_decision_ids() -> set[str]:
    ids: set[str] = set()
    with DECISIONS_CSV.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            match = re.match(r"\s*D-(\d+)", row.get("Decision") or "")
            if match:
                ids.add(normalise(match.group(1)))
    return ids


def known_adr_ids() -> set[str]:
    return {path.name[:4] for path in ADR_DIR.glob("[0-9][0-9][0-9][0-9]-*.md")}


def markdown_files() -> list[Path]:
    files: list[Path] = []
    for directory in SCAN_DIRS:
        if directory.exists():
            files.extend(sorted(directory.rglob("*.md")))
    return files


def check_references() -> list[str]:
    decisions, adrs = known_decision_ids(), known_adr_ids()
    problems: list[str] = []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT).as_posix()
        for number in DECISION_REF.findall(text):
            if normalise(number) not in decisions:
                problems.append(f"{rel}: cites D-{number}, which is not in decisions-log.csv")
        for number in set(ADR_REF.findall(text)) | set(ADR_PATH_REF.findall(text)):
            if number not in adrs:
                problems.append(f"{rel}: cites ADR {number}, which has no file in docs/decisions/")
    return problems


def added_files(base: str) -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=A", f"{base}...HEAD"],
            capture_output=True, text=True, cwd=ROOT, check=True,
        ).stdout
    except subprocess.CalledProcessError:
        return []
    paths = []
    for line in out.splitlines():
        path = ROOT / line.strip()
        if path.suffix == ".md" and any(
            str(path).startswith(str(d)) for d in SCAN_DIRS
        ):
            paths.append(path)
    return paths


def check_declared_evidence(base: str) -> list[str]:
    decisions, adrs = known_decision_ids(), known_adr_ids()
    problems: list[str] = []
    for path in added_files(base):
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        front = FRONT_MATTER.search(text)
        field = SCOPE_EVIDENCE.search(front.group(1)) if front else None
        if field is None:
            problems.append(
                f"{rel}: new document has no `x-scope-evidence` field "
                f"(name the approving record, or `none` if it claims no new product scope)"
            )
            continue
        value = field.group(1).strip().strip("\"'")
        if value.lower() == "none":
            continue
        cited = False
        for number in DECISION_REF.findall(value):
            cited = True
            if normalise(number) not in decisions:
                problems.append(f"{rel}: x-scope-evidence cites D-{number}, which does not exist")
        for number in set(ADR_REF.findall(value)) | set(ADR_PATH_REF.findall(value)):
            cited = True
            if number not in adrs:
                problems.append(f"{rel}: x-scope-evidence cites ADR {number}, which does not exist")
        if not cited:
            problems.append(f"{rel}: x-scope-evidence names no D-NNN or ADR reference and is not `none`")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=None, help="base ref for the added-files check")
    parser.add_argument("--explain", default=None, help="report whether one id resolves")
    args = parser.parse_args()

    if args.explain:
        match = DECISION_REF.search(args.explain)
        if match:
            target = normalise(match.group(1))
            print(f"{args.explain} -> {target}: "
                  f"{'resolved' if target in known_decision_ids() else 'NOT FOUND'}")
            return 0
        print(f"{args.explain}: not a decision id")
        return 1

    problems = check_references()
    if args.base:
        problems += check_declared_evidence(args.base)

    if problems:
        print("scope-evidence-check: failed")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("scope-evidence-check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Add the field to the templates**

In `docs/specs/0000-template.md` front matter, after `source: authored`:

```yaml
x-scope-evidence: none
```

with a line in the body under *References*:

> **x-scope-evidence** — the approving record for any new product scope this spec
> claims (`D-NNN`, `ADR-NNNN`, or several). Use `none` when the document claims
> no new product scope. Checked by `scripts/checks/scope_evidence_check.py`.

Do the same for the roadmap task template if one exists; otherwise record the
convention in `docs/roadmap/README.md`.

- [ ] **Step 5: Run to confirm pass**

```bash
python scripts/checks/scope_evidence_check.py
python scripts/checks/scope_evidence_check.py --base main
python -m pytest scripts/checks/tests/test_scope_evidence_check.py -q
```
Expected: `scope-evidence-check: OK` both times, tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/checks/scope_evidence_check.py scripts/checks/tests/test_scope_evidence_check.py docs/specs/0000-template.md
git commit -m "feat(checks): scope-evidence-check for reference integrity and declared evidence"
```

---

### Task 14: knowledge-query-guard

**Repository:** Arcwright

**Goal:** A function that generates character speech must look up that character's knowledge first. Narration and mini-game resolution are not characters and must not be caught.

**Files:**
- Create: `scripts/checks/knowledge_query_guard.py`
- Create: `scripts/checks/tests/test_knowledge_query_guard.py`

**Acceptance Criteria:**
- [ ] Parses `engine/` with `ast`, not regex
- [ ] Flags a function calling `generate()` with `task_type="character_dialogue"` and no prior `build_character_generation_context()` in the same function body
- [ ] Does not flag `mini_games/resolver.py` or `narrator/bridge.py`
- [ ] Exits 0 on the current tree
- [ ] Reports file, line and function name on failure

**Verify:** `python scripts/checks/knowledge_query_guard.py` → exit 0

**Steps:**

- [ ] **Step 1: Write the failing test**

Create `scripts/checks/tests/test_knowledge_query_guard.py`:

```python
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "checks" / "knowledge_query_guard.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT
    )


def test_passes_on_clean_tree():
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr


def test_does_not_flag_non_character_generation():
    result = run()
    assert "resolver.py" not in result.stdout
    assert "bridge.py" not in result.stdout


def test_flags_unguarded_character_generation():
    planted = ROOT / "engine" / "characters" / "_guard_probe.py"
    planted.write_text(
        "from engine.routing import generate\n\n"
        "async def speak(db, session_id):\n"
        "    return await generate(db, session_id=session_id, "
        'task_type="character_dialogue", messages=[])\n',
        encoding="utf-8",
    )
    try:
        result = run()
        assert result.returncode != 0
        assert "_guard_probe.py" in result.stdout
        assert "speak" in result.stdout
    finally:
        planted.unlink()
```

- [ ] **Step 2: Run to confirm failure**

Run: `python -m pytest scripts/checks/tests/test_knowledge_query_guard.py -q`
Expected: FAIL — the script does not exist.

- [ ] **Step 3: Write the script**

Create `scripts/checks/knowledge_query_guard.py`:

```python
"""Require a knowledge-state query before every AI character generation.

AGENTS.md: "Knowledge state queries are mandatory before every AI character
generation (non-negotiable)."

Four call sites in engine/ generate text outside the routing module. Only the
two passing task_type="character_dialogue" produce character speech;
narrative_generation (mini-game resolution) and narrator_bridge (narration) are
not characters and must not be caught by this rule.

The check walks the AST rather than matching text, so a call split across lines
or renamed via keyword order is still seen.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "engine"

GUARDED_TASK_TYPE = "character_dialogue"
GENERATE_NAMES = {"generate", "route_generation"}
KNOWLEDGE_QUERY = "build_character_generation_context"
SKIP_DIR_PARTS = {"__pycache__", "tests"}


def call_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def is_guarded_generation(node: ast.Call) -> bool:
    if call_name(node) not in GENERATE_NAMES:
        return False
    for keyword in node.keywords:
        if keyword.arg == "task_type" and isinstance(keyword.value, ast.Constant):
            return keyword.value.value == GUARDED_TASK_TYPE
    return False


def check_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int | None:
    """Return the line of an unguarded generation, or None if the function is fine."""
    knowledge_lines = [
        child.lineno
        for child in ast.walk(node)
        if isinstance(child, ast.Call) and call_name(child) == KNOWLEDGE_QUERY
    ]
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and is_guarded_generation(child):
            if not any(line < child.lineno for line in knowledge_lines):
                return child.lineno
    return None


def scan() -> list[str]:
    problems: list[str] = []
    for path in sorted(ENGINE.rglob("*.py")):
        if SKIP_DIR_PARTS & set(path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                line = check_function(node)
                if line is not None:
                    problems.append(
                        f"{rel}:{line}: {node.name}() generates character dialogue "
                        f"without calling {KNOWLEDGE_QUERY}() first"
                    )
    return problems


def main() -> int:
    problems = scan()
    if problems:
        print("knowledge-query-guard: failed")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("knowledge-query-guard: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run to confirm pass**

```bash
python scripts/checks/knowledge_query_guard.py
python -m pytest scripts/checks/tests/test_knowledge_query_guard.py -q
```
Expected: `knowledge-query-guard: OK`, tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/checks/knowledge_query_guard.py scripts/checks/tests/test_knowledge_query_guard.py
git commit -m "feat(checks): knowledge-query-guard for character generation"
```

---

### Task 14b: Make the cost tier real instead of declared

**Repository:** team-ai, then Arcwright

**Goal:** Emitted agents carry a `model` the host actually reads, so the
`model_tier` every domain already declares stops being inert.

**Why this is not cosmetic.** All 14 domains declare `model_tier: small` and the
router declares `none`. The emitter writes `model_tier` into agent front
matter, but that is team-ai's own vocabulary — Claude Code reads `name`,
`description`, `tools` and `model`. Nothing sets `model`, so all 17 agents run
on the session default, which is the most expensive option available, while the
architecture marks every one of them as cheap-tier work. `AGENTS.md` principle 6
says the opposite in as many words: *"Do not default to the best available
frontier model when a cheaper model meets the quality bar."*

These agents grep a namespace, read documents, and answer with citations. That
is the task a small fast model is for. One mapping fixes all 17, and it saves
on every invocation from then on rather than once.

**This must land before Task 15 cuts the tag.** It is a framework change, so a
tag cut before it gives CI an emitter that does not set `model`.

> **Unblocked: D-B13 approved 2026-09-20.** Setting `model` puts a model alias
> into every `.claude/agents/team-ai-*.md`. That is within the rule, not an
> exemption to it: principle 8 scopes itself to platform operations and model
> calls, and `provider-leak-check` already scans product code only, never
> `.claude/`. Development tooling is outside the rule; the product's runtime
> inference is not. See D-B13 in the design document.

**Files:**
- Modify (team-ai): `src/emit/claude-code.ts` (the `meta` object, around line 132)
- Test (team-ai): `src/emit/claude-code.test.ts`
- Modify: `.claude/agents/team-ai-*.md` (regenerated, 17 files)

**Acceptance Criteria:**
- [ ] The emitter maps `model_tier` to the host's `model` field
- [ ] The mapping lives in team-ai, so no model name enters Arcwright's docs,
      which `docs/README.md` forbids
- [ ] Every emitted agent carries a `model` line
- [ ] The values are ones Claude Code documents as valid — confirmed from its
      documentation, not assumed from this plan
- [ ] `model_tier` is still emitted, so the generated file stays traceable to
      its source definition
- [ ] Regenerating produces no diff
- [ ] One agent dispatches after the merge — *Verify:* in a Claude Code
      session, ask a specialist to reply "OK" without reading files; a reply
      proves the front matter parsed. No knowledge-base content is involved

**Verify:** `grep -L "^model:" .claude/agents/team-ai-*.md | wc -l` → `0`

**Steps:**

- [ ] **Step 1: Confirm the accepted values before writing any**

This plan deliberately does not name them. Check Claude Code's own subagent
documentation for what `model` accepts — tier aliases and any inherit-style
value — and use those exact strings. If a value is wrong the host may ignore
the field silently, which would leave the tier just as inert as it is now while
looking fixed.

Record what you confirmed, and where, in the commit message.

- [ ] **Step 2: Write the failing test**

In `src/emit/claude-code.test.ts`:

```ts
it("maps the model tier onto the host's model field", () => {
  const out = emitClaudeCode(inputWithTier("small"), tmpDir, { builtinSearch: true });
  expect(readFileSync(out[0], "utf8")).toMatch(/^model: \S+$/m);
});

it("gives a large-tier agent a different model from a small-tier one", () => {
  const small = readFileSync(
    emitClaudeCode(inputWithTier("small"), tmpDir, { builtinSearch: true })[0], "utf8");
  const large = readFileSync(
    emitClaudeCode(inputWithTier("large"), tmpDir2, { builtinSearch: true })[0], "utf8");
  const pick = (s: string) => /^model: (\S+)$/m.exec(s)?.[1];
  expect(pick(small)).not.toBe(pick(large));
});
```

- [ ] **Step 3: Run to confirm failure**

Run: `cd ../team-ai && npx vitest run src/emit/claude-code.test.ts`
Expected: FAIL — no `model` line is emitted.

- [ ] **Step 4: Add the mapping**

In `src/emit/claude-code.ts`, above `frontMatter`, using the values confirmed in
Step 1:

```ts
// Claude Code reads `model`; `model_tier` is team-ai's own vocabulary and is
// inert to the host. Mapping one onto the other is what makes a declared cost
// tier real. `none` means the work needs no model judgement at all, so it takes
// the cheapest tier rather than being omitted — an absent `model` inherits the
// session default, which is the expensive outcome this mapping exists to avoid.
const MODEL_FOR_TIER: Record<ModelTier, string> = {
  none: "<cheapest alias>",
  small: "<cheapest alias>",
  large: "<capable alias>",
};
```

and add it to the `meta` object beside `model_tier`:

```ts
    model: MODEL_FOR_TIER[input.def.model_tier],
```

- [ ] **Step 5: Run to confirm all pass**

Run: `cd ../team-ai && npx vitest run src/emit/ && node dist/cli.js check-agnostic`
Expected: PASS, and `check-agnostic: OK`.

- [ ] **Step 6: Regenerate Arcwright's agents**

```bash
cd ../team-ai && npm run build && cd -
node ../team-ai/dist/cli.js emit --target claude-code --dir team-ai --out .. --file-prefix team-ai- --no-plugin-manifest --builtin-search --allow-tracked
grep -L "^model:" .claude/agents/team-ai-*.md | wc -l      # expect 0
git diff --stat -- .claude/agents                           # expect 17 files, one line each
```

Then confirm regeneration is stable:

```bash
git add .claude/agents          # snapshot the first emit; HEAD is not the baseline yet
node ../team-ai/dist/cli.js emit --target claude-code --dir team-ai --out .. --file-prefix team-ai- --no-plugin-manifest --builtin-search --allow-tracked
git diff --exit-code -- .claude/agents && echo stable
```

- [ ] **Step 7: Confirm an agent still dispatches — run this in Claude Code, not here**

The risk is narrow: an unknown or malformed front-matter value can make the host
skip an agent, and a silently skipped agent looks exactly like a working one
until someone needs it.

Proving that needs **no knowledge-base content**. Dispatch one specialist with a
prompt that requires reading nothing:

> Reply with the single word OK. Do not read any files.

A reply proves the front matter parsed and the agent is dispatchable. Whether
it answers *correctly* from the corpus is a different question, already measured
by the coverage metric (Task 6) and the delegation eval (Task 19) — do not
re-test it here.

**This step is not the implementer's.** It exercises a Claude Code feature, so
it belongs in a Claude Code session, and the regenerated agents have to be
committed and merged before one can load them. Commit Step 6's output, hand
over, and let the founder's Claude Code session run the dispatch check after
the merge.

- [ ] **Step 8: Commit**

```bash
cd ../team-ai && git add src/emit && git commit -m "feat(emit): map model tier onto the host's model field"
cd - && git add .claude/agents && git commit -m "feat(agents): emit the declared cost tier as a model"
```

---

### Task 15: Wire the three checks into CI

**Repository:** Arcwright

**Goal:** All three checks and the eval gate run on every pull request and block merge on failure.

**Files:**
- Modify: `.github/workflows/team-ai.yml`

**Acceptance Criteria:**
- [ ] All three checks run on pull requests
- [ ] `scope-evidence-check` receives the pull request's base branch
- [ ] `run-evals` runs and its exit code blocks merge
- [ ] Checker unit tests run
- [ ] The pinned team-ai tag exists on GitHub and contains every framework
      change this phase made — *Verify:* `git ls-remote --tags origin v0.6.0`
      from the team-ai clone returns a sha, and that sha's
      `schemas/frontmatter.schema.json` contains `patternProperties`

**Verify:** the local commands below all pass. The workflow itself cannot be
confirmed until a branch reaches GitHub, so that check happens when Phase B's
pull request opens — not mid-phase, and not by pushing a detached worktree

**Steps:**

- [ ] **Step 1: Add the steps**

Append to the `team-ai` job in `.github/workflows/team-ai.yml`:

```yaml
      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"
      - name: checker unit tests
        run: python -m pytest scripts/checks/tests/ -q
      - name: provider-leak-check
        run: python scripts/checks/provider_leak_check.py
      - name: knowledge-query-guard
        run: python scripts/checks/knowledge_query_guard.py
      - name: scope-evidence-check
        run: python scripts/checks/scope_evidence_check.py --base origin/${{ github.base_ref || 'main' }}
      - name: eval gate
        run: node .team-ai-cli/dist/cli.js run-evals --root team-ai
```

The checkout needs history for the base comparison, so add to the first `actions/checkout@v4`:

```yaml
        with:
          fetch-depth: 0
```

- [ ] **Step 1b: Publish team-ai, or CI cannot see any of this work**

Everything Phase B changed in team-ai lives in a local clone. Arcwright's CI
checks the framework out **from GitHub by tag**:

```yaml
      - uses: actions/checkout@v4
        with:
          repository: nickejanssen/team-ai
          ref: v0.6.0
```

so an unpushed commit or tag does not exist as far as CI is concerned, and the
job fails at checkout rather than at a test. Local green proves nothing here.

The tag must also contain every framework change this phase made — including
the front-matter extension from Task 13. Tagging before that commit gives CI a
schema that rejects `x-scope-evidence` while the local build accepts it.

**The tag follows the merge, it does not precede it.** team-ai lands every
change through a squash PR, so merging produces a *new* commit on `main` with a
SHA that does not exist on the feature branch. Tagging before the merge points
`v0.6.0` at a commit `main` never contains, and CI checks out the tag.

The framework work is also not on `main` — it accumulates on a feature branch.
Check before assuming: `git rev-parse --abbrev-ref HEAD`.

```bash
cd ../team-ai
git log --oneline origin/main..HEAD          # every commit CI still cannot see
git push origin HEAD:refs/heads/feat/<name>  # a new branch, never a force push
gh pr create --base main --head feat/<name> --title "..." --body "..."
# after CI passes and the PR is squash-merged:
git fetch origin
git tag -f v0.6.0 origin/main                # the merged commit, not the branch tip
git push -f origin v0.6.0
```

Then verify what CI will actually receive, by fetching the tag the way CI does
rather than trusting the local clone:

```bash
git clone --depth 1 --branch v0.6.0 https://github.com/nickejanssen/team-ai.git /tmp/tagcheck
cd /tmp/tagcheck && npm ci && npm run build && node dist/cli.js check-agnostic
cd <arcwright> && node /tmp/tagcheck/dist/cli.js validate-kb --instance team-ai
```

**Force-pushing the tag is safe only while it has never been published.** Once
it has, cut `v0.6.1` and bump the workflow instead of moving it.

**Founder approval required before this push.** It is a publish to the
framework repository, and everything after it depends on the tag being correct.

*Completed 2026-09-20:* team-ai PR #8 squash-merged as `86c7503`; `v0.6.0`
re-pointed there and pushed; the tag verified by fresh clone, build,
`check-agnostic`, and `validate-kb` against Arcwright.

- [ ] **Step 2: Verify locally first**

```bash
python -m pytest scripts/checks/tests/ -q
python scripts/checks/provider_leak_check.py
python scripts/checks/knowledge_query_guard.py
python scripts/checks/scope_evidence_check.py --base main
node ../team-ai/dist/cli.js run-evals --root team-ai
```
Expected: all pass.

- [ ] **Step 3: Commit and push**

```bash
git add .github/workflows/team-ai.yml
git commit -m "ci: run the three enforcement checks and the eval gate"
git push
```

---

## Part 3 — Hooks

### Task 16: PreToolUse and PostToolUse

**Repository:** Arcwright

**Goal:** Block edits to generated files, and record which paths each session writes — as raw fact, not interpretation.

**Files:**
- Create: `scripts/hooks/block_generated_writes.py`
- Create: `scripts/hooks/record_observation.py`
- Create: `scripts/hooks/tests/test_hooks.py`
- Modify: `.claude/settings.json`

**Acceptance Criteria:**
- [ ] A write to `.claude/agents/team-ai-*.md` is blocked with a message naming the regeneration command
- [ ] A write to `docs/` is allowed
- [ ] Each write appends one JSON line to `team-ai/graph/observations/<YYYY-MM>/<session-id>.jsonl`
- [ ] The record contains only session id, timestamp and path — no edge type or weight
- [ ] Each hook honours its own enable flag
- [ ] Two branches that each recorded observations merge without conflict

**Verify:** `python -m pytest scripts/hooks/tests/ -q` → pass

**Steps:**

- [ ] **Step 1: Write the failing test**

Create `scripts/hooks/tests/test_hooks.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BLOCK = ROOT / "scripts" / "hooks" / "block_generated_writes.py"
RECORD = ROOT / "scripts" / "hooks" / "record_observation.py"


def run(script, payload):
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload), capture_output=True, text=True, cwd=ROOT,
    )


def test_blocks_generated_agent_write():
    result = run(BLOCK, {"tool_input": {"file_path": ".claude/agents/team-ai-sme.md"}})
    assert result.returncode != 0
    assert "emit" in result.stdout + result.stderr


def test_allows_ordinary_doc_write():
    result = run(BLOCK, {"tool_input": {"file_path": "docs/specs/0089-x.md"}})
    assert result.returncode == 0


def test_records_one_raw_line(tmp_path):
    result = run(RECORD, {
        "session_id": "probe-session",
        "tool_input": {"file_path": "docs/specs/0089-x.md"},
    })
    assert result.returncode == 0
    written = list((ROOT / "team-ai" / "graph" / "observations").rglob("probe-session.jsonl"))
    assert written, "no observation file written"
    record = json.loads(written[0].read_text(encoding="utf-8").splitlines()[-1])
    assert set(record) == {"session_id", "at", "path"}
    written[0].unlink()
```

- [ ] **Step 2: Run to confirm failure**

Run: `python -m pytest scripts/hooks/tests/test_hooks.py -q`
Expected: FAIL — neither script exists.

- [ ] **Step 3: Write the guard**

Create `scripts/hooks/block_generated_writes.py`:

```python
"""Block edits to generated files and agent-local directories.

Emitted agents are regenerated from team-ai/; hand-editing one is silently
undone on the next emit, and CI only catches it afterwards. Blocking the write
turns a late CI failure into an immediate message.
"""

from __future__ import annotations

import fnmatch
import json
import os
import sys

BLOCKED = (
    (".claude/agents/team-ai-*.md",
     "Generated from team-ai/. Edit team-ai/agents/<name>.md, then run:\n"
     "  node ../team-ai/dist/cli.js emit --target claude-code --dir team-ai "
     "--out .. --file-prefix team-ai- --no-plugin-manifest --builtin-search --allow-tracked"),
    ("team-ai/manifest.yaml",
     "Generated by assemble-manifest. Edit team-ai/agents/manifest.fragment.yaml instead."),
)


def main() -> int:
    if os.environ.get("ARCWRIGHT_HOOK_BLOCK_GENERATED", "1") != "1":
        return 0
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    path = str(payload.get("tool_input", {}).get("file_path", "")).replace("\\", "/")
    if not path:
        return 0
    for pattern, message in BLOCKED:
        if fnmatch.fnmatch(path, f"*{pattern}") or fnmatch.fnmatch(path, pattern):
            print(f"Refusing to edit {path}\n{message}")
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Write the recorder**

Create `scripts/hooks/record_observation.py`:

```python
"""Record one raw fact per write: which session touched which path, and when.

Deliberately records no edge type, no weight and no relationship. A statement
that "this session touched these paths" cannot be wrong, so Phase C derives
edges from it rather than being forced to reshape a format guessed here.

Files are sharded per session and only ever appended to by the session that
owns them, so two branches cannot conflict on the same file.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OBSERVATIONS = ROOT / "team-ai" / "graph" / "observations"


def main() -> int:
    if os.environ.get("ARCWRIGHT_HOOK_RECORD_OBSERVATIONS", "1") != "1":
        return 0
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    path = str(payload.get("tool_input", {}).get("file_path", "")).replace("\\", "/")
    session_id = str(payload.get("session_id", "")) or "unknown"
    if not path:
        return 0
    try:
        path = Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return 0  # outside the repository; not ours to record

    now = datetime.now(timezone.utc)
    target = OBSERVATIONS / now.strftime("%Y-%m") / f"{session_id}.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    record = {"session_id": session_id, "at": now.isoformat(), "path": path}
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Register both hooks**

In `.claude/settings.json`, add:

```json
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "python scripts/hooks/block_generated_writes.py" }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "python scripts/hooks/record_observation.py" }]
      }
    ]
  }
```

Each script honours an environment flag, so a hook can be disabled without editing this file.

- [ ] **Step 6: Verify the merge property**

```bash
git checkout -b probe-a && python -c "
import json,subprocess,sys
subprocess.run([sys.executable,'scripts/hooks/record_observation.py'],input=json.dumps({'session_id':'a','tool_input':{'file_path':'docs/README.md'}}),text=True)"
git add team-ai/graph && git commit -q -m "probe a"
git checkout -q - && git checkout -qb probe-b && python -c "
import json,subprocess,sys
subprocess.run([sys.executable,'scripts/hooks/record_observation.py'],input=json.dumps({'session_id':'b','tool_input':{'file_path':'docs/README.md'}}),text=True)"
git add team-ai/graph && git commit -q -m "probe b"
git merge probe-a -m "probe merge" && echo "MERGED CLEANLY"
git checkout -q - && git branch -D probe-a probe-b
```
Expected: `MERGED CLEANLY`.

- [ ] **Step 7: Run tests and commit**

```bash
python -m pytest scripts/hooks/tests/ -q
git add scripts/hooks .claude/settings.json
git commit -m "feat(hooks): block generated writes and record raw observations"
```

---

### Task 16b: Resolve the framework CLI from anywhere in the repo

**Repository:** Arcwright, then team-ai

**Goal:** Nothing in the repository assumes the framework sits at `../team-ai`.
That path is correct only in the main checkout, and every session here runs in a
git worktree.

**Why.** Three things hardcode it, and the worst ships to the agents:

| where | consequence |
|---|---|
| The three large-domain agents' search command | An agent is told to run a path that does not exist, and will fail or improvise — the hallucination surface that removing the dead tool instructions existed to close |
| Task 17's hook scripts | A `Stop` hook that errors every session |
| `.claude/settings.json`'s permission string | Names a path that varies by checkout |

In a worktree, the repository's parent is the worktree container, not the
checkout's parent. `git rev-parse --git-common-dir` points at the *main*
repository's `.git` from anywhere, including a worktree, which is what makes
this solvable at all.

**Files:**
- Create: `scripts/team_ai_cli.py`
- Create: `scripts/tests/test_team_ai_cli.py`
- Modify (team-ai): `src/emit/claude-code.ts`, `src/commands/emit.ts`
- Modify: `.claude/agents/team-ai-*.md` (regenerated), `.claude/settings.json`

**Acceptance Criteria:**
- [ ] The resolver finds the CLI from the main checkout and from a worktree
- [ ] `TEAM_AI_CLI` overrides the search when set
- [ ] A missing CLI returns nothing rather than raising; callers decide
- [ ] No emitted agent contains `../team-ai`
- [ ] The settings permission names the resolver, not a framework path
- [ ] team-ai learns nothing about Arcwright — the command is passed in

**Verify:** from a worktree, `python scripts/team_ai_cli.py --path` prints an existing path

**Steps:**

- [ ] **Step 1: Write the failing test**

Create `scripts/tests/test_team_ai_cli.py`:

```python
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "team_ai_cli.py"


def test_resolves_from_this_checkout():
    out = subprocess.run([sys.executable, str(SCRIPT), "--path"],
                         capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr
    assert Path(out.stdout.strip()).exists()


def test_env_override_wins(tmp_path):
    fake = tmp_path / "cli.js"
    fake.write_text("", encoding="utf-8")
    env = {**os.environ, "TEAM_AI_CLI": str(fake)}
    out = subprocess.run([sys.executable, str(SCRIPT), "--path"],
                         capture_output=True, text=True, cwd=ROOT, env=env)
    assert out.stdout.strip() == str(fake)


def test_missing_cli_exits_nonzero_without_raising(tmp_path):
    env = {**os.environ, "TEAM_AI_CLI": str(tmp_path / "absent.js")}
    out = subprocess.run([sys.executable, str(SCRIPT), "--path"],
                         capture_output=True, text=True, cwd=ROOT, env=env)
    assert out.returncode != 0
    assert "Traceback" not in out.stderr
```

- [ ] **Step 2: Run to confirm failure**

Run: `python -m pytest scripts/tests/test_team_ai_cli.py -q`
Expected: FAIL — the script does not exist.

- [ ] **Step 3: Write the resolver**

Create `scripts/team_ai_cli.py`:

```python
"""Locate the team-ai CLI, and optionally run it.

`../team-ai` is correct only in the main checkout. Every agent session here runs
in a git worktree, where the repository's parent is the worktree container
rather than the checkout's parent. `git rev-parse --git-common-dir` points at
the main repository's `.git` from anywhere, including a worktree, so the
checkout's real sibling stays reachable from all of them.

Callers decide what a missing CLI means. Hooks must not fail because a sibling
checkout is absent: a check that breaks every session is worse than no check.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REL = Path("team-ai") / "dist" / "cli.js"


def _main_checkout() -> Path | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return None
    return Path(out).parent if out else None


def find_cli() -> Path | None:
    """Return the CLI path, or None. Never raises."""
    override = os.environ.get("TEAM_AI_CLI")
    if override:
        candidate = Path(override)
        return candidate if candidate.is_file() else None

    roots: list[Path] = []
    main = _main_checkout()
    if main is not None:
        roots.append(main.parent)
    here = Path(__file__).resolve().parents[1]
    roots.extend([here.parent, here.parent.parent])

    for root in roots:
        candidate = root / REL
        if candidate.is_file():
            return candidate
    return None


def main() -> int:
    args = sys.argv[1:]
    cli = find_cli()
    if cli is None:
        print("team-ai CLI not found. Set TEAM_AI_CLI, or clone team-ai beside "
              "this repository and run npm ci && npm run build.", file=sys.stderr)
        return 1
    if args[:1] == ["--path"]:
        print(cli)
        return 0
    return subprocess.run(["node", str(cli), *args]).returncode


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run to confirm all pass**

```bash
python -m pytest scripts/tests/test_team_ai_cli.py -q
python scripts/team_ai_cli.py --path
python scripts/team_ai_cli.py validate-kb --instance team-ai
```

- [ ] **Step 5: Let the emitter take the search command as an option**

The framework must not learn Arcwright's script name. In
`src/emit/claude-code.ts`, add `searchCommand?: string` to
`EmitClaudeCodeOptions`, default it to the current `node ../team-ai/dist/cli.js`
so other instances are unaffected, and use it where the search line is built. In
`src/commands/emit.ts`, add a `--search-command <cmd>` flag that passes it
through. Add an emitter test asserting a custom command appears in the output.

- [ ] **Step 6: Regenerate with the resolver, and fix the permission**

```bash
python scripts/team_ai_cli.py emit --target claude-code --dir team-ai --out .. --file-prefix team-ai- --no-plugin-manifest --builtin-search --allow-tracked --search-command "python scripts/team_ai_cli.py"
grep -l "team-ai/dist/cli.js" .claude/agents/team-ai-*.md || echo "no hardcoded framework paths"
```

In `.claude/settings.json`, replace the framework-path permission with the
resolver, which does not vary by checkout:

```json
      "Bash(python scripts/team_ai_cli.py search:*)"
```

Then confirm regeneration is stable, staging the first emit first as Task 11 does.

- [ ] **Step 7: Commit**

```bash
cd ../team-ai && git add src/emit src/commands/emit.ts && git commit -m "feat(emit): let the instance supply the search command"
cd - && git add scripts .claude/agents .claude/settings.json && git commit -m "feat(scripts): resolve the framework CLI from any checkout"
```

**The tag moves again — to a new number.** This is another framework change, so
`v0.6.0` no longer matches `main`. `v0.6.0` has been published, so it must not
be moved: cut `v0.6.1` after the merge and bump the workflow pin.

---

### Task 17: Stop and SessionStart as a non-blocking loop

**Repository:** Arcwright

**Goal:** `Stop` fires the validation and freshness checks detached and writes a snapshot; `SessionStart` reads that snapshot in milliseconds. Neither ever makes the founder wait.

**Files:**
- Create: `scripts/hooks/snapshot_knowledge_state.py`
- Create: `scripts/hooks/inject_session_context.py`
- Create: `team-ai/graph/freshness-baseline.json`
- Modify: `.claude/settings.json`

**Acceptance Criteria:**
- [ ] `Stop` returns immediately; the checks run detached
- [ ] The snapshot records validate-kb, validate-manifest and freshness results
- [ ] `SessionStart` injects the domain map plus the delta against the committed baseline, not the raw 436 orphaned count
- [ ] With the framework CLI absent, `Stop` still exits 0 and the next
      `SessionStart` reports that the checks did not run — *Verify:*
      `TEAM_AI_CLI=/nonexistent python scripts/hooks/snapshot_knowledge_state.py`,
      wait for the child, then run the injector and confirm it says so rather
      than reporting a clean knowledge base
- [ ] `SessionStart` completes in well under a second
- [ ] Both honour their enable flags
- [ ] If detachment proves unreliable on Windows, the documented fallback is used and recorded

**Verify:** `time python scripts/hooks/inject_session_context.py < /dev/null` → under 1 second

**Steps:**

- [ ] **Step 1: Commit the freshness baseline**

```bash
node ../team-ai/dist/cli.js freshness-audit --instance team-ai > team-ai/graph/freshness-baseline.json
python -c "import json;print(json.load(open('team-ai/graph/freshness-baseline.json'))['summary'])"
```
Expected: `{'total': 447, 'stale': 0, 'orphaned': 436, 'unowned': 0, ...}`.

- [ ] **Step 2: Write the snapshot script**

Create `scripts/hooks/snapshot_knowledge_state.py`:

```python
"""Run the knowledge-base checks detached and write a snapshot for the next session.

These are the same checks CI runs on every pull request. Running them
synchronously at session stop costs about 16 seconds each time and duplicates
CI. Running them detached costs nothing and still surfaces the result — the
next SessionStart reads the snapshot.

Verification note: if reliable detachment is not achievable on this platform,
fall back to running the checks only when the session touched docs/ or
team-ai/, and in parallel (about 6 seconds on those sessions, nothing on the
rest). Record which path is in use here.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from team_ai_cli import find_cli          # noqa: E402  (Task 16b)
SNAPSHOT = ROOT / "team-ai" / "graph" / "last-session-snapshot.json"


def run_checks() -> dict:
    # find_cli returns None rather than raising. A missing sibling checkout must
    # not break the session, but it must also not be reported as a clean run —
    # record that the checks could not execute and let SessionStart say so.
    cli = find_cli()
    if cli is None:
        return {
            "at": datetime.now(timezone.utc).isoformat(),
            "unavailable": "team-ai CLI not found; set TEAM_AI_CLI or build the framework",
        }

    def call(args: list[str]) -> tuple[int, str]:
        result = subprocess.run(
            ["node", str(cli), *args], capture_output=True, text=True, cwd=ROOT
        )
        return result.returncode, (result.stdout or result.stderr).strip()

    kb_code, kb_out = call(["validate-kb", "--instance", "team-ai"])
    mf_code, mf_out = call(["validate-manifest", "--root", "team-ai"])
    fr_code, fr_out = call(["freshness-audit", "--instance", "team-ai"])
    try:
        freshness = json.loads(fr_out)["summary"]
    except (json.JSONDecodeError, KeyError):
        freshness = {}
    return {
        "at": datetime.now(timezone.utc).isoformat(),
        "validate_kb": {"ok": kb_code == 0, "output": kb_out[-500:]},
        "validate_manifest": {"ok": mf_code == 0, "output": mf_out[-500:]},
        "freshness": freshness,
    }


def main() -> int:
    if os.environ.get("ARCWRIGHT_HOOK_SNAPSHOT", "1") != "1":
        return 0
    if os.environ.get("ARCWRIGHT_SNAPSHOT_CHILD") == "1":
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT.write_text(json.dumps(run_checks(), indent=2), encoding="utf-8")
        return 0

    # Re-invoke self detached so the session stop returns immediately.
    env = {**os.environ, "ARCWRIGHT_SNAPSHOT_CHILD": "1"}
    kwargs: dict = {"cwd": ROOT, "env": env,
                    "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if os.name == "nt":
        kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        )
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen([sys.executable, str(Path(__file__).resolve())], **kwargs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Write the injector**

Create `scripts/hooks/inject_session_context.py`:

```python
"""Inject the domain map and the last session's findings at session start.

Reads files only — no CLI calls — so it costs milliseconds rather than the six
seconds a freshness audit takes.

Freshness is reported as a delta against a committed baseline. The absolute
figures are 0 stale, 0 unowned and 436 orphaned of 447; printing 436 every
session is noise, while a change against it is a signal.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "team-ai" / "manifest.yaml"
SNAPSHOT = ROOT / "team-ai" / "graph" / "last-session-snapshot.json"
BASELINE = ROOT / "team-ai" / "graph" / "freshness-baseline.json"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> int:
    if os.environ.get("ARCWRIGHT_HOOK_SESSION_CONTEXT", "1") != "1":
        return 0

    lines: list[str] = []
    try:
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        manifest = {}
    domains = manifest.get("domains", [])
    if domains:
        lines.append("Knowledge domains and the agent that owns each:")
        for domain in domains:
            lines.append(f"  {domain['id']:24} -> {domain['subagent']}")

    snapshot = read_json(SNAPSHOT)
    if snapshot.get("unavailable"):
        lines.append("")
        lines.append(f"Knowledge-base checks did not run last session: {snapshot['unavailable']}")
    elif snapshot:
        problems = [
            name
            for name in ("validate_kb", "validate_manifest")
            if isinstance(snapshot.get(name), dict) and snapshot[name].get("ok") is False
        ]
        if problems:
            lines.append("")
            lines.append(f"Knowledge base FAILING as of last session: {', '.join(problems)}")

        baseline = read_json(BASELINE).get("summary", {})
        current = snapshot.get("freshness", {})
        deltas = [
            f"{key} {current[key] - baseline.get(key, 0):+d}"
            for key in ("stale", "orphaned", "unowned")
            if key in current and current[key] != baseline.get(key, 0)
        ]
        if deltas:
            lines.append(f"Freshness change since baseline: {', '.join(deltas)}")

    if lines:
        print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Register both hooks**

Extend the `hooks` object in `.claude/settings.json`:

```json
    "Stop": [
      { "hooks": [{ "type": "command", "command": "python scripts/hooks/snapshot_knowledge_state.py" }] }
    ],
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "python scripts/hooks/inject_session_context.py" }] }
    ]
```

- [ ] **Step 5: Verify timing and detachment**

```bash
# Stop must return immediately.
time python scripts/hooks/snapshot_knowledge_state.py
# Wait for the detached child, then confirm the snapshot landed.
sleep 20 && python -c "import json;print(json.load(open('team-ai/graph/last-session-snapshot.json'))['freshness'])"
# SessionStart must be fast.
time python scripts/hooks/inject_session_context.py
```
Expected: the first returns in well under a second; the snapshot exists afterwards; the third prints the domain map in well under a second.

If the snapshot never appears, detachment is not working on this platform. Switch to the documented fallback: run the checks synchronously, but only when `git status --porcelain docs team-ai` is non-empty, and in parallel. Record the change in the script's docstring and in the design document's risk section.

- [ ] **Step 6: Commit**

```bash
git add scripts/hooks .claude/settings.json team-ai/graph/freshness-baseline.json
git commit -m "feat(hooks): non-blocking knowledge-state loop between Stop and SessionStart"
```

---

## Part 4 — Command, delegation eval, and records

### Task 18: The /doc-review command

**Repository:** Arcwright

**Goal:** One command runs the freshness audit, explains what is stale in plain language, takes the founder's decision, and acts only on what was approved.

**Files:**
- Create: `.claude/commands/doc-review.md`

**Acceptance Criteria:**
- [ ] Runs the freshness audit and reports in plain language
- [ ] Presents findings and stops for a decision before changing anything
- [ ] Acts only on approved items
- [ ] Never infers approval from silence

**Verify:** Run `/doc-review` in a session → it reports and pauses without editing

**Steps:**

- [ ] **Step 1: Read an existing command for the house pattern**

```bash
cat .claude/commands/scribe.md
```

- [ ] **Step 2: Write the command**

Create `.claude/commands/doc-review.md`:

```markdown
---
description: Review which knowledge-base documents have gone stale and fix the ones approved
---

# Document currency review

## 1. Gather

Run the freshness audit and read the JSON:

```bash
node ../team-ai/dist/cli.js freshness-audit --instance team-ai
```

Its three categories mean:
- **stale** — past its `review_by` date
- **orphaned** — no `relations` entries connecting it to other documents
- **unowned** — no `owner` in its front matter

Compare against `team-ai/graph/freshness-baseline.json` and report the change,
not the absolute count. 436 of 447 documents are orphaned at baseline; that
number on its own is noise.

## 2. Report

For each stale document tell the founder, in plain language and without jargon:
- what the document is for
- why its being out of date matters, concretely
- what you would change

Do not use the words stale, orphaned or unowned without explaining them.

## 3. Stop

Present the list and ask which to act on. **Wait for an answer.** Never infer
approval from silence, and never act on an item that was not named.
`docs/conventions/human-collaboration.md` governs this gate.

## 4. Act

Update only the approved documents. For each, set a new `review_by` date and
make the content change actually needed — never only the date, which would
hide the staleness rather than resolve it.

## 5. Confirm

List what changed and what was deliberately left, and run:

```bash
node ../team-ai/dist/cli.js validate-kb --instance team-ai
```
```

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/doc-review.md
git commit -m "feat(commands): /doc-review for document currency"
```

---

### Task 19: Delegation eval

**Repository:** Arcwright

**Goal:** Measure the path that actually ships — which agent a model picks given the agent descriptions and a question.

**Files:**
- Create: `evals/delegation/run_delegation_eval.py`
- Create: `evals/delegation/README.md`

**Acceptance Criteria:**
- [ ] Reuses the committed golden questions, so no second question set is maintained
- [ ] Reports per question which agent was chosen and whether it matched `expect_route`
- [ ] Reports refusal behaviour on the out-of-scope questions
- [ ] Runs on demand only, never in the pull-request workflow
- [ ] Writes a dated report under `evals/reports/`

**Verify:** `python evals/delegation/run_delegation_eval.py --dry-run` → prints the prompt it would send, makes no model call

**Steps:**

- [ ] **Step 1: Write the runner**

Create `evals/delegation/run_delegation_eval.py`. It must:
1. Load `team-ai/evals/golden/arcwright.golden.yaml`.
2. Read each `.claude/agents/team-ai-*.md` front matter for `name` and `description` — this is exactly what the host shows a model when delegating.
3. For each question, send the agent list and the question through `engine.routing`'s abstraction with `task_type="pacing_decision"` and the cheapest quality tier, asking for one agent name or `__refuse__`.
4. Compare against `expect_route` and write a dated JSON report to `evals/reports/`.

Model selection goes through the routing abstraction. Do not name a provider or
model anywhere in this file — `provider_leak_check.py` scans `engine/` and
`api/`, but `AGENTS.md` applies everywhere.

- [ ] **Step 2: Document why it is separate**

In `evals/delegation/README.md`, record: this eval measures the delivery path
(a model choosing among agent descriptions), whereas `run-evals` measures the
deterministic harness. It costs model calls, so it runs on demand, which is
what keeps team-ai free of them.

- [ ] **Step 3: Dry run, then a real run**

```bash
python evals/delegation/run_delegation_eval.py --dry-run
python evals/delegation/run_delegation_eval.py
```

- [ ] **Step 4: Commit**

```bash
git add evals/delegation
git commit -m "test(evals): delegation eval over the emitted agent descriptions"
```

---

### Task 20: Update the records

**Repository:** Arcwright

**Goal:** Spec 0089 reflects what Phase B actually did, and the inaccurate `AGENTS.md` rule is corrected.

**Files:**
- Modify: `docs/specs/0089-team-ai-agent-architecture.md`
- Modify: `AGENTS.md`
- Modify: `.github/copilot-instructions.md` (mirror)
- Modify: `docs/superpowers/specs/2026-09-20-team-ai-agent-architecture-phase-b-design.md`

**Acceptance Criteria:**
- [ ] Spec 0089's Phase B section matches what was built, with the dropped items and reasons
- [ ] Phase B acceptance criteria are marked against the real outcome
- [ ] The Q1 open question is resolved or explicitly restated
- [ ] `AGENTS.md` states accurately which `.claude/` paths are tracked
- [ ] `.github/copilot-instructions.md` matches `AGENTS.md` exactly
- [ ] Spec 0089 carries a *Kill Criteria* section naming the conditions under
      which the agent layer is cut back, and stating that Phase C is one thing
      and there is no Phase D

**Verify:** `diff <(sed -n '/^# Agent Operating Guide/,$p' AGENTS.md) <(sed -n '/^# Agent Operating Guide/,$p' .github/copilot-instructions.md)` → no output

**Steps:**

- [ ] **Step 1: Correct the `.claude/` rule**

In `AGENTS.md`, replace the sentence claiming the exception "covers no other path under `.claude/`" with an accurate list. `.claude/settings.json`, `.claude/commands/`, `.claude/agents/implementer.md` and `.claude/agents/reviewer.md` are already tracked, and Phase B adds hook registration to `settings.json`:

```markdown
- Exception: these `.claude/` paths are intentionally tracked and may be changed
  when a task calls for it:
  - `.claude/agents/team-ai-*.md` — generated by `team-ai emit`; never edit by
    hand, always regenerate
  - `.claude/agents/implementer.md`, `.claude/agents/reviewer.md` — hand-authored
  - `.claude/commands/*.md` — hand-authored slash commands
  - `.claude/settings.json` — permissions and hook registration
  No other path under `.claude/` may be created, modified or committed.
```

- [ ] **Step 2: Mirror to Copilot**

```bash
python - <<'PY'
from pathlib import Path
agents = Path("AGENTS.md").read_text(encoding="utf-8")
body = agents[agents.index("# Agent Operating Guide"):]
mirror = Path(".github/copilot-instructions.md")
head = mirror.read_text(encoding="utf-8")
mirror.write_text(head[:head.index("# Agent Operating Guide")] + body, encoding="utf-8")
PY
diff <(sed -n '/^# Agent Operating Guide/,$p' AGENTS.md) <(sed -n '/^# Agent Operating Guide/,$p' .github/copilot-instructions.md) && echo "mirror matches"
```

- [ ] **Step 3: Update spec 0089**

Bump to v1.5. In the Phase B section, record what was built and what was
dropped with its reason (the table in the design document's *What Phase B does
not build*). Tick the Phase B acceptance criteria that hold, and replace those
that no longer apply — the workflow criterion in particular — with the
`/doc-review` equivalent. Add the measured before-and-after numbers. Resolve
Q1 with the decision recorded in the design document, or restate it if the
conditional semantic work did not proceed.

- [ ] **Step 3b: Record the kill criteria**

Approved by the founder on 2026-09-20, to be written when Phase B closes. Add
this section to `docs/specs/0089-team-ai-agent-architecture.md`, after
*Approved Decisions*. The wording is settled — add it as given.

```markdown
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
```

- [ ] **Step 4: Verify the whole suite one more time**

```bash
python -m pytest scripts/checks/tests/ scripts/hooks/tests/ -q
python scripts/checks/provider_leak_check.py
python scripts/checks/knowledge_query_guard.py
python scripts/checks/scope_evidence_check.py --base main
node ../team-ai/dist/cli.js validate-kb --instance team-ai
node ../team-ai/dist/cli.js validate-manifest --root team-ai
node ../team-ai/dist/cli.js run-evals --root team-ai
node ../team-ai/dist/cli.js emit --target claude-code --dir team-ai --out .. --file-prefix team-ai- --no-plugin-manifest --builtin-search --allow-tracked
git diff --exit-code -- .claude/agents && echo "emit stable"
git status --short
```
Expected: everything passes; `git status` shows no agent-local files staged.

- [ ] **Step 5: Commit**

```bash
git add AGENTS.md .github/copilot-instructions.md docs/specs/0089-team-ai-agent-architecture.md docs/superpowers/specs/2026-09-20-team-ai-agent-architecture-phase-b-design.md
git commit -m "docs: record Phase B outcome and correct the .claude/ path rule"
```

---

## Founder sign-offs required before merge

These are separate approvals. None may be inferred from approval of this plan.

1. **Task 12, Step 4** — the one `engine/` comment line, against spec 0089's *Out of Scope*.
2. **Task 11, Step 3** — scoped shell access for the three large-corpus agents, which hold read-only tools today.
3. **Task 11, Step 1** — the 17-file regeneration diff.
4. **Task 20, Step 1** — the `AGENTS.md` `.claude/` rule correction.

## Deferred, with the evidence that decides them

- **Semantic retrieval** — conditional on Task 7's measurement (D-B2).
- **17 agents to 8** — decided on Task 6's per-domain coverage and Task 16's observation log (D-B12).
- **Corpus re-namespacing** — not scheduled; would be a second migration over ~390 documents.
