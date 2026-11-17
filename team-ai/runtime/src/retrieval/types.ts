export type DriverName =
  "lexical" | "vector-embedded" | "vector-pgvector" | "vector-hosted" | "graph" | "hybrid";

export interface SearchOpts {
  namespace?: string | string[];
  k?: number; // default 8, hard cap 20
  filters?: {
    status?: string[];
    sensitivity?: string[];
    tags?: string[];
    owner?: string;
  };
  mode?: "lexical" | "vector" | "graph" | "hybrid";
}

export interface Hit {
  doc_id: string;
  chunk_id: string;
  path: string; // repo-relative, citation target
  heading_path: string;
  score: number; // normalized 0..1 across all drivers
  text: string;
  metadata: Record<string, unknown>; // front matter
}

export interface Document {
  id: string;
  path: string;
  frontmatter: Record<string, unknown>;
  body: string;
}

export interface IndexStats {
  documents: number;
  chunks: number;
  driver: string;
  tookMs: number;
}

export interface RetrievalAdapter {
  search(query: string, opts?: SearchOpts): Promise<Hit[]>;
  get(idOrPath: string, section?: string): Promise<Document>;
  neighbors?(id: string, relation?: string, depth?: number): Promise<Hit[]>;
  reindex(paths?: string[]): Promise<IndexStats>;
}
