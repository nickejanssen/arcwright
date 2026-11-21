// How the story's lines are paced on the TV. Each line carries the pause its
// author wrote before it; between two lines the TV waits at least a short
// floor, so a line never flashes past. The values live here so they can be
// tuned at the TV run. Voice, emotion and lighting hints are carried by the
// engine and ignored in session 1 (no audio, spec 0095 decision 8).

import { useEffect, useRef, useState } from "react";

export interface StageLine {
  text: string;
  speaker: string | null;
  pauseBeforeMs: number;
}

// The shortest wait between one line and the next.
export const LINE_FLOOR_MS = 2000;

export function readLines(raw: Array<Record<string, unknown>>): StageLine[] {
  const lines: StageLine[] = [];
  for (const line of raw) {
    if (typeof line.text !== "string" || line.text === "") continue;
    const hints = (line.hints ?? {}) as { pause_before_ms?: unknown };
    lines.push({
      text: line.text,
      speaker:
        typeof line.speaker === "string" && line.speaker !== ""
          ? line.speaker
          : null,
      pauseBeforeMs:
        typeof hints.pause_before_ms === "number" ? hints.pause_before_ms : 0,
    });
  }
  return lines;
}

// When each line appears, in milliseconds after the phase begins: the first
// after its own pause, each later one after its pause or the floor, whichever
// is longer.
export function scheduleLines(
  lines: StageLine[],
  floorMs: number = LINE_FLOOR_MS,
): number[] {
  const at: number[] = [];
  lines.forEach((line, i) => {
    at.push(
      i === 0
        ? line.pauseBeforeMs
        : at[i - 1] + Math.max(line.pauseBeforeMs, floorMs),
    );
  });
  return at;
}

// The phone's "Reduce motion" setting is on the page's root element; the TV has
// none, so it follows the browser's own setting.
export function prefersReducedMotion(): boolean {
  try {
    if (
      document.documentElement.getAttribute("data-reduce-motion") === "always"
    ) {
      return true;
    }
    return Boolean(
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches,
    );
  } catch {
    return false;
  }
}

// The lines to show now. Every line shows at once under reduced motion; a
// reload of the TV starts the staging again. `phaseKey` names this showing of
// these lines, so a new phase starts afresh and a re-read of the same one does
// not.
export function useStagedLines(
  lines: StageLine[],
  phaseKey: string,
): StageLine[] {
  const linesRef = useRef(lines);
  linesRef.current = lines;

  function startCount(): number {
    if (prefersReducedMotion()) return lines.length;
    return scheduleLines(lines).filter((t) => t <= 0).length;
  }

  const [count, setCount] = useState<number>(startCount);

  useEffect(() => {
    const all = linesRef.current;
    if (prefersReducedMotion()) {
      setCount(all.length);
      return undefined;
    }
    const at = scheduleLines(all);
    setCount(at.filter((t) => t <= 0).length);
    const timers = at
      .map((t, i) => ({ t, n: i + 1 }))
      .filter((step) => step.t > 0)
      .map((step) => setTimeout(() => setCount(step.n), step.t));
    return () => timers.forEach(clearTimeout);
  }, [phaseKey]);

  return lines.slice(0, count);
}
