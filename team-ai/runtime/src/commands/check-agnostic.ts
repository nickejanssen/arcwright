// Deterministic. No model calls. No network.
//
// `team-ai check-agnostic` guards the framework against a team's content leaking
// into shipped source. It scans a fixed set of paths under the repo root for any
// token listed in the framework-shipped `agnostic-denylist.txt` (proper nouns
// pulled from the companion design docs) and exits non-zero on a hit.
//
// Scanned: src/**/*.ts (excluding **/*.test.ts and **/fixtures/**), schemas/**/*.json,
// catalog/** , src/interview/questions.yaml, templates/** , bin/**/*.js.
// NOT scanned: docs/, node_modules/, dist/, evals/, tests, and fixtures — those
// legitimately carry example names.

import { existsSync, readdirSync, readFileSync, type Dirent } from "node:fs";
import { join, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";

export interface AgnosticHit {
  file: string;
  line: number;
  term: string;
}

export interface Denylist {
  denied: string[];
  allow: string[];
}

export interface CheckAgnosticOptions {
  fix?: never;
}

// The denylist ships with the framework, not with the tree being scanned, so it
// is resolved relative to this module (mirrors `schemaPath` in schema/load.ts).
function denylistPath(): string {
  return fileURLToPath(new URL("../../agnostic-denylist.txt", import.meta.url));
}

// One term per line. `#` lines are comments, blank lines are ignored, and a
// leading `!` marks an allowlist exception. Everything is lowercased so matching
// is case-insensitive.
export function parseDenylist(text: string): Denylist {
  const denied: string[] = [];
  const allow: string[] = [];
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (line.length === 0 || line.startsWith("#")) continue;
    if (line.startsWith("!")) {
      const term = line.slice(1).trim().toLowerCase();
      if (term.length > 0) allow.push(term);
      continue;
    }
    denied.push(line.toLowerCase());
  }
  // Strip longer allowlist phrases first so a phrase is removed before any
  // shorter allowlisted substring of it.
  allow.sort((a, b) => b.length - a.length);
  return { denied, allow };
}

function escapeRegex(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// Word/phrase boundary match on already-lowercased content. `\b` cannot express
// the boundary for a term containing a space (a two-word product name), so an
// explicit non-alphanumeric edge (or string boundary) is required on each side.
function deniedPattern(term: string): RegExp {
  return new RegExp(`(?:^|[^a-z0-9])${escapeRegex(term)}(?:[^a-z0-9]|$)`);
}

function toPosix(path: string): string {
  return path.split(sep).join("/");
}

function walk(absDir: string): string[] {
  const results: string[] = [];
  const stack: string[] = [absDir];
  while (stack.length > 0) {
    const current = stack.pop();
    if (current === undefined) break;
    let entries: Dirent[];
    try {
      entries = readdirSync(current, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries) {
      const full = join(current, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else if (entry.isFile()) results.push(full);
    }
  }
  return results;
}

// The concrete list of repo-relative (posix) files check-agnostic reads.
export function listAgnosticFiles(root: string): string[] {
  const files = new Set<string>();
  const add = (abs: string): void => {
    files.add(toPosix(relative(root, abs)));
  };

  for (const abs of walk(join(root, "src"))) {
    const rel = toPosix(relative(root, abs));
    if (!rel.endsWith(".ts")) continue;
    if (rel.endsWith(".test.ts")) continue;
    if (rel.split("/").includes("fixtures")) continue;
    files.add(rel);
  }

  for (const abs of walk(join(root, "schemas"))) {
    if (abs.endsWith(".json")) add(abs);
  }

  for (const abs of walk(join(root, "catalog"))) add(abs);

  const questions = join(root, "src", "interview", "questions.yaml");
  if (existsSync(questions)) add(questions);

  for (const abs of walk(join(root, "templates"))) add(abs);

  for (const abs of walk(join(root, "bin"))) {
    if (abs.endsWith(".js")) add(abs);
  }

  return [...files].sort((a, b) => a.localeCompare(b));
}

// Pure scanner: returns one hit per (line, denied term). The denylist is the
// framework's own; `root` is only the tree being scanned.
export function scanAgnostic(root: string): AgnosticHit[] {
  const { denied, allow } = parseDenylist(readFileSync(denylistPath(), "utf8"));
  const patterns = denied.map((term) => ({ term, regex: deniedPattern(term) }));

  const hits: AgnosticHit[] = [];
  for (const rel of listAgnosticFiles(root)) {
    let content: string;
    try {
      content = readFileSync(join(root, rel), "utf8");
    } catch {
      continue;
    }
    const lines = content.split(/\r?\n/);
    for (let i = 0; i < lines.length; i += 1) {
      let haystack = (lines[i] ?? "").toLowerCase();
      for (const term of allow) {
        haystack = haystack.split(term).join(" ");
      }
      for (const { term, regex } of patterns) {
        if (regex.test(haystack)) {
          hits.push({ file: rel, line: i + 1, term });
        }
      }
    }
  }
  return hits;
}

// Async signature to match the shared command contract; the scan itself is
// synchronous and does no IO beyond reading files.
export function run(opts: CheckAgnosticOptions): Promise<number> {
  void opts;
  const root = process.cwd();

  let files: string[];
  let hits: AgnosticHit[];
  try {
    files = listAgnosticFiles(root);
    hits = scanAgnostic(root);
  } catch (err) {
    console.error(`check-agnostic: ${err instanceof Error ? err.message : String(err)}`);
    return Promise.resolve(1);
  }

  if (hits.length > 0) {
    for (const hit of hits) {
      console.error(`${hit.file}:${hit.line}: contains denied token '${hit.term}'`);
    }
    return Promise.resolve(1);
  }

  console.log(`check-agnostic: OK (${files.length} files scanned, 0 denied tokens)`);
  return Promise.resolve(0);
}
