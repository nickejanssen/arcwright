// Catalog model: the toolkit ships presets for the four catalog kinds
// (namespaces, roles, skills, personas). An org fork or a single instance may
// override any entry by dropping a same-stem file in its own catalog layer.
//
// Namespace, role, and skill entries are validated against the JSON Schemas in
// `schemas/`. Personas are plain markdown with no schema.

import type { ModelTier } from "../schema/types.js";

export interface SeedDoc {
  // Path relative to `kb/`.
  path: string;
  title: string;
  purpose: string;
}

export interface NamespacePreset {
  name: string;
  description: string;
  second_level: string[];
  domain_dir: string | null;
  seed_docs: SeedDoc[];
}

export interface RoleArchetype {
  name: string;
  summary: string;
  default_namespaces: string[];
  default_skills: string[];
  model_tier: ModelTier;
  persona_default: string;
}

export interface SkillCatalogEntry {
  name: string;
  tier: ModelTier;
  summary: string;
  presets: string[] | "all";
}

export interface PersonaCatalogEntry {
  name: string;
  body: string;
}

export type CatalogOrigin = "toolkit" | "org" | "instance";

export interface CatalogItem<T> {
  value: T;
  origin: CatalogOrigin;
}

export interface ResolvedCatalog {
  namespaces: Map<string, CatalogItem<NamespacePreset>>;
  roles: Map<string, CatalogItem<RoleArchetype>>;
  skills: Map<string, CatalogItem<SkillCatalogEntry>>;
  personas: Map<string, CatalogItem<PersonaCatalogEntry>>;
}
