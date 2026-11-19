// Fingerprint exactly the source inputs used to build a lexical index.
import { createHash } from "node:crypto";
import { readFileSync, readdirSync, realpathSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { isExcluded } from "../kb/loader.js";

// Bump for indexing semantics not represented by these runtime files.
const INDEX_ALGORITHM_REVISION = "lexical-index-v1";
const INDEX_CODE = [
  "./lexical.js",
  "./fingerprint.js",
  "./factory.js",
  "./index-lock.js",
  "../kb/chunk.js",
  "../kb/loader.js",
  "../kb/frontmatter.js",
  "../kb/headings.js",
  "../kb/slugify.js",
  "../schema/validate.js",
  "../schema/load.js",
];

export function runtimeInputs(): SourceEntry[] {
  const code = INDEX_CODE.map((name) => {
    let url = new URL(name, import.meta.url);
    try {
      return { path: name, raw: readFileSync(fileURLToPath(url), "utf8") };
    } catch (error) {
      // Vitest executes TypeScript directly; deployed runtime uses built JS.
      if (!(error instanceof Error && "code" in error && error.code === "ENOENT")) throw error;
      url = new URL(name.replace(/\.js$/, ".ts"), import.meta.url);
      return { path: name, raw: readFileSync(fileURLToPath(url), "utf8") };
    }
  });
  for (const name of ["../../schemas/frontmatter.schema.json", "../../package-lock.json"]) {
    code.push({
      path: name,
      raw: readFileSync(fileURLToPath(new URL(name, import.meta.url)), "utf8"),
    });
  }
  return code;
}
export type SourceEntry = { path: string; raw: string };

export function fingerprintSources(
  root: string,
  exclude: string[],
  lock: string,
  entries: SourceEntry[],
  runtime: SourceEntry[] = runtimeInputs(),
): string {
  const ordered = [...entries].sort((a, b) => a.path.localeCompare(b.path));
  return createHash("sha256")
    .update(
      JSON.stringify({
        revision: INDEX_ALGORITHM_REVISION,
        root: realpathSync(root),
        exclude,
        lock,
        runtime,
        entries: ordered,
      }),
    )
    .digest("hex");
}

export function fingerprintCurrent(root: string, exclude: string[], lock: string): string {
  const listed: string[] = readdirSync(root, { recursive: true, encoding: "utf8" });
  const files = listed
    .map((path) => path.split(/[\\/]/).join("/"))
    .filter((path) => path.endsWith(".md") && !isExcluded(path, exclude))
    .sort((a, b) => a.localeCompare(b));
  const entries = files.map((path) => ({ path, raw: readFileSync(join(root, path), "utf8") }));
  return fingerprintSources(root, exclude, lock, entries);
}
