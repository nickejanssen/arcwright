// Deterministic. No model calls. No network.

import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { getLastModifiedMap } from "./git-owner.js";

const dirs: string[] = [];

function tmp(): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-gitdate-"));
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

afterEach(() => {
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("getLastModifiedMap", () => {
  it("returns each path's most recent commit date from one traversal, not its first", () => {
    const repo = tmp();
    git(repo, ["init", "-q"]);
    git(repo, ["config", "user.email", "t@example.com"]);
    git(repo, ["config", "user.name", "Test"]);
    mkdirSync(join(repo, "docs"), { recursive: true });

    writeFileSync(join(repo, "docs", "a.md"), "# A\n");
    writeFileSync(join(repo, "docs", "b.md"), "# B\n");
    git(repo, ["add", "."]);
    git(repo, ["commit", "-q", "-m", "old"], "2024-01-10T00:00:00Z");

    // Only a.md is touched again — its last-modified date must move forward;
    // b.md's must stay at the first (and only) commit that touched it.
    writeFileSync(join(repo, "docs", "a.md"), "# A\n\nupdated\n");
    git(repo, ["add", "."]);
    git(repo, ["commit", "-q", "-m", "update a"], "2025-06-01T00:00:00Z");

    const map = getLastModifiedMap(repo, "docs");
    expect(map.get("docs/a.md")?.toISOString().slice(0, 10)).toBe("2025-06-01");
    expect(map.get("docs/b.md")?.toISOString().slice(0, 10)).toBe("2024-01-10");
    expect(map.has("docs/missing.md")).toBe(false);
  });

  it("returns an empty map for a directory with no git history, and never throws", () => {
    const repo = tmp();
    expect(() => getLastModifiedMap(repo, ".")).not.toThrow();
    expect(getLastModifiedMap(repo, ".").size).toBe(0);
  });
});
