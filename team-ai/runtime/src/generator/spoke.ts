// Deterministic. No model calls. No network.
//
// `team-ai spoke` scaffolds a thin spoke repo: a `spoke.yaml`, an empty `kb/`
// and `skills/`, and a validate workflow that calls the framework's reusable
// spoke check. It asks five short questions, renders `templates/spoke`
// non-destructively, then runs `validateSpoke` on the result so the operator
// leaves with a repo that already passes the contract (0 core edits required).

import { existsSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { input } from "@inquirer/prompts";

import { validateSpoke } from "../spoke/validate.js";
import { renderTree } from "./render.js";

const TEMPLATES_SPOKE = fileURLToPath(new URL("../../templates/spoke", import.meta.url));

export interface SpokeOptions {
  dir?: string;
  force?: boolean;
  answers?: () => Promise<string>;
  output?: (s: string) => void;
}

function slug(text: string): string {
  return text
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export async function run(opts: SpokeOptions): Promise<number> {
  const output = opts.output ?? ((s: string): void => console.log(s));
  const error = (s: string): void => console.error(s);
  const dir = opts.dir ?? ".";

  if (existsSync(join(dir, "spoke.yaml")) && opts.force !== true) {
    error("spoke.yaml already exists (use --force to overwrite)");
    return 1;
  }

  const ask = (message: string): Promise<string> =>
    opts.answers ? opts.answers() : input({ message });

  const name = (await ask("Spoke name (kebab-case)")).trim();
  const kbNamespace = (await ask("kb_namespace (e.g. partners/<x>)")).trim();
  const owner = (await ask("Owner (person or role)")).trim();
  const coreRepo = (await ask("Core instance repo URL")).trim();
  const domainId = (await ask("Domain id (kebab-case)")).trim();
  const domainDescription = (await ask("Domain description (one line)")).trim();

  const domainSlug = slug(domainId) || "domain";
  const context = {
    name,
    namespace: kbNamespace,
    owner,
    core_repo: coreRepo,
    domain: {
      id: domainSlug,
      description: domainDescription || `Questions and support for the ${domainSlug} domain.`,
      subagent: `${domainSlug}-sme`,
    },
  };

  const rendered = await renderTree({
    templateDir: TEMPLATES_SPOKE,
    destDir: dir,
    context,
    onCollision: "skip",
  });
  for (const warning of rendered.warnings) error(warning);

  const v = await validateSpoke(dir);
  for (const message of v.errors) error(message);

  if (v.ok) {
    output(`OK — spoke '${name}' generated (0 core edits required)`);
    return 0;
  }
  error(`spoke '${name}' does not pass the contract yet (${v.coreEditsRequired} core edit(s))`);
  return 1;
}
