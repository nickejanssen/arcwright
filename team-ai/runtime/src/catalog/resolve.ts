// Deterministic. No model calls. No network.
//
// Three-layer catalog resolution: toolkit -> org -> instance. Each layer is a
// directory with up to four subdirs (`namespaces/`, `roles/`, `skills/`,
// `personas/`). Entries are keyed by filename-without-extension. A later layer
// REPLACES an earlier entry with the same key (no merge) and stamps its origin.
//
// `.yaml` entries are parsed with `yaml` and validated against the matching
// JSON Schema. Personas are plain markdown, keyed by file stem, with the file
// contents as the body and no schema.

import { readdirSync, readFileSync, type Dirent } from "node:fs";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";

import type { SchemaTypeMap } from "../schema/validate.js";
import { validate } from "../schema/validate.js";
import type { CatalogItem, CatalogOrigin, PersonaCatalogEntry, ResolvedCatalog } from "./types.js";

export interface ResolveCatalogOptions {
  toolkitDir: string;
  orgDir?: string;
  instanceDir?: string;
}

interface Layer {
  dir: string;
  origin: CatalogOrigin;
}

type SchemaKind = "namespace-preset" | "role" | "skill-catalog";

function reason(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

function listFiles(dir: string, ext: string): string[] {
  let entries: Dirent[];
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return [];
  }
  return entries
    .filter((entry) => entry.isFile() && entry.name.endsWith(ext))
    .map((entry) => entry.name)
    .sort((a, b) => a.localeCompare(b));
}

function resolveKind<N extends SchemaKind>(
  layers: Layer[],
  subdir: string,
  schema: N,
): Map<string, CatalogItem<SchemaTypeMap[N]>> {
  const out = new Map<string, CatalogItem<SchemaTypeMap[N]>>();
  for (const layer of layers) {
    const kindDir = join(layer.dir, subdir);
    for (const file of listFiles(kindDir, ".yaml")) {
      const path = join(kindDir, file);
      let parsed: unknown;
      try {
        parsed = parseYaml(readFileSync(path, "utf8"));
      } catch (err) {
        throw new Error(`catalog: ${path}: ${reason(err)}`);
      }
      const result = validate(schema, parsed);
      if (!result.ok) {
        throw new Error(`catalog: ${path}: ${result.errors.join("; ")}`);
      }
      out.set(file.slice(0, -".yaml".length), { value: result.value, origin: layer.origin });
    }
  }
  return out;
}

function resolvePersonas(layers: Layer[]): Map<string, CatalogItem<PersonaCatalogEntry>> {
  const out = new Map<string, CatalogItem<PersonaCatalogEntry>>();
  for (const layer of layers) {
    const kindDir = join(layer.dir, "personas");
    for (const file of listFiles(kindDir, ".md")) {
      const path = join(kindDir, file);
      let body: string;
      try {
        body = readFileSync(path, "utf8");
      } catch (err) {
        throw new Error(`catalog: ${path}: ${reason(err)}`);
      }
      const name = file.slice(0, -".md".length);
      out.set(name, { value: { name, body }, origin: layer.origin });
    }
  }
  return out;
}

export function resolveCatalog(opts: ResolveCatalogOptions): ResolvedCatalog {
  const layers: Layer[] = [{ dir: opts.toolkitDir, origin: "toolkit" }];
  if (opts.orgDir !== undefined) layers.push({ dir: opts.orgDir, origin: "org" });
  if (opts.instanceDir !== undefined) layers.push({ dir: opts.instanceDir, origin: "instance" });

  return {
    namespaces: resolveKind(layers, "namespaces", "namespace-preset"),
    roles: resolveKind(layers, "roles", "role"),
    skills: resolveKind(layers, "skills", "skill-catalog"),
    personas: resolvePersonas(layers),
  };
}
