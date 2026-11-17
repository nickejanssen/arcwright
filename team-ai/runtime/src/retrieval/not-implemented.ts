// Honest stubs for the retrieval drivers that do not ship in v1.
//
// Only the lexical driver is implemented. The other five (vector-embedded,
// vector-pgvector, vector-hosted, graph, hybrid) exist as real classes that
// satisfy `RetrievalAdapter` so the interface stays honest, but every method
// fails loudly instead of pretending to work.

import type { Document, Hit, IndexStats, RetrievalAdapter, SearchOpts } from "./types.js";

export class NotImplementedError extends Error {
  constructor(driver: string, method: string) {
    super(
      `${driver} retrieval driver is not implemented (${method}). Only 'lexical' ships in v1; ` +
        `evaluate vector/graph at the phase-8 index checkpoint — see docs/architecture.md §19.`,
    );
    this.name = "NotImplementedError";
  }
}

export abstract class NotImplementedAdapter implements RetrievalAdapter {
  protected abstract readonly driver: string;

  search(query: string, opts?: SearchOpts): Promise<Hit[]> {
    void query;
    void opts;
    return Promise.reject(new NotImplementedError(this.driver, "search"));
  }

  get(idOrPath: string, section?: string): Promise<Document> {
    void idOrPath;
    void section;
    return Promise.reject(new NotImplementedError(this.driver, "get"));
  }

  neighbors(id: string, relation?: string, depth?: number): Promise<Hit[]> {
    void id;
    void relation;
    void depth;
    return Promise.reject(new NotImplementedError(this.driver, "neighbors"));
  }

  reindex(paths?: string[]): Promise<IndexStats> {
    void paths;
    return Promise.reject(new NotImplementedError(this.driver, "reindex"));
  }
}
