import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";
import { afterEach, describe, expect, it, vi } from "vitest";

import { readIndexLock } from "../retrieval/index-lock.js";
import { packageVersion } from "../version.js";
import { generateInstance } from "./fixtures/instance-fixture.js";
import { run } from "./upgrade.js";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
afterEach(() => {
  log.mockClear();
  error.mockClear();
});

describe("team-ai upgrade", () => {
  it("refreshes plumbing and index.lock chunk without touching kb or agents", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-upgrade-"));
    expect(await generateInstance(dir)).toBe(0);

    const kbPath = join(dir, "kb/operating/charter.md");
    const agentPath = join(dir, "agents/billing-api-sme.yaml");
    const kbBefore = readFileSync(kbPath, "utf8");
    const agentBefore = readFileSync(agentPath, "utf8");

    // Stale the index.lock chunk and drop a workflow file.
    writeFileSync(
      join(dir, "index.lock"),
      "driver: lexical\nchunk:\n  split_on: [h2]\n  target_tokens: 999\n  hard_cap: 1500\nembedding: null\nkb:\n  root: docs\n  exclude: [archive/]\n",
      "utf8",
    );
    rmSync(join(dir, ".github/workflows/validate.yml"));

    const code = await run({ dir, output: () => undefined });
    expect(code).toBe(0);

    // Plumbing restored.
    expect(existsSync(join(dir, ".github/workflows/validate.yml"))).toBe(true);
    const lock = readIndexLock(dir);
    expect(lock.chunk).toEqual({ split_on: ["h2", "h3"], target_tokens: 800, hard_cap: 1200 });
    expect(lock.driver).toBe("lexical");
    expect(lock.kb).toEqual({ root: "docs", exclude: ["archive/"] });

    // Content untouched.
    expect(readFileSync(kbPath, "utf8")).toBe(kbBefore);
    expect(readFileSync(agentPath, "utf8")).toBe(agentBefore);

    const profile = parseYaml(readFileSync(join(dir, "team-profile.yaml"), "utf8")) as {
      team_ai_version: string;
    };
    expect(profile.team_ai_version).toBe(packageVersion());
  });

  it("drops a sibling for a hand-edited plumbing file instead of overwriting it", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-upgrade-"));
    expect(await generateInstance(dir)).toBe(0);

    const gates = join(dir, "evals/gates.yaml");
    writeFileSync(gates, "hitRate: 0.5 # my override\n", "utf8");

    const code = await run({ dir, output: () => undefined });
    expect(code).toBe(0);
    expect(readFileSync(gates, "utf8")).toBe("hitRate: 0.5 # my override\n");
    expect(existsSync(`${gates}.team-ai-new`)).toBe(true);
  });

  it("returns 1 when there is no team-profile.yaml", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-upgrade-"));
    expect(await run({ dir, output: () => undefined })).toBe(1);
  });
});
