// Deterministic. No model calls. No network.
//
// Shared shapes for the `team-ai adopt` flow: front-matter inference, namespace
// mapping, the quality-bar gap report, and the full adoption plan that
// `schemas/adoption-plan.schema.json` validates.

import type { FrontMatter } from "../schema/types.js";

// The namespace a backfill item carries until its folder's namespace decision
// is made. `team-ai adopt --apply` refuses to write a doc that still has it.
export const PENDING_NAMESPACE = "__pending__";

export interface NamespaceMatch {
  folder: string;
  namespace: string;
}

export interface NamespaceDecision {
  folder: string;
  candidates: string[];
  chosen: string | null;
}

export interface AdoptionNamespaceMap {
  matched: NamespaceMatch[];
  decisions: NamespaceDecision[];
}

export interface BackfillItem {
  path: string;
  namespace: string;
  frontmatter: FrontMatter;
  approved: boolean;
  conflict: string | null;
}

export interface RelabelItem {
  path: string;
  current_source: string | null;
  proposed_source: string;
  approved: boolean;
}

export interface GapEntry {
  id: string;
  satisfied: boolean;
  evidence: string;
  closesWith: string;
}

export interface AdoptionPlan {
  generated_by: string;
  root: string;
  created: string;
  namespace_map: AdoptionNamespaceMap;
  backfill: BackfillItem[];
  relabels: RelabelItem[];
  gap: GapEntry[];
  collisions: string[];
  archived_skipped: number;
}
