import { describe, expect, it } from "vitest";

import { proposeNamespaceMap } from "./namespaces.js";

const PRESET = ["operating", "platform", "patterns", "playbooks", "decisions", "architecture"];

describe("proposeNamespaceMap", () => {
  it("matches exact names and leaves prd for a human decision", () => {
    const result = proposeNamespaceMap(["architecture", "decisions", "prd", "conventions"], PRESET);

    const matchedFolders = result.matched.map((m) => m.folder);
    expect(matchedFolders).toContain("architecture");
    expect(matchedFolders).toContain("decisions");

    const prd = result.unmatched.find((u) => u.folder === "prd");
    expect(prd).toBeDefined();
    expect(prd?.candidates.at(-1)).toBe("custom");
    expect(prd?.candidates).toHaveLength(4);
    for (const candidate of prd?.candidates.slice(0, 3) ?? []) {
      expect(PRESET).toContain(candidate);
    }
  });

  it("sorts matched entries by folder", () => {
    const result = proposeNamespaceMap(["platform", "decisions", "architecture"], PRESET);
    expect(result.matched.map((m) => m.folder)).toEqual(["architecture", "decisions", "platform"]);
  });

  it("resolves a synonym (arch -> architecture)", () => {
    const result = proposeNamespaceMap(["arch"], PRESET);
    expect(result.matched).toEqual([{ folder: "arch", namespace: "architecture" }]);
    expect(result.unmatched).toEqual([]);
  });

  it("matches singular/plural forms", () => {
    const result = proposeNamespaceMap(["decision", "pattern"], PRESET);
    expect(result.matched.map((m) => m.namespace).sort()).toEqual(["decisions", "patterns"]);
  });
});
