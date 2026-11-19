// Keeps a screen current. It reads the lobby and round routes when asked, when
// the event stream signals, and on a steady poll, so a stream that is down or a
// restarted engine never leaves a screen stale. It decides nothing.

import type { EventSignal } from "../api/events";
import { ApiError } from "../api/lobby";
import type { LobbyState } from "../api/lobby";
import type { RoundState } from "../api/round";

export interface FeedState {
  lobby: LobbyState | null;
  round: RoundState | null;
  // The engine could not be reached (it may be starting again).
  unreachable: boolean;
  // The engine answered that this game does not exist.
  gone: boolean;
}

export const INITIAL_FEED: FeedState = {
  lobby: null,
  round: null,
  unreachable: false,
  gone: false,
};

export interface FeedDeps {
  fetchLobby(): Promise<LobbyState>;
  fetchRound(): Promise<RoundState | null>;
  subscribe(onSignal: (signal: EventSignal) => void): () => void;
  // Runs `tick` on a steady beat and returns a function that stops it.
  every(tick: () => void): () => void;
  onState(state: FeedState): void;
}

export function startFeed(deps: FeedDeps): () => void {
  let stopped = false;
  let reading = false;
  let again = false;
  let state = INITIAL_FEED;

  function publish(next: FeedState): void {
    state = next;
    if (!stopped) deps.onState(state);
  }

  async function read(): Promise<void> {
    // One read at a time; a signal that arrives mid-read asks for one more.
    if (reading) {
      again = true;
      return;
    }
    reading = true;
    try {
      do {
        again = false;
        try {
          const lobby = await deps.fetchLobby();
          const round = await deps.fetchRound().catch(() => null);
          publish({ lobby, round, unreachable: false, gone: false });
        } catch (error) {
          const gone = error instanceof ApiError && error.status === 404;
          publish({
            ...state,
            unreachable: !gone,
            gone,
          });
        }
      } while (again && !stopped);
    } finally {
      reading = false;
    }
  }

  void read();
  const stopSignals = deps.subscribe(() => void read());
  const stopBeat = deps.every(() => void read());
  return () => {
    stopped = true;
    stopSignals();
    stopBeat();
  };
}
