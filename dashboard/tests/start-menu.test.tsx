// Acceptance 2: every phone has a Start menu (Pause, Resume, Settings); the
// host's adds Start game, Move on, mini-game Resolve and Cancel, End game and
// handing the host role on (spec 0095 Q1, D-133). Each control is one route
// call with the seat's token.

import assert from "node:assert/strict";
import test from "node:test";

import { createElement } from "react";
import { createControls } from "../src/api/controls.js";
import type { Controls } from "../src/api/controls.js";
import { ApiError } from "../src/api/lobby.js";
import StartMenu from "../src/shell/StartMenu.js";
import type { StartMenuInfo } from "../src/shell/StartMenu.js";
import { mount } from "./helpers/dom.js";

function fakeControls() {
  const calls: string[] = [];
  const note = (name: string) => async () => void calls.push(name);
  const controls: Controls = {
    start: note("start"),
    pause: note("pause"),
    resume: note("resume"),
    moveOn: note("moveOn"),
    end: note("end"),
    resolveMiniGame: note("resolve"),
    cancelMiniGame: note("cancel"),
  };
  return { calls, controls };
}

function menu(
  over: Partial<StartMenuInfo>,
  controls: Controls,
  closed: string[] = [],
) {
  return createElement(StartMenu, {
    role: "player",
    sessionStatus: "active",
    phase: "scene",
    playerCount: 3,
    minPlayers: 2,
    controls,
    canHandOver: false,
    onOpenSettings: () => void closed.push("settings"),
    onClose: () => void closed.push("close"),
    ...over,
  });
}

const labels = (page: { buttons(): HTMLButtonElement[] }) =>
  page.buttons().map((b) => b.textContent?.trim());

test("a player's menu is Pause (or Resume) and Settings, nothing else", async () => {
  const { controls } = fakeControls();
  const running = await mount(menu({}, controls));
  assert.deepEqual(labels(running), ["Pause", "Settings", "Close"]);
  await running.unmount();

  const paused = await mount(menu({ sessionStatus: "paused" }, controls));
  assert.deepEqual(labels(paused), ["Resume", "Settings", "Close"]);
  await paused.unmount();
});

test("the host's menu adds the host controls, and mini-game controls only during a mini-game", async () => {
  const { controls } = fakeControls();
  const scene = await mount(menu({ role: "host" }, controls));
  assert.deepEqual(labels(scene), [
    "Pause",
    "Move on",
    "End game",
    "Settings",
    "Close",
  ]);
  await scene.unmount();

  const mini = await mount(
    menu({ role: "host", phase: "mini_game" }, controls),
  );
  assert.deepEqual(labels(mini), [
    "Pause",
    "Move on",
    "Finish mini-game now",
    "Cancel mini-game",
    "End game",
    "Settings",
    "Close",
  ]);
  await mini.unmount();
});

test("the menu swaps when the role changes", async () => {
  const { controls } = fakeControls();
  const page = await mount(menu({ role: "player" }, controls));
  assert.ok(!labels(page).includes("End game"));
  await page.rerender(menu({ role: "host" }, controls));
  assert.ok(labels(page).includes("End game"));
  await page.rerender(menu({ role: "player" }, controls));
  assert.ok(!labels(page).includes("End game"));
  await page.unmount();
});

test("Start game waits for the route's minimum, then calls start once and closes", async () => {
  const { calls, controls } = fakeControls();
  const closed: string[] = [];

  const few = await mount(
    menu(
      { role: "host", sessionStatus: "created", playerCount: 1, minPlayers: 2 },
      controls,
      closed,
    ),
  );
  assert.equal(few.button("Start game").disabled, true);
  assert.ok(few.text().includes("Needs 2 or more players."));
  await few.unmount();

  const enough = await mount(
    menu(
      { role: "host", sessionStatus: "created", playerCount: 2, minPlayers: 2 },
      controls,
      closed,
    ),
  );
  assert.equal(enough.button("Start game").disabled, false);
  await enough.click("Start game");
  assert.deepEqual(calls, ["start"]);
  assert.deepEqual(closed, ["close"]);
  await enough.unmount();
});

