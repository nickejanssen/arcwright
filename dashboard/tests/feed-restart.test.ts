// Acceptance 3: when the engine restarts and event numbers begin again, the
// screens reread the lobby and round routes and show the new phase. The steady
// poll still works with the event stream down.

import assert from "node:assert/strict";
import test from "node:test";

import { subscribeEvents } from "../src/api/events.js";
import type { EventSignal } from "../src/api/events.js";
import { ApiError } from "../src/api/lobby.js";
import type { LobbyState } from "../src/api/lobby.js";
import type { RoundState } from "../src/api/round.js";
import { startFeed } from "../src/shell/feed.js";
import type { FeedState } from "../src/shell/feed.js";

const lobby: LobbyState = {
  session_id: "game-1",
  join_code: "K7QP",
  status: "active",
  current_beat_id: "beat_1",
  is_terminal: false,
  min_players: 2,
  player_count: 3,
  players: [],
};

function round(phase: string): RoundState {
  return {
    sessionStatus: "active",
    beatName: null,
    phase,
    status: "running",
    secondsLeft: 30,
    readyCount: 0,
    playerCount: 3,
    lines: [],
  };
}

const flush = async () => {
  for (let i = 0; i < 6; i += 1) await new Promise((r) => setTimeout(r, 0));
};

function harness(
  readLobby: () => Promise<LobbyState>,
  readRound: () => Promise<RoundState | null>,
) {
  const states: FeedState[] = [];
  let signal: (s: EventSignal) => void = () => {};
  let beat: () => void = () => {};
  const stop = startFeed({
    fetchLobby: readLobby,
    fetchRound: readRound,
    subscribe: (on) => {
      signal = on;
      return () => {};
    },
    every: (tick) => {
      beat = tick;
      return () => {};
    },
    onState: (s) => void states.push(s),
  });
  return {
    states,
    stop,
    signal: (s: EventSignal) => signal(s),
    beat: () => beat(),
    last: () => states[states.length - 1],
  };
}

test("event numbers going back to 1 make the feed reread and show the new phase", async () => {
  let phase = "scene";
  let rounds = 0;
  const h = harness(
    async () => lobby,
    async () => {
      rounds += 1;
      return round(phase);
    },
  );
  await flush();
  assert.equal(h.last().round?.phase, "scene");

  // The engine restarts into a different phase; its event numbers begin again.
  phase = "choices";
  h.signal("restart");
  await flush();
  assert.equal(h.last().round?.phase, "choices");
  assert.equal(rounds, 2, "the round route was read again");
  h.stop();
});

test("a stream reconnect rereads, and the poll still works with the stream down", async () => {
  let phase = "scene";
  const h = harness(
    async () => lobby,
    async () => round(phase),
  );
  await flush();

  phase = "bridge";
  h.signal("reconnect");
  await flush();
  assert.equal(h.last().round?.phase, "bridge");

  // No stream signal at all: only the steady beat.
  phase = "commit";
  h.beat();
  await flush();
  assert.equal(h.last().round?.phase, "commit");
  h.stop();
});

test("signals that arrive during a read ask for exactly one more read", async () => {
  let reads = 0;
  let release: () => void = () => {};
  const gate = new Promise<void>((done) => {
    release = done;
  });
  const h = harness(
    async () => {
      reads += 1;
      if (reads === 1) await gate;
      return lobby;
    },
    async () => null,
  );
  await flush();
  assert.equal(reads, 1, "first read is waiting");

  h.signal("event");
  h.signal("event");
  h.beat();
  release();
  await flush();
  assert.equal(reads, 2, "three signals during one read give one more read");
  h.stop();
});

test("a missing game is 'gone'; an unreachable engine keeps what was shown", async () => {
  let mode: "ok" | "down" | "gone" = "ok";
  const h = harness(
    async () => {
      if (mode === "down") throw new Error("network");
      if (mode === "gone") throw new ApiError("no game", 404);
      return lobby;
    },
    async () => round("scene"),
  );
  await flush();
  assert.equal(h.last().lobby?.join_code, "K7QP");

  mode = "down";
  h.beat();
  await flush();
  assert.equal(h.last().unreachable, true);
  assert.equal(h.last().gone, false);
  assert.equal(h.last().lobby?.join_code, "K7QP", "the last known room stays");

  mode = "gone";
  h.beat();
  await flush();
  assert.equal(h.last().gone, true);
  h.stop();
});

test("a failed round read does not hide the lobby", async () => {
  const h = harness(
    async () => lobby,
    async () => {
      throw new Error("round route down");
    },
  );
  await flush();
  assert.equal(h.last().lobby?.status, "active");
  assert.equal(h.last().round, null);
  h.stop();
});

test("the event stream gives reconnect, event and restart signals from event numbers alone", async () => {
  const encoder = new TextEncoder();
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      for (const n of [8, 9, 1]) {
        controller.enqueue(
          encoder.encode(
            `data: ${JSON.stringify({ sequence_number: n, payload: { secret: "x" } })}\n\n`,
          ),
        );
      }
      controller.close();
    },
  });
  const urls: string[] = [];
  const signals: EventSignal[] = [];
  const stop = subscribeEvents({
    sessionId: "game-1",
    retryMs: 60_000,
    fetcher: (async (input: RequestInfo | URL) => {
      urls.push(String(input));
      return new Response(body, { status: 200 });
    }) as typeof fetch,
    onSignal: (s) => void signals.push(s),
  });
  await flush();
  stop();

  assert.deepEqual(signals, ["reconnect", "event", "event", "restart"]);
  assert.equal(urls[0], "/v1/sessions/game-1/events?since=0");
});
