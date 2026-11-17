// Deterministic. No model calls. No network.
//
// buildContext turns a completed interview into the flat, nested-friendly data
// object every instance template renders against. It reads only
// `engine.effectiveAnswers()` and the resolved catalog; it never writes.

import type { RoleArchetype } from "../catalog/types.js";
import type { Engine } from "../interview/engine.js";
import { CORE_SKILLS, loadCatalog, parseDomains, slug } from "../interview/gates.js";

const DEFAULT_NAMESPACES = ["operating", "platform", "patterns", "playbooks", "decisions"];
const REVIEW_WINDOW_DAYS = 180;

interface TeamBlock {
  name: string;
  mission: string;
  slug: string;
  size: string;
}

interface DomainBlock {
  slug: string;
  name: string;
  namespace: string;
}

function asString(value: unknown, fallback = ""): string {
  return typeof value === "string" && value.length > 0 ? value : fallback;
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((v): v is string => typeof v === "string") : [];
}

function addDays(from: Date, days: number): string {
  const d = new Date(from.getTime());
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

export interface BuildContextExtra {
  today?: Date;
  [key: string]: unknown;
}

export function buildContext(
  engine: Engine,
  extra: BuildContextExtra = {},
): Record<string, unknown> {
  const eff = engine.effectiveAnswers();
  const catalogDir =
    typeof extra.instanceCatalogDir === "string" ? extra.instanceCatalogDir : undefined;
  const catalog = loadCatalog(catalogDir);
  const { today, ...rest } = extra;

  const name = asString(eff["team.name"]);
  const team: TeamBlock = {
    name,
    mission: asString(eff["team.mission"]),
    // A single token: seed-doc ids are `<slug>.<namespace>.<name>` and the id
    // pattern forbids `-` and `_` in the first segment, so a multi-word team
    // name must collapse to one run of `[a-z0-9]`.
    slug: slug(name).replace(/-/g, ""),
    size: asString(eff["team.size"], "4-8"),
  };

  const presetName = asString(eff["kb.namespaces"], "generic");
  const preset = catalog?.namespaces.get(presetName);
  const namespaces = preset ? [...preset.value.second_level] : [...DEFAULT_NAMESPACES];

  const rawDriver = asString(eff["arch.index_driver"], "lexical");
  const driver = rawDriver === "decide-later" ? "lexical" : rawDriver;

  const rolesSuppressed = team.size === "1-3";
  const roles: RoleArchetype[] = rolesSuppressed
    ? []
    : asStringArray(eff["agents.roles"])
        .map((r) => catalog?.roles.get(r)?.value)
        .filter((r): r is RoleArchetype => r !== undefined);

  const domains: DomainBlock[] = parseDomains(eff["agents.domains"]).map((d) => {
    const s = slug(d);
    return {
      slug: s,
      name: d,
      namespace: namespaces.includes(s) ? s : (namespaces[0] ?? "operating"),
    };
  });

  const personaList = asStringArray(eff["agents.personas"]).filter((p) => p !== "custom");
  const personas = personaList.length > 0 ? personaList : ["internal-technical"];

  const skills = [...new Set<string>([...CORE_SKILLS, ...asStringArray(eff["agents.skills"])])];

  return {
    team,
    org_path: asString(eff["ctx.org_path"], "your-org"),
    namespaces,
    driver,
    hosting: asString(eff["arch.hosting"], "no-server"),
    server: asString(eff["arch.hosting"], "no-server") !== "no-server",
    roles,
    domains,
    personas,
    skills,
    seed: eff["agents.seed"] === "yes-5-starter-docs",
    reviewByDate: addDays(today ?? new Date(), REVIEW_WINDOW_DAYS),
    strictness: asString(eff["agents.strictness"], "refuse-log-gap"),
    writeBack: asString(eff["kb.write_back"], "pr-only"),
    sensitivity: asString(eff["kb.sensitivity"], "three-tiers"),
    preset: presetName,
    ...rest,
  };
}
