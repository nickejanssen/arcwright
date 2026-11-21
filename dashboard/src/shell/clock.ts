// A clock for the screens. The engine's seconds are the truth; between two
// reads the screen counts down on its own so the clock moves each second, and
// it takes the engine's number again whenever one arrives. Nothing here is a
// game rule.

import { useEffect, useState } from "react";

export function formatClock(seconds: number): string {
  const whole = Math.max(0, Math.floor(seconds));
  const minutes = Math.floor(whole / 60);
  const rest = String(whole % 60).padStart(2, "0");
  return `${minutes}:${rest}`;
}

// The seconds to show now: the engine's number, counted down once a second
// until the next one arrives. A paused or absent clock does not move.
export function useCountdown(
  seconds: number | null,
  running: boolean,
): number | null {
  const [shown, setShown] = useState<number | null>(seconds);

  useEffect(() => {
    setShown(seconds);
    if (seconds === null || !running) return undefined;
    const timer = setInterval(() => {
      setShown((s) => (s === null ? null : Math.max(0, s - 1)));
    }, 1000);
    return () => clearInterval(timer);
  }, [seconds, running]);

  return shown;
}
