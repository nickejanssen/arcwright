// The CI-durable half of Task 39: run the framework against itself.
//
// Run B (Partner Solutions) and a synthetic reconciliation check run
// everywhere. Run A and Run A-adopt need the real Arcwright repo on disk at
// ARCWRIGHT; when it is absent (CI, a fresh clone) those `it`s skip rather than
// fail. The convenience shell version is `test/dogfood.sh`.
//
// Nothing here writes into Arcwright: preflight and adopt only ever read it,
// and every generated artifact lands under a fresh temp dir.

import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  cpSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import * as adopt from "../commands/adopt.js";
import * as assembleManifest from "../commands/assemble-manifest.js";
import * as doctor from "../commands/doctor.js";
import * as reindex from "../commands/reindex.js";
import * as search from "../commands/search.js";
import * as validateCitations from "../commands/validate-citations.js";
import * as validateKb from "../commands/validate-kb.js";
import { validate } from "../schema/validate.js";
import { loadAnswerFile } from "./init-answers.js";
import * as init from "./init.js";

const ARCWRIGHT = "C:/Users/nicke/OneDrive/Desktop/arcwright";
const HAS_ARCWRIGHT = existsSync(join(ARCWRIGHT, "AGENTS.md"));
const ARC_ANSWERS = "test/fixtures/answers/dogfood-arcwright.yaml";
const PARTNER_ANSWERS = "test/fixtures/answers/dogfood-partner-solutions.yaml";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const errorLog = vi.spyOn(console, "error").mockImplementation(() => undefined);
const dirs: string[] = [];

function tmp(): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-dogfood-"));
  dirs.push(dir);
  return dir;
}

