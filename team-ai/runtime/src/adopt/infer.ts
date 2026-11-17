// Deterministic. No model calls. No network.
//
// inferFrontmatter turns an un-annotated markdown file into a schema-valid
// FrontMatter block using only signals already present in the repo: the file
// path, the first heading, the git author history, and a few header markers
// that a sync pipeline leaves behind. Every field is computed by a fixed rule.

import { slug } from "../kb/slugify.js";
import type { FrontMatter } from "../schema/types.js";

export interface InferFrontmatterOptions {
  relPath: string;
  body: string;
  namespace: string;
  gitAuthors: string[];
  horizonDays: number;
  today: Date;
  // The doc's most recent git commit date, when known. `review_by` anchors
  // here instead of on `today` so pre-existing content that hasn't been
  // touched in years is honestly overdue on adoption, not given a fresh
  // multi-month grace period as if someone reviewed it today. Content with
  // no git history (untracked / newly authored) has no better anchor than
  // `today`, which is the prior behavior.
  lastModified?: Date | null;
}

const HEAD_LINES = 8;

function stripExtension(relPath: string): string {
  return relPath.replace(/\.[^./\\]+$/, "");
}

function pathSegments(relPath: string): string[] {
  return stripExtension(relPath)
    .split(/[/\\]/)
    .map((segment) => segment.trim())
    .filter((segment) => segment.length > 0);
}

export function namespaceIdSegment(namespace: string): string {
  return slug(namespace).replace(/-/g, "");
}

export function inferId(relPath: string, namespace: string): string {
  const first = namespaceIdSegment(namespace);
  const parts = [first, ...pathSegments(relPath).map((segment) => slug(segment))].filter(
    (part) => part.length > 0,
  );
  while (parts.length < 2) parts.push("doc");
  return parts.join(".");
}

function titleCase(stem: string): string {
  return stem
    .split(/[-_\s]+/)
    .filter((word) => word.length > 0)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function inferTitle(relPath: string, body: string): string {
  for (const line of body.split(/\r?\n/)) {
    const heading = line.match(/^#\s+(.+)$/);
    if (heading?.[1] !== undefined) return heading[1].trim();
  }
  const stem = pathSegments(relPath).at(-1) ?? "untitled";
  return titleCase(stem);
}

function inferOwner(gitAuthors: string[]): string {
  if (gitAuthors.length === 0) return "unassigned";
  const counts = new Map<string, number>();
  for (const author of gitAuthors) counts.set(author, (counts.get(author) ?? 0) + 1);
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0))
    .map(([name]) => name)[0] as string;
}

function inferReviewBy(anchor: Date, horizonDays: number): string {
  const at = new Date(
    Date.UTC(anchor.getUTCFullYear(), anchor.getUTCMonth(), anchor.getUTCDate() + horizonDays),
  );
  return at.toISOString().slice(0, 10);
}

function sanitizeSystem(system: string): string {
  const cleaned = system.toLowerCase().replace(/[^a-z0-9-]/g, "");
  return cleaned.length > 0 ? cleaned : "external";
}

// `authored` unless one of the first eight body lines carries a sync marker.
// A named system ("edit in Notion") is the most specific signal and wins over
// the generic "do not edit" / "> Source:" fallbacks even when it appears on a
// later line — otherwise a doc that leads with "> Source:" is mislabelled
// `synced:external` when it actually names its system two lines down.
export function detectSyncedSource(body: string): string | null {
  const head = body.split(/\r?\n/).slice(0, HEAD_LINES);
  for (const line of head) {
    const editIn = line.match(/edit in (\w+)/i);
    if (editIn?.[1] !== undefined) return `synced:${sanitizeSystem(editIn[1])}`;
  }
  for (const line of head) {
    if (/do not edit/i.test(line)) return "synced:external";
    if (/^>\s*Source:/i.test(line)) return "synced:external";
  }
  return null;
}

function inferTags(body: string): string[] {
  const match = body.match(/^\*\*Tags:\*\*\s*(.+)$/im);
  if (match?.[1] === undefined) return [];
  return match[1]
    .split(",")
    .map((tag) => slug(tag.trim().toLowerCase()))
    .filter((tag) => tag.length > 0);
}

export function inferFrontmatter(opts: InferFrontmatterOptions): FrontMatter {
  return {
    id: inferId(opts.relPath, opts.namespace),
    namespace: opts.namespace,
    title: inferTitle(opts.relPath, opts.body),
    owner: inferOwner(opts.gitAuthors),
    status: "active",
    review_by: inferReviewBy(opts.lastModified ?? opts.today, opts.horizonDays),
    sensitivity: "internal",
    source: detectSyncedSource(opts.body) ?? "authored",
    tags: inferTags(opts.body),
    supersedes: [],
  };
}
