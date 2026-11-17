import { describe, expect, it } from "vitest";

import { checkRelations } from "./relations.js";
import type { FrontMatterRelations } from "../schema/types.js";
import type { KbDoc } from "./types.js";

function doc(id: string, relations?: FrontMatterRelations): KbDoc {
  return {
    id,
    path: `${id.split(".").join("/")}.md`,
    frontmatter: {
      id,
      namespace: "platform",
      title: id,
      owner: "o",
      status: "active",
      review_by: "2027-01-01",
      sensitivity: "internal",
      source: "authored",
      tags: [],
      supersedes: [],
      ...(relations ? { relations } : {}),
    },
    body: "",
    headings: [],
    isBacklog: false,
  };
}

const roles = new Set(["platform-lead", "support-lead"]);

describe("checkRelations", () => {
  it("returns no errors when every relation target is valid", () => {
    const docs = [
      doc("x.platform.rl", {
        depends_on: ["x.platform.auth"],
        used_by_partner: ["acme-co"],
        owned_by_role: "platform-lead",
      }),
      doc("x.platform.auth"),
    ];
    expect(checkRelations(docs, roles)).toEqual([]);
  });

  it("flags an unknown doc id in depends_on", () => {
    const docs = [doc("x.platform.rl", { depends_on: ["x.platform.missing"] })];
    expect(checkRelations(docs, roles)).toEqual([
      {
        doc_id: "x.platform.rl",
        relation: "depends_on",
        value: "x.platform.missing",
        reason: "unknown doc id",
      },
    ]);
  });

  it("does not validate used_by_partner values as doc ids", () => {
    const docs = [doc("x.platform.rl", { used_by_partner: ["acme-co", "beta-team"] })];
    expect(checkRelations(docs, roles)).toEqual([]);
  });

  it("flags a used_by_partner value that is not a valid partner slug", () => {
    const docs = [doc("x.platform.rl", { used_by_partner: ["Acme Co"] })];
    expect(checkRelations(docs, roles)).toEqual([
      {
        doc_id: "x.platform.rl",
        relation: "used_by_partner",
        value: "Acme Co",
        reason: "not a valid partner slug",
      },
    ]);
  });

  it("flags owned_by_role not in knownRoles", () => {
    const docs = [doc("x.platform.rl", { owned_by_role: "ghost-role" })];
    expect(checkRelations(docs, roles)).toEqual([
      {
        doc_id: "x.platform.rl",
        relation: "owned_by_role",
        value: "ghost-role",
        reason: "unknown role",
      },
    ]);
  });

  it("does not flag owned_by_role in knownRoles", () => {
    const docs = [doc("x.platform.rl", { owned_by_role: "support-lead" })];
    expect(checkRelations(docs, roles)).toEqual([]);
  });

  it("flags an unknown doc id in a custom relation key", () => {
    const docs = [doc("x.platform.rl", { blocks: ["x.a.missing"] }), doc("x.platform.auth")];
    expect(checkRelations(docs, roles)).toEqual([
      {
        doc_id: "x.platform.rl",
        relation: "blocks",
        value: "x.a.missing",
        reason: "unknown doc id",
      },
    ]);
  });

  it("flags a wrong-typed relation value", () => {
    const docs = [
      doc("x.platform.rl", { depends_on: "x.platform.auth" } as unknown as FrontMatterRelations),
      doc("x.platform.rl2", {
        owned_by_role: ["platform-lead"],
      } as unknown as FrontMatterRelations),
      doc("x.platform.auth"),
    ];
    const errors = checkRelations(docs, roles);
    expect(errors).toContainEqual({
      doc_id: "x.platform.rl",
      relation: "depends_on",
      value: "x.platform.auth",
      reason: "wrong type",
    });
    expect(errors).toContainEqual({
      doc_id: "x.platform.rl2",
      relation: "owned_by_role",
      value: "platform-lead",
      reason: "wrong type",
    });
  });

  it("returns all errors across all docs", () => {
    const docs = [
      doc("x.a", { depends_on: ["x.missing1"] }),
      doc("x.b", { depends_on: ["x.missing2"], owned_by_role: "ghost" }),
    ];
    expect(checkRelations(docs, roles)).toHaveLength(3);
  });
});
