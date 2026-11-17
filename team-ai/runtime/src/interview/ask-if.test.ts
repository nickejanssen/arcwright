import { describe, expect, it } from "vitest";

import { evalAskIf } from "./ask-if.js";

describe("evalAskIf", () => {
  const cases: Array<[string, Record<string, unknown>, boolean]> = [
    ["always", {}, true],

    // != against a known and an unknown identifier
    ['team.size != "1-3"', { "team.size": "4-8" }, true],
    ['team.size != "1-3"', { "team.size": "1-3" }, false],
    ['team.size != "1-3"', {}, true],

    // == semantics, including unknown -> false
    ['mode == "attach"', { mode: "attach" }, true],
    ['mode == "attach"', { mode: "instance" }, false],
    ['mode == "attach"', {}, false],

    // in list, scalar and multi_select array membership
    ['team.size in ["4-8", "9-20"]', { "team.size": "4-8" }, true],
    ['team.size in ["4-8", "9-20"]', { "team.size": "1-3" }, false],
    ['team.surfaces in ["chat-apps"]', { "team.surfaces": ["coding-agent", "chat-apps"] }, true],
    ['team.surfaces in ["voice"]', { "team.surfaces": ["coding-agent", "chat-apps"] }, false],
    ['missing in ["a"]', {}, false],

    // has(): array contains, string equals, unknown -> false
    ['has(team.surfaces, "chat-apps")', { "team.surfaces": ["chat-apps"] }, true],
    ['has(team.surfaces, "chat-apps")', { "team.surfaces": ["coding-agent"] }, false],
    ['has(team.surfaces, "chat-apps")', { "team.surfaces": "chat-apps" }, true],
    ['has(team.surfaces, "chat-apps")', {}, false],

    // boolean composition and precedence
    ['a == "1" && (b in ["2", "3"])', { a: "1", b: "3" }, true],
    ['a == "1" && (b in ["2", "3"])', { a: "1", b: "9" }, false],
    ['a == "1" || b == "2"', { b: "2" }, true],
    ['a == "1" || b == "2"', {}, false],
    ['a == "1" || b == "2" && c == "3"', { b: "2" }, false],
    ['a == "1" || b == "2" && c == "3"', { a: "1" }, true],
  ];

  for (const [expr, answers, expected] of cases) {
    it(`${expr} with ${JSON.stringify(answers)} -> ${String(expected)}`, () => {
      expect(evalAskIf(expr, answers)).toBe(expected);
    });
  }

  it("never throws on an unknown identifier", () => {
    expect(() => evalAskIf('nope.here == "x"', {})).not.toThrow();
    expect(() => evalAskIf('has(nope.here, "x")', {})).not.toThrow();
    expect(() => evalAskIf('nope in ["x"]', {})).not.toThrow();
  });

  it("throws a formatted parse error on a malformed expression", () => {
    expect(() => evalAskIf('team.size ~~ "1-3"', {})).toThrow(
      /ask_if parse error in 'team.size ~~ "1-3"'/,
    );
    expect(() => evalAskIf("team.size ==", {})).toThrow(/ask_if parse error/);
    expect(() => evalAskIf('(a == "1"', {})).toThrow(/ask_if parse error/);
    expect(() => evalAskIf("", {})).toThrow(/ask_if parse error/);
  });
});
