// AW-347: the replies a real route sends reach the Tell Me Something True
// package screen unchanged. The file under fixtures/ is written by
// api/tests/test_mini_game_views_api.py from the real routes, and that test
// fails when the file goes stale. Here the replies go through the real loader
// to the real package renderer, and a thin wrapper records what the screen was
// given.
//
// What this proves: the real step is in the screen's state (runtimeState.phase)
// and the generated title replaces the screen's fallback title. What it does
// not prove: the screen does not yet read the step or draw a spotlight line;
// that mismatch is the follow-up task AW-351.

import assert from "node:assert/strict";
import test from "node:test";
import { Window as HappyWindow } from "happy-dom";

import tmstRenderer from "../../nightcap/mini_games/tell-me-something-true/client/renderer.ts";
import tmstDefinition from "../../nightcap/mini_games/tell-me-something-true/definitions/0.1.0.json";
import { bootMiniGameStage } from "../src/mini-games/client.js";
import { RendererRegistry } from "../src/mini-games/registry.js";
import type {
  MiniGameContext,
  MiniGameDefinition,
  MiniGameRenderer,
  Surface,
} from "../src/mini-game-kit/index.js";
import recorded from "./fixtures/mini-game-live-replies.json";

const GAME_ID = "tell-me-something-true";
const FALLBACK_TITLE = "Tell Me Something True";
const PHASES = ["input", "spotlight", "scoreboard"] as const;

type Reply = Record<string, unknown> & {
  presentation: Record<string, unknown>;
  runtime_state: Record<string, unknown>;
};
const replies = recorded as unknown as Record<
  (typeof PHASES)[number],
  { shared_display: Reply; player: Reply }
>;

function emptyStream(): Response {
  return new Response(
    new ReadableStream<Uint8Array>({ start: (c) => c.close() }),
    { status: 200, headers: { "content-type": "text/event-stream" } },
  );
}

// The shared screen reads the public address; a phone reads the signed-in one.
function serverReturning(reply: {
  display: Reply;
  active: Reply;
}): typeof fetch {
  return (async (input: RequestInfo | URL): Promise<Response> => {
    const url = String(input);
    if (url.includes("/mini-games/active/display")) {
      return new Response(JSON.stringify(reply.display), { status: 200 });
    }
    if (url.includes("/mini-games/active")) {
      return new Response(JSON.stringify(reply.active), { status: 200 });
    }
    if (url.includes("/events?since=")) return emptyStream();
    return new Response("not found", { status: 404 });
  }) as typeof fetch;
}

// The recorded replies carry a real deadline, so the screen starts a countdown.
// Closing the fake window stops its timers so the test process can end.
async function close(window: HappyWindow): Promise<void> {
  await window.happyDOM.close();
}

async function bootWith(phase: (typeof PHASES)[number], surface: Surface) {
  const window = new HappyWindow();
  const stage = window.document.createElement(
    "section",
  ) as unknown as HTMLElement;
  const seen: MiniGameContext[] = [];
  const registry = new RendererRegistry();
  const spy: MiniGameRenderer = {
    gameId: GAME_ID,
    mount(root, ctx) {
      seen.push(ctx);
      return tmstRenderer.mount(root, ctx);
    },
  };
  registry.register(spy);

  const controller = await bootMiniGameStage(stage, {
    registry,
    baseUrl: "https://arcwright.test",
    sessionId: "session-1",
    ...(surface === "phone" ? { token: "token-x" } : {}),
    surface,
    participantId: "p-1",
    characterId: "c-1",
    loadDefinition: async () => tmstDefinition as unknown as MiniGameDefinition,
    view: window as unknown as Window,
    fetcher: serverReturning({
      display: replies[phase].shared_display,
      active: replies[phase].player,
    }),
    perfTransport: "none",
  });
  assert.equal(seen.length, 1, "the screen was mounted once");
  return { stage, ctx: seen[0] as MiniGameContext, controller, window };
}

for (const phase of PHASES) {
  test(`the shared screen is given the ${phase} step and the generated title`, async () => {
    const { stage, ctx, controller, window } = await bootWith(
      phase,
      "shared_display",
    );

    assert.equal(ctx.state.runtimeState?.phase, phase);
    assert.equal(
      ctx.state.presentation?.title,
      replies[phase].shared_display.presentation.title,
    );
    const shown = stage.querySelector('[data-role="title"]')?.textContent;
    assert.ok(
      shown && shown !== FALLBACK_TITLE,
      "generated title, not fallback",
    );
    assert.equal(shown, replies[phase].shared_display.presentation.title);
    assert.equal(
      ctx.state.presentation?.prompt,
      undefined,
      "the phone-only prompt never reaches the shared screen",
    );
    controller.unmount();
    await close(window);
  });

  test(`the phone is given the ${phase} step and its own prompt`, async () => {
    const { ctx, controller, window } = await bootWith(phase, "phone");

    assert.equal(ctx.state.runtimeState?.phase, phase);
    assert.equal(
      ctx.state.presentation?.prompt,
      replies[phase].player.presentation.prompt,
    );
    controller.unmount();
    await close(window);
  });
}
