const BASE = "/v1";

export interface LobbyPlayer {
  participant_id: string;
  display_name: string | null;
}

export interface LobbyState {
  session_id: string;
  join_code: string | null;
  status: string;
  player_count: number;
  players: LobbyPlayer[];
}

export interface LobbyJoinResult {
  participant_id: string;
  session_id: string;
  display_name: string;
  // Optional auth fields returned by the engine once player auth is active.
  // Required for ArcwrightClient initialization on the player device.
  player_token?: string;
  character_id?: string;
}

export async function fetchLobbyState(sessionId: string): Promise<LobbyState> {
  const res = await fetch(`${BASE}/sessions/${sessionId}/lobby`);
  if (!res.ok) throw new Error(`Lobby fetch failed: ${res.status}`);
  return res.json() as Promise<LobbyState>;
}

export async function joinLobby(
  name: string,
  joinCode: string,
): Promise<LobbyJoinResult> {
  const res = await fetch(`${BASE}/lobby-join`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, join_code: joinCode.toUpperCase() }),
  });
  if (res.status === 404)
    throw new Error("Invalid join code. Check the screen and try again.");
  if (!res.ok) throw new Error(`Join failed: ${res.status}`);
  return res.json() as Promise<LobbyJoinResult>;
}
