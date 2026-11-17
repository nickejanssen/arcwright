// Deterministic. No model calls.
//
// Orchestration for the golden eval harness: wires the knowledge base, the
// domain manifest, and the retrieval index together, replays each golden
// question through the architecture's routing procedure, and produces the
// per-question `EvalOutcome`s that `metrics.computeReport` aggregates.
//
// `routeQuestion` mirrors docs/architecture.md §16:
//   1. Zero-model exact keyword route when one domain uniquely owns the query.
//   2. Search-assisted route (tier "small") on a keyword tie or miss, resolved
//      by the top hit's namespace.
//   3. Refuse when retrieval returns nothing above the 0.2 score threshold, or
//      when nothing retrieved maps to a manifest domain. A confident wrong
//      route is worse than no answer.

import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";

import { resolveCitation } from "../kb/citations.js";
import { loadKb } from "../kb/loader.js";
import type { KbDoc } from "../kb/types.js";
import { createAdapter } from "../retrieval/factory.js";
import { resolveKbScope } from "../retrieval/index-lock.js";
import type { Hit, RetrievalAdapter } from "../retrieval/types.js";
import type { GoldenQuestion, Manifest, ManifestDomain, ModelTier } from "../schema/types.js";
import { validate } from "../schema/validate.js";
import type { EvalOutcome, GateThresholds } from "./metrics.js";

const TOP_K = 8;
const REFUSE_ROUTE = "__refuse__";
// Measured against a 37-question golden set over a ~966,000-token corpus on
// 2026-09-20: no threshold
// over term statistics separates answerable from unanswerable questions on a
// ~966,000-token corpus. Out-of-scope top scores ran 0.547-0.773 against
// in-scope 0.525-0.686; peakedness and content-word coverage overlap likewise.
// A corpus this large contains nearly every common English word, so an
// unrelated question still finds real matches. Refusal is a judgement over
// retrieved content, made by the agent in the delivery path and measured by
// the delegation eval, not by this harness. The threshold below
// only suppresses genuinely empty result sets. Refusal is not decidable from
// term statistics, so the strict comparison only rejects a non-match.
const REFUSE_THRESHOLD = 0;

// The single source of truth for the built-in gate thresholds. `evals/gates.yaml`
// at the repo root is a human-readable reference copy of these values, not a
// file this module loads.
export const DEFAULT_GATES: GateThresholds = {
  hitRate: 0.8,
  citationValidity: 1.0,
  coverage: 0.8,
};

const TIER_RANK: Record<ModelTier, number> = { none: 0, small: 1, large: 2 };

export interface RoutingResult {
  route: string;
  tier: ModelTier;
}

export interface RunContext {
  instanceDir: string;
}

type SearchFn = (query: string) => Promise<Hit[]>;

function closeAdapter(adapter: RetrievalAdapter): void {
  const close = (adapter as { close?: () => void }).close;
  if (typeof close === "function") close.call(adapter);
}

function hitNamespace(hit: Hit): string | undefined {
  const namespace = hit.metadata.namespace;
  return typeof namespace === "string" ? namespace : undefined;
}

