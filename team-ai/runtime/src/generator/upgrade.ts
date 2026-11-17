// Deterministic. No model calls. No network.
//
// `team-ai upgrade` refreshes only the framework "plumbing" in an instance —
// the CI workflows, the eval gate thresholds, `SETUP.md`, and the `chunk`
// section of `index.lock` — to the versions this framework build ships. It never
// touches the knowledge base, the agents, the personas, the skills, the docs, or
// the manifest: those are the team's content. A plumbing file the operator has
// hand-edited is reported and left in place, with the fresh version dropped
// beside it as `<path>.team-ai-new`.

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import { parse as parseYaml, stringify as stringifyYaml } from "yaml";

import { loadBank } from "../interview/bank.js";
import { Engine } from "../interview/engine.js";
import {
  DEFAULT_INDEX_LOCK,
  lockChanged,
  readIndexLock,
  writeIndexLock,
} from "../retrieval/index-lock.js";
import { packageVersion } from "../version.js";
import { buildContext } from "./context.js";
import { TEMPLATES_INSTANCE } from "./entity-files.js";
import { mergeGeneratedManifest, readGeneratedManifest } from "./generated-manifest.js";
import { renderTree } from "./render.js";
import { stateFromProfile, type ProfileShape } from "./state-from-profile.js";

export interface UpgradeOptions {
  dir?: string;
  catalog?: string;
  output?: (s: string) => void;
}

// Everything under `templates/instance` EXCEPT the plumbing paths. `renderTree`
// matches these against the template-relative path with the `.hbs` still
// attached; a trailing `/` matches a subtree, otherwise the match is exact.
const NON_PLUMBING_EXCLUDE = [
  "kb/",
  "agents/",
  "personas/",
  "skills/",
  "catalog/",
  "docs/",
  "evals/golden/",
  "mcp-server/",
  "manifest.yaml.hbs",
  ".mcp.json.hbs",
  "README.md.hbs",
  ".gitignore.hbs",
  "index.lock.hbs",
];

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readProfile(dir: string): { raw: Record<string, unknown>; shape: ProfileShape } | null {
  const file = join(dir, "team-profile.yaml");
  if (!existsSync(file)) return null;
  let parsed: unknown;
  try {
    parsed = parseYaml(readFileSync(file, "utf8"));
  } catch {
    return null;
  }
  if (!isRecord(parsed)) return null;
  const answers = isRecord(parsed.answers) ? parsed.answers : {};
  const deferred = Array.isArray(parsed.deferred)
    ? (parsed.deferred as ProfileShape["deferred"])
    : [];
  return { raw: parsed, shape: { answers, deferred } };
}

export async function run(opts: UpgradeOptions): Promise<number> {
  const output = opts.output ?? ((s: string): void => console.log(s));
  const dir = opts.dir ?? ".";

  const profile = readProfile(dir);
  if (!profile) {
    output("upgrade: no team-profile.yaml found; run 'team-ai init' first");
    return 1;
  }

  const bank = loadBank();
  const engine = Engine.load(bank, stateFromProfile(bank, profile.shape));
  const context = buildContext(
    engine,
    opts.catalog !== undefined ? { instanceCatalogDir: opts.catalog } : {},
  );

  const priorManifest = readGeneratedManifest(dir);
  const result = await renderTree({
    templateDir: TEMPLATES_INSTANCE,
    destDir: dir,
    context,
    priorManifest,
    onCollision: "siblings",
    exclude: NON_PLUMBING_EXCLUDE,
  });
  mergeGeneratedManifest(dir, result.manifestEntries);

  // Refresh only `chunk` in index.lock; the driver and embedding are the team's
  // retrieval choices and are left untouched.
  const currentLock = readIndexLock(dir);
  const nextLock = {
    driver: currentLock.driver,
    chunk: {
      split_on: [...DEFAULT_INDEX_LOCK.chunk.split_on],
      target_tokens: DEFAULT_INDEX_LOCK.chunk.target_tokens,
      hard_cap: DEFAULT_INDEX_LOCK.chunk.hard_cap,
    },
    embedding: currentLock.embedding,
    ...(currentLock.kb
      ? { kb: { root: currentLock.kb.root, exclude: [...currentLock.kb.exclude] } }
      : {}),
  };
  const lockUpdated = lockChanged(currentLock, nextLock);
  if (lockUpdated) writeIndexLock(dir, nextLock);

  // Bump the recorded framework version.
  const nextProfile: Record<string, unknown> = { ...profile.raw };
  const priorVersion = nextProfile.team_ai_version;
  nextProfile.team_ai_version = packageVersion();
  writeFileSync(join(dir, "team-profile.yaml"), stringifyYaml(nextProfile), "utf8");

  output("");
  output(
    `upgrade: ${result.created.length} created, ${result.updated.length} updated, ` +
      `${result.collisions.length} skipped, index.lock ${lockUpdated ? "refreshed" : "unchanged"}.`,
  );
  for (const collision of result.collisions) {
    output(`  skipped — locally modified; see ${collision}.team-ai-new`);
  }
  if (priorVersion !== nextProfile.team_ai_version) {
    output(`  team_ai_version ${String(priorVersion)} -> ${String(nextProfile.team_ai_version)}`);
  }
  return 0;
}
