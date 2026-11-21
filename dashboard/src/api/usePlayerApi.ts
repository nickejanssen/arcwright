import { useMemo, useRef } from "react";
import { createPlayerApi } from "./player";
import type { PlayerApi } from "./player";

// One player API for this screen's lifetime. The sign-in is read when a call is
// made, so a refreshed sign-in is always the one used.
export function usePlayerApi(
  sessionId: string,
  getToken: (() => Promise<string>) | undefined,
): PlayerApi {
  const latest = useRef(getToken);
  latest.current = getToken;
  return useMemo(
    () =>
      createPlayerApi(sessionId, async () => {
        const get = latest.current;
        if (!get) throw new Error("This screen has no sign-in.");
        return get();
      }),
    [sessionId],
  );
}
