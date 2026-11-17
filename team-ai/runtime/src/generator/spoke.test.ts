import { existsSync, mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";
import { afterEach, describe, expect, it, vi } from "vitest";

import { validate } from "../schema/validate.js";
import { validateSpoke } from "../spoke/validate.js";
import { run } from "./spoke.js";

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
  "partner-x-spoke",
  "partners/partner-x",
  "partner-lead",
  "github.com/your-org/team-ai-core",
  "partner-x-support",
  "Integration and support questions for partner-x.",
];

describe("team-ai spoke", () => {
  it("generates a spoke.yaml that passes validateSpoke with 0 core edits", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-spoke-"));
    const code = await run({ dir, answers: puller(ANSWERS) });
    expect(code).toBe(0);

    expect(existsSync(join(dir, "spoke.yaml"))).toBe(true);
    const parsed = parseYaml(readFileSync(join(dir, "spoke.yaml"), "utf8")) as Record<
      string,
      unknown
    >;
    expect(validate("spoke", parsed).ok).toBe(true);
    expect(parsed.name).toBe("partner-x-spoke");
    expect(parsed.kb_namespace).toBe("partners/partner-x");
    expect((parsed.domains as { subagent: string }[])[0]?.subagent).toBe("partner-x-support-sme");

    const v = await validateSpoke(dir);
    expect(v.ok).toBe(true);
    expect(v.coreEditsRequired).toBe(0);

    expect(log).toHaveBeenCalledWith(
      "OK — spoke 'partner-x-spoke' generated (0 core edits required)",
    );
  });

  it("refuses to overwrite an existing spoke.yaml without --force", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-spoke-"));
    expect(await run({ dir, answers: puller(ANSWERS) })).toBe(0);

    const code = await run({ dir, answers: puller(ANSWERS) });
    expect(code).toBe(1);
    expect(error).toHaveBeenCalledWith("spoke.yaml already exists (use --force to overwrite)");
  });
});
