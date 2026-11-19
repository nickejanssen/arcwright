// AW-330 (moved from AW-329): once the pages are replaced, nothing under
// dashboard/src/ outside screens/tmst/ imports the old Tell Me Something True
// screens. They stay on disk, unused (spec 0095 Part K).

import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";
import test from "node:test";

const srcDir = join(process.env.DASHBOARD_DIR ?? process.cwd(), "src");

function sourceFiles(dir: string): string[] {
  const found: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) found.push(...sourceFiles(path));
    else if (/\.tsx?$/.test(entry.name)) found.push(path);
  }
  return found;
}

test("nothing under dashboard/src outside screens/tmst imports screens/tmst", () => {
  const offenders: string[] = [];
  for (const file of sourceFiles(srcDir)) {
    const rel = relative(srcDir, file).replace(/\\/g, "/");
    if (rel.startsWith("screens/tmst/")) continue;
    // "from 'x'", a bare "import 'x'" and a dynamic "import('x')".
    if (
      /(?:from\s+|import\s*\(?\s*)["'][^"']*\btmst\//.test(
        readFileSync(file, "utf8"),
      )
    ) {
      offenders.push(rel);
    }
  }
  assert.deepEqual(offenders, []);
});
