import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";
import { afterEach, describe, expect, it, vi } from "vitest";

import { run } from "./attach.js";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
afterEach(() => {
  log.mockClear();
  error.mockClear();
});

function puller(queue: string[]): () => Promise<string> {
  let idx = 0;
  return () => Promise.resolve(queue[idx++] ?? "");
}

const ANSWERS = [
  "github.com/your-org/team-ai-core",
  "billing-sme, onboarding-sme",
  "kb-answer",
  "operating, platform",
];

describe("team-ai attach", () => {
  it("writes a .team-ai.yaml with exactly the five attach keys and mode attach", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-attach-"));
    const code = await run({ dir, answers: puller(ANSWERS) });
    expect(code).toBe(0);

    const parsed = parseYaml(readFileSync(join(dir, ".team-ai.yaml"), "utf8")) as Record<
      string,
      unknown
    >;
    expect(Object.keys(parsed).sort()).toEqual(
      ["agents", "instance", "kb_namespaces", "mode", "skills"].sort(),
    );
    expect(parsed.mode).toBe("attach");
    expect(parsed.agents).toEqual(["billing-sme", "onboarding-sme"]);
    expect(parsed.kb_namespaces).toEqual(["operating", "platform"]);
    expect(log).toHaveBeenCalledWith("OK — .team-ai.yaml written (attach mode)");
  });

  it("refuses to overwrite an existing .team-ai.yaml without --force", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-attach-"));
    expect(await run({ dir, answers: puller(ANSWERS) })).toBe(0);
    const code = await run({ dir, answers: puller(ANSWERS) });
    expect(code).toBe(1);
    expect(error).toHaveBeenCalledWith(".team-ai.yaml already exists (use --force to overwrite)");
  });
});
