import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { parse as parseYaml } from "yaml";
import { describe, expect, it } from "vitest";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const SKILL_DIR = join(ROOT, "skills/scaffold-interview");
const SKILL_MD = join(SKILL_DIR, "SKILL.md");

describe("skills/scaffold-interview/SKILL.md", () => {
  it("exists", () => {
    expect(existsSync(SKILL_MD)).toBe(true);
  });

  const raw = readFileSync(SKILL_MD, "utf8");
  const fmMatch = raw.match(/^---\n([\s\S]*?)\n---\n/);
  const body = fmMatch ? raw.slice(fmMatch[0].length) : raw;

  it("has YAML front matter with name and a non-empty description", () => {
    expect(fmMatch, "front matter block").not.toBeNull();
    const fm = parseYaml(fmMatch![1] as string) as { name?: string; description?: string };
    expect(fm.name).toBe("scaffold-interview");
    expect(typeof fm.description).toBe("string");
    expect((fm.description ?? "").trim().length).toBeGreaterThan(0);
  });

  it("names every act 0 through 5", () => {
    for (let n = 0; n <= 5; n += 1) {
      expect(body, `Act ${n}`).toContain(`Act ${n}`);
    }
  });

  it("restates the engine's branching vocabulary and points at engine.ts", () => {
    for (const token of [
      "ask_if",
      "implies",
      "defer",
      "recommend",
      "team-profile.yaml",
      "engine.ts",
    ]) {
      expect(body, token).toContain(token);
    }
  });

  it("ships the question-flow reference", () => {
    expect(existsSync(join(SKILL_DIR, "reference/question-flow.md"))).toBe(true);
  });
});
