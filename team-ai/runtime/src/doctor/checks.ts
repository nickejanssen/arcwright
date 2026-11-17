// Deterministic. No model calls. No network.
//
// The pure checks behind `team-ai doctor`. Two families:
//
//   runSelfChecks(repoRoot)   framework self-verification used by CI
//                             (`team-ai doctor --self`)
//   runInstanceChecks(root)   the interview-spec setup checklist, run against a
//                             forked instance directory
//
// Every check returns a CheckResult. `skipped: true` marks a "not built yet"
// item: it counts as a pass by default and as a failure under `--strict`
// (the CLI decides; these functions only report).

import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";

import { parse as parseYaml } from "yaml";

import { parseDenylist } from "../commands/check-agnostic.js";
import { DEFAULT_GATES } from "../evals/run.js";
import { loadKb } from "../kb/loader.js";
import { resolveKbScope } from "../retrieval/index-lock.js";
import { loadValidator, type SchemaName } from "../schema/load.js";
import { validate } from "../schema/validate.js";

export interface CheckResult {
  label: string;
  ok: boolean;
  note?: string;
  skipped?: boolean;
}

function pass(label: string, note?: string): CheckResult {
  return note === undefined ? { label, ok: true } : { label, ok: true, note };
}

function fail(label: string, note?: string): CheckResult {
  return note === undefined ? { label, ok: false } : { label, ok: false, note };
}

function skip(label: string, note: string): CheckResult {
  return { label, ok: true, skipped: true, note };
}

function firstLine(message: string): string {
  return message.split(/\r?\n/)[0] ?? message;
}

// ---------------------------------------------------------------------------
// Self checks (framework)
// ---------------------------------------------------------------------------

const SCHEMA_NAMES: readonly SchemaName[] = [
  "frontmatter",
  "agent",
  "manifest",
  "spoke",
  "team-profile",
  "golden",
];

export function checkSchemasCompile(repoRoot: string): CheckResult {
  const label = "schemas load and Ajv-compile";
  try {
    for (const name of SCHEMA_NAMES) {
      if (loadValidator(name) === undefined) {
        return fail(label, `${name}.schema.json did not compile`);
      }
    }
  } catch (err) {
    return fail(label, err instanceof Error ? firstLine(err.message) : String(err));
  }

  const schemasDir = join(repoRoot, "schemas");
  let jsonFiles: string[];
  try {
    jsonFiles = readdirSync(schemasDir).filter((file) => file.endsWith(".schema.json"));
  } catch {
    return fail(label, "schemas/ directory not found");
  }

  const known = new Set(SCHEMA_NAMES.map((name) => `${name}.schema.json`));
  let extra = 0;
  for (const file of jsonFiles) {
    if (known.has(file)) continue;
    extra += 1;
    try {
      JSON.parse(readFileSync(join(schemasDir, file), "utf8"));
    } catch (err) {
      return fail(label, `${file}: ${err instanceof Error ? firstLine(err.message) : String(err)}`);
    }
  }

  const suffix = extra > 0 ? `, ${extra} extra parsed` : "";
  return pass(label, `${SCHEMA_NAMES.length} compiled${suffix}`);
}

export function checkDenylist(repoRoot: string): CheckResult {
  const label = "agnostic-denylist.txt present and non-empty";
  const path = join(repoRoot, "agnostic-denylist.txt");
  if (!existsSync(path)) return fail(label, "file not found");
  const { denied } = parseDenylist(readFileSync(path, "utf8"));
  if (denied.length === 0) return fail(label, "no denied tokens defined");
  return pass(label, `${denied.length} denied token(s)`);
}

export function checkBinResolves(repoRoot: string): CheckResult {
  const label = "package.json bin.team-ai resolves";
  let pkg: { bin?: Record<string, unknown> };
  try {
    pkg = JSON.parse(readFileSync(join(repoRoot, "package.json"), "utf8")) as {
      bin?: Record<string, unknown>;
    };
  } catch (err) {
    return fail(label, err instanceof Error ? firstLine(err.message) : String(err));
  }
  const target = pkg.bin?.["team-ai"];
  if (typeof target !== "string" || target.length === 0) {
    return fail(label, "no bin.team-ai entry");
  }
  if (!existsSync(join(repoRoot, target))) return fail(label, `${target} does not exist`);
  return pass(label, target);
}

export function checkGatesMatchDefault(repoRoot: string): CheckResult {
  const label = "evals/gates.yaml matches DEFAULT_GATES";
  const path = join(repoRoot, "evals", "gates.yaml");
  if (!existsSync(path)) return fail(label, "file not found");

  let parsed: unknown;
  try {
    parsed = parseYaml(readFileSync(path, "utf8"));
  } catch (err) {
    return fail(label, err instanceof Error ? firstLine(err.message) : String(err));
  }
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    return fail(label, "not a mapping");
  }

  const record = parsed as Record<string, unknown>;
  const keys = Object.keys(DEFAULT_GATES) as (keyof typeof DEFAULT_GATES)[];
  const extra = Object.keys(record).filter((key) => !(keys as string[]).includes(key));
  if (extra.length > 0) return fail(label, `unexpected key(s): ${extra.join(", ")}`);

  for (const key of keys) {
    if (record[key] !== DEFAULT_GATES[key]) {
      return fail(label, `${key}: ${String(record[key])} != ${String(DEFAULT_GATES[key])}`);
    }
  }
  return pass(label, `${keys.length} gate(s) aligned`);
}

