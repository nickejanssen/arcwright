// Deterministic. No model calls. No network.
//
// Emit a generated instance in a platform-neutral shape: a single `agents.json`
// describing every agent's routing-relevant fields, plus one `prompts/<name>.md`
// per agent holding its instruction text. `parseGeneric` reads `agents.json`
// back for round-trip checks.

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";

import { resolveWithin } from "../generator/contain.js";
import type { EmitInput } from "./index.js";

interface GenericAgent {
  name: string;
  kind: string;
  model_tier: string;
  kb_namespaces: string[];
  tools: string[];
  max_hops: number;
}

// Agent names come from instance files a person can edit, so every path is
// resolved through `resolveWithin` rather than joined blindly.
function write(outDir: string, rel: string, content: string): string {
  const path = resolveWithin(outDir, rel);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content, "utf8");
  return path;
}

export function emitGeneric(input: EmitInput, outDir: string): string[] {
  const written: string[] = [];

  const agents: GenericAgent[] = input.agents.map((agent) => ({
    name: agent.def.name,
    kind: agent.def.kind,
    model_tier: agent.def.model_tier,
    kb_namespaces: agent.def.kb_namespaces,
    tools: agent.def.tools,
    max_hops: agent.def.max_hops,
  }));
  written.push(write(outDir, "agents.json", `${JSON.stringify(agents, null, 2)}\n`));

  for (const agent of input.agents) {
    const body = agent.instructions.trim();
    written.push(
      write(outDir, `prompts/${agent.name}.md`, `${body}${body.length > 0 ? "\n" : ""}`),
    );
  }

  return written;
}

export function parseGeneric(outDir: string): { name: string; model_tier: string }[] {
  const file = join(outDir, "agents.json");
  if (!existsSync(file)) return [];
  const parsed: unknown = JSON.parse(readFileSync(file, "utf8"));
  if (!Array.isArray(parsed)) return [];
  const out: { name: string; model_tier: string }[] = [];
  for (const item of parsed) {
    if (item !== null && typeof item === "object") {
      const rec = item as Record<string, unknown>;
      if (typeof rec.name === "string" && typeof rec.model_tier === "string") {
        out.push({ name: rec.name, model_tier: rec.model_tier });
      }
    }
  }
  return out;
}
