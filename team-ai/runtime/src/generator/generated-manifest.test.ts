import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { parse as parseYaml, stringify as stringifyYaml } from "yaml";
import { describe, expect, it } from "vitest";

import { mergeGeneratedManifest, readGeneratedManifest, sha256Of } from "./generated-manifest.js";

function tempDir(): string {
  return mkdtempSync(join(tmpdir(), "team-ai-genman-"));
}

describe("sha256Of", () => {
  it("is a stable lowercase hex digest", () => {
    expect(sha256Of("hello")).toBe(sha256Of("hello"));
    expect(sha256Of("hello")).toMatch(/^[a-f0-9]{64}$/);
    expect(sha256Of("hello")).not.toBe(sha256Of("world"));
  });
});

describe("readGeneratedManifest", () => {
  it("returns [] when team-profile.yaml is absent", () => {
    expect(readGeneratedManifest(tempDir())).toEqual([]);
  });

  it("returns [] when the key is missing", () => {
    const dir = tempDir();
    writeFileSync(join(dir, "team-profile.yaml"), stringifyYaml({ team_ai_version: "0.1.0" }));
    expect(readGeneratedManifest(dir)).toEqual([]);
  });

  it("reads the recorded entries", () => {
    const dir = tempDir();
    const entries = [{ path: "README.md", sha256: sha256Of("a") }];
    writeFileSync(join(dir, "team-profile.yaml"), stringifyYaml({ generated_paths: entries }));
    expect(readGeneratedManifest(dir)).toEqual(entries);
  });
});

describe("mergeGeneratedManifest", () => {
  it("no-ops with a warning when team-profile.yaml is absent", () => {
    const res = mergeGeneratedManifest(tempDir(), [{ path: "x", sha256: sha256Of("x") }]);
    expect(res.written).toBe(false);
    expect(res.warning).toMatch(/team-profile\.yaml/);
  });

  it("unions by path (newer sha wins) and preserves other keys", () => {
    const dir = tempDir();
    writeFileSync(
      join(dir, "team-profile.yaml"),
      stringifyYaml({
        team_ai_version: "0.1.0",
        answers: { "team.name": "x" },
        generated_paths: [
          { path: "readme.md", sha256: sha256Of("old") },
          { path: "index.lock", sha256: sha256Of("lock") },
        ],
      }),
    );

    const res = mergeGeneratedManifest(dir, [
      { path: "readme.md", sha256: sha256Of("new") },
      { path: "docs/strategy.md", sha256: sha256Of("s") },
    ]);
    expect(res.written).toBe(true);

    const profile = parseYaml(readFileSync(join(dir, "team-profile.yaml"), "utf8")) as {
      team_ai_version: string;
      answers: Record<string, unknown>;
      generated_paths: { path: string; sha256: string }[];
    };
    expect(profile.team_ai_version).toBe("0.1.0");
    expect(profile.answers).toEqual({ "team.name": "x" });
    expect(profile.generated_paths).toEqual([
      { path: "docs/strategy.md", sha256: sha256Of("s") },
      { path: "index.lock", sha256: sha256Of("lock") },
      { path: "readme.md", sha256: sha256Of("new") },
    ]);
  });
});
