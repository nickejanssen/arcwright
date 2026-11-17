// Deterministic. No model calls. No network. No disk I/O. Pure state machine.
//
// The interview engine walks a question bank act by act, skipping questions
// whose `ask_if` gate is false, pausing at three confirmation gates, and
// resolving `implies` pre-fills into a `derived` layer that explicit answers
// always override. Both runtimes drive this same class: the CLI renders each
// `Step` as a prompt; the in-Claude skill renders it as a message. Neither owns
// the branching logic.

import { evalAskIf } from "./ask-if.js";
import type { Question } from "./types.js";

export type Step = { kind: "question"; question: Question } | { kind: "gate"; gate: 1 | 2 | 3 };

export interface AnswerRecord {
  value: unknown;
  via: "direct" | "defer" | "recommend";
  why?: string;
}

export interface DerivedRecord {
  value: string | number | boolean;
  from: string;
  overridden: boolean;
}

export interface EngineState {
  answers: Record<string, AnswerRecord>;
  derived: Record<string, DerivedRecord>;
  history: string[];
  confirmedGates: number[];
  phase: "act:0" | "act:1" | "act:2" | "gate:1" | "act:3" | "gate:2" | "act:4" | "gate:3" | "done";
}

const DEFER = "__defer__";
const RECOMMEND = "__recommend__";
const ACTS = [0, 1, 2, 3, 4] as const;
const GATE_AFTER_ACT: Record<number, 1 | 2 | 3> = { 2: 1, 3: 2, 4: 3 };
const ACT_BEFORE_GATE: Record<number, number> = { 1: 2, 2: 3, 3: 4 };

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function freshState(): EngineState {
  return { answers: {}, derived: {}, history: [], confirmedGates: [], phase: "act:0" };
}

function fmt(value: unknown): string {
  return typeof value === "string" ? value : (JSON.stringify(value) ?? "undefined");
}

export class Engine {
  private readonly bank: Question[];
  private state: EngineState;

  constructor(bank: Question[], state?: EngineState) {
    this.bank = bank;
    this.state = state ? clone(state) : freshState();
  }

  static load(bank: Question[], state: EngineState): Engine {
    return new Engine(bank, state);
  }

  /**
   * The answer view used for `ask_if` evaluation and `implies` chaining:
   * non-overridden `derived` values underneath the explicit `answers` values.
   */
  effectiveAnswers(): Record<string, unknown> {
    const out: Record<string, unknown> = {};
    for (const [k, d] of Object.entries(this.state.derived)) {
      if (!d.overridden) out[k] = d.value;
    }
    for (const [k, a] of Object.entries(this.state.answers)) {
      out[k] = a.value;
    }
    return out;
  }

  /**
   * Next step to present, or `null` once the interview is done. Advances
   * `this.state.phase` to reflect the current position; does not otherwise
   * mutate. `computeStep()` never reads `phase`, so save/load is unaffected.
   */
  next(): Step | null {
    const step = this.computeStep();
    this.state.phase = this.phaseFor(step);
    return step;
  }

  answer(id: string, value: unknown): void {
    const question = this.mustFind(id);
    const impliesList: Array<Record<string, string | number | boolean>> = [];
    let record: AnswerRecord;

    if (value === DEFER) {
      if (!question.allow_defer) throw new Error(`question '${id}' does not allow defer`);
      const resolved = question.default ?? null;
      record = { value: resolved, via: "defer" };
      this.collectImplies(question, resolved, impliesList);
    } else if (value === RECOMMEND) {
      if (question.recommend === undefined) {
        throw new Error(`question '${id}' has no recommendation`);
      }
      record = { value: question.recommend, via: "recommend" };
      if (question.recommend_why !== undefined) record.why = question.recommend_why;
      this.collectImplies(question, question.recommend, impliesList);
    } else {
      if (question.type === "single_select") {
        const option = question.options.find((o) => o.value === value);
        if (!option) {
          throw new Error(`'${fmt(value)}' is not a valid option for '${id}'`);
        }
        if (option.implies) impliesList.push(option.implies);
      } else if (question.type === "multi_select") {
        if (!Array.isArray(value)) {
          throw new Error(`'${id}' expects an array of option values`);
        }
        const known = new Set(question.options.map((o) => o.value));
        for (const v of value) {
          if (typeof v !== "string" || !known.has(v)) {
            throw new Error(`'${fmt(v)}' is not a valid option for '${id}'`);
          }
        }
        for (const option of question.options) {
          if (value.includes(option.value) && option.implies) impliesList.push(option.implies);
        }
      }
      record = { value, via: "direct" };
    }

    const alreadyAnswered = id in this.state.answers;
    this.state.answers[id] = record;

    // An explicit answer for a key another question had derived wins outright.
    const selfDerived = this.state.derived[id];
    if (selfDerived) selfDerived.overridden = true;

    // Re-answering: retract the previous choice's derivations before applying
    // the new option's implies, so `derived` never carries a stale pre-fill.
    for (const k of Object.keys(this.state.derived)) {
      if (this.state.derived[k]?.from === id) delete this.state.derived[k];
    }

    for (const implies of impliesList) {
      for (const [k, v] of Object.entries(implies)) {
        if (k === "warn") continue;
        if (k in this.state.answers) {
          const existing = this.state.derived[k];
          if (existing) existing.overridden = true;
          continue;
        }
        this.state.derived[k] = { value: v, from: id, overridden: false };
      }
    }

    // The id is already in `history` on a re-answer; don't record it twice.
    if (!alreadyAnswered) this.state.history.push(id);
  }

