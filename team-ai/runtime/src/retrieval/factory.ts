// Driver factory: reads the driver name recorded in `index.lock` and returns the
// matching `RetrievalAdapter`. The lexical driver is fully implemented; the other
// five resolve to honest stubs that fail loudly. An unrecognized name is a hard
// error that lists the valid drivers.

import { join } from "node:path";

import { readIndexLock, resolveKbScope } from "./index-lock.js";
import { LexicalAdapter } from "./lexical.js";
import type { LexicalAdapterOpts } from "./lexical.js";
import {
  GraphAdapter,
  HybridAdapter,
  VectorEmbeddedAdapter,
  VectorHostedAdapter,
  VectorPgvectorAdapter,
} from "./stubs.js";
import type { DriverName, RetrievalAdapter } from "./types.js";

export const VALID_DRIVERS: readonly DriverName[] = [
  "lexical",
  "vector-embedded",
  "vector-pgvector",
  "vector-hosted",
  "graph",
  "hybrid",
];

export function createAdapter(
  dir: string,
  opts?: { kbRoot?: string; dbPath?: string },
): RetrievalAdapter {
  const driver = readIndexLock(dir).driver;

  switch (driver) {
    case "lexical": {
      const scope =
        opts?.kbRoot === undefined ? resolveKbScope(dir) : { root: opts.kbRoot, exclude: [] };
      const lexicalOpts: LexicalAdapterOpts = {
        kbRoot: scope.root,
        exclude: scope.exclude,
        // The index belongs to the instance directory, not the process cwd, so
        // that concurrent instances never share one SQLite file.
        dbPath: opts?.dbPath ?? join(dir, ".team-ai", "index.sqlite"),
      };
      return new LexicalAdapter(lexicalOpts);
    }
    case "vector-embedded":
      return new VectorEmbeddedAdapter();
    case "vector-pgvector":
      return new VectorPgvectorAdapter();
    case "vector-hosted":
      return new VectorHostedAdapter();
    case "graph":
      return new GraphAdapter();
    case "hybrid":
      return new HybridAdapter();
    default:
      throw new Error(
        `unknown retrieval driver '${driver}' in index.lock — valid: ` +
          `lexical, vector-embedded, vector-pgvector, vector-hosted, graph, hybrid`,
      );
  }
}
