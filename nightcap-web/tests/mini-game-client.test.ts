// Browser-entry / stage client tests. Verify the boot loop:
// - fetches active state from Arcwright
// - looks up the right renderer
// - mounts the lifecycle
// - reacts to state_transition events (refresh)
// - calls getMiniGameState again on stream drop (reconnect)
// - cleans up on unmount

import assert from "node:assert/strict";
import test from "node:test";
import { Window as HappyWindow } from "happy-dom";

import { RendererRegistry } from "../src/mini-games/registry.js";
import { bootMiniGameStage } from "../src/mini-games/client.js";
import {
  defineRenderer,
  type MiniGameDefinition,
  type SurfaceLifecycle,
} from "../src/mini-game-kit/index.js";

function makeDefinition(gameId: string): MiniGameDefinition {
  return {
    schema_version: "1.0",
    game_id: gameId,
    version: "0.1.0",
    mechanic_type: "timed-choice",
    participation_mode: "individual",
    content_mode: "authored",
    min_players: 1,
    max_players: 10,
    duration_seconds: 30,
    rules: {},
    authored_content: { prompt: "Pick one", choices: ["a", "b"] },
    generation_constraints: null,
    behavioral_outputs: [],
    clue_fallback: {
      delay_seconds: 15,
      clue_variant: "reduced",
      host_override: true,
    },
  };
}

interface MountLog {
  ctx: { gameId: string; runId: string };
}

function makeTracingRenderer(gameId: string, log: MountLog[]) {
  return defineRenderer({
    gameId,
    phone: {
      mount(root, ctx): SurfaceLifecycle {
        log.push({ ctx: { gameId, runId: ctx.state.runId } });
        root.setAttribute("data-test-mounted", gameId);
        return {
          update: () => {},
          handleEvent: () => {},
          unmount: () => {
            root.removeAttribute("data-test-mounted");
          },
        };
      },
    },
  });
}

function makeStreamingResponse(body: string): Response {
  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(encoder.encode(body));
      controller.close();
    },
  });
  return new Response(stream, {
    status: 200,
    headers: { "content-type": "text/event-stream" },
  });
}

function makeFetcher(responses: Record<string, () => Response>): typeof fetch {
  return (async (input: RequestInfo | URL): Promise<Response> => {
    const url = typeof input === "string" ? input : input.toString();
    for (const [pattern, builder] of Object.entries(responses)) {
      if (url.includes(pattern)) return builder();
    }
    return new Response("Not found", { status: 404 });
  }) as typeof fetch;
}

test("client: boots, fetches state, mounts the registered renderer", async () => {
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const stage = doc.createElement("section");
  const log: MountLog[] = [];
  const registry = new RendererRegistry();
  registry.register(makeTracingRenderer("fixture-individual", log));

  const fetcher = makeFetcher({
    "/mini-games/active": () =>
      new Response(
        JSON.stringify({
          run_id: "run-1",
          game_id: "fixture-individual",
          status: "active",
          deadline_at: null,
          my_submissions: [],
        }),
        { status: 200 },
      ),
    "/events?since=": () => makeStreamingResponse(""),
  });

  const controller = await bootMiniGameStage(stage, {
    registry,
    baseUrl: "https://arcwright.test",
    sessionId: "session-1",
    token: "token-x",
    surface: "phone",
    participantId: "p-1",
    characterId: "c-1",
    loadDefinition: async () => makeDefinition("fixture-individual"),
    view: window as unknown as Window,
    fetcher,
    perfTransport: "none",
  });

  assert.equal(log.length, 1);
  assert.equal(log[0]?.ctx.gameId, "fixture-individual");
  assert.equal(log[0]?.ctx.runId, "run-1");
  assert.equal(stage.getAttribute("data-test-mounted"), "fixture-individual");
  assert.match(stage.getAttribute("data-mini-game-state") ?? "", /active:/);

  controller.unmount();
  assert.equal(stage.getAttribute("data-test-mounted"), null);
});

test("client: idle when no active mini-game", async () => {
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const stage = doc.createElement("section");
  const registry = new RendererRegistry();
  const fetcher = makeFetcher({
    "/mini-games/active": () => new Response("", { status: 404 }),
    "/events?since=": () => makeStreamingResponse(""),
  });

  const controller = await bootMiniGameStage(stage, {
    registry,
    baseUrl: "https://arcwright.test",
    sessionId: "session-1",
    token: "token-x",
    surface: "phone",
    participantId: "p-1",
    characterId: "c-1",
    loadDefinition: async () => makeDefinition("none"),
    view: window as unknown as Window,
    fetcher,
    perfTransport: "none",
  });

  assert.equal(stage.getAttribute("data-mini-game-state"), "idle");
  controller.unmount();
});

