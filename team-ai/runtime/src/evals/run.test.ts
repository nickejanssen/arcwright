import {
  cpSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  renameSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { createAdapter } from "../retrieval/factory.js";
import type { Hit, RetrievalAdapter } from "../retrieval/types.js";
import type { GoldenQuestion, Manifest } from "../schema/types.js";
import { run as runEvals } from "../commands/run-evals.js";
import { DEFAULT_GATES, loadGates, routeQuestion, runGoldenFile } from "./run.js";
import type { GateThresholds } from "./metrics.js";

const FIXTURE = "src/evals/fixtures/instance";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);

const dirs: string[] = [];

function makeInstance(): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-evals-"));
  dirs.push(dir);
  cpSync(FIXTURE, dir, { recursive: true });
  return dir;
}

function readManifest(dir: string): Manifest {
  return parseYaml(readFileSync(join(dir, "manifest.yaml"), "utf8")) as Manifest;
}

function readGolden(dir: string): GoldenQuestion[] {
  return parseYaml(
    readFileSync(join(dir, "golden", "fixture.golden.yaml"), "utf8"),
  ) as GoldenQuestion[];
}

afterEach(() => {
  log.mockClear();
  error.mockClear();
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("routeQuestion", () => {
  let dir: string;
  let manifest: Manifest;
  let adapter: RetrievalAdapter;
  let search: (query: string) => Promise<Hit[]>;

  beforeEach(async () => {
    dir = makeInstance();
    manifest = readManifest(dir);
    adapter = createAdapter(dir);
    await adapter.reindex();
    search = (query) => adapter.search(query, { k: 8 });
  });

  afterEach(() => {
    (adapter as { close?: () => void }).close?.();
  });

  it("takes the zero-model exact route when one domain uniquely owns the keywords", async () => {
    const result = await routeQuestion(
      "What should a caller do about a 429 rate limit error?",
      manifest,
      search,
    );
    expect(result).toEqual({ route: "platform-sme", tier: "none" });
  });

  it("falls back to retrieval (tier small) when no keyword matches", async () => {
    const result = await routeQuestion(
      "What happens during a new hire's first week with their buddy?",
      manifest,
      search,
    );
    expect(result).toEqual({ route: "handbook-sme", tier: "small" });
  });

  it("refuses when retrieval returns nothing above threshold", async () => {
    const result = await routeQuestion(
      "Which quantum computing frameworks support GraphQL subscriptions?",
      manifest,
      search,
    );
    expect(result).toEqual({ route: "__refuse__", tier: "none" });
  });

  it("matches keywords on word boundaries, not as interior substrings", async () => {
    // The handbook keyword "pto" must NOT fire on "cryptography". With a correct
    // word-boundary match, step 1 finds nothing and retrieval routes the query
    // to platform (its top hit is the rate-limits / key-rotation material).
    const result = await routeQuestion(
      "how does our cryptography key rotation work",
      manifest,
      search,
    );
    expect(result).toEqual({ route: "platform-sme", tier: "small" });
    expect(result).not.toEqual({ route: "handbook-sme", tier: "none" });
  });

  it("matches a keyword against its plural (429 -> '429s')", async () => {
    const result = await routeQuestion(
      "What do partners do when they start getting 429s?",
      manifest,
      search,
    );
    expect(result).toEqual({ route: "platform-sme", tier: "none" });
  });

  it("matches a keyword against its plural (webhook -> 'webhooks')", async () => {
    const result = await routeQuestion("Our webhooks keep failing — what now?", manifest, search);
    expect(result).toEqual({ route: "platform-sme", tier: "none" });
  });

  it("refuses when a retrieved hit's namespace maps to no manifest domain", async () => {
    const stub = (): Promise<Hit[]> =>
      Promise.resolve([
        {
          doc_id: "d",
          chunk_id: "c",
          path: "legal/contracts.md",
          heading_path: "Contracts",
          score: 0.8,
          text: "indemnification clauses",
          metadata: { namespace: "legal" },
        },
      ]);
    const result = await routeQuestion(
      "what are our standard indemnification terms",
      manifest,
      stub,
    );
    expect(result.route).toBe("__refuse__");
    expect(result).toEqual({ route: "__refuse__", tier: "none" });
  });

  it("breaks a keyword tie with the top hit's namespace (tier small)", async () => {
    // Both domains match exactly one keyword, so step 1 cannot decide; a stub
    // search returns a platform-namespace top hit and routing follows it.
    const [platform, handbook] = manifest.domains;
    const tie: Manifest = {
      domains: [
        { ...(platform as Manifest["domains"][number]), keywords: ["token"] },
        { ...(handbook as Manifest["domains"][number]), keywords: ["onboarding"] },
      ],
    };
    const stub = (): Promise<Hit[]> =>
      Promise.resolve([
        {
          doc_id: "d",
          chunk_id: "c",
          path: "platform/authentication.md",
          heading_path: "Authentication",
          score: 0.7,
          text: "tokens",
          metadata: { namespace: "platform" },
        },
      ]);
    const result = await routeQuestion("Which onboarding step sets up my API token?", tie, stub);
    expect(result).toEqual({ route: "platform-sme", tier: "small" });
  });

  it("refuses when the top hit is a non-match", async () => {
    const stub = (): Promise<Hit[]> =>
      Promise.resolve([
        {
          doc_id: "d",
          chunk_id: "c",
          path: "platform/authentication.md",
          heading_path: "Authentication",
          score: 0,
          text: "tokens",
          metadata: { namespace: "platform" },
        },
      ]);
    const result = await routeQuestion("totally unrelated wording here", manifest, stub);
    expect(result).toEqual({ route: "__refuse__", tier: "none" });
  });
});

describe("runGoldenFile", () => {
  it("produces one sane outcome per question", async () => {
    const dir = makeInstance();
    const outcomes = await runGoldenFile(readGolden(dir), { instanceDir: dir });

    expect(outcomes.map((o) => o.id)).toEqual([
      "eval.fixture.rate-limit-429",
      "eval.fixture.pto-accrual",
      "eval.fixture.new-hire-first-week",
      "eval.fixture.refuse-out-of-kb",
    ]);

    const byId = new Map(outcomes.map((o) => [o.id, o]));
    const rateLimit = byId.get("eval.fixture.rate-limit-429");
    expect(rateLimit?.hit).toBe(true);
    expect(rateLimit?.routedTo).toBe("platform-sme");
    expect(rateLimit?.routeCorrect).toBe(true);
    expect(rateLimit?.citationsValid).toBe(true);
    expect(rateLimit?.namespaceOk).toBe(true);
    expect(rateLimit?.tierOk).toBe(true);

    const refuse = byId.get("eval.fixture.refuse-out-of-kb");
    expect(refuse?.refuseExpected).toBe(true);
    expect(refuse?.refuseCorrect).toBe(true);
    expect(refuse?.routedTo).toBe("__refuse__");
    expect(refuse?.citationsValid).toBe(true);
    expect(refuse?.namespaceOk).toBe(true);
  });

  it("marks citationsValid false when must_cite is true but expect_paths is empty", async () => {
    const dir = makeInstance();
    const question: GoldenQuestion = {
      id: "eval.test.must-cite-no-paths",
      question: "What should a caller do when they hit a 429 rate limit error?",
      expect_namespace: "platform",
      expect_paths: [],
      expect_route: "platform-sme",
      expect_tier_max: "small",
      must_cite: true,
    };
    const [outcome] = await runGoldenFile([question], { instanceDir: dir });
    expect(outcome?.citationsValid).toBe(false);
  });

  it("marks namespaceOk false when the routed domain's namespace differs from expect_namespace", async () => {
    const dir = makeInstance();
    const question: GoldenQuestion = {
      id: "eval.test.wrong-namespace",
      question: "What should a caller do when they hit a 429 rate limit error?",
      expect_namespace: "handbook",
      expect_paths: ["kb/platform/rate-limits.md"],
      expect_route: "platform-sme",
      expect_tier_max: "none",
      must_cite: true,
    };
    const [outcome] = await runGoldenFile([question], { instanceDir: dir });
    expect(outcome?.routedTo).toBe("platform-sme");
    expect(outcome?.namespaceOk).toBe(false);
  });

  it("loads documents from the declared KB root and skips exclusions", async () => {
    const dir = makeInstance();
    renameSync(join(dir, "kb"), join(dir, "docs"));
    mkdirSync(join(dir, "docs", "archive"), { recursive: true });
    writeFileSync(join(dir, "docs", "archive", "bad.md"), "no front matter", "utf8");
    writeFileSync(
      join(dir, "index.lock"),
      "driver: lexical\nchunk:\n  split_on: [h2, h3]\n  target_tokens: 800\n  hard_cap: 1200\nembedding: null\nkb:\n  root: docs\n  exclude: [archive/]\n",
      "utf8",
    );

    const outcomes = await runGoldenFile(readGolden(dir), { instanceDir: dir });
    expect(outcomes).toHaveLength(4);
    expect(outcomes.every((outcome) => outcome.citationsValid)).toBe(true);
  });
});

describe("loadGates", () => {
  it("returns the shipped defaults when no gates.yaml is present", () => {
    const dir = makeInstance();
    expect(loadGates(dir)).toEqual({
      hitRate: 0.8,
      citationValidity: 1.0,
      coverage: 0.8,
    });
  });

  it("reads overrides from <instance>/evals/gates.yaml", () => {
    const dir = makeInstance();
    mkdirSync(join(dir, "evals"), { recursive: true });
    writeFileSync(join(dir, "evals", "gates.yaml"), "hitRate: 0.5\n");
    const gates = loadGates(dir);
    expect(gates.hitRate).toBe(0.5);
    // unspecified keys fall back to the shipped defaults
    expect(gates.citationValidity).toBe(1);
    expect(gates.coverage).toBe(0.8);
  });

  it("keeps the reference evals/gates.yaml in sync with DEFAULT_GATES", () => {
    const reference = parseYaml(readFileSync("evals/gates.yaml", "utf8")) as GateThresholds;
    expect(reference).toEqual(DEFAULT_GATES);
  });
});

describe("run-evals command", () => {
  it("returns 0 for a fixture golden set authored to pass its gates", async () => {
    const dir = makeInstance();
    const code = await runEvals({ root: dir, golden: "golden" });
    expect(code).toBe(0);
    const printed = log.mock.calls.map((c) => String(c[0])).join("\n");
    expect(printed).toContain("PASS");
    expect(printed).not.toContain("FAIL");
  });

  it("emits a parseable EvalReport with --json", async () => {
    const dir = makeInstance();
    const code = await runEvals({ root: dir, golden: "golden", json: true });
    expect(code).toBe(0);
    const payload: unknown = JSON.parse(log.mock.calls.map((c) => String(c[0])).join(""));
    expect(payload).toMatchObject({ pass: true });
  });

  it("prints 'no golden questions found' and exits 0 when only the example file is present", async () => {
    const code = await runEvals({ root: "." });
    expect(code).toBe(0);
    const printed = log.mock.calls.map((c) => String(c[0])).join("\n");
    expect(printed).toContain("skipping example.golden.yaml");
    expect(printed).toContain("no golden questions found");
  });

  it("returns 1 with a clean error when the golden directory is missing", async () => {
    const dir = makeInstance();
    const code = await runEvals({ root: dir, golden: "no-such-dir" });
    expect(code).toBe(1);
    const printed = error.mock.calls.map((c) => String(c[0])).join("\n");
    expect(printed).toContain("cannot read golden directory");
  });

  it("returns 1 when a golden file fails the schema", async () => {
    const dir = makeInstance();
    rmSync(join(dir, "golden", "fixture.golden.yaml"));
    writeFileSync(
      join(dir, "golden", "broken.golden.yaml"),
      "- id: eval.broken.missing-fields\n  question: incomplete\n",
    );
    const code = await runEvals({ root: dir, golden: "golden" });
    expect(code).toBe(1);
    expect(error).toHaveBeenCalled();
  });
});
