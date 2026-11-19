// Performance measurement hook. Renderers call ctx.reportPerf(name, value)
// for mount-to-paint, input latency, and SSE-to-DOM-update measurements.
// AW-253 ships the client side; the receiving Arcwright endpoint lands in a
// follow-up task. Until then, the beacon attempts post-and-ignore.

export type PerfTransport = "beacon" | "none";

export interface PerfReporterOptions {
  baseUrl: string;
  sessionId: string;
  token: string;
  surface: string;
  gameId: string;
  participantId: string;
  view?: Window | null;
  transport?: PerfTransport;
}

export interface PerfReporter {
  report(name: string, value: number): void;
}

interface PerfPayload {
  session_id: string;
  game_id: string;
  surface: string;
  participant_id: string;
  metric: string;
  value: number;
  timestamp: number;
}

const ENDPOINT_PATH = "/v1/sessions";

export function createPerfReporter(opts: PerfReporterOptions): PerfReporter {
  const view = opts.view ?? (typeof window !== "undefined" ? window : null);
  const baseUrl = opts.baseUrl.replace(/\/$/, "");
  const url = `${baseUrl}${ENDPOINT_PATH}/${encodeURIComponent(opts.sessionId)}/telemetry/mini-game-perf`;

  return {
    report(name, value) {
      if (opts.transport === "none") return;
      const payload: PerfPayload = {
        session_id: opts.sessionId,
        game_id: opts.gameId,
        surface: opts.surface,
        participant_id: opts.participantId,
        metric: name,
        value,
        timestamp: Date.now(),
      };

      const navigatorRef = view?.navigator;
      if (!navigatorRef || typeof navigatorRef.sendBeacon !== "function") {
        // Perf is fire-and-forget. If sendBeacon is unavailable, silently drop
        // rather than falling back to fetch (which leaks unhandled async work
        // past a renderer's mount tick).
        return;
      }
      try {
        const blob = new Blob([JSON.stringify(payload)], {
          type: "application/json",
        });
        navigatorRef.sendBeacon(url, blob);
      } catch {
        // Sending perf must never throw.
      }
    },
  };
}
