// Diagnostic only: use the fixture's expected namespace as an oracle. This
// measures retrieval within a correct specialist scope, not routing accuracy.
import { readdir, readFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { parse } from "yaml";
import { visibleHits } from "../commands/search.js";
import { createAdapter } from "../retrieval/factory.js";
import type { Hit } from "../retrieval/types.js";
import type { GoldenQuestion } from "../schema/types.js";

const root = resolve(process.argv[2] ?? "team-ai");
const goldenDir = join(root, "evals", "golden");
const files = (await readdir(goldenDir)).filter((f) => /\.ya?ml$/.test(f)).sort();
const questions = (
  await Promise.all(
    files.map(
      async (file) => parse(await readFile(join(goldenDir, file), "utf8")) as GoldenQuestion[],
    ),
  )
)
  .flat()
  .filter((q) => q.expect_route !== "__refuse__");
const adapter = createAdapter(root);
const matches = (question: GoldenQuestion, hits: Hit[]): boolean =>
  hits.some((hit) =>
    question.expect_paths.some(
      (path) => hit.path === path || hit.path === path.replace(/^kb\//, ""),
    ),
  );

try {
  await adapter.reindex();
  let direct = 0;
  let wrapper = 0;
  const misses: string[] = [];
  for (const question of questions) {
    const options = { namespace: question.expect_namespace };
    const directHits = visibleHits(await adapter.search(question.question, { ...options, k: 8 }));
    // scripts/team_ai_cli.py widens scoped 8-result requests to 16, then
    // filters low scores in CLI text mode, then returns the first eight lines.
    const wrapperHits = visibleHits(
      await adapter.search(question.question, { ...options, k: 16 }),
    ).slice(0, 8);
    if (matches(question, directHits)) direct++;
    if (matches(question, wrapperHits)) wrapper++;
    else misses.push(question.id);
  }
  console.log(JSON.stringify({ total: questions.length, direct, wrapper, misses }, null, 2));
} finally {
  (adapter as { close?: () => void }).close?.();
}
