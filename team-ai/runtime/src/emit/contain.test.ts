import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { emitClaudeCode } from "./claude-code.js";
import { emitGeneric } from "./generic.js";
import type { EmitInput } from "./index.js";

const dirs: string[] = [];

function out(): string {
  // Nest one level so the escaped target lands inside a directory this test owns.
  const parent = mkdtempSync(join(tmpdir(), "team-ai-emit-contain-"));
  dirs.push(parent);
  return join(parent, "out");
}

function inputWithAgentName(name: string): EmitInput {
  return {
    agents: [
      {
        name,
        def: {
          name,
          kind: "subagent",
          description: "probe",
          model_tier: "small",
          kb_namespaces: ["operating"],
          tools: [],
          max_hops: 0,
          instructions_file: "agents/probe.md",
        },
        instructions: "body",
      },
    ],
    skills: [],
    personas: [],
    manifest: null,
  };
}

afterEach(() => {
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("emitters refuse agent names that escape the output directory", () => {
  it("emitClaudeCode", () => {
    const dir = out();
    expect(() => emitClaudeCode(inputWithAgentName("../../../escape"), dir)).toThrow(
      /refusing to write outside/,
    );
    expect(existsSync(resolve(dir, "..", "escape.md"))).toBe(false);
  });

  it("emitGeneric", () => {
    const dir = out();
    expect(() => emitGeneric(inputWithAgentName("../../escape"), dir)).toThrow(
      /refusing to write outside/,
    );
    expect(existsSync(resolve(dir, "..", "escape.md"))).toBe(false);
  });
});