test("client: unknown gameId surfaces unknown-game state", async () => {
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const stage = doc.createElement("section");
  const registry = new RendererRegistry();
  // No renderers registered.
  const fetcher = makeFetcher({
    "/mini-games/active": () =>
      new Response(
        JSON.stringify({
          run_id: "run-1",
          game_id: "unregistered-game",
          status: "active",
          deadline_at: null,
          my_submissions: [],
        }),
        { status: 200 },
      ),
    "/events?since=": () => makeStreamingResponse(""),
  });

  const controller = await bootMiniGameStage(stage, {
    registry,
    baseUrl: "https://arcwright.test",
    sessionId: "session-1",
    token: "token-x",
    surface: "phone",
    participantId: "p-1",
    characterId: "c-1",
    loadDefinition: async () => makeDefinition("unregistered-game"),
    view: window as unknown as Window,
    fetcher,
    perfTransport: "none",
  });

  assert.equal(stage.getAttribute("data-mini-game-state"), "unknown-game");
  controller.unmount();
});

test("client: refresh remounts when runId changes", async () => {
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const stage = doc.createElement("section");
  const log: MountLog[] = [];
  const registry = new RendererRegistry();
  registry.register(makeTracingRenderer("fixture-individual", log));

  let runId = "run-1";
  const fetcher = makeFetcher({
    "/mini-games/active": () =>
      new Response(
        JSON.stringify({
          run_id: runId,
          game_id: "fixture-individual",
          status: "active",
          deadline_at: null,
          my_submissions: [],
        }),
        { status: 200 },
      ),
    "/events?since=": () => makeStreamingResponse(""),
  });

  const controller = await bootMiniGameStage(stage, {
    registry,
    baseUrl: "https://arcwright.test",
    sessionId: "session-1",
    token: "token-x",
    surface: "phone",
    participantId: "p-1",
    characterId: "c-1",
    loadDefinition: async () => makeDefinition("fixture-individual"),
    view: window as unknown as Window,
    fetcher,
    perfTransport: "none",
  });

  assert.equal(log.length, 1);

  runId = "run-2";
  await controller.refresh();
  assert.equal(log.length, 2);
  assert.equal(log[1]?.ctx.runId, "run-2");

  controller.unmount();
});

test("client: submits action with generated submission id", async () => {
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const stage = doc.createElement("section");

  const submissionsSeen: { runId: string; body: unknown }[] = [];
  const registry = new RendererRegistry();

  const captured: { submit?: (payload: unknown) => Promise<unknown> } = {};
  registry.register(
    defineRenderer({
      gameId: "test-game",
      phone: {
        mount(_, ctx): SurfaceLifecycle {
          captured.submit = (payload) =>
            ctx.submit(payload as Record<string, unknown>);
          return {
            update: () => {},
            handleEvent: () => {},
            unmount: () => {},
          };
        },
      },
    }),
  );

  const fetcher = (async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    const url = typeof input === "string" ? input : input.toString();
    if (url.includes("/mini-games/active")) {
      return new Response(
        JSON.stringify({
          run_id: "run-1",
          game_id: "test-game",
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
    if (url.includes("/submissions")) {
      const body = init?.body ? JSON.parse(String(init.body)) : null;
      submissionsSeen.push({ runId: "run-1", body });
      return new Response(
        JSON.stringify({
          submission_id: body.submission_id,
          is_accepted: true,
        }),
        { status: 200 },
      );
    }
    return new Response("Not found", { status: 404 });
  }) as typeof fetch;

  const controller = await bootMiniGameStage(stage, {
    registry,
    baseUrl: "https://arcwright.test",
    sessionId: "session-1",
    token: "token-x",
    surface: "phone",
    participantId: "p-1",
    characterId: "c-1",
    loadDefinition: async () => makeDefinition("test-game"),
    view: window as unknown as Window,
    fetcher,
    perfTransport: "none",
  });

  await captured.submit?.({ choice: "a" });
  assert.equal(submissionsSeen.length, 1);
  const seen = submissionsSeen[0]?.body as {
    submission_id: string;
    payload: { choice: string };
  };
  assert.equal(typeof seen.submission_id, "string");
  assert.deepEqual(seen.payload, { choice: "a" });

  controller.unmount();
});
