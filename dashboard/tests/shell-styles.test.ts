// Spec 0095 Part L, read from the stylesheet: TV text is at least 40 px, and
// "Follow my phone" really follows the browser's reduced-motion setting.

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

const css = readFileSync(
  join(process.env.DASHBOARD_DIR ?? process.cwd(), "src", "index.css"),
  "utf8",
);

function ruleBody(selector: string): string {
  const start = css.indexOf(`\n${selector} {`);
  assert.ok(start >= 0, `a rule for ${selector}`);
  return css.slice(start, css.indexOf("}", start));
}

test("every TV text rule is at least 40 px (2.5rem at the default size)", () => {
  for (const selector of [
    ".tv-brand",
    ".tv-label",
    ".tv-text",
    ".tv-names",
    ".tv-notice",
    ".tv-title",
  ]) {
    const size = /font-size:\s*([\d.]+)rem/.exec(ruleBody(selector));
    assert.ok(size, `${selector} sets a size in rem`);
    assert.ok(Number(size[1]) >= 2.5, `${selector} is ${size[1]}rem`);
  }
});

test("phone controls are at least 44 px tall", () => {
  for (const selector of [".sh-button", ".sh-input", ".sh-choice"]) {
    assert.match(ruleBody(selector), /min-height:\s*44px/, selector);
  }
});

test("Follow my phone turns motion off under the browser's reduced-motion setting", () => {
  const media = css.indexOf("@media (prefers-reduced-motion: reduce)");
  assert.ok(media >= 0, "a prefers-reduced-motion rule exists");
  const block = css.slice(media, css.indexOf("\n}\n", media));
  assert.ok(block.includes('data-reduce-motion="system"'));
  assert.ok(block.includes("animation-duration: 0.001ms"));
  assert.ok(block.includes("transition-duration: 0.001ms"));
});
