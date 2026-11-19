// Spec 0095 decision 6: the TV never holds a sign-in. The TV page reads no
// storage and sends no Authorization header, and a host sign-in left in an old
// rehearsal link is removed from the address bar and ignored.

import assert from "node:assert/strict";
import test from "node:test";

import { createElement } from "react";
import { mount, setUrl } from "./helpers/dom.js";
import DisplayScreen from "../src/screens/DisplayScreen.js";

const lobbyBody = {
  session_id: "game-1",
  join_code: "K7QP",
  status: "created",
  current_beat_id: "beat_internal_1",
  is_terminal: false,
  min_players: 2,
  player_count: 1,
  players: [{ participant_id: "p-1", display_name: "Jordan" }],
};

test("the TV page reads no storage, sends no Authorization, and scrubs a host token from the address", async () => {
  setUrl("https://tv.test/display/game-1?x=1#host_token=SECRET-CUSTOM-TOKEN");

  // Any touch of storage fails the test.
  const globals = globalThis as Record<string, unknown>;
  const blocked = new Proxy(
    {},
    {
      get() {
        throw new Error("the TV page touched storage");
      },
    },
  );
  const savedLocal = Object.getOwnPropertyDescriptor(globals, "localStorage");
  const savedSession = Object.getOwnPropertyDescriptor(
    globals,
    "sessionStorage",
  );
  Object.defineProperty(globals, "localStorage", {
    value: blocked,
    configurable: true,
  });
  Object.defineProperty(globals, "sessionStorage", {
    value: blocked,
    configurable: true,
  });

  const seen: Array<{ url: string; headers: unknown }> = [];
  const realFetch = globals.fetch;
  globals.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    seen.push({ url: String(input), headers: init?.headers });
    const url = String(input);
    if (url.endsWith("/lobby")) {
      return new Response(JSON.stringify(lobbyBody), { status: 200 });
    }
    if (url.includes("/events?")) {
      return new Response(new ReadableStream<Uint8Array>({ start() {} }), {
        status: 200,
      });
    }
    return new Response("no", { status: 404 });
  };

  try {
    const page = await mount(
      createElement(DisplayScreen, { sessionId: "game-1" }),
    );

    assert.ok(page.text().includes("K7QP"), "the room code is shown");
    assert.ok(seen.length > 0, "the page did read the engine");
    for (const call of seen) {
      const headers = JSON.stringify(call.headers ?? {}).toLowerCase();
      assert.ok(
        !headers.includes("authorization"),
        `${call.url} sent an Authorization header`,
      );
    }
    assert.ok(
      !window.location.hash.includes("host_token"),
      "the host token is gone from the address bar",
    );
    assert.equal(
      window.location.search,
      "?x=1",
      "the rest of the address stays",
    );
    assert.ok(
      !page.text().includes("SECRET-CUSTOM-TOKEN"),
      "the token is never drawn",
    );
    assert.equal(
      page.buttons().length,
      0,
      "the TV has no controls, not even for a host",
    );
    await page.unmount();
  } finally {
    globals.fetch = realFetch;
    for (const [name, saved] of [
      ["localStorage", savedLocal],
      ["sessionStorage", savedSession],
    ] as const) {
      if (saved) Object.defineProperty(globals, name, saved);
      else delete globals[name];
    }
  }
});
