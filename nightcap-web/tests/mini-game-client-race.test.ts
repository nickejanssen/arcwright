// Regression tests for the concurrent-refresh race and event-dispatch
// snapshot bug found during PR #174 review. Both tests use a never-closing
// SSE stream so the inner streamLoop yields cooperatively to the test's
// macrotask waits rather than monopolizing the microtask queue.

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
    authored_content: null,
    generation_constraints: null,
    behavioral_outputs: [],
    clue_fallback: {
      delay_seconds: 15,
      clue_variant: "reduced",
      host_override: true,
    },
  };
}

// Stream that stays open until its reader is cancelled. Lets streamLoop
// suspend at `await reader.read()` so the test runtime can interleave.
function makeOpenStreamingResponse(): Response {
  const stream = new ReadableStream<Uint8Array>({
    start() {
      // Never enqueue; reader.read() suspends until cancel.
    },
  });
  return new Response(stream, { status: 200 });
}

function makeOneShotStreamingResponse(body: string): Response {
  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(encoder.encode(body));
      controller.close();
    },
  });
  return new Response(stream, { status: 200 });
}

test("client: concurrent refresh() calls do not double-mount", async () => {
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const stage = doc.createElement("section");
  let mountCount = 0;

  const registry = new RendererRegistry();
  registry.register(
    defineRenderer({
      gameId: "fixture-individual",
      phone: {
        mount(root): SurfaceLifecycle {
          mountCount += 1;
          root.setAttribute("data-test-mounted", String(mountCount));
          return {
            update: () => {},
            handleEvent: () => {},
            unmount: () => {
              root.removeAttribute("data-test-mounted");
            },
          };
        },
      },
    }),
  );

  // Slow the active-state fetch so multiple concurrent refresh()es overlap.
  const fetcher = (async (input: RequestInfo | URL): Promise<Response> => {
    const url = typeof input === "string" ? input : input.toString();
    if (url.includes("/mini-games/active")) {
      await new Promise((r) => setTimeout(r, 10));
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
      return makeOpenStreamingResponse();
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
    loadDefinition: async () => makeDefinition("fixture-individual"),
    view: window as unknown as Window,
    fetcher,
    perfTransport: "none",
  });

  // Initial boot mounted once. Now fire three concurrent refreshes. With the
  // sequence-counter guard, stale refreshes return early instead of calling
  // mountRenderer a second time on the same run.
  await Promise.all([
    controller.refresh(),
    controller.refresh(),
    controller.refresh(),
  ]);

  assert.equal(mountCount, 1, "renderer mounts exactly once across overlap");

  controller.unmount();
});

test("client: handler unsubscribing mid-dispatch does not skip siblings", async () => {
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const stage = doc.createElement("section");
  const registry = new RendererRegistry();

  let secondHandlerCalls = 0;
  let unsubscribeFirst: (() => void) | null = null;

  registry.register(
    defineRenderer({
      gameId: "test",
      phone: {
        mount(_, ctx): SurfaceLifecycle {
          // First handler unsubscribes itself when it fires; the second
          // handler must still receive the same event despite the listener
          // array shrinking mid-iteration.
          unsubscribeFirst = ctx.onEvent(() => {
            if (unsubscribeFirst) {
              unsubscribeFirst();
              unsubscribeFirst = null;
            }
          });
          ctx.onEvent(() => {
            secondHandlerCalls += 1;
          });
          return {
            update: () => {},
            handleEvent: () => {},
            unmount: () => {},
          };
        },
      },
    }),
  );

  const eventJson = JSON.stringify({
    event_id: "evt-1",
    session_id: "session-1",
    timestamp: "2026-06-26T00:00:00Z",
    category: "narrative",
    event_type: "test_event",
    actor_id: null,
    target_audience: "all",
    target_player_id: null,
    payload: {},
    presentation_hints: {
      emotion: null,
      urgency: null,
      voice_hint: null,
      animation_hint: null,
      lighting_hint: null,
      pause_before_ms: 0,
    },
    sequence_number: 1,
  });

  let eventsCalled = 0;
  const fetcher = (async (input: RequestInfo | URL): Promise<Response> => {
    const url = typeof input === "string" ? input : input.toString();
    if (url.includes("/mini-games/active")) {
      return new Response(
        JSON.stringify({
          run_id: "run-1",
          game_id: "test",
          status: "active",
          deadline_at: null,
          my_submissions: [],
        }),
        { status: 200 },
      );
    }
    if (url.includes("/events?since=")) {
      eventsCalled += 1;
      // First call delivers the event then closes. Subsequent calls stay
      // open so streamLoop doesn't spin retrying after the initial delivery.
      if (eventsCalled === 1) {
        return makeOneShotStreamingResponse(`data: ${eventJson}\n\n`);
      }
      return makeOpenStreamingResponse();
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
    loadDefinition: async () => makeDefinition("test"),
    view: window as unknown as Window,
    fetcher,
    perfTransport: "none",
  });

  await new Promise((r) => setTimeout(r, 50));

  assert.equal(
    secondHandlerCalls,
    1,
    "second handler must receive the event even after first handler unsubscribed mid-dispatch",
  );

  controller.unmount();
});
