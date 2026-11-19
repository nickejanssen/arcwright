// AW-329: the dashboard mounts a mini-game package's own renderer by game ID
// through the copied loader. The renderer under test is the real Tell Me
// Something True package renderer, not a stand-in, and the fake server answers
// in the shape the engine's API sends (api/schemas MiniGameRunResponse).

import assert from "node:assert/strict";
import test from "node:test";
import { Window as HappyWindow } from "happy-dom";

import tmstRenderer from "../../nightcap/mini_games/tell-me-something-true/client/renderer.ts";
import tmstDefinition from "../../nightcap/mini_games/tell-me-something-true/definitions/0.1.0.json";
import { bootMiniGameStage } from "../src/mini-games/client.js";
import { RendererRegistry } from "../src/mini-games/registry.js";
import {
  defineRenderer,
  type MiniGameDefinition,
  type Surface,
} from "../src/mini-game-kit/index.js";

const GAME_ID = "tell-me-something-true";

function runReply(gameId: string): string {
  return JSON.stringify({
    run_id: "run-1",
    game_id: gameId,
    definition_version: "0.1.0",
    status: "active",
    mechanic_type: "social-truth-bluff",
    deadline_at: null,
    phase_state: null,
    my_submissions: [],
  });
}

function emptyStream(): Response {
  return new Response(
    new ReadableStream<Uint8Array>({ start: (c) => c.close() }),
    { status: 200, headers: { "content-type": "text/event-stream" } },
  );
}

function fakeServer(gameId: string): typeof fetch {
  return (async (input: RequestInfo | URL): Promise<Response> => {
    const url = String(input);
    if (url.includes("/mini-games/active")) {
      return new Response(runReply(gameId), { status: 200 });
    }
    if (url.includes("/events?since=")) return emptyStream();
    return new Response("not found", { status: 404 });
  }) as typeof fetch;
}

function makeStage(window: HappyWindow): HTMLElement {
  return window.document.createElement("section") as unknown as HTMLElement;
}

async function bootOn(
  surface: Surface,
  registry: RendererRegistry,
  gameId: string,
  window: HappyWindow,
  stage: HTMLElement,
) {
  return bootMiniGameStage(stage, {
    registry,
    baseUrl: "https://arcwright.test",
    sessionId: "session-1",
    token: "token-x",
    surface,
    participantId: "p-1",
    characterId: "c-1",
    loadDefinition: async () => tmstDefinition as unknown as MiniGameDefinition,
    view: window as unknown as Window,
    fetcher: fakeServer(gameId),
    perfTransport: "none",
  });
}

for (const surface of ["shared_display", "phone"] as const) {
  test(`loader mounts the Tell Me Something True renderer by game ID on the ${surface}`, async () => {
    const window = new HappyWindow();
    const stage = makeStage(window);
    const registry = new RendererRegistry();
    registry.register(tmstRenderer);

    const controller = await bootOn(surface, registry, GAME_ID, window, stage);

    assert.equal(
      stage.getAttribute("data-mini-game-state"),
      `active:${GAME_ID}`,
    );
    assert.ok(
      stage.querySelector('[data-role="tmst-shell"]'),
      "the package's own shell is drawn",
    );
    assert.match(stage.textContent ?? "", /NON_AUTHORITATIVE_PREVIEW/);
    controller.unmount();
  });
}

test("the TV stage draws no phone-only input", async () => {
  const window = new HappyWindow();
  const stage = makeStage(window);
  const registry = new RendererRegistry();
  registry.register(tmstRenderer);

  const controller = await bootOn(
    "shared_display",
    registry,
    GAME_ID,
    window,
    stage,
  );

  assert.equal(stage.querySelector('[data-role="statement-input"]'), null);
  assert.equal(stage.querySelector('[data-role="truth-action"]'), null);
  controller.unmount();
});

test("an unregistered game ID ends in unknown-game", async () => {
  const window = new HappyWindow();
  const stage = makeStage(window);

  const controller = await bootOn(
    "phone",
    new RendererRegistry(),
    "no-such-game",
    window,
    stage,
  );

  assert.equal(stage.getAttribute("data-mini-game-state"), "unknown-game");
  controller.unmount();
});

test("two stages on one page run two different games at once", async () => {
  const window = new HappyWindow();
  const registry = new RendererRegistry();
  registry.register(tmstRenderer);
  registry.register(
    defineRenderer({
      gameId: "second-game",
      phone: {
        mount(root) {
          root.setAttribute("data-second-game", "mounted");
          return { update() {}, handleEvent() {}, unmount() {} };
        },
      },
    }),
  );
  const first = makeStage(window);
  const second = makeStage(window);

  const [a, b] = await Promise.all([
    bootOn("phone", registry, GAME_ID, window, first),
    bootOn("phone", registry, "second-game", window, second),
  ]);

  assert.equal(first.getAttribute("data-mini-game-state"), `active:${GAME_ID}`);
  assert.equal(
    second.getAttribute("data-mini-game-state"),
    "active:second-game",
  );
  assert.equal(second.getAttribute("data-second-game"), "mounted");
  assert.equal(first.getAttribute("data-second-game"), null);
  a.unmount();
  b.unmount();
});
