// Deterministic. No model calls. No network.
//
// The generated-file manifest records which paths in an instance were written by
// a team-ai render and the sha256 of the exact bytes that were written. It lives
// inside `team-profile.yaml` under `generated_paths`, so a later render can tell
// a pristine prior render (safe to overwrite) from a hand-edited file (never
// overwrite). This module only reads and merges that list; the profile file is
// owned by the interview writer.

import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import { parse as parseYaml, stringify as stringifyYaml } from "yaml";

export interface GeneratedEntry {
  /** Repo-relative to the instance root, POSIX separators. */
  path: string;
  /** Lowercase hex sha256 of the rendered file content. */
  sha256: string;
}

const PROFILE_FILE = "team-profile.yaml";

export function sha256Of(content: string): string {
  return createHash("sha256").update(content, "utf8").digest("hex");
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function coerceEntries(value: unknown): GeneratedEntry[] {
  if (!Array.isArray(value)) return [];
  const out: GeneratedEntry[] = [];
  for (const item of value) {
    if (!isRecord(item)) continue;
    const { path, sha256 } = item;
    if (typeof path === "string" && typeof sha256 === "string") {
      out.push({ path, sha256 });
    }
  }
  return out;
}

/** The `generated_paths` list from `<destDir>/team-profile.yaml`, or `[]`. */
export function readGeneratedManifest(destDir: string): GeneratedEntry[] {
  const file = join(destDir, PROFILE_FILE);
  if (!existsSync(file)) return [];
  let parsed: unknown;
  try {
    parsed = parseYaml(readFileSync(file, "utf8"));
  } catch {
    return [];
  }
  if (!isRecord(parsed)) return [];
  return coerceEntries(parsed.generated_paths);
}

export interface MergeResult {
  written: boolean;
  warning?: string;
}

/**
 * Union `entries` into `team-profile.yaml`'s `generated_paths` (keyed by `path`,
 * the newer sha wins), preserving every other key. If the profile file does not
 * exist this is a no-op: the manifest has no home without it.
 */
export function mergeGeneratedManifest(destDir: string, entries: GeneratedEntry[]): MergeResult {
  const file = join(destDir, PROFILE_FILE);
  if (!existsSync(file)) {
    return {
      written: false,
      warning: `mergeGeneratedManifest: ${PROFILE_FILE} not found in ${destDir}; nothing recorded`,
    };
  }

  let parsed: unknown;
  try {
    parsed = parseYaml(readFileSync(file, "utf8"));
  } catch (err) {
    const reason = err instanceof Error ? err.message : String(err);
    return { written: false, warning: `mergeGeneratedManifest: ${file} did not parse: ${reason}` };
  }
  const profile: Record<string, unknown> = isRecord(parsed) ? { ...parsed } : {};

  const merged = new Map<string, string>();
  for (const entry of coerceEntries(profile.generated_paths)) {
    merged.set(entry.path, entry.sha256);
  }
  for (const entry of entries) {
    merged.set(entry.path, entry.sha256);
  }

  profile.generated_paths = [...merged.entries()]
    .map(([path, sha256]) => ({ path, sha256 }))
    .sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));

  writeFileSync(file, stringifyYaml(profile), "utf8");
  return { written: true };
}
