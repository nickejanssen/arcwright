// Validate front-matter `relations` targets against the set of loaded doc ids.

import type { KbDoc } from "./types.js";

export interface RelationError {
  doc_id: string;
  relation: string;
  value: string;
  reason: string;
}

const PARTNER_SLUG = /^[a-z0-9-]+$/;

export function checkRelations(docs: KbDoc[], knownRoles: Set<string>): RelationError[] {
  const errors: RelationError[] = [];
  const knownIds = new Set(docs.map((doc) => doc.id));

  for (const doc of docs) {
    const relations = doc.frontmatter.relations;
    if (!relations) continue;

    for (const [relation, value] of Object.entries(relations)) {
      if (value === undefined) continue;

      if (relation === "owned_by_role") {
        if (typeof value !== "string") {
          errors.push({ doc_id: doc.id, relation, value: String(value), reason: "wrong type" });
          continue;
        }
        if (!knownRoles.has(value)) {
          errors.push({ doc_id: doc.id, relation, value, reason: "unknown role" });
        }
        continue;
      }

      if (relation === "used_by_partner") {
        if (!Array.isArray(value)) {
          errors.push({ doc_id: doc.id, relation, value, reason: "wrong type" });
          continue;
        }
        for (const entry of value) {
          if (!PARTNER_SLUG.test(entry)) {
            errors.push({
              doc_id: doc.id,
              relation,
              value: entry,
              reason: "not a valid partner slug",
            });
          }
        }
        continue;
      }

      // Every other relation key holds an array of doc ids.
      if (!Array.isArray(value)) {
        errors.push({ doc_id: doc.id, relation, value, reason: "wrong type" });
        continue;
      }
      for (const entry of value) {
        if (!knownIds.has(entry)) {
          errors.push({ doc_id: doc.id, relation, value: entry, reason: "unknown doc id" });
        }
      }
    }
  }

  return errors;
}
