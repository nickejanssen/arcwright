// Reads GET /v1/sessions/{id}/room (AW-331): the engine's public answer to
// "where is the game". It needs no sign-in, so the TV can read it, and it
// carries the round's title, the phase and its entry number, the clock, the
// lines and each seated player's ready flag. The screens show this; they never
// work it out.

export interface RoundPlayer {
  // Used to tell which seat is this phone's. It is never shown.
  participantId: string;
  name: string | null;
  ready: boolean;
}

export interface RoundState {
  sessionStatus: string;
  // The round's title, written by the case author (the beat's name).
  beatName: string | null;
  phase: string | null;
  // The number of this visit to the phase; ready names it so a stale tap
  // changes nothing.
  phaseEntry: number | null;
  status: "running" | "paused" | "ended" | null;
  secondsLeft: number | null;
  readyCount: number;
  playerCount: number;
  players: RoundPlayer[];
  lines: Array<Record<string, unknown>>;
}

interface RoomWire {
  session_status: string;
  round_title?: string | null;
  phase?: string | null;
  phase_entry?: number | null;
  seconds_left?: number | null;
  paused?: boolean;
  over?: boolean;
  ready_count?: number;
  player_count?: number;
  players?: Array<{
    participant_id: string;
    display_name?: string | null;
    ready?: boolean;
  }>;
  lines?: Array<Record<string, unknown>>;
}

// The room view says whether the game is over or paused; the screens' table
// reads one status word, so the flags become it here.
function statusOf(wire: RoomWire): RoundState["status"] {
  if (wire.over) return "ended";
  if (wire.paused) return "paused";
  return wire.phase ? "running" : null;
}

// An unknown game is "no round", not an error: the lobby read reports it.
export async function fetchRound(
  sessionId: string,
  fetcher: typeof fetch = fetch,
): Promise<RoundState | null> {
  const res = await fetcher(`/v1/sessions/${sessionId}/room`);
  if (!res.ok) return null;
  const wire = (await res.json()) as RoomWire;
  return {
    sessionStatus: wire.session_status,
    beatName: wire.round_title ?? null,
    phase: wire.phase ?? null,
    phaseEntry: wire.phase_entry ?? null,
    status: statusOf(wire),
    secondsLeft: wire.seconds_left ?? null,
    readyCount: wire.ready_count ?? 0,
    playerCount: wire.player_count ?? 0,
    players: (wire.players ?? []).map((p) => ({
      participantId: p.participant_id,
      name: p.display_name ?? null,
      ready: Boolean(p.ready),
    })),
    lines: wire.lines ?? [],
  };
}
