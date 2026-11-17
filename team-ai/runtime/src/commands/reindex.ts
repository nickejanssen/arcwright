// Deterministic. No model calls.
//
// Rebuilds the retrieval index for an instance directory. Creates `index.lock`
// with the default (lexical) configuration when it is missing, then runs the
// driver's full reindex and prints the resulting stats.

import { existsSync } from "node:fs";
import { join } from "node:path";

import { createAdapter } from "../retrieval/factory.js";
import { DEFAULT_INDEX_LOCK, writeIndexLock } from "../retrieval/index-lock.js";
import type { RetrievalAdapter } from "../retrieval/types.js";

export interface ReindexCommandOptions {
  root?: string;
}

function closeAdapter(adapter: RetrievalAdapter): void {
  const close = (adapter as { close?: () => void }).close;
  if (typeof close === "function") close.call(adapter);
}

export async function run(opts: ReindexCommandOptions): Promise<number> {
  const root = opts.root ?? ".";

  if (!existsSync(join(root, "index.lock"))) {
    writeIndexLock(root, DEFAULT_INDEX_LOCK);
    console.log("wrote index.lock");
  }

  const adapter = createAdapter(root);
  try {
    const stats = await adapter.reindex();
    console.log(
      `indexed ${stats.documents} document(s), ${stats.chunks} chunk(s) ` +
        `via ${stats.driver} in ${stats.tookMs}ms`,
    );
    return 0;
  } catch (err) {
    console.error(err instanceof Error ? err.message : String(err));
    return 1;
  } finally {
    closeAdapter(adapter);
  }
}
