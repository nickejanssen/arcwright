const BASE = "/v1";

export interface LobbyPlayer {
  participant_id: string;
  character_id: string;
  display_name: string | null;
}

export interface LobbyState {
  session_id: string;
  join_code: string | null;
  status: string;
  current_beat_id: string;
  is_terminal: boolean;
  min_players: number;
  player_count: number;
  players: LobbyPlayer[];
}

export interface LobbyJoinResult {
  participant_id: string;
  session_id: string;
  display_name: string;
  character_id: string;
  player_token: string;
}

// An answer from the engine with a status the screens can act on.
export class ApiError extends Error {
  readonly status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

// Why a join was refused. The words for each live in shell/copy.ts.
export type JoinFailure = "bad_code" | "started" | "failed";

export class JoinError extends Error {
  readonly failure: JoinFailure;
  constructor(failure: JoinFailure, status: number) {
    super(`Join failed: ${status}`);
    this.name = "JoinError";
    this.failure = failure;
  }
}

export async function fetchLobbyState(
  sessionId: string,
  fetcher: typeof fetch = fetch,
): Promise<LobbyState> {
  const res = await fetcher(`${BASE}/sessions/${sessionId}/lobby`);
  if (!res.ok) {
    throw new ApiError(`Lobby fetch failed: ${res.status}`, res.status);
  }
  return res.json() as Promise<LobbyState>;
}

export async function joinLobby(
  name: string,
  joinCode: string,
  fetcher: typeof fetch = fetch,
): Promise<LobbyJoinResult> {
  const res = await fetcher(`${BASE}/lobby-join`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, join_code: joinCode.toUpperCase() }),
  });
  if (res.status === 404) throw new JoinError("bad_code", 404);
  // Today the engine answers 409 for a finished game; AW-331 adds the rule
  // for a game that has started. The screen treats every 409 the same way.
  if (res.status === 409) throw new JoinError("started", 409);
  if (!res.ok) throw new JoinError("failed", res.status);
  return res.json() as Promise<LobbyJoinResult>;
}
