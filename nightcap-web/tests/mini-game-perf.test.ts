// Performance budget gate. Mount-to-paint must stay under the budget defined
// in spec 0050 Design Notes. Measured against a no-op renderer using
// happy-dom so it captures the kit overhead, not the renderer's logic.

import assert from "node:assert/strict";
import test from "node:test";
import { Window as HappyWindow } from "happy-dom";

import {
  defineRenderer,
  el,
  type SurfaceLifecycle,
} from "../src/mini-game-kit/index.js";
import { RendererRegistry } from "../src/mini-games/registry.js";
import { bootMiniGameStage } from "../src/mini-games/client.js";
import type { MiniGameDefinition } from "../src/mini-game-kit/index.js";

const MOUNT_BUDGET_MS = 100;

function makeStreamingResponse(body: string): Response {
  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(encoder.encode(body));
      controller.close();
    },
  });
  return new Response(stream, { status: 200 });
}

function makeDefinition(): MiniGameDefinition {
  return {
    schema_version: "1.0",
    game_id: "fixture-individual",
    version: "0.1.0",
    mechanic_type: "timed-choice",
    participation_mode: "individual",
    content_mode: "authored",
    min_players: 1,
    max_players: 10,
    duration_seconds: 30,
    rules: {},
    authored_content: { prompt: "x", choices: ["a", "b"] },
    generation_constraints: null,
    behavioral_outputs: [],
    clue_fallback: {
      delay_seconds: 15,
      clue_variant: "reduced",
      host_override: true,
    },
  };
}

test("mount-to-paint stays under budget (cold)", async () => {
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const stage = doc.createElement("section");
  const registry = new RendererRegistry();
  registry.register(
    defineRenderer({
      gameId: "fixture-individual",
      phone: {
        mount(root): SurfaceLifecycle {
          const node = el(doc, "div", { "data-role": "perf-marker" }, [
            "ready",
          ]);
          root.appendChild(node);
          return {
            update: () => {},
            handleEvent: () => {},
            unmount: () => {},
          };
        },
      },
    }),
  );

  const fetcher = (async (input: RequestInfo | URL): Promise<Response> => {
    const url = typeof input === "string" ? input : input.toString();
    if (url.includes("/mini-games/active")) {
      return new Response(
        JSON.stringify({
          run_id: "run-1",
          game_id: "fixture-individual",
          status: "active",
          deadline_at: null,
          my_submissions: [],
        }),
        { status: 200 },
      );
    }
    if (url.includes("/events?since=")) {
      return makeStreamingResponse("");
    }
    return new Response("Not found", { status: 404 });
  }) as typeof fetch;

  const start =
    typeof performance !== "undefined" ? performance.now() : Date.now();
  const controller = await bootMiniGameStage(stage, {
    registry,
    baseUrl: "https://arcwright.test",
    sessionId: "session-1",
    token: "token-x",
    surface: "phone",
    participantId: "p-1",
    characterId: "c-1",
    loadDefinition: async () => makeDefinition(),
    view: window as unknown as Window,
    fetcher,
    perfTransport: "none",
  });
  const elapsed =
    (typeof performance !== "undefined" ? performance.now() : Date.now()) -
    start;

  assert.ok(
    stage.querySelector('[data-role="perf-marker"]'),
    "expected renderer to have painted",
  );
  assert.ok(
    elapsed < MOUNT_BUDGET_MS,
    `mount-to-paint ${elapsed.toFixed(1)}ms exceeds budget ${MOUNT_BUDGET_MS}ms`,
  );

  controller.unmount();
});
