import { useEffect, useState } from "react";
import { subscribeEvents } from "../api/events";
import { fetchLobbyState } from "../api/lobby";
import { fetchRound } from "../api/round";
import { INITIAL_FEED, startFeed } from "./feed";
import type { FeedState } from "./feed";

const POLL_MS = 2000;

export function useFeed(sessionId: string): FeedState {
  const [state, setState] = useState<FeedState>(INITIAL_FEED);

  useEffect(() => {
    setState(INITIAL_FEED);
    return startFeed({
      fetchLobby: () => fetchLobbyState(sessionId),
      fetchRound: () => fetchRound(sessionId),
      subscribe: (onSignal) => subscribeEvents({ sessionId, onSignal }),
      every: (tick) => {
        const timer = setInterval(tick, POLL_MS);
        return () => clearInterval(timer);
      },
      onState: setState,
    });
  }, [sessionId]);

  return state;
}
