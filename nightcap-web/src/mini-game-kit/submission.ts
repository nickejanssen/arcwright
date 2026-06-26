// Single-flight submission guard. Prevents double-tap from posting twice,
// stable submission IDs are generated locally so retries are idempotent on
// the engine side, and the renderer never has to track in-flight state.

import type { MiniGamePayload, MiniGameSubmissionResult } from "../types.js";

export interface SubmissionGuardOptions {
  submit(
    submissionId: string,
    payload: MiniGamePayload,
  ): Promise<MiniGameSubmissionResult>;
  generateSubmissionId?: () => string;
}

export interface SubmissionGuard {
  submit(payload: MiniGamePayload): Promise<MiniGameSubmissionResult | null>;
  isPending(): boolean;
  hasSubmitted(): boolean;
  reset(): void;
}

function fallbackSubmissionId(): string {
  // Workers and modern browsers expose crypto.randomUUID. Fallback covers
  // happy-dom environments without crypto.
  const cryptoGlobal = (
    globalThis as { crypto?: { randomUUID?: () => string } }
  ).crypto;
  if (cryptoGlobal && typeof cryptoGlobal.randomUUID === "function") {
    return cryptoGlobal.randomUUID();
  }
  // RFC 4122 v4 stub; sufficient for non-cryptographic deduplication.
  let value = "";
  for (let i = 0; i < 32; i++) {
    if (i === 8 || i === 12 || i === 16 || i === 20) value += "-";
    const r = Math.floor(Math.random() * 16);
    value += r.toString(16);
  }
  return value;
}

export function createSubmissionGuard(
  opts: SubmissionGuardOptions,
): SubmissionGuard {
  const generate = opts.generateSubmissionId ?? fallbackSubmissionId;
  let pending = false;
  let submitted = false;

  return {
    async submit(payload) {
      if (pending || submitted) return null;
      pending = true;
      try {
        const result = await opts.submit(generate(), payload);
        if (result.isAccepted) {
          submitted = true;
        }
        return result;
      } finally {
        pending = false;
      }
    },
    isPending: () => pending,
    hasSubmitted: () => submitted,
    reset: () => {
      pending = false;
      submitted = false;
    },
  };
}
