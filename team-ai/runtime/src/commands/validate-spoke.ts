// Deterministic. No model calls.
//
// Thin CLI wrapper over src/spoke/validate.ts. Checks a spoke repo against the
// spoke contract: requires spoke.yaml and a front-matter-valid kb/, validates
// any agents/ definitions, and flags forbidden content that belongs in the core
// repo (server/, retrieval adapters, index.lock, schemas/, templates/). Prints
// errors and the core-edit count to stderr; on success prints an OK line to
// stdout. Exit code is 0 when compliant, 1 otherwise.

import { readFile } from "node:fs/promises";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";

import { validateSpoke } from "../spoke/validate.js";

export interface ValidateSpokeOptions {
  root?: string;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

async function readSpokeName(root: string): Promise<string> {
  try {
    const parsed: unknown = parseYaml(await readFile(join(root, "spoke.yaml"), "utf8")) as unknown;
    if (isRecord(parsed) && typeof parsed.name === "string" && parsed.name.length > 0) {
      return parsed.name;
    }
  } catch {
    // fall through to the placeholder
  }
  return "unknown";
}

export async function run(opts: ValidateSpokeOptions): Promise<number> {
  const root = opts.root ?? ".";
  const result = await validateSpoke(root);

  for (const error of result.errors) console.error(error);
  console.error(`coreEditsRequired: ${result.coreEditsRequired}`);

  if (result.ok) {
    const name = await readSpokeName(root);
    console.log(`OK — spoke '${name}' is contract-compliant (0 core edits required)`);
    return 0;
  }

  return 1;
}