function escapeRegex(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// A keyword matches only as a whole word or phrase, never as an interior
// substring: the keyword "pto" must not fire on "cryptography". Word edges are
// any non-alphanumeric character (or the string boundary), and a trailing plural
// or possessive is allowed so "429" still matches "429s" and "webhook" matches
// "webhooks". Spaces inside a multi-word keyword are matched literally.
function keywordMatches(haystack: string, keyword: string): boolean {
  const pattern = new RegExp(
    `(?:^|[^a-z0-9])${escapeRegex(keyword.toLowerCase())}(?:'s|s)?(?:[^a-z0-9]|$)`,
  );
  return pattern.test(haystack);
}

// How many of a domain's keywords occur as whole words/phrases in the question,
// case-insensitively.
function keywordScore(question: string, keywords: string[]): number {
  const haystack = question.toLowerCase();
  return keywords.filter((keyword) => keyword.length > 0 && keywordMatches(haystack, keyword))
    .length;
}

export async function routeQuestion(
  question: string,
  manifest: Manifest,
  search: SearchFn,
): Promise<RoutingResult> {
  const domains = manifest.domains;

  // Step 1: zero-model exact route when exactly one domain owns the most keywords.
  const scored = domains.map((domain) => ({
    domain,
    score: keywordScore(question, domain.keywords),
  }));
  const maxScore = scored.reduce((max, entry) => Math.max(max, entry.score), 0);
  if (maxScore > 0) {
    const leaders = scored.filter((entry) => entry.score === maxScore);
    const only = leaders.length === 1 ? leaders[0] : undefined;
    if (only !== undefined) {
      return { route: only.domain.subagent, tier: "none" };
    }
  }

  // Step 2: keyword tie or miss — let retrieval decide.
  const hits = await search(question);
  const top = hits[0];
  if (top !== undefined && top.score > REFUSE_THRESHOLD) {
    const topNamespace = hitNamespace(top);
    const topMatches =
      topNamespace === undefined
        ? []
        : domains.filter((domain) => domain.kb_namespace === topNamespace);
    // Exactly one mapped domain, or a namespace shared by several domains
    // (ambiguous but real) resolved by manifest array order.
    const firstMatch = topMatches[0];
    if (firstMatch !== undefined) {
      return { route: firstMatch.subagent, tier: "small" };
    }
    // The top hit's namespace maps to no domain: try the best-scoring hit whose
    // namespace does map. If nothing retrieved maps to a domain, refuse rather
    // than route confidently to the wrong place.
    const mapped = bestMappedDomain(hits, domains);
    if (mapped !== undefined) {
      return { route: mapped.subagent, tier: "small" };
    }
  }

  // Step 3: nothing retrievable above threshold, or nothing that maps to a domain.
  return { route: REFUSE_ROUTE, tier: "none" };
}

function bestMappedDomain(hits: Hit[], domains: ManifestDomain[]): ManifestDomain | undefined {
  for (const hit of hits) {
    const namespace = hitNamespace(hit);
    if (namespace === undefined) continue;
    const domain = domains.find((candidate) => candidate.kb_namespace === namespace);
    if (domain !== undefined) return domain;
  }
  return undefined;
}

function stripKbPrefix(path: string): string {
  return path.startsWith("kb/") ? path.slice(3) : path;
}

function expectedPathHit(expectPaths: string[], hits: Hit[]): boolean {
  if (expectPaths.length === 0) return false;
  const hitPaths = new Set(hits.map((hit) => hit.path));
  return expectPaths.some((path) => hitPaths.has(path) || hitPaths.has(stripKbPrefix(path)));
}

function readManifest(instanceDir: string): Manifest {
  const path = join(instanceDir, "manifest.yaml");
  const parsed: unknown = parseYaml(readFileSync(path, "utf8"));
  const result = validate("manifest", parsed);
  if (!result.ok) {
    throw new Error(`invalid manifest.yaml: ${result.errors[0] ?? "validation failed"}`);
  }
  return result.value;
}

// `must_cite: true` demands a non-empty `expect_paths` that fully resolves.
// `must_cite: false` still requires any listed path to resolve, but an empty
// list is fine (a refusal cites nothing).
function citationsResolve(docs: KbDoc[], question: GoldenQuestion): boolean {
  const paths = question.expect_paths;
  if (question.must_cite && paths.length === 0) return false;
  return paths.every((path) => resolveCitation(docs, path).ok);
}

function namespaceForRoute(manifest: Manifest, route: string): string | undefined {
  return manifest.domains.find((domain) => domain.subagent === route)?.kb_namespace;
}

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

export async function runGoldenFile(
  questions: GoldenQuestion[],
  ctx: RunContext,
): Promise<EvalOutcome[]> {
  const scope = resolveKbScope(ctx.instanceDir);
  const docs = await loadKb(scope.root, { exclude: scope.exclude });
  const manifest = readManifest(ctx.instanceDir);

  const adapter = createAdapter(ctx.instanceDir);
  try {
    await adapter.reindex();
    const search: SearchFn = (query) => adapter.search(query, { k: TOP_K });

    const outcomes: EvalOutcome[] = [];
    for (const question of questions) {
      const hits = await search(question.question);
      const routing = await routeQuestion(question.question, manifest, search);
      const refuseExpected = question.expect_route === REFUSE_ROUTE;
      const routedTo = routing.route;
      const routedNamespace = namespaceForRoute(manifest, routedTo);
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

      outcomes.push({
        id: question.id,
        question: question.question,
        hit: expectedPathHit(question.expect_paths, hits),
        citationsValid: citationsResolve(docs, question),
        routedTo,
        routeCorrect: routedTo === question.expect_route,
        namespaceOk: refuseExpected
          ? question.expect_namespace === ""
          : routedNamespace !== undefined && routedNamespace === question.expect_namespace,
        tier: routing.tier,
        tierOk: TIER_RANK[routing.tier] <= TIER_RANK[question.expect_tier_max],
        refuseExpected,
        refuseCorrect: refuseExpected ? routedTo === REFUSE_ROUTE : routedTo !== REFUSE_ROUTE,
        covered,
        expectNamespace: question.expect_namespace,
        sourceChangedSinceGenerated,
      });
    }
    return outcomes;
  } finally {
    closeAdapter(adapter);
  }
}

// The built-in `DEFAULT_GATES` are the base; an optional
// `<instance>/evals/gates.yaml` overrides individual keys.
export function loadGates(instanceDir: string): GateThresholds {
  const path = join(instanceDir, "evals", "gates.yaml");
  let record: Record<string, unknown> = {};
  try {
    const parsed: unknown = parseYaml(readFileSync(path, "utf8"));
    if (typeof parsed === "object" && parsed !== null) {
      record = parsed as Record<string, unknown>;
    }
  } catch {
    // No instance override file (or an unreadable one): fall back to defaults.
  }

  const pick = (key: keyof GateThresholds): number => {
    const value = record[key];
    return typeof value === "number" && Number.isFinite(value) ? value : DEFAULT_GATES[key];
  };

  return {
    hitRate: pick("hitRate"),
    citationValidity: pick("citationValidity"),
    coverage: pick("coverage"),
  };
}
