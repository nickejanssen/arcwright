// Deadline-anchored countdown. Reads the system clock each frame instead of
// counting down an interval, so reconnect, tab-switch, and clock drift do not
// desync the displayed time. The engine remains the time authority; this is
// display only.

import { prefersReducedMotion } from "./dom.js";

export interface CountdownOptions {
  deadlineAt: string | null;
  onTick: (remainingMs: number) => void;
  onExpire?: () => void;
  view?: Window | null;
  now?: () => number;
}

export interface CountdownHandle {
  cancel(): void;
}

const NOOP: CountdownHandle = { cancel: () => {} };

export function useCountdown(opts: CountdownOptions): CountdownHandle {
  const view = opts.view ?? (typeof window !== "undefined" ? window : null);
  if (!view || opts.deadlineAt === null) {
    opts.onTick(0);
    return NOOP;
  }

  const deadlineMs = Date.parse(opts.deadlineAt);
  if (!Number.isFinite(deadlineMs)) {
    opts.onTick(0);
    return NOOP;
  }

  const now = opts.now ?? (() => Date.now());
  const reduced = prefersReducedMotion(view);
  let cancelled = false;
  let expired = false;
  let timerHandle: ReturnType<typeof setTimeout> | null = null;
  let rafHandle: number | null = null;

  const tick = (): void => {
    if (cancelled) return;
    const remaining = Math.max(0, deadlineMs - now());
    opts.onTick(remaining);
    if (remaining <= 0) {
      if (!expired) {
        expired = true;
        opts.onExpire?.();
      }
      return;
    }
    schedule();
  };

  const schedule = (): void => {
    if (reduced) {
      timerHandle = setTimeout(tick, 1000);
      return;
    }
    if (typeof view.requestAnimationFrame === "function") {
      rafHandle = view.requestAnimationFrame(tick);
      return;
    }
    timerHandle = setTimeout(tick, 16);
  };

  tick();

  return {
    cancel: () => {
      cancelled = true;
      if (
        rafHandle !== null &&
        typeof view.cancelAnimationFrame === "function"
      ) {
        view.cancelAnimationFrame(rafHandle);
        rafHandle = null;
      }
      if (timerHandle !== null) {
        clearTimeout(timerHandle);
        timerHandle = null;
      }
    },
  };
}

export function formatRemaining(remainingMs: number): string {
  const totalSeconds = Math.max(0, Math.ceil(remainingMs / 1000));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}
