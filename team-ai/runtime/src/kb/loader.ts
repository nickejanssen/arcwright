import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";

import { validate } from "../schema/validate.js";
import { parseFrontmatter } from "./frontmatter.js";
import { extractHeadings } from "./headings.js";
import type { KbDoc } from "./types.js";

export class KbValidationError extends Error {
  constructor(public readonly failures: { file: string; error: string }[]) {
    super(
      `${failures.length} invalid document(s):\n` +
        failures.map((f) => `  ${f.file}: ${f.error}`).join("\n"),
    );
    this.name = "KbValidationError";
  }
}

function toPosix(relPath: string): string {
  return relPath.split(/[\\/]/).join("/");
}

function byPath(a: string, b: string): number {
  return a.localeCompare(b);
}

async function listMarkdown(root: string): Promise<string[]> {
  let entries: string[];
  try {
    entries = await readdir(root, { recursive: true });
  } catch (err) {
    if (err instanceof Error && "code" in err && err.code === "ENOENT") {
      throw new Error(`KB root not found: ${root}`);
    }
    throw err;
  }
  return entries
    .filter((entry) => entry.endsWith(".md"))
    .map(toPosix)
    .sort(byPath);
}

export interface LoadKbOptions {
  exclude?: string[];
}

export function isExcluded(relPath: string, exclude: string[]): boolean {
  return exclude.some((entry) => {
    if (entry.endsWith("/")) return relPath.startsWith(entry);
    if (entry.startsWith("**/")) {
      const tail = entry.slice(3);
      return relPath === tail || relPath.endsWith(`/${tail}`);
    }
    return relPath === entry;
  });
}

export async function loadKb(root: string, opts: LoadKbOptions = {}): Promise<KbDoc[]> {
  const markdown = (await listMarkdown(root)).filter((rel) => !isExcluded(rel, opts.exclude ?? []));

  const docs: KbDoc[] = [];
  const failures: { file: string; error: string }[] = [];

  for (const relPath of markdown) {
    const raw = await readFile(join(root, relPath), "utf8");
    let parsed: ReturnType<typeof parseFrontmatter>;
    try {
      parsed = parseFrontmatter(raw);
    } catch (err) {
      const reason =
        err instanceof Error ? (err.message.split("\n")[0] ?? err.message) : String(err);
      failures.push({ file: relPath, error: `front matter does not parse: ${reason}` });
      continue;
    }
    const { data, body } = parsed;
    const result = validate("frontmatter", data);
    if (!result.ok) {
      failures.push({ file: relPath, error: result.errors[0] ?? "invalid front matter" });
      continue;
    }
    docs.push({
      id: result.value.id,
      path: relPath,
      frontmatter: result.value,
      body,
      headings: extractHeadings(body),
      isBacklog: relPath.split("/").includes("_backlog"),
    });
  }

  if (failures.length > 0) throw new KbValidationError(failures);

  return docs.sort((a, b) => byPath(a.path, b.path));
}
