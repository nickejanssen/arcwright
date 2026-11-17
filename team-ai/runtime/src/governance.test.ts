import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("governance", () => {
  it("LICENSE is Apache-2.0", () => {
    const t = readFileSync("LICENSE", "utf8");
    expect(t).toContain("Apache License");
    expect(t).toContain("Version 2.0, January 2004");
  });
  it("CHANGELOG has a 0.1.0 section", () => {
    expect(readFileSync("CHANGELOG.md", "utf8")).toMatch(/##\s*\[0\.1\.0\]/);
  });
  it("CONTRIBUTING forbids team content in framework code", () => {
    expect(readFileSync("CONTRIBUTING.md", "utf8").toLowerCase()).toContain("no team");
  });
  it("CODEOWNERS assigns the whole tree", () => {
    expect(readFileSync("CODEOWNERS", "utf8")).toContain("* @nickejanssen");
  });
  it("PR template asks about the quality bar", () => {
    expect(readFileSync(".github/PULL_REQUEST_TEMPLATE.md", "utf8").toLowerCase()).toContain(
      "quality-bar",
    );
  });
});
