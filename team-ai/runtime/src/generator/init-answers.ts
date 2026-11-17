// Deterministic. No model calls. No network. One disk read at construction time.
//
// Backs `team-ai init --answers <file>`. A YAML mapping is keyed by question id
// (plus `gate.1`–`gate.3`), which survives question-bank changes: a missing key
// fails loudly instead of shifting every later answer. A YAML list is the legacy
// positional form.

import { readFileSync } from "node:fs";

import { parse as parseYaml } from "yaml";

export type AnswerSource = (key: string) => Promise<string>;

export interface LoadedAnswers {
  pull: AnswerSource;
  unusedKeys: () => string[];
}

const CONTROL_WORDS = new Set(["why", "back", "save"]);

function coerce(value: unknown, where: string): string {
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) return value.map((v) => coerce(v, where)).join(",");
  throw new Error(`${where}: every answer must be a string, number, boolean, or list of them`);
}

function rejectControlWords(value: unknown, where: string): void {
  if (typeof value === "string" && CONTROL_WORDS.has(value.trim().toLowerCase())) {
    throw new Error(`${where}: '${value}' is a control word, not an answer`);
  }
  if (Array.isArray(value)) {
    value.forEach((entry, index) => rejectControlWords(entry, `${where}[${index}]`));
  }
}

export function loadAnswerFile(path: string): LoadedAnswers {
  let parsed: unknown;
  try {
    parsed = parseYaml(readFileSync(path, "utf8"));
  } catch (err) {
    throw new Error(
      `${path}: not valid YAML — ${err instanceof Error ? err.message : String(err)}`,
    );
  }

  if (Array.isArray(parsed)) {
    const entries = parsed.map((entry, i) => coerce(entry, `${path} entry ${i}`));
    let index = 0;
    return {
      pull: () => {
        if (index >= entries.length) {
          return Promise.reject(
            new Error(`answer file exhausted: ${path} has ${entries.length} entries`),
          );
        }
        const next = entries[index] ?? "";
        index += 1;
        return Promise.resolve(next);
      },
      unusedKeys: () => [],
    };
  }

  if (parsed === null || typeof parsed !== "object") {
    throw new Error(`${path}: expected a mapping of question id to answer, or a list`);
  }

  const keyed = new Map<string, string>();
  for (const [key, value] of Object.entries(parsed as Record<string, unknown>)) {
    rejectControlWords(value, `${path} key '${key}'`);
    const answer = coerce(value, `${path} key '${key}'`);
    keyed.set(key, answer);
  }

  const used = new Set<string>();
  let lastKey: string | undefined;
  return {
    pull: (key) => {
      if (key === lastKey) {
        return Promise.reject(
          new Error(`answer file ${path}: the answer for '${key}' was not accepted`),
        );
      }
      lastKey = key;
      const answer = keyed.get(key);
      if (answer === undefined) {
        return Promise.reject(new Error(`answer file ${path} has no answer for '${key}'`));
      }
      used.add(key);
      return Promise.resolve(answer);
    },
    unusedKeys: () => [...keyed.keys()].filter((key) => !used.has(key)).sort(),
  };
}
