import { afterEach, describe, expect, it, vi } from "vitest";

import { run } from "./doctor.js";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);

afterEach(() => log.mockClear());

function printed(): string {
  return log.mock.calls.map((c) => String(c[0])).join("\n");
}

describe("doctor --self", () => {
  it("passes on the framework and exits 0", async () => {
    expect(await run({ self: true })).toBe(0);
    expect(printed()).toContain("✓ schemas load and Ajv-compile");
  });

  it("passes --strict now that every framework piece is built", async () => {
    expect(await run({ self: true, strict: true })).toBe(0);
  });
});

describe("doctor instance mode", () => {
  it("is report-only: exits 0 even with remaining items", async () => {
    const code = await run({ root: "src/doctor/fixtures/incomplete-instance" });
    expect(code).toBe(0);
    expect(printed()).toMatch(/\d+ item\(s\) remaining\. See SETUP\.md\./);
  });

  it("exits 1 under --strict when items remain", async () => {
    const code = await run({ root: "src/doctor/fixtures/incomplete-instance", strict: true });
    expect(code).toBe(1);
  });

  it("marks most checks green on the complete fixture", async () => {
    const code = await run({ root: "src/doctor/fixtures/complete-instance" });
    expect(code).toBe(0);
    expect(printed()).toContain("✓ repo structure");
    expect(printed()).toContain("✓ manifest assembled");
  });
});
