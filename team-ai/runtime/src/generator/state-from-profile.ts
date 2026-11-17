// Deterministic. No model calls. No network. No disk I/O.
//
// Reconstruct an interview `EngineState` from a saved `team-profile.yaml`. The
// profile is only written after all three gates are confirmed, so a profile
// always reconstructs to a complete interview: every recorded answer becomes an
// `answers` entry, all three gates are confirmed, and `phase` is `done`.
// `derived` starts empty and is recomputed lazily as `resume` re-answers.

import type { AnswerRecord, EngineState } from "../interview/engine.js";
import type { Question } from "../interview/types.js";

export interface ProfileShape {
  answers: Record<string, unknown>;
  deferred: { question: string; applied_default?: unknown; revisit?: string }[];
}

export function stateFromProfile(bank: Question[], profile: ProfileShape): EngineState {
  const deferredIds = new Set(
    (profile.deferred ?? [])
      .map((entry) => entry.question)
      .filter((id): id is string => typeof id === "string"),
  );

  const answers: Record<string, AnswerRecord> = {};
  const profileAnswers = profile.answers ?? {};
  for (const [id, value] of Object.entries(profileAnswers)) {
    answers[id] = { value, via: deferredIds.has(id) ? "defer" : "direct" };
  }

  const history = bank.map((q) => q.id).filter((id) => id in answers);

  return {
    answers,
    derived: {},
    history,
    confirmedGates: [1, 2, 3],
    phase: "done",
  };
}
