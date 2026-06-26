import assert from "node:assert/strict";
import test from "node:test";

import { useCountdown, formatRemaining } from "../src/mini-game-kit/index.js";

function makeFakeView(now: () => number, reducedMotion = false) {
  const view = {
    requestAnimationFrame(_cb: FrameRequestCallback): number {
      void _cb;
      return 0;
    },
    cancelAnimationFrame(_handle: number): void {
      void _handle;
    },
    matchMedia(query: string) {
      return {
        matches: reducedMotion && query === "(prefers-reduced-motion: reduce)",
        addEventListener: () => {},
        removeEventListener: () => {},
      };
    },
    setTimeout: setTimeout.bind(globalThis),
    clearTimeout: clearTimeout.bind(globalThis),
  };
  return { view, now };
}

test("countdown: emits initial tick with remaining ms", () => {
  let received: number | null = null;
  const fakeNow = 1_000;
  const { view, now } = makeFakeView(() => fakeNow);
  const handle = useCountdown({
    deadlineAt: new Date(fakeNow + 30_000).toISOString(),
    onTick: (ms) => {
      received = ms;
    },
    view: view as unknown as Window,
    now,
  });
  handle.cancel();
  assert.equal(received, 30_000);
});

test("countdown: null deadline emits 0 and is inert", () => {
  let received: number | null = null;
  const handle = useCountdown({
    deadlineAt: null,
    onTick: (ms) => {
      received = ms;
    },
  });
  handle.cancel();
  assert.equal(received, 0);
});

test("countdown: invalid deadline emits 0", () => {
  let received: number | null = null;
  const handle = useCountdown({
    deadlineAt: "not-a-date",
    onTick: (ms) => {
      received = ms;
    },
  });
  handle.cancel();
  assert.equal(received, 0);
});

test("countdown: cancel stops further ticks", () => {
  let count = 0;
  let fakeNow = 0;
  const { view } = makeFakeView(() => fakeNow);
  const handle = useCountdown({
    deadlineAt: new Date(fakeNow + 100_000).toISOString(),
    onTick: () => {
      count += 1;
    },
    view: view as unknown as Window,
    now: () => fakeNow,
  });
  handle.cancel();
  fakeNow = 200_000;
  // No further ticks should be observed; the rAF scheduler stub doesn't
  // actually fire, so count stays at the initial tick.
  assert.equal(count, 1);
});

test("formatRemaining: M:SS padded", () => {
  assert.equal(formatRemaining(75_000), "1:15");
  assert.equal(formatRemaining(5_000), "0:05");
  assert.equal(formatRemaining(0), "0:00");
  assert.equal(formatRemaining(-1000), "0:00");
});
