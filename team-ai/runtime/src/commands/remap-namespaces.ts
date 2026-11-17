// All file IO for `team-ai remap-namespaces`. Proposal by default; --apply writes.

import { existsSync, readFileSync, realpathSync, writeFileSync } from "node:fs";
import { basename, dirname, isAbsolute, join, relative, resolve, sep } from "node:path";

import { parse as parseYaml, stringify as stringifyYaml } from "yaml";

import { applyRemapPlan } from "../remap/apply.js";
import { buildRemapPlan, formatInventory, validateRemapMapping } from "../remap/plan.js";

export interface RemapNamespacesOptions {
  instance?: string;
  mapping?: string;
  out?: string;
  inventory?: string;
  apply?: boolean;
}

interface Artifact {
  label: string;
  path: string;
  content: string;
  write: boolean;
}

function canonicalPath(path: string): string {
  const abs = resolve(path);
  if (existsSync(abs)) return realpathSync.native(abs);
  return join(realpathSync.native(dirname(abs)), basename(abs));
}

function pathKey(path: string): string {
  return process.platform === "win32" ? path.toLowerCase() : path;
}

function isWithinOrEqual(root: string, target: string): boolean {
  const rel = relative(root, target);
  return rel === "" || (!isAbsolute(rel) && rel !== ".." && !rel.startsWith(`..${sep}`));
}

function prepareArtifacts(
  kbRoot: string,
  mappingPath: string,
  requested: { label: string; path: string; content: string }[],
): Artifact[] {
  const canonicalKbRoot = canonicalPath(kbRoot);
  const canonicalMapping = canonicalPath(mappingPath);
  const seen = new Map<string, string>();
  const artifacts = requested.map((artifact) => {
    const path = canonicalPath(artifact.path);
    const key = pathKey(path);
    const prior = seen.get(key);
    if (prior !== undefined) {
      throw new Error(`artifact path collision: ${prior} and ${artifact.label}`);
    }
    seen.set(key, artifact.label);
    if (key === pathKey(canonicalMapping)) {
      throw new Error(`${artifact.label} collides with the mapping file`);
    }
    if (isWithinOrEqual(canonicalKbRoot, path)) {
      throw new Error(`${artifact.label} must be outside the KB root`);
    }

    if (!existsSync(path)) return { ...artifact, path, write: true };
    const current = readFileSync(path, "utf8");
    if (current !== artifact.content) {
      throw new Error(`${artifact.label} already exists with different content: ${path}`);
    }
    return { ...artifact, path, write: false };
  });
  return artifacts;
}

function writeArtifacts(artifacts: Artifact[]): void {
  for (const artifact of artifacts) {
    if (!artifact.write) continue;
    try {
      writeFileSync(artifact.path, artifact.content, { encoding: "utf8", flag: "wx" });
    } catch (err) {
      if (err instanceof Error && "code" in err && err.code === "EEXIST") {
        if (readFileSync(artifact.path, "utf8") === artifact.content) continue;
        throw new Error(`${artifact.label} appeared with different content: ${artifact.path}`);
      }
      throw err;
    }
  }
}

function runChecked(opts: RemapNamespacesOptions): number {
  if (opts.mapping === undefined) {
    throw new Error("--mapping is required");
  }
  const mappingPath = canonicalPath(opts.mapping);
  const mapping = validateRemapMapping(parseYaml(readFileSync(mappingPath, "utf8")));
  const plan = buildRemapPlan({
    instance: opts.instance ?? ".",
    mapping,
  });

  const counts = { remap: 0, unchanged: 0, skipped: 0, conflict: 0 };
  for (const item of plan.items) counts[item.status] += 1;

  const out = opts.out ?? "remap-proposal.yaml";
  const requested = [
    { label: "proposal", path: out, content: stringifyYaml(plan) },
    ...(opts.inventory === undefined
      ? []
      : [{ label: "inventory", path: opts.inventory, content: formatInventory(plan) }]),
  ];
  writeArtifacts(prepareArtifacts(plan.kbRoot, mappingPath, requested));
  console.log(`remap proposal: ${out}`);
  console.log(
    `  remap ${counts.remap}  unchanged ${counts.unchanged}  skipped ${counts.skipped}  conflict ${counts.conflict}`,
  );
  for (const item of plan.items.filter((i) => i.status === "conflict")) {
    console.error(`  conflict: ${item.path} — ${item.reason ?? ""}`);
  }

  if (opts.apply !== true) return counts.conflict > 0 ? 1 : 0;
  const { written } = applyRemapPlan(plan);
  console.log(`  applied to ${written.length} file(s)`);
  return 0;
}

export function run(opts: RemapNamespacesOptions): Promise<number> {
  try {
    return Promise.resolve(runChecked(opts));
  } catch (err) {
    console.error(`remap-namespaces: ${err instanceof Error ? err.message : String(err)}`);
    return Promise.resolve(1);
  }
}
