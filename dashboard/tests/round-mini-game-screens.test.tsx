// AW-332 pull request B: the mini-game phase uses the package stage on both
// surfaces, and a finding left open by the choices phase is shown once here.

import assert from "node:assert/strict";
import test from "node:test";
import { createElement } from "react";

import MiniGamePhone from "../src/screens/round/MiniGamePhone.js";
import MiniGameTv from "../src/screens/round/MiniGameTv.js";
import InvestigatePhone from "../src/screens/round/InvestigatePhone.js";
import { DEFAULT_SLOTS, resolveScreen } from "../src/shell/phaseScreens.js";
import { mount, settle } from "./helpers/dom.js";
import {
  ME,
  fakeEngine,
  lobby,
  round,
  withFetch,
} from "./helpers/round-fixtures.js";
import { fixtureServices } from "./helpers/mini-game-fixture.js";

const base = {
  sessionId: "game-uuid-1111",
  lobby: lobby(),
  seat: {
    participantId: ME,
    characterId: "character-internal",
    displayName: "Jordan",
  },
  getToken: async () => "player-sign-in",
};

test("the mini-game phase selects screen 10 on TV and screen 11 on phone", () => {
  const state = round({ phase: "mini_game", phaseEntry: 12 });
  const tv = resolveScreen("tv", lobby(), state, DEFAULT_SLOTS);
  const phone = resolveScreen("phone", lobby(), state, DEFAULT_SLOTS);
  assert.equal(tv.kind === "phase" && tv.Slot, MiniGameTv);
  assert.equal(phone.kind === "phase" && phone.Slot, MiniGamePhone);
});

test("screen 10 loads a fixture package on the public display address without sign-in or a shell clock", async () => {
  const seen: string[] = [];
  const services = fixtureServices(seen);
  const fetchActive = services.fetcher!;
  let release: () => void = () => {};
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  services.fetcher = (async (input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input).includes("/mini-games/active")) await gate;
    return fetchActive(input, init);
  }) as typeof fetch;
  const page = await mount(
    createElement(MiniGameTv, {
      ...base,
      round: round({ phase: "mini_game", phaseEntry: 12 }),
      stageServices: services,
    }),
  );
  assert.ok(page.text().includes("Getting the game ready..."));
  release();
  await settle();

  assert.ok(page.text().includes("A Quiet Evening"));
  assert.ok(
    page.text().includes("Fixture shared view"),
    `${page.text()} ${page.container.innerHTML} ${seen.join(" | ")}`,
  );
  assert.ok(!page.text().includes("1:42"), "the shell adds no second clock");
  assert.ok(seen.some((url) => url.endsWith("/mini-games/active/display")));
  assert.ok(!seen.some((url) => url.endsWith("/mini-games/active")));
  await page.unmount();
});

test("screen 10 explains when no mini-game is running", async () => {
  const services = fixtureServices();
  const fetcher = services.fetcher!;
  services.fetcher = (async (input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input).endsWith("/mini-games/active/display")) {
      return new Response("not found", { status: 404 });
    }
    return fetcher(input, init);
  }) as typeof fetch;
  const page = await mount(
    createElement(MiniGameTv, {
      ...base,
      round: round({ phase: "mini_game", phaseEntry: 12 }),
      stageServices: services,
    }),
  );

  assert.ok(page.text().includes("No mini-game in progress."));
  await page.unmount();
});

test("screen 11 uses this seat's sign-in on the player route", async () => {
  const seen: string[] = [];
  const page = await mount(
    createElement(MiniGamePhone, {
      ...base,
      round: round({ phase: "mini_game", phaseEntry: 12 }),
      stageServices: fixtureServices(seen),
    }),
  );
  await settle();

  assert.ok(page.text().includes("Fixture phone view"));
  assert.ok(seen.some((url) => url.endsWith("/mini-games/active")));
  assert.ok(!seen.some((url) => url.endsWith("/mini-games/active/display")));
  await page.unmount();
});

test("a later mini-game phase entry remounts the package stage", async () => {
  const seen: string[] = [];
  const services = fixtureServices(seen);
  const props = {
    ...base,
    round: round({ phase: "mini_game", phaseEntry: 12 }),
    stageServices: services,
  };
  const page = await mount(createElement(MiniGameTv, props));
  await settle();
  const before = seen.filter((url) =>
    url.endsWith("/mini-games/active/display"),
  ).length;
  assert.ok(before >= 1);

  await page.rerender(
    createElement(MiniGameTv, {
      ...props,
      round: round({ phase: "mini_game", phaseEntry: 13 }),
    }),
  );
  await settle();
  assert.ok(
    seen.filter((url) => url.endsWith("/mini-games/active/display")).length >
      before,
  );
  await page.unmount();
});

test("a finding left open at time-up is shown once on the mini-game phone", async () => {
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const investigate = await mount(
      createElement(InvestigatePhone, {
        ...base,
        round: round({ phase: "choices" }),
      }),
    );
    await investigate.clickContaining("Search the desk");
    await investigate.click("Spend it");
    assert.ok(
      investigate.text().includes("A torn page is wedged behind the drawer."),
    );
    await investigate.unmount();

    const first = await mount(
      createElement(MiniGamePhone, {
        ...base,
        round: round({ phase: "mini_game", phaseEntry: 12 }),
        stageServices: fixtureServices(),
      }),
    );
    assert.ok(
      first.text().includes("A torn page is wedged behind the drawer."),
    );
    assert.ok(first.text().includes("Time's up. It's in your notebook."));
    await first.click("OK");
    await first.unmount();

    const second = await mount(
      createElement(MiniGamePhone, {
        ...base,
        round: round({ phase: "mini_game", phaseEntry: 13 }),
        stageServices: fixtureServices(),
      }),
    );
    assert.ok(
      !second.text().includes("A torn page is wedged behind the drawer."),
    );
    await second.unmount();
  });
});
