import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("tooling config", () => {
  it("eslint bans explicit any and floating promises", () => {
    const cfg = readFileSync("eslint.config.js", "utf8");
    expect(cfg).toContain('"@typescript-eslint/no-explicit-any": "error"');
    expect(cfg).toContain('"@typescript-eslint/no-floating-promises": "error"');
  });
  it("lefthook runs commitlint on commit-msg", () => {
    const cfg = readFileSync("lefthook.yml", "utf8");
    expect(cfg).toContain("commitlint --edit");
  });
  it("prettier config sets printWidth 100", () => {
    const cfg = JSON.parse(readFileSync(".prettierrc.json", "utf8")) as { printWidth: number };
    expect(cfg.printWidth).toBe(100);
  });
});
