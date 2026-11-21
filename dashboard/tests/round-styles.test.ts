// Spec 0095 Part L, read from the stylesheet for the round screens: TV text is
// at least 40 px, phone tap targets at least 44 px, and the ready marks do not
// rely on colour.

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

const root = process.env.DASHBOARD_DIR ?? process.cwd();
const css = readFileSync(join(root, "src", "index.css"), "utf8");

// The body of the rule whose selector list names `selector`.
function ruleBody(selector: string): string {
  for (const rule of css.matchAll(/([^{}]+)\{([^}]*)\}/g)) {
    const selectors = rule[1].split(",").map((part) => part.trim());
    if (selectors.includes(selector)) return rule[2];
  }
  assert.fail(`a rule for ${selector}`);
}

test("every round TV text rule is at least 40 px (2.5rem at the default size)", () => {
  for (const selector of [
    ".tv-round-title",
    ".tv-clock",
    ".tv-line",
    ".tv-speaker",
    ".tv-ready",
    ".tv-ready-item",
    ".tv-prompt",
  ]) {
    const size = /font-size:\s*([\d.]+)rem/.exec(ruleBody(selector));
    assert.ok(size, `${selector} sets a size in rem`);
    assert.ok(Number(size[1]) >= 2.5, `${selector} is ${size[1]}rem`);
  }
});

test("every round phone control is at least 44 px tall", () => {
  for (const selector of [".rd-tab", ".rd-item", ".rd-summary", ".rd-note"]) {
    assert.match(ruleBody(selector), /min-height:\s*44px/, selector);
  }
});

test("a ready player is shown by a word and a mark, not by colour alone", () => {
  const source = readFileSync(
    join(root, "src", "screens", "round", "TvParts.tsx"),
    "utf8",
  );
  const words = readFileSync(join(root, "src", "shell", "copy.ts"), "utf8");
  assert.match(words, /readyWord:\s*"ready"/);
  assert.match(words, /notReadyWord:\s*"not yet"/);
  assert.match(source, /copy\.round\.readyWord/);
  assert.match(source, /copy\.round\.notReadyWord/);
  assert.match(source, /aria-hidden/, "the mark is drawn beside the word");
});

test("nothing on the thinking-time TV is animated", () => {
  assert.ok(!/@keyframes/.test(css), "no keyframe animation in the stylesheet");
  assert.ok(!/\.tv-clock[^{]*\{[^}]*animation/.test(css));
});

test("the story lines scroll instead of being cut off", () => {
  const body = ruleBody(".tv-lines");
  assert.ok(!/overflow(-y)?:\s*hidden/.test(body), "no hidden overflow");
  assert.match(body, /overflow-y:\s*auto/);
  assert.match(body, /min-height:\s*0/);
});
