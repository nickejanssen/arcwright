import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  cpSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { parse } from "yaml";
import { afterEach, describe, expect, it, vi } from "vitest";

import { validate } from "../schema/validate.js";
import { buildAdoptionPlan, countAlreadyStale } from "./plan.js";

const FIXTURE = "src/adopt/fixtures/legacy-repo";
const FIXTURE_FILES = ["README.md", "docs/architecture/a.md", "docs/notes/b.md", "docs/prd/c.md"];
const TODAY = new Date("2026-08-31T00:00:00Z");

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const dirs: string[] = [];

function tmp(): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-plan-"));
  dirs.push(dir);
  return dir;
}

function git(repo: string, args: string[], dateEnv?: string): void {
  const env =
    dateEnv === undefined
      ? process.env
      : { ...process.env, GIT_AUTHOR_DATE: dateEnv, GIT_COMMITTER_DATE: dateEnv };
  execFileSync("git", args, { cwd: repo, env, stdio: "ignore" });
}

function fingerprint(): Record<string, string> {
  const out: Record<string, string> = {};
  for (const rel of FIXTURE_FILES) {
    out[rel] = createHash("sha256")
      .update(readFileSync(join(FIXTURE, rel)))
      .digest("hex");
  }
  return out;
}

afterEach(() => {
  log.mockClear();
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("buildAdoptionPlan", () => {
  it("writes exactly the plan doc and yaml, and nothing else, leaving the repo untouched", async () => {
    const before = fingerprint();
    const out = tmp();

    const plan = await buildAdoptionPlan({ root: FIXTURE, out, horizonDays: 180, today: TODAY });

    expect(readdirSync(out).sort()).toEqual(["adoption-plan.yaml", "docs"]);
    expect(readdirSync(join(out, "docs"))).toEqual(["adoption-plan.md"]);

    expect(fingerprint()).toEqual(before);

    const yaml = readFileSync(join(out, "adoption-plan.yaml"), "utf8");
    expect(validate("adoption-plan", parse(yaml)).ok).toBe(true);

    expect(plan.backfill).toHaveLength(3);
    const notes = plan.backfill.find((b) => b.path === "docs/notes/b.md");
    expect(notes?.frontmatter.source).toBe("synced:notion");

    const decisionFolders = plan.namespace_map.decisions.map((d) => d.folder);
    expect(decisionFolders).toContain("prd");
    expect(decisionFolders).toContain("notes");

    expect(plan.gap).toHaveLength(17);
    expect(plan.created).toBe("2026-08-31T00:00:00.000Z");
  });

  it("applies a namespace-map override to move a folder into matched", async () => {
    const out = tmp();
    const plan = await buildAdoptionPlan({
      root: FIXTURE,
      out,
      horizonDays: 180,
      today: TODAY,
      namespaceMap: { prd: "operating" },
    });

    expect(plan.namespace_map.matched).toContainEqual({ folder: "prd", namespace: "operating" });
    expect(plan.namespace_map.decisions.map((d) => d.folder)).not.toContain("prd");
    const prdDoc = plan.backfill.find((b) => b.path === "docs/prd/c.md");
    expect(prdDoc?.namespace).toBe("operating");
  });
});

describe("buildAdoptionPlan — freshness anchored on last git edit", () => {
  it("gives a long-untouched doc a review_by that is already overdue, not a fresh grace period", async () => {
    const repo = tmp();
    git(repo, ["init", "-q"]);
    git(repo, ["config", "user.email", "t@example.com"]);
    git(repo, ["config", "user.name", "Test"]);
    mkdirSync(join(repo, "docs", "architecture"), { recursive: true });
    writeFileSync(join(repo, "docs", "architecture", "old.md"), "# Old\n\ntext\n");
    git(repo, ["add", "."]);
    git(repo, ["commit", "-q", "-m", "add old doc"], "2024-01-10T00:00:00Z");

    const out = tmp();
    const plan = await buildAdoptionPlan({ root: repo, out, horizonDays: 180, today: TODAY });

    const item = plan.backfill.find((b) => b.path === "docs/architecture/old.md");
    expect(item?.frontmatter.review_by).toBe("2024-07-08");
    expect(item?.frontmatter.review_by).not.toBe("2027-02-27"); // not a fresh today+180 clock
    expect(countAlreadyStale(plan)).toBe(1);
  });

  it("falls back to today+horizon for a doc with no git history at all", async () => {
    const repo = tmp();
    git(repo, ["init", "-q"]);
    git(repo, ["config", "user.email", "t@example.com"]);
    git(repo, ["config", "user.name", "Test"]);
    mkdirSync(join(repo, "docs", "architecture"), { recursive: true });
    // Committed so it's discoverable, but with a recent date well within today+180.
    writeFileSync(join(repo, "docs", "architecture", "fresh.md"), "# Fresh\n");
    git(repo, ["add", "."]);
    git(repo, ["commit", "-q", "-m", "add fresh doc"], TODAY.toISOString());

    const out = tmp();
    const plan = await buildAdoptionPlan({ root: repo, out, horizonDays: 180, today: TODAY });

    const item = plan.backfill.find((b) => b.path === "docs/architecture/fresh.md");
    expect(item?.frontmatter.review_by).toBe("2027-02-27");
    expect(countAlreadyStale(plan)).toBe(0);
  });
});

describe("buildAdoptionPlan — CRLF-fronted docs are not mistaken for un-fronted ones", () => {
  it("leaves a doc completely alone when it already has valid KB front matter opened with CRLF", async () => {
    const out = tmp();
    // Real Arcwright files were found with CRLF front matter during dogfooding
    // — an exact "---\n" prefix check reads this as no front matter at all,
    // which at apply time means stacking a second block on top of a real one.
    // With genuinely valid, already-complete front matter, the doc needs
    // neither a backfill entry NOR a relabel entry — it's simply done.
    // Only the opening delimiter needs a trailing \r to reproduce the bug —
    // that's the one line hasFrontmatter's regex has to get right. Plain \n
    // for the rest avoids an unrelated YAML-parser quirk with \r inside a
    // flow sequence, which isn't what this test is about.
    const crlfDoc =
      "---\r\n" +
      "id: platform.already-fronted.x\n" +
      "namespace: platform\n" +
      "title: Already Fronted\n" +
      "owner: Ada\n" +
      "status: active\n" +
      'review_by: "2027-01-01"\n' +
      "sensitivity: internal\n" +
      "source: authored\n" +
      "tags: []\n" +
      "supersedes: []\n" +
      "---\n\n# Existing\n";

    // Reuse the legacy-repo fixture layout, plus one extra CRLF-fronted file.
    const repo = mkdtempSync(join(tmpdir(), "team-ai-crlf-"));
    dirs.push(repo);
    cpSync(FIXTURE, repo, { recursive: true });
    mkdirSync(join(repo, "docs", "already-fronted"), { recursive: true });
    writeFileSync(join(repo, "docs", "already-fronted", "x.md"), crlfDoc);

    const plan = await buildAdoptionPlan({ root: repo, out, horizonDays: 180, today: TODAY });
    expect(plan.backfill.some((b) => b.path === "docs/already-fronted/x.md")).toBe(false);
    expect(plan.relabels.some((r) => r.path === "docs/already-fronted/x.md")).toBe(false);
  });

  it("still flags CRLF-fronted content whose existing front matter is invalid, but never as 'no front matter at all'", async () => {
    const out = tmp();
    // Not every CRLF-fronted file is KB-shaped (e.g. a Claude Skill manifest's
    // `name`/`description` front matter) — that's a real, separate problem
    // (front matter exists, but isn't a valid KB doc) and SHOULD still be
    // flagged for a human to resolve. The point is it must be flagged via the
    // "existing front matter is invalid" path, not silently treated as if
    // there were no front matter and prepended with a second block.
    const skillLikeDoc =
      "---\r\nname: some-skill\r\ndescription: does a thing\r\n---\r\n\r\nBody\r\n";
    const repo = mkdtempSync(join(tmpdir(), "team-ai-crlf-invalid-"));
    dirs.push(repo);
    cpSync(FIXTURE, repo, { recursive: true });
    mkdirSync(join(repo, "docs", "skills"), { recursive: true });
    writeFileSync(join(repo, "docs", "skills", "y.md"), skillLikeDoc);

    const plan = await buildAdoptionPlan({ root: repo, out, horizonDays: 180, today: TODAY });
    const item = plan.backfill.find((b) => b.path === "docs/skills/y.md");
    expect(item).toBeDefined();
    expect(item?.conflict).not.toBeNull(); // flagged as invalid existing front matter
    expect(item?.conflict).toMatch(/must have required property|required/i);
  });
});