export function checkQuestionsYaml(repoRoot: string): CheckResult {
  const label = "src/interview/questions.yaml parses";
  const path = join(repoRoot, "src", "interview", "questions.yaml");
  if (!existsSync(path)) return skip(label, "(not built yet)");
  try {
    parseYaml(readFileSync(path, "utf8"));
  } catch (err) {
    return fail(label, err instanceof Error ? firstLine(err.message) : String(err));
  }
  return pass(label);
}

export function checkTemplatesDir(repoRoot: string): CheckResult {
  const label = "templates/ present";
  const dir = join(repoRoot, "templates");
  if (!existsSync(dir)) return skip(label, "(not built yet)");
  let count = 0;
  try {
    count = readdirSync(dir).length;
  } catch {
    // an unreadable directory still counts as present
  }
  return pass(label, `${count} entr${count === 1 ? "y" : "ies"}`);
}

export function runSelfChecks(repoRoot: string): CheckResult[] {
  return [
    checkSchemasCompile(repoRoot),
    checkDenylist(repoRoot),
    checkBinResolves(repoRoot),
    checkGatesMatchDefault(repoRoot),
    checkQuestionsYaml(repoRoot),
    checkTemplatesDir(repoRoot),
  ];
}

// ---------------------------------------------------------------------------
// Instance checks (forked team repo) — the interview-spec setup checklist
// ---------------------------------------------------------------------------

export function checkRepoStructure(root: string): CheckResult {
  const label = "repo structure";
  let scope: ReturnType<typeof resolveKbScope>;
  try {
    scope = resolveKbScope(root);
  } catch (err) {
    return fail(label, err instanceof Error ? firstLine(err.message) : String(err));
  }
  const kbLabel = relative(root, scope.root).split(/[\\/]/).join("/") || ".";
  const hasKb = existsSync(scope.root);
  const hasManifest =
    existsSync(join(root, "manifest.yaml")) ||
    existsSync(join(root, "agents", "manifest.fragment.yaml"));
  if (hasKb && hasManifest) return pass(label);

  const missing: string[] = [];
  if (!hasKb) missing.push(`${kbLabel}/`);
  if (!hasManifest) missing.push("manifest.yaml or agents/manifest.fragment.yaml");
  return fail(label, `missing ${missing.join(", ")}`);
}

export async function checkSeedDocuments(root: string): Promise<CheckResult> {
  const label = "seed documents pass front matter";
  try {
    const scope = resolveKbScope(root);
    const docs = await loadKb(scope.root, { exclude: scope.exclude });
    return pass(label, `${docs.length} doc(s)`);
  } catch (err) {
    return fail(label, err instanceof Error ? firstLine(err.message) : String(err));
  }
}

export function checkIndexBuilt(root: string): CheckResult {
  const label = "index built";
  if (existsSync(join(root, ".team-ai", "index.sqlite"))) return pass(label);
  return fail(label, "run 'team-ai reindex'");
}

export function checkManifestAssembled(root: string): CheckResult {
  const label = "manifest assembled";
  const path = join(root, "manifest.yaml");
  if (!existsSync(path)) return fail(label, "manifest.yaml not found");

  let parsed: unknown;
  try {
    parsed = parseYaml(readFileSync(path, "utf8"));
  } catch (err) {
    return fail(label, err instanceof Error ? firstLine(err.message) : String(err));
  }
  const result = validate("manifest", parsed);
  if (!result.ok) return fail(label, result.errors[0] ?? "invalid manifest");
  return pass(label, `${result.value.domains.length} domain(s)`);
}

export function checkMcpTokenMinted(): CheckResult {
  return fail("MCP reader token minted", "manual — see SETUP.md");
}

export function checkConnectorRegistered(): CheckResult {
  return fail("connector registered in chat apps", "manual — see SETUP.md");
}

export function checkGoldenAnswers(root: string): CheckResult {
  const label = "golden eval answers filled in";
  const dir = join(root, "evals", "golden");
  let entries: string[];
  try {
    entries = readdirSync(dir, { recursive: true, encoding: "utf8" });
  } catch {
    return fail(label, "no evals/golden/ directory");
  }

  let filled = 0;
  for (const entry of entries) {
    if (!entry.endsWith(".golden.yaml")) continue;
    const head = firstLine(readFileSync(join(dir, entry), "utf8"));
    if (head.includes("EXAMPLE")) continue;
    filled += 1;
  }
  if (filled === 0) {
    return fail(label, "add a non-EXAMPLE *.golden.yaml under evals/golden/");
  }
  return pass(label, `${filled} set(s)`);
}

export async function runInstanceChecks(root: string): Promise<CheckResult[]> {
  return [
    checkRepoStructure(root),
    await checkSeedDocuments(root),
    checkIndexBuilt(root),
    checkManifestAssembled(root),
    checkMcpTokenMinted(),
    checkConnectorRegistered(),
    checkGoldenAnswers(root),
  ];
}
