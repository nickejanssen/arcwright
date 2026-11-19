// Reads GET /v1/sessions/{id}/round (AW-325): the engine's public answer to
// "where is the game". It needs no sign-in, so the TV can read it. The screens
// show this; they never work it out.

export interface RoundState {
  sessionStatus: string;
  beatName: string | null;
  phase: string | null;
  status: "running" | "paused" | "ended" | null;
  secondsLeft: number | null;
  readyCount: number;
  playerCount: number;
  lines: Array<Record<string, unknown>>;
}

interface RoundWire {
  session_status: string;
  beat_name?: string | null;
  phase?: string | null;
  status?: "running" | "paused" | "ended" | null;
  seconds_left?: number | null;
  ready_count?: number;
  player_count?: number;
  lines?: Array<Record<string, unknown>>;
}

// A game that has not started has no round yet; the engine refuses, and the
// screens show the room instead. That is "no round", not an error.
export async function fetchRound(
  sessionId: string,
  fetcher: typeof fetch = fetch,
): Promise<RoundState | null> {
  const res = await fetcher(`/v1/sessions/${sessionId}/round`);
  if (!res.ok) return null;
  const wire = (await res.json()) as RoundWire;
  return {
    sessionStatus: wire.session_status,
    beatName: wire.beat_name ?? null,
    phase: wire.phase ?? null,
    status: wire.status ?? null,
    secondsLeft: wire.seconds_left ?? null,
    readyCount: wire.ready_count ?? 0,
    playerCount: wire.player_count ?? 0,
    lines: wire.lines ?? [],
  };
}
