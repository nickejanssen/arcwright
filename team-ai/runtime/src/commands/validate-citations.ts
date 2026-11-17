import { readdir, readFile, stat } from "node:fs/promises";
import { join, relative } from "node:path";

import { findCitationsInText, resolveCitation } from "../kb/citations.js";
import { isExcluded, KbValidationError, loadKb } from "../kb/loader.js";
import type { KbDoc } from "../kb/types.js";
import { resolveKbScope } from "../retrieval/index-lock.js";

export interface ValidateCitationsOptions {
  root?: string;
}

interface Unresolved {
  file: string;
  citation: string;
  reason: string;
}

async function isDir(path: string): Promise<boolean> {
  try {
    return (await stat(path)).isDirectory();
  } catch {
    return false;
  }
}

async function listMarkdown(dir: string, exclude: string[] = []): Promise<string[]> {
  const entries = await readdir(dir, { recursive: true });
  return entries
    .filter((entry) => entry.endsWith(".md"))
    .map((entry) => entry.split(/[\\/]/).join("/"))
    .filter((entry) => !isExcluded(entry, exclude))
    .sort((a, b) => a.localeCompare(b));
}

export async function run(opts: ValidateCitationsOptions): Promise<number> {
  const root = opts.root ?? ".";
  let kbScope: ReturnType<typeof resolveKbScope>;
  try {
    kbScope = resolveKbScope(root);
  } catch (err) {
    console.error(err instanceof Error ? err.message : String(err));
    return 1;
  }
  const kbDir = kbScope.root;
  const kbLabel = relative(root, kbDir).split(/[\\/]/).join("/") || ".";
  const agentsDir = join(root, "agents");

  const hasKb = await isDir(kbDir);
  const hasAgents = await isDir(agentsDir);

  if (!hasKb && !hasAgents) {
    console.error(`no ${kbLabel}/ or agents/ under ${root}`);
    return 1;
  }

  let kbDocs: KbDoc[] = [];
  if (hasKb) {
    try {
      kbDocs = await loadKb(kbDir, { exclude: kbScope.exclude });
    } catch (err) {
      if (err instanceof KbValidationError) {
        console.error(
          `citations cannot be checked until KB front matter is valid ` +
            `(${err.failures.length} invalid document(s))`,
        );
        for (const failure of err.failures) {
          console.error(`  ${failure.file}: ${failure.error}`);
        }
        return 1;
      }
      console.error(err instanceof Error ? err.message : String(err));
      return 1;
    }
  }

  const scopes: { dir: string; prefix: string }[] = [];
  if (hasKb) scopes.push({ dir: kbDir, prefix: kbLabel });
  if (hasAgents) scopes.push({ dir: agentsDir, prefix: "agents" });

  const unresolved: Unresolved[] = [];
  let citationCount = 0;
  let fileCount = 0;

  for (const scanScope of scopes) {
    const exclude = scanScope.dir === kbDir ? kbScope.exclude : [];
    for (const relPath of await listMarkdown(scanScope.dir, exclude)) {
      fileCount += 1;
      const label = `${scanScope.prefix}/${relPath}`;
      const text = await readFile(join(scanScope.dir, relPath), "utf8");
      for (const citation of findCitationsInText(text)) {
        citationCount += 1;
        const result = resolveCitation(kbDocs, citation);
        if (!result.ok) {
          unresolved.push({ file: label, citation, reason: result.reason });
        }
      }
    }
  }

  if (unresolved.length > 0) {
    for (const item of unresolved) {
      console.error(`${item.file}: ${item.citation} — ${item.reason}`);
    }
    return 1;
  }

  console.log(`OK ${citationCount} citation(s) across ${fileCount} file(s)`);
  return 0;
}
