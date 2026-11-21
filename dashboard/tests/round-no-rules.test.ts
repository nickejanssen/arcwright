// Spec 0095 Part L / AGENTS.md: no game rule in TypeScript. A search of the
// round and notebook code for the three things the screens must never do:
// work out the budget, judge right or wrong, or build the menu. It is a plain
// text search, so it is a tripwire, not a proof; review does the reading.

import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

const root = process.env.DASHBOARD_DIR ?? process.cwd();

function sources(): Array<{ path: string; text: string }> {
  const files = [join(root, "src", "api", "player.ts")];
  for (const dir of ["round", "notebook"]) {
    const base = join(root, "src", "screens", dir);
    for (const name of readdirSync(base)) {
      if (/\.tsx?$/.test(name)) files.push(join(base, name));
    }
  }
  return files.map((path) => ({ path, text: readFileSync(path, "utf8") }));
}

// Code only: comments are stripped so the rule can be written about.
function code(text: string): string {
  return text.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");
}

test("no arithmetic on the budget, the cost or the number left", () => {
  // Operators with a space on each side, as the formatter writes arithmetic.
  const names = "(?:remainingBudget|remaining_budget|left|cost|budget)";
  const op = "(?:[-+*/]|<=?|>=?)";
  const sums = new RegExp(
    `\\b${names}\\s+${op}\\s+[\\w(]|[\\w)]\\s+${op}\\s+${names}\\b`,
  );
  for (const { path, text } of sources()) {
    for (const line of code(text).split("\n")) {
      // The route's number may be compared with 0 to choose a sentence.
      const without = line.replace(/(remainingBudget|left)\s*===\s*0/g, "");
      assert.ok(!sums.test(without), `${path}: ${line.trim()}`);
    }
  }
});

test("no right-or-wrong, no theory and no truth words in the round code", () => {
  for (const { path, text } of sources()) {
    const body = code(text);
    for (const word of [
      /\bcorrect\b/i,
      /\bwrong\b/i,
      /\bisRight\b/,
      /\bguilty\b/i,
      /\bsolution\b/i,
      /\bsupports?\b/i,
      /\bcontradict/i,
    ]) {
      assert.ok(!word.test(body), `${path} has ${word}`);
    }
  }
});

test("no menu is built: the screens never create items or filter the route's list by a rule", () => {
  for (const { path, text } of sources()) {
    const body = code(text);
    assert.ok(!/\.sort\(/.test(body), `${path} sorts a list the engine gave`);
    assert.ok(!/\.reverse\(/.test(body), `${path} reverses a list`);
    assert.ok(
      !/\b(menu|items)[\w.?]*\.filter\(/.test(body),
      `${path} filters the menu`,
    );
  }
});
