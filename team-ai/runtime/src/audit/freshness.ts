// Pure freshness analysis over already-loaded KB docs. Deterministic: no
// filesystem, no network, no model calls, no clock — callers pass the docs and
// the reference date. The CLI wrapper (src/commands/freshness-audit.ts) owns I/O.

import { findCitationsInText } from "../kb/citations.js";
import type { KbDoc } from "../kb/types.js";

export interface FreshnessItem {
  id: string;
  path: string;
  owner: string;
  reason: string;
}

export interface FreshnessReport {
  stale: FreshnessItem[];
  orphaned: FreshnessItem[];
  unowned: FreshnessItem[];
  summary: {
    total: number;
    stale: number;
    orphaned: number;
    unowned: number;
    asOf: string;
  };
}

// Basenames that are structural entry points, not leaf content: an unreferenced
// index/overview page is expected and must never be reported as orphaned.
const INDEX_BASENAMES = new Set(["index", "README", "readme", "overview", "charter"]);

function isoDate(value: Date): string {
  return value.toISOString().slice(0, 10);
}

function basename(path: string): string {
  const last = path.split("/").pop() ?? path;
  return last.endsWith(".md") ? last.slice(0, -3) : last;
}

function stripKbPrefix(path: string): string {
  return path.startsWith("kb/") ? path.slice(3) : path;
}

// Normalize a citation target to a bare doc path: drop any `#fragment` and an
// optional leading `kb/` so `kb/a/b.md#x` and `a/b.md` compare equal.
function citationPath(citation: string): string {
  const hash = citation.indexOf("#");
  const raw = hash === -1 ? citation : citation.slice(0, hash);
  return stripKbPrefix(raw);
}

function addRef(map: Map<string, Set<string>>, key: string, referrer: string): void {
  let set = map.get(key);
  if (set === undefined) {
    set = new Set<string>();
    map.set(key, set);
  }
  set.add(referrer);
}

// True when some doc OTHER than `selfPath` references `key`.
function referencedByOther(map: Map<string, Set<string>>, key: string, selfPath: string): boolean {
  const set = map.get(key);
  if (set === undefined) return false;
  for (const referrer of set) {
    if (referrer !== selfPath) return true;
  }
  return false;
}

function toItem(doc: KbDoc, reason: string): FreshnessItem {
  return { id: doc.id, path: doc.path, owner: doc.frontmatter.owner, reason };
}

export function auditFreshness(
  docs: KbDoc[],
  opts: { today: Date; knownRoles?: Set<string> },
): FreshnessReport {
  const asOf = isoDate(opts.today);
  const knownRoles = opts.knownRoles;
  const useRoles = knownRoles !== undefined && knownRoles.size > 0;

  // referrer indexes: relation-target id -> referring doc paths, and citation
  // target path -> referring doc paths.
  const relationRefs = new Map<string, Set<string>>();
  const citationRefs = new Map<string, Set<string>>();

  for (const doc of docs) {
    const relations = doc.frontmatter.relations;
    if (relations !== undefined) {
      for (const value of Object.values(relations)) {
        if (value === undefined) continue;
        const entries = Array.isArray(value) ? value : [value];
        for (const entry of entries) {
          addRef(relationRefs, entry, doc.path);
        }
      }
    }
    for (const citation of findCitationsInText(doc.body)) {
      addRef(citationRefs, citationPath(citation), doc.path);
    }
  }

  const stale: FreshnessItem[] = [];
  const orphaned: FreshnessItem[] = [];
  const unowned: FreshnessItem[] = [];

  for (const doc of docs) {
    // stale — deprecated docs are expected to be stale; backlog is out of scope.
    if (!doc.isBacklog && doc.frontmatter.status !== "deprecated") {
      const reviewBy = doc.frontmatter.review_by;
      const reviewDate = new Date(`${reviewBy}T00:00:00Z`);
      if (!Number.isNaN(reviewDate.getTime()) && isoDate(reviewDate) < asOf) {
        stale.push(toItem(doc, `review_by ${reviewBy} passed`));
      }
    }

    // orphaned — all four conditions must hold.
    if (
      !doc.isBacklog &&
      !INDEX_BASENAMES.has(basename(doc.path)) &&
      !referencedByOther(relationRefs, doc.id, doc.path) &&
      !referencedByOther(citationRefs, doc.path, doc.path)
    ) {
      orphaned.push(toItem(doc, "not referenced by any document"));
    }

    // unowned — empty owner always; unknown role only when a catalog is given.
    if (!doc.isBacklog) {
      const owner = doc.frontmatter.owner;
      if (owner.trim().length === 0) {
        unowned.push(toItem(doc, "owner is empty"));
      } else if (useRoles && !knownRoles.has(owner)) {
        unowned.push(toItem(doc, `owner '${owner}' is not a known role`));
      }
    }
  }

  return {
    stale,
    orphaned,
    unowned,
    summary: {
      total: docs.length,
      stale: stale.length,
      orphaned: orphaned.length,
      unowned: unowned.length,
      asOf,
    },
  };
}

// One issue draft per stale doc, for the `--open-issues` dry path. The doc owner
// is named so the filed issue can be routed to them.
export function renderIssueDrafts(
  report: FreshnessReport,
): { title: string; body: string; labels: string[] }[] {
  return report.stale.map((item) => {
    const reviewDate = /review_by (\S+) passed/.exec(item.reason)?.[1] ?? "an earlier date";
    return {
      title: `Refresh KB doc: ${item.path}`,
      body:
        `\`${item.path}\` passed its review date (${reviewDate}). ` +
        `Owner: ${item.owner}. This issue is assigned to owner for review and refresh.`,
      labels: ["kb-freshness"],
    };
  });
}
