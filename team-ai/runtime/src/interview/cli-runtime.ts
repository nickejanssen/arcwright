// Deterministic control flow. No model calls. No network. The only disk write is
// the resume file, and only when the operator types "save".
//
// runInterviewCli drives the shared Engine as a terminal prompt loop: it prints
// each question with numbered options, reads a line, and interprets the control
// words (back / skip / why / save / defer / recommend) before treating anything
// else as an answer. Tests inject a string puller via `opts.answers`; without one
// it falls back to @inquirer/prompts. It never calls writeOutputs.

import { writeFile } from "node:fs/promises";
import { join } from "node:path";

import { checkbox, input, select } from "@inquirer/prompts";

import { loadBank } from "./bank.js";
import { Engine, type EngineState } from "./engine.js";
import { renderGate } from "./gates.js";
import type { Question } from "./types.js";
import type { AnswerSource } from "../generator/init-answers.js";

const RESUME_FILE = ".team-ai-interview-state.json";

export interface CliRuntimeOptions {
  cwd: string;
  answers?: AnswerSource;
  output?: (line: string) => void;
}

type StepResult = "advance" | "return";

function reason(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

function isSelect(question: Question): boolean {
  return question.type === "single_select" || question.type === "multi_select";
}

// Accepts the option value, its 1-based position, or its label (case-insensitive).
function resolveOption(question: Question, token: string): string {
  const trimmed = token.trim();
  const byValue = question.options.find((o) => o.value === trimmed);
  if (byValue) return byValue.value;

  if (/^\d+$/.test(trimmed)) {
    const option = question.options[Number.parseInt(trimmed, 10) - 1];
    if (option) return option.value;
  }

  const lower = trimmed.toLowerCase();
  const byLabel = question.options.find((o) => o.label.toLowerCase() === lower);
  if (byLabel) return byLabel.value;

  throw new Error(`'${token}' does not match an option for '${question.id}'`);
}

function resolveAnswer(question: Question, raw: string): unknown {
  if (question.type === "single_select") return resolveOption(question, raw);
  if (question.type === "multi_select") {
    return raw
      .split(",")
      .map((part) => part.trim())
      .filter((part) => part.length > 0)
      .map((part) => resolveOption(question, part));
  }
  return raw;
}

export async function runInterviewCli(opts: CliRuntimeOptions): Promise<EngineState> {
  const output = opts.output ?? ((line: string): void => console.log(line));
  const engine = new Engine(loadBank());

  const pull = async (key: string, question: Question | null): Promise<string> => {
    if (opts.answers) return opts.answers(key);
    return question ? inquireQuestion(question) : inquireGate();
  };

  const saveAndHint = async (): Promise<void> => {
    const path = join(opts.cwd, RESUME_FILE);
    await writeFile(path, JSON.stringify(engine.save(), null, 2), "utf8");
    output(`Saved to ${RESUME_FILE}. Resume with: team-ai resume`);
  };

  const handleQuestion = async (question: Question): Promise<StepResult> => {
    for (;;) {
      printQuestion(output, question);
      const raw = (await pull(question.id, question)).trim();
      const word = raw.toLowerCase();

      if (word === "back") {
        engine.back();
        return "advance";
      }
      if (word === "save") {
        await saveAndHint();
        return "return";
      }
      if (word === "why") {
        output(engine.why(question.id));
        continue;
      }

      try {
        if (word === "skip") {
          engine.skip(question.id);
        } else if (word === "defer") {
          engine.answer(question.id, "__defer__");
        } else if (word === "recommend") {
          engine.answer(question.id, "__recommend__");
        } else {
          engine.answer(question.id, resolveAnswer(question, raw));
        }
        return "advance";
      } catch (err) {
        output(reason(err));
        continue;
      }
    }
  };

  const handleGate = async (gate: 1 | 2 | 3): Promise<StepResult> => {
    for (;;) {
      output(renderGate(gate, engine));
      const word = (await pull(`gate.${gate}`, null)).trim().toLowerCase();

      if (word === "confirm" || word === "y" || word === "yes") {
        engine.confirmGate(gate);
        return "advance";
      }
      if (word === "back") {
        engine.back();
        return "advance";
      }
      if (word === "save") {
        await saveAndHint();
        return "return";
      }
      output("Type 'confirm', 'back', or 'save'.");
    }
  };

  for (let guard = 0; guard < 2000; guard += 1) {
    const step = engine.next();
    if (step === null) return engine.save();

    const result =
      step.kind === "gate" ? await handleGate(step.gate) : await handleQuestion(step.question);
    if (result === "return") return engine.save();
  }

  return engine.save();
}

function printQuestion(output: (line: string) => void, question: Question): void {
  output(question.prompt);
  if (isSelect(question)) {
    question.options.forEach((option, i) => {
      const tradeoff = option.tradeoff ? ` — ${option.tradeoff.replace(/\s+/g, " ").trim()}` : "";
      output(`  ${i + 1}) ${option.label}${tradeoff}`);
    });
  }
  const controls = ["back", "why", "save"];
  if (question.allow_defer) controls.push("defer", "skip");
  if (question.recommend !== undefined) controls.push("recommend");
  output(`  (enter a choice, or: ${controls.join(" / ")})`);
}

// --- @inquirer fallback (thin; the injected-answers path is what tests drive) ---

async function inquireQuestion(question: Question): Promise<string> {
  if (question.type === "multi_select") {
    const picked = await checkbox({
      message: question.prompt,
      choices: question.options.map((o) => ({ name: o.label, value: o.value })),
    });
    return picked.join(",");
  }
  if (question.type === "single_select") {
    const extra = [
      { name: "(explain why this is asked)", value: "why" },
      { name: "(go back)", value: "back" },
      { name: "(save and exit)", value: "save" },
    ];
    return select({
      message: question.prompt,
      choices: [...question.options.map((o) => ({ name: o.label, value: o.value })), ...extra],
    });
  }
  return input({ message: question.prompt });
}

async function inquireGate(): Promise<string> {
  return select({
    message: "Confirm this gate?",
    choices: [
      { name: "Confirm", value: "confirm" },
      { name: "Back", value: "back" },
      { name: "Save and exit", value: "save" },
    ],
  });
}
