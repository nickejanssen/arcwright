// Deterministic. No model calls. No network.
//
// The interview question bank: one `questions.yaml`, two runtimes. `loadBank()`
// reads the bundled file, validates it against `schemas/questions.schema.json`,
// normalizes optional fields, and returns typed `Question[]`. Both the CLI
// prompts and the in-Claude `scaffold-interview` skill consume this.
//
// `questions.yaml` ships as source (it is listed in package.json `files` and the
// build does not copy it to `dist/`). Resolving it relative to the package root
// works from both `dist/interview/bank.js` and `src/interview/bank.ts`: each
// lives two segments below its root, so `../../src/interview/questions.yaml`
// lands on the same file under vitest and in a published install.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { parse as parseYaml } from "yaml";

import { validate } from "../schema/validate.js";
import type { Question, QuestionOption, RawQuestion } from "./types.js";

export type { Question, QuestionOption, QuestionType, RawQuestion } from "./types.js";

export function questionsPath(): string {
  return fileURLToPath(new URL("../../src/interview/questions.yaml", import.meta.url));
}

function normalize(raw: RawQuestion): Question {
  const options = (raw.options ?? []).map((option) => Object.freeze({ ...option }));
  const question: Question = {
    id: raw.id,
    act: raw.act,
    type: raw.type,
    prompt: raw.prompt,
    why: raw.why,
    options: Object.freeze(options) as QuestionOption[],
    allow_defer: raw.allow_defer ?? false,
    ask_if: raw.ask_if,
  };
  if ("default" in raw) question.default = raw.default;
  if ("recommend" in raw) question.recommend = raw.recommend;
  if (raw.recommend_why !== undefined) question.recommend_why = raw.recommend_why;
  return Object.freeze(question);
}

export function loadBank(): Question[] {
  const text = readFileSync(questionsPath(), "utf8");
  const parsed: unknown = parseYaml(text);

  const result = validate("questions", parsed);
  if (!result.ok) {
    throw new Error(`questions.yaml is invalid:\n  ${result.errors.join("\n  ")}`);
  }

  return Object.freeze(result.value.questions.map(normalize)) as Question[];
}
