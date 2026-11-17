// Lexical retrieval driver: SQLite FTS5 over the chunked KB.
//
// This is the only real retrieval driver in team-ai. It builds a full-text
// index of the chunked knowledge base with better-sqlite3's bundled FTS5 and
// serves BM25-ranked hits with scores normalized to 0..1.

import { existsSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";

import Database from "better-sqlite3";

import type { Chunk } from "../kb/chunk.js";
import { chunkDoc } from "../kb/chunk.js";
import { loadKb } from "../kb/loader.js";
import { slug } from "../kb/slugify.js";
import type { Document, Hit, IndexStats, RetrievalAdapter, SearchOpts } from "./types.js";

const DEFAULT_DB_PATH = ".team-ai/index.sqlite";
const DEFAULT_K = 8;
const MAX_K = 20;
// SQL over-fetch multiplier so post-filtering has candidates to work with.
const CANDIDATE_MULTIPLIER = 4;
const CANDIDATE_CAP = 80;

// Shape of a row from the FTS5 `chunks` table. bm25() is aliased to `bm25`.
interface ChunkRow {
  text: string;
  doc_id: string;
  chunk_id: string;
  path: string;
  heading_path: string;
  metadata: string;
  bm25: number;
}

// Parsed front matter as stored per chunk. Only the fields used by filters are
// named; everything else is passed through untyped.
interface ChunkMeta extends Record<string, unknown> {
  namespace?: unknown;
  status?: unknown;
  sensitivity?: unknown;
  owner?: unknown;
  tags?: unknown;
}

export interface LexicalAdapterOpts {
  kbRoot: string;
  dbPath?: string;
  exclude?: string[];
}

export class LexicalAdapter implements RetrievalAdapter {
  private readonly kbRoot: string;
  private readonly dbPath: string;
  private readonly exclude: string[];
  private handle: Database.Database | null = null;

  constructor(opts: LexicalAdapterOpts) {
    this.kbRoot = opts.kbRoot;
    this.dbPath = opts.dbPath ?? DEFAULT_DB_PATH;
    this.exclude = opts.exclude ?? [];
  }

  private db(): Database.Database {
    if (this.handle === null) {
      mkdirSync(dirname(this.dbPath), { recursive: true });
      this.handle = new Database(this.dbPath);
      this.handle.pragma("journal_mode = WAL");
    }
    return this.handle;
  }

  close(): void {
    if (this.handle !== null) {
      this.handle.close();
      this.handle = null;
    }
  }

  // `paths` is accepted for API stability but ignored: every call is a full
  // drop/recreate reindex. Incremental reindex is future work.
  async reindex(paths?: string[]): Promise<IndexStats> {
    void paths;
    const start = performance.now();
    const db = this.db();

    const docs = await loadKb(this.kbRoot, { exclude: this.exclude });
    const chunks = docs.flatMap((doc) => chunkDoc(doc));

    // DROP + CREATE + all inserts run in ONE transaction (SQLite DDL is
    // transactional): a mid-reindex failure rolls back to the prior index
    // rather than leaving an empty-but-queryable table. Insert order is stable
    // (chunkDoc is deterministic), so repeat reindexes yield an identical table
    // and byte-identical search output.
    const rebuild = db.transaction((rows: Chunk[]) => {
      db.exec("DROP TABLE IF EXISTS chunks");
      db.exec(
        "CREATE VIRTUAL TABLE chunks USING fts5(" +
          "text, " +
          "doc_id UNINDEXED, " +
          "chunk_id UNINDEXED, " +
          "path UNINDEXED, " +
          "heading_path UNINDEXED, " +
          "metadata UNINDEXED)",
      );
      const insert = db.prepare(
        "INSERT INTO chunks (text, doc_id, chunk_id, path, heading_path, metadata) " +
          "VALUES (?, ?, ?, ?, ?, ?)",
      );
      for (const c of rows) {
        insert.run(
          c.text,
          c.doc_id,
          c.chunk_id,
          c.path,
          c.heading_path,
          JSON.stringify(c.metadata),
        );
      }
    });
    rebuild(chunks);

    return {
      documents: docs.length,
      chunks: chunks.length,
      driver: "lexical",
      tookMs: Math.round(performance.now() - start),
    };
  }

  // Not `async`: all work is synchronous (better-sqlite3 is sync). The Promise
  // return type keeps the RetrievalAdapter contract uniform across drivers.
  search(query: string, opts: SearchOpts = {}): Promise<Hit[]> {
    try {
      return Promise.resolve(this.searchSync(query, opts));
    } catch (err) {
      return Promise.reject(err instanceof Error ? err : new Error(String(err)));
    }
  }

  private searchSync(query: string, opts: SearchOpts): Hit[] {
    const match = sanitizeQuery(query);
    if (match === null) return [];
    const termCount = match.split(" OR ").length;

    // Fail clearly (and without creating a stray empty db file) when search runs
    // before the first reindex.
    if (this.handle === null && !existsSync(this.dbPath)) {
      throw new Error("index not built — run reindex() first");
    }

    const k = clampK(opts.k);
    const limit = Math.min(k * CANDIDATE_MULTIPLIER, CANDIDATE_CAP);
    const db = this.db();

    let rows: ChunkRow[];
    try {
      rows = db
        .prepare(
          "SELECT text, doc_id, chunk_id, path, heading_path, metadata, bm25(chunks) AS bm25 " +
            "FROM chunks WHERE chunks MATCH ? ORDER BY bm25 LIMIT ?",
        )
        .all(match, limit) as ChunkRow[];
    } catch (err) {
      if (err instanceof Error && /no such table/.test(err.message)) {
        throw new Error("index not built — run reindex() first");
      }
      throw err;
    }

    // Post-filter on parsed metadata, then take the top k. Filtering happens
    // after the SQL LIMIT (k*4, capped 80) so filters never widen the search.
    const filtered = rows
      .map((row) => ({ row, meta: parseMeta(row.metadata) }))
      .filter(({ meta }) => passesFilters(meta, opts));

    return filtered.slice(0, k).map(({ row, meta }) => ({
      doc_id: row.doc_id,
      chunk_id: row.chunk_id,
      path: row.path,
      heading_path: row.heading_path,
      score: scoreFromBm25(row.bm25, termCount),
      text: row.text,
      metadata: meta,
    }));
  }

  async get(idOrPath: string, section?: string): Promise<Document> {
    const wantPath = idOrPath.replace(/^kb\//, "");
    const docs = await loadKb(this.kbRoot, { exclude: this.exclude });
    const doc = docs.find((d) => d.id === idOrPath || d.path === wantPath);
    if (doc === undefined) throw new Error(`no document: ${idOrPath}`);

    let body = doc.body;
    if (section !== undefined) {
      const sliced = sliceSection(body, section);
      if (sliced === null) throw new Error(`no section '${section}' in ${doc.path}`);
      body = sliced;
    }

    return {
      id: doc.id,
      path: doc.path,
      frontmatter: doc.frontmatter as unknown as Record<string, unknown>,
      body,
    };
  }
}

// --- helpers -------------------------------------------------------------------

function clampK(k: number | undefined): number {
  if (k === undefined) return DEFAULT_K;
  if (!Number.isFinite(k)) return DEFAULT_K;
  return Math.min(MAX_K, Math.max(1, Math.floor(k)));
}

// A query made only of function words carries no retrieval intent and must
// retrieve nothing. The list below is used as a GATE for that purpose. It is
// deliberately NOT used to filter terms out of the match expression.
//
// Measured 2026-09-20 on a 37-question golden set over a ~966,000-token corpus:
// filtering stopwords out
// of the match cost 6.1 points of hit rate (48.5% -> 42.4%) and 8.1 points of
// routing accuracy (24.3% -> 16.2%). BM25 already discounts common terms by
// inverse document frequency, so removing them discards disambiguating context
// and buys nothing. Gating on them preserves the "no content words retrieves
// nothing" property at zero cost.
const STOPWORDS = new Set([
  "a",
  "about",
  "an",
  "and",
  "any",
  "are",
  "as",
  "at",
  "be",
  "been",
  "but",
  "by",
  "can",
  "could",
  "did",
  "do",
  "does",
  "for",
  "from",
  "get",
  "had",
  "has",
  "have",
  "how",
  "i",
  "if",
  "in",
  "into",
  "is",
  "it",
  "its",
  "just",
  "may",
  "might",
  "much",
  "must",
  "my",
  "no",
  "not",
  "of",
  "on",
  "or",
  "our",
  "out",
  "over",
  "should",
  "so",
  "some",
  "such",
  "than",
  "that",
  "the",
  "their",
  "them",
  "then",
  "there",
  "these",
  "they",
  "this",
  "those",
  "to",
  "up",
  "was",
  "we",
  "were",
  "what",
  "when",
  "where",
  "which",
  "while",
  "who",
  "why",
  "will",
  "with",
  "would",
  "you",
  "your",
]);

// Turn arbitrary user text into a safe FTS5 MATCH string. FTS5 treats bare
// punctuation and quotes as syntax and throws on malformed input, so we reduce
// the query to alphanumeric/hyphen tokens, quote each one, and OR them
// together. Returns null when the query contains no content word at all.
export function sanitizeQuery(query: string): string | null {
  const tokens = query
    .split(/\s+/)
    .map((t) => t.replace(/[^\w-]/g, ""))
    .filter((t) => /\w/.test(t));
  const hasContentWord = tokens.some((t) => !STOPWORDS.has(t.toLowerCase()));
  if (!hasContentWord) return null;
  return tokens.map((t) => `"${t}"`).join(" OR ");
}

function parseMeta(json: string): ChunkMeta {
  const parsed: unknown = JSON.parse(json);
  if (typeof parsed === "object" && parsed !== null) return parsed as ChunkMeta;
  return {};
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((v): v is string => typeof v === "string") : [];
}

function inSet(value: unknown, set: string[]): boolean {
  return typeof value === "string" && set.includes(value);
}

function passesFilters(meta: ChunkMeta, opts: SearchOpts): boolean {
  if (opts.namespace !== undefined) {
    const ns = Array.isArray(opts.namespace) ? opts.namespace : [opts.namespace];
    if (!inSet(meta.namespace, ns)) return false;
  }
  const f = opts.filters;
  if (f !== undefined) {
    if (f.status !== undefined && !inSet(meta.status, f.status)) return false;
    if (f.sensitivity !== undefined && !inSet(meta.sensitivity, f.sensitivity)) return false;
    if (f.owner !== undefined && meta.owner !== f.owner) return false;
    if (f.tags !== undefined) {
      const tags = asStringArray(meta.tags);
      if (!f.tags.some((t) => tags.includes(t))) return false;
    }
  }
  return true;
}

// Score normalization (documented formula):
//   FTS5 bm25() is negative for a match and more negative = more relevant; a
//   non-match or a value >= 0 scores 0.
//   Let rel = -bm25 (positive; larger = better), and n = the number of terms in
//   the sanitized query. BM25 sums a contribution per matched term, so rel grows
//   with query length; dividing by n makes the score describe per-term relevance
//   and therefore comparable across queries of different lengths. Without this,
//   a long question of ordinary words outscores a short precise one and the
//   "cite or refuse" threshold becomes unreachable.
//     score = (rel / n) / ((rel / n) + BM25_K)
const BM25_K = 1.5;

export function scoreFromBm25(bm25: number, termCount: number): number {
  const rel = -bm25;
  if (rel <= 0) return 0;
  const perTerm = rel / Math.max(1, termCount);
  return Math.min(1, Math.max(0, perTerm / (perTerm + BM25_K)));
}

// Slice `body` to a single `## `/`### ` section: from the matching heading line
// through the line before the next heading of the same-or-higher level. The
// section argument is matched slug-insensitively against heading text.
function sliceSection(body: string, section: string): string | null {
  const target = slug(section);
  const lines = body.split("\n");
  const fence = /^(```|~~~)/;
  const atx = /^(#{2,3})\s+(.+?)\s*$/;

  let inFence = false;
  let startIdx = -1;
  let startLevel = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = (lines[i] ?? "").replace(/\r$/, "");
    if (fence.test(line)) {
      inFence = !inFence;
      continue;
    }
    if (inFence) continue;

    const m = atx.exec(line);
    if (m === null) continue;
    const hashes = m[1];
    const text = m[2];
    if (hashes === undefined || text === undefined) continue;
    const level = hashes.length;

    if (startIdx === -1) {
      if (slug(text) === target) {
        startIdx = i;
        startLevel = level;
      }
    } else if (level <= startLevel) {
      return lines.slice(startIdx, i).join("\n").replace(/\s+$/, "");
    }
  }

  if (startIdx === -1) return null;
  return lines.slice(startIdx).join("\n").replace(/\s+$/, "");
}
