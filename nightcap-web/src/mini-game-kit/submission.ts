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
  // Submission IDs are the engine's idempotency key. Prefer crypto.randomUUID
  // when available, fall through to crypto.getRandomValues + RFC 4122 v4
  // formatting, and only as a last resort use Math.random (very unlikely
  // path: a browser without Web Crypto).
  const cryptoGlobal = (
    globalThis as {
      crypto?: {
        randomUUID?: () => string;
        getRandomValues?: <T extends ArrayBufferView>(array: T) => T;
      };
    }
  ).crypto;
  if (cryptoGlobal?.randomUUID) {
    return cryptoGlobal.randomUUID();
  }
  if (cryptoGlobal?.getRandomValues) {
    const bytes = new Uint8Array(16);
    cryptoGlobal.getRandomValues(bytes);
    // RFC 4122 v4: set version (4) and variant (10x) bits.
    bytes[6] = ((bytes[6] ?? 0) & 0x0f) | 0x40;
    bytes[8] = ((bytes[8] ?? 0) & 0x3f) | 0x80;
    const hex = Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join(
      "",
    );
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
  }
  // Math.random last resort. Not collision-resistant under adversarial
  // conditions, but acceptable as a deduplication key when the engine also
  // validates submissions server-side.
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
