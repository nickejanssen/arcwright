// Deterministic. No model calls. No network.
//
// Path containment for every generator and emitter write. Entity names reach
// file paths from interview answers, team-profile.yaml, and catalog files, all
// of which a person can edit by hand, so a name like `../docs/agents/x` must
// never resolve to a path outside the directory being written.

import { isAbsolute, relative, resolve, sep } from "node:path";

/**
 * True when `target` resolves strictly inside `destResolved`. The destination
 * itself does not count as inside, and a child whose name merely starts with
 * two dots (`..foo`) is inside; only a real parent traversal is rejected.
 */
export function withinDest(destResolved: string, target: string): boolean {
  const rel = relative(destResolved, target);
  if (rel.length === 0 || isAbsolute(rel)) return false;
  return rel !== ".." && !rel.startsWith(`..${sep}`);
}

/**
 * Resolve `rel` against `destDir`, throwing instead of returning a path that
 * would escape it. Use this for every write whose path includes a name that
 * did not come from the framework's own templates.
 */
export function resolveWithin(destDir: string, rel: string): string {
  const dest = resolve(destDir);
  const abs = resolve(dest, rel);
  if (!withinDest(dest, abs)) {
    throw new Error(`refusing to write outside ${destDir}: ${rel}`);
  }
  return abs;
}
