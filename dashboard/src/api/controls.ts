// The Start menu's actions. Each one is a single call to an existing engine
// route; the engine decides whether it is allowed and what follows. Nothing
// here knows a game rule.

import { ApiError } from "./lobby";

export interface Controls {
  start(): Promise<void>;
  pause(): Promise<void>;
  resume(): Promise<void>;
  moveOn(): Promise<void>;
  end(): Promise<void>;
  resolveMiniGame(): Promise<void>;
  cancelMiniGame(): Promise<void>;
}

export function createControls(
  sessionId: string,
  getToken: () => Promise<string>,
  fetcher: typeof fetch = fetch,
): Controls {
  const base = `/v1/sessions/${encodeURIComponent(sessionId)}`;

  async function post(path: string, body?: unknown): Promise<Response> {
    const token = await getToken();
    const res = await fetcher(`${base}${path}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    if (!res.ok)
      throw new ApiError(`Request failed: ${res.status}`, res.status);
    return res;
  }

  // The running mini-game's run is public on the display route.
  async function activeRunId(): Promise<string> {
    const res = await fetcher(`${base}/mini-games/active/display`);
    if (!res.ok) throw new ApiError("No mini-game is running.", res.status);
    return ((await res.json()) as { run_id: string }).run_id;
  }

  async function hostCommand(command: "resolve" | "cancel"): Promise<void> {
    const runId = await activeRunId();
    await post(`/mini-games/${encodeURIComponent(runId)}/host-commands`, {
      command,
    });
  }

  return {
    start: async () => void (await post("/start")),
    pause: async () => void (await post("/pause")),
    resume: async () => void (await post("/resume")),
    moveOn: async () => void (await post("/round/move-on")),
    end: async () => void (await post("/end")),
    resolveMiniGame: () => hostCommand("resolve"),
    cancelMiniGame: () => hostCommand("cancel"),
  };
}
