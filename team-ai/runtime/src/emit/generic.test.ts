import { existsSync, mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { afterEach, describe, expect, it, vi } from "vitest";

import { run as emitRun } from "../commands/emit.js";
import { emitGeneric, parseGeneric } from "./generic.js";
import { loadEmitInput } from "./index.js";

const FIXTURE = fileURLToPath(new URL("./fixtures/instance", import.meta.url));

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
afterEach(() => {
  log.mockClear();
  error.mockClear();
});

describe("emitGeneric", () => {
  it("round-trips every agent name and model_tier through agents.json", async () => {
    const input = await loadEmitInput(FIXTURE);
    const out = mkdtempSync(join(tmpdir(), "team-ai-emit-generic-"));
    const written = emitGeneric(input, out);

    expect(written.some((p) => p.endsWith("agents.json"))).toBe(true);
    for (const agent of input.agents) {
      expect(existsSync(join(out, "prompts", `${agent.name}.md`))).toBe(true);
    }

    const parsed = parseGeneric(out).sort((a, b) => a.name.localeCompare(b.name));
    const expected = input.agents
      .map((a) => ({ name: a.def.name, model_tier: a.def.model_tier }))
      .sort((a, b) => a.name.localeCompare(b.name));
    expect(parsed).toEqual(expected);
  });
});

describe("emit.run", () => {
  it("emits the generic target and returns 0 with files under --out", async () => {
    const out = mkdtempSync(join(tmpdir(), "team-ai-emit-run-"));
    const code = await emitRun({ target: "generic", dir: FIXTURE, out });
    expect(code).toBe(0);
    expect(existsSync(join(out, "agents.json"))).toBe(true);
    expect(JSON.parse(readFileSync(join(out, "agents.json"), "utf8"))).toHaveLength(2);
  });

  it("rejects a missing or unknown target", async () => {
    expect(await emitRun({ dir: FIXTURE })).toBe(1);
    expect(await emitRun({ target: "nope", dir: FIXTURE })).toBe(1);
  });
});
