// AW-347: the replies a real route sends reach the Tell Me Something True
// package screen unchanged. The file under fixtures/ is written by
// api/tests/test_mini_game_views_api.py from the real routes, and that test
// fails when the file goes stale. Here the replies go through the real loader
// to the real package renderer, and a thin wrapper records what the screen was
// given.
//
// The public lobby data below is a representative response, separate from the
// recorded mini-game replies.

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
  SurfaceLifecycle,
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
  return new Response(new ReadableStream<Uint8Array>(), {
    status: 200,
    headers: { "content-type": "text/event-stream" },
  });
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
    if (url.endsWith("/lobby")) {
      return new Response(
        JSON.stringify({
          players: [
            {
              character_id: "a0000000-0000-4000-8000-0000000000c2",
              display_name: "Alex",
            },
          ],
        }),
        { status: 200 },
      );
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

async function bootWith(
  phase: (typeof PHASES)[number],
  surface: Surface,
  reply = {
    display: replies[phase].shared_display,
    active: replies[phase].player,
  },
  fetcher: typeof fetch = serverReturning(reply),
) {
  const window = new HappyWindow();
  const stage = window.document.createElement(
    "section",
  ) as unknown as HTMLElement;
  const seen: MiniGameContext[] = [];
  let lifecycle: SurfaceLifecycle | undefined;
  const registry = new RendererRegistry();
  const spy: MiniGameRenderer = {
    gameId: GAME_ID,
    mount(root, ctx) {
      seen.push(ctx);
      lifecycle = tmstRenderer.mount(root, ctx);
      return lifecycle;
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
    fetcher,
    perfTransport: "none",
  });
  assert.equal(seen.length, 1, "the screen was mounted once");
  return {
    stage,
    ctx: seen[0] as MiniGameContext,
    controller,
    window,
    lifecycle: lifecycle!,
  };
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

test("the shared screen distinguishes the three recorded steps", async () => {
  const labels: string[] = [];
  for (const phase of PHASES) {
    const { stage, controller, window } = await bootWith(
      phase,
      "shared_display",
    );
    labels.push(stage.querySelector('[data-role="status"]')?.textContent ?? "");
    controller.unmount();
    await close(window);
  }
  assert.ok(labels.every((label) => label.length > 0));
  assert.equal(
    new Set(labels).size,
    PHASES.length,
    "each step has a visible label",
  );
  assert.match(labels[0]!, /statement/i);
  assert.match(labels[1]!, /spotlight/i);
  assert.match(labels[2]!, /scoreboard/i);
});

test("refresh updates the displayed step and spotlight", async () => {
  const reply = {
    display: replies.input.shared_display,
    active: replies.input.player,
  };
  const { stage, controller, window } = await bootWith(
    "input",
    "shared_display",
    reply,
  );
  const initial = stage.querySelector('[data-role="status"]')?.textContent;
  reply.display = replies.spotlight.shared_display;
  await controller.refresh();
  const spotlight =
    stage.querySelector('[data-role="spotlight"]')?.textContent ?? "";
  const next = stage.querySelector('[data-role="status"]')?.textContent;
  reply.display = replies.scoreboard.shared_display;
  await controller.refresh();
  const last = stage.querySelector('[data-role="status"]')?.textContent;
  controller.unmount();
  await close(window);
  assert.match(spotlight, /Alex/);
  assert.equal(new Set([initial, next, last]).size, 3);
});

test("the recorded spotlight names the player on the shared screen", async () => {
  const { stage, controller, window } = await bootWith(
    "spotlight",
    "shared_display",
  );
  await new Promise((resolve) => setTimeout(resolve, 0));
  const spotlight =
    stage.querySelector('[data-role="spotlight"]')?.textContent ?? "";
  controller.unmount();
  await close(window);
  assert.match(spotlight, /Alex/);
});

test("spotlight events use the public name and never show an unknown ID", async () => {
  const { stage, controller, window, lifecycle } = await bootWith(
    "input",
    "shared_display",
  );
  await new Promise((resolve) => setTimeout(resolve, 0));
  const event = {
    event_type: "tmst_spotlight_started",
    payload: { target_character_id: "a0000000-0000-4000-8000-0000000000c2" },
  } as Parameters<SurfaceLifecycle["handleEvent"]>[0];
  lifecycle.handleEvent(event);
  const named =
    stage.querySelector('[data-role="spotlight"]')?.textContent ?? "";
  lifecycle.handleEvent({
    ...event,
    payload: { target_character_id: "unknown-id" },
  });
  const unknown =
    stage.querySelector('[data-role="spotlight"]')?.textContent ?? "";
  controller.unmount();
  await close(window);
  assert.match(named, /Alex/);
  assert.doesNotMatch(unknown, /unknown-id|Alex/);
});

test("a stalled lobby cannot block the shared game from mounting", async () => {
  const reply = {
    display: replies.input.shared_display,
    active: replies.input.player,
  };
  const standard = serverReturning(reply);
  let release!: () => void;
  const stalled = new Promise<Response>((resolve) => {
    release = () => resolve(new Response("unavailable", { status: 503 }));
  });
  const fetcher: typeof fetch = (input, init) =>
    String(input).endsWith("/lobby") ? stalled : standard(input, init);
  const boot = bootWith("input", "shared_display", reply, fetcher);
  const result = await Promise.race([
    boot.then(() => "mounted"),
    new Promise<string>((resolve) =>
      setTimeout(() => resolve("blocked"), 1800),
    ),
  ]);
  release();
  const { controller, window } = await boot;
  controller.unmount();
  await close(window);
  assert.equal(result, "mounted");
});

test("a completed result shows the public standing after a slow lobby reply", async () => {
  let release!: (response: Response) => void;
  const lobby = new Promise<Response>((resolve) => {
    release = resolve;
  });
  const fetcher: typeof fetch = async (input) => {
    const url = String(input);
    if (url.endsWith("/mini-games/active/display"))
      return new Response("", { status: 404 });
    if (url.endsWith("/mini-games/result/display"))
      return Response.json({
        run_id: "r",
        game_id: GAME_ID,
        definition_version: "0.1.0",
        phase_entry: 3,
        deadline_at: null,
        standing: [["participant-a"]],
      });
    if (url.endsWith("/lobby")) return lobby;
    return new Response("", { status: 404 });
  };
  const { stage, controller, window } = await bootWith(
    "input",
    "shared_display",
    undefined,
    fetcher,
  );
  assert.match(stage.textContent ?? "", /Player/);
  release(
    Response.json({
      players: [{ participant_id: "participant-a", display_name: "Alex" }],
    }),
  );
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.match(stage.textContent ?? "", /Alex/);
  assert.doesNotMatch(stage.textContent ?? "", /participant-a/);
  controller.unmount();
  await close(window);
});

test("a transient result read preserves the hold and retries successfully", async () => {
  let fail = false;
  const fetcher: typeof fetch = async (input) => {
    const url = String(input);
    if (url.endsWith("/mini-games/active/display"))
      return new Response("", { status: 404 });
    if (url.endsWith("/mini-games/result/display")) {
      if (fail) return new Response("unavailable", { status: 503 });
      return Response.json({
        run_id: "r",
        game_id: GAME_ID,
        definition_version: "0.1.0",
        phase_entry: 3,
        deadline_at: null,
        standing: [["p-1"]],
      });
    }
    if (url.endsWith("/lobby"))
      return Response.json({
        players: [{ participant_id: "p-1", display_name: "Alex" }],
      });
    return new Response("", { status: 404 });
  };
  const { stage, controller, window } = await bootWith(
    "input",
    "shared_display",
    undefined,
    fetcher,
  );
  assert.match(stage.textContent ?? "", /Alex/);
  fail = true;
  await controller.refresh();
  assert.match(stage.textContent ?? "", /Alex/);
  fail = false;
  await controller.refresh();
  assert.match(stage.textContent ?? "", /Alex/);
  controller.unmount();
  await close(window);
});

test("the phone can mark the held visit ready", async () => {
  let posted: unknown;
  const fetcher: typeof fetch = async (input, init) => {
    const url = String(input);
    if (url.endsWith("/mini-games/active"))
      return new Response("", { status: 404 });
    if (url.endsWith("/mini-games/result/display"))
      return Response.json({
        run_id: "r",
        game_id: GAME_ID,
        definition_version: "0.1.0",
        phase_entry: 3,
        deadline_at: null,
        standing: [["p-1"]],
      });
    if (url.endsWith("/room"))
      return Response.json({
        phase_entry: 3,
        players: [{ participant_id: "p-1", ready: false }],
      });
    if (url.endsWith("/me/ready")) {
      posted = JSON.parse(String(init?.body));
      return Response.json({});
    }
    return new Response("", { status: 404 });
  };
  const { stage, controller, window } = await bootWith(
    "input",
    "phone",
    undefined,
    fetcher,
  );
  (
    stage.querySelector('[data-role="result-ready"]') as HTMLButtonElement
  ).click();
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.deepEqual(posted, { phase_entry: 3 });
  assert.match(stage.textContent ?? "", /Waiting for the room/);
  controller.unmount();
  await close(window);
});

test("result refresh shows ready count and the paused clock", async () => {
  const fetcher: typeof fetch = async (input) => {
    const url = String(input);
    if (url.endsWith("/mini-games/active/display"))
      return new Response("", { status: 404 });
    if (url.endsWith("/mini-games/result/display"))
      return Response.json({
        run_id: "r",
        game_id: GAME_ID,
        definition_version: "0.1.0",
        phase_entry: 3,
        deadline_at: null,
        standing: [["p-1", "p-2"]],
      });
    if (url.endsWith("/room"))
      return Response.json({
        phase_entry: 3,
        paused: true,
        seconds_left: 11,
        ready_count: 1,
        player_count: 2,
      });
    return new Response("", { status: 404 });
  };
  const { stage, controller, window } = await bootWith(
    "input",
    "shared_display",
    undefined,
    fetcher,
  );
  assert.match(stage.textContent ?? "", /1 of 2 ready/);
  assert.match(
    stage.querySelector('[data-role="timer"]')?.textContent ?? "",
    /0:11/,
  );
  controller.unmount();
  await close(window);
});

test("a late name lookup from an earlier run cannot rename the next run", async () => {
  let runId = "run-a";
  let releaseOld!: (response: Response) => void;
  const oldLobby = new Promise<Response>((resolve) => {
    releaseOld = resolve;
  });
  let lobbyCalls = 0;
  const fetcher: typeof fetch = async (input) => {
    const url = String(input);
    if (url.endsWith("/mini-games/active/display"))
      return Response.json({
        ...replies.spotlight.shared_display,
        run_id: runId,
      });
    if (url.endsWith("/lobby")) {
      lobbyCalls++;
      return lobbyCalls === 1
        ? oldLobby
        : Response.json({
            players: [
              {
                character_id: "a0000000-0000-4000-8000-0000000000c2",
                display_name: "New Name",
              },
            ],
          });
    }
    return new Response("", { status: 404 });
  };
  const { stage, controller, window } = await bootWith(
    "spotlight",
    "shared_display",
    undefined,
    fetcher,
  );
  runId = "run-b";
  await controller.refresh();
  releaseOld(
    Response.json({
      players: [
        {
          character_id: "a0000000-0000-4000-8000-0000000000c2",
          display_name: "Old Name",
        },
      ],
    }),
  );
  await new Promise((resolve) => setTimeout(resolve, 0));
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.doesNotMatch(stage.textContent ?? "", /Old Name/);
  assert.match(stage.textContent ?? "", /New Name/);
  controller.unmount();
  await close(window);
});

test("legacy spotlight labels remain visible without a player-name mapping", async () => {
  const { stage, controller, window, lifecycle } = await bootWith(
    "input",
    "shared_display",
  );
  lifecycle.handleEvent({
    event_type: "tmst_spotlight_started",
    payload: { target_character_id: "legacy-id", spotlight_label: "Vesper" },
  } as Parameters<SurfaceLifecycle["handleEvent"]>[0]);
  const shown =
    stage.querySelector('[data-role="spotlight"]')?.textContent ?? "";
  controller.unmount();
  await close(window);
  assert.match(shown, /Vesper/);
});

test("a failed lobby refresh keeps previously received public names", async () => {
  const reply = {
    display: replies.input.shared_display,
    active: replies.input.player,
  };
  const standard = serverReturning(reply);
  let failLobby = false;
  const fetcher: typeof fetch = (input, init) =>
    failLobby && String(input).endsWith("/lobby")
      ? Promise.resolve(new Response("unavailable", { status: 503 }))
      : standard(input, init);
  const { stage, controller, window } = await bootWith(
    "input",
    "shared_display",
    reply,
    fetcher,
  );
  failLobby = true;
  reply.display = replies.spotlight.shared_display;
  await controller.refresh();
  const shown =
    stage.querySelector('[data-role="spotlight"]')?.textContent ?? "";
  controller.unmount();
  await close(window);
  assert.match(shown, /Alex/);
});

test("a legacy spotlight label remains visible on mount", async () => {
  const display = {
    ...replies.input.shared_display,
    runtime_state: { spotlight_label: "Vesper" },
  };
  const reply = { display, active: replies.input.player };
  const { stage, controller, window } = await bootWith(
    "input",
    "shared_display",
    reply,
  );
  const shown =
    stage.querySelector('[data-role="spotlight"]')?.textContent ?? "";
  controller.unmount();
  await close(window);
  assert.match(shown, /Vesper/);
});
