// Deterministic. No model calls. No network.

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";

import { loadEmitInput } from "../emit/index.js";
import { checkManifestInvariants } from "../manifest/invariants.js";
import type { AgentDef } from "../schema/types.js";
import { validate } from "../schema/validate.js";

export interface ValidateManifestOptions {
  root?: string;
}

export async function run(opts: ValidateManifestOptions): Promise<number> {
  const root = opts.root ?? ".";
  const file = join(root, "manifest.yaml");
  if (!existsSync(file)) {
    console.error(`validate-manifest: no manifest.yaml under ${root}`);
    return 1;
  }
  const result = validate("manifest", parseYaml(readFileSync(file, "utf8")));
  if (!result.ok) {
    for (const error of result.errors) console.error(`manifest.yaml: ${error}`);
    return 1;
  }
  if ((result.value.agents ?? []).length === 0) {
    console.log("validate-manifest: OK (no agents section; topology invariants not checked)");
    return 0;
  }

  const input = await loadEmitInput(root);
  const definitions = new Map<string, AgentDef>(input.agents.map((a) => [a.name, a.def]));
  const violations = checkManifestInvariants(result.value, definitions);
  for (const v of violations) console.error(`${v.subject}: [${v.rule}] ${v.message}`);
  if (violations.length > 0) return 1;

  console.log(`validate-manifest: OK (${result.value.agents?.length ?? 0} agents)`);
  return 0;
}
