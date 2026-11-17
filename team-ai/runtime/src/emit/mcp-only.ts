// Deterministic. No model calls. No network.
//
// Emit a generated instance as a flat prompt registry for an app client that
// talks to the knowledge base over MCP and needs only each agent's description,
// model tier, and instruction text — no file layout, no routing graph.

import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";

import type { EmitInput } from "./index.js";

function write(path: string, content: string): string {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content, "utf8");
  return path;
}

export function emitMcpOnly(input: EmitInput, outDir: string): string[] {
  const registry: Record<
    string,
    { description: string; model_tier: string; instructions: string }
  > = {};
  for (const agent of input.agents) {
    registry[agent.name] = {
      description: agent.def.description,
      model_tier: agent.def.model_tier,
      instructions: agent.instructions.trim(),
    };
  }
  return [write(join(outDir, "prompt-registry.json"), `${JSON.stringify(registry, null, 2)}\n`)];
}
