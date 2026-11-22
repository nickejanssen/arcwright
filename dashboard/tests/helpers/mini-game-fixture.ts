import type { MiniGameDefinition } from "../../src/mini-game-kit/index.js";
import { defineRenderer } from "../../src/mini-game-kit/index.js";
import { RendererRegistry } from "../../src/mini-games/registry.js";
import type { StageServices } from "../../src/screens/round/RoundMiniGameStage.js";

const definition = { game_id: "fixture-game" } as unknown as MiniGameDefinition;

export function fixtureServices(seen: string[] = []): StageServices {
  const registry = new RendererRegistry();
  registry.register(
    defineRenderer({
      gameId: "fixture-game",
      sharedDisplay: {
        mount(root: HTMLElement) {
          root.textContent = "Fixture shared view";
          return { update() {}, handleEvent() {}, unmount() {} };
        },
      },
      phone: {
        mount(root: HTMLElement) {
          root.textContent = "Fixture phone view";
          return { update() {}, handleEvent() {}, unmount() {} };
        },
      },
    }),
  );

  const fetcher = (async (input: RequestInfo | URL) => {
    const url = String(input);
    seen.push(url);
    if (url.includes("/mini-games/active")) {
      return new Response(
        JSON.stringify({
          run_id: "run_internal_1",
          game_id: "fixture-game",
          definition_version: "0.1.0",
          status: "active",
          deadline_at: null,
          my_submissions: [],
        }),
        { status: 200 },
      );
    }
    if (url.includes("/lobby")) {
      return new Response(JSON.stringify({ players: [] }), { status: 200 });
    }
    if (url.includes("/events?since=")) {
      return new Response(new ReadableStream<Uint8Array>({ start() {} }), {
        status: 200,
      });
    }
    return new Response("not found", { status: 404 });
  }) as typeof fetch;

  return {
    registry,
    loadDefinition: async () => definition,
    fetcher,
    perfTransport: "none",
  };
}
