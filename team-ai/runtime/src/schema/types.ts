// Hand-written TypeScript mirrors of the JSON Schemas in `schemas/`.
// Keep these in sync with the schema files.

export type ModelTier = "none" | "small" | "large";

export type DocStatus = "draft" | "active" | "deprecated";

export type Sensitivity = "public" | "internal" | "confidential";

export interface FrontMatterRelations {
  depends_on?: string[];
  used_by_partner?: string[];
  owned_by_role?: string;
  [relation: string]: string[] | string | undefined;
}

export interface FrontMatter {
  id: string;
  namespace: string;
  title: string;
  owner: string;
  status: DocStatus;
  review_by: string;
  sensitivity: Sensitivity;
  source: string;
  tags: string[];
  supersedes: string[];
  source_url?: string | null;
  relations?: FrontMatterRelations;
}

export type AgentKind = "router" | "subagent" | "persona";

export interface AgentDef {
  name: string;
  kind: AgentKind;
  description: string;
  model_tier: ModelTier;
  kb_namespaces: string[];
  tools: string[];
  max_hops: number;
  instructions_file: string;
  escalate_to?: string;
}

export type DomainAuthority = "canonical" | "provisional" | "archived";

export interface ManifestDomain {
  id: string;
  description: string;
  keywords: string[];
  kb_namespace: string;
  subagent: string;
  model_tier: ModelTier;
  owner: string;
  repo?: string;
  escalate_to?: string;
  group?: string;
  authority?: DomainAuthority;
  not_owned?: string[];
  depends_on?: string[];
}

export interface ManifestAgent {
  name: string;
  tier: 1 | 2 | 3;
  kind: AgentKind;
  max_hops: number;
  kb_namespaces: string[];
  group?: string;
  skills?: string[];
  escalate_to?: string;
  source?: "generated" | "authored";
  path?: string;
}

export interface ManifestSkill {
  id: string;
  deterministic: boolean;
  description?: string;
  script?: string;
  used_by?: string[];
  path?: string;
  source?: "generated" | "authored";
}

export interface Manifest {
  domains: ManifestDomain[];
  agents?: ManifestAgent[];
  skills?: ManifestSkill[];
}

export interface GoldenQuestion {
  id: string;
  question: string;
  expect_namespace: string;
  expect_paths: string[];
  expect_route: string;
  expect_tier_max: ModelTier;
  must_cite: boolean;
  source_path?: string;
  generated_on?: string;
  answer_evidence?: string;
}

export interface SpokeDomain {
  id: string;
  description: string;
  keywords: string[];
  subagent: string;
  model_tier: ModelTier;
  escalate_to?: string;
}

export interface SpokeExports {
  skills?: string[];
  agents?: string[];
}

export interface SpokeConfig {
  name: string;
  kb_namespace: string;
  owner: string;
  core_repo: string;
  toolkit_version: string;
  domains: SpokeDomain[];
  exports?: SpokeExports;
}

export interface DeferredDecision {
  question: string;
  applied_default: unknown;
  revisit: string;
}

export interface GeneratedPathEntry {
  path: string;
  sha256: string;
}

export interface TeamProfile {
  team_ai_version: string;
  created: string;
  answers: Record<string, unknown>;
  deferred: DeferredDecision[];
  generated_paths?: GeneratedPathEntry[];
}
