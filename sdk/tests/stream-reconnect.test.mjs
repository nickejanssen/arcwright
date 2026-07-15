// Verifies ArcwrightClient's single-reconnect-attempt behavior applies
// uniformly to every way the SSE event stream can end unexpectedly: a
// fetch() network failure, a non-OK response, and a clean stream close.
// Runs against the built dist/index.js (npm run build first).

import assert from "node:assert/strict";
import test from "node:test";

import { ArcwrightClient } from "../dist/index.js";

const encoder = new TextEncoder();

function sseBodyFromEvents(events) {
  const lines = events.map((e) => `data: ${JSON.stringify(e)}\n\n`).join("");
  const bytes = encoder.encode(lines);
  let sent = false;
  return {
    getReader() {
      return {
        async read() {
          if (sent) return { done: true, value: undefined };
          sent = true;
          return { done: false, value: bytes };
        },
        async cancel() {},
      };
    },
  };
}

function okResponse(events) {
  return { ok: true, status: 200, body: sseBodyFromEvents(events) };
}

function makeClient() {
  return new ArcwrightClient(
    "session-1",
    "player-token",
    "character-1",
    "https://example.test",
  );
}

test("reconnects once after a fetch() network failure, then stops", async () => {
  let calls = 0;
  globalThis.fetch = async () => {
    calls += 1;
    if (calls === 1) throw new TypeError("network error");
    // Second call (the single reconnect) also fails.
    throw new TypeError("network error");
  };

  const client = makeClient();
  const received = [];
  client.onEvent((event) => received.push(event));

  // Let the fire-and-forget stream loop run to completion.
  await new Promise((resolve) => setTimeout(resolve, 20));

  assert.equal(calls, 2, "initial attempt plus exactly one reconnect");
  assert.deepEqual(received, []);
});

test("reconnects once after a non-OK response, then stops", async () => {
  let calls = 0;
  globalThis.fetch = async () => {
    calls += 1;
    return { ok: false, status: 500, body: null };
  };

  const client = makeClient();
  client.onEvent(() => {});

  await new Promise((resolve) => setTimeout(resolve, 20));

  assert.equal(calls, 2, "initial attempt plus exactly one reconnect");
});

test("delivers events, then reconnects once after a clean stream close", async () => {
  let calls = 0;
  globalThis.fetch = async () => {
    calls += 1;
    if (calls === 1) {
      return okResponse([
        {
          event_id: "e1",
          session_id: "session-1",
          sequence_number: 1,
          category: "narrative",
          event_type: "narrator_bridge",
          target_audience: "all",
          payload: { text: "hello" },
          presentation_hints: {},
        },
      ]);
    }
    // Second call (the single reconnect): stream ends immediately with no
    // further events; loop should stop after this without a third call.
    return okResponse([]);
  };

  const client = makeClient();
  const received = [];
  client.onEvent((event) => received.push(event));

  await new Promise((resolve) => setTimeout(resolve, 20));

  assert.equal(calls, 2, "initial connection plus exactly one reconnect");
  assert.equal(received.length, 1);
  assert.equal(received[0].event_id, "e1");
});

test("a fetch failure on the reconnect attempt still stops after exactly one retry", async () => {
  let calls = 0;
  globalThis.fetch = async () => {
    calls += 1;
    if (calls === 1) return { ok: false, status: 503, body: null };
    throw new TypeError("network error");
  };

  const client = makeClient();
  client.onEvent(() => {});

  await new Promise((resolve) => setTimeout(resolve, 20));

  assert.equal(calls, 2, "mixed failure modes still cap at one reconnect");
});