test("Move on in Last Call and End game ask first; saying no sends nothing", async () => {
  const { calls, controls } = fakeControls();

  const lastCall = await mount(
    menu({ role: "host", phase: "commit" }, controls),
  );
  await lastCall.click("Move on");
  assert.ok(lastCall.text().includes("This locks every saved theory."));
  await lastCall.click("Keep waiting");
  assert.deepEqual(calls, [], "no call after cancelling");
  await lastCall.click("Move on");
  await lastCall.click("Lock and move on");
  assert.deepEqual(calls, ["moveOn"]);
  await lastCall.unmount();

  const end = await mount(menu({ role: "host" }, controls));
  await end.click("End game");
  assert.ok(end.text().includes("It cannot be restarted."));
  await end.click("Keep playing");
  assert.deepEqual(calls, ["moveOn"], "still nothing new after cancelling");
  await end.click("End game");
  await end.click("End game");
  assert.deepEqual(calls, ["moveOn", "end"]);
  await end.unmount();

  const scene = await mount(menu({ role: "host", phase: "scene" }, controls));
  await scene.click("Move on");
  assert.deepEqual(
    calls,
    ["moveOn", "end", "moveOn"],
    "other phases move on at once",
  );
  await scene.unmount();
});

test("a refusal shows the plain words and keeps the menu open", async () => {
  const { controls } = fakeControls();
  const closed: string[] = [];
  const refusing: Controls = {
    ...controls,
    pause: async () => {
      throw new ApiError("no", 403);
    },
    resume: async () => {
      throw new ApiError("boom", 500);
    },
  };
  const page = await mount(menu({}, refusing, closed));
  await page.click("Pause");
  assert.ok(page.text().includes("Only the host can do that for now."));
  assert.deepEqual(closed, []);
  await page.unmount();

  const failing = await mount(
    menu({ sessionStatus: "paused" }, refusing, closed),
  );
  await failing.click("Resume");
  assert.ok(failing.text().includes("That did not work. Try again."));
  await failing.unmount();
});

test("Make someone else host shows only when the engine can do it", async () => {
  const { controls } = fakeControls();
  const handed: string[] = [];
  const onHandOver = async () => void handed.push("over");

  const hidden = await mount(menu({ role: "host", onHandOver }, controls));
  assert.ok(!labels(hidden).includes("Make someone else host"));
  await hidden.unmount();

  const shown = await mount(
    menu({ role: "host", canHandOver: true, onHandOver }, controls),
  );
  await shown.click("Make someone else host");
  assert.deepEqual(handed, ["over"]);
  await shown.unmount();
});

test("each control is one route call with the seat's token", async () => {
  const seen: Array<{
    url: string;
    method?: string;
    auth?: string;
    body?: string;
  }> = [];
  const fetcher = (async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    seen.push({
      url,
      method: init?.method,
      auth: (init?.headers as Record<string, string> | undefined)
        ?.Authorization,
      body: init?.body as string | undefined,
    });
    if (url.endsWith("/mini-games/active/display")) {
      return new Response(JSON.stringify({ run_id: "run-7" }), { status: 200 });
    }
    return new Response("{}", { status: 200 });
  }) as typeof fetch;
  const controls = createControls("game-1", async () => "tok", fetcher);

  await controls.start();
  await controls.pause();
  await controls.resume();
  await controls.moveOn();
  await controls.end();
  await controls.resolveMiniGame();
  await controls.cancelMiniGame();

  const posts = seen.filter((c) => c.method === "POST");
  assert.deepEqual(
    posts.map((c) => c.url),
    [
      "/v1/sessions/game-1/start",
      "/v1/sessions/game-1/pause",
      "/v1/sessions/game-1/resume",
      "/v1/sessions/game-1/round/move-on",
      "/v1/sessions/game-1/end",
      "/v1/sessions/game-1/mini-games/run-7/host-commands",
      "/v1/sessions/game-1/mini-games/run-7/host-commands",
    ],
  );
  assert.ok(posts.every((c) => c.auth === "Bearer tok"));
  assert.equal(posts[5].body, JSON.stringify({ command: "resolve" }));
  assert.equal(posts[6].body, JSON.stringify({ command: "cancel" }));
});
