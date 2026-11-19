// AW-329: the React wrapper mounts a stage through the loader and cleans up
// when it leaves the page. Uses happy-dom for a DOM and react-dom's own client;
// no browser.

import assert from "node:assert/strict";
import test from "node:test";
import { Window as HappyWindow } from "happy-dom";

import { defineRenderer } from "../src/mini-game-kit/index.js";
import type { MiniGameDefinition } from "../src/mini-game-kit/index.js";
import { RendererRegistry } from "../src/mini-games/registry.js";

const happy = new HappyWindow();
const globals = globalThis as Record<string, unknown>;
for (const name of ["window", "document", "HTMLElement", "Node"]) {
  globals[name] = (happy as unknown as Record<string, unknown>)[name];
}
globals.IS_REACT_ACT_ENVIRONMENT = true;

const { act, createElement } = await import("react");
const { createRoot } = await import("react-dom/client");
const { MiniGameStage } = await import("../src/mini-games/MiniGameStage.js");

const definition = { game_id: "fixture-game" } as unknown as MiniGameDefinition;

function fakeServer(): typeof fetch {
  return (async (input: RequestInfo | URL): Promise<Response> => {
    const url = String(input);
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
      return new Response(
        new ReadableStream<Uint8Array>({ start: (c) => c.close() }),
        { status: 200 },
      );
    }
    return new Response("not found", { status: 404 });
  }) as typeof fetch;
}

test("MiniGameStage mounts the registered renderer and unmounts it on leave", async () => {
  const registry = new RendererRegistry();
  registry.register(
    defineRenderer({
      gameId: "fixture-game",
      sharedDisplay: {
        mount(root) {
          root.setAttribute("data-fixture", "mounted");
          return {
            update() {},
            handleEvent() {},
            unmount() {
              root.removeAttribute("data-fixture");
            },
          };
        },
      },
    } as Parameters<typeof defineRenderer>[0]),
  );
  const host = happy.document.createElement("div");
  happy.document.body.appendChild(host);
  const root = createRoot(host as unknown as HTMLElement);

  await act(async () => {
    root.render(
      createElement(MiniGameStage, {
        surface: "shared_display",
        sessionId: "session-1",
        participantId: "p-1",
        characterId: "c-1",
        token: "token-x",
        baseUrl: "https://arcwright.test",
        registry,
        loadDefinition: async () => definition,
        fetcher: fakeServer(),
      }),
    );
    await new Promise((done) => setTimeout(done, 50));
  });

  const stage = host.querySelector("[data-mini-game-stage]");
  assert.ok(stage, "a stage section is drawn");
  assert.equal(stage.getAttribute("data-surface"), "shared_display");
  assert.equal(
    stage.getAttribute("data-mini-game-state"),
    "active:fixture-game",
  );
  assert.equal(stage.getAttribute("data-fixture"), "mounted");

  await act(async () => {
    root.unmount();
  });
  assert.equal(host.querySelector("[data-mini-game-stage]"), null);
});
