// Deterministic. No model calls. No network.
//
// applyFrontmatter prepends an inferred FrontMatter block to a markdown file
// that has none. It never deletes and never rewrites: a file that already opens
// with `---` is left exactly as it was and reported back as a no-op.

import { readFileSync, writeFileSync } from "node:fs";

import { serializeFrontmatter } from "../kb/frontmatter.js";
import type { FrontMatter } from "../schema/types.js";

export interface ApplyFrontmatterOptions {
  dryRun?: boolean;
}

export interface ApplyFrontmatterResult {
  ok: boolean;
  reason?: string;
  content?: string;
}

// A real file can open with CRLF line endings ("---\r\n"), which an exact
// "---\n" prefix check misses entirely — the file reads as having NO front
// matter when it actually does. Two places need this same check to agree
// (plan-time detection and apply-time detection): if they disagree, plan
// generation schedules a backfill item for a file that already has front
// matter, and only apply-time's own guard stops it from being prepended a
// second time. Single source of truth here so that mismatch can't happen.
export function hasFrontmatter(raw: string): boolean {
  return /^---\r?\n/.test(raw);
}

export function applyFrontmatter(
  absPath: string,
  fm: FrontMatter,
  opts: ApplyFrontmatterOptions,
): ApplyFrontmatterResult {
  const raw = readFileSync(absPath, "utf8");
  if (hasFrontmatter(raw)) return { ok: false, reason: "already has front matter" };

  const content = serializeFrontmatter(fm as unknown as Record<string, unknown>, raw);
  if (opts.dryRun === true) return { ok: true, content };

  writeFileSync(absPath, content, "utf8");
  return { ok: true };
}
