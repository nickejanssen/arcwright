import { describe, expect, it } from "vitest";
import { packageVersion } from "./version.js";

describe("packageVersion", () => {
  it("returns a semver string", () => {
    expect(packageVersion()).toMatch(/^\d+\.\d+\.\d+$/);
  });
});
