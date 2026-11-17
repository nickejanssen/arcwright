// Hand-written TypeScript mirror of `schemas/questions.schema.json`.
// Keep in sync with the schema file. The bank is the single source of truth for
// both interview runtimes (the CLI prompts and the in-Claude skill), so the
// shape stays deliberately renderer-neutral.

export type QuestionType = "single_select" | "multi_select" | "text" | "confirm" | "rank";

export interface QuestionOption {
  value: string;
  label: string;
  tradeoff?: string;
  // Pre-fills a later answer (keyed by question id) or the pseudo-key "warn",
  // which surfaces the downside once and then respects the choice.
  implies?: Record<string, string | number | boolean>;
}

export interface Question {
  id: string;
  act: number;
  type: QuestionType;
  prompt: string;
  why: string;
  options: QuestionOption[];
  default?: unknown;
  recommend?: unknown;
  recommend_why?: string;
  allow_defer: boolean;
  ask_if: string;
}

// The parsed file shape before normalization: `options` and `allow_defer` may be
// absent, everything else matches `Question`.
export interface RawQuestion {
  id: string;
  act: number;
  type: QuestionType;
  prompt: string;
  why: string;
  options?: QuestionOption[];
  default?: unknown;
  recommend?: unknown;
  recommend_why?: string;
  allow_defer?: boolean;
  ask_if: string;
}

export interface QuestionBankFile {
  questions: RawQuestion[];
}
