// Deterministic. No model calls.
//
// Pure contract check for a spoke repo. A spoke ships a spoke.yaml, a kb/
// directory of front-matter-valid documents, and optionally agents/ definitions.
// Retrieval, server code, indexing, the schema contract, and scaffolding
// templates all live in the core repo; a spoke that carries any of them fails
// the contract and each such violation is counted as a required core edit.

import { readFile, readdir, stat } from "node:fs/promises";
import { join, relative } from "node:path";

import { parse as parseYaml } from "yaml";

import { KbValidationError, loadKb } from "../kb/loader.js";
import { resolveKbScope } from "../retrieval/index-lock.js";
import { validate } from "../schema/validate.js";

export interface SpokeValidationResult {
  ok: boolean;
  errors: string[];
  coreEditsRequired: number;
}

function toPosix(relPath: string): string {
  return relPath.split(/[\\/]/).join("/");
}

async function pathExists(target: string): Promise<boolean> {
  try {
    await stat(target);
    return true;
  } catch {
    return false;
  }
}

async function isDirectory(target: string): Promise<boolean> {
  try {
    return (await stat(target)).isDirectory();
  } catch {
    return false;
  }
}

async function walk(dir: string): Promise<string[]> {
  try {
    const entries = await readdir(dir, { recursive: true });
    return entries.map(toPosix).sort((a, b) => a.localeCompare(b));
  } catch {
    return [];
  }
}

async function checkSpokeConfig(dir: string, errors: string[]): Promise<void> {
  const spokePath = join(dir, "spoke.yaml");
  if (!(await pathExists(spokePath))) {
    errors.push("spoke.yaml not found");
    return;
  }

  let parsed: unknown;
  try {
    parsed = parseYaml(await readFile(spokePath, "utf8")) as unknown;
  } catch (err) {
    errors.push(`spoke.yaml: not valid YAML (${err instanceof Error ? err.message : String(err)})`);
    return;
  }

  const result = validate("spoke", parsed);
  if (!result.ok) {
    for (const failure of result.errors) errors.push(`spoke.yaml: ${failure}`);
  }
}

async function checkKb(dir: string, errors: string[]): Promise<void> {
  let label = "kb";
  try {
    const scope = resolveKbScope(dir);
    label = toPosix(relative(dir, scope.root)) || ".";
    await loadKb(scope.root, { exclude: scope.exclude });
  } catch (err) {
    if (err instanceof KbValidationError) {
      for (const failure of err.failures) {
        errors.push(`${label}/${failure.file}: ${failure.error}`);
      }
      return;
    }
    if (err instanceof Error && err.message.startsWith("KB root not found")) {
      errors.push(`${label}/ directory is required`);
      return;
    }
    errors.push(err instanceof Error ? err.message : String(err));
  }
}

async function checkAgents(dir: string, errors: string[]): Promise<void> {
  const agentsDir = join(dir, "agents");
  if (!(await isDirectory(agentsDir))) return;

  const yamlFiles = (await walk(agentsDir)).filter((rel) => rel.endsWith(".yaml"));
  for (const rel of yamlFiles) {
    const full = join(agentsDir, rel);
    if (!(await stat(full)).isFile()) continue;

    let parsed: unknown;
    try {
      parsed = parseYaml(await readFile(full, "utf8")) as unknown;
    } catch (err) {
      errors.push(
        `agents/${rel}: not valid YAML (${err instanceof Error ? err.message : String(err)})`,
      );
      continue;
    }

    const result = validate("agent", parsed);
    if (!result.ok) {
      for (const failure of result.errors) errors.push(`agents/${rel}: ${failure}`);
    }
  }
}

const ADAPTER_DIR_FILE = /(^|\/)adapters\/[^/]+\.ts$/;
const RETRIEVAL_FILE = /(^|\/)(lexical|graph|hybrid|vector-[^/]*)\.ts$/;

async function findForbidden(dir: string): Promise<string[]> {
  const violations: string[] = [];

  if (await isDirectory(join(dir, "server"))) {
    violations.push(
      "a spoke ships no server/ (retrieval, server, and indexing live in the core repo)",
    );
  }
  if (await isDirectory(join(dir, "schemas"))) {
    violations.push("a spoke ships no schemas/ (the schema contract lives in the core repo)");
  }
  if (await isDirectory(join(dir, "templates"))) {
    violations.push("a spoke ships no templates/ (scaffolding templates live in the core repo)");
  }
  if (await pathExists(join(dir, "index.lock"))) {
    violations.push("a spoke ships no index.lock (the retrieval index is built in the core repo)");
  }

  for (const rel of await walk(dir)) {
    if (ADAPTER_DIR_FILE.test(rel) || RETRIEVAL_FILE.test(rel)) {
      violations.push(
        `a spoke ships no retrieval adapter code (${rel}); retrieval lives in the core repo`,
      );
    }
  }

  return violations;
}

export async function validateSpoke(dir: string): Promise<SpokeValidationResult> {
  const errors: string[] = [];

  await checkSpokeConfig(dir, errors);
  await checkKb(dir, errors);
  await checkAgents(dir, errors);

  const forbidden = await findForbidden(dir);
  for (const violation of forbidden) errors.push(violation);

  return {
    ok: errors.length === 0,
    errors,
    coreEditsRequired: forbidden.length,
  };
}
