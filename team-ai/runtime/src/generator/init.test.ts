import {
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  existsSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";
import { afterEach, describe, expect, it, vi } from "vitest";

import * as assembleManifest from "../commands/assemble-manifest.js";
import * as reindex from "../commands/reindex.js";
import * as validateKb from "../commands/validate-kb.js";
import { loadBank } from "../interview/bank.js";
import { Engine } from "../interview/engine.js";
import type { Question } from "../interview/types.js";
import { validate } from "../schema/validate.js";
import { run } from "./init.js";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const errorLog = vi.spyOn(console, "error").mockImplementation(() => undefined);
afterEach(() => {
  log.mockClear();
  errorLog.mockClear();
});

const OVERRIDES: Record<string, unknown> = {
  "pre.assessment": "coexist",
  "pre.overlap": "decide-later",
  "pre.probe_result": "continue",
  mode: "instance",
  "ctx.org_path": "testorg",
  "team.name": "atlasdata",
  "team.mission": "Own the customer data platform",
  "team.size": "4-8",
  "team.surfaces": ["coding-agent"],
  "team.sources": ["github"],
  "team.consumers": ["engineers"],
  "kb.substrate": "md-git",
  "kb.namespaces": "engineering",
  "kb.catalog_override": "use-preset",
  "kb.sources_strategy": "link-only",
  "kb.sensitivity": "three-tiers",
  "kb.write_back": "pr-only",
  "arch.index_driver": "lexical",
  "arch.hosting": "no-server",
  "arch.language": "typescript",
  "arch.ci": "github-actions",
  "arch.topology": "single-repo",
  "arch.model_tiers": "balanced",
  "arch.cache": "yes",
  "agents.roles": ["architect"],
  "agents.domains": "billing api",
  "agents.personas": ["internal-technical"],
  "agents.skills": [],
  "agents.strictness": "refuse-log-gap",
  "agents.seed": "yes-5-starter-docs",
};

// Walk a fresh Engine with the desired answers to learn the exact question order
// the CLI runtime will follow, and record the string token to feed for each step.
function scriptedAnswers(overrides: Record<string, unknown>): string[] {
  const engine = new Engine(loadBank());
  const out: string[] = [];
  for (let guard = 0; guard < 500; guard += 1) {
    const step = engine.next();
    if (step === null) break;
    if (step.kind === "gate") {
      out.push("confirm");
      engine.confirmGate(step.gate);
      continue;
    }
    const q: Question = step.question;
    let value: unknown;
    if (q.id in overrides) value = overrides[q.id];
    else if (q.type === "multi_select") value = Array.isArray(q.default) ? q.default : [];
    else if (q.default !== undefined) value = q.default;
    else if (q.type === "single_select") value = q.options[0]?.value;
    else value = `${q.id}-value`;
    out.push(Array.isArray(value) ? value.join(",") : String(value));
    engine.answer(q.id, value);
  }
  return out;
}

function puller(queue: string[]): () => Promise<string> {
  let idx = 0;
  return () => Promise.resolve(queue[idx++] ?? "");
}

describe("team-ai init", () => {
  it("runs the interview and generates a working instance into an empty dir", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-init-"));
    const code = await run({ dir, answers: puller(scriptedAnswers(OVERRIDES)) });
    expect(code).toBe(0);

    expect(await validateKb.run({ root: join(dir, "kb"), schemaOnly: true })).toBe(0);
    expect(await reindex.run({ root: dir })).toBe(0);
    expect(await assembleManifest.run({ root: dir, check: false })).toBe(0);

    expect(existsSync(join(dir, "team-profile.yaml"))).toBe(true);
    const profile = parseYaml(readFileSync(join(dir, "team-profile.yaml"), "utf8")) as unknown;
    expect(validate("team-profile", profile).ok).toBe(true);

    expect(existsSync(join(dir, "agents/billing-api-sme.yaml"))).toBe(true);
    const agent = parseYaml(
      readFileSync(join(dir, "agents/billing-api-sme.yaml"), "utf8"),
    ) as unknown;
    expect(validate("agent", agent).ok).toBe(true);

    expect(existsSync(join(dir, "agents/roles/architect.yaml"))).toBe(true);
    expect(existsSync(join(dir, "personas/internal-technical.md"))).toBe(true);
  });

  it("uses an instance catalog namespace preset when generating domain SMEs", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-init-"));
    mkdirSync(join(dir, "cat", "namespaces"), { recursive: true });
    const seeds = ["a", "b", "c", "d", "e"]
      .map((n) => `  - path: ${n}.md\n    title: ${n}\n    purpose: seed ${n}`)
      .join("\n");
    writeFileSync(
      join(dir, "cat", "namespaces", "custom.yaml"),
      `name: named-differently\ndescription: x\nsecond_level:\n  - alpha\n  - beta\ndomain_dir: null\nseed_docs:\n${seeds}\n`,
      "utf8",
    );
    const overrides = {
      ...OVERRIDES,
      "kb.namespaces": "custom",
      "agents.domains": "alpha, beta",
    };
    const code = await run({
      dir,
      catalog: join(dir, "cat"),
      answers: puller(scriptedAnswers(overrides)),
    });
    expect(code).toBe(0);

    expect(await validateKb.run({ root: join(dir, "kb"), schemaOnly: true })).toBe(0);
    expect(await reindex.run({ root: dir })).toBe(0);
    expect(await assembleManifest.run({ root: dir, check: false })).toBe(0);

    expect(existsSync(join(dir, "team-profile.yaml"))).toBe(true);
    const profile = parseYaml(readFileSync(join(dir, "team-profile.yaml"), "utf8")) as unknown;
    expect(validate("team-profile", profile).ok).toBe(true);

    expect(readFileSync(join(dir, "agents", "alpha-sme.yaml"), "utf8")).toContain(
      "kb_namespaces: [alpha]",
    );
    expect(readFileSync(join(dir, "agents", "beta-sme.yaml"), "utf8")).toContain(
      "kb_namespaces: [beta]",
    );

    expect(existsSync(join(dir, "agents/roles/architect.yaml"))).toBe(true);
    expect(existsSync(join(dir, "personas/internal-technical.md"))).toBe(true);
  });

  it("never overwrites a hand-authored file; writes a .team-ai-new sibling instead", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-init-"));
    mkdirSync(join(dir, "agents"), { recursive: true });
    const sentinel = "# HAND AUTHORED SENTINEL\n";
    writeFileSync(join(dir, "agents/sme.yaml"), sentinel, "utf8");

    const code = await run({
      dir,
      onConflict: "siblings",
      answers: puller(scriptedAnswers(OVERRIDES)),
    });
    expect(code).toBe(0);

    expect(readFileSync(join(dir, "agents/sme.yaml"), "utf8")).toBe(sentinel);
    expect(existsSync(join(dir, "agents/sme.yaml.team-ai-new"))).toBe(true);
  });

  it("--dry-run writes nothing", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-init-"));
    const code = await run({ dir, dryRun: true, answers: puller(scriptedAnswers(OVERRIDES)) });
    expect(code).toBe(0);
    expect(readdirSync(dir)).toEqual([]);
  });
});