function sha256(path: string): string {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

// The contract is "our runs never write into Arcwright", not "Arcwright is
// globally frozen" — a parallel process on this machine edits it during the
// suite. So the guard is: no porcelain entry that appears after a run (and was
// not there before) may name a team-ai output artifact. Everything team-ai
// adopt / init / preflight writes goes under a `--out` / `--dir` we control.
const TEAM_AI_ARTIFACT = /adoption-plan|\.team-ai|team-profile\.yaml|index\.lock/;

function arcwrightStatus(): string {
  return execFileSync("git", ["-C", ARCWRIGHT, "status", "--porcelain"], { encoding: "utf8" });
}

function arcwrightUntouched(before: string): void {
  const beforeLines = new Set(before.split("\n"));
  const leaked = arcwrightStatus()
    .split("\n")
    .filter((line) => line.trim().length > 0 && !beforeLines.has(line))
    .filter((line) => TEAM_AI_ARTIFACT.test(line));
  expect(leaked).toEqual([]);
}

let arcwrightBefore = "";

// The six deterministic checks every generated instance must pass.
async function sixChecks(dir: string): Promise<void> {
  expect(await validateKb.run({ root: join(dir, "kb"), schemaOnly: true })).toBe(0);
  expect(await validateCitations.run({ root: dir })).toBe(0);
  expect(await reindex.run({ root: dir })).toBe(0);

  const printed: string[] = [];
  log.mockImplementation((...args: unknown[]) => {
    printed.push(args.map(String).join(" "));
  });
  const searchCode = await search.run("charter", { root: dir, json: true });
  log.mockImplementation(() => undefined);
  expect(searchCode).toBe(0);
  const hits = JSON.parse(printed.join("\n")) as unknown[];
  expect(hits.length).toBeGreaterThan(0);

  expect(await assembleManifest.run({ root: dir, check: false })).toBe(0);
  expect(await doctor.run({ root: dir })).toBe(0);
}

beforeEach(() => {
  if (HAS_ARCWRIGHT) arcwrightBefore = arcwrightStatus();
});

afterEach(() => {
  log.mockClear();
  errorLog.mockClear();
  log.mockImplementation(() => undefined);
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
  if (HAS_ARCWRIGHT) arcwrightUntouched(arcwrightBefore);
});

describe("dogfood Run A — Arcwright (needs the real repo)", () => {
  it.skipIf(!HAS_ARCWRIGHT)("preflight reports EXTEND and the six checks pass", async () => {
    const dir = tmp();
    const printed: string[] = [];
    const code = await init.run({
      dir,
      answers: loadAnswerFile(ARC_ANSWERS).pull,
      preflightTarget: ARCWRIGHT,
      onConflict: "adopt-existing",
      output: (s) => printed.push(s),
    });
    expect(code).toBe(0);

    const report = printed.join("\n");
    expect(report).toContain("Assessment: EXTEND");
    expect(report).toContain("AGENTS.md");
    expect(report).toMatch(/agent config file: AGENTS\.md/);

    await sixChecks(dir);

    const validateYml = readFileSync(join(dir, ".github/workflows/validate.yml"), "utf8");
    expect(parseYaml(validateYml)).toBeTruthy();
    expect(validateYml).toContain("validate-kb.reusable.yml@v0");
  });

  it.skipIf(!HAS_ARCWRIGHT)(
    "reconciliation: a hand-authored AGENTS.md + agents/sme.yaml survive byte-for-byte",
    async () => {
      const dir = tmp();
      mkdirSync(join(dir, "agents"), { recursive: true });
      cpSync(join(ARCWRIGHT, "AGENTS.md"), join(dir, "AGENTS.md"));
      const sentinel = "# HAND AUTHORED SENTINEL\n";
      writeFileSync(join(dir, "agents/sme.yaml"), sentinel, "utf8");
      const beforeAgents = sha256(join(dir, "AGENTS.md"));
      const beforeSme = sha256(join(dir, "agents/sme.yaml"));

      const code = await init.run({
        dir,
        answers: loadAnswerFile(ARC_ANSWERS).pull,
        preflightTarget: ARCWRIGHT,
        onConflict: "adopt-existing",
        output: () => undefined,
      });
      expect(code).toBe(0);

      expect(sha256(join(dir, "AGENTS.md"))).toBe(beforeAgents);
      expect(sha256(join(dir, "agents/sme.yaml"))).toBe(beforeSme);
      expect(readFileSync(join(dir, "agents/sme.yaml"), "utf8")).toBe(sentinel);
      expect(existsSync(join(dir, "agents/sme.yaml.team-ai-new"))).toBe(false);

      const architecture = readFileSync(join(dir, "docs/architecture.md"), "utf8");
      expect(architecture).toContain("Coexistence boundary");
      expect(architecture).toContain("AGENTS.md");
    },
  );

  it.skipIf(!HAS_ARCWRIGHT)(
    "reconciliation: siblings mode writes .team-ai-new and leaves the sentinel alone",
    async () => {
      const dir = tmp();
      mkdirSync(join(dir, "agents"), { recursive: true });
      const sentinel = "# HAND AUTHORED SENTINEL\n";
      writeFileSync(join(dir, "agents/sme.yaml"), sentinel, "utf8");

      const code = await init.run({
        dir,
        answers: loadAnswerFile(ARC_ANSWERS).pull,
        preflightTarget: ARCWRIGHT,
        onConflict: "siblings",
        output: () => undefined,
      });
      expect(code).toBe(0);

      expect(readFileSync(join(dir, "agents/sme.yaml"), "utf8")).toBe(sentinel);
      expect(existsSync(join(dir, "agents/sme.yaml.team-ai-new"))).toBe(true);
    },
  );

  it.skipIf(!HAS_ARCWRIGHT)(
    "adopt against the real repo writes only the plan, repo untouched",
    async () => {
      const out = tmp();
      const code = await adopt.run({ root: ARCWRIGHT, out, horizonDays: 180 });
      expect(code).toBe(0);
      arcwrightUntouched(arcwrightBefore);

      expect(readdirSync(out).sort()).toEqual(["adoption-plan.yaml", "docs"]);
      expect(readdirSync(join(out, "docs"))).toEqual(["adoption-plan.md"]);

      const plan = parseYaml(readFileSync(join(out, "adoption-plan.yaml"), "utf8")) as {
        backfill: unknown[];
        gap: unknown[];
        namespace_map: { decisions: unknown[] };
      };
      expect(validate("adoption-plan", plan).ok).toBe(true);
      expect(plan.backfill.length).toBeGreaterThan(0);
      expect(plan.gap).toHaveLength(17);
      expect(plan.namespace_map.decisions.length).toBeGreaterThan(0);
    },
  );
});

describe("dogfood Run B — Partner Solutions (runs everywhere)", () => {
  it("generates a working instance; size 1-3 suppresses role subagents", async () => {
    const dir = tmp();
    const code = await init.run({
      dir,
      answers: loadAnswerFile(PARTNER_ANSWERS).pull,
      output: () => undefined,
    });
    expect(code).toBe(0);

    await sixChecks(dir);

    // team.size 1-3 → no role subagent files, only domain agents.
    const rolesDir = join(dir, "agents/roles");
    const roleFiles = existsSync(rolesDir)
      ? readdirSync(rolesDir).filter((f) => f.endsWith(".yaml") || f.endsWith(".md"))
      : [];
    expect(roleFiles).toEqual([]);
    expect(existsSync(join(dir, "agents/widgets-api-sme.yaml"))).toBe(true);

    const agentPlan = readFileSync(join(dir, "docs/agent-plan.md"), "utf8");
    expect(agentPlan).toMatch(/Role subagents\s*\n\s*\nNone\./);

    // arch.hosting no-server → both server gate conditions recorded.
    const architecture = readFileSync(join(dir, "docs/architecture.md"), "utf8");
    expect(architecture).toContain("when a 2nd coding client appears");
    expect(architecture).toContain("after 2 asks from people who cannot clone the repo");
  });
});
