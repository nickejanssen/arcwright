// AW-330 (orchestrator finding 3): the display surface holds no sign-in, so the
// loader sends no Authorization header there and reads the public display
// route. With a token it behaves as before.

import assert from "node:assert/strict";
import test from "node:test";
import { Window as HappyWindow } from "happy-dom";

import { defineRenderer } from "../src/mini-game-kit/index.js";
import type { MiniGameDefinition } from "../src/mini-game-kit/index.js";
import { bootMiniGameStage } from "../src/mini-games/client.js";
import { RendererRegistry } from "../src/mini-games/registry.js";

const definition = { game_id: "fixture-game" } as unknown as MiniGameDefinition;

function recordingServer(seen: Array<{ url: string; headers: unknown }>) {
  return (async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    seen.push({ url, headers: init?.headers });
    if (url.includes("/mini-games/active")) {
      return new Response(
        JSON.stringify({
          run_id: "run-1",
          game_id: "fixture-game",
          definition_version: "0.1.0",
          status: "active",
          deadline_at: null,
          my_submissions: [],
        }),
        { status: 200 },
      );
    }
    if (url.includes("/events?since=")) {
      return new Response(new ReadableStream<Uint8Array>({ start() {} }), {
        status: 200,
      });
    }
    return new Response("no", { status: 404 });
  }) as typeof fetch;
}

async function boot(token: string | undefined) {
  const window = new HappyWindow();
  const stage = window.document.createElement("div") as unknown as HTMLElement;
  const registry = new RendererRegistry();
  registry.register(
    defineRenderer({
      gameId: "fixture-game",
      sharedDisplay: {
        mount() {
          return { update() {}, handleEvent() {}, unmount() {} };
        },
      },
    }),
  );
  const seen: Array<{ url: string; headers: unknown }> = [];
  const controller = await bootMiniGameStage(stage, {
    registry,
    baseUrl: "https://arcwright.test",
    sessionId: "game-1",
    ...(token ? { token } : {}),
    surface: "shared_display",
    participantId: "display",
    characterId: "",
    loadDefinition: async () => definition,
    view: window as unknown as Window,
    fetcher: recordingServer(seen),
    perfTransport: "none",
  });
  return { stage, seen, controller };
}

test("with no token the loader reads the public display route and sends no Authorization", async () => {
  const { stage, seen, controller } = await boot(undefined);

  assert.equal(
    stage.getAttribute("data-mini-game-state"),
    "active:fixture-game",
  );
  assert.ok(
    seen.some((c) => c.url.endsWith("/mini-games/active/display")),
    "reads the display route",
  );
  assert.ok(seen.some((c) => c.url.includes("/events?since=")));
  for (const call of seen) {
    assert.ok(
      !JSON.stringify(call.headers ?? {})
        .toLowerCase()
        .includes("authorization"),
      `${call.url} sent a sign-in`,
    );
  }
  controller.unmount();
});

test("with a token the loader still reads the player route and sends it", async () => {
  const { seen, controller } = await boot("token-x");

  const stateCall = seen.find((c) => c.url.includes("/mini-games/active"));
  assert.ok(stateCall && !stateCall.url.endsWith("/display"));
  assert.deepEqual(stateCall.headers, { Authorization: "Bearer token-x" });
  controller.unmount();
});
