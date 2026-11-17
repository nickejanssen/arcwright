// Concrete stub adapters for the retrieval drivers deferred past v1. Each one is
// a real `RetrievalAdapter` whose every method rejects with a `NotImplementedError`
// that names the driver and points at the phase-8 index checkpoint.

import { NotImplementedAdapter } from "./not-implemented.js";

export class VectorEmbeddedAdapter extends NotImplementedAdapter {
  protected readonly driver = "vector-embedded";
}

export class VectorPgvectorAdapter extends NotImplementedAdapter {
  protected readonly driver = "vector-pgvector";
}

export class VectorHostedAdapter extends NotImplementedAdapter {
  protected readonly driver = "vector-hosted";
}

export class GraphAdapter extends NotImplementedAdapter {
  protected readonly driver = "graph";
}

export class HybridAdapter extends NotImplementedAdapter {
  protected readonly driver = "hybrid";
}
