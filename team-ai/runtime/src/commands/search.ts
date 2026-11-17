// Deterministic. No model calls.
//
// Queries the retrieval index for an instance directory and prints ranked hits.
// A "no results above threshold" line (every hit scoring below 0.2, or none at
// all) is the deterministic refuse signal a downstream router keys on.

import { createAdapter } from "../retrieval/factory.js";
import type { Hit, RetrievalAdapter, SearchOpts } from "../retrieval/types.js";
import { slug } from "../kb/slugify.js";

const SCORE_THRESHOLD = 0.2;
const SNIPPET_CHARS = 80;

export interface SearchCommandOptions {
  root?: string;
  k?: number;
  namespace?: string[];
  json?: boolean;
}

function closeAdapter(adapter: RetrievalAdapter): void {
  const close = (adapter as { close?: () => void }).close;
  if (typeof close === "function") close.call(adapter);
}

function formatHit(hit: Hit): string {
  const anchor = hit.heading_path.trim().length > 0 ? `#${slug(hit.heading_path)}` : "";
  const snippet = hit.text.replace(/\s+/g, " ").trim().slice(0, SNIPPET_CHARS);
  return `${hit.score.toFixed(3)}  ${hit.path}${anchor}  —  ${snippet}`;
}

export async function run(query: string, opts: SearchCommandOptions): Promise<number> {
  const root = opts.root ?? ".";
  const k = opts.k ?? 8;
  const namespace = opts.namespace ?? [];

  const adapter = createAdapter(root);

  const searchOpts: SearchOpts = namespace.length > 0 ? { k, namespace } : { k };

  let hits: Hit[];
  try {
    hits = await adapter.search(query, searchOpts);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    if (message.includes("index not built")) {
      console.error("index not built — run 'team-ai reindex' first");
      return 1;
    }
    console.error(message);
    return 1;
  } finally {
    closeAdapter(adapter);
  }

  if (opts.json === true) {
    console.log(JSON.stringify(hits, null, 2));
    return 0;
  }

  const above = hits.filter((hit) => hit.score >= SCORE_THRESHOLD);
  if (above.length === 0) {
    console.log("no results above threshold");
    return 0;
  }

  for (const hit of above) console.log(formatHit(hit));
  return 0;
}
