// AW-331: the seam reads this seat's role from the engine's own route. The
// screen never decides who the host is, and "Make someone else host" stays
// hidden until its follow-up task builds the name picker.

import assert from "node:assert/strict";
import test from "node:test";

import { fetchMyRole, handOverAvailable } from "../src/api/seam.js";

function fakeFetch(status: number, body: unknown) {
  const calls: { url: string; auth: string | null }[] = [];
  const fetcher = (async (url: string, init?: RequestInit) => {
    calls.push({
      url: String(url),
      auth: new Headers(init?.headers).get("Authorization"),
    });
    return new Response(JSON.stringify(body), { status });
  }) as unknown as typeof fetch;
  return { calls, fetcher };
}

test("the role is whatever the engine says for this seat", async () => {
  const host = fakeFetch(200, {
    participant_id: "p-1",
    display_name: "Ada",
    role: "host",
  });
  assert.equal(
    await fetchMyRole("game 1", async () => "tok", host.fetcher),
    "host",
  );
  assert.deepEqual(host.calls, [
    { url: "/v1/sessions/game%201/me/seat", auth: "Bearer tok" },
  ]);

  const player = fakeFetch(200, { role: "player" });
  assert.equal(
    await fetchMyRole("game-1", async () => "tok", player.fetcher),
    "player",
  );
});

test("an answer the screen does not understand never makes a host", async () => {
  const odd = fakeFetch(200, { role: "admin" });
  assert.equal(
    await fetchMyRole("game-1", async () => "tok", odd.fetcher),
    "player",
  );
  const empty = fakeFetch(200, {});
  assert.equal(
    await fetchMyRole("game-1", async () => "tok", empty.fetcher),
    "player",
  );
});

test("when the engine refuses or fails, the seat is a player", async () => {
  for (const status of [401, 403, 404, 500]) {
    const refused = fakeFetch(status, { detail: "no" });
    assert.equal(
      await fetchMyRole("game-1", async () => "tok", refused.fetcher),
      "player",
      `status ${status}`,
    );
  }
});

test("the hand-over choice stays hidden until its own task builds it", () => {
  assert.equal(handOverAvailable(), false);
});