  /** Alias for `answer(id, "__defer__")`. */
  skip(id: string): void {
    this.answer(id, DEFER);
  }

  back(): void {
    const id = this.state.history.pop();
    if (id === undefined) return;

    delete this.state.answers[id];
    for (const k of Object.keys(this.state.derived)) {
      if (this.state.derived[k]?.from === id) delete this.state.derived[k];
    }
    // If this answer had overridden a still-live derived value, hand it back.
    const restored = this.state.derived[id];
    if (restored) restored.overridden = false;

    const eff = this.effectiveAnswers();
    this.state.confirmedGates = this.state.confirmedGates.filter((g) => {
      const act = ACT_BEFORE_GATE[g];
      return act !== undefined && this.actComplete(act, eff);
    });
  }

  confirmGate(n: 1 | 2 | 3): void {
    const step = this.next();
    if (!step || step.kind !== "gate" || step.gate !== n) {
      throw new Error(`gate ${n} is not the current step`);
    }
    this.state.confirmedGates.push(n);
    this.next();
  }

  why(id: string): string {
    return this.mustFind(id).why;
  }

  /** Question ids whose chosen option surfaced an `implies.warn`. Computed. */
  warnings(): string[] {
    const out: string[] = [];
    for (const q of this.bank) {
      const record = this.state.answers[q.id];
      if (!record) continue;
      const chosen = Array.isArray(record.value) ? record.value : [record.value];
      const warned = q.options.some((o) => chosen.includes(o.value) && o.implies?.warn === true);
      if (warned) out.push(q.id);
    }
    return out;
  }

  /** Serializable deep clone of the current state. */
  save(): EngineState {
    return clone(this.state);
  }

  private mustFind(id: string): Question {
    const question = this.bank.find((q) => q.id === id);
    if (!question) throw new Error(`unknown question '${id}'`);
    return question;
  }

  private collectImplies(
    question: Question,
    resolved: unknown,
    into: Array<Record<string, string | number | boolean>>,
  ): void {
    const option = question.options.find((o) => o.value === resolved);
    if (option?.implies) into.push(option.implies);
  }

  private actComplete(act: number, eff: Record<string, unknown>): boolean {
    for (const q of this.bank) {
      if (q.act !== act) continue;
      if (q.id in this.state.answers) continue;
      if (!evalAskIf(q.ask_if, eff)) continue;
      return false;
    }
    return true;
  }

  private computeStep(): Step | null {
    const eff = this.effectiveAnswers();
    for (const act of ACTS) {
      for (const q of this.bank) {
        if (q.act !== act) continue;
        if (q.id in this.state.answers) continue;
        if (!evalAskIf(q.ask_if, eff)) continue;
        return { kind: "question", question: q };
      }
      const gate = GATE_AFTER_ACT[act];
      if (gate !== undefined && !this.state.confirmedGates.includes(gate)) {
        return { kind: "gate", gate };
      }
    }
    return null;
  }

  private phaseFor(step: Step | null): EngineState["phase"] {
    if (step === null) return "done";
    if (step.kind === "gate") return `gate:${step.gate}`;
    const act = step.question.act;
    if (act === 0 || act === 1 || act === 2 || act === 3 || act === 4) return `act:${act}`;
    return "done";
  }
}
