import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it, vi } from "vitest";

import { parseFrontmatter } from "../kb/frontmatter.js";
import { validate } from "../schema/validate.js";
import { applyPlan } from "./apply.js";
import { buildAdoptionPlan } from "./plan.js";

const FIXTURE = "src/adopt/fixtures/legacy-repo";
const TODAY = new Date("2026-08-31T00:00:00Z");

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
const dirs: string[] = [];

async function stagedRepo(): Promise<{ repo: string; planPath: string }> {
  const repo = mkdtempSync(join(tmpdir(), "team-ai-apply-"));
  dirs.push(repo);
  cpSync(FIXTURE, repo, { recursive: true });
  await buildAdoptionPlan({ root: repo, out: repo, horizonDays: 180, today: TODAY });
  return { repo, planPath: join(repo, "adoption-plan.yaml") };
}

async function approve(planPath: string, paths: string[]): Promise<void> {
  const { parse, stringify } = await import("yaml");
  const plan = parse(readFileSync(planPath, "utf8")) as {
    backfill: { path: string; approved: boolean }[];
  };
  for (const item of plan.backfill) {
    if (paths.includes(item.path)) item.approved = true;
  }
  writeFileSync(planPath, stringify(plan), "utf8");
}

// Resolve pending namespace decisions the way `team-ai adopt --interactive` would.
async function decide(planPath: string, picks: Record<string, string>): Promise<void> {
  const { parse, stringify } = await import("yaml");
  const plan = parse(readFileSync(planPath, "utf8")) as {
    namespace_map: { decisions: { folder: string; chosen: string | null }[] };
  };
  for (const decision of plan.namespace_map.decisions) {
    const pick = picks[decision.folder];
    if (pick !== undefined) decision.chosen = pick;
  }
  writeFileSync(planPath, stringify(plan), "utf8");
}

afterEach(() => {
  log.mockClear();
  error.mockClear();
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("applyPlan", () => {
  it("backfills only the approved docs, leaves the rest untouched, and is idempotent", async () => {
    const { repo, planPath } = await stagedRepo();
    await approve(planPath, ["docs/architecture/a.md", "docs/notes/b.md"]);
    await decide(planPath, { architecture: "platform", notes: "operating" });

    const first = await applyPlan(planPath, { root: repo });
    expect(first.applied.sort()).toEqual(["docs/architecture/a.md", "docs/notes/b.md"]);
    expect(first.conflicts).toEqual([]);

    for (const rel of ["docs/architecture/a.md", "docs/notes/b.md"]) {
      const content = readFileSync(join(repo, rel), "utf8");
      expect(content.startsWith("---\n")).toBe(true);
      const { data } = parseFrontmatter(content);
      expect(validate("frontmatter", data).ok).toBe(true);
      expect(data.namespace).not.toBe("__pending__");
    }
    // The un-approved third doc is unchanged.
    expect(readFileSync(join(repo, "docs/prd/c.md"), "utf8").startsWith("---\n")).toBe(false);

    const second = await applyPlan(planPath, { root: repo });
    expect(second.applied).toEqual([]);
    expect(second.skipped).toContain("docs/architecture/a.md");
    expect(second.skipped).toContain("docs/notes/b.md");
    expect(second.conflicts).toEqual([]);
  });

  it("refuses an approved backfill item whose namespace decision is still open", async () => {
    const { repo, planPath } = await stagedRepo();
    await approve(planPath, ["docs/prd/c.md"]);
    // No `decide()` — prd/ is still `__pending__`.

    const result = await applyPlan(planPath, { root: repo });
    expect(result.applied).toEqual([]);
    expect(result.skipped).toContain("docs/prd/c.md");
    expect(readFileSync(join(repo, "docs/prd/c.md"), "utf8").startsWith("---\n")).toBe(false);

    // Once the decision is made, the same plan applies cleanly.
    await decide(planPath, { prd: "operating" });
    const after = await applyPlan(planPath, { root: repo });
    expect(after.applied).toEqual(["docs/prd/c.md"]);
    const { data } = parseFrontmatter(readFileSync(join(repo, "docs/prd/c.md"), "utf8"));
    expect(data.namespace).toBe("operating");
    expect(data.id).toBe("operating.prd.c");
  });

  it("records namespace decisions into .team-ai-namespaces.yaml", async () => {
    const { repo, planPath } = await stagedRepo();
    const { parse, stringify } = await import("yaml");
    const plan = parse(readFileSync(planPath, "utf8")) as {
      namespace_map: { decisions: { folder: string; chosen: string | null }[] };
    };
    for (const decision of plan.namespace_map.decisions) {
      if (decision.folder === "prd") decision.chosen = "operating";
    }
    writeFileSync(planPath, stringify(plan), "utf8");

    await applyPlan(planPath, { root: repo });

    const nsFile = readFileSync(join(repo, ".team-ai-namespaces.yaml"), "utf8");
    expect(nsFile).toContain("prd: operating");
  });
});
