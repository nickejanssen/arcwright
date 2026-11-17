// Deterministic. No model calls. No network.
//
// `team-ai attach` drops a `.team-ai.yaml` in a repo that wants to consume an
// existing team-ai instance without owning one: it names the instance, the
// agents and skills to pull, and the knowledge-base namespaces to read. The file
// is the whole footprint — attach mode ships no kb/, no agents/, no scripts.

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { input } from "@inquirer/prompts";
import { parse as parseYaml } from "yaml";

import { renderTree } from "./render.js";

const TEMPLATES_ATTACH = fileURLToPath(new URL("../../templates/attach", import.meta.url));
const EXPECTED_KEYS = ["mode", "instance", "agents", "skills", "kb_namespaces"];

export interface AttachOptions {
  dir?: string;
  force?: boolean;
  answers?: () => Promise<string>;
  output?: (s: string) => void;
}

function list(raw: string): string[] {
  return raw
    .split(",")
    .map((part) => part.trim())
    .filter((part) => part.length > 0);
}

export async function run(opts: AttachOptions): Promise<number> {
  const output = opts.output ?? ((s: string): void => console.log(s));
  const error = (s: string): void => console.error(s);
  const dir = opts.dir ?? ".";

  if (existsSync(join(dir, ".team-ai.yaml")) && opts.force !== true) {
    error(".team-ai.yaml already exists (use --force to overwrite)");
    return 1;
  }

  const ask = (message: string): Promise<string> =>
    opts.answers ? opts.answers() : input({ message });

  const instance = (await ask("Instance repo URL")).trim();
  const agents = list(await ask("Agents to pull (comma-separated)"));
  const skills = list(await ask("Skills to pull (comma-separated)"));
  const kbNamespaces = list(await ask("kb namespaces to read (comma-separated)"));

  const rendered = await renderTree({
    templateDir: TEMPLATES_ATTACH,
    destDir: dir,
    context: { instance, agents, skills, kb_namespaces: kbNamespaces },
    onCollision: "skip",
  });
  for (const warning of rendered.warnings) error(warning);

  const written = join(dir, ".team-ai.yaml");
  let parsed: unknown;
  try {
    parsed = parseYaml(readFileSync(written, "utf8"));
  } catch (err) {
    error(`.team-ai.yaml did not parse: ${err instanceof Error ? err.message : String(err)}`);
    return 1;
  }

  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    error(".team-ai.yaml is not a mapping");
    return 1;
  }
  const record: Record<string, unknown> = parsed as Record<string, unknown>;
  const keys = Object.keys(record);
  const missing = EXPECTED_KEYS.filter((k) => !keys.includes(k));
  const extra = keys.filter((k) => !EXPECTED_KEYS.includes(k));
  if (missing.length > 0 || extra.length > 0) {
    error(
      `.team-ai.yaml key mismatch (missing: ${missing.join(", ") || "none"}; ` +
        `unexpected: ${extra.join(", ") || "none"})`,
    );
    return 1;
  }
  if (record.mode !== "attach") {
    error(`.team-ai.yaml mode must be 'attach', got '${String(record.mode)}'`);
    return 1;
  }

  output("OK — .team-ai.yaml written (attach mode)");
  return 0;
}
