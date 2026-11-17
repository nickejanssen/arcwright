// Deterministic. No model calls.
//
// Thin CLI wrapper over src/manifest/assemble.ts. Reads the instance manifest
// fragment and every spokes/<name>/spoke.yaml, then either writes a merged,
// schema-valid manifest.yaml or (with --check) verifies the committed file is
// current and exits non-zero when it drifts.

import { existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";

import { assembleManifest, serializeManifest } from "../manifest/assemble.js";

export interface AssembleManifestOptions {
  root?: string;
  check?: boolean;
}

interface SpokeInput {
  name: string;
  config: unknown;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readYamlFile(path: string): unknown {
  return parseYaml(readFileSync(path, "utf8"));
}

function readFragment(root: string): unknown {
  const path = join(root, "agents", "manifest.fragment.yaml");
  return existsSync(path) ? readYamlFile(path) : undefined;
}

function readSpokes(root: string): SpokeInput[] {
  const spokesDir = join(root, "spokes");
  if (!existsSync(spokesDir)) return [];

  const spokes: SpokeInput[] = [];
  for (const entry of readdirSync(spokesDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const path = join(spokesDir, entry.name, "spoke.yaml");
    if (!existsSync(path)) continue;
    spokes.push({ name: entry.name, config: readYamlFile(path) });
  }
  return spokes.sort((a, b) => a.name.localeCompare(b.name));
}

// Ignore trailing whitespace and final-newline differences when comparing the
// freshly assembled output to the committed file.
function normalize(text: string): string {
  return text
    .replace(/\r\n/g, "\n")
    .replace(/[ \t]+$/gm, "")
    .replace(/\n+$/, "");
}

function domainMap(text: string): Map<string, string> {
  const map = new Map<string, string>();
  let parsed: unknown;
  try {
    parsed = parseYaml(text);
  } catch {
    return map;
  }
  if (!isRecord(parsed) || !Array.isArray(parsed.domains)) return map;
  for (const domain of parsed.domains) {
    if (isRecord(domain) && typeof domain.id === "string") {
      map.set(domain.id, JSON.stringify(domain));
    }
  }
  return map;
}

function reportDrift(current: string, output: string): void {
  const before = domainMap(current);
  const after = domainMap(output);
  const added = [...after.keys()].filter((id) => !before.has(id)).sort();
  const removed = [...before.keys()].filter((id) => !after.has(id)).sort();
  const changed = [...after.keys()]
    .filter((id) => before.has(id) && before.get(id) !== after.get(id))
    .sort();

  if (added.length > 0) console.error(`  added:   ${added.join(", ")}`);
  if (removed.length > 0) console.error(`  removed: ${removed.join(", ")}`);
  if (changed.length > 0) console.error(`  changed: ${changed.join(", ")}`);
}

export function run(opts: AssembleManifestOptions): Promise<number> {
  return Promise.resolve(assemble(opts));
}

// Fully synchronous; the command surface is Promise-based for consistency with
// the other commands.
function assemble(opts: AssembleManifestOptions): number {
  const root = opts.root ?? ".";
  const check = opts.check ?? false;

  let output: string;
  let domainCount: number;
  try {
    const manifest = assembleManifest({
      fragment: readFragment(root),
      spokes: readSpokes(root),
    });
    output = serializeManifest(manifest);
    domainCount = manifest.domains.length;
  } catch (err) {
    console.error(err instanceof Error ? err.message : String(err));
    return 1;
  }

  const manifestPath = join(root, "manifest.yaml");

  if (check) {
    if (!existsSync(manifestPath)) {
      console.error("manifest.yaml missing; run without --check to generate");
      return 1;
    }
    const current = readFileSync(manifestPath, "utf8");
    if (normalize(current) === normalize(output)) {
      console.log(`manifest.yaml up to date (${domainCount} domains)`);
      return 0;
    }
    console.error("manifest.yaml is stale — run 'team-ai assemble-manifest' to regenerate");
    reportDrift(current, output);
    return 1;
  }

  writeFileSync(manifestPath, output, "utf8");
  console.log(`wrote manifest.yaml (${domainCount} domains)`);
  return 0;
}
